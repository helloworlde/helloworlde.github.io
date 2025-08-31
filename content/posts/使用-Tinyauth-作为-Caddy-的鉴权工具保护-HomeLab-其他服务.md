---
date: 2025-08-30
# description: ""
# image: ""
lastmod: 2025-08-30
showTableOfContents: false
title: "使用 Tinyauth 作为 Caddy 的鉴权工具保护 HomeLab 其他服务"
type: "post"
tags:
  - Caddy
  - HomeLab
  - Gateway
  - Auth
featured: true
---

[Tinyauth](https://tinyauth.app/) 是一个非常轻量级的鉴权工具，相比 Authelia/Authentik/Keycloack 等更适合 HomeLab 使用；同时支持使用 OIDC 的鉴权方式，可以结合 GitHub/Google 等支持 OIDC 的第三方账号进行登录

![homelab-caddy-auth-tinyauth-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-auth-tinyauth-homepage.png)

## 部署 Tinyauth

对 Caddy 和 Tinyauth 解耦，分别使用 Docker Compose 进行部署；关于 Caddy 的安装使用可以参考[使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)

### 创建用户

Tinyauth 支持多种登录方式，如 GitHub/Google 账户，或者单独创建用户

```bash
docker run -i -t --rm ghcr.io/steveiliop56/tinyauth:v3 user create --interactive
```

将会显示交互界面，输入用户名和密码，并选择使用 Docker 的格式化输出：

```bash
  Username
  > admin

  Password
  > 123456

┃ Format the output for docker?
┃ > Yes
┃   No

```

将得到用户名和密码，这个信息后面会作为 Tinyauth 的环境变量使用；如果有多个用户，可以重复执行上面的命令创建

```bash
2025-08-31T14:48:50Z INF Creating user docker=true password=123456 username=admin
2025-08-31T14:48:50Z INF User created user=admin:$$2a$$10$$XjPRGRi5clgDD16LRaeEvetazg8roIUpS0dUOrqgFL51uD25ZCkl6
```

### 生成 SECRET

Tinyauth 需要一个 SECRET 用于加密 Cookie，可以使用下面的命令生成一个 32 位的随机字符串

```bash
openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32 && echo
```

将得到长度为 32 的随机字符串：

```bash
LcR2VFcDatCXSw2h7hkoCARAfUqVvAkG
```

### 部署 Tinyauth

使用 Docker Compose 部署 Tinyauth，环境变量需要使用上面生成的用户和 SECRET；

如果需要使用 GitHub 或者 Google 作为登录方式，可以参考官方文档[OAuth with Github OAuth](https://tinyauth.app/docs/guides/github-oauth) 和 [OAuth with Google](https://tinyauth.app/docs/guides/google-oauth) 进行配置；将对应的 Client ID 和 Secret 作为环境变量传入即可

- docker-compose.yaml

APP_URL 需要设置为 Tinyauth 的访问地址，和 Caddy 配合使用时，可以通过指定 DNS 解析或者配置 hosts 文件的方式进行访问；关于环境变量的详细说明可以参考[Configuration](https://tinyauth.app/docs/reference/configuration)

```yaml
services:
  tinyauth:
    container_name: tinyauth
    image: ghcr.io/steveiliop56/tinyauth:v3
    restart: unless-stopped
    ports:
      - 3000:3000
    environment:
      - APP_URL=http://auth.svc.homelab # Tinyauth 的访问地址
      - SECRET=LcR2VFcDatCXSw2h7hkoCARAfUqVvAkG # 上面生成的 SECRET
      - USERS=admin:$$2a$$10$$XjPRGRi5clgDD16LRaeEvetazg8roIUpS0dUOrqgFL51uD25ZCkl6 # 上面创建的用户，如果有多个用户使用逗号分隔
      - GENERIC_SKIP_SSL=true # 忽略ssl 证书错误
      - OAUTH_AUTO_REDIRECT=none # 关闭自动跳转
      # - GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com # Google OIDC 的 Client ID 和 Secret
      # - GOOGLE_CLIENT_SECRET=xxx
      # - GITHUB_CLIENT_ID=xxxx # GitHub OIDC 的 Client ID 和 Secret
      # - GITHUB_CLIENT_SECRET=xxxx
```

启动后可以通过访问对应的 3000 端口即可看到 Tinyauth 的登录页面

## 配置 Caddy 使用 Tinyauth 进行鉴权

在 Caddy 的配置文件中添加 Tinyauth 的鉴权配置，详细配置可以参考文档[Caddy](https://tinyauth.app/docs/community/caddy)

### 为特定路由添加 Tinyauth 的鉴权配置

以 who.svc.homelab 为例，配置 Caddy 使用 Tinyauth 进行鉴权

- Caddyfile

```conf
who.svc.homelab {
    tls internal
    route {
      forward_auth http://auth.svc.homelab:3000 {
        uri /api/auth/caddy
        copy_headers Remote-User Remote-Name Remote-Email Remote-Groups
      }
      reverse_proxy 10.0.0.2:8081
    }
}
```

这样配置之后访问 who.svc.homelab 时会先检查是否登录，如果没有登录会自动跳转到 Tinyauth 的登录页面，登录成功后会跳转回 who.svc.homelab 页面继续访问

![homelab-caddy-auth-tinyauth-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-auth-tinyauth-homepage.png)

### 给多个路由添加鉴权配置

如果有多个路由需要添加鉴权配置，可以使用 Caddy 的 `import` 功能，将鉴权作为公共配置片段进行引用

- Caddyfile

```conf
(tinyauth_forwarder) {
	forward_auth http://auth.svc.homelab:3000 {
		uri /api/auth/caddy
	}
}

who.svc.homelab {
	tls internal
	route {
		import tinyauth_forwarder
		reverse_proxy 10.0.0.2:8081
	}
}

*.example.com {
	tls internal
	route {
		import tinyauth_forwarder
		reverse_proxy 10.0.0.3:3000
	}
}
```

这样就可以给多个路由添加鉴权配置，使用统一的鉴权规则，方便统一管理

## 参考文档

- [Getting Started](https://tinyauth.app/docs/getting-started)
- [Configuration](https://tinyauth.app/docs/reference/configuration)
