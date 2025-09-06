---
date: 2025-07-30
# description: ""
# image: ""
lastmod: 2025-08-02
tags:
  - HomeLab
  - Cloudflare
featured: true
type: post
title: "使用 Cloudflare 和 Caddy 代理 HomeLab 服务"
---

HomeLab 内网使用 Caddy 进行代理，外部访问通过 Cloudflare 将请求转发给 Caddy，然后再由 Caddy 转发给对应的服务，这样的好处是服务变动只需要配置一次 Caddy 的路由即可

## 使用 Cloudflare Tunnel 将服务转发给 Caddy

关于 Cloudflare Tunnel 的安装使用可以参考 [使用 Cloudflare Tunnel 作为反向代理访问内网服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-cloudflare-tunnel-%E4%BD%9C%E4%B8%BA%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86%E8%AE%BF%E9%97%AE%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1/)

关于 Caddy 的安装使用参考 [使用 Caddy 作为反向代理访问内网服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)

以 traefik/whoami 服务为例

### 部署 whoami 服务

traefik/whoami 是一个可以返回请求信息的 Go 服务，用 docker-compose 部署

```yaml
services:
  whoami:
    image: traefik/whoami
    restart: unless-stopped
    container_name: whoami
    hostname: whoami
    ports:
      - 8081:80
```

启动后请求 `http://localhost:8081` 会返回请求信息

```bash
curl localhost:8081

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.20.0.4
RemoteAddr: 172.20.0.1:59018
GET / HTTP/1.1
Host: localhost:8081
User-Agent: curl/8.9.1
Accept: */*
```

### 配置 Caddy

在 Caddyfile 中新增一条路由规则，将 whoami.homelab.dev 转发给 whoami 服务

```conf
http://whoami.svc.homelab {
    reverse_proxy 10.0.0.3:8081
}
```

重启或重新加载 Caddy 使路由生效，然后使用 curl 访问 `http://whoami.svc.homelab`

```bash
curl -i http://whoami.svc.homelab
HTTP/1.1 200 OK
Content-Length: 289
Content-Type: text/plain; charset=utf-8
Date: Wed, 30 Jul 2025 01:22:32 GMT
Via: 1.1 Caddy

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.20.0.4
RemoteAddr: 10.0.0.4:58012
GET / HTTP/1.1
Host: whoami.svc.homelab
User-Agent: curl/8.9.1
Accept: */*
Accept-Encoding: gzip
Via: 1.1 Caddy
X-Forwarded-For: 172.18.0.1
X-Forwarded-Host: whoami.svc.homelab
X-Forwarded-Proto: http
```

### 配置 Cloudflare Tunnel

修改 Cloduflare Tunnel 的路由，将 `whoami` 主机名转发到 `whoami.svc.homelab`，同时需要在 HTTP 设置中配置 HTTP 主机头为 `whoami.svc.homelab`，否则在经过 Tunnel 后没有 host header, Caddy 不知道转发到哪里

![homelab-tunnel-to-caddy-cloudflare-edit-tunnel-router.png](https://img.hellowood.dev/picture/homelab-tunnel-to-caddy-cloudflare-edit-tunnel-router.png)

然后请求 `https://whoami.example.com`, 会返回 Caddy 转发的 whoami 服务的信息

```bash
curl https://whoami.hellowood.dev/

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.20.0.4
RemoteAddr: 10.0.0.4:49670
GET / HTTP/1.1
Host: whoami.svc.homelab
User-Agent: curl/8.9.1
Accept: */*
Accept-Encoding: gzip, br
Cdn-Loop: cloudflare; loops=1
Cf-Ipcountry: CN
Cf-Visitor: {"scheme":"https"}
Via: 1.1 Caddy
X-Forwarded-For: 10.0.0.4
X-Forwarded-Host: whoami.svc.homelab
X-Forwarded-Proto: http
```

### HTTPS 服务转发

HTTPS 的服务如 PVE 的管理页面，需要通过 HTTPS 转发，并忽略 HTTPS 证书验证

- Tunnel 指定 Host 并忽略 TLS 证书验证

Tunnel 的服务类型选择 HTTPS，然后转发给 pve.svc.homelab，在 TLS 配置中选择无 TLS 验证，这样就会忽略 HTTPS 证书错误；同样在 HTTP 设置中配置 HTTP 主机头为 pve.svc.homelab

- Caddy 配置忽略 HTTPS 证书验证

通过 `tls_insecure_skip_verify` 忽略 HTTPS 证书错误

```conf
http://pve.svc.homelab {
    reverse_proxy https://10.0.0.3:8006 {
        transport http {
            tls_insecure_skip_verify
        }
    }
}
```
