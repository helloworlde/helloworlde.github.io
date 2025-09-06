---
title: 使用WireGuard从外网访问OpenWrt
type: post
date: 2023-06-12T16:30:22+08:00
lastmod: 2025-08-02
tags:
  - HomeLab
  - WireGuard
  - OpenWrt
featured: true
---

在使用过程中，如果通过DDNS 的方式将 OpenWrt 暴露在公网中，很容易遭受攻击或者入侵，因此可以使用 WireGuard 作为 VPN 进行访问，更加安全；因此，使用 OpenWrt 搭建 WireGuard VPN，实现从外网访问 OpenWrt

[WireGuard](https://www.wireguard.com/) 是一种现代的 VPN 协议，可以快速、安全地建立虚拟私人网络连接。相比于传统的 VPN 协议，如 OpenVPN 和I PSec，WireGuard 具有更简单的设计、更快的速度、更高的安全性和更小的代码量

## 核心概念

WireGuard中主要涉及以下几个概念：

- 接口（Interface）：表示一个 WireGuard 端点（Peer）的虚拟网络接口，用于处理加密和解密流量、路由和其他传输信息。
- 对等端（Peer）：表示使用 WireGuard 连接的每个设备或节点。每个 Peer 在连接时需要交换公钥和预共享密钥等信息。
- 公钥（PublicKey）：每个 WireGuard 对等端拥有的公钥，用于加密通信流量和生成预共享密钥。
- 私钥（PrivateKey）：与每个公钥相配对的私钥，只应该存储在拥有者的设备上。
- 端点（Endpoint）：是在网络中可访问某个 Peer 的 IP 地址和端口号，用于建立连接。
- IP 分配（IP Address Assignment）：指定每个接口使用的 IPv4/IPv6 前缀范围。
- 允许 IP（Allowed IP）：定义被 WireGuard 处理的哪些 IP 包，以及将这些包重新路由到哪个接口。
- 预共享密钥（Pre-shared Key）：在 Peer 之间建立安全连接时使用的共享密钥，用于加密数据包。
- Listen Port（监听端口）：一个 Peer 监听的 UDP 端口号。其他 Peer 使用此端口发送数据包到该 Peer

## 配置 OpenWrt

### 安装 WireGuard

```bash
opkg update && \
  opkg install wireguard-tools luci-app-wireguard luci-i18n-wireguard-zh-cn
```

此命令会自动安装 WireGuard 的依赖，也可以在管理界面进行安装；安装完成后打开 OpenWrt 管理界面-状态，就可以看到 WireGuard 的控制界面了；此时提示未配置 WireGuard 端口，需要在网络-接口中进行配置

![homelab-wireguard-openwrt-wireguard-homepage.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-wireguard-homepage.png)

### 创建密钥

建议使用 wireguard-tools 创建公私钥，便于配置和保存

- 创建文件夹并修改权限

```bash
mkdir wireguard && cd wireguard
umask 077
```

`umask 077` 的作用是设置系统默认文件和文件夹的权限为只有创建用户拥有全部权限（读、写和执行）

- 创建 OpenWrt 密钥对

先创建私钥，然后使用私钥创建公钥

```bash
wg genkey > openwrt_private_key
wg pubkey < openwrt_private_key > openwrt_public_key
```

- 创建预共享密钥

```bash
wg genpsk > pre_share_key
```

- 创建对端密钥对

```bash
wg genkey > peer_private_key
wg pubkey < peer_private_key > peer_public_key
```

### 添加 WireGuard 接口

#### 添加接口

在网络-接口中，选择添加新接口；协议类型选择 `WireGuard VPN`，然后创建接口

![homelab-wireguard-openwrt-add-wireguard-interface.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-add-wireguard-interface.png)

#### 配置接口

使用前面生成的公钥和私钥进行配置，也可以选择生成新的密钥对，需要注意要将公私钥保存下来方便后续配置；配置完成后点击保存并应用

![homelab-wireguard-openwrt-config-wireguard-interface.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-config-wireguard-interface.png)

- 公钥/私钥：用于对端连接的加密通信和身份认证
- 监听端口：用于监听和处理网络流量的 UDP 端口号，需要固定，便于对端访问
- IP地址：用于标识节点，通常使用 CIDR 格式进行表示，如这里配置 `10.0.0.1/24`表示 OpenWrt 节点的 IP 地址是 10.0.0.1，/24 表示网络前缀长度，包含从 10.0.0.0 到 10.0.0.255 的范围
- 无主机路由（Host-agnostic routing）：是一种在多个 Peer 之间分享一个公共网络环境的方法，它允许用户在不需要修改主机路由表的情况下实现跨越多个子网的通信；使用无主机路由时，可以仅将交互对等端的地址（即相邻的 WireGuard 对等端）添加到本地路由表，这样就可以通过走最短路径实现高效直接通信，而不必像其他VPN一样让所有的流量都走 VPN 隧道，避免了额外的开销和不必要的延迟；使用无主机路由可以确保在 WireGuard 网络中增加更多的子网和节点时，不会破坏现有的 IP 路由设置，从而实现更高效的通信

![homelab-wireguard-openwrt-config-wireguard-interface-completed.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-config-wireguard-interface-completed.png)

### 配置对端

编辑 WireGuard 接口，选择对端-添加对端；使用之前创建的公钥、私钥和预共享密钥；也可以选择生成新的密钥对和预共享密钥

![homelab-wireguard-openwrt-config-wireguard-interface-peer-config2.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-config-wireguard-interface-peer-config2.png)

- 预共享密钥：用于增强对连接双方身份验证的安全性，以及生成对称加密密钥来保护通信中的数据隐私和完整性
- 允许的 IP：添加对端所允许的 IP 地址列表，表示仅允许目标设置为该节点的这些 IP 数据包通过 WireGuard 接口路由，建议指定为密钥对应的客户端的IP，不能冲突；如 `10.0.0.2/32`，仅允许这一个对端使用这个密钥对进行访问

其他的配置不需要修改；这样就完成了 WireGuard 的配置；重启 WireGuard 接口或者重启 OpenWrt 使配置生效，就可以使用客户端软件进行连接了

## 对端使用

### 添加配置文件

- openwrt.conf

```dsconfig
[Interface]
PrivateKey = 8MG0PBAlRjk3+tc9DWfOAZF+lrDKAn4GREs+7NpsMGo=
Address = 10.0.0.2/32

[Peer]
PublicKey = Dc+xgDkSA7vYh311ZOhCPeGS5Rnqphel1u60VeCI2lE=
PresharedKey = HAntyG+i3nhaDzy7PhmzUDk4+te20JVPglzFbMllJvg=
AllowedIPs = 10.0.0.0/24
Endpoint = 192.168.2.253:19999
PersistentKeepalive = 25
```

- `Interface`：表示本地节点的网络接口属性配置
  - `PrivateKey` 是本地节点的私钥，用于加解密网络数据包
  - `Address` 是该节点所在子网的 IPv4 地址，需要和在 OpenWrt 配置的对端的地址一致

- `Peer`：表示需要连接的远程节点的属性配置
  - `PublicKey` 是对端公钥，可以通过与远程节点交换公钥获取
  - `PresharedKey` 是本地和远程节点之间协商设定的预共享密钥，用于增强对连接双方身份验证的安全性，以及生成对称加密密钥来保护通信中的数据隐私和完整性
  - `AllowedIPs` 是指定允许通过 VPN 通道的 IP 地址范围，用于筛选所有通过该 VPN 的流量；这里只有访问 `10.0.0.0/24`网段的会使用该 VPN 访问
  - `Endpoint` 是指定远程节点的 IP 地址和端口号，如果在公网访问需要对端有公网的IP
  - `PersistentKeepalive` 是指定保持连接的活跃性，以防止 VPN 连接因长时间不活跃而断开。

### 安装 WireGuard

在 WireGuard Installation 下载对应的软件进行安装，选择编辑好的配置文件 `openwrt.conf`进行导入，然后点击启动即可进行连接，显示有最新的握手说明连接成功

![homelab-wireguard-openwrt-peers-connect2.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-peers-connect2.png)

查看 OpenWrt 的 WireGuard 连接状态，发现对端已经成功连接了

![homelab-wireguard-openwrt-peers-connect-status.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-peers-connect-status.png)

使用浏览器访问 [http://10.0.0.1/](http://10.0.0.1/)，可以正常访问到 OpenWrt 的页面

![homelab-wireguard-openwrt-peers-connect-login-page2.png](https://img.hellowood.dev/picture/homelab-wireguard-openwrt-peers-connect-login-page2.png)
