---
date: 2025-06-08
# description: ""
# image: ""
lastmod: 2025-09-06
showTableOfContents: false
tags:
  - HomeLab
  - Easytier
featured: true
title: "Easytier 使用自建公共节点进行异地组网"
type: "post"
---

[Easytier](https://easytier.cn/guide/introduction.html) 是一个基于 WireGuard 的 VPN 工具，使用 Rust 语言开发，支持跨平台、NAT穿透、子网代理，智能路由等功能

## 部署共享节点

使用 docker 部署共享节点，需要开放 11010/11011/11012 这三个端口；共享节点不需要指定任何参数，直接启动 `easytier-core` 即可

- docker-compose.yml

```yaml
services:
  easytier:
    image: easytier/easytier:latest
    hostname: ${HOSTNAME}
    container_name: easytier
    restart: unless-stopped
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    environment:
      - TZ=Asia/Shanghai
    devices:
      - /dev/net/tun:/dev/net/tun
    volumes:
      - ./data:/root
      - /etc/machine-id:/etc/machine-id:ro
```

通过启动日志查看启动状态

```bash
easytier  | Starting easytier with config:
easytier  | ############### TOML ###############
easytier  |
easytier  | instance_name = "default"
easytier  | dhcp = false
easytier  | listeners = [
easytier  |     "tcp://0.0.0.0:11010",
easytier  |     "udp://0.0.0.0:11010",
easytier  |     "wg://0.0.0.0:11011",
easytier  |     "ws://0.0.0.0:11011/",
easytier  |     "wss://0.0.0.0:11012/",
easytier  | ]
easytier  | mapped_listeners = []
easytier  | exit_nodes = []
easytier  | peer = []
easytier  | rpc_portal = "0.0.0.0:15888"
easytier  |
easytier  | [network_identity]
easytier  | network_name = "default"
easytier  | network_secret = ""
easytier  |
easytier  | [flags]
easytier  |
easytier  | -----------------------------------
easytier  | 2025-06-09 09:31:01: new listener added. listener: tcp://0.0.0.0:11010
easytier  | 2025-06-09 09:31:01: new listener added. listener: udp://0.0.0.0:11010
easytier  | 2025-06-09 09:31:01: new listener added. listener: tcp://[::]:11010
easytier  | 2025-06-09 09:31:01: new listener added. listener: udp://[::]:11010
easytier  | 2025-06-09 09:31:01: new listener added. listener: wg://0.0.0.0:11011
easytier  | 2025-06-09 09:31:01: new listener added. listener: wg://[::]:11011
easytier  | 2025-06-09 09:31:01: new listener added. listener: ws://0.0.0.0:11011/
easytier  | 2025-06-09 09:31:01: new listener added. listener: ws://[::]:11011/
easytier  | 2025-06-09 09:31:01: new listener added. listener: wss://0.0.0.0:11012/
easytier  | 2025-06-09 09:31:01: new listener added. listener: wss://[::]:11012/
```

## 部署边缘节点

### 部署

Easytier 依赖 tun 创建虚拟网络，因此如果是在 PVE 的 CT 容器中部署，需要将 tun 挂载到容器中，可以参考 [Proxmox-VE 开启 CT/LXC 容器 Wireguard/Tailscale 访问 TUN 权限](https://blog.hellowood.dev/posts/proxmox-ve-%E5%BC%80%E5%90%AF-ct-lxc-%E5%AE%B9%E5%99%A8-wireguard-tailscale-%E8%AE%BF%E9%97%AE-tun-%E6%9D%83%E9%99%90/)

- docker-compose.yml

节点的地址、公共节点等信息是通过环境变量的方式传递到启动命令的，需要配置 `.env` 文件

```yaml
services:
  easytier:
    image: easytier/easytier:latest
    hostname: ${HOSTNAME}
    container_name: easytier
    restart: unless-stopped
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    environment:
      - TZ=Asia/Shanghai
    devices:
      - /dev/net/tun:/dev/net/tun
    volumes:
      - ./data:/root
      - /etc/machine-id:/etc/machine-id:ro
    command: -i ${ADDR} --network-name ${NETWORK_NAME} --network-secret ${NETWORK_PASSWORD} -p ${PUBLIC_PEER}
```

- .env

```bash
ADDR=10.2.0.3/24
NETWORK_NAME=homelab
NETWORK_PASSWORD=123456
PUBLIC_PEER=tcp://192.168.2.120:11010
```

启动日志可以看到已经成功加入共享节点

```go
easytier  | Starting easytier with config:
easytier  | ############### TOML ###############
easytier  |
easytier  | ipv4 = "10.2.0.3/24"
easytier  | listeners = [
easytier  |     "tcp://0.0.0.0:11010",
easytier  |     "udp://0.0.0.0:11010",
easytier  |     "wg://0.0.0.0:11011",
easytier  |     "ws://0.0.0.0:11011/",
easytier  |     "wss://0.0.0.0:11012/",
easytier  | ]
easytier  | rpc_portal = "0.0.0.0:0"
easytier  |
easytier  | [network_identity]
easytier  | network_name = "homelab"
easytier  | network_secret = "123456"
easytier  |
easytier  | [[peer]]
easytier  | uri = "tcp://192.168.2.120:11010"
easytier  |
easytier  | [flags]
easytier  |
easytier  | -----------------------------------
easytier  | 2025-06-09 09:19:17: new listener added. listener: tcp://0.0.0.0:11010
easytier  | 2025-06-09 09:19:17: new listener added. listener: udp://0.0.0.0:11010
easytier  | 2025-06-09 09:19:17: new listener added. listener: tcp://[::]:11010
easytier  | 2025-06-09 09:19:17: new listener added. listener: udp://[::]:11010
easytier  | 2025-06-09 09:19:17: new listener added. listener: wg://0.0.0.0:11011
easytier  | 2025-06-09 09:19:17: new listener added. listener: wss://[::]:11012/
easytier  | 2025-06-09 09:19:17: new listener added. listener: wg://[::]:11011
easytier  | 2025-06-09 09:19:17: new listener added. listener: ws://0.0.0.0:11011/
easytier  | 2025-06-09 09:19:17: new listener added. listener: ws://[::]:11011/
easytier  | 2025-06-09 09:19:17: new listener added. listener: wss://0.0.0.0:11012/
easytier  | 2025-06-09 09:19:17: tun device ready. dev: tun0
easytier  | 2025-06-09 09:19:18: connecting to peer. dst: tcp://192.168.2.120:11010
easytier  | 2025-06-09 09:19:18: new peer connection added. conn_info: my_peer_id: 729510693, dst_peer_id: 518302289, tunnel_info: Some(TunnelInfo { tunnel_type: "tcp", local_addr: Some(Url { url: "tcp://192.168.2.121:35727" }), remote_addr: Some(Url { url: "tcp://192.168.2.120:11010" }) })
easytier  | 2025-06-09 09:19:18: new peer added. peer_id: 518302289
```

其他边缘节点使用同样的方式部署，只需要修改 ADDR 不要重复即可

### 检查网络状态

- 检查网络状态

通过 `easytier-cli peer` 可以看到对端节点已经成功加入，并且网络状态正常

```bash
/app # easytier-cli peer
┌─────────────┬──────────────────┬───────┬────────┬───────────┬──────────┬──────────┬──────────────┬────────────────┬────────────┬────────────────┐
│ ipv4        │ hostname         │ cost  │ lat_ms │ loss_rate │ rx_bytes │ tx_bytes │ tunnel_proto │ nat_type       │ id         │ version        │
├─────────────┼──────────────────┼───────┼────────┼───────────┼──────────┼──────────┼──────────────┼────────────────┼────────────┼────────────────┤
│ 10.2.0.2/24 │ drft2            │ Local │ -      │ -         │ -        │ -        │ -            │ PortRestricted │ 2310410712 │ 2.3.0-d7c3179c │
├─────────────┼──────────────────┼───────┼────────┼───────────┼──────────┼──────────┼──────────────┼────────────────┼────────────┼────────────────┤
│             │ PublicServer_dev │ p2p   │ 0.120  │ 0.000     │ 0 B      │ 0 B      │ tcp          │ Unknown        │ 518302289  │ 2.2.4-67100407 │
├─────────────┼──────────────────┼───────┼────────┼───────────┼──────────┼──────────┼──────────────┼────────────────┼────────────┼────────────────┤
│ 10.2.0.3/24 │ draft            │ p2p   │ 0.087  │ 0.000     │ 0 B      │ 0 B      │ udp,tcp      │ PortRestricted │ 729510693  │ 2.3.1-a6773aa5 │
└─────────────┴──────────────────┴───────┴────────┴───────────┴──────────┴──────────┴──────────────┴────────────────┴────────────┴────────────────┘
```

- ping 对端节点

ping 对端的 10.2.0.3 可以成功

```bash
/app # ping 10.2.0.3
PING 10.2.0.3 (10.2.0.3): 56 data bytes
64 bytes from 10.2.0.3: seq=0 ttl=64 time=0.267 ms
64 bytes from 10.2.0.3: seq=1 ttl=64 time=0.322 ms
64 bytes from 10.2.0.3: seq=2 ttl=64 time=0.330 ms
^C
--- 10.2.0.3 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.267/0.306/0.330 ms
```
