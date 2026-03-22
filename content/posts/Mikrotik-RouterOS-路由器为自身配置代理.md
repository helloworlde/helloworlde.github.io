---
date: 2026-02-13
description: "Mikrotik RouterOS 配置 DNS 代理与路由表，实现 Docker 域名解析转发至 GoogleDNS，优化网络性能。"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
# tags: ["",]
title: "Mikrotik RouterOS 路由器为自身配置代理"
keywords:
  - "Mikrotik RouterOS"
  - "DAE proxy"
  - "DNS routing"
  - "Docker proxy"
  - "RouterOS routing"
  - "DNS upstream"
  - "Mikrotik DNS"
  - "RouterOS config"
slug: "mikrotik-routeros-proxy-configuration"
aliases:
  - "/posts/mikrotik-routeros-路由器为自身配置代理/"
type: "post"
featured: false
---

## 配置代理服务

以 dae 为例：

```hcl

# DNS 配置
dns {
  ipversion_prefer: 4
  upstream {
    googledns: 'tcp+udp://8.8.8.8:53'
  }
  routing {
    # 按由上到下的顺序匹配
    request {
      # docker
      qname(keyword: docker) -> googledns
    }
  }
}

# 路由配置
routing {
    dip(224.0.0.0/3, 'ff00::/8') -> direct
    dip(8.8.8.8) -> must_direct
    dip(1.1.1.1) -> must_direct

    ### Docker
    domain(suffix: docker.io) -> proxy
    domain(suffix: docker.com) -> proxy
    domain(keyword: docker) -> proxy
}
```

## 配置路由表

### 获取域名的 IP 地址

```bash
/ping auth.docker.io
```

```bash
/ping registry-1.docker.io
```

### 配置路由表

```

```
