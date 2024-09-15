---
title: "Proxmox VE 创建自定义的 LXC 容器 CT 模板"
type: post
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

登录到创建的 LXC 容器中，根据需求安装需要用到的软件和配置进行初始化，可以参考 [ubuntu-22-环境初始化](https://blog.hellowood.dev/posts/ubuntu-22-环境初始化)

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

## 配置 LXC 容器

使用 Docker 时需要挂载 NFS，所以需要使用特权容器，并配置访问权限；登录 PVE 命令行，在 `/etc/pve/lxc` 下修改对应的 LXC 容器的配置：

- `/etc/pve/lxc/110.conf`

添加如下配置：

```
unprivileged: 0
lxc.apparmor.profile: unconfined
lxc.cap.drop:
```

`unprivileged: 0`表示容器将在特权模式下运行，即容器内的进程将具有与主机相同的权限
`lxc.apparmor.profile: unconfined` 表示容器内的进程将不受任何 AppArmor 限制
`lxc.cap.drop:` 用于指定容器内进程的能力限制，允许进程执行一些特定的操作，例如修改系统时间、挂载文件系统等
