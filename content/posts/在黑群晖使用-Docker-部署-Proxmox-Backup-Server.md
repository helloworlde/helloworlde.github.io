---
title: "在黑群晖使用 Docker 部署 Proxmox Backup Server"
date: 2023-12-23T21:52:00+08:00
tags:
    - Proxmox
    - HomeLab
categories: 
    - Proxmox
    - HomeLab
series: 
    - Proxmox
    - HomeLab
featured: true 
---

# 在黑群晖使用 Docker 部署 Proxmox Backup Server

Proxmox Backup Server 是 PVE 容器、虚拟机的备份解决方案，支持增量、重复数据消除备份，可以节省存储空间，同时支持加密和完整性校验

Proxmox Backup Server 官方提供了 iso 格式的镜像，同时社区也有开源的 Docker 镜像的部署方式，为了在黑群晖上部署方便，使用 Docker 的方式进行部署，项目地址：[https://github.com/ayufan/pve-backup-server-dockerfiles](https://github.com/ayufan/pve-backup-server-dockerfiles)

## 部署 Proxmox Backup Server

使用 Docker 或者 Docker Compose 方式部署都可以

- docker-compose.yaml

需要注意，要使用 tmpfs 方式挂载 /run 目录，用于容器内部创建临时文件和目录；

`/etc/proxmox-backup`: 用于存储 PVE Backup Server 的配置信息
`/var/log/proxmox-backup`: 用于存储日志信息
`/var/lib/proxmox-backup`：用于存储数据
`/backups`：存储容器、虚拟机的备份数据

```yaml
version: '2.1'

services:
  pve-backup-server:
    image: ayufan/proxmox-backup-server:latest
    ports:
      - "8007:8007"
    volumes:
      - /docker/PVEBackup/etc:/etc/proxmox-backup
      - /docker/PVEBackup/log:/var/log/proxmox-backup
      - /docker/PVEBackup/lib:/var/lib/proxmox-backup
      - /BackupServer:/backups
    tmpfs:
      - /run
    restart: unless-stopped
```

配置完成后启动容器，访问 `https://<ip>:8007/` 端口即可进行登录，默认的用户名是 `admin`，密码是 `pbspbs`，选择 `Proxmox Backup authentication server` 领域进行登录

![homelab-pve-backup-server-login-page.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-login-page.png)

## 配置存储

- 配置存储路径

在 Proxmox Backup Server 的数据存储中添加数据存储，将刚才映射的 `/backups` 目录作为存储路径

![homelab-pve-backup-server-add-backup-storage.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-add-backup-storage.png)

- 为用户添加权限

给用于备份的 root 和 admin 用户添加备份路径的访问权限

![homelab-pve-backup-server-add-backup-permission.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-add-backup-permission.png)

## 配置

- 获取 Proxmox Backup Server 的指纹

指纹用于在 PVE 中添加备份时进行认证

![homelab-pve-backup-server-show-printfinger.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-show-printfinger.png)

- 添加存储

在 PVE 的数据中心-存储中选择添加 Proxmox Backup Server，输入认证信息和指纹；Datastore 为 Proxmox Backup Server 的数据存储的名称，如 Backup

![homelab-pve-backup-server-add-data-storage.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-add-data-storage.png)

- 添加备份作业

在 PVE 的数据中心-备份中添加备份计划，按需添加，添加完成后选择现在运行即可开始备份

![homelab-pve-backup-server-add-backup-task.png](https://img.hellowood.dev/picture/homelab-pve-backup-server-add-backup-task.png)