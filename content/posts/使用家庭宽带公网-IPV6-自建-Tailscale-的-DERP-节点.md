---
title: "使用家庭宽带公网 IPV6 自建 Tailscale 的 DERP 节点"
type: post
date: 2024-06-11T21:33:44+08:00
tags: 
    - HomeLab
    - Network
series: 
    - HomeLab
    - Network
featured: true
---


# 使用家庭宽带公网 IPV6 自建 Tailscale 的 DERP 节点

日常使用 Tailscale 连接异地的设备，但是因为经常出现无法直接连接，需要通过香港或东京的 DERP 服务器进行转发，导致延迟很高，影响网络质量；因此计划使用自建的 DERP 解决无法直连的问题；如果部署在国内的服务器上绑定域名需要备案，但是活动购买的服务器限制性能限制带宽限制流量还要单独购买公网 IP，并不合适；国外的延迟高可能还不如 Tailscale 官方的 DERP；

另外自建的 DERP 服务器要求节点能够直接通过公网访问，不能在 NAT 或者负载均衡后面，因此基于家庭宽带的公网 IPV6 自建 DERP 服务器最合适

## 现状

检测 tailscale 的网络节点，延迟最低的是东京的节点，延迟在 70 ms 左右

```shell
tailscale netcheck

Report:
	* UDP: true
	* IPv4: yes, xxx.xxx.xxx.xxx:39325
	* IPv6: yes, [2409:xxxx:xxxx:xxxx::xxxx]:34341
	* MappingVariesByDestIP: false
	* HairPinning: false
	* PortMapping:
	* CaptivePortal: false
	* Nearest DERP: Tokyo
	* DERP latency:
		- tok: 71.6ms  (Tokyo)
		- hkg: 93.1ms  (Hong Kong)
		- sin: 100.5ms (Singapore)
```

## 自建 DERP 节点

### 1. 要求

- 可访问的公网 IPV4 或 IPV6 地址
- 域名，DERP 不修改源码必须要使用域名访问
- 开放 DERP和 STUN端口

