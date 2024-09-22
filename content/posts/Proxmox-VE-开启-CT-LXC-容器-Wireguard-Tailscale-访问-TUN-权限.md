---
title: "Proxmox-VE 开启 CT/LXC 容器 Wireguard/Tailscale 访问 TUN 权限"
date: 2024-09-17T10:57:59+08:00
tags:
  - Proxmox
  - HomeLab
  - LXC
  - Tailscale
  - Wireguard
categories:
  - Proxmox
  - HomeLab
  - LXC
  - Tailscale
  - Wireguard
featured: true
type: post
---

PVE 的 LXC/CT 的容器如果想要使用 Wireguard 或者 Tailscale，需要访问 tun 设备，但是非特权容器并不提供，需要手动挂载

## 修改容器配置

需要登录到 PVE 宿主机，修改 LXC/CT 容器对应的配置文件；路径是 `/etc/pve/lxc/xxx.conf`，xxx 是容器的编号，以 113 这个容器为例：

使用 nano 编辑 113.conf 配置文件

```bash
nano /etc/pve/lxc/113.conf
```

- 113.conf

```conf
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

修改后的完整配置如下：

```conf
arch: amd64
cores: 2
features: nesting=1
hostname: Debian
memory: 4096
net0: name=eth0,bridge=vmbr0,firewall=1,gw=192.168.2.1,hwaddr=AA:BB:CC:E2:42:EE,ip=192.168.2.8/24,ip6=auto,type=veth
ostype: debian
rootfs: local-lvm:vm-113-disk-0,size=60G
swap: 4096
unprivileged: 1
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

修改后在 PVE 控制台重启容器即可

## 参考文档

- [Tailscale in LXC containers](https://tailscale.com/kb/1130/lxc-unprivileged)
- [在PVE的LXC容器中直通核心显卡](https://blog.hellowood.dev/posts/%E5%9C%A8pve%E7%9A%84lxc%E5%AE%B9%E5%99%A8%E4%B8%AD%E7%9B%B4%E9%80%9A%E6%A0%B8%E5%BF%83%E6%98%BE%E5%8D%A1/)
