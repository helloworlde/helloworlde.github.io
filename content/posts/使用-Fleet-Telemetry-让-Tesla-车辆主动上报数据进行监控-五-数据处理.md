---
date: 2025-09-28
# description: ""
# image: ""
lastmod: 2025-10-01
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理"
type: "post"
---

在正确配置 Fleet Telemetry 并下发配置给车辆后，就可以接收到车辆的上报数据，并且通过 MQTT 转发

## 一、数据处理

### 1.1 查看数据

车辆定期上报的数据到服务器，通过 MQTT 转发给下游；可以查看日志或者 MQTT 客户端订阅对应的 topic 来查看数据

- 查看日志

下面日志是电量的上报内容

```bash
docker logs -f fleet-telemetry

fleet-telemetry  | {"activity":true,"context":"fleet-telemetry","data":{"CreatedAt":"2025-09-28T00:43:13Z","EstBatteryRange":{"doubleValue":232.09772017025708},"IdealBatteryRange":{"doubleValue":232.09772017025708},"IsResend":false,"RatedRange":{"doubleValue":232.09772017025708},"Soc":{"doubleValue":86.09375},"Vin":"{VIN}"},"level":"info","metadata":{"device_client_version":"1.0.3","receivedat":"1759020194000","timestamp":"0","txid":"ac19f006a71b472296b8b3-000000495","txtype":"V","version":"0","vin":"{VIN}"},"msg":"record_payload","time":"2025-09-28T00:43:14Z","vin":"{VIN}"}
```

- 使用 MQTT 客户端订阅

以连接状态为例, topic 为 `telemetry/{VIN}/v/connectivity`，可以使用 [MQTTX](https://mqttx.app/zh/docs) 等工具查看

```bash
{
  "ConnectionId": "xxxx",
  "CreatedAt": "2025-09-27T12:22:21Z",
  "Status": "CONNECTED"
}
```

### 1.2 处理数据

可以使用 EMQX 的规则引擎将数据存储到数据库中，或者使用其他的工具进行处理，下面以将数据存储到 PostgreSQL 为例，SQL 为:

- 在 PostgreSQL 创建表

```sql
create table if not exists tesla_fleet_telemetry (
    id bigint generated always as identity primary key,
    topic varchar(1000),
    payload varchar(10000),
    "timestamp" timestamp,
    add_time timestamp default now()
);

```

- 使用 EMQX 规则引擎插入数据

```sql
insert into tesla_fleet_telemetry (topic, payload, timestamp)
 values
 (${topic}, ${payload}, TO_TIMESTAMP((${timestamp} :: bigint)/1000));
```

![homelab-tesla-fleet-telemetry-emqx-flow-rewrite-message-to-pg.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-emqx-flow-rewrite-message-to-pg.png)

- 查看 PostgreSQL 数据

```sql
select *
from tesla_fleet_telemetry
order by add_time desc
```

这里只是简单的将数据存储到数据库中，示例需要对数据的 Topic、Payload 进行解析，然后存储到对应的字段中，方便后续查询和分析

## 参考文档

- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(一)申请证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%80-%E7%94%B3%E8%AF%B7%E8%AF%81%E4%B9%A6/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%8C-%E6%B7%BB%E5%8A%A0%E8%99%9A%E6%8B%9F%E9%92%A5%E5%8C%99/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%89-%E9%83%A8%E7%BD%B2%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%9B%9B-%E4%B8%8B%E5%8F%91%E9%85%8D%E7%BD%AE/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%94-%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%85%AD-%E7%9B%91%E6%8E%A7%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%83-%E5%AE%8C%E6%95%B4%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E/)
