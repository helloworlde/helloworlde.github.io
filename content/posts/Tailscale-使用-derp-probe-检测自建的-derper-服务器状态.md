---
title: "Tailscale 使用 Derp Probe 检测自建的 Derper 服务器状态"
date: 2024-09-22T21:20:35+08:00
tags:
  - HomeLab
  - Network
  - Tailscale
featured: true
type: post
---

在使用服务器部署自建的 HomeLab Derp 服务器之后，偶尔会出现 Derp 服务器无法访问，因此想要监控 Derp 服务器的状态，进行延迟检测等；Tailscale 官方提供了 [derpprobe](https://github.com/tailscale/tailscale/blob/main/cmd/derpprobe/derpprobe.go) 这个工具，可以对 Derp 服务器的 UDP/UDP6/TLS/MESH 等协议以及带宽进行检测

自行部署 Derp Server 参考 [使用家庭宽带公网 IPV6 自建 Tailscale 的 DERP 节点](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8%E5%AE%B6%E5%BA%AD%E5%AE%BD%E5%B8%A6%E5%85%AC%E7%BD%91-ipv6-%E8%87%AA%E5%BB%BA-tailscale-%E7%9A%84-derp-%E8%8A%82%E7%82%B9/)

## 构建 Docker 镜像

derpprobe 没有提供 docker 镜像，可以直接使用我构建的镜像 `ghcr.io/helloworlde/tailscale-derpprober:main`，跳过这一步；或者自行构建

- 下载项目

```bash
git clone https://github.com/tailscale/tailscale.git
```

- 创建 Dockerfile

进入项目下，并在根目录创建 Dockerfile.derpprobe 文件，内容如下：

```Dockerfile
FROM golang:1.23-alpine AS build-env

WORKDIR /go/src/tailscale

COPY tailscale/go.mod tailscale/go.sum ./
RUN go mod download

COPY tailscale .

ARG TARGETARCH
RUN GOARCH=$TARGETARCH go build -o  derpprobe cmd/derpprobe/derpprobe.go

FROM alpine:3.18
RUN apk add --no-cache ca-certificates

ENV DERP_MAP=https://login.tailscale.com/derpmap/default
ENV LISTEN=:8030
ENV ONCE=false
ENV SPREAD=false
ENV INTERVAL=15s
ENV MESH_INTERVAL=15s
ENV STUN_INTERVAL=15s
ENV TLS_INTERVAL=15s
ENV BW_INTERVAL=0
ENV BW_PROBE_SIZE_BYTES=1_000_000

COPY --from=build-env /go/src/tailscale/derpprobe /usr/local/bin/derpprobe

ENTRYPOINT ["sh", "-c", "/usr/local/bin/derpprobe \
    -derp-map=${DERP_MAP} \
    -listen=${LISTEN} \
    -once=${ONCE} \
    -spread=${SPREAD} \
    -interval=${INTERVAL} \
    -mesh-interval=${MESH_INTERVAL} \
    -stun-interval=${STUN_INTERVAL} \
    -tls-interval=${TLS_INTERVAL} \
    -bw-interval=${BW_INTERVAL} \
    -bw-probe-size-bytes=${BW_PROBE_SIZE_BYTES}"]
```

- 构建镜像

```bash
docker build -t derpprobe -f Dockerfile.derpprobe .
```

## 部署

通过 docker compose 部署

### 使用默认配置

- docker-compose.yaml

```yaml
services:
  derpprobe:
    image: ghcr.io/helloworlde/tailscale-derpprober:main
    container_name: derpprobe
    hostname: derpprobe
    restart: unless-stopped
    ports:
      - "8030:8030"
```

部署后，访问 8083 端口即可看到检查状态信息

![homelab-tailscale-derp-probe-homepage.png](https://img.hellowood.dev/picture/homelab-tailscale-derp-probe-homepage.png)

### 指定配置

可以通过 ENV 配置参数，如下：

| 环境变量            | 对应参数名称        | 默认值                                      | 解释说明                                                                  |
| ------------------- | ------------------- | ------------------------------------------- | ------------------------------------------------------------------------- |
| DERP_MAP            | derp-map            | https://login.tailscale.com/derpmap/default | derp 服务器信息，可以使用本地文件，或者指定为 local 从本地 tailscale 获取 |
| SPREAD              | spread              | true                                        | 第一次探测前添加随机延迟间隔                                              |
| LISTEN              | listen              | :8030                                       | 监听的 HTTP 端口                                                          |
| INTERVAL            | interval            | 15s                                         | udp/udp6 协议检测时间间隔                                                 |
| MESH_INTERVAL       | mesh-interval       | 15s                                         | mesh 协议检测时间间隔                                                     |
| STUN_INTERVAL       | stun-interval       | 15s                                         | STUN 协议检测时间间隔                                                     |
| TLS_INTERVAL        | tls-interval        | 15s                                         | TLS 协议检测时间间隔                                                      |
| BW_INTERVAL         | bw-interval         | 0                                           | 带宽检测时间间隔                                                          |
| BW_PROBE_SIZE_BYTES | bw-probe-size-bytes | 1_000_000                                   | 带宽检测的包大小                                                          |

- docker-compose.yaml

```yaml
services:
  derpprobe:
    image: ghcr.io/helloworlde/tailscale-derpprober:main
    container_name: derpprobe
    hostname: derpprobe
    restart: unless-stopped
    environment:
      - LISTEN=:8030
      - SPREAD=true
      - INTERVAL=60s
      - MESH_INTERVAL=60s
      - STUN_INTERVAL=60s
      - TLS_INTERVAL=60s
      - BW_INTERVAL=600s
    ports:
      - "8030:8030"
```

### 使用自定义的 derp-map

derp-map 包含 derp 服务器的信息，默认从 [https://login.tailscale.com/derpmap/default](https://login.tailscale.com/derpmap/default) 获取，也可以自行指定地址；如果是本地文件，则需要添加 `files://` 前缀; 如仅测试自定义的 derp 服务器，配置可以参考: [使用家庭宽带公网 IPV6 自建 Tailscale 的 DERP 节点](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8%E5%AE%B6%E5%BA%AD%E5%AE%BD%E5%B8%A6%E5%85%AC%E7%BD%91-ipv6-%E8%87%AA%E5%BB%BA-tailscale-%E7%9A%84-derp-%E8%8A%82%E7%82%B9/) 的 "修改 tailscale 配置" 部分

需要注意的是，如果 IPV4/IPV6 地址不是固定的就不要添加到配置中，这样不会检测 udp 和 udp6 的延迟信息

```json
{
  "Regions": {
    "900": {
      "RegionID": 900,
      "RegionCode": "homelab",
      "RegionName": "HomeLab",
      "Nodes": [
        {
          "Name": "HomeLab Server",
          "RegionID": 900,
          "HostName": "derp.xxx.xxx",
          "CanPort80": false,
          "DERPPort": 12345,
          "IPv4": "103.6.84.152",
          "IPv6": "2403:2500:8000:1::ef6",
          "CanPort80": true
        }
      ]
    }
  }
}
```

- docker-compose.yaml

```yaml
services:
  derpprobe:
    image: ghcr.io/helloworlde/tailscale-derpprober:main
    container_name: derpprobe
    hostname: derpprobe
    restart: unless-stopped
    environment:
      - DERP_MAP=file:///config/derpmap.json
    ports:
      - "8030:8030"
    volumes:
      - ./config:/config
```

如果想同时检测官方和自己部署的的 Derp 服务器，可以将配置写到同一个配置文件中，也可以通过本地的 Tailscale 进行获取，这样就要求 derpprobe 所在的服务器也是 Tailscale 的节点；

指定要读取的 DERP_MAP 是 local，并且将 Tailscale 的 socks 文件挂载到容器中即可

```yaml
services:
  derpprobe:
    image: ghcr.io/helloworlde/tailscale-derpprober:main
    container_name: derpprobe
    hostname: derpprobe
    restart: unless-stopped
    environment:
      - DERP_MAP=local
    ports:
      - "8030:8030"
    volumes:
      - /var/run/tailscale/tailscaled.sock:/var/run/tailscale/tailscaled.sock
```

### 使用 Prometheus 抓取指标

derpprobe 支持 Prometheus 格式的指标，但是仅允许 debug 或者本地部署时使用，通过容器部署后不能直接访问；可以通过指定环境变量的方式实现；key 是 `TS_ALLOW_DEBUG_IP`, 值是 Prometheus 的地址

- docker-compose.yaml

```yaml
services:
  derpprobe:
    image: ghcr.io/helloworlde/tailscale-derpprober:main
    container_name: derpprobe
    hostname: derpprobe
    restart: unless-stopped
    environment:
      - TS_ALLOW_DEBUG_IP=192.168.65.3
    ports:
      - "8030:8030"
```

这样就可以通过 [http://192.168.65.2:8030/debug/varz](http://192.168.65.2:8030/debug/varz) 路径获取 Prometheus 指标了，之后可以通过 Grafana 进行监控

![homelab-tailscale-derp-probe-grafana-pannel.png](https://img.hellowood.dev/picture/homelab-tailscale-derp-probe-grafana-pannel.png)
