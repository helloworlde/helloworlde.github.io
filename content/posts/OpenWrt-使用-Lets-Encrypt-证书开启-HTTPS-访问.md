---
title: OpenWrt 使用 Lets Encrypt 证书开启 HTTPS 访问
type: post
date: 2022-11-11T21:57:52+08:00
lastmod: 2024-12-04
tags:
  - OpenWrt
  - HomeLab
featured: true
---

OpenWrt 支持开启 HTTPS 访问，但是自签发的证书无法通过 Chrome 等浏览器的认证；因此需要使用 Let's Encrypt 申请证书；通过 uHTTPd 应用配置证书，使用 DNS 验证的方式申请证书

配置 HTTPS 访问需要使用到公网 IP 和域名，需要确认已经可以通过公网访问，并且可以修改域名的解析

## 安装 uHTTPd

uHTTPd 用于 OpenWrt 配置 Web 服务，如端口，证书等

```bash
opkg update
opkg install luci-app-uhttpd luci-i18n-uhttpd-zh-cn
```

安装完成后即可在服务-uHTTPd 页面查看端口和证书配置

## 安装配置 ACME

[ACME](https://letsencrypt.org/zh-cn/docs/client-options/) 是 Let's Encrypt 官方支持的客户端；OpenWrt 支持使用 ACME 申请证书，在 ACME 应用中添加证书相关配置即可

### 安装 ACME

```bash
opkg update
opkg install acme luci-app-acme luci-i18n-acme-zh-cn acme-dnsapi
```

安装完成后可以在服务-ACME 证书中进行配置

### 配置 ACME

#### 配置账户信息

首先需要为 ACME 配置邮箱，用于接受证书过期等信息；在 ACME 全局配置-电子邮件帐户添加即可

![homelab-openwrt-acme-email-config.png](https://img.hellowood.dev/picture/homelab-openwrt-acme-email-config.png)

#### 配置证书

- 常规设置

在证书配置中，添加一个新的配置；这里使用阿里云作为 DNS 解析；

首先启用配置，并添加要配置的域名，支持特定域名或者通配的域名；

建议第一次使用时勾选使用临时服务器，测试通过后再申请正式的证书；同时选中用于 uhttpd，这样 ACME 会直接修改 uHTTPd 的证书为生成的证书

![homelab-openwrt-acme-regular-config.png](https://img.hellowood.dev/picture/homelab-openwrt-acme-regular-config.png)

- 质询验证

因为域名没有指向运行中的服务，所以选择验证方式为 DNS，在验证时会添加 DNS 解析的方式进行验证；

DNS API 为域名解析商，具体的值可以在 [https://github.com/acmesh-official/acme.sh/wiki/dnsapi](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) 查找，如阿里云的值为 `dns_ali`

DNS API 凭证为域名解析商的验证凭据信息，具体的值可以在 [ https://github.com/acmesh-official/acme.sh/wiki/dnsapi](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) 查找；如阿里云使用 AK/SK，对应的名称为 `Ali_Key` 和 `Ali_Secret`
![homelab-openwrt-acme-auth-config.png](https://img.hellowood.dev/picture/homelab-openwrt-acme-auth-config.png)

然后选择保存并应用，ACME 会在后台运行，申请证书；申请结果将会在 `/etc/acme`路径下；如果申请成功，后出现域名对应的文件夹，包含需要的证书文件；如果申请失败，会出现`域名-failed`格式的文件夹

```bash
ls -alh /etc/acme/
drwxr-xr-x    2 root     root        4.0K Nov  1 19:53 *.homelab.dev
drwxr-xr-x    4 root     root        4.0K Nov  7 12:46 .
drwxr-xr-x    1 root     root        4.0K Oct 15 20:32 ..
-rw-r--r--    1 root     root         179 Nov  1 19:53 account.conf
drwxr-xr-x    4 root     root        4.0K Nov  1 19:43 ca
-rw-r--r--    1 root     root         230 Nov  7 00:00 http.header
-rw-r--r--    1 root     root           0 Nov  2 10:40 wget-log


ls -alh /etc/acme/*.homelab.dev/
-rw-r--r--    1 root     root        1.8K Nov  1 19:53 *.homelab.dev.cer
-rw-r--r--    1 root     root         631 Nov  1 19:53 *.homelab.dev.conf
-rw-r--r--    1 root     root         980 Nov  1 19:53 *.homelab.dev.csr
-rw-r--r--    1 root     root         158 Nov  1 19:53 *.homelab.csr.conf
-rw-r--r--    1 root     root        1.6K Nov  1 19:53 *.homelab.dev.key
drwxr-xr-x    2 root     root        4.0K Nov  1 19:53 .
drwxr-xr-x    4 root     root        4.0K Nov  7 12:46 ..
-rw-r--r--    1 root     root        3.7K Nov  1 19:53 ca.cer
-rw-r--r--    1 root     root        5.5K Nov  1 19:53 fullchain.cer
```

访问服务-uHTTPd，发现证书已经被替换为 ACME申请的证书：

![homelab-openwrt-acme-uhttpd-config.png](https://img.hellowood.dev/picture/homelab-openwrt-acme-uhttpd-config.png)

如果没有自动替换，可以手动选择对应的证书路径，或者修改 `/ect/config/uhttpd` 配置文件指定

```bash
config uhttpd 'main'
	list listen_https '0.0.0.0:443'
	list listen_https '[::]:443'
	// ...
	option key '/etc/acme/*.homelab.dev/*.homelab.dev.key'
	option cert '/etc/acme/*.homelab.dev/fullchain.cer'
```

这样，就可以在外网通过
