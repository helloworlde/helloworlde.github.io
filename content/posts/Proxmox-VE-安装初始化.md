---
title: "Proxmox VE 安装初始化"
type: post
date: 2023-02-27T21:41:04+08:00
tags:
  - Proxmox VE
  - HomeLab
categories:
  - Proxmox VE
  - HomeLab
series:
  - Proxmox VE
featured: true
---

# Proxmox VE(PVE) 安装初始化

> Proxmox VE，是一个开源的服务器虚拟化环境Linux发行版。Proxmox VE基于Debian，使用基于Ubuntu的定制内核，包含安装程序、网页控制台和命令行工具，并且向第三方工具提供了REST API - 维基百科

PVE 和 Vmware ESXi 类似，都支持虚拟化环境；PVE 基于 Linux，扩展性更强

## 安装

- 下载 ISO 镜像

PVE的镜像可在 PVE 官网的[下载页面](https://www.proxmox.com/en/downloads/category/iso-images-pve)进行下载

- 制作启动盘

使用 [Rufus](https://rufus.ie/zh/) 或者 [balenaEtcher](https://www.balena.io/etcher) 将下载的 ISO 镜像写入到 U 盘或者移动硬盘中

![homelab-pve-install-write-iso.png](https://img.hellowood.dev/picture/homelab-pve-install-write-iso.png)

- 插入主机并启动

启动后选择安装 Proxmox VE

![homelab-pve-install-start-install.png](https://img.hellowood.dev/picture/homelab-pve-install-start-install.png)

- 设置 IP 地址

IP地址用于后续访问，可以通过DHCP获取，也可以设置为固定的 IP

![homelab-pve-install-set-ip.png](https://img.hellowood.dev/picture/homelab-pve-install-set-ip.png)

- 安装完成

安装完成后，会提示重启

![homelab-pve-install-completed.png](https://img.hellowood.dev/picture/homelab-pve-install-completed.png)

- 登录

重启完成后，在命令行会提示访问的地址，默认端口是 8006，

![homelab-pve-install-login-page.png](https://img.hellowood.dev/picture/homelab-pve-install-login-page.png)

通过 HTTPS 协议访问；如 [https://192.168.17.129:8006](https://192.168.17.129:8006)

![homelab-pve-install-web-login-page.png](https://img.hellowood.dev/picture/homelab-pve-install-web-login-page.png)
