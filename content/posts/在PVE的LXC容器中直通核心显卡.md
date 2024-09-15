---
title: "在PVE的LXC容器中直通核心显卡"
type: post
date: 2023-09-09T17:53:36+08:00
tags:
  - LXC
  - Proxmox
  - HomeLab
categories:
  - HomeLab
featured: true
---

# 在 ProxmoxVE 的 LXC 容器中直通核心显卡

在 ProxmoxVE 平台中使用 LXC 容器使用 Docker 部署 [frigate](https://frigate.video/) 时(或其他需要GPU的容器如Jellyfin等)，需要使用 GPU 对 ffmpeg 进行加速，因此需要将宿主机 N5105 的核心显卡挂载到 LXC 容器到 Docker 容器中

## 安装核显驱动

- 查看设备

如果能够看到 PCI 设备中包含核心显卡，说明设备识别正常

```bash
lspci | grep VGA
00:02.0 VGA compatible controller: Intel Corporation JasperLake [UHD Graphics] (rev 01)
```

- 查看驱动

可以看到 card0 和 renderD128 都存在，说明驱动正常

```bash
ls /dev/dri/
by-path  card0	renderD128
```

通常不需要安装驱动，如果设备没有正确识别，可以参考 [https://dgpu-docs.intel.com/driver/installation.html#ubuntu-install-steps](https://dgpu-docs.intel.com/driver/installation.html#ubuntu-install-steps) 进行安装

## 创建 LXC 容器

如图，在 PVE的控制界面，选择创建 CT 容器；配置中取消 "无特权容器" 的勾选，模板选择 CentOS 或 Ubuntu 等均可

![homelab-pve-lxc-intel-graphics-mount-1.png](https://img.hellowood.dev/picture/homelab-pve-lxc-intel-graphics-mount-1.png)

![homelab-pve-lxc-intel-graphics-mount-2.png](https://img.hellowood.dev/picture/homelab-pve-lxc-intel-graphics-mount-2.png)

创建完成后，即可看到容器的 ID，即VMID，这里是 104

## 修改核心显卡直通

修改核心显卡直通，需要使用 PVE 宿主机的命令行修改 LXC 容器的配置文件

- 添加核心显卡直通

使用 nano 编辑容器对应的配置文件，容器ID 104对应的文件是 `104.conf`，路径是 `/etc/pve/lxc/`

```bash
nano /etc/pve/lxc/104.conf
```

打开后默认的配置如下：

```dsconfig
arch: amd64
cores: 2
hostname: frigate
memory: 2048
net0: name=eth0,bridge=vmbr0,firewall=1,hwaddr=A6:43:11:F3:EE:78,ip=dhcp,type=veth
ostype: ubuntu
rootfs: local-lvm:vm-104-disk-0,size=8G
swap: 512
```

需要添加以下内容

```dsconfig
lxc.apparmor.profile: unconfined
lxc.cgroup.devices.allow: a
lxc.cap.drop:
lxc.cgroup2.devices.allow: c 226:0 rwm
lxc.cgroup2.devices.allow: c 226:128 rwm
lxc.mount.entry: /dev/dri/card0 dev/dri/card0 none bind,optional,create=file
lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file
```

这些配置参数是针对 Linux 容器（通常是 LXC 容器）的一些安全和资源控制设置，用于限制容器内部的行为和访问。以下是每个配置项的作用解释：

`lxc.apparmor.profile: unconfined`：该配置指定了 AppArmor（应用程序安全性配置框架）的配置文件名称，这里设置为 "unconfined"，用于允许容器内的进程具有更高的系统权限

`lxc.cgroup.devices.allow: a`： 允许容器内的进程访问所有的 cgroup 设备。

`lxc.cap.drop`: 此配置项为空，容器内的进程将继承主机系统的默认能力设置。

`lxc.cgroup2.devices.allow: c 226:0 rwm` 和 `lxc.cgroup2.devices.allow: c 226:128 rwm`： 允许容器内的进程对设备号为 `226:0` 和 `226:128` 的字符设备节点拥有读、写和映射（rwm）的权限。用于允许容器内的进程访问特定的设备，如图形加速设备。

`lxc.mount.entry: /dev/dri/card0 dev/dri/card0 none bind,optional,create=file` 和
`lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file`：将主机系统上的两个设备节点 `/dev/dri/card0` 和 `/dev/dri/renderD128` 挂载到容器内的相同位置，用于允许容器内的应用程序访问图形硬件加速功能，以便执行图形相关的任务

修改完成后保存，启动 LXC 容器

## 检查核显

等容器启动成功后，进入容器，使用命令行检查 `/dev/dri` 路径下挂载的文件，`card0`和 `renderD128` 都正常

```bash
ls /dev/dri/
card0  renderD128
```

查看 PCI 也能看到核心显卡，说明挂载成功

```bash
lspci | grep VGA
00:02.0 VGA compatible controller: Intel Corporation JasperLake [UHD Graphics] (rev 01)
```

## 将显卡挂载到 Docker 容器中

使用 docker-compose 部署 frigate，在配置文件中将设备 `/dev/dri/renderD128` 挂载到容器中即可

```yaml
services:
  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "256mb"
    devices:
      - /dev/dri/renderD128
```

这样，容器就可以正常使用核显进行 ffmpeg 硬件加速了

## 挂载 TUN 设备

如果你需要在 LXC 容器中使用 WireGuard/ TailScale/Clash 等依赖 TUN 网络的设备，还需要添加以下内容：

```dsconfig
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

否则会报错，提示找不到 Socket，这是因为 LXC 容器默认不会挂载 TUN 设备，所以无法访问

```
failed to connect to local tailscaled (which appears to be running as tailscaled, pid 94512). Got error: Failed to connect to local Tailscale daemon for /localapi/v0/status; systemd tailscaled.service not running. Error: dial unix /var/run/tailscale/tailscaled.sock: connect: no such file or directory
```
