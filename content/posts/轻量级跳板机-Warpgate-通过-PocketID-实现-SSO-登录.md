---
date: 2026-02-01
# description: ""
# image: ""
lastmod: 2026-02-01
showTableOfContents: false
# tags: ["",]
title: "轻量级跳板机 Warpgate 通过 PocketID 实现 SSO 登录"
type: "post"
tags:
  - HomeLab
featured: true
---

在[部署轻量跳板机 Warpgate 通过 SSH 访问机器](https://blog.hellowood.dev/posts/%E9%83%A8%E7%BD%B2%E8%BD%BB%E9%87%8F%E8%B7%B3%E6%9D%BF%E6%9C%BA-warpgate-%E9%80%9A%E8%BF%87-ssh-%E8%AE%BF%E9%97%AE%E6%9C%BA%E5%99%A8/)后还需要对 Warpgate 的登录方式进行配置，以实现和其他的服务一样通过 OAuth2 进行 SSO 登录，让用户管理和认证都通过统一的身份提供商来完成；官方文档介绍可以参考 [Single sign-on](https://warpgate.null.page/sso/)

Warpgate 支持通过 Google/Apple/GitLab/Azure/Okta 等 OIDC 提供商进行认证；这里通过 [PocketID](https://pocket-id.org/) 来实现 Warpgate 的 SSO 登录；关于 PocketID 的介绍和部署可以参考[使用 PocketID 搭建个人身份认证服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-pocketid-%E4%BD%9C%E4%B8%BA-homelab-%E7%9A%84%E7%BB%9F%E4%B8%80%E7%99%BB%E5%BD%95%E8%AE%A4%E8%AF%81%E5%B7%A5%E5%85%B7/)

![homelab-jumper-warpgate-sso-login-homepage.png](https://img.hellowood.dev/picture/homelab-jumper-warpgate-sso-login-homepage.png)

## 配置 PocketID

在 PocketID 中创建一个新的 OIDC 客户端，名称为 `Warpgate`，回调 URL 为 `https://jumper.example.com/@warpgate/api/sso/return`（将 `jumper.example.com` 替换为实际的 Warpgate 访问地址）

![homelab-jumper-warpgate-sso-login-pocketid-add-new-client.png](https://img.hellowood.dev/picture/homelab-jumper-warpgate-sso-login-pocketid-add-new-client.png)

## 配置 Warpgate

### 配置文件中添加 SSO 配置

在 `data/warpgate.yaml` 中修改配置，指定 SSO 的配置；另外需要注意 Warpgate 会自动拼接回调地址到登录域名后面，因此如果有使用反向代理，需要指定 `external_host` 和 `external_port` 为反向代理的地址和端口，否则会导致回调地址错误无法登录（建议测试期间在 PocketID 删除回调地址）

```yaml
external_host: jumper.example.com # # 对外提供的域名，回调地址会使用这个域名
sso_providers:
  - name: PocketID # 登录页面显示的登录方式名称
    label: PocketID # 用户页登录方式 SSO 的名称
    trust_unknown_audiences: true # 信任 Token 中未配置的 audience
    auto_create_users: true # 自动创建用户
    provider:
      type: custom # 自定义的 OIDC 类型是 custom
      client_id: abcd-xxxx
      client_secret: xxxxx
      issuer_url: https://pocket.example.com # OIDC 配置的URL，会自动拼接 /.well-known/openid-configuration 查找
      scopes:
        - "email"

# ... 其他配置保持不变
http:
  listen: "0.0.0.0:8888"
  external_port: 443 # 指定回调的端口，如果有反向代理需要指定反向代理的端口，而不是内部监听的端口
  # ...
```

配置完成后重启 Warpgate 服务，可以看到登录页面已经多了一个 PocketID 的登录方式：

![homelab-jumper-warpgate-sso-login-homepage.png](https://img.hellowood.dev/picture/homelab-jumper-warpgate-sso-login-homepage.png)

### 为用户添加 SSO 登录

在 Warpgate 的管理页面 - `Manage Warpgate - Config - Users` 中为需要使用 SSO 登录的用户添加 `PocketID` 登录方式

![homelab-jumper-warpgate-sso-user-add.png](https://img.hellowood.dev/picture/homelab-jumper-warpgate-sso-user-add.png)

以 admin 用户为例，点击 `Add SSO`，输入 PocketID 用户的邮箱地址，`SSO Provider` 选择 PocketID，保存后即可通过 PocketID 登录 Warpgate

![homelab-jumper-warpgate-sso-user-setup.png](https://img.hellowood.dev/picture/homelab-jumper-warpgate-sso-user-setup.png)
