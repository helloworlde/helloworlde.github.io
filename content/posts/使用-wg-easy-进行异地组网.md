---
date: 2025-06-08
# description: ""
# image: ""
lastmod: 2025-06-08
showTableOfContents: false
tags:
  - HomeLab
  - WireGuard
featured: true
title: "使用 wg-easy 进行异地组网"
type: "post"
---

[wg-easy](https://wg-easy.github.io/wg-easy/latest/) 是一个开源的 WireGuard 配置管理工具，支持通过 Web 界面快速生成和管理 WireGuard 配置文件，以及客 WireGuard 节点之间的简单的监控

![homelab-sd-wan-wg-easy-homepage.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-homepage.png)

这里总共有五个节点，用 WireGuard 进行组网，在其中一个部署 wg-easy

## 部署 wg-easy

使用 docker 在 VPS 上部署 wg-easy，作用控制面和中转节点；在 sysctls 中开启 ipv4 转发和 ipv6 转发，用于转发不同节点之间的流量

- docker-compose.yml

```yaml
services:
  wg-easy:
    image: ghcr.io/wg-easy/wg-easy:15
    container_name: wg-easy
    hostname: wg-easy
    restart: unless-stopped
    ports:
      - "51820:51820/udp"
      - "51821:51821/tcp"
    environment:
      - PORT=51821
      - HOST=0.0.0.0
      - INSECURE=true
    volumes:
      - /etc/wireguard:/etc/wireguard
      - /lib/modules:/lib/modules:ro
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    sysctls:
      - net.ipv4.ip_forward=1
      - net.ipv4.conf.all.src_valid_mark=1
      - net.ipv6.conf.all.disable_ipv6=0
      - net.ipv6.conf.all.forwarding=1
      - net.ipv6.conf.default.forwarding=1
```

## 配置 WireGuard

- 配置用户

首次登录需要配置用户，并设置密码

![homelab-sd-wan-wg-easy-setup0.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-setup0.png)

- 配置地址

配置地址和端口，用于其他节点连接，这里选择 VPS 的 IP 地址，端口是 51820

![homelab-sd-wan-wg-easy-setup1.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-setup1.png)

- 配置允许访问的地址

配置完成后登录，点击右上角用户，进入 Admin Pannel 进行配置；在 Config 中配置 Alowed IPs 为 10.8.0.0/24，允许这个网段的节点之间互相访问，避免配置为 0.0.0.0/0 影响其他地址的访问；点击 Save 保存配置

![homelab-sd-wan-wg-easy-setup-allow-ips.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-setup-allow-ips.png)

## 配置节点

### 生成配置文件

在 wg-easy 中点击 New 创建新的节点，输入节点名称和过期时间，点击 Create Client 生成配置文件

![homelab-sd-wan-wg-easy-create-peer0.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-create-peer0.png)

![homelab-sd-wan-wg-easy-create-peer-result.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-create-peer-result.png)

### 配置节点

- 安装 WireGuard

以 Ubuntu 为例，安装 WireGuard

```bash
apt install wireguard -y
```

- 添加配置文件

下载刚才配置好的文件，登录到要添加到节点，将配置添加到 `/etc/wireguard/wg0.conf` 中，重启 WireGuard 服务

```conf
[Interface]
PrivateKey = OKbDiMlyg7b/x0lQfnEdgXXJ0pz5fB0dc8mNYmopGEg=
Address = 10.8.0.2/24
DNS = 1.1.1.1
MTU = 1420

[Peer]
PublicKey = 7KTILyzHbby1ZG272BRorYwx0I8u0K4YEK7/4nKiJxI=
PresharedKey = ngQRXQ+E+LttUFheruhmd2G7igWu6C1OguyYFSAhKvo=
AllowedIPs = 10.8.0.0/24
PersistentKeepalive = 0
Endpoint = 100.64.1.251:51820
```

- 启动 WireGuard


```bash
wg-quick up wg0
```

```bash
[#]
[#] ip link add wg0 type wireguard
[#] wg setconf wg0 /dev/fd/63
[#] ip -4 address add 10.8.0.1/24 dev wg0
[#] ip -6 address add fdcc:ad94:bacf:61a4::cafe:1/112 dev wg0
[#] ip link set mtu 1420 up dev wg0
[#] iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE; iptables -A INPUT -p udp -m udp --dport 51820 -j ACCEPT; iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; ip6tables -t nat -A POSTROUTING -s fdcc:ad94:bacf:61a4::cafe:0/112 -o eth0 -j MASQUERADE; ip6tables -A INPUT -p udp -m udp --dport 51820 -j ACCEPT; ip6tables -A FORWARD -i wg0 -j ACCEPT; ip6tables -A FORWARD -o wg0 -j ACCEPT;
```

- 查看 WireGuard 状态

```bash
wg show
```

连接成功后，会显示 WireGuard 的状态

```bash
interface: wg0
  public key: 7KTILyzHbby1ZG272BRorYwx0I8u0K4YEK7/4nKiJxI=
  private key: (hidden)
  listening port: 51820

peer: 1F7BRiqsR/GsNGw3etrjzZxGsKTrUlOKK9dloSE2Q2g=
  preshared key: (hidden)
  endpoint: [100.64.1.252]:43386
  allowed ips: 10.8.0.0/24
  latest handshake: 1 minute, 7 seconds ago
  transfer: 2.58 TiB received, 202.89 GiB sent
  persistent keepalive: every 15 seconds
```

## 添加监控 

在 wg-easy 中点击 Admin Pannel，在 General 中开启 Prometheus 监控，并添加对应的任务和面板即可看到 wg-easy 的监控信息，详细参考 [Prometheus](https://wg-easy.github.io/wg-easy/latest/advanced/metrics/prometheus/)

![homelab-sd-wan-wg-easy-monitor.png](https://img.hellowood.dev/picture/homelab-sd-wan-wg-easy-monitor.png)

## 参考文档

- [wg-easy](https://wg-easy.github.io/wg-easy/latest/)