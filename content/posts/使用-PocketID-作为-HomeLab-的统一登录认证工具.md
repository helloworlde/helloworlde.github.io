---
date: 2025-08-31
# description: ""
# image: ""
lastmod: 2025-09-02
showTableOfContents: false
title: "使用 PocketID 作为 HomeLab 的统一登录认证工具"
type: "post"
tags:
  - Caddy
  - HomeLab
  - Gateway
  - Auth
featured: true
---

[PocketID](https://pocket-id.org/) 是一个轻量、只支持通行密钥(passkey)的用户管理系统，支持 OIDC 协议，和 GitHub/Google/Microsoft 等一样可以作为身份认证提供者；同时可以给 Tinyauth/Grafana/Memos/Beszel 等 HomeLab 服务提供 OIDC 的身份认证

![homelab-caddy-auth-pocketid-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-homepage.png)

PocketID 只支持通行密钥(passkey) 的方式进行登录，因此要求 PocketID 服务的访问地址必须是 HTTPS 的；如果是在本地部署，可以使用 Cloudflare Tunnel 转发，或者通过 Split DNS + Caddy 代理的方式进行访问；关于 Split DNS 可以参考 [使用 Split DNS 打造 HomeLab 内网和公网一致的访问体验](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-split-dns-%E6%89%93%E9%80%A0-homelab-%E5%86%85%E7%BD%91%E5%92%8C%E5%85%AC%E7%BD%91%E4%B8%80%E8%87%B4%E7%9A%84%E8%AE%BF%E9%97%AE%E4%BD%93%E9%AA%8C/)

以 PocketID 和 Tinyauth 为例，使用 PocketID 作为统一的登录认证工具，配合 Tinyauth 保护 HomeLab 内网的其他服务

关于 Caddy 和 Tinyauth 的安装使用可以参考[使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/) 和 [使用 Tinyauth 作为 Caddy 的鉴权工具保护 HomeLab 其他服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-tinyauth-%E4%BD%9C%E4%B8%BA-caddy-%E7%9A%84%E9%89%B4%E6%9D%83%E5%B7%A5%E5%85%B7%E4%BF%9D%E6%8A%A4-homelab-%E5%85%B6%E4%BB%96%E6%9C%8D%E5%8A%A1/)

## 部署 PocketID

PocketID 的数据支持 SQLite 和 PostgreSQL 两种方式进行保存，因为用户和 OIDC 客户端信息会影响到所有相关使用 PocketID 的服务，因此强烈建议使用 PostgreSQL 保存数据，并对数据进行定期、多副本备份

### 创建 PG 数据库

PG 数据库可以使用 docker 部署，或者使用 [Supabase](https://supabase.com/) 等 SaaS 服务

- 创建 pocketid 数据库

```sql
CREATE DATABASE pocketid;
```

- 创建 pocketid 用户，并授权

```sql
CREATE USER pocketid WITH PASSWORD '123456';

GRANT ALL PRIVILEGES ON DATABASE pocketid TO pocketid;
GRANT ALL PRIVILEGES ON SCHEMA public TO pocketid;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO pocketid;
```

### 部署 PocketID

- 生成加密的 KEY

可以使用下面的命令生成一个 32 位的随机字符串，用于加密数据

```bash
openssl rand -base64 32

jen/Xz9GUbrS6BXkj+EcFjri6ZCRzHoO8+rPkRbef3Q=
```

- docker-compose.yaml

如果不使用 PG 数据库，可以将 `DB_PROVIDER` 设置为 `sqlite`，这样会在 `./data` 目录下生成 `pocket-id.db` 的 SQLite 数据库文件

另外需要注意的是 passkey 设计只支持 HTTPS 的访问，因此 `APP_URL` 需要设置为 HTTPS 的地址，并且证书必须是可信的，否则其他服务无法使用；可以通过 mkcert 生成证书并信任，或者使用 Cloudflare Tunnel 等反向代理工具代理

```yaml
services:
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id
    container_name: pocketid
    hostname: pocketid
    restart: unless-stopped
    ports:
      - 1411:1411
    volumes:
      - "./data:/app/data" # 用于保存 SQLite 数据库文件、图片、GEO 信息
    extra_hosts:
      - "host.docker.internal:host-gateway"
    healthcheck:
      test: ["CMD", "/app/pocket-id", "healthcheck"]
      interval: 1m30s
      timeout: 5s
      retries: 2
      start_period: 10s
    environment:
      - APP_URL=https://pocketid.example.com # PocketID 的访问地址
      - TRUST_PROXY=true # 如果通过反向代理访问，需要设置为 true
      - ENCRYPTION_KEY=jen/Xz9GUbrS6BXkj+EcFjri6ZCRzHoO8+rPkRbef3Q= # 上面生成的加密 KEY
      - ALLOW_USER_SIGNUPS=withToken # 仅允许邀请的用户注册
      - DB_PROVIDER=postgres # 数据库类型，支持 sqlite 和 postgres
      - DB_CONNECTION_STRING=postgres://pocketid:123456@100.0.0.2:5432/pocketid?sslmode=disable # PostgreSQL 的连接字符串
```

然后启动 PocketID，会自动创建数据表，等待启动成功后访问 https://pocketid.example.com 即可看到 PocketID 的登录页面

![homelab-caddy-auth-pocketid-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-homepage.png)

### 配置 PocketID

第一次使用需要先访问 [https://pocketid.example.com/setup](https://pocketid.example.com/setup) 进行管理员账号的创建

![homelab-caddy-auth-pocketid-setup-page.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-setup-page.png)

然后添加一个 passkey，用于后续登录:

![homelab-caddy-auth-pocketid-add-passkey.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-add-passkey.png)

需要注意的是，如果这里不创建，后续登录只能进入容器创建登录码的方式进行登录，参考 [Account Recovery](https://pocket-id.org/docs/troubleshooting/account-recovery)

```bash
docker compose exec pocket-id /app/pocket-id one-time-access-token admin

2025/09/02 01:36:24 INFO Connected to database provider=sqlite
A one-time access token valid for 1 hour has been created for "admin".
Use the following URL to sign in once: https://pocketid.example.com/lc/lAuSRYzsLsqUUFNf
```

启动后就可以通过访问上面的 URL 进行登录，登录成功后会看到 PocketID 的管理页面

![homelab-caddy-auth-pocketid-homepage.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-homepage.png)

## 配置 OIDC 客户端

以 Memos 为例，将 PocketID 作为 Memos 的身份认证提供者；其他服务的配置类似，可以参考 [Client Examples](https://pocket-id.org/docs/client-examples)

### 添加 OIDC 客户端

在 PocketID 的管理页面，选择 OIDC 客户端，然后点击添加 OIDC 客户端创建一个新的客户端

![homelab-caddy-auth-pocketid-add-oidc-client.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-add-oidc-client.png)

名称填写 Memos，重定向 URL 填写 Memos 的回调地址，比如 `https://memos.example.com/auth/callback`，然后保存；会生成对应的客户端ID和密钥，点击详情会显示需要在 Memos 中配置的参数

![homelab-caddy-auth-pocketid-add-oidc-client-detail.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-add-oidc-client-detail.png)

### 配置 Memos 使用 PocketID 进行登录

在 Memos 的设置 - 单点登录中选择创建，模板选择 Custom，输入对应的 PocketID 生成的客户端ID、密钥、授权地址、令牌地址、用户信息地址等参数，保存后即可使用 PocketID 进行登录；需要注意的是回调地址和 PocketID 的地址都需要是 HTTPS 的，否则会导致登录失败

![homelab-caddy-auth-pocketid-memos-add-pocketid.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-memos-add-pocketid.png)

![homelab-caddy-auth-pocketid-memos-login-by-pocketid.png](https://img.hellowood.dev/picture/homelab-caddy-auth-pocketid-memos-login-by-pocketid.png)

## PocketID 其他配置

PokcetID 还有一些环境变量可以进行配置，用于优化使用体验和安全，可以参考 [Environment Variables](https://pocket-id.org/docs/configuration/environment-variables)

```yaml
APP_URL=https://pocketid.example.com # PocketID 的访问地址
TRUST_PROXY=true # 如果通过反向代理访问，需要设置为 true
ENCRYPTION_KEY=jen/Xz9GUbrS6BXkj+EcFjri6ZCRzHoO8+rPkRbef3Q= # 上面生成的加密 KEY
ALLOW_USER_SIGNUPS=withToken # 仅允许邀请的用户注册
DB_PROVIDER=postgres # 数据库类型，支持 sqlite 和 postgres
DB_CONNECTION_STRING=postgres://pocketid:123456@100.0.0.2:5432/pocketid?sslmode=disable # PostgreSQL 的连接字符串
MAXMIND_LICENSE_KEY=xxx # 下载 GEO 信息的 MaxMind 的 License Key，用于登录日志中识别 IP 地址的地理位置
PUID=1000 # 设置用户ID避免权限问题
PGID=1000 # 设置组ID避免权限问题
ANALYTICS_DISABLED=true # 禁用匿名数据收集
LOG_JSON=true # 使用 JSON 格式输出日志，方便日志收集和分析

APP_NAME=Pocket ID # 应用名称
SESSION_DURATION=3600 # 会话持续时间，单位为秒，默认 3600 秒

ENABLE_PASSKEYS=true # 启用 Passkeys 登录
EMAIL_ONE_TIME_ACCESS_AS_ADMIN_ENABLED=true # 启用管理员通过邮箱发送一次性登录链接
EMAIL_ONE_TIME_ACCESS_AS_UNAUTHENTICATED_ENABLED=true # 禁止未认证用户通过邮箱发送一次性登录链接
```
