---
title: "Grafana 使用 ClickHouse 作为数据源配置图表"
type: post
date: 2023-11-27T15:20:30+08:00
tags:
  - Grafana
  - ClickHouse
series:
  - Grafana
  - ClickHouse
featured: true
---

ClickHouse 是一种开源的列式数据库管理系统，专注于处理大规模数据分析工作负载。它在处理海量数据时具有高性能、可扩展、灵活的数据模型、支持 SQL 等特性；适用于需要及时分析最新数据的应用场景，如日志分析、事件跟踪等

在应用过程中，使用 ClickHouse 作为数据源，保存服务上报的秒级指标信息，用于 Grafana 查询秒级监控指标

> 这里使用的 Grafana 版本 v10.1.1, ClickHouse 版本为 23.9.3.12

## 启动服务并添加数据

### 启动 ClickHouse 和 Grafana

使用 Docker Compose 启动

```yaml
version: "3.7"
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./data/plugins/:/var/lib/grafana/plugins
      - ./data/provisioning:/etc/grafana/provisioning
    networks:
      - grafana

  clickhouse:
    image: "clickhouse/clickhouse-server"
    container_name: "grafana-clickhouse-server"
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - ./data/data:/var/lib/clickhouse
      - ./data/temp:/temp
      - ./data/log:/var/log/clickhouse-server
    environment:
      CLICKHOUSE_SERVER_USER: default
      CLICKHOUSE_SERVER_PASSWORD: 123456
    networks:
      - grafana

networks:
  grafana:
```

### 添加数据

- 登陆数据库

进入到 docker 容器中，然后使用 `clickhouse-client` 访问数据库

```bash
docker exec -it clickhouse bash
```

```bash
clickhouse-client
```

```bash
ClickHouse client version 23.10.5.20 (official build).
Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 23.10.5 revision 54466.

Warnings:
 * Linux transparent hugepages are set to "always". Check /sys/kernel/mm/transparent_hugepage/enabled

clickhouse :)
```

- 创建测试数据库

```SQL
CREATE DATABASE IF NOT EXISTS metrics
```

- 创建测试表

```SQL
CREATE TABLE IF NOT EXISTS metrics.request_history
(
    `id` UUID DEFAULT generateUUIDv4(),
    `application` LowCardinality(String),
    `env` LowCardinality(String),
    `hostname` LowCardinality(String),
    `uri` String,
    `add_time` DateTime64(3) CODEC(DoubleDelta, LZ4)
)
ENGINE = MergeTree
PARTITION BY toDate(add_time)
ORDER BY (application, env, hostname, uri)
TTL toDate(add_time) + 30;
```

- 插入随机数据

```SQL
INSERT INTO metrics.request_history(application, env, hostname, uri) VALUES('app1', 'prod', 'hostname1', '/api/user');
//...
```

## 配置 Grafana

### 安装 ClickHouse 插件

在 Grafana 面板 Connections -> Add new connection 中添加 ClickHouse 插件