tailscale 的 [Prerequisites](https://tailscale.com/kb/1118/custom-derp-servers#prerequisites)文档中要求开放HTTP/HTTPS/STUN 三个端口，默认是 80/443/3478 端口，实际上有 HTTPS/STUN 就够了

### 2. 申请 Let's Encrypt 证书 

Tailscale 的流量必须通过 HTTPS 进行转发，因此域名需要有有效的 TLS 证书，可以使用免费的 Let's Encrypt 证书；

申请 Let's Encrypt 证书可以通过 Lego、Certbot、acme.sh 等多种方式；这里使用 Lego；

在申请证书的过程中，Lego 需要添加一条 `_acme-challenge.域名` 的 txt 记录用于验证域名的信息，所以需要通过 API 添加 DNS 解析

我的域名解析是通过 Cloudflare 托管的，所以需要 Clouflare 的认证信息，得申请一个有 DNS 编辑权限的TOKEN，参考 [Create an API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)

- 申请证书

```shell
CLOUDFLARE_PROPAGATION_TIMEOUT=300 \
  CLOUDFLARE_DNS_API_TOKEN=申请的 TOKEN \
  lego --dns cloudflare \
  --domains 域名 \
  --email 邮箱 \
  --dns.resolvers 1.1.1.1 \
  run
```

`CLOUDFLARE_PROPAGATION_TIMEOUT` 用于控制等待 DNS 记录验证的超时时间，默认为2分钟，但是这个时间 DNS 不一定能生效，可能会导致申请失败，因此配置为 5分钟；同时通过 `dns.resolvers` 指定 DNS 服务器为 `1.1.1.1`，避免局域网内的 DNS 服务器查询时没有记录导致申请失败

### 3. 启动 DERP 服务器

- docker-compose.yaml

需要注意的是，STUN 使用的 3478 端口必须是 UDP 协议，否则会导致连接失败；家庭宽带的 80/443 是不允许对外开放的，因此修改 HTTPS 端口为 12345

另外，需要将申请的证书的 `.key` 和 `.crt` 文件上传到 `cert` 路径下，挂载到容器中

```yaml
version: '3.8'

services:
  derper:
    image: yangchuansheng/derper:latest
    container_name: derper
    restart: always
    ports:
      - "12345:12345"
      - "3478:3478/udp"
    volumes:
      - ./cert:/app/certs
    environment:
      - DERP_VERIFY_CLIENTS=false
      - DERP_CERT_MODE=manual
      - DERP_ADDR=:12345
      - DERP_DOMAIN=域名
      - DERP_DEBUG_LOGS=true
```

- 启动 

```shell
docker-compose up -d
```

输出日志：

```
derper    | 2024/06/09 11:35:54 no config path specified; using /var/lib/derper/derper.key
derper    | 2024/06/09 11:35:54 derper: serving on :12345 with TLS
derper    | 2024/06/09 11:35:54 running STUN server on [::]:3478
```

- 检查 DERP 是否可用

配置 DNS 解析到 DERP 所在的公网地址后，如果能通过域名正常访问，说明证书配置没有问题

![homelab-net-tailscale-derp-server-homepage.png](https://img.hellowood.dev/picture/homelab-net-tailscale-derp-server-homepage.png)

### 4. 修改 tailscale 配置

登录 Tailscale 的控制页面，选择 [Access Controls](https://login.tailscale.com/admin/acls/file)，添加 derpMap 部分的配置，并保存

```json
{
  // ...
  "derpMap": {
    "OmitDefaultRegions": false,// 是否仅使用自定义的 DERP 节点，默认为 false
    "Regions": {
      "900": { 
        "RegionID": 900, // 900-999之间
        "RegionCode": "homelab", // 自定义 Code
        "RegionName": "HomeLab", // 自定义名称
        "Nodes": [ // derp 服务器节点
          {
            "Name": "HomeLab Server",// 名称
            "RegionID": 900, // 和上面的 regionId 一样
            "HostName": "derp.xxx.xxx", // 域名
            "DERPPort": 12345, // DERP 服务器 HTTPS 端口，默认为 443,用于数据中转
            "STUNPort": 3478, // DERP 服务器 STUN 端口，默认为3478，用于 NAT 穿越的端口
            // "IPv6": "2409:xxxx:xxxx:xxxx::xxxx", // IPV6 地址，用于在测试阶段绕过域名解析
			// "InsecureForTests": true, // 如果 TLS 证书未申请，则可以不检测证书
          }
        ]
      }
    }
  }
}
```

关于配置字段的详细解释可以参考 [DERPRegion](https://pkg.go.dev/tailscale.com/tailcfg#DERPRegion) 和 [DERPNode](https://pkg.go.dev/tailscale.com/tailcfg#DERPNode)

## 检查网络连接

使用 `tailscale netcheck` 命令检查网络，配置的 HomeLab 节点的可以正常通信，说明配置成功；最近的 DERP 节点是 HomeLab 而不再是东京，延迟为 40ms 左右

```shell
tailscale netcheck

Report:
	* UDP: true
	* IPv4: yes, xxx.xxx.0.1:34176
	* IPv6: yes, [2409:xxxx:xxxx:xxxx]:47123
	* MappingVariesByDestIP: true
	* HairPinning: false
	* PortMapping:
	* CaptivePortal: false
	* Nearest DERP: HomeLab
	* DERP latency:
		- homelab: 47.3ms  (HomeLab)
		- tok: 115.7ms (Tokyo)
		- hkg: 117.9ms (Hong Kong)
		- sin: 163.4ms (Singapore)
		- syd: 191.5ms (Sydney)
		- par: 220.7ms (Paris)
```

## 启用客户端校验

不开启客户端校验时，别人只需要将地址添加到 Access Control 中即可进行转发，这样会导致自己的节点的带宽和流量被占用，因此最好开启客户端校验

开启客户端校验需要部署 DERP 的服务器自己也是 Tailscale 的节点，另外还需要将 `/var/run/tailscale/tailscaled.sock` 挂载到容器中用于通信

- docker-compose.yaml

```
version: '3.8'

services:
  derper:
    image: yangchuansheng/derper:latest
    container_name: derper
    restart: always
    ports:
      - "12345:12345"
      - "3478:3478/udp"
    volumes:
      - ./cert:/app/certs
      - /var/run/tailscale/tailscaled.sock:/var/run/tailscale/tailscaled.sock
    environment:
      - DERP_VERIFY_CLIENTS=true
      - DERP_CERT_MODE=manual
      - DERP_ADDR=:12345
      - DERP_DOMAIN=derp.xxx.xxx
      - DERP_DEBUG_LOGS=true
```

## 参考文档

- [Custom DERP Servers](https://tailscale.com/kb/1118/custom-derp-servers#prerequisites)
- [浅探 Tailscale DERP 中转服务](https://kiprey.github.io/2023/11/tailscale-derp)
- [How NAT traversal works](https://tailscale.com/blog/how-nat-traversal-works)
- [Tailscale 基础教程：部署私有 DERP 中继服务器](https://icloudnative.io/posts/custom-derp-servers)