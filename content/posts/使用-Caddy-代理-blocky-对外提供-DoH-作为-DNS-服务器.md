---
date: 2025-08-02
# description: ""
# image: ""
lastmod: 2025-08-02
showTableOfContents: false
tags:
  - HomeLab
  - Caddy
  - Cert
featured: true
type: post
title: "使用 Caddy 代理 Blocky 对外提供 DoH 作为 DNS 服务器"
---

因为国内的 DNS 都开始限速，频繁出现 DNS 等待数分钟甚至无响应的情况，国外的 DNS 响应又比较慢，非常影响使用；刚好阿里云的服务器内网 DNS 不限速，并且网络延迟只有10ms，可以将其作为 DoH 服务器，用于提供 DNS 查询

在服务器部署 Caddy 对外提供 DoH 接口，然后将请求转发到 Blocky 服务，Blocky 服务再将 DNS 请求转发给阿里云的服务器的 DNS，间接实现 DoH 服务；经过测试，平均响应延迟在 16ms 左右，比直接使用阿里云的公网 DNS 更快更稳定

![homelab-dns-server-doh-caddy-with-blocky-adguard-result.png](https://img.hellowood.dev/picture/homelab-dns-server-doh-caddy-with-blocky-adguard-result.png)


可选择的 DoH 服务有 AdGuard、Blocky、Kind、CordDNS 等，因为需要过滤广告，支持 HTTP 查询，并且需要可观测，所以选择 Blocky 作为 DoH 服务；整体的请求链路是：

```bash
客户端 -(https)-> Caddy -(http)-> Blocky -(udp)-> 阿里云内网 DNS
```


关于 Caddy 的使用可以参考 [使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)，HTTPS 证书使用 ZeroSSL 提供的 IP 证书，可以参考 [阿里云服务器使用 Caddy 和 ZeroSSL 提供的 IP 证书为服务开启 HTTPS](https://blog.hellowood.dev/posts/%E9%98%BF%E9%87%8C%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8caddy-%E5%92%8C-zerossl-%E6%8F%90%E4%BE%9B%E7%9A%84-ip-%E8%AF%81%E4%B9%A6%E4%B8%BA%E6%9C%8D%E5%8A%A1%E5%BC%80%E5%90%AF-https/)


## 部署 Blocky

- 查找服务器使用的 DNS

```bash
resolvectl status
```

使用 `resolvectl` 查看系统的 DNS 信息，`100.100.2.136` 和 `100.100.2.138` 就是默认的 DNS 服务器地址，这个地址需要作为 blocky 的上游

```bash
Global
         Protocols: -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
  resolv.conf mode: stub

Link 2 (eth0)
    Current Scopes: DNS
         Protocols: +DefaultRoute -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 100.100.2.136
       DNS Servers: 100.100.2.136 100.100.2.138
```

- 配置 blocky

配置 blocky 的配置文件 `config.yml`，具体可以参考 [Configuration](https://0xerr0r.github.io/blocky/latest/configuration/)

```yaml
upstreams:
  groups:
    default:
      - 100.100.2.138
      - 100.100.2.136
  timeout: 1s

# 配置广告过滤
blocking:
  denylists:
    ads:
      - https://proxy.hellowood.dev/https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
  clientGroupsBlock:
    default:
      - ads

# 监听端口
ports:
  dns: 153 # 不使用UDP，改为其他端口
  http: 4000 #用于提供 DoH/Prometheus 等

# 指标
prometheus:
  enable: true
  path: /metrics

# 用于解析 DoH 域名
bootstrapDns:
  - upstream: tcp+udp:1.1.1.1
  - upstream: tcp+udp:8.8.8.8

# 记录请求日志
queryLog:
  type: csv
  target: /logs
  logRetentionDays: 7
  fields:
  - clientIP
  - question
  - duration
  - responseAnswer
  - responseReason
  flushInterval: 30s
```

- docker-compose.yml

使用 docker compose 部署，将 4000 端口映射到宿主机，同时将配置文件和访问日志目录挂载到容器

```yaml
services:
  blocky:
    image: ghcr.io/0xerr0r/blocky:latest
    container_name: blocky
    ports:
      - "4000:4000"
    volumes:
      - ./config.yml:/app/config.yml
      - ./log:/logs
    restart: unless-stopped
```

- 访问验证

使用 DoH 访问 `http://localhost:4000`，查询 `example.com` 验证 DNS 是否生效

```bash
curl -H 'accept: application/dns-message' 'http://localhost:4000/dns-query?dns=q80BAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB' | hexdump
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   143  100   143    0     0  44409      0 --:--:-- --:--:-- --:--:-- 47666
0000000 cdab 8081 0100 0400 0000 0000 7703 7777
0000010 6507 6178 706d 656c 6303 6d6f 0000 0001
0000020 c001 000c 0005 0001 0000 000a 0322 7777
0000030 0777 7865 6d61 6c70 0665 6f63 2d6d 3476
0000040 6509 6764 7365 6975 6574 6e03 7465 c000
0000050 002d 0005 0001 0000 000a 0514 3161 3234
0000060 0432 7364 7263 6106 616b 616d c069 c04a
0000070 005b 0001 0001 0000 000a 1704 46dc c029
0000080 005b 0001 0001 0000 000a 1704 46dc 002e
000008f
```

## 配置 Caddy 代理

DoH 需要使用 HTTPS 访问，需要 Caddy 配置 HTTPS 证书，参考 [阿里云服务器使用 Caddy 和 ZeroSSL 提供的 IP 证书为服务开启 HTTPS](https://blog.hellowood.dev/posts/%E9%98%BF%E9%87%8C%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8caddy-%E5%92%8C-zerossl-%E6%8F%90%E4%BE%9B%E7%9A%84-ip-%E8%AF%81%E4%B9%A6%E4%B8%BA%E6%9C%8D%E5%8A%A1%E5%BC%80%E5%90%AF-https/)

- docker-compose.yml

```yaml
services:
  caddy:
    image: caddy
    container_name: caddy
    ports:
      - "10443:10443" # https
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./static:/var/www/html/.well-known/pki-validation # 认证文件
      - ./certs:/certs # TLS 证书
    extra_hosts:
      - "host.docker.internal:host-gateway" # 用于容器内访问宿主机
    restart: unless-stopped
```

- Caddyfile

```conf
{
    debug
    log {
        output stdout
        format console
    }
    default_sni 100.0.0.2
}

# 监听 10443 端口
https://100.0.0.2:10443 {
    tls /certs/fullchain.crt /certs/private.key
    # 将 dns-query 路径转发给 blocky 服务
    route /dns-query* {
        reverse_proxy http://host.docker.internal:4000
    }
}
```

配置完成后启动 blocky 和 caddy 服务

## 查询验证

```bash
curl -H 'accept: application/dns-message' 'https://100.0.0.2:10443/dns-query?dns=q80BAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB' | hexdump
```

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   143  100   143    0     0   2353      0 --:--:-- --:--:-- --:--:--  2383
0000000 cdab 8081 0100 0400 0000 0000 7703 7777
0000010 6507 6178 706d 656c 6303 6d6f 0000 0001
0000020 c001 000c 0005 0001 0000 000a 0322 7777
0000030 0777 7865 6d61 6c70 0665 6f63 2d6d 3476
0000040 6509 6764 7365 6975 6574 6e03 7465 c000
0000050 002d 0005 0001 0000 000a 0514 3161 3234
0000060 0432 7364 7263 6106 616b 616d c069 c04a
0000070 005b 0001 0001 0000 000a 1704 0530 c011
0000080 005b 0001 0001 0000 000a 1704 0530 0004
000008f
```

这样就可以将 `https://100.0.0.2:10443/dns-query` 作为 AdGuard、Clash、Dae 等工具的 DNS 服务器了:

![homelab-dns-server-doh-caddy-with-blocky-adguard-result.png](https://img.hellowood.dev/picture/homelab-dns-server-doh-caddy-with-blocky-adguard-result.png)
