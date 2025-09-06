---
date: 2025-09-02
# description: ""
# image: ""
lastmod: 2025-09-02
showTableOfContents: false
tags:
  - HomeLab
  - Gateway
  - DNS
title: "使用 Split DNS 打造 HomeLab 内网和公网一致的访问体验"
type: "post"
featured: true
---

Split DNS（分割DNS）是一种DNS配置技术，指对同一个域名在不同网络环境下提供不同的DNS解析结果；例如在内网环境下访问 `example.com` 解析到内网IP地址，而在公网环境下访问 `example.com` 解析到公网IP地址；

![homelab-split-dns-diagram-2.svg](https://img.hellowood.dev/picture/homelab-split-dns-diagram-2.svg)

在 HomeLab 场景下，服务部署在内网，可以直接访问；而外网通常需要使用 Cloudflare Tunnel 等反向代理工具进行转发；之前在内网尝试过使用 `.local`/`.homelab` 等域名访问服务，但是一些强依赖 HTTPS 的服务（如 PocketID）因自签名证书不信任问题无法使用(Java/Python服务、Firefox浏览器等均有自己的校验规则)；同时内网访问和外网访问的域名不一致，需要分别记住内网和外网的访问地址，影响使用体验

为了解决上述问题，可以使用 Split DNS，将内网的请求转发到内网的反向代理上，使用 Let's Encrypt 颁发的证书，保证内外网访问地址一致，并且支持 HTTPS 访问

公网访问时 DNS 解析到 Cloudflare Tunnel，然后请求由 Tunnel 带着 Host Header 转发到 Caddy 再转发给具体的服务；内网访问时使用 AdGuard 覆盖了内网的 DNS 解析，将请求转发到 Caddy，再转发给具体的服务

## 配置 Caddy 路由规则

### 申请证书

证书可以使用免费的 Let's Encrypt 证书，或者 ZeroSSL 等免费证书颁发机构申请，参考 [使用 Let’s Encrypt 申请 HTTPS 证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-lets-encrypt-%E7%94%B3%E8%AF%B7-https-%E8%AF%81%E4%B9%A6/)

建议直接申请泛域名证书，例如 `*.example.com`，这样可以保证后续添加新的服务时不需要重新申请证书，减少维护成本

### 配置路由

在 Caddy 的路由配置中添加路由规则，同时指定刚才申请的证书路径

- Caddyfile

```conf
whoami.example.com {
    tls /certs/_.example.com.crt /certs/_.example.com.key
    reverse_proxy 100.0.0.3:8081
}
```

详细信息可以参考:

- [使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)
- [使用 Cloudflare 和 Caddy 代理 HomeLab 服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-cloudflare-%E5%92%8C-caddy-%E4%BB%A3%E7%90%86-homelab-%E6%9C%8D%E5%8A%A1/)
- [阿里云服务器使用 Caddy 和 ZeroSSL 提供的 IP 证书为服务开启 HTTPS](https://blog.hellowood.dev/posts/%E9%98%BF%E9%87%8C%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8caddy-%E5%92%8C-zerossl-%E6%8F%90%E4%BE%9B%E7%9A%84-ip-%E8%AF%81%E4%B9%A6%E4%B8%BA%E6%9C%8D%E5%8A%A1%E5%BC%80%E5%90%AF-https/)

## 配置 Cloudflare Tunnel

修改 Cloduflare Tunnel 的路由，将 whoami 主机名转发到 Caddy 的地址 100.0.0.2，然后在 HTTP 设置中配置 HTTP 主机头为 whoami.example.com，用于 Caddy 根据 Host Header 进行路由转发；TLS 配置中也将无 TLS 验证打开，避免证书过期、域名不匹配等问题导致转发失败

![homelab-split-dns-cloudflare-tunnel-route2.png](https://img.hellowood.dev/picture/homelab-split-dns-cloudflare-tunnel-route2.png)

## 配置 Split DNS

whoami.example.com 域名，公网解析到 Cloudflare Tunnel，内网解析到 Caddy 的地址 100.0.0.2

在 AdGuard -> 过滤器 -> DNS 重写，中添加以下自定义 DNS 规则：

```yaml
filtering:
  rewrites:
    - domain: whoami.example.com
      answer: 100.0.0.2 # Caddy 内网 IP 地址
```

这样，内网的所有配置了 AdGuard 为 DNS 的设备都可以通过内网直接访问到 whoami.example.com 服务；未使用 AdGuard 作为 DNS 的设备，则是通过公网 Cloudflare Tunnel 转发的方式访问

## 验证

- 公网访问

将 DNS 地址配置为 1.1.1.1，然后通过公网访问，可以看到有 Cloudflare 的请求头信息，说明请求是通过 Cloudflare Tunnel 转发的；

```bash
curl https://whoami.example.com/

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.20.0.4
RemoteAddr: 100.0.0.2:37982
GET / HTTP/1.1
Host: whoami.example.com
User-Agent: curl/8.7.1
Accept: */*
Accept-Encoding: gzip, br
Cdn-Loop: cloudflare; loops=1
Cf-Cert-Presented: false
Cf-Cert-Revoked: false
Cf-Cert-Verified: false
Cf-Connecting-Ip: xx.xx.xx.xx
Cf-Ipcity: Osaka
Cf-Ipcontinent: AS
Cf-Ipcountry: JP
Cf-Iplatitude: 34.69379
Cf-Iplongitude: 135.50107
Cf-Metro-Code: 0
Cf-Postal-Code: 543-0062
Cf-Ray: xxxx
Cf-Region: Osaka
Cf-Region-Code: 27
Cf-Timezone: Asia/Tokyo
Cf-Visitor: {"scheme":"https"}
Via: 2.0 Caddy
X-Forwarded-For: xx.xx.xx.xx
X-Forwarded-Host: whoami.example.com
X-Forwarded-Proto: https
X-Real-Ip: xx.xx.xx.xx
```

- 内网访问

将 DNS 配置为 AdGuard 的地址，通过内网访问，只有 Caddy 的请求头信息

```bash
curl https://whoami.example.com/

Hostname: whoami
IP: 127.0.0.1
IP: ::1
IP: 172.20.0.4
RemoteAddr: 100.0.0.2:46730
GET / HTTP/1.1
Host: whoami.example.com
User-Agent: curl/8.7.1
Accept: */*
Accept-Encoding: gzip
Via: 2.0 Caddy
X-Forwarded-For: 100.0.0.4
X-Forwarded-Host: whoami.example.com
X-Forwarded-Proto: https
```

## 参考文档

- [Split DNS](https://docs.linuxserver.io/general/split-dns/)
- [What is Split DNS & Why Should You Use It?](https://tailscale.com/learn/why-split-dns)
- [Split DNS](https://nordvpn.com/zh/cybersecurity/glossary/split-dns/)
