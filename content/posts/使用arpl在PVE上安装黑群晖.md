---
description: "基于 PVE 虚拟机使用开源 arpl 自动装载程序一键安装黑群晖系统，包含下载、配置及初始化完整教程。"
title: 使用arpl在PVE上安装黑群晖
slug: "install-synology-on-pve-with-arpl"
aliases:
  - "/posts/使用arpl在pve上安装黑群晖/"
type: post
date: 2023-07-01T16:12:02+08:00
lastmod: 2026-03-22
tags:
  - HomeLab
  - Synology
  - NAS
featured: true
---

[arpl](https://github.com/fbelavenuto/arpl) 是 GitHub 上开源的自动装载程序，能够实现使用 arpl 在物理机或虚拟机中安装黑群晖

## 1. 下载 arpl

在 GitHub 项目 [fbelavenuto/arpl](https://github.com/fbelavenuto/arpl) 的 [Releases](https://github.com/fbelavenuto/arpl/releases) 中选择下载最新版本，选择 `img.zip` 后缀的文件进行下载

![在 GitHub 下载 arpl 黑群晖安装镜像文件](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-download.png)

解压后可以得到一个名为 `arpl.img` 的文件，这个文件用于后续安装黑群晖

## 2. 配置虚拟机

### 2.1 上传 arpl

将 `arpl.img` 文件上传到 PVE 的 ISO 镜像中，用于后续引导黑群晖

![在 PVE 界面上传 arpl.img 文件到 ISO 镜像](https://img.hellowood.dev/picture/homelab-nas-synology-upload-arpl-img.png)

### 2.2 创建虚拟机

在 PVE 中创建一个新的虚拟机，操作系统选择 '不使用任何介质'，不使用磁盘，或者在创建后将磁盘删除

![在 PVE 中创建黑群晖虚拟机的实例界面](https://img.hellowood.dev/picture/homelab-nas-synology-create-vm-instance.png)

### 2.3 配置磁盘

#### 2.3.1 将 arpl 作为磁盘导入虚拟机

使用 PVE 的命令行，使用以下命令将 arpl.img 作为虚拟机的磁盘导入，虚拟机 ID 为 101

```bash
qm importdisk 101 /var/lib/vz/template/iso/arpl.img local-lvm
```

然后在控制台修改磁盘 '总线/设备' 为 SATA 并添加

![在 PVE 中将 arpl 导入为虚拟机 SATA 磁盘](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-import-as-disk-set-sata.png)

#### 2.3.2 配置系统硬盘

在控制台再添加一个 SATA 硬盘，用于安装群晖系统及套件

![PVE 虚拟机配置 SATA 系统硬盘用于安装群晖](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-system-disk.png)

### 2.4 修改引导顺序

在选项-引导顺序中，启用 arpl 作为的引导，这样启动后就可以使用 arpl 安装和引导群晖了

![在 PVE 引导顺序中启用 arpl 作为启动项](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-change-boot.png)

## 3. 配置群晖

### 3.1 启动虚拟机

启动虚拟机，等待启动成功后，会出现 arpl 的控制台，其中有控制台的 IP 和端口信息；其中 IP 是通过 DHCP 获取到的局域网IP，端口默认是 7681

![arpl 控制台显示获取到的 IP 地址和端口信息](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-startup.png)

### 3.2 配置群晖系统

使用浏览器访问 arpl 的地址 http://192.168.2.2324:7681 进行配置

![arpl 控制台显示 IP 地址和端口信息](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-setup-synology-info.png)

分别配置群晖硬件类型，版本和序列号，然后选择构建加载器进行构建

![ARPL 界面配置群晖硬件版本序列号并构建加载器](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-build-loader.png)

构建完成后，菜单中会出现启动加载器，选择执行后会开始启动群晖系统

![arpl 构建群晖启动加载器并执行启动](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-boot-loader.png)

可以看到会加载群晖的启动项并启动，等待启动即可

![群晖安装界面在浏览器中通过端口5000访问](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-startup.png)

![arpl 启动黑群晖系统并显示启动日志](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-boot-log.png)

## 4 安装初始化群晖

### 4.1 安装

在启动成功后，可以使用对应的 IP 访问群晖安装界面，端口是 5000；如 IP 是 192.168.2.234，则群晖的界面是 http://192.168.2.234:5000

![群晖安装界面显示系统版本选择与下载选项](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-install.png)

选择最新版本的系统下载安装即可，安装后等待 10 分钟左右即可使用

![群晖安装完成界面显示等待初始化配置](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-install-complte-waiting.png)

### 4.2 初始化配置

启动成功后需要进行初始化配置，按照提示配置即可

![群晖初始化配置界面显示存储池硬盘选择](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-init-settings.png)

存储池选择添加的第二块硬盘进行创建

![黑群晖初始化配置界面创建存储池](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-create-storage-pool-2.png)

这样黑群晖就安装完成可以使用了

![黑群晖初始化配置完成后的首页界面截图](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-homepage.png)

## 5. 硬盘直通

将 PVE 中的机械硬盘挂载到黑群晖中，作为存储池使用

### 5.1 挂载硬盘信息

在命令行查看硬盘 ID，其中 `ata-Hitachi_HTS545050A7380_TE85113RHUAM6R` 就是机械硬盘的ID

```bash
ls /dev/disk/by-id

ata-Hitachi_HTS545050A7380_TE85113RHUAM6R
ata-Hitachi_HTS545050A7380_TE85113RHUAM6R-part1
ata-Hitachi_HTS545050A7380_TE85113RHUAM6R-part2
ata-Hitachi_HTS545050A7380_TE85113 HUAM6R-part3
ata-Hitachi_HTS545050A7380_TE85113RHUAM6R-part5
nvme-Fanxiang_$690_1B_FX2322025836
nvme-Fanxiang_S690_1TB_FX2322025836-part1
nvme-Fanxiang_S690_1TB_FX2322025836-part2
nvme-Fanxiang_S690_1B_FX2322025836-part3
```

- 挂载硬盘到虚拟机

关闭虚拟机挂载磁盘，完成后重新开机

```bash
qm set 101 -sata2 /dev/disk/by-id/ata-Hitachi_HTS545050A7380_TE85113RHUAM6R

update VM 101: -sata2 /dev/disk/bv-id/ata-Hitachi_HTS545050A7380_TE85113RHUAM6R
```

挂载完成后可以在虚拟机的配置中看到已经挂在的磁盘信息：

![群晖系统界面显示磁盘挂载与存储池配置信息](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-mount-disk.png)

### 5.2 挂载为新磁盘

将磁盘格式化作为新的存储池使用即可

### 5.3 恢复原有磁盘

如果磁盘是在其他群晖系统中拆下来的磁盘并且要保留数据，可以使用群晖的在线重组功能进行恢复

![群晖系统在线重组功能恢复原有磁盘数据](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-disk-repair-1.png)

![使用 arpl 在 PVE 上安装黑群晖的磁盘修复界面](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-disk-repair-2.png)

![群晖在线重组功能恢复原有磁盘数据界面](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-disk-repair-3.png)

![使用 arpl 工具在 PVE 上安装黑群晖的磁盘修复界面](https://img.hellowood.dev/picture/homelab-nas-synology-arpl-synology-disk-repair-4.png)
