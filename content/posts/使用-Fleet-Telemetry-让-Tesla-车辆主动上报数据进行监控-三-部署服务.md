---
date: 2025-09-26
# description: ""
# image: ""
lastmod: 2025-10-04
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务"
type: "post"
---

## 一、部署依赖服务

### 1.1 部署 tesla-http-proxy

> tesla-http-proxy 可以使用 [https://github.com/helloworlde/fleet-telemetry-proxy](https://github.com/helloworlde/fleet-telemetry-proxy) 在 Cloudflare Worker 部署替代

[vehicle-command](https://github.com/teslamotors/vehicle-command) 是一个用于向车辆发送命令的工具，需要使用其中的 [tesla-http-proxy](https://github.com/teslamotors/vehicle-command?tab=readme-ov-file#using-the-http-proxy) 向车辆发送配置指令；

用 docker 部署 tesla-http-proxy，需要挂载前面生成的私钥证书和 Certbot 申请的 TLS 证书

文件目录结构如下, `private-key.pem` 是前面手动生成的私钥，`tls/fullchain.pem` 和 `tls/privkey.pem` 是 Certbot 申请的证书

```bash
.
├── certs
│   ├── private-key.pem
│   └── tls
│       ├── cert.pem
│       ├── chain.pem
│       ├── fullchain.pem
│       ├── privkey.pem
└── docker-compose.yaml
```

- docker-compose.yaml

```yaml
services:
  tesla_http_proxy:
    image: tesla/vehicle-command:latest
    container_name: tesla_http_proxy
    ports:
      - 4443:4443
    environment:
      - TESLA_HTTP_PROXY_TLS_CERT=/certs/tls/fullchain.pem
      - TESLA_HTTP_PROXY_TLS_KEY=/certs/tls/privkey.pem
      - TESLA_KEY_FILE=/certs/private-key.pem
      - TESLA_HTTP_PROXY_HOST=0.0.0.0
      - TESLA_HTTP_PROXY_PORT=4443
      - TESLA_HTTP_PROXY_TIMEOUT=10s
      - TESLA_VERBOSE=true
    volumes:
      - ./certs/tls/fullchain.pem:/certs/tls/fullchain.pem:ro # Certboot 生成的公钥和中间证书，用于 https 连接
      - ./certs/tls/privkey.pem:/certs/tls/privkey.pem:ro # Certbot 生成的私钥，用于 https 连接
      - ./certs/private-key.pem:/certs/private-key.pem:ro # 手动生成的私钥，用于加密指令
```

然后使用 docker compose 启动，启动成功后访问 `https://fleet.example.com:4443/health`，返回 OK 说明启动成功

```bash
curl https://fleet.example.com:4443/health
OK#
```

### 1.2 部署 MQTT

MQTT 用于转发 Fleet Telemetry 发送的车辆数据，可以使用 EMQX、Mosquitto 等 MQTT 服务；因为 EMQX 提供消息处理能力，所以使用 EMQX 为例进行部署，详细可以参考 [通过 Docker 运行 EMQX](https://docs.emqx.com/zh/emqx/v5.10/deploy/install-docker.html)

- docker-compose.yaml

```yaml
services:
  mqtt:
    image: emqx/emqx-enterprise
    container_name: mqtt
    restart: always
    ports:
      - "1883:1883" # MQTT
      - "8083:8083" # WebSocket
      - "8084:8084" # WebSocket/TLS
      - "8883:8883" # MQTT/TLS
      - "18083:18083" # Dashboard
    volumes:
      - ./data:/opt/emqx/data
      - ./log:/opt/emqx/log
```

## 二、部署 Fleet Telemetry

### 2.1 配置文件

Fleet Telemetry 需要一个配置文件，用于指定监听的端口、转发的消息等组件

- config.json

关于配置的详细的配置解释可以参考 [Install steps](https://github.com/teslamotors/fleet-telemetry?tab=readme-ov-file#install-steps)

这里将消息转发给了 MQTT，监听 12345 端口，TLS 使用 Certbot 申请的证书；MQTT topic 的格式为 `<topic_base>/<VIN>/v/<field_name>`，如车速为 `telemetry/xxx/v/VehicleSpeed`，详细可以参考 [MQTT Datastore](https://github.com/teslamotors/fleet-telemetry/blob/main/datastore/mqtt/README.md)

```json
{
  "host": "0.0.0.0",
  "port": 12345,
  "status_port": 12346,
  "log_level": "info",
  "json_log_enable": true,
  "namespace": "tesla_telemetry",
  "reliable_ack": false,
  "transmit_decoded_records": true,
  "reliable_ack_sources": {
    "V": "mqtt"
  },
  "logger": {
    "verbose": true
  },
  "mqtt": {
    "broker": "100.0.0.2:1883",
    "client_id": "tesla-telemetry",
    "topic_base": "telemetry",
    "qos": 1,
    "retained": true,
    "connect_timeout_ms": 30000,
    "publish_timeout_ms": 5000,
    "connect_retry_interval_ms": 10
  },
  "vins_signal_tracking_enabled": ["dtelemetry"],
  "monitoring": {
    "prometheus_metrics_port": 9091,
    "profiler_port": 4269,
    "profiling_path": "/tmp/trace.out"
  },
  "rate_limit": {
    "enabled": true,
    "message_interval_time": 30,
    "message_limit": 1000
  },
  "records": {
    "alerts": ["logger", "mqtt"],
    "errors": ["logger", "mqtt"],
    "V": ["logger", "mqtt"],
    "connectivity": ["logger", "mqtt"]
  },
  "tls": {
    "server_cert": "/certs/fullchain.pem",
    "server_key": "/certs/privkey.pem"
  }
}
```

### 2.2 部署 Fleet Telemetry

使用 docker 部署 Fleet Telemetry，目录结构如下：

```bash
.
├── certs
│   ├── cert.pem
│   ├── chain.pem
│   ├── fullchain.pem
│   └── privkey.pem
├── config.json
├── docker-compose.yaml
```

- docker-compose.yaml

需要挂载前面使用 Certbot 申请的 TLS 证书；另外需要注意的是 Fleet Telemetry 和车辆使用 mTLS 进行通信，如果中间有反向代理，需要保证反向代理支持 mTLS，否则车辆无法连接；如果配置不对排查比较困难，建议直接将端口暴露到公网，减少复杂度

```yaml
services:
  fleet-telemetry:
    image: tesla/fleet-telemetry:latest
    container_name: fleet-telemetry
    command:
      - /fleet-telemetry
      - -config=/etc/fleet-telemetry/config.json
    ports:
      - 12345:12345 # TLS port
      - 12346:12346 # status port
      - 9091:9091 # prometheus metrics port
    volumes:
      - ./config.json:/etc/fleet-telemetry/config.json:ro
      - ./certs/fullchain.pem:/certs/fullchain.pem:ro
```

启动后会输出相关的监听日志:

```bash
fleet-telemetry  | 2025/09/27 06:15:02 maxprocs: Leaving GOMAXPROCS=1: CPU quota undefined
fleet-telemetry  | {"activity":true,"context":"fleet-telemetry","level":"info","msg":"starting_server","time":"2025-09-27T06:15:02Z"}
fleet-telemetry  | {"activity":true,"context":"fleet-telemetry","level":"info","msg":"profiler_started","port":4269,"time":"2025-09-27T06:15:02Z"}
```

访问 status 端口检查状态，返回 ok 说明服务正确启动

```bash
curl localhost:12346/status
ok#
```

### 2.3 验证配置

检查时需要通过 `config.json` 配置文件声明要检查的域名、CA 等信息

- config.json

```bash
{
  "hostname": "fleet.example.com",
  "port": 12345,
  "ca": "CA 证书内容"
}
```

执行 [check_server_cert.sh](https://github.com/teslamotors/fleet-telemetry/blob/main/tools/check_server_cert.sh) 脚本检查配置，如果配置正确将返回 OK 状态，说明 mTLS 配置没有问题

```bash
./check_server_cert.sh config.json
/tmp/tmp.yhc6u2DX4Y: OK
The server certificate is valid.
```

## 参考文档

- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(一)申请证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%80-%E7%94%B3%E8%AF%B7%E8%AF%81%E4%B9%A6/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%8C-%E6%B7%BB%E5%8A%A0%E8%99%9A%E6%8B%9F%E9%92%A5%E5%8C%99/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%89-%E9%83%A8%E7%BD%B2%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%9B%9B-%E4%B8%8B%E5%8F%91%E9%85%8D%E7%BD%AE/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%94-%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%85%AD-%E7%9B%91%E6%8E%A7%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%83-%E5%AE%8C%E6%95%B4%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E/)
