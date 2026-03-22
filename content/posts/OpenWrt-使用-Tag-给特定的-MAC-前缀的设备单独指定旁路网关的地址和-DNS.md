---
date: 2025-08-11
description: "OpenWrt 通过 MAC 前缀匹配实现 DHCP 旁路网关与 DNS 自定义配置，支持 LXC 容器批量网络规则设置。"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
tags:
  - OpenWrt
  - HomeLab
title: "OpenWrt 使用 Tag 给特定的 MAC 前缀的设备单独指定旁路网关的地址和 DNS"
slug: "openwrt-tag-mac-prefix-bypass-gateway-dns"
aliases:
  - "/posts/openwrt-使用-tag-给特定的-mac-前缀的设备单独指定旁路网关的地址和-dns/"
type: "post"
featured: true
---

之前使用 tag 给特定的设备单独指定胖路网关的地址和 DNS，通过设备的 MAC 地址匹配，(参考 [OpenWrt 使用 Tag 给特定的设备单独指定旁路网关的地址和 DNS](https://blog.hellowood.dev/posts/openwrt-tag-specific-device-bypass-gateway-dns/))

但是这种方式只能匹配到具体的设备，如果想给特定的 MAC 前缀的设备使用相同的规则，可以使用 mac 前缀的方式来实现；如我在 PVE 中配置所有的 LXC 容器的 MAC 地址前缀都是 `AA:BB:CC`，可以通过这个前缀来给所有的 LXC 容器指定旁路网关和 DNS 地址

## 添加匹配规则

登录到 OpenWrt 的命令行，执行以下命令：

```bash
uci set dhcp.homelab="mac"
uci set dhcp.homelab.mac="AA:BB:CC:*:*:*"
uci add_list dhcp.homelab.dhcp_option="3,10.0.0.2"
uci add_list dhcp.homelab.dhcp_option="6,10.0.0.2,1.1.1.1"
uci commit dhcp
```

命令的作用是让所有 MAC 地址以 `AA:BB:CC` 开头的设备，在连接网络时自动获取到 `10.0.0.2` 作为网关和主DNS，并将 `1.1.1.1` 作为备用DNS

这里的 `homelab` 是自定义的规则名称，`mac` 是规则类型，`AA:BB:CC:*:*:*` 是匹配的 MAC 前缀，可以根据需要修改；`dhcp_option` 中的 `3` 是网关地址，`6` 是 DNS 地址，多个 DNS 地址用逗号分隔

## 参考文档

- [DHCP options](https://openwrt.org/docs/guide-user/base-system/dhcp_configuration#dhcp_options)
- [Client classifying and individual options](https://openwrt.org/docs/guide-user/base-system/dhcp_configuration#client_classifying_and_individual_options)
- [DHCP pools](https://openwrt.org/docs/guide-user/base-system/dhcp#dhcp_pools)
