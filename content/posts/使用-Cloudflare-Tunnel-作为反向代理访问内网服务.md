---
title: "使用 Cloudflare Tunnel 作为反向代理访问内网服务"
date: 2024-12-04T15:48:56+08:00
tags:
  - HomeLab
  - Cloudflare
featured: true
type: post
---

Cloudflare Tunnel 是一款隧道软件，可以理解为反向代理；可以快速安全地加密应用程序到任何类型基础设施的流量，如 TCP/HTTP/SSH 等，同时能够隐藏 web 服务器 IP 地址，阻止直接攻击，适用于没有公网 IP，但是又需要从公网访问内网部署的服务；详细可以参考官方文档：[Cloudflare Tunnel](https://www.cloudflare.com/zh-cn/products/tunnel/)

在 Linux 服务器上安装为例，对外提供 whoami 的 web 程序

## 创建 Tunnel

Tunnel 支持在线和本地两种配置方式；在线维护方式添加、修改比较方便，推荐使用在线的方式进行配置；

在 Zero Trust => Network => Tunnels 中选择创建 Tunnel

![homelab-cloudflare-tunnel-init-create-tunnel.png](https://img.hellowood.dev/picture/homelab-cloudflare-tunnel-init-create-tunnel.png)

![homelab-cloudflare-tunnel-init-name-tunnel.png](https://img.hellowood.dev/picture/homelab-cloudflare-tunnel-init-name-tunnel.png)

## 安装配置 Cloudflare Tunnel

Tunnel 支持二进制包或者 Docker 容器的方式进行安装；选择相应的平台，会生成安装命令，在命令后执行该命令即可

![homelab-cloudflare-tunnel-init-install.png](https://img.hellowood.dev/picture/homelab-cloudflare-tunnel-init-install.png)

如果没有对应的平台，可以在 [GitHub 仓库](https://github.com/cloudflare/cloudflared/releases)下载对应的版本，然后进行安装；以 Ubuntu 22 为例：

- 下载最新的 Cloudflared

```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
```

- 安装

```bash
dpkg -i cloudflared-linux-amd64.deb
```

- 创建 Cloudflared 服务

这样会创建并自动启动 Cloudflared 服务

```bash
sudo cloudflared service install ${TOKEN}
```

## 配置路由规则

路由规则支持在本地或者 Cloudflare 平台配置两种方式，建议在 Cloudflare 平台配置，更加灵活

- 启动服务

在本地启动一个 whoami 服务，对外暴露 8080 端口提供 web 服务；使用 docker-compose 方式启动

```yaml
services:
  whoami:
    image: "traefik/whoami"
    restart: unless-stopped
    container_name: whoami
    hostname: whoami
    ports:
      - "8080:80"
```

- 配置路由规则

点击对应的 Tunnel，选择 edit => Public Hostname => Add a public hostname 添加新的路由规则，将域名 whoami.homelab.dev 的请求转发到 [192.168.31.254:8080](192.168.31.254:8080) 这个地址，服务类型为 HTTP

这样配置之后服务是向公网开放的，如果想要通过权限控制，仅允许特定用户或者 IP 访问，可以参考 [Cloudflare-Tunnel-配置权限控制保护服务安全访问](https://blog.hellowood.dev/posts/Cloudflare-Tunnel-%E9%85%8D%E7%BD%AE%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E4%BF%9D%E6%8A%A4%E6%9C%8D%E5%8A%A1%E5%AE%89%E5%85%A8%E8%AE%BF%E9%97%AE/)

![homelab-cloudflare-tunnel-init-router-config.png](https://img.hellowood.dev/picture/homelab-cloudflare-tunnel-init-router-config.png)

- 访问路由

配置完成之后访问对应的路由即可返回相关的信息

```bash
curl https://whoami.homelab.dev

Hostname: whoami
IP: 127.0.0.1
RemoteAddr: 172.24.0.1:38002
GET / HTTP/1.1
Host: whoami.homelab.dev
User-Agent: curl/8.5.0
Accept: */*
Accept-Encoding: gzip, br
Cdn-Loop: cloudflare; loops=1
Cf-Connecting-Ip: 1.1.1.1
Cf-Visitor: {"scheme":"https"}
Cf-Warp-Tag-Id: 653af42c-aaaa-bbbb-cccc-dddddeee1234
Connection: keep-alive
X-Forwarded-For: 1.1.1.1
X-Forwarded-Host: whoami.homelab.dev
X-Forwarded-Proto: https
```

## 修改配置

Cloudflared 默认的配置在国内不一定适用，可以通过修改 Cloudflared 服务配置进行指定

自动生成的 Service 配置文件是 `/etc/systemd/system/cloudflared.service`，编辑该文件添加配置即可；按需添加以下配置：

- `--loglevel info`：指定日志级别
- `--logfile /var/log/cloudflared-tunnel.log`：日志输出文件
- `--metrics 0.0.0.0:19991`：允许暴露指标，用于监控运行信息
- `--edge-ip-version 4`：使用 IPv4 连接边缘节点(如果有 IPv6建议使用 IPv6)
- `--protocol http2`：连接协议使用 http2，默认的 quic 协议在国内丢包严重

```conf
[Unit]
Description=cloudflared
After=network.target

[Service]
TimeoutStartSec=0
Type=notify
ExecStart=/usr/bin/cloudflared --no-autoupdate tunnel --loglevel info --logfile /var/log/cloudflared-tunnel.log --metrics 0.0.0.0:19991 --edge-ip-version 6 --protocol http2 run --token ${TOKEN}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

- 重载配置并重启服务

```bash
systemctl daemon-reload
systemctl restart cloudflared
```

- 查看服务状态

```bash
systemctl status cloudflared
```

服务正确运行

```bash
● cloudflared.service - cloudflared
     Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2024-02-27 22:44:53 CST; 43min ago
   Main PID: 111 (cloudflared)
      Tasks: 9 (limit: 38155)
     Memory: 43.7M
        CPU: 8.539s
     CGroup: /system.slice/cloudflared.service
             └─111 /usr/bin/cloudflared --no-autoupdate tunnel --loglevel info --metrics 0.0.0.0:19991 --edge-ip-version 6 --protocol auto run --token ${TOKEN}
```

Cloudflare 默认和边缘节点的数据中心建立 4 个连接，但是边缘节点都在美国，使用 IPv4 连接边缘节点在国内高峰期基本是无法使用的；如下是使用 IPv4 和 IPv6 连接时有效连接的边缘节点数量，因此强烈建议使用 IPv6

![homelab-cloudflare-tunnel-metrics-ipv4-and-ipv6-compare.png](https://img.hellowood.dev/picture/homelab-cloudflare-tunnel-metrics-ipv4-and-ipv6-compare.png)

## 参考文档

- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
