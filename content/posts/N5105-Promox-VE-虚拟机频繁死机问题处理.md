---
title: N5105 Promox VE 虚拟机频繁死机问题处理
type: post
date: 2023-03-25T21:31:50+08:00
tags:
  - Proxmox VE
  - HomeLab
featured: true
---

使用 N5105 作为 HomeLab 的服务器；之前安装的 ESXi，使用 Ubuntu 22 的时候经常会出现 Ubuntu CPU 占用达到100%，然后死机；但是其他的虚拟机都没有问题，因为对 Linux 并不熟，查看了 ESXi 和 Ubuntu 日志并没有异常；后面安装黑群晖一直失败，因此换到了 Proxmox VE

换到 PVE 后依然存在同样的问题，以为是服务的问题，于是给 Docker 容器添加了资源限制，无效后迁移到了 CentOS 部署，发现还是同样的问题；并且越来越频繁，从一天一次变成了几小时一次，几乎无法使用

猜测会不会是硬件问题，一番搜索发现在 N5105 上居然是个普遍的问题

## 问题

这个问题于 2022-08-04 在 Proxmox 的问题反馈中提交：[Bug 4188 - VMs freeze on Intel N5105 CPU](https://bugzilla.proxmox.com/show_bug.cgi?id=4188)，描述中"到运行Intel N5105 CPU的一些用户注意到在Proxmox上运行的虚拟机会冻结，并记录了各种错误。虚拟机会冻结，控制台无法输入，CPU利用率达到最大值，直到强制重启虚拟机"，现象和我遇到的是一样的，说明该现象是通病；

![homelab-pve-vm-freeze-issue-bug-feedback.png](https://img.hellowood.dev/picture/homelab-pve-vm-freeze-issue-bug-feedback.png)

2022-9-13 在帖子 [Opt-in Linux 5.19 Kernel for Proxmox VE 7.x available](https://forum.proxmox.com/threads/opt-in-linux-5-19-kernel-for-proxmox-ve-7-x-available.115090/) 中，PVE员工宣布将 PVE 的内核升级到 5.19版本，在 Bug 反馈到讨论中有不少人确认有效

![homelab-pve-vm-freeze-issue-519-kenel.png](https://img.hellowood.dev/picture/homelab-pve-vm-freeze-issue-519-kenel.png)

这个问题在 2022-12-06 状态变更为 'FIX PACKAGED'；在 2022-12-14，PVE员工宣布支持将内核升级到 6.1

![homelab-pve-vm-freeze-issue-61-kenel.png](https://img.hellowood.dev/picture/homelab-pve-vm-freeze-issue-61-kenel.png)

在 Bug 反馈的最后几条评论中，反馈死机的问题在升级 5.19 或 6.1 的内核后确实减少了，但是依然可能出现

![homelab-pve-vm-freeze-issue-bug-comments2.png](https://img.hellowood.dev/picture/homelab-pve-vm-freeze-issue-bug-comments2.png)

## 修复

按照 PVE 的回复，需要将 Linux 内核升级到 5.19 版本

### 修改订阅源

- 关闭企业订阅源

该订阅源是付费版本的订阅源，提供例如集群管理、备份和恢复等功能，未购买时无法使用，因此需要将其移除；为了保险将文件重命名为 backup

```bash
mv /etc/apt/sources.list.d/pve-enterprise.list /etc/apt/sources.list.d/pve-enterprise.list.backup
```

- 添加非订阅源

"pve-no-subscription" 是 Proxmox VE 软件包源名称中的一个参数，代表这个软件包源提供的是免费版本的 Proxmox VE 软件包， "bullseye" 是 Debian GNU/Linux 操作系统的一个版本号，是该操作系统的第11个主要发行版

```bash
echo 'deb http://download.proxmox.com/debian/pve bullseye pve-no-subscription' >> /etc/apt/sources.list.d/pve-no-subscription.list
```

- 添加 Debian non-free 源

添加 non-free 是为了更新 Microcode，默认的软件源不包含 non-free

```bash
tee /etc/apt/sources.list.d/debian-non-free.list > /dev/null <<EOF
deb http://deb.debian.org/debian bullseye main contrib non-free
deb http://security.debian.org/debian-security bullseye-security main contrib non-free
deb http://deb.debian.org/debian bullseye-updates main contrib non-free
EOF
```

在Debian操作系统中，软件包分为三个部分：main，contrib和non-free。其中，main 和 contrib 部分的软件都是自由软件，它们遵循自由软件定义（Free Software Definition），可以自由地使用、修改、复制和重新分发。

而 non-free 部分则包含了一些不符合自由软件定义的软件，例如某些专有硬件驱动程序、特定格式的音频和视频编码器等。这些软件可能有一些限制，例如不允许用户对其进行修改或重新分发。因此，这些软件在Debian社区中并不被认为是自由软件。

`deb http://deb.debian.org/debian bullseye main contrib non-free` 这是Debian操作系统的主要软件源，其中包含了Debian操作系统的核心软件包和一些第三方软件包，其中contrib和non-free分别代表自由度不同的软件包。

`deb http://security.debian.org/debian-security bullseye-security main contrib non-free` 这个源提供了Debian操作系统安全更新的软件包。这些软件包通常修复已知的漏洞和安全问题。

`deb http://deb.debian.org/debian bullseye-updates main contrib non-free` 这个源提供了针对Debian操作系统稳定版本的非安全更新的软件包。这些软件包通常修复错误并提供新功能。

### 更新 5.19 版本的内核

更新软件后安装 5.19 版本的内核

```bash
apt update -y
apt install pve-kernel-5.19 -y
```

### 安装 Intel CPU microcode

处理器微码([Microcode] )。

intel-microcode 作用是为英特尔处理器提供微码（[microcode](https://wiki.debian.org/Microcode)）更新。微码是一组指令，类似于处理器固件，可以在处理器上执行，以改变其行为或修复错误，内核能够在不需要通过BIOS更新的情况下更新处理器的固件。微码更新保存在易失性存储器中，因此BIOS/UEFI或内核会在每次启动时更新微码

intel-microcode 的更新通常由操作系统或设备厂商提供，旨在提高处理器的性能、稳定性和安全性。

```bash
apt update -y
apt install intel-microcode -y
```

### 重启

等待更新完成后重启即可

```bash
reboot
```

重启后查看 Linux 内核版本，已经更新到了 `5.19.17-2-pve`

```bash
uname -r

5.19.17-2-pve
```

查看 Microcode 版本，可以看到更新到 `0x24000023` 版本，发布日期是 2022-02-19

```bash
dmesg | grep microcode

[    0.000000] microcode: microcode updated early to revision 0x24000023, date = 2022-02-19
[    0.203334] SRBDS: Vulnerable: No microcode
[    1.337062] microcode: sig=0x906c0, pf=0x1, revision=0x24000023
[    1.337093] microcode: Microcode Update Driver: v2.2.
```
