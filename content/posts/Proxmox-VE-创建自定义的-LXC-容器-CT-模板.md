---
title: "Proxmox VE 创建自定义的 LXC 容器 CT 模板"
date: 2024-01-07T12:00:10+08:00
tags:
    - Proxmox
    - HomeLab
    - LXC
categories: 
    - Proxmox
    - HomeLab
    - LXC
series: 
    - Proxmox
    - HomeLab
    - LXC
featured: true 
---

# Proxmox VE 创建自定义的 LXC 容器 CT 模板

LXC 是一种操作系统级别的虚拟化容器技术，可以理解为比 VM 更轻量的容器虚拟机；Docker 适用于为服务提供隔离环境，LXC 容器适用于作为虚拟机进行隔离；在 PVE 上 LXC 称为 CT

在使用 PVE 的过程中会创建多个容器，容器的基础配置基本相同，通过模板的方式创建更方便；虽然 LXC 容器提供了类似 Dockerfile 的配置文件可以创建镜像，但是使用起来比较复杂，学习成本较高；因此可以基于 LXC 容器进行初始化，然后将修改后的 LXC 容器作为基础创建模板

## 创建 LXC 容器

以 Ubuntu 容器为例进行模板的创建，在 PVE 控制页面创建一个 LXC 容器并启动

![homelab-pve-ct-template-create-ct-by-origin-template.png](https://img.hellowood.dev/picture/homelab-pve-ct-template-create-ct-by-origin-template.png)

## 初始化 LXC 容器配置

登录到创建的 LXC 容器中，根据需求安装需要用到的软件和配置进行初始化

- 修改镜像源

```bash
mv /etc/apt/sources.list /etc/apt/sources.list.backup

sudo bash -c "cat << EOF > /etc/apt/sources.list && apt update 
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
EOF"
```

- 安装 Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

- 安装常用软件

```bash
apt install -y --fix-missing curl vim git jq unzip  
```

## 创建 CT 模板

### 清理容器

清理容器的目的是删除可能变化配置和不需要的文件及配置

- 清除无效软件

```bash
apt autoremove
``` 

- 清除 DNS 和主机名配置

```bash
rm /etc/resolv.conf
rm /etc/hostname
```

- 清除操作命令

```bash
history -c
```

### 备份 LXC 容器

清理完成后，回到 PVE 的控制页面，选择刚才创建的 CT 容器进行备份

![homelab-pve-ct-template-backup-ct-as-template.png](https://img.hellowood.dev/picture/homelab-pve-ct-template-backup-ct-as-template.png)

### 将备份作为 CT 模板

登录到 PVE 机器，将刚才的备份从 `/var/lib/vz/dump/` 目录移动到存放 CT 模板的 `/var/lib/vz/template/cache/` 目录

```bash
mv /var/lib/vz/dump/vzdump-lxc-110-2023_12_31-16_13_12.tar.gz /var/lib/vz/template/cache/homelab-ubuntu-22.04-standard.tar.gz
```

移动完成后回到 PVE 控制页面，可以看到刚才创建的模板

![homelab-pve-ct-template-create-template.png](https://img.hellowood.dev/picture/homelab-pve-ct-template-create-template.png)

## 使用 CT 模板创建容器

选择新建 CT 容器，使用刚才的模板进行创建即可

![homelab-pve-ct-template-create-ct-from-tempate.png](https://img.hellowood.dev/picture/homelab-pve-ct-template-create-ct-from-tempate.png)