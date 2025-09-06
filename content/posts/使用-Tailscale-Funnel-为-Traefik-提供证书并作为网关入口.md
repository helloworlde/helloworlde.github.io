---
title: "使用 Tailscale Funnel 为 Traefik 提供证书并作为网关入口"
date: 2024-09-23T08:34:00+08:00
lastmod: 2025-09-06
tags:
  - HomeLab
  - Network
  - Tailscale
  - Traefik
featured: true
type: post
---

[Tailscale Funnel](https://tailscale.com/kb/1223/funnel) 是 Tailscale 提供的网关工具，和 Cloudflare Tunnel 类似，支持将流量从公网路由到 Tailscale 节点设备的服务上，如 Web 服务、静态文件、SSH 等

![](https://tailscale.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ffunnel-diagram.2f3f0e10.png&w=3840&q=75)

不过 Tailscale Funnel 当前的功能并不完善，只支持路由到一个目标地址，也不支持自定义路由；如果想路由到其他服务，需要在 Funnel 后面部署一个网关服务；在 Traefik 3.1 的版本中已经支持使用 Tailscale 作为 TLS 证书的提供方，用于将 Tailscale 域名作为 Traefik 的入口

## 配置 Traefik

在 Tailscale 的节点上使用 docker-compose 部署 traefik

- 创建网络

为了方便能通过 Docker 自动发现服务路由，创建一个容器共用的网络，用于 Traefik 路由到对应服务

```bash
docker network create traefik
```

- docker-compose.yaml

需要在 docker-compose 指定网络，并挂载 `/var/run/docker.sock`，用于自动获取路由规则

```yaml
networks:
  traefik:
    external: true

services:
  traefik:
    image: traefik
    container_name: traefik
    hostname: traefik
    restart: always
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/ping"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 30s
    command:
      - "--configFile=/etc/traefik/traefik.yml"
    ports:
      - "81:80"
      - "8443:443"
      - "8080:8080"
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./traefik.yml:/etc/traefik/traefik.yml"
    networks:
      - traefik
    environment:
      - TZ=Asia/Shanghai
```

- traefik.yml

配置中定义了一个 certificatesResolvers，名称是 `default`，由 tailscale 提供；同时指定了 tls 的 certResolver 名称是 `default`，这样就会由 tailscale 提供 TLS 证书；完整的配置如下：

```yaml
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: default

certificatesResolvers:
  default:
    tailscale: {}

ping: {}

log:
  level: DEBUG

providers:
  docker:
    exposedByDefault: false
    network: traefik
```

- 启动 traefik

通过 docker compose 启动容器

```bash
docker compose up -d
```

启动后通过 IP:PORT 访问 traefik，如 [http://localhost:8080](http://localhost:8080)可以正常访问，说明 traefik 已经正确配置

![homelab-traefik-tailscale-default-configuration-homepage.png](https://img.hellowood.dev/picture/homelab-traefik-tailscale-default-configuration-homepage.png)

## 启动 Tailscale Funnel

Funnel 相关介绍参考 [Tailscale Funnel](https://tailscale.com/kb/1223/funnel)；因为 traefik 的 443 端口映射到了宿主机的 8443 端口，所以需要将请求转发到 localhost:8443，忽略证书验证，所以配置的转发地址是 [https+insecure://localhost:8443](https+insecure://localhost:8443)

```bash
tailscale funnel --bg https+insecure://localhost:8443
```

启动后会提示 funnel 监听的域名以及转发的地址

```bash
Available on the internet:

https://homelab.xxx.ts.net/
|-- proxy https+insecure://localhost:8443

Funnel started and running in the background.
To disable the proxy, run: tailscale funnel --https=443 off
```

- 查看状态

```bash
tailscale serve status
```

funnel 开启，并转发到 https://localhost:8443

```bash
# Funnel on:
#     - https://homelab.xxx.ts.net

https://homelab.xxx.ts.net (Funnel on)
|-- / proxy https+insecure://localhost:8443
```

因为还没有配置路由规则，所以此时访问 [https://homelab.xxx.ts.net](https://homelab.xxx.ts.net) 会返回 404；如果 8443 端口没有监听，则会返回 502

```bash
curl -i https://homelab.xxx.ts.net
HTTP/2 404
content-length: 0
date: Sun, 13 Oct 2024 12:34:45 GMT
lastmod: 2025-09-06
```

## 添加路由规则

配置证书后需要添加路由规则，将 Tailscale 的 tailnet 域名添加到路由规则中

### 路由到 traefik

通过给 Docker 容器添加 label 的方式配置路由规则，将根路径路由到 Traefik 的 Dashboard

- docker-compose.yaml

添加 label 配置，Host 是 Tailscale 的节点路由，格式是 `节点名称+Tailnet名称`；如节点是 homelab，Tailnet名称是 `xxx.ts.net`；同时还需要将 `/var/run/tailscale/tailscaled.sock` 挂载到容器中，用于 Tailscale 节点通信

```yaml
networks:
  traefik:
    external: true

services:
  traefik:
    image: traefik
    container_name: traefik
    hostname: traefik
    restart: always
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/ping"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 30s
    command:
      - "--configFile=/etc/traefik/traefik.yml"
    ports:
      - "81:80"
      - "8443:443"
      - "8080:8080"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`homelab.xxx.ts.net`)"
      - "traefik.http.routers.traefik.entrypoints=web,websecure"
      - "traefik.http.routers.traefik.tls=true"
      - "traefik.http.routers.traefik.tls.certresolver=default"
      - "traefik.http.services.traefik.loadbalancer.server.port=8080"
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./traefik.yml:/etc/traefik/traefik.yml"
      - /var/run/tailscale/tailscaled.sock:/var/run/tailscale/tailscaled.sock
    networks:
      - traefik
    environment:
      - TZ=Asia/Shanghai
```

启动后就可以在日志中看到使用了 tailscale 作为证书提供，并添加了对应的路由

```go
...
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/provider/tailscale/provider.go:254 > Fetched certificate for domain "homelab.xxx.ts.net" providerName=default.tailscale
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/server/configurationwatcher.go:227 > Configuration received config={"http":{},"tcp":{},"tls":{},"udp":{}} providerName=default.tailscale
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/tls/certificate.go:131 > Adding certificate for domain(s) homelab.xxx.ts.net
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/tls/tlsmanager.go:321 > No default certificate, fallback to the internal generated certificate tlsStoreName=default
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/stripprefix/strip_prefix.go:32 > Creating middleware entryPointName=traefik middlewareName=dashboard_stripprefix@internal middlewareType=StripPrefix routerName=dashboard@internal
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/observability/middleware.go:33 > Adding tracing to middleware entryPointName=traefik middlewareName=dashboard_stripprefix@internal routerName=dashboard@internal
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/redirect/redirect_regex.go:17 > Creating middleware entryPointName=traefik middlewareName=dashboard_redirect@internal middlewareType=RedirectRegex routerName=dashboard@internal
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/redirect/redirect_regex.go:18 > Setting up redirection from ^(http:\/\/(\[[\w:.]+\]|[\w\._-]+)(:\d+)?)\/$ to ${1}/dashboard/ entryPointName=traefik middlewareName=dashboard_redirect@internal middlewareType=RedirectRegex routerName=dashboard@internal
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/observability/middleware.go:33 > Adding tracing to middleware entryPointName=traefik middlewareName=dashboard_redirect@internal routerName=dashboard@internal
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/recovery/recovery.go:22 > Creating middleware entryPointName=traefik middlewareName=traefik-internal-recovery middlewareType=Recovery
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/server/service/service.go:267 > Creating load-balancer entryPointName=websecure routerName=websecure-traefik@docker serviceName=traefik@docker
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/server/service/service.go:309 > Creating server entryPointName=websecure routerName=websecure-traefik@docker serverName=da81a48dc1e3586e serviceName=traefik@docker target=http://172.18.0.2:8080
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/recovery/recovery.go:22 > Creating middleware entryPointName=websecure middlewareName=traefik-internal-recovery middlewareType=Recovery
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/middlewares/recovery/recovery.go:22 > Creating middleware entryPointName=web middlewareName=traefik-internal-recovery middlewareType=Recovery
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/server/router/tcp/manager.go:237 > Adding route for homelab.xxx.ts.net with TLS options default entryPointName=web
traefik  | 2024-10-13T18:41:34+08:00 DBG github.com/traefik/traefik/v3/pkg/server/router/tcp/manager.go:237 > Adding route for homelab.xxx.ts.net with TLS options default entryPointName=websecure
```

- 访问

此时访问 [https://homelab.xxx.ts.net](https://homelab.xxx.ts.net) 域名，可以正常访问 traefik 的 dashboard，说明配置正确 (因为 Tailscale Funnel 的公网入口部署在美国，所以访问很慢，使用同一个 Tailscale 子网下的其他设备访问会更快)

![homelab-traefik-tailscale-dashboard-route-rule-list.png](https://img.hellowood.dev/picture/homelab-traefik-tailscale-dashboard-route-rule-list.png)

### 路由到其他服务

如果服务在同一个 docker network 下的容器，可以直接通过 label 的方式配置路由规则；如果不在同一个网络下，可以通过文件的方式配置

#### 启动 whoami 服务

以 whoami 服务为例，通过 docker 容器启动该服务

- docker-compose

```yaml
services:
  whoami:
    image: "traefik/whoami"
    restart: unless-stopped
    container_name: "whoami"
    hostname: whoami
    ports:
      - "8081:80"
```

启动后访问 8081 端口，能正常返回信息

```bash
curl -i 192.168.31.2:8081
```

```bash
HTTP/1.1 200 OK
Date: Sun, 13 Oct 2024 12:49:33 GMT
Content-Length: 167
Content-Type: text/plain; charset=utf-8

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.18.0.3
RemoteAddr: 192.168.31.2:42734
GET / HTTP/1.1
Host: 192.168.31.2:8081
User-Agent: curl/8.5.0
Accept: */*
```

#### 创建路由规则

- router/whoami.yml

创建 router 文件夹，用于存放路由规则，并在 router 路径下配置 whoami 服务的路由

```yaml
http:
  routers:
    whoami:
      entryPoints:
        - "websecure"
        - "web"
      rule: "Host(`homelab.xxx.ts.net`) && Path(`/whoami`)"
      service: "whoami"
      tls:
        certResolver: default

  services:
    whoami:
      loadBalancer:
        servers:
          - url: "http://192.168.31.2:8081"
```

#### 挂载路由规则

修改 traefik 的配置文件，将 router 路径挂载到容器中

- docker-compose.yaml

```yaml
services:
  traefik:
    image: traefik
    # ...
    volumes:
      # ...
      - "./router:/etc/traefik/router"
      # ...
```

- traefik.yml

添加文件路由规则的配置

```yaml
# ...
providers:
  docker:
    exposedByDefault: false
    network: traefik
  # 添加文件配置
  file:
    directory: /etc/traefik/router
    watch: true
    debugLogGeneratedTemplate: true
```

此时的路由规则如下：

![homelab-traefik-tailscale-custom-route-rule-list.png](https://img.hellowood.dev/picture/homelab-traefik-tailscale-custom-route-rule-list.png)

#### 访问

重新启动 traefik 容器，访问 [https://homelab.xxx.ts.net/whoami](https://homelab.xxx.ts.net/whoami)

```bash
curl -i https://homelab.xxx.ts.net/whoami
```

可以正确转发并返回访问信息，说明路由规则配置正确

```bash
HTTP/2 200
content-type: text/plain; charset=utf-8
date: Sun, 13 Oct 2024 13:03:11 GMT
lastmod: 2025-09-06
content-length: 364

Hostname: whoami
IP: 127.0.0.1
IP: 172.20.0.5
RemoteAddr: 192.168.31.2:43242
GET /whoami HTTP/1.1
Host: homelab.xxx.ts.net
User-Agent: curl/8.5.0
Accept: */*
Accept-Encoding: gzip
X-Forwarded-For: 172.18.0.1
X-Forwarded-Host: homelab.xxx.ts.net
X-Forwarded-Port: 443
X-Forwarded-Proto: https
X-Forwarded-Server: traefik
X-Real-Ip: 172.18.0.1
```
