---
date: 2025-04-28
description: "OpenWrt 安装 Dae eBPF 代理：ImmortalWRT 编译内核支持、eBPF 流量分流、HTTPS/VMess/VLESS 协议及 PVE 虚拟机部署指南。"
# image: ""
lastmod: 2025-05-06
showTableOfContents: false
# tags: ["",]
title: "OpenWrt 安装使用 Dae 作为代理"
type: "post"
tags:
  - Proxy
  - Dae
  - HomeLab
  - OpenWrt
featured: true
---

[Dae](https://github.com/daeuniverse/dae) 是一种高性能透明代理解决方案，在 Linux 内核中使用 eBPF 实现了代理能力；支持以域名、源 IP、目的 IP、源端口、目的端口、TCP/UDP、IPv4/IPv6、进程名、MAC 地址等对流量进行分流；相对于其他代理方案，如 Clash 等，Dae 的代理规则相对灵活，直连的性能更好(本机进程，作为网关实际效果差距不大)

Dae 的出栈协议支持 HTTPS/VMess/VLESS/Shadowsocks/Trojan/Tuic/Juicity/Hysteria2 等

Dae 和其他的代理软件如 Clash 等相比，在可靠性、稳定性、速度、容灾等方面并没有明显的优势，并且对设备的要求较高，因此并不见得是最佳选择

## 安装 OpenWrt

因为 dae 是基于 eBPF 实现的，所以需要 OpenWrt 内核支持 eBPF，内核版本需要大于 5.17，并且需要开启 eBPF；OpenWrt 官方提供的镜像未开启 eBPF 支持，需要自行编译，或者使用 ImmortalWRT 构建的镜像

### 使用 ImmortalWRT 构建镜像

访问 [https://firmware-selector.immortalwrt.org/](https://firmware-selector.immortalwrt.org/)，我是在 x86 机器的 PVE 中使用虚拟机的方式运行 OpenWrt，因此选择 `Generic x86/64`，其他平台如 arm 等选择对应的平台即可

在 Installed Packages 后面追加 eBPF 和 Dae 相关的包：

```shell
kmod-xdp-sockets-diag kmod-veth kmod-sched-core kmod-sched-bpf kmod-nft-bridge dae-geosite dae-geoip dae
```

软件包的作用如下：

| 软件名                  | 作用                                                           |
| ----------------------- | -------------------------------------------------------------- |
| `kmod-xdp-sockets-diag` | 提供 XDP 套接字诊断，用于监控与排查基于 XDP 的高性能网络程序   |
| `kmod-veth`             | 支持成对虚拟以太网设备（veth），常用于容器网络隔离             |
| `kmod-sched-core`       | 提供 Linux 内核的流量调度核心框架，支撑 QoS 策略               |
| `kmod-sched-bpf`        | 基于 BPF 的流量调度扩展，支持自定义数据包处理策略              |
| `kmod-nft-bridge`       | 在桥接接口上集成 nftables 防火墙规则                           |
| `dae-geosite`           | 为 dae 守护进程提供 GeoSite 支持，可按域名或网站分类过滤流量   |
| `dae-geoip`             | 为 dae 守护进程提供 GeoIP 支持，可按 IP 地理位置过滤或路由流量 |
| `dae`                   | 核心 dae 守护进程，实现后台流量过滤与转发等网络服务            |

完整的包列表如下：

```shell
autocore automount base-files block-mount ca-bundle default-settings-chn dnsmasq-full dropbear fdisk firewall4 fstools grub2-bios-setup i915-firmware-dmc kmod-8139cp kmod-8139too kmod-button-hotplug kmod-e1000e kmod-fs-f2fs kmod-i40e kmod-igb kmod-igbvf kmod-igc kmod-ixgbe kmod-ixgbevf kmod-nf-nathelper kmod-nf-nathelper-extra kmod-nft-offload kmod-pcnet32 kmod-r8101 kmod-r8125 kmod-r8126 kmod-r8168 kmod-tulip kmod-usb-hid kmod-usb-net kmod-usb-net-asix kmod-usb-net-asix-ax88179 kmod-usb-net-rtl8150 kmod-usb-net-rtl8152-vendor kmod-vmxnet3 libc libgcc libustream-openssl logd luci-app-package-manager luci-compat luci-lib-base luci-lib-ipkg luci-light mkf2fs mtd netifd nftables odhcp6c odhcpd-ipv6only opkg partx-utils ppp ppp-mod-pppoe procd-ujail uci uclient-fetch urandom-seed urngd kmod-amazon-ena kmod-amd-xgbe kmod-bnx2 kmod-e1000 kmod-dwmac-intel kmod-forcedeth kmod-fs-vfat kmod-tg3 kmod-drm-i915 kmod-xdp-sockets-diag kmod-veth kmod-sched-core kmod-sched-bpf kmod-nft-bridge dae-geosite dae-geoip dae
```

![homelab-openwrt-dae-build-openwrt-firmware.png](https://img.hellowood.dev/picture/homelab-openwrt-dae-build-openwrt-firmware.png)

然后选择 `REQUEST BUILD` 构建镜像；等待构建完成后选择 `COMBINED-EFI (EXT4)` 下载到本地

### 在 PVE 中运行 OpenWrt

使用刚才下载的镜像在 PVE 中创建 OpenWrt 的虚拟机并运行，详细参考 [OpenWrt 在 PVE 中以虚拟机方式安装](https://blog.hellowood.dev/posts/openwrt-%E5%9C%A8-pve-%E4%B8%AD%E4%BB%A5%E8%99%9A%E6%8B%9F%E6%9C%BA%E6%96%B9%E5%BC%8F%E5%AE%89%E8%A3%85/)

## 配置 Dae

### 修改配置文件

登录 OpenWrt 的命令行进行修改，关于 Dae 配置的详细解释可以参考: [dae-代理软件的配置](https://blog.hellowood.dev/posts/dae-%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E7%9A%84%E9%85%8D%E7%BD%AE/)

配置文件位置在 `/etc/dae/` 路径下，创建 `/etc/dae/config.dae` 文件，文件内容如下:

- `/etc/dae/config.dae`

```nginx
# 完整配置参考 https://github.com/daeuniverse/dae/blob/main/example.dae
global {
    # 修改日志级别为 debug，方便调试
    log_level: debug
    # lan 口绑定 eth0
    lan_interface: eth0
    # 用强制 SNI 嗅探进行分流
    dial_mode: domain++
}

# DNS 配置
dns {
  # 使用 IPv4 的 DNS，避免部分 node 不支持 IPv6 导致请求失败
  ipversion_prefer: 4
  # 上游 DNS
  upstream {
    # 阿里云 DNS，用于国内域名查询
    alidns: 'udp://223.5.5.5:53'
    # 本地 DNS，用于内网自定义的  DNS 查询
    adguard: 'udp://10.0.0.1:53'
    # Cloudflare DNS，用于非国内的 DNS 查询
    cfdns: 'tcp+udp://1.1.1.1:53'
  }

  # DNS 查询规则
  routing {
    # 根据 DNS 查询，决定使用哪个 DNS 上游，按由上到下的顺序匹配
    request {
      # svc.local 结尾的域名，用本地的 DNS 查询
      qname(suffix: svc.local) -> adguard
      # 对于中国大陆域名使用 alidns，其他使用 cfdns 查询。
      qname(geosite:cn) -> alidns
      # fallback 即默认兜底 DNS
      fallback: cfdns
    }
  }
}

# 如果使用订阅地址，必须是符合 SIP008 格式或者 base64/urlencode 编码或者 txt 格式的节点列表，详细参考: https://blog.hellowood.dev/posts/dae-%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E7%9A%84%E9%85%8D%E7%BD%AE/

# subscription 的节点解析过滤后作为 node，tag 是
subscription {
  sub_airport_1: 'https://订阅地址'
}

# 自己搭建的节点，直接配置到 node 方便调试
node {
    # HTTPS/VMess/VLESS/Shadowsocks/Trojan/Tuic/Juicity/Hysteria2 等格式
    hy2: "hysteria2://user:password@host:443/?insecure=false"
}

# 节点分组
group {
    # 分组一，名称是 proxy，用于 routing 选择
    # 没有过滤条件，使用所有节点
    proxy {
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }

    # AI 分组，用于 claude 等对地区有限制的服务商
    ai {
        # 从 subscription 的 sub_airport_1 中过滤名称包含新加坡的作为这个分组的可用节点
        filter: subtag(sub_airport_1) && name(keyword: '新加坡')
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }
}

# 路由配置
routing {
    # DNS/SSH 等相关进程强制直连
    pname(dnsmasq, dropbear) -> must_direct
    # DNS 地址或域名，强制直连
    dip(8.8.8.8) -> must_direct
    dip(1.1.1.1) -> must_direct
    domain(dns.alidns.com) -> must_direct
    domain(dns.google) -> must_direct
    domain(cloudflare-dns.com) -> must_direct

    # 目标 IP 多播、广播地址，直连
    dip(224.0.0.0/3, 'ff00::/8') -> direct
    # 目标 IP geoip 中的内网地址，直连
    dip(geoip:private) -> direct

    # 目标 IP 中国 IP，直连
    dip(geoip:cn) -> direct
    # 中国域名，直连
    domain(geosite:cn) -> direct

    # 广告域名，拒绝
    domain(geosite:category-ads) -> block

    # AI 域名，AI 分组代理
    domain(suffix: claude.ai) -> ai
    domain(suffix: openai.com) -> ai

    # 未命中上面的规则的走 proxy 代理
    fallback: proxy
}
```

需要注意，dae 要求配置文件的权限是 640 以下的权限，否则会提示 `permissions 0644 for '/etc/dae/config.dae' are too open`；通过以下命令修改:

```bash
chmod 600 /etc/dae/config.dae
```

- 检查配置文件

通过 `dae` 检查配置文件是否正确，如果没有输出错误信息，表示配置没有问题

```bash
/usr/bin/dae validate -c /etc/dae/config.dae
```

### 启动 dae

- 通过 `/etc/init.d/dae` 脚本启动 dae

允许 dae 自动启动

```bash
/etc/init.d/dae enable
```

然后启动 dae

```bash
/etc/init.d/dae start
```

- 检查 dae 状态

可以通过 `ps` 查看 dae 的进程

```bash
ps w |grep dae
13609 root     1359m S    /usr/bin/dae run --disable-timestamp -c /etc/dae/config.dae
14819 root      1184 S    grep dae
```

- 查看 dae 的日志

```bash
tail -f /var/log/dae.log
```

可以从日志中看到 dae 启动、更新 Node 的信息

```golang
level=info msg="Include config files: [/etc/dae/config.dae]"
level=info msg="Waiting for network..."
level=debug msg="CheckNetwork: Get "http://www.gstatic.com/generate_204": context deadline exceeded (Client.Timeout exceeded while awaiting headers)"
level=info msg="Network online."
level=info msg="Fetching subscriptions..."
level=debug msg="ResolveSubscription: https://订阅地址"
level=debug msg="Try to resolve as sip008"
level=debug msg="failed to unmarshal json to sip008"
level=debug msg="Try to resolve as base64"
level=info msg="Loading eBPF programs and maps into the kernel..."
level=info msg="The loading process takes about 120MB free memory, which will be released after loading. Insufficient memory will cause loading failure."
level=info msg="Loaded eBPF programs and maps"
level=info msg="Bind to LAN: eth0"
level=info msg="Group "proxy" node list:"
level=info msg="	hy2"
level=info msg="	剩余流量：322.88 GB"
level=info msg="	套餐到期：长期有效"
level=info msg="	新加坡01aws"
# ...
```

## 使用

如果 OpenWrt 作为主路由，则不需要任何设置；如果是作为旁路网关，则需要将设备的网关指向 OpenWrt

- 修改网络配置

网关地址改为 OpenWrt 的地址，如 10.0.0.254

![homelab-openwrt-dae-modify-device-gateway.png](https://img.hellowood.dev/picture/homelab-openwrt-dae-modify-device-gateway.png)

- 修改 DNS 地址

DNS 地址也可以修改为指向 OpenWrt，这样能够保证 dae 正确分流，配置 DNS 不是必须的，但是配置之后效果会更好；如果不配置 DNS，也可以将 `dial_mode` 设置为 `domain++` 进行强制 SNI 嗅探分流

![homelab-openwrt-dae-modify-device-dns.png](https://img.hellowood.dev/picture/homelab-openwrt-dae-modify-device-dns.png)

- 查看访问日志

以 claude.ai 为例，配置完成后，访问 claude.ai 地址，检查 OpenWrt 的日志，发现使用 DNS 查询使用了 cloudflare，节点使用了新加坡的节点，outbound 的分组为 ai，嗅探到的域名是 claude.ai，符合预期

```bash
tail -f /var/log/dae.log |grep claude
level=info msg="10.0.0.1:61301 <-> 1.1.1.1:53" _qname=claude.ai. dialer=direct dscp=0 mac="00:11:22:33:44:55" network="udp4(DNS)" outbound=direct pid=0 pname= policy=fixed qtype=HTTPS
level=info msg="10.0.0.1:27818 <-> 1.1.1.1:53" _qname=claude.ai. dialer=direct dscp=0 mac="00:11:22:33:44:55" network="udp4(DNS)" outbound=direct pid=0 pname= policy=fixed qtype=A
level=info msg="10.0.0.1:27818 <-> 1.1.1.1:53" _qname=claude.ai. dialer=direct dscp=0 mac="00:11:22:33:44:55" network="udp4(DNS)" outbound=direct pid=0 pname= policy=fixed qtype=AAAA
level=info msg="10.0.0.1:64316 <-> claude.ai:443" dialer="新加坡09aws" dscp=0 ip="10.0.0.2:443" mac="00:11:22:33:44:55" network=tcp4 outbound=ai pid=0 pname= policy=min_moving_avg sniffed=claude.ai
level=info msg="10.0.0.1:64376 <-> claude.ai:443" dialer="新加坡07aws" dscp=0 ip="10.0.0.2:443" mac="00:11:22:33:44:55" network=tcp4 outbound=ai pid=0 pname= policy=min_moving_avg sniffed=claude.ai
```

## 参考文档

- [Dae 代理软件的配置](https://blog.hellowood.dev/posts/dae-%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E7%9A%84%E9%85%8D%E7%BD%AE/)
- [OpenWrt 在 PVE 中以虚拟机方式安装](https://blog.hellowood.dev/posts/openwrt-%E5%9C%A8-pve-%E4%B8%AD%E4%BB%A5%E8%99%9A%E6%8B%9F%E6%9C%BA%E6%96%B9%E5%BC%8F%E5%AE%89%E8%A3%85/)
- [🦢Dae安装及配置指南](https://deeprouter.org/article/dae-installation-configuration-guide#1ac975710fee8089983de9e660c0e0eb)
- [https://github.com/daeuniverse/dae/blob/main/example.dae](https://github.com/daeuniverse/dae/blob/main/example.dae)
- [吃鹅直通手册](https://github.com/daeuniverse/dae/blob/main/docs/zh/README.md)
- [Download ImmortalWrt Firmware for your Device](https://firmware-selector.immortalwrt.org/)
