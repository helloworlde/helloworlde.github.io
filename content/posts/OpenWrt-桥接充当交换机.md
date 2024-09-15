---
title: "OpenWrt 桥接充当交换机"
type: post
date: 2023-03-21T21:33:24+08:00
tags:
  - OpenWrt
  - HomeLab
categories:
  - OpenWrt
  - HomeLab
series:
  - OpenWrt
featured: true
---


## 需求背景

使用的路由器只有 3 个 LAN 口，在购入 NAS 后网口捉襟见肘，并且 NAS 不支持 Wi-Fi，因此需要更多的网口支持设备连接

路由器是小米的 Redmi AX6000， 支持WiFi 6E，协商速度能达到2400Mbps，但却只有千兆的网口；因为家里的两台电脑和 NAS 都是 2.5G 的网口和 WiFi6E 的无线网卡，想要 NAS 高速读写就需要 2.5G 以上的交换机；但是 2.5G 的交换机价格都在 400+，性价比不高

日常将四网口的 N5105 作为 HomeLab 的服务器使用，只有一个网口连接到路由器，其他三个网口空闲；因此想将 N5105 作为交换机，用于连接 NAS 和电脑；有三种方案：

1. 路由器和 N5105 做链路聚合，NAS连接到 N5105，电脑通过 WiFi 访问；速度能达到 2000Mbps，不过这样额外占用了两个网口，但是好处是所有的支持 WiFi6 的设备都能高速访问 NAS
2. 不做链路聚合，这样能够多三个 2.5G 的网口；NAS 和电脑都通过网线连接到 N5105，通过网线连接的设备均能以 2.5G 的速度访问 NAS
3. 为 N5105 添加 WiFi6E 无线网卡，并启用混杂模式，NAS 通过网线连接到 N5105，电脑通过 WiFi 访问 NAS；所有支持 WiFi6 的设备可以 2400Mbps 的速度访问 NAS；但是需要额外购买一张 WiFi6 的无线网卡，并且设备需要连接到 N5150 的 WiFi网络上

基于以上考虑，不做链路聚合成本最低且能扩展网口，添加 WiFi6 网卡效果最好；因为手头没有 WiFi6 的网卡，因此先通过不做链路聚合的方式实现

## 配置

### 交换机方案

有很多专业的开源或者收费的交换机方案，如 VyOS，Cumulus Linux，Open vSwitch（OVS）等，也可以基于 iKuai 或者 OpenWrt 等路由；
基于学习成本，维护成本，以及便捷性，最终选择 OpenWrt 作为交换机的方案（实际是路由器的 AP 模式）

### 安装 OpenWrt

在 Esxi/PVE 上安装 OpenWrt 的文档有很多，不再赘述；

建议使用最新的 OpenWrt 版本，当前最新的版本是 22.03.3，该版本已经支持了 Intel I225V 网卡，因此无需额外安装驱动；如果选择的是之前的版本，需要单独安装对应的驱动

### 直通网卡

在硬件中添加 PCI设备，将 PCI 网卡添加到 OpenWrt 中，作为 OpenWrt 的 LAN 口；WAN口是 PVE 虚拟机提供的虚拟网卡

![homelab-openwrt-pve-switch-add-pci-devices.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-switch-add-pci-devices.png)

### 安装驱动

#### 检查 PCI 设备是否连接

需要安装 `pciutils` 后才能查看 PCI 设备

```bash
opkg update
opkg install pciutils
```

通过 `lspci` 命令查看，发现连接没有问题

```bash
lspci | grep Eth

00:10.0 Ethernet controller: Intel Corporation Ethernet Controller I225-V (rev 03)
00:11.0 Ethernet controller: Intel Corporation Ethernet Controller I225-V (rev 03)
00:12.0 Ethernet controller: Red Hat, Inc. Virtio network device
00:1b.0 Ethernet controller: Intel Corporation Ethernet Controller I225-V (rev 03)
```

#### 检查网口是否识别

查看网口是否成功识别，发现只有 `br-lan`, `eth0`, `lo` 三个网口；说明网卡的驱动没有安装

```bash
ls -l /sys/class/net/

lrwxrwxrwx    1 root     root             0 Mar 20 08:00 br-lan -> ../../devices/virtual/net/br-lan
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 eth0 -> ../../devices/pci0000:00/0000:00:12.0/virtio1/net/eth0
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 lo -> ../../devices/virtual/net/lo
```

#### 安装驱动

```bash
opkg update
opkg install kmod-igc
```

安装完成后再次查看网口，发现多了 `eth1`, `eth2`,`eth3`，说明网口识别正确

```
ls -l /sys/class/net/

lrwxrwxrwx    1 root     root             0 Mar 20 08:00 br-lan -> ../../devices/virtual/net/br-lan
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 eth0 -> ../../devices/pci0000:00/0000:00:12.0/virtio1/net/eth0
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 eth1 -> ../../devices/pci0000:00/0000:00:10.0/net/eth1
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 eth2 -> ../../devices/pci0000:00/0000:00:11.0/net/eth2
lrwxrwxrwx    1 root     root             0 Mar 20 08:07 eth3 -> ../../devices/pci0000:00/0000:00:1b.0/net/eth3
lrwxrwxrwx    1 root     root             0 Mar 20 08:00 lo -> ../../devices/virtual/net/lo
```

### 配置 OpenWrt

进入 OpenWrt 配置界面，在网络-接口-设备，选择配置 `br-lan`

![homelab-openwrt-pve-switch-config-network-0.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-switch-config-network-0.png)

在网桥端口中，将 `eth0`, `eth1`,`eth2`,`eth3`全部选中，作为网桥的桥接端口；然后点击保存并应用，这样就可以将 OpenWrt 作为交换机使用了

![homelab-openwrt-pve-switch-config-network-1.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-switch-config-network-1.png)

## 测试

使用网线将 NAS 和电脑都连接到 N5105 的网口中，然后在 NAS 上通过 Docker 启动 [adolfintel/speedtest](https://github.com/librespeed/speedtest)，在电脑上通过浏览器测试；测试结果能达到 2.5G 的速度

![homelab-openwrt-pve-switch-speed-test.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-switch-speed-test.png)
