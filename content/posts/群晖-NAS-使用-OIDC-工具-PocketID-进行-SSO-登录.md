---
date: 2026-02-07
# description: ""
# image: ""
lastmod: 2026-02-07
showTableOfContents: false
# tags: ["",]
title: "群晖 NAS 使用 OIDC 工具 PocketID 进行 SSO 登录"
type: "post"
tags:
  - HomeLab
featured: true
---

群晖 NAS 每次登录都需要输入用户名密码，比较麻烦；群晖 NAS 支持 OIDC/LDAP 等方式进行 SSO 登录认证，因此可以使用 PocketID 来实现统一的身份认证服务

![homelab-nas-sso-pocket-login-page.png](https://img.hellowood.dev/picture/homelab-nas-sso-pocket-login-page.png)

关于 PocketID 的介绍和部署可以参考[使用 PocketID 搭建个人身份认证服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-pocketid-%E4%BD%9C%E4%B8%BA-homelab-%E7%9A%84%E7%BB%9F%E4%B8%80%E7%99%BB%E5%BD%95%E8%AE%A4%E8%AF%81%E5%B7%A5%E5%85%B7/)

## 配置 PocketID

在 PocketID 中创建一个新的 OIDC 客户端，名称为 `Synology NAS`，回调 URL 为 NAS 的访问地址，如 `https://nas.example.com`（将 `nas.example.com` 替换为实际的群晖 NAS 访问地址）

![homelab-nas-sso-pocket-create-new-application.png](https://img.hellowood.dev/picture/homelab-nas-sso-pocket-create-new-application.png)

创建完成后需要使用 `客户端 ID`，`客户端密钥` 以及 `OIDC发现网址` 来配置群晖 NAS 的 OIDC 登录

## 配置群晖 nas

登录群晖 NAS 后进入 `控制面板` -> `域/LDAP` -> `SSO 客户端`，选择 `启用 OpenID Connect SSO 服务` 选项，然后进行配置：

![homelab-nas-sso-pocket-nas-add-sso-config.png](https://img.hellowood.dev/picture/homelab-nas-sso-pocket-nas-add-sso-config.png)

- 配置文件中选择 `OIDC`
- 账户类型选择 `域/LDAP/本地`
- 名称可以随意填写，如 `PocketID`
- `Well-known URL` 是 OIDC发现网址，如 `https://pocket.example.com/.well-known/openid-configuration`
- 应用程序ID和应用程序密钥填写之前在 PocketID 创建的客户端ID、客户端密钥
- 重定向 URI 填写 NAS 的访问地址，如 `https://nas.example.com`
- 授权范围需要按需填写，不同的 ODIC 服务端不一样，PocketID 可以填写 `openid email profile`，实际群晖只会用到 `profile`
- 用户名声明是群晖用于从 OIDC 用户信息中获取用户名的字段，PocketID 中是 `preferred_username`；也可以是其他字段，如 `username` 等，但是这个字段必须和 NAS 登录的用户名一致，否则登录会失败

## 测试登录

配置完成后打开新的浏览器窗口访问 NAS 地址，可以看到多了一个 `PocketID` 的登录选项，点击后会跳转到 PocketID 的登录页面，登录成功后会跳转回 NAS 并完成登录

![homelab-nas-sso-pocket-login-page.png](https://img.hellowood.dev/picture/homelab-nas-sso-pocket-login-page.png)

## 参考文档

- [SSO 客户端](https://kb.synology.cn/zh-cn/DSM/help/DSM/AdminCenter/file_directory_service_sso?version=7)
