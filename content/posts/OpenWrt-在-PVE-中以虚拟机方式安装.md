---
title: OpenWrt 在 PVE 中以虚拟机方式安装
type: post
date: 2023-03-20T21:35:17+08:00
lastmod: 2025-09-06
tags:
  - Proxmox VE
  - OpenWrt
  - HomeLab
featured: true
---

## 下载镜像

- 下载镜像

在 [https://openwrt.org/zh/downloads](https://openwrt.org/zh/downloads) 选择稳定发行版，然后选择需要下载的版本；这里使用当前最新的 22.03.3 版本，使用[阿里云 OpenWrt 镜像](https://mirrors.aliyun.com/openwrt/)进行下载

选择下载 `generic-ext4-combined-efi.img.gz` 这个压缩文件，用于 bios 引导

![homelab-openwrt-esxi-ima-download.png](https://img.hellowood.dev/picture/homelab-openwrt-esxi-ima-download.png)

- 解压

使用 `gunzip` 命令解压 `gz` 压缩文件

```bash
gunzip openwrt-22.03.3-x86-64-generic-ext4-combined-efi.img.gz
```

将下载的镜像解压后得到 `img`格式的文件

## 虚拟机配置

### 创建虚拟机

1. 创建虚拟机，输入名称
2. 操作系统这里选择 "不使用任何介质"
3. 磁盘这里，选择左侧删除按钮，将磁盘删除；因为会将 img 文件导入作为磁盘，因此这里不需要
4. 按需配置 CPU 和内存；通常 1核和 512M就已经足够了

![homelab-openwrt-pve-init-configuration.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-configuration.png)

### 添加硬盘

- 上传 img 镜像

选择 local - ISO镜像，将解压后的 img 文件上传到 PVE

![homelab-openwrt-pve-init-upload-img.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-upload-img.png)

等待上传完成，记录上传后的地址，即 target file 后面的路径，需要在导入时使用

![homelab-openwrt-pve-init-upload-img-result.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-upload-img-result.png)

- 将 img 镜像导入为虚拟磁盘

打开 PVE 的 shell，执行导入命令，将 img 作为虚拟磁盘，导入到 106 虚拟机（即刚才创建的虚拟机的 vmid）

```bash
qm importdisk 106 /var/lib/vz/template/iso/openwrt-22.03.3-x86-64-generic-ext4-combined-efi.img local-lvm
```

![homelab-openwrt-pve-init-convert-img-to-disk.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-convert-img-to-disk.png)

- 将硬盘添加到虚拟机

待导入完成后，会在虚拟机中显示未使用的磁盘

![homelab-openwrt-pve-init-add-disk-to-vm-0.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-add-disk-to-vm-0.png)

选择该磁盘，修改 "总线/设备" 为 SATA，然后点击添加

![homelab-openwrt-pve-init-add-disk-to-vm-1.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-add-disk-to-vm-1.png)

### 修改引导顺序

默认的引导项是 CD 驱动和网卡，需要修改为添加的硬盘才能启动；
选择虚拟机的选项-引导顺序，选择添加的 sata0 磁盘作为引导

![homelab-openwrt-pve-init-set-boot-order.png](https://img.hellowood.dev/picture/homelab-openwrt-pve-init-set-boot-order.png)

配置完成后启动虚拟机，在控制台可以看到 OpenWrt 正常启动安装

## 网络配置

启动后，需要编辑 Openwrt 的网络配置才可以进行访问

- 修改网络配置

编辑 `/etc/config/network`文件，修改 `ipaddr` 为当前局域网网段的 IP；指定 `gateway`为当前网段的网关地址； `dns`可以是当前网关的地址，也可以是 DNS 服务器的地址（建议使用 DNS 服务器，网关可能无法提供 DNS 解析）

```bash
vi /etc/config/network
```

```bash
config interface 'lan'
	option device 'br-lan'
	option proto 'static'
	option ipaddr '192.168.2.9'
	option gateway '192.168.2.1'
	option netmask '255.255.255.0'
	option ip6assign '60'
	list dns '223.5.5.5'
```

- 重启网络

重新启动网络

```bash
/ect/init.d/network restart
```

网络重启完成后，即可通过指定的地址 [192.168.2.9](192.168.2.9) 进行访问，默认账户名 `root`，没有密码
![homelab-openwrt-esxi-login.png](https://img.hellowood.dev/picture/homelab-openwrt-esxi-login.png)
