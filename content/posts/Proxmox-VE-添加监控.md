---
title: "Proxmox VE 添加监控"
type: post
date: 2023-04-09T21:29:39+08:00
tags:
    - Proxmox VE
    - InfluxDB
    - HomeLab
categories: 
    - Proxmox VE
    - InfluxDB
    - HomeLab
series: 
    - Proxmox VE
featured: true  
---

# Proxmox VE 添加监控 

PVE 支持添加 [Graphite](https://graphiteapp.org/) 或者 [InfluxDB](https://www.influxdata.com/) 作为指标数据的存储；在添加配置后，PVE 会主动将配置信息发送到对应的存储中，用于记录和监控 PVE 的状态

基于 Docker 容器，使用 InfluxDB 和 Grafana 对 PVE 进行监控，效果如图：

![homelab-promoxve-monitor-metrics-dashboard.png](https://img.hellowood.dev/picture/homelab-promoxve-monitor-metrics-dashboard.png)

## 配置 InfluxDB 

使用的是 InfluxDB 2 版本，使用 Flux 语法进行查询；因此需要启动 InfluxDB 2 的容器，使用 DockerCompose 方便配置

- docker-compose.yaml

```yaml
version: '3'

services:
  influxdb:
    container_name: influxdb
    image: influxdb:2.6
    ports:
      - "8086:8086"
    volumes:
      - ./data/influx/data:/var/lib/influxdb2
      - ./data/influx/config:/etc/influxdb2
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: qwertyuiop
      DOCKER_INFLUXDB_INIT_ORG: influx
      DOCKER_INFLUXDB_INIT_BUCKET: influx
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: 123456
```

`DOCKER_INFLUXDB_INIT_MODE`它用于指定容器启动时运行的初始化模式。该变量有两个有效值：
- `setup`: 表示在容器首次启动时，将执行InfluxDB初始化脚本并创建管理员用户。
- `skip`：表示跳过初始化脚本的执行，直接启动InfluxDB服务。

`DOCKER_INFLUXDB_INIT_PASSWORD` 不能设置的太简单，否则 InfluxDB 启动时会报错
`DOCKER_INFLUXDB_INIT_ORG` 用于指定 InfluxDB 的组织
`DOCKER_INFLUXDB_INIT_BUCKET` 用于指定初始化使用的 Bucket
`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` 用于访问时进行鉴权


## 配置 PVE 

在 PVE 的服务器视图下，选择数据中心 - 指标服务器，选择添加 InfluxDB，输入相关的配置；协议选择 HTTP，组织添加 `DOCKER_INFLUXDB_INIT_ORG` 配置的值，插槽添加 `DOCKER_INFLUXDB_INIT_BUCKET` 配置的 Bucket， 令牌填写 `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` 配置的 token

添加后 PVE 就会将监控指标推送到 InfluxDB 的 Bucket 中了

![homelab-promoxve-monitor-metrics-pve-add-influxdb.png](https://img.hellowood.dev/picture/homelab-promoxve-monitor-metrics-pve-add-influxdb.png)

## 配置 Grafana

### 启动 Grafana

- docker-compose.yaml

```yaml
version: '3'

services:
  # influxdb ...
  
  grafana:
    image: grafana/grafana
    container_name: grafana-server
    restart: always
    depends_on:
      - influxdb
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    links:
      - influxdb
    ports:
      - '3000:3000'
    volumes:
      - ./data/grafana:/var/lib/grafana
```

### 添加 InfluxDB 作为数据源

登陆 Grafana 并添加数据源，使用 InfluDB 作为数据源

![homelab-promoxve-monitor-metrics-grafana-add-datasource.png](https://img.hellowood.dev/picture/homelab-promoxve-monitor-metrics-grafana-add-datasource.png)

在 InfluxDB 2 版本以后，添加到 Grafana 数据源变得不太方便；配置如下：

- `Query Language` 选择 `Flux`
-  `URL` 填写 InfluxDB 的地址，如 `http://192.168.2.8:8086`
-  `Access`选择 `Server(default)`(高版本的 Grfana 已不包含该选项)
-  `Auth`下的配置全部关闭，不需要配置
-  `Custom HTTP Headers` 添加一个新的配置，Header 名称为 `Authorization`, Value 为 `Token`+`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` 配置的 Token，如 `Token 123456`(需注意中间有空格)
-  `Organization` 为 `DOCKER_INFLUXDB_INIT_ORG` 配置的值，如 `influx`
-  `Token` 不用配置
-  `Default Bucket` 为 `DOCKER_INFLUXDB_INIT_BUCKET` 配置的值，如 `influx`

配置完成后，点击 `Save and Test`，如果提示成功则表示配置正确

### 添加 Grafana 图表

在 [Grafana Dashboard](https://grafana.com/grafana/dashboards/?search=proxmox) 中搜索 proxmox，选择支持 Flux 查询语法的图表进行添加，如添加 [Proxmox \[Flux\]](https://grafana.com/grafana/dashboards/15356-proxmox-flux/)，根据 ID 导入 Grafana 即可看到 PVE 的监控指标

![homelab-promoxve-monitor-metrics-dashboard.png](https://img.hellowood.dev/picture/homelab-promoxve-monitor-metrics-dashboard.png)