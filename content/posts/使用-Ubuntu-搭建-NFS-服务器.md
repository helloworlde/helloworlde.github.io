---
title: 使用 Ubuntu 搭建 NFS 服务器
type: post
date: 2024-01-27T11:20:19+08:00
tags:
    - Ubuntu
    - HomeLab
categories: 
    - Ubuntu
    - HomeLab
series: 
    - Ubuntu
    - HomeLab
featured: true
---

NFS(Network File System) 是由 Sun 公司提出的分布式文件系统协议，可以通过网络共享远程目录；默认没有加密，不提供身份验证，而是通过客户端 IP 或主机名限制客户端的访问

## 搭建 Server 端

### 安装 nfs-kernel-server

NFS 的 Server 端由 `nfs-kernel-server` 提供，使用 apt 进行安装

```bash
apt update
apt install -y nfs-kernel-server
```

安装完成后，使用 	`systemctl` 查看状态

```bash
systemctl status nfs-mountd.service
```

```bash
● nfs-mountd.service - NFS Mount Daemon
     Loaded: loaded (/lib/systemd/system/nfs-mountd.service; static)
     Active: active (running) since Thu 2022-09-22 18:43:43 CST; 1h 5min ago
   Main PID: 128914 (rpc.mountd)
      Tasks: 1 (limit: 4415)
     Memory: 556.0K
        CPU: 59ms
     CGroup: /system.slice/nfs-mountd.service
             └─128914 /usr/sbin/rpc.mountd

Sep 22 18:43:43 rasp systemd[1]: Starting NFS Mount Daemon...
Sep 22 18:43:43 rasp rpc.mountd[128914]: Version 2.6.1 starting
Sep 22 18:43:43 rasp systemd[1]: Started NFS Mount Daemon.
```

### 修改 NFS 配置

- 创建挂载目录并修改权限

首先，创建需要分享的目录，如 `/data/nfs`

```bash
mkdir -p /data/nfs
```
创建后的文件夹属于当前用户，被挂载后可能会提示权限不足，导致无法操作；因此需要先将这个目录的用户和组修改为 `nobody` 和 `nogroup`

```bash
sudo chown nobody:nogroup /data/nfs
```

- 指定要分享的目录

修改 `/etc/exports`，指定分享的目录`/data/nfs`，同时允许 `192.168.2.0/24`网段可以使用异步的方式读写，不检查子文件夹权限，不能使用 root 身份操作文件夹

```
/data/nfs 192.168.2.0/24(rw,async,no_subtree_check,no_root_squash)
```

修改完成后重启 NFS 服务

```bash
sudo systemctl restart nfs-kernel-server.service
```

## 客户使用 NFS 

### 挂载 NFS 

在 Mac 或其他的 Linux 服务器上挂载该 NFS 文件夹

```bash
mount -t nfs 192.168.2.5:/data/nfs /mnt/nfs
```

使用 df 命令检查

```bash
df -h

Filesystem                         Size  Used Avail Use% Mounted on
tmpfs                              393M  4.4M  389M   2% /run
/dev/mapper/ubuntu--vg-ubuntu--lv   38G   18G   19G  50% /
tmpfs                              2.0G     0  2.0G   0% /dev/shm
tmpfs                              5.0M     0  5.0M   0% /run/lock
/dev/sda2                          2.0G  246M  1.6G  14% /boot
tmpfs                              393M  4.0K  393M   1% /run/user/0
192.168.2.5:/data/nfs              118G  4.7G  108G   5% /data/nfs
```

### 开机后自动挂载 

编辑 `/etc/fstab`，将要挂载的目录添加进去

```
192.168.2.5:/data/nfs    /mnt/nfs   nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
```