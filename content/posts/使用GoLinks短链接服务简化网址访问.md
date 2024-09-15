---
title: "使用 GoLinks 短链接服务简化网址访问"
type: post
date: 2023-11-27T11:40:53+08:00
tags:
  - Tools
categories:
  - Tools
featured: true
---

最近在内网查找文档时看到一个类似 `go/文档名` 的链接，在浏览器的 URL 输入后可以跳转到对应的文档，对比其他的短链接服务要方便不少；

一番探索后发现原来是一个叫 GoLinks 的短链接服务，通过域名配合 DNS 搜索域，实现了可以直接访问 `go` 域名；然后根据路径，重定向到对应的 URL。

![go-links-homepage.png](https://img.hellowood.dev/picture/go-links-homepage.png)

## 什么是 GoLinks

根据 Tailscale 的文档，GoLinks 服务第一次出现应该是2006年，在谷歌作为内部短链接工具，后来被各个公司复制

GoLinks 通过 DNS 配置，简化了短链接服务本身的访问地址，因此，可以通过形如 `go/google`, `go/search/golinks` 这样的方式直接访问

在 GitHub上搜索发现 Tailscale 也提供了这样的工具，项目地址为 [https://github.com/tailscale/golink](https://github.com/tailscale/golink)，在开启 Tailscale 后可以通过 MagicDNS 直接使用。同时可以配置为开发模式，通过内网的 DNS 和搜索域的配合也可以实现相同的功能。相关文档参考 [Private go links for your tailnet](https://tailscale.com/blog/golink/)

## 内网使用 GoLinks 服务

使用 GoLinks 服务有两个条件：

1. 需要能够将 `go` 解析为对应的服务地址，可以通过配置 DNS 或者 host 的方式实现
2. 需要 GoLinks 服务监听 80 端口因为访问时为了简单不想再输入 https 或者端口号，因此需要使用 80 端口作为 GoLinks 服务的端口

有三种方式可以解析 `go`：

1. 配置 DNS，将 `go` 直接解析为 GoLinks 服务的地址
2. DNS 服务器配置 `go.xxx`解析规则，然后通过路由器下发 DNS 搜索域；这样在访问`go`时就会自动搜索`go.xxx`域名，适用于内网访问
3. 修改 host 配置，将 `go` 指向 GoLinks 服务的地址，适用于不方便配置 DNS 的场景使用

## 启动 GoLinks 服务

可以通过 Docker 容器启动 GoLinks 服务，用于快速使用，为了方便测试，将端口指定为 80

```bash
docker run -it --rm -p 80:80 ghcr.io/tailscale/golink:main -dev-listen :80
```

也可以通过 Docker Compose 启动，`--sqlitedb /data/golink.db`用于指定保存短链接配置的数据库地址

```yaml
version: "3"

services:
  golink:
    image: ghcr.io/tailscale/golink:main
    hostname: golink
    container_name: golink
    command: -dev-listen :80 --sqlitedb /data/golink.db
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./data:/data
    environment:
      - TZ=Asia/Shanghai
```

## 配置网络

### 通过 host 配置

最简单的方式就是配置 host，在 host 中指定 GoLinks 服务的 IP 即可

- `/etc/hosts`

在 host 中添加 `go`，指向本地

```
127.0.0.1       localhost
127.0.0.1       go
```

这样，访问 `go/xxx` 就会自动跳转到对应的地址，如果没有找到，会跳转到 GoLinks 页面进行配置

### 通过 DNS 配置

#### 配置 DNS 解析

配置 DNS 的方式需要 DNS 服务器支持，在 DNS 中添加对应的解析，以 CoreDNS 为例，添加名为 `go.svc.local` 的解析，指向部署了 GoLinks 服务的机器

```bash
go.svc.local. IN A 192.168.2.4
```

检查 DNS 解析

```bash
nslookup go.svc.local 192.168.2.2
Server:		192.168.2.2
Address:	192.168.2.2#53

Name:	go.svc.local
Address: 192.168.2.4
```

#### 配置 DNS 搜索域

> 搜索域包含了一组默认的域名后缀，在 DNS 查询中，当查询一个不完整的域名时，系统会尝试在搜索列表中的每个域名后缀下进行解析，直到找到匹配的域名为止；

如 DNS 为 `go.svc.local`，配置搜索域为 `svc.local`，通过 `go` 访问；查询时会先查找 `go` 域名，查找不到时会将搜索域添加到域名中进行搜索，即向 DNS 服务器查询 `go.svc.local`

##### 修改路由器的搜索域

OpenWrt 路由器默认的搜索域为 `lan`，其他大部分的路由器默认不会下发搜索域，因此需要手动配置，需要修改为 GoLinks 所在的域（如果图方便可以将 GoLinks 的域名配置为 `go.lan`）

OpenWrt 或基于 OpenWrt 的路由器都是使用 Dnsmasq 做 DNS 解析，因此，修改 Dnsmasq 的配置即可

- 在页面配置

将 Local Domain 配置由 `lan` 修改为 `svc.local`

![go-links-search-lan-configuration-in-openwrt-page.png](https://img.hellowood.dev/picture/go-links-search-lan-configuration-in-openwrt-page.png)

- 修改 `/etc/config/dhcp`

如果是小米路由器等基于 OpenWrt 修改的路由器，可以登陆后将 dhcp 配置文件的 `domain` 配置由 `lan` 修改为 `svc.local`

```
config dnsmasq
	option local '/lan/'
	option domain 'svc.local'
	// ...
```

这样，重启路由器后再次分配的 DNS 信息中就包含 `svc.local` 搜索域了

![go-links-search-lan-configuration-by-router.png](https://img.hellowood.dev/picture/go-links-search-lan-configuration-by-router.png)

##### 修改设备的搜索域

可以通过网络中的 DNS 配置，手动添加 DNS 搜索域
![go-links-search-lan-configuration.png](https://img.hellowood.dev/picture/go-links-search-lan-configuration.png)

也可以在 `/etc/resolv.conf` 配置中指定 `search`

```
search svc.local
nameserver 192.168.2.2
nameserver 223.5.5.5
```

## 使用

在 GoLinks 服务配置 `search` 路径，指向 `https://www.google.com/{{if .Path}}search?q={{QueryEscape .Path}}{{end}}`，用于 Google 搜索

直接访问，会发现跳转到了 https://www.google.com/

```bash
curl -i go/search

HTTP/1.1 302 Found
Location: https://www.google.com/
type: post
date: Mon, 27 Nov 2023 03:22:19 GMT
Content-Length: 0
```

带上 path 作为查询参数，会发现跳转到了 https://www.google.com/search?q=%E4%BB%80%E4%B9%88%E6%98%AFgolinks

```bash
curl -i go/search/什么是golinks

HTTP/1.1 302 Found
Location: https://www.google.com/search?q=%E4%BB%80%E4%B9%88%E6%98%AFgolinks
type: post
date: Mon, 27 Nov 2023 03:34:36 GMT
Content-Length: 0
```
