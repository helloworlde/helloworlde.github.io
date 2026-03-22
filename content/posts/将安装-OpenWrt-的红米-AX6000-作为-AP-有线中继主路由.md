---
date: 2025-11-02
description: "解决 OpenWrt 红米 AX6000 信号差卡顿问题，通过删除 WAN 接口、配置静态 IP 关闭 DHCP 及 IPv6 实现有线 AP 中继主路由部署。"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
tags:
  - OpenWrt
  - HomeLab
title: "将安装 OpenWrt 的红米 AX6000 作为 AP 有线中继主路由"
slug: "openwrt-redmi-ax6000-wired-ap-repeater"
aliases:
  - "/posts/将安装-openwrt-的红米-ax6000-作为-ap-有线中继主路由/"
type: "post"
featured: true
---

在将[红米 AX6000 解锁 SSH 并刷机 OpenWrt 系统](https://blog.hellowood.dev/posts/redmi-ax6000-ssh-openwrt/) 使用半年后，一些问题逐渐显现：

1. 信号变差：5G Wi-Fi 在 OpenWrt 下开启 160Mhz 后信号很差，隔着不到5米的洗手间墙壁就基本没信号了
2. 出现卡顿：尤其是刷短视频、玩游戏时，经常出现网络波动、延迟高、掉线等问题

经过一段时间的折磨之后，终于决定将主路由换成 MikroTik 的 RB5009UG+，将红米 AX6000 作为 AP 通过有线方式中继主路由

## 配置 AP 有线中继主路由

- 删除 WAN 接口

点击删除按钮，将 wan 和 wan6 接口删除

![删除 OpenWrt 中的 wan 和 wan6 接口](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-delete-wan-and-wan6.png)

- 设置静态 IP 地址

编辑 LAN 接口，配置为静态 IP，地址是主路由网段内未被使用的地址，如 192.168.2.254；网关地址是主路由地址，如 192.168.2.1，广播地址是该网段的广播IP，如 192.168.2.255
![OpenWrt 设置 LAN 接口静态 IP 地址和网关](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-set-lan-gateway-and-address.png)

- 关闭 DHCP

编辑 LAN 接口，禁用 DHCP 服务器，选择忽略该接口

![OpenWrt 设置中忽略 DHCP 接口以配置为 AP 模式](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-ignore-dhcp-interface.png)

- 禁用 IPv6

编辑 LAN 接口，将 RA/DHCPv6/NDP 服务器禁用，关闭 IPv6

![OpenWrt 设置界面禁用 IPv6 服务器选项](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-disable-ipv6-relay.png)

- 合并网口

编辑设备，取消配置 br-lan 以外的所有接口

![OpenWrt 取消配置 WAN 接口以设置 AP 模式](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-unconfigure-wan-devices.png)

然后配置 br-lan，将设备的接口合并为一个桥接接口

![OpenWrt 配置界面将 WAN 接口添加到 br-lan 桥接](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-add-wan-to-bridge.png)

- 保存配置

完成以上配置后，保存应用配置，等待配置生效后正常配置 Wi-Fi，即可通过有线方式将红米 AX6000 作为 AP 中继主路由使用

![红米 AX6000 配置为有线 AP 中继主路由完成界面](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-complete-config.png)
