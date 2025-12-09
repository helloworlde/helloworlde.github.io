---
date: 2025-11-02
# description: ""
# image: ""
lastmod: 2025-12-03
showTableOfContents: false
tags:
  - OpenWrt
  - HomeLab
title: "将安装 OpenWrt 的红米 AX6000 作为 AP 有线中继主路由"
type: "post"
featured: true
---

在将[红米 AX6000 解锁 SSH 并刷机 OpenWrt 系统](https://blog.hellowood.dev/posts/%E7%BA%A2%E7%B1%B3-ax6000-%E8%A7%A3%E9%94%81-ssh-%E5%B9%B6%E5%88%B7%E6%9C%BA-openwrt-%E7%B3%BB%E7%BB%9F/) 使用半年后，一些问题逐渐显现：
1. 信号变差：5G Wi-Fi 在 OpenWrt 下开启 160Mhz 后信号很差，隔着不到5米的洗手间墙壁就基本没信号了
2. 出现卡顿：尤其是刷短视频、玩游戏时，经常出现网络波动、延迟高、掉线等问题

经过一段时间的折磨之后，终于决定将主路由换成 MikroTik 的 RB5009UG+，将红米 AX6000 作为 AP 通过有线方式中继主路由

## 配置 AP 有线中继主路由

- 删除 WAN 接口

点击删除按钮，将 wan 和 wan6 接口删除

![homelab-openwrt-as-ap-delete-wan-and-wan6.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-delete-wan-and-wan6.png)

- 设置静态 IP 地址

编辑 LAN 接口，配置为静态 IP，地址是主路由网段内未被使用的地址，如 192.168.2.254；网关地址是主路由地址，如 192.168.2.1，广播地址是该网段的广播IP，如 192.168.2.255
![homelab-openwrt-as-ap-set-lan-gateway-and-address.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-set-lan-gateway-and-address.png)

- 关闭 DHCP

编辑 LAN 接口，禁用 DHCP 服务器，选择忽略该接口

![homelab-openwrt-as-ap-ignore-dhcp-interface.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-ignore-dhcp-interface.png)

- 禁用 IPv6

编辑 LAN 接口，将 RA/DHCPv6/NDP 服务器禁用，关闭 IPv6 

![homelab-openwrt-as-ap-disable-ipv6-relay.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-disable-ipv6-relay.png)

- 合并网口

编辑设备，取消配置 br-lan 以外的所有接口

![homelab-openwrt-as-ap-unconfigure-wan-devices.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-unconfigure-wan-devices.png)

然后配置 br-lan，将设备的接口合并为一个桥接接口

![homelab-openwrt-as-ap-add-wan-to-bridge.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-add-wan-to-bridge.png)

- 保存配置

完成以上配置后，保存应用配置，等待配置生效后正常配置 Wi-Fi，即可通过有线方式将红米 AX6000 作为 AP 中继主路由使用

![homelab-openwrt-as-ap-complete-config.png](https://img.hellowood.dev/picture/homelab-openwrt-as-ap-complete-config.png)


