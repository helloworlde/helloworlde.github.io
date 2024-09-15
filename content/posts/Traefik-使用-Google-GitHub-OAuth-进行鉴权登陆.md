---
title: "Traefik 使用 Google GitHub OAuth 进行鉴权登陆"
type: post
date: 2023-02-15T21:42:38+08:00
tags:
  - Traefik
  - HomeLab
categories:
  - Traefik
  - HomeLab
series:
  - Traefik
featured: true
---


在使用 Traefik 作为 Homelab 的网关时，考虑到部分服务涉及隐私，因此需要限制用户登陆后才能使用；

Traefik 支持使用 HTTP 中间件，可以将鉴权信息转发给其他服务进行鉴权，因此，使用 [https://github.com/thomseddon/traefik-forward-auth](https://github.com/thomseddon/traefik-forward-auth) 作为鉴权的服务，该服务默认使用 Google OAuth，因此，可以通过 Google 账号登陆访问内部服务；该服务也支持任何 OAuth 标准的认证服务，如 GitHub，微软等

## 申请 OAuth 应用

在 [Google Cloud](https://console.cloud.google.com/apis/credentials) 创建新的应用，选择 "APIs and Services" -> "Credentials"，选择 "CREATE CREDENTIALS" -> "OAuth Client ID"，应用类型选择 "Web Application"，填写名称，重定向 URL 为要访问的 URL + 认证路径，traefik-forward-auth 的认证路径为 `/_oauth`

![homelab-traefik-sso-google-oauth-apply-oauth-app.png](https://img.hellowood.dev/picture/homelab-traefik-sso-google-oauth-apply-oauth-app.png)

确认后会提示 Client ID 和 Client Secret，需要保存好，作为 traefik-forward-auth 配置

## 为特定的服务添加认证

认证特定的服务，需要启动 traefik-forward-auth 服务，然后为要认证的服务添加中间件即可；如这里给 whoami 服务添加了名为 `traefik-forward-auth` 的 HTTP 中间件

这里通过将域名指向本地的方式进行测试，如在 `/etc/hosts` 中添加 `whoami.homelab.io`相关的域名作为 whoami 服务的域名：

- `/etc/hosts`

```
127.0.0.1 whoami.homelab.io
```

- docker-compose.yaml

需要将 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET` 替换为自己申请的

```yaml
version: "3"

networks:
  traefik:
    driver: bridge

services:
  traefik:
    image: traefik:v3.0
    container_name: traefik
    command: --api.insecure=true --api.dashboard=true --providers.docker
    ports:
      - "80:80"
      - "8080:8080"
    networks:
      - traefik
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  traefik-forward-auth:
    image: thomseddon/traefik-forward-auth
    container_name: "traefik-forward-auth"
    environment:
      - PROVIDERS_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - PROVIDERS_GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - SECRET=traefik
      - INSECURE_COOKIE=true # 允许 HTTP 访问
    labels:
      - "traefik.http.services.traefik-forward-auth.loadbalancer.server.port=4181"
      - "traefik.http.routers.traefik-forward-auth.middlewares=traefik-forward-auth"
      - "traefik.http.middlewares.traefik-forward-auth.forwardauth.address=http://traefik-forward-auth:4181"
      - "traefik.http.middlewares.traefik-forward-auth.forwardauth.authResponseHeaders=X-Forwarded-User"
    networks:
      - traefik

  whoami:
    image: "traefik/whoami"
    container_name: "whoami"
    labels:
      - "traefik.enable=true"
      - "traefik.http.services.whoami.loadbalancer.server.port=80"
      - "traefik.http.routers.whoami.rule=Host(`whoami.homelab.io`)"
      - "traefik.http.routers.whoami.middlewares=traefik-forward-auth"
    networks:
      - traefik
```

启动成功后，通过无痕浏览器访问 [http://whoami.homelab.io/](http://whoami.homelab.io/)，会跳转到 Google 账号登陆，登陆完成后，会重定向到 [http://whoami.homelab.io/\_oauth](http://whoami.homelab.io/_oauth) 进行认证，认证通过后再次重定向到 [http://whoami.homelab.io/](http://whoami.homelab.io/)，同时会添加名称为 `_forward_auth` 的 Cookie，作为后续访问的凭证

## 为域名添加认证

通常我们会使用子域名指向不同的服务，当有大量服务时，域名的认证配置就会非常复杂，容易漏掉；而且每个都需要登陆一次；因此需要通过给域名添加认证的方式，为所有子域名认证

- `/etc/hosts`

同样，我们还是将域名指向本地进行测试；这次添加了多个域名

```
127.0.0.1 homelab.io
127.0.0.1 auth.homelab.io
127.0.0.1 whoami.homelab.io
```

- docker-compose.yaml

配置有以下变动：

1. treafik 需要声明 entrypoints 并为其指定中间件为 `traefik-forward-auth@docker`
2. treafik-forward-auth 需要指定 `COOKIE_DOMAIN` 为上级域名，这样所有的子域名都可以访问到；同时需要指定 `AUTH_HOST`，用于认证服务的域名
3. whoami 服务删除了中间件配置
4. Google Cloud 应用到 OAuth 配置中的重定向 URL 改为 [http://auth.homelab.io/\_oauth](http://auth.homelab.io/_oauth)

这样就可以对 Traefik 下所有的服务进行认证；同时，只允许自己的账户访问，因此通过环境变量的方式指定白名单

```yaml
version: 3'

networks:
  traefik:
    driver: bridge

services:
  traefik:
    image: traefik:v3.0
    container_name: traefik
    command: |
      --api.insecure=true 
      --api.dashboard=true 
      --providers.docker 
      --entrypoints.web.address=:80 
      --entrypoints.web.http.middlewares=traefik-forward-auth@docker
    ports:
      - "80:80"
      - "8080:8080"
    labels:
      - "traefik.enable=true"
      - "traefik.http.services.traefik.loadbalancer.server.port=8080"
      - "traefik.http.routers.traefik.rule=Host(`homelab.io`)"
    networks:
      - traefik
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  traefik-forward-auth:
    image: thomseddon/traefik-forward-auth:0
    container_name: "traefik-forward-auth"
    environment:
      - PROVIDERS_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - PROVIDERS_GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - SECRET=traefik
      - INSECURE_COOKIE=true # 允许 HTTP 访问
      - COOKIE_DOMAIN=homelab.io # 指定 Cookie 的域名
      - AUTH_HOST=auth.homelab.io # 指定认证服务的域名
      - WHITELIST=a@google.com,b@google.com # 只允许白名单用户访问
    labels:
      - "traefik.http.routers.traefik-forward-auth.rule=Host(`auth.homelab.io`)"
      - "traefik.http.services.traefik-forward-auth.loadbalancer.server.port=4181"
      - "traefik.http.middlewares.traefik-forward-auth.forwardauth.address=http://traefik-forward-auth:4181"
      - "traefik.http.middlewares.traefik-forward-auth.forwardauth.authResponseHeaders=X-Forwarded-User"
    networks:
      - traefik
  whoami:
    image: "traefik/whoami"
    container_name: "whoami"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.homelab.io`)"
      - "traefik.http.services.whoami.loadbalancer.server.port=80"
    networks:
      - traefik
```

## 使用 GitHub 认证

treafik-forward-auth 支持使用其他的 OAuth 服务进行认证，只需要修改配置即可；通过环境变量指定使用的认证服务类型，以及相关的 URL

- 申请 OAuth 应用

在 GitHub -> Settings -> Developer settings 申请 OAuth 应用，指定 Callback URL 为 [http://auth.homelab.io/\_oauth](http://auth.homelab.io/_oauth)

![homelab-traefik-sso-github-oauth-apply-oauth-app.png](https://img.hellowood.dev/picture/homelab-traefik-sso-github-oauth-apply-oauth-app.png)

- docker-compose.yaml

```yaml
# ...
traefik-forward-auth:
  image: thomseddon/traefik-forward-auth:0
  container_name: "traefik-forward-auth"
  environment:
    - DEFAULT_PROVIDER=generic-oauth # 使用通用的 OAuth
    - PROVIDERS_GENERIC_OAUTH_AUTH_URL=https://github.com/login/oauth/authorize
    - PROVIDERS_GENERIC_OAUTH_CLIENT_ID=${GITHUB_CLIENT_ID}
    - PROVIDERS_GENERIC_OAUTH_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
    - PROVIDERS_GENERIC_OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
    - PROVIDERS_GENERIC_OAUTH_USER_URL=https://api.github.com/user
    - SECRET=traefik
    - INSECURE_COOKIE=true # 允许 HTTP 访问
    - COOKIE_DOMAIN=homelab.io # 指定 Cookie 的域名
    - AUTH_HOST=auth.homelab.io # 指定认证服务的域名
# ...
```
