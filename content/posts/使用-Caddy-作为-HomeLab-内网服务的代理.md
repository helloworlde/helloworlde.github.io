---
date: 2025-07-20
# description: ""
# image: ""
lastmod: 2025-07-20
showTableOfContents: false
tags:
  - Caddy
  - HomeLab
featured: true
title: "使用 Caddy 作为 HomeLab 内网服务的代理"
type: "post"
---

HomeLab 部署的服务越来越多，部署在不同的服务器上，还需要记住对应的端口，通过 IP:Port 的方式访问起来非常不方便，因此需要通过反向代理服务，通过域名的方式进行访问；代理服务器常用的有 Nginx、Traefik、Caddy 等

[Caddy](https://caddyserver.com/) 是一款基于 Go 语言编写的 Web 服务器或代理，支持动态修改配置，自动申请 HTTPS 证书等功能，和 Traefik 相比更简单，更适用于 HomeLab 场景

通过 Caddy 代理 PVE 服务，访问地址为 `https://pve.svc.homelab`：
![homelab-caddy-proxy-pve-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-proxy-pve-homepage.png)

## 部署

使用 docker-compose 部署

### 启动 Caddy

- Caddyfile 

Caddy 默认使用 Caddyfile 作为配置文件，Caddyfile 语法和 Nginx 类似，可以参考 [Caddyfile 语法](https://caddyserver.com/docs/caddyfile)；先配置一个最简单的

```conf
{
    log {
        output stdout
        format console
        level info
    }
    admin 0.0.0.0:2019
}

http://localhost:80 {
    respond "hello caddy"
}

https://localhost:443 {
    tls internal
    respond "hello https caddy"
}
```

- docker-compose.yml

```yaml
services:
  caddy:
    image: caddy
    container_name: caddy
    ports:
      - "80:80" #http 
      - "443:443" # https
      - "2019:2019" # admin
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./data:/data/caddy # 证书等信息
      - ./config:/config/caddy # 路由信息
      - ./router:/etc/caddy/router # 路由配置文件
    restart: unless-stopped
```

通过 `docker compose up` 启动

### 测试路由 

- 测试 80 端口

```bash
curl -i http://localhost:80
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Server: Caddy
Date: Tue, 29 Jul 2025 15:00:50 GMT
Content-Length: 11

hello caddy
```

- 测试 443 端口

```bash
curl -i -k https://localhost:443
HTTP/2 200
alt-svc: h3=":443"; ma=2592000
content-type: text/plain; charset=utf-8
server: Caddy
content-length: 17
date: Tue, 29 Jul 2025 15:00:21 GMT

hello https caddy#
```

- 测试 admin 端口

```bash
curl -i http://localhost:2019/config/
HTTP/1.1 200 OK
Content-Type: application/json
Etag: "/config/ cb0f204627d2880f"
Date: Tue, 29 Jul 2025 15:01:20 GMT
Content-Length: 672

{"admin":{"listen":"0.0.0.0:2019"},"apps":{"http":{"servers":{"srv0":{"listen":[":443"],"routes":[{"handle":[{"handler":"subroute","routes":[{"handle":[{"body":"hello https caddy","handler":"static_response"}]}]}],"match":[{"host":["localhost"]}],"terminal":true}]},"srv1":{"listen":[":80"],"routes":[{"handle":[{"handler":"subroute","routes":[{"handle":[{"body":"hello caddy","handler":"static_response"}]}]}],"match":[{"host":["localhost"]}],"terminal":true}]}}},"tls":{"automation":{"policies":[{"issuers":[{"module":"internal"}],"subjects":["localhost"]}]}}},"logging":{"logs":{"default":{"encoder":{"format":"console"},"level":"info","writer":{"output":"stdout"}}}}}
```

可以正常返回说明路由配置没有问题

## 配置路由

### 修改 DNS

内网部署的服务使用 `svc.homelab` 结尾的域名，如果内网有多个设备需要访问，则需要修改 DNS 服务器，将所有的 `svc.homelab` 结尾的域名解析到 Caddy 服务器的 IP 地址；可以在 AdGuard 或者 OpenWrt 中修改；如果仅在本地使用，则可以直接修改 `/etc/hosts`：

```bash
127.0.0.1 caddy.svc.homelab 
```

### 配置路由

- Caddyfile

修改 Caddyfile，配置 `*.svc.homelab` 的路由规则；为了维护方便，将具体的路由分不同的文件配置，通过 `import` 导入
通常 HTTP 的路由就够了，HTTPS 只用于 PVE 等个别必须使用 HTTPS 访问的服务

```conf
{
    log {
        output stdout
        format console
        level info
    }
    admin 0.0.0.0:2019
}

http://*.svc.homelab:80, https://*.svc.homelab:443 {
    tls internal
    # 为了维护方便，将具体的路由分不同的文件配置
    import /etc/caddy/router/*.conf

    handle {
        respond "unknown service" 404
    }
}
```

- router/saas.conf

saas 中配置了一些自己部署的服务，如 OpenWrt、PVE 等，通过请求的 host 匹配；

建议不同的服务使用不同的 host，如果通过 path 转发，一些服务的前端页面可能无法正确资源和路由导致无法使用

```conf
    # 路由器
    @router host router.svc.homelab
    handle @router {
        reverse_proxy 10.0.0.1
    }
  
    # PVE，需要用 https 转发
    @pve host pve.svc.homelab
    handle @pve {
        reverse_proxy https://10.0.0.2:8006 {
            # 忽略 https 证书验证
            transport http {
                tls_insecure_skip_verify
            }
        }
    }
```

这样访问 PVE 就可以通过 `https://pve.svc.homelab` 访问


## 动态更新路由

caddy 支持动态更新路由，每次修改路由配置后，进入到 Caddy 容器中执行 `caddy reload` 即可：

```bash
caddy reload --config /etc/caddy/Caddyfile
```