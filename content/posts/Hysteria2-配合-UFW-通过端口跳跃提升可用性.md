---
date: 2026-03-01
description: "Hysteria2 结合 UFW 实现端口跳跃与高可用部署，优化网络穿透性能，提升服务器访问稳定性"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
tags:
  - Hysteria2
  - HomeLab
  - Network
title: "Hysteria2 配合 UFW 通过端口跳跃提升可用性"
slug: "hysteria2-ufw-port-hopping-availability"
aliases:
  - "/posts/hysteria2-配合-ufw-通过端口跳跃提升可用性/"
type: "post"
---

Hysteria2 支持端口跳跃，通过端口跳跃可以提升可用性，当一个端口被运营商阻塞时，可以切换到另一个端口继续使用，提升代理的稳定性。本方案结合 UFW 实现端口跳跃，通过端口跳跃提升可用性

关于 Hysteria2 的配置，可以参考 [使用 Docker 在 Linux 服务器搭建 Hysteria2 作为代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-docker-%E5%9C%A8-linux-%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%90%AD%E5%BB%BA-hysteria2-%E4%BD%9C%E4%B8%BA%E4%BB%A3%E7%90%86/)

## 服务端

服务端需要使用 iptables 或者 nftables 通过 DNAT 将端口转发到服务器的监听端口，可以参考 [端口跳跃](https://v2.hysteria.network/zh/docs/advanced/Port-Hopping/)，以使用 iptables 的 UFW 为例：

### 开启端口转发

编辑 `/etc/sysctl.conf`，将以下配置添加到文件中

```bash
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

执行以下命令使配置生效

```bash
sysctl -p
```

### 添加 NAT 转发规则

需要将跳跃的端口添加到 ufw 的 NAT 转发规则中，编辑 `/etc/ufw/before.rules`，将以下内容添加到文件的最前面，注意将网卡名称替换为实际的网卡名称；这样 Hysteria2 实际只监听 9443 一个端口，但客户端可以随机使用 20000-30000 范围内任意端口发包，由 iptables 在内核层透明转发

```bash
# hysteria2 端口跳跃配置，将 UDP 协议 20000-30000 端口转发到 9443 端口，网卡为 enp3s0
*nat
:PREROUTING ACCEPT [0:0]
-A PREROUTING -i enp3s0 -p udp --dport 20000:30000 -j REDIRECT --to-ports 9443
COMMIT
```

### 配置防火墙

因为 iptables PREROUTING 允许在数据包到达 INPUT 链之前对其进行修改， 所以 UFW 过滤时看到的已经是转换后的端口，因此防火墙仅需要配置放行 9443 端口即可：

```bash
ufw allow from 10.0.0.0/16 to any port 9443 proto udp
```

## 客户端配置

### ClashX Meta

通过 proxy-providers 方式配置，详细可以参考 [使用 Docker 部署 Clash Premium](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8docker%E9%83%A8%E7%BD%B2clash-premium/)

```yaml
proxies:
  - name: "hysteria2"
    type: hysteria2
    server: hysteria2.example.com
    password: password
    port: 9443
    ports: 20000-30000 # 随机使用 20000-30000 范围内任意端口发包
    up: "100 Mbps"
    down: "100 Mbps"
```
