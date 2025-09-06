---
date: 2025-07-20
# description: ""
# image: ""
lastmod: 2025-08-02
showTableOfContents: false
title: "解决阿里云和 Tailscale 的 100 网段冲突的问题"
tags:
  - HomeLab
  - Network
  - Tailscale
featured: true
type: post
---

Tailscale 使用的 `100.64.0.0/10` 是一个运营商级网络地址转换(CGNAT)网段，这个网段是一个私有 IP 范围，不用于公共互联网，因此一些云服务商如阿里云等也使用这个网段作为内网网段，这样在阿里云服务器使用 Tailscale 的时候就会出现冲突，表现为启用 Tailscale 开启后阿里云的 DNS、软件源等 100 网段的服务都无法使用

这个问题可以通过配置 Tailscale 的防火墙策略解决

## 配置 Tailscale 的防火墙

在启动时将自动防火墙配置程度设置为 `nodivert`，这样 Tailscale 就不会自动配置防火墙规则，而是使用阿里云的防火墙规则；同时启用接受来自控制台的 DNS 配置，用于解析 Tailscale 节点的 IP 地址；这样就可以解决阿里云和 Tailscale 的 100 网段冲突的问题；

不过需要注意的是改为 `nodivert` 可能会影响子网路由(advertise-routes) 和出口节点(exit node)功能

```bash
tailscale up --netfilter-mode=nodivert --accept-dns=true
```

`--netfilter-mode=nodivert` 这个参数是用于控制 Tailscale 自动配置防火墙（iptables/netfilter）规则的程度：
| 参数值 | 含义 |
|---------------|----------------------------------------------------------------------|
| `on` | Tailscale 自动管理 netfilter/iptables 规则，默认使用 |
| `nodivert` | Tailscale 创建并管理自有规则链，但不会挂载到系统主链，需要用户主动调用 |
| `off` | 完全不管理任何防火墙规则，所有流量控制需用户自行配置 |

但是修改为 `nodivert` 会存在安全漏洞 [[CVE-2019-14899] Inferring and hijacking VPN-tunneled TCP connections.](https://seclists.org/oss-sec/2019/q4/122)；这个漏洞可以让攻击者通过旁路监听（man-in-the-middle 或同网段监听）的方式，识别并劫持 VPN 隧道内的 TCP 连接，不过在内网环境下，这个漏洞的影响范围相对较小；如果是公网或者开放环境，则需要注意

## 参考文档

- [tailscale up command](https://tailscale.com/kb/1241/tailscale-up)
- [IP pool](https://tailscale.com/kb/1304/ip-pool)
- [FR: netfilter CGNAT mode when non-Tailscale CGNAT addresses should be allowed](https://github.com/tailscale/tailscale/issues/3104)
