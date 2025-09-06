---
title: "Proxmox VE 8 挂载 PCIe 接口版本的 Goolge Coral TPU 用于 LXC 容器中部署的 Frigate 进行人物识别"
date: 2024-12-01T20:26:09+08:00
lastmod: 2024-12-29
tags:
  - Proxmox VE
  - HomeLab
  - Frigate
  - TPU
featured: true
type: post
---

在 PVE 的 LXC 容器中运行的 Frigate Docker 容器中使用 PCIe 接口版本的 Google Coral TPU 进行人物识别

之前使用的是 USB Accelerator 版本，将设备挂载到容器中就可以工作了；但是新入手的 [M.2 Accelerator with Dual Edge TPU](https://coral.ai/products/m2-accelerator-dual-edgetpu) 是通过 PCIe 挂载的，配置有所区别；

其他的版本，如 Mini PCIe Accelerator，M.2 Accelerator A+E key，M.2 Accelerator B+M key 的配置与 M.2 Accelerator with Dual Edge TPU 类似

![Coral TPU](https://lh3.googleusercontent.com/-R0H37d9aKorHo_VYWf8hCfukvbZolBaW2SHW1uDDn1G411r3MqemjxPZa9f44q8OwlfYIkGxSoj-GQbZGd2j7lxtyzSklIQVUWvo9r88mn8CzB-rcw=w2000-rw)

## 一、PVE 配置

### 1. 修改订阅源

如果使用的是 PVE 的默认软件源，需要修改为以下订阅源：

- `/etc/apt/sources.list.d/ceph.list`

将 `/etc/apt/sources.list.d/ceph.list` 中的配置替换为以下内容：

```
deb http://download.proxmox.com/debian/ceph-reef bookworm no-subscription
```

- `/etc/apt/sources.list`

将 `/etc/apt/sources.list` 中的配置替换为以下内容：

```
# debian 软件
deb http://ftp.debian.org/debian bookworm main contrib
deb http://ftp.debian.org/debian bookworm-updates main contrib

# PVE 官方非订阅源 pve-no-subscription
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription

# 安全相关
deb http://security.debian.org/debian-security bookworm-security main contrib
```

接着更新订阅源

```bash
apt update
```

### 2. 安装依赖

- 安装 pve-headers

pve-headers 是 Proxmox VE（虚拟化平台）相关的头文件包。安装这个包的主要作用是提供内核头文件，用于编译 Coral 的 PCIe 驱动

```bash
apt install pve-headers
```

- 卸载 gasket-dkms

gasket-dkms 是 Google Gasket 框架相关的 DKMS 模块包，是 TPU 设备的驱动；gasket-dkms 在新版本中需要手动编译安装，如果已经存在需要先卸载

```bash
apt remove gasket-dkms
```

- 安装 dkms 依赖

```bash
apt install git
apt install devscripts
apt install dh-dkms
apt install dkms
```

### 3. 安装驱动和运行时环境

#### 3.1 安装驱动和依赖

`gasket-dkms` 提供底层的硬件访问支持；`libedgetpu1-std` 提供上层的应用接口

- 编译并安装 gasket-dkms

```bash
cd /home
git clone https://github.com/google/gasket-driver.git
cd gasket-driver/
debuild -us -uc -tc -b
cd ..
dpkg -i gasket-dkms_1.0-18_all.deb
```

- 添加 Google Coral 的订阅源

```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
```

- 安装运行时依赖

```bash
apt update
apt install libedgetpu1-std
```

#### 3.2 配置用户访问

- 添加 udev 规则

允许 apex 设备能被 apex 组的用户访问

```bash
sh -c "echo 'SUBSYSTEM==\"apex\", MODE=\"0660\", GROUP=\"apex\"' >> /etc/udev/rules.d/65-apex.rules"
```

- 添加用户组和用户

将当前用户添加到 apex 组

```bash
groupadd apex
adduser $USER apex
```

重启 PVE 系统

```bash
reboot
```

#### 3.3 检查设备

- 查看设备

重启完成后可以查看设备是否正确挂载

```bash
lspci -nn | grep 089a

03:00.0 System peripheral [0880]: Global Unichip Corp. Coral Edge TPU [1ac1:089a]
```

查看驱动

```bash
ls /dev/apex_0

/dev/apex_0
```

### 4. 配置 PCIe 硬件直通

#### 4.1 修改 grub

grub 是启动加载程序，用于系统引导、配置和管理；修改 `/etc/default/grub` 文件，配置硬件直通

使用以下命令检查设备类型，明确是 AMD 还是 Intel：

```bash
lscpu | grep "Vendor ID"
```

将 GRUB_CMDLINE_LINUX_DEFAULT 的配置修改为以下内容，如果显示 "GenuineIntel"，使用 intel_iommu；如果显示 "AuthenticAMD" 则使用 amd_iommu

```
# AMD
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"
```

```
# Intel
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"
```

- 更新 grub

```bash
update-grub
```

#### 4.2 修改内核加载配置

修改 `/etc/modules` 文件，添加以下配置；用于虚拟机中实现硬件直通，提高虚拟化环境中的性能，实现设备隔离和安全访问

```
vfio
vfio_iommu_type1
vfio_pci
vfio_virqfd
```

然后重启 PVE 系统

```bash
reboot
```

## 二、LXC 容器配置

编辑对应 LXC 容器的配置，添加设备挂载配置

```bash
nano /etc/pve/lxc/105.conf
```

添加以下配置，将宿主机的 `/dev/apex_0` 设备挂载到容器内的 `dev/apex_0` 并配置访问权限；`c`: 表示字符设备，`120:*`: 主设备号为 120，任意次设备号；`rwm`: 允许读(r)、写(w)和创建设备节点(m)的权限

```conf
lxc.mount.entry: /dev/apex_0 dev/apex_0 none bind,optional,create=file
lxc.cgroup2.devices.allow: c 120:* rwm
```

## 三、容器配置

- 挂载设备到容器

在 `devices` 中添加要挂载的设备

```yaml
services:
  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "512mb"
    devices:
      # 挂载 Coral TPU 到容器
      - /dev/apex_0:/dev/apex_0
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /data/frigate/config/:/config
      - /data/frigate/data/db/:/data/db
      - type: tmpfs # Optional: 1GB of memory, reduces SSD/SD Card wear
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    ports:
      - "5000:5000"
```

- Frigate 使用 PCIe Coral

Frigate 中指定使用的 detector 是 PCIe 的 TPU

```yaml
detectors:
  coral:
    type: edgetpu
    device: pci
```

## 参考文档

- [How to install Coral M.2 PCI passthrough for Frigate on Proxmox 8+](https://forum.proxmox.com/threads/how-to-install-coral-m-2-pci-passthrough-for-frigate-on-proxmox-8.145557/post-709933)
