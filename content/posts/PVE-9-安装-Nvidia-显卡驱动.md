---
date: 2026-03-23T09:18:55+08:00
description: "PVE9 内核 6.17 不支持 CUDA12，需降级至 6.14 安装 Nvidia 驱动 550 以兼容 Ollama，详解 proxmox-boot-tool 固定内核与 apt 安装步骤。"
# image: ""
lastmod: 2026-03-23
showTableOfContents: false
# tags: ["",]
title: "PVE 9 安装 Nvidia 显卡驱动"
keywords:
  - "Proxmox VE"
  - "LXC"
  - "NVIDIA Driver"
  - "Docker"
  - "GPU Passthrough"
  - "Ollama"
  - "pve-no-subscription"
  - "nvidia-smi"
slug: "pve-9-install-nvidia-driver"
aliases:
  - "/posts/pve-9-安装-nvidia-显卡驱动/"
type: "post"
tags:
  - Proxmox VE
  - HomeLab
  - NVIDIA
---

PVE 9 更新后使用的内核是 6.17，该内核版本支持的 Nvidia 驱动是 580+，对应的 cuda 版本是 13，但是 ollama 等依赖 cuda 12 的服务无法正常使用 GPU；Debian 13 推荐的 nvidia 驱动版本是 550，为了支持 cuda 12 的服务，需要将内核版本降低到6.14，然后安装 550 版本的驱动

## 检查内核版本

- 查看可用的内核版本

```bash
proxmox-boot-tool kernel list
```

输出如下，当前会自动选择最新的内核版本

```bash
Manually selected kernels:
None.

Automatically selected kernels:
6.17.13-1-pve
6.17.9-1-pve
```

- 查看当前生效的内核版本

```bash
uname -r
```

生效的版本是 6.17.13-1-pve，这个版本不支持 Nvidia 550 版本的驱动

```bash
6.17.13-1-pve
```

## 安装 6.14 内核

- 安装 6.14 版本内核包和头文件

```bash
apt install proxmox-kernel-6.14 proxmox-headers-6.14 --fix-missing
```

- 查看新增的内核版本

```bash
proxmox-boot-tool kernel list
```

输出如下，新增了 6.14.11-5-pve 版本

```bash
Manually selected kernels:
None.

Automatically selected kernels:
6.14.11-5-pve
6.17.13-1-pve
6.17.9-1-pve
```

- 固定内核版本为 6.14

```bash
proxmox-boot-tool kernel unpin
proxmox-boot-tool kernel pin 6.14.11-5-pve
```

- 刷新引导配置

```bash
proxmox-boot-tool refresh
```

- 查看内核列表

```bash
proxmox-boot-tool kernel list
```

看到 6.14.11-5-pve 版本被 pin 为默认启动

```bash
Manually selected kernels:
None.

Automatically selected kernels:
6.14.11-5-pve
6.17.13-1-pve
6.17.9-1-pve

Pinned kernel:
6.14.11-5-pve
```

- 重启服务器

重启服务器后使内核版本生效

```bash
reboot
```

- 验证生效的内核版本

```bash
uname -r
6.14.11-5-pve
```

说明内核版本已经生效，当前版本为 6.14.11-5-pve

## 安装 Nvidia 驱动

安装 Nvidia 驱动的流程参考[Proxmox VE LXC 容器中安装 NVIDIA 显卡驱动并在 Docker 中使用](https://blog.hellowood.dev/posts/proxmox-ve-lxc-nvidia-driver-docker/)，选择 550 版本的驱动下载安装即可

```bash
nvidia-smi
```

输出如下，说明驱动已经正确安装

```bash
nvidia-smi
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.163.01             Driver Version: 550.163.01     CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3060        Off |   00000000:01:00.0 Off |                  N/A |
|  0%   56C    P8             14W /  170W |    5654MiB /  12288MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
+-----------------------------------------------------------------------------------------+
```