ClickHouse 有两个插件，分别是 Grafana 官方提供的 [ClickHouse](https://github.com/grafana/clickhouse-datasource)
和社区提供的 [Altinity plugin for ClickHouse](https://github.com/Altinity/clickhouse-grafana)；

官方的 ClickHouse 仅支持 Grafana >=9.0.0 的版本使用，Altinity plugin for ClickHouse 支持 Grafana 4.6 之后的版本

这两个插件在用法和交互上有所差异，这里使用官方的 ClickHouse 进行查询

![grafana-clickhouse-add-datasource.png](https://img.hellowood.dev/picture/grafana-clickhouse-add-datasource.png)

### 配置数据源

在 Grafana 面板 Connections -> Data sources 中添加 ClickHouse 数据源

## 配置图表

选择新增图表，并选择 ClickHouse 作为数据源

### 配置 table 图表

创建 Table 图表直接使用 SQL 查询需要的列即可

```SQL
SELECT  env,
        hostname,
        uri,
        value
FROM metrics.request_history
ORDER BY add_time
LIMIT 10
```

### 配置时间序列的图表

时间序列的图表需要至少有三列，分别是时间、名称、值；此时列需要聚合

```SQL
SELECT  toDateTime64(add_time, 0) as time ,
        uri as label,
        sum(value) as value
FROM metrics.request_history
GROUP BY label, time
ORDER BY time
```

## 配置查询条件

ClickHouse 插件支持多个宏(Macro)，在向 ClickHouse 发送查询前会将 Macro 替换为对应的值

### 时间范围查询条件

使用 `$__timeFilter()` 作为时间范围的查询条件，使用的字段是指定的 DateTime 或 Timestamp
对应的列，如 `where $__timeFilter(add_time)` 会被替换为 `where add_time >= xxx and add_time <= xxx`

```SQL
SELECT  toDateTime64(add_time, 0) as time ,
        uri as label,
        sum(value) as value
FROM metrics.request_history
WHERE $__timeFilter(add_time)
GROUP BY label, time
ORDER BY time
```

最终查询的 SQL 为:

```SQL
SELECT  toDateTime64(add_time, 0) as time ,
        uri as label,
        sum(value) as value
FROM metrics.request_history
WHERE add_time >= '1699940462' AND add_time <= '1699962062'
GROUP BY label, time
ORDER BY time
```

### 使用变量作为查询条件

- 添加变量

变量的定义和 Prometheus 数据源类似，不过是使用 SQL 查询，如配置 env，使用选中的时间范围进行查询；
因为 `add_time` 类型是 `DateTime`，所以需要将当前的时间范围转为秒级的时间戳，然后使用 `toDateTime` 转为 `DateTime` 进行比较

```SQL
SELECT  distinct(toString(env))
FROM metrics.request_history
WHERE add_time BETWEEN toDateTime(${__from:type: post
date:seconds}) AND toDateTime(${__to:type: post
date:seconds})
```

依赖其他变量进行查询，添加到查询条件即可，使用 `singlequote`添加引号，避免查询语法错误

```SQL
SELECT  distinct(toString(application))
FROM `logs`.`red_sentinel_metrics`
WHERE env in (${env:singlequote})
AND ActionDate BETWEEN toDateTime(${__from:type: post
date:seconds}) AND toDateTime(${__to:type: post
date:seconds})
```

- 添加动态查询条件

动态查询条件使用 `$__conditionalAll` 进行查询；

`$__conditionalAll` 接收两个参数，第一个参数是 `SQL predicate`，第二个参数是 `$variable`，当 `$variable` 不为空的时候会将 `SQL predicate` 作为查询条件添加到 SQL 中，如果是空或者是 ALL 则会添加 `1=1`，

如 `AND $__conditionalAll(uri in ('${uri:singlequote}'), '${uri:singlequote}')`，如果 uri 不为空，则会将 `AND uri in (xxx)` 作为查询条件；如果 uri 为空则是 `AND 1=1`

```SQL
SELECT toDateTime64(add_time, 0) as time,
       uri as label,
       sum(value) as value
FROM metrics.request_history
WHERE $__timeFilter(add_time)
AND $__conditionalAll(uri in ('${uri:singlequote}'), '${uri:singlequote}')
GROUP BY  label,time
ORDER BY time
```

最终 SQL 为：

```SQL
SELECT add_time as time,
       uri as label,
       sum(value) as value
FROM metrics.request_history
WHERE add_time >= '1699861790' AND add_time <= '1699883390'
AND  uri in ('/api/user')
GROUP BY  label,time
ORDER BY time
```

### 聚合

可以用 `$__conditionalAll` 进行聚合，或者将要聚合的字段拼接为一个字段

官方的 ClickHouse 对聚合支持不够完善，`$__conditionalAll` 如果是空会被替换为 `1=1`，会导致语法错误，如果不为空，则字段是固定存在的，事实上并不动态；而 Altinity plugin for ClickHouse 插件的 `$conditionalTest` 为空时不做任何拼接更能满足动态聚合的场景

- 用 conditionalAll

注意，这种场景下 uri 变量必须要有值，否则会出现 `GROUP BY 1=1` 这样的错误语法

```SQL
SELECT $__timeInterval(add_time) as time,
       uri as label,
       sum(value) as value
FROM metrics.request_history
WHERE $__timeFilter(add_time)
AND $__conditionalAll(uri in (${uri:singlequote}), ${uri:singlequote})
GROUP BY  $__conditionalAll(uri, ${uri:singlequote}), $__conditionalAll(hostname, ${hostname:singlequote}), time
ORDER BY time
```

最终查询为:

```SQL
SELECT toDateTime64(add_time, 0) as time,
       uri as label,
       sum(value) as value
FROM metrics.request_history
WHERE add_time >= '1699944714' AND add_time <= '1699966314'
AND uri in ('/status','/actuator/health')
GROUP BY  uri, hostname, time
ORDER BY time
```

- 用字段拼接

拼接后的字段用于做聚合，适用于固定的聚合字段

```SQL
SELECT toDateTime64(add_time, 0) as time,
       concat(application, ': ', uri) as label,
       sum(value) as value
FROM metrics.request_history
WHERE $__timeFilter(add_time)
AND $__conditionalAll(uri in (${uri:singlequote}), ${uri:singlequote})
GROUP BY label, time
ORDER BY time
```

最终查询为：

```SQL
SELECT toDateTime64(add_time, 0) as time,
       concat(application, ': ', uri) as label,
       sum(value) as value
FROM metrics.request_history
WHERE add_time >= '1699944327' AND add_time <= '1699965927'
AND uri in ('/status','/actuator/health')
GROUP BY label, time
ORDER BY time
```
