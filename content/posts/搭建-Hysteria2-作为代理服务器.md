---
date: 2024-12-29
# description: ""
# image: ""
lastmod: 2024-12-29
showTableOfContents: false
tags:
  - Hysteria2
  - HomeLab
  - Network
title: "搭建 Hysteria2 作为代理服务器"
type: "post"
---

[Hysteria](https://v2.hysteria.network/zh/) 是一个代理工具，支持 SOCKS5、HTTP 代理、TCP/UDP 转发、Linux TProxy、TUN 等代理方式；基于魔改的 QUIC 协议和抢占式塞控制算法，Hysteria 在不稳定和容易丢包的网络环境中也能比 [Trojan](https://trojan-gfw.github.io/trojan/protocol) 有相对较好的延迟表现，这对于代理来说是非常重要的

Hysteria 由服务端和客户端组成，服务端支持 Docker、二进制等方式部署，客户端可以是 ClashX、ShellCrash 等支持 Hysteria 协议的软件，或者 Hysteria 自己的客户端

基于 Docker 容器搭建服务端，并使用运行在路由器中的 ShellCrash 作为客户端

## 服务端

因为 Hysteria 需要伪装成 HTTP/3 流量，需要一个公网 IP 和域名(如果没有域名也可以在 ZeroSSL 申请 IP 的 TLS 证书)

### 获取 SSL 证书

证书可以使用 Let's Encrypt，ZeroSSL 等免费获取，参考 [使用 Let’s Encrypt 申请 HTTPS 证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-lets-encrypt-%E7%94%B3%E8%AF%B7-https-%E8%AF%81%E4%B9%A6/)

### 部署服务端

#### 服务端配置文件

- `config/hysteria.yaml`

服务端配置文件位于 `config/` 路径下，关于配置细节可以参考 [完整服务端配置](https://v2.hysteria.network/zh/docs/advanced/Full-Server-Config/)

```yaml
listen: :443

# 伪装为 bing
masquerade:
  listenHTTP: :80
  listenHTTPS: :9443
  forceHTTPS: true
  type: proxy
  proxy:
    url: https://bing.com
    rewriteHost: true

# 用于流量分析
trafficStats:
  listen: :9999
  secret: 123456

disableUDP: false

log:
  level: debug

speedTest: true

# 带宽
bandwidth:
  up: 100 mbps
  down: 50 mbps

# DNS
resolver:
  type: tcp
  tcp:
    addr: 8.8.8.8:53
    timeout: 4s
  udp:
    addr: 8.8.4.4:53
    timeout: 4s
  tls:
    addr: 1.1.1.1:853
    timeout: 10s
    sni: cloudflare-dns.com
    insecure: false
  https:
    addr: 1.1.1.1:443
    timeout: 10s
    sni: cloudflare-dns.com
    insecure: false

tls:
  cert: /cert/hy.example.com.crt
  key: /cert/hy.example.com.key

auth:
  type: userpass
  userpass:
    - admin: 123456

# 协议嗅探
sniff:
  enable: true
  timeout: 2s
  rewriteDomain: false
  tcpPorts: 80,9443,8000-9000
  udpPorts: all
```

#### 部署

- docker-compose.yaml

申请后的证书放在 `cert/`路径下，挂载到容器中

```yaml
services:
  hysteria:
    image: tobyxdd/hysteria
    container_name: hysteria
    hostname: hysteria
    restart: unless-stopped
    network_mode: host
    environment:
      - TZ=Asia/Shanghai
      - HYSTERIA_BBR_DEBUG=1
      - HYSTERIA_LOG_LEVEL=debug
      - HYSTERIA_BRUTAL_DEBUG=1
    volumes:
      - ./cert:/cert
      - ./config/hysteria.yaml:/etc/hysteria.yaml
    command: ["server", "-c", "/etc/hysteria.yaml"]
```

使用 `docker compose up -d` 启动后便会监听 443 端口，添加 DNS 解析后访问 hy.example.com 域名会自动重定向到 bing.com

## 客户端

客户端使用 ShellCrash，安装使用参考 [ShellCrash](https://github.com/juewuy/ShellCrash)

### Hysteria 节点配置

hysteria 的配置文件放在了 GitHub Gist 中，通过 proxy-providers 提供给 Clash，配置内容如下：

```yaml
proxies:
  - name: "hy-node"
    type: hysteria2
    server: hy.example.com
    password: "admin:123456"
    port: 443
    ports: 443
    up: "50 mbps"
    down: "100 mbps"
```

### ShellCrash 配置文件

- config.yaml

```yaml
port: 7890
socks-port: 7891
redir-port: 7892
allow-lan: true
mode: rule
log-level: info
# 控制端口
external-controller: :9090
# 访问密码，建议设置
secret: "123456"

# TUN 模式，用于代理 TCP、UDP、ICMP 流量
tun:
  enable: true
  stack: system
  auto-route: true
  auto-redir: true
  auto-detect-interface: true

proxy-providers:
  # 配置文件地址，参考 https://wiki.metacubex.one/config/proxy-providers/
  hysteria:
    type: http
    url: "https://gist.githubusercontent.com/xx/raw/hysteria.yaml"
    path: ./hysteria.yaml

proxy-groups:
  - name: "PROXY"
    type: url-test
    use:
      - hysteria
    url: "http://www.gstatic.com/generate_204"
    interval: 180

rule-providers:
  reject:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt"
    path: ./ruleset/reject.yaml
    interval: 86400

  icloud:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt"
    path: ./ruleset/icloud.yaml
    interval: 86400

  apple:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt"
    path: ./ruleset/apple.yaml
    interval: 86400

  google:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt"
    path: ./ruleset/google.yaml
    interval: 86400

  proxy:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt"
    path: ./ruleset/proxy.yaml
    interval: 86400

  direct:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt"
    path: ./ruleset/direct.yaml
    interval: 86400

  private:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt"
    path: ./ruleset/private.yaml
    interval: 86400

  gfw:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt"
    path: ./ruleset/gfw.yaml
    interval: 86400

  tld-not-cn:
    type: http
    behavior: domain
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt"
    path: ./ruleset/tld-not-cn.yaml
    interval: 86400

  telegramcidr:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt"
    path: ./ruleset/telegramcidr.yaml
    interval: 86400

  cncidr:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt"
    path: ./ruleset/cncidr.yaml
    interval: 86400

  lancidr:
    type: http
    behavior: ipcidr
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt"
    path: ./ruleset/lancidr.yaml
    interval: 86400

  applications:
    type: http
    behavior: classical
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt"
    path: ./ruleset/applications.yaml
    interval: 86400

rules:
  - RULE-SET,google,PROXY
  - RULE-SET,proxy,PROXY
  - RULE-SET,telegramcidr,PROXY
  - RULE-SET,applications,DIRECT
  - RULE-SET,private,DIRECT
  - RULE-SET,reject,REJECT
  - RULE-SET,icloud,DIRECT
  - RULE-SET,apple,DIRECT
  - RULE-SET,direct,DIRECT
  - RULE-SET,lancidr,DIRECT
  - RULE-SET,cncidr,DIRECT
  - GEOIP,LAN,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,DIRECT
```

启动 ShellCrash，即可在代理中看到节点信息，协议类型是 Hysteria2

![homelab-proxy-server-hysteria2.png](https://img.hellowood.dev/picture/homelab-proxy-server-hysteria2.png)
