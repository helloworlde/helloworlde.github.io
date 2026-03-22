---
date: 2025-07-20
description: "Cloudflare Tunnel 内网服务鉴权指南：配置 Zero Trust Access 策略、规则组与应用程序，实现基于身份验证的安全访问控制。"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
title: "Cloudflare 使用应用程序和策略为 Tunnel 代理的服务添加鉴权"
keywords:
  - "Cloudflare Tunnel"
  - "Zero Trust Access"
  - "Access Policy"
  - "Rule Group"
  - "Bypass Policy"
  - "Cloudflare Application"
  - "Identity Provider"
  - "Internal Service Auth"
slug: "cloudflare-tunnel-authentication-applications-policies"
aliases:
  - "/posts/cloudflare-使用应用程序和策略为-tunnel-代理的服务添加鉴权/"
type: "post"
tags:
  - HomeLab
  - Cloudflare
featured: true
---

在使用 Cloudflare Tunnel 代理内网服务后，服务直接暴露在公网任何人都可以访问，非常不安全，因此需要为对应的域名通过应用程序和策略来为 Tunnel 代理的服务添加鉴权

![Cloudflare 应用程序登录页面展示鉴权界面](https://img.hellowood.dev/picture/homelab-cloudflare-application-login-page.png)

## 使用 Tunnel 代理服务

如何配置和使用 Tunnel 可以参考 [使用 Cloudflare Tunnel 作为反向代理访问内网服务](https://blog.hellowood.dev/posts/cloudflare-tunnel-reverse-proxy-access-internal-services/) 以及 [使用 Cloudflare Tunnels 通过 Web SSH 访问服务器](https://blog.hellowood.dev/posts/cloudflare-tunnels-web-ssh-server-access/)

## 配置鉴权

相关的配置在 Zero Trust -> Access 中：

- 规则组用于配置哪些用户、区域、IP、认证方式等可以访问应用程序
- 策略用于配置规则或规则组的匹配条件
- 应用程序用于配置需要鉴权的主机名或路径以及配置访问策略

### 添加登录方式

Cloudflare 应用的默认的登录方式给邮箱发送为一次性验证码，如果想使用第三方登录如 Google/GitHub 等，可以在设置 - 身份验证 - 登录方式选择新增，然后根据说明从对应的网站获取登录方式的配置即可
![Cloudflare Zero Trust 添加第三方登录方式列表](https://img.hellowood.dev/picture/homelab-cloudflare-add-login-method-list.png)

![Cloudflare 添加第三方登录方式的配置结果界面](https://img.hellowood.dev/picture/homelab-cloudflare-add-login-method-result.png)

### 添加规则组

在规则组中新增一个规则组，如超级管理员仅允许特定的几个账户，选择器为 Emails, 然后输入特定邮件地址

![Cloudflare 添加规则组配置超级管理员邮件地址](https://img.hellowood.dev/picture/homelab-cloudflare-add-rule-group.png)

### 添加策略

大部分服务只需要添加鉴权和绕过策略即可；鉴权需要登录并认证通过，绕过策略则不需要认证即可对策略指定的用户放行

- 鉴权策略

添加一个策略，操作选择 Allow，规则选择器使用 Rule Group，值选择刚才创建的 Super Admin 规则组；
![Cloudflare Tunnel 添加超级管理员鉴权策略配置](https://img.hellowood.dev/picture/homelab-cloudflare-add-access-policy.png)

然后使用下面的策略测试器进行检查，除了超级管理员，其他账户都被拒绝；如果允许非管理员账户临时登录，可以在其他设置配置目的正当性，并打开临时身份验证
![Cloudflare 添加允许超级管理员的访问策略配置界面](https://img.hellowood.dev/picture/homelab-cloudflare-add-access-policy-check.png)

- 绕过策略

同样新建一个策略，操作选择 Bypass 即可，规则选择器选择 Everyone，即可对所有用户放行（也可以选择指定的地区、访问方式放行）；

注意 Bypass 和 Allow 操作不一样，Bypass 不需要任何登录态，也不会记录请求日志和统计信息；Allow 则需要登录态

![Cloudflare Tunnel 中配置 Bypass 策略以绕过身份验证](https://img.hellowood.dev/picture/homelab-cloudflare-add-Bypass-policy.png)

### 添加应用程序

目前 Cloudflare 的应用程序没有直接支持对特定路径配置鉴权或者免鉴权，因此需要配置两个应用程序，一个对所有的路径都配置鉴权，另一个配置特定的路径免鉴权；以 Web 统计工具 [umami](https://umami.is/) 为例

#### 添加需要鉴权的应用程序

添加应用程序，类型选择自托管，然后输入应用名称和对应的主机名，如应用名为 `Public Scope Service`, 主机名为 `umami.example.com`
![Cloudflare 添加自托管应用程序配置界面](https://img.hellowood.dev/picture/homelab-cloudflare-application-auth-app.png)

策略选择前面创建的鉴权策略
![Cloudflare Tunnel 为 umami 配置应用程序鉴权策略](https://img.hellowood.dev/picture/homelab-cloudflare-application-auth-policy.png)

同时可以配置使用的登录方式，默认选择所有的登录方式
![在 Cloudflare Tunnel 中为应用配置登录方式](https://img.hellowood.dev/picture/homelab-cloudflare-add-login-method-for-app.png)

#### 添加免鉴权的应用程序

通用添加自托管的应用程序，应用名为 `Global Public Service`，主机名为 `umami.example.com`，同时指定路径 `api/send` 和 `script.js`

![配置 Cloudflare Tunnel 免鉴权应用策略](https://img.hellowood.dev/picture/homelab-cloudflare-application-Bypass-app.png)

策略选择前面创建的 `Bypass for Public`，对这两个路径不做任何鉴权

![Cloudflare Tunnel 配置免鉴权策略的界面截图](https://img.hellowood.dev/picture/homelab-cloudflare-application-Bypass-policy.png)

## 检验鉴权结果

- 用允许访问的用户登录

访问 `https://umami.example.com`，会自动跳转到 Cloudflare Access 登录界面，根据前面配置的登录方式进行登录，登录成功后会跳转到 umami 主页正常访问

![Cloudflare Access 登录页面验证用户身份](https://img.hellowood.dev/picture/homelab-cloudflare-application-login-page.png)

- 用不允许访问的用户登录

如果用户不在规则组中，会被禁止访问
![Cloudflare Access 拒绝未授权用户访问的登录页面](https://img.hellowood.dev/picture/homelab-cloudflare-application-login-deny-page.png)

- 检查免鉴权的路径

在命令行直接访问检验，可以看到直接返回了 200 状态码，说明免鉴权的路径配置成功

```shell
curl -I https://umami.example.com/script.js

HTTP/2 200
date: Mon, 28 Jul 2025 14:26:39 GMT
content-type: application/javascript; charset=UTF-8
access-control-Allow-origin: *
cache-control: public, max-age=86400, must-revalidate
last-modified: Mon, 12 May 2025 07:17:22 GMT
vary: Accept-Encoding
x-dns-prefetch-control: on
age: 15406
cf-cache-status: HIT
nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
strict-transport-security: max-age=0
speculation-rules: "/cdn-cgi/speculation"
server: cloudflare
alt-svc: h3=":443"; ma=86400
```

访问其他路径则被重定向到登录界面

```shell
curl -I https://umami.hellowood.dev/index

HTTP/2 302
date: Mon, 28 Jul 2025 14:44:47 GMT
content-type: text/html
content-length: 143
location: https://user.cloudflareaccess.com/xxx
set-cookie: CF_AppSession=n79bf3da3e2ce9270; Expires=Tue, 29 Jul 2025 14:44:47 GMT; Path=/; Secure; HttpOnly
access-control-allow-credentials: true
cache-control: private, max-age=0, no-store, no-cache, must-revalidate, post-check=0, pre-check=0
expires: Thu, 01 Jan 1970 00:00:01 GMT
nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
strict-transport-security: max-age=0
speculation-rules: "/cdn-cgi/speculation"
server: cloudflare
alt-svc: h3=":443"; ma=86400
```
