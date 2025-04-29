---
date: 2025-03-24
lastmod: 2025-03-24
showTableOfContents: false
title: "Proxmox VE LXC 容器中安装 NVIDIA 显卡驱动并在 Docker 中使用"
type: "post"
tags:
  - Proxmox VE
  - HomeLab
  - NVIDIA
featured: true
---

在 PVE 的 LXC 容器中使用 NVIDIA 显卡，用于 Ollama 等模型推理或者 GPU 加速的应用

## 一、PVE 安装 NVIDIA 驱动

### 1.1 修改订阅源

- 修改 `/etc/apt/sources.list` 文件，添加 pve-no-subscription 源；完整的配置如下:

```bash
deb http://mirrors.tuna.tsinghua.edu.cn/debian bookworm main contrib non-free non-free-firmware
deb http://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware
deb http://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
```

- 更新

```bash
apt update
```

### 1.2 安装 NVIDIA 驱动

- 安装内核头文件

pve-headers 允许 DKMS 机制在内核更新时自动重新编译需要编译和安装动态内核模块，即 NVIDIA 驱动

```bash
apt install pve-headers
```

- 下载驱动

访问 [https://www.nvidia.cn/drivers/unix/](https://www.nvidia.cn/drivers/unix/)，找到 `Linux x86_64/AMD64/EM64T`
![homelab-pve-nvidia-driver-install-download-0.png](https://img.hellowood.dev/picture/homelab-pve-nvidia-driver-install-download-0.png)

点击[压缩文件](https://www.nvidia.cn/drivers/unix/linux-amd64-display-archive/)查看历史版本，选择 `535.216.01` 版本(ubuntu 22 推荐的版本)
![homelab-pve-nvidia-driver-install-download-1.png](https://img.hellowood.dev/picture/homelab-pve-nvidia-driver-install-download-1.png)

点击链接查看驱动详细信息，右键复制下载链接地址
![homelab-pve-nvidia-driver-install-download-2.png](https://img.hellowood.dev/picture/homelab-pve-nvidia-driver-install-download-2.png)

然后在 PVE 宿主机中通过 wget 下载驱动

```bash
wget https://cn.download.nvidia.com/XFree86/Linux-x86_64/535.216.01/NVIDIA-Linux-x86_64-535.216.01.run
```

![homelab-pve-nvidia-driver-install-lxc-install.png](https://img.hellowood.dev/picture/homelab-pve-nvidia-driver-install-lxc-install.png)

- 授予执行权限

```bash
chmod +x ./NVIDIA-Linux-x86_64-535.216.01.run
```

- 安装驱动

```bash
./NVIDIA-Linux-x86_64-535.216.01.run
```

### 1.3 重启系统

安装完成后需要重启 PVE

```bash
reboot
```

### 1.4 验证 NVIDIA 驱动

```bash
nvidia-smi
```

正确返回显卡的信息说明驱动已经正确安装

```bash
Sat Mar 29 23:31:27 2025
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.216.01             Driver Version: 535.216.01   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3060        On  | 00000000:01:00.0 Off |                  N/A |
| 53%   49C    P8              14W / 170W |      3MiB / 12288MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+

+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|  No running processes found                                                           |
+---------------------------------------------------------------------------------------+
```

## 二、LXC 容器安装 NVIDIA 驱动

LXC 容器中安装 NVIDIA 驱动之前需要先将显卡挂载到容器中，然后在容器中安装 NVIDIA 驱动

### 2.1 挂载 NVIDIA 设备

在 PVE 宿主机中将显卡挂载到容器中

#### 2.1.1 获取 NVIDIA 设备的主次编号

```bash
ls /dev/nvidia* -l
```

返回信息如下, 对应的设备编号是 `195, 0` 和 `195, 255` 等

```bash
crw-rw-rw- 1 root root 195,   0 Mar 23 23:02 /dev/nvidia0
crw-rw-rw- 1 root root 195, 255 Mar 23 23:02 /dev/nvidiactl
crw-rw-rw- 1 root root 195, 254 Mar 23 23:02 /dev/nvidia-modeset
crw-rw-rw- 1 root root 234,   0 Mar 23 23:03 /dev/nvidia-uvm
crw-rw-rw- 1 root root 234,   1 Mar 23 23:03 /dev/nvidia-uvm-tools

/dev/nvidia-caps:
total 0
cr-------- 1 root root 238, 1 Mar 23 23:03 nvidia-cap1
cr--r--r-- 1 root root 238, 2 Mar 23 23:03 nvidia-cap2
```

相关设备作用如下：

- 设备文件列表及作用

| 设备文件                    | 作用描述                                                          |
| --------------------------- | ----------------------------------------------------------------- |
| **`/dev/nvidia0`**          | 代表第一块 GPU，多个 GPU 会有 `/dev/nvidia1` 等                   |
| **`/dev/nvidiactl`**        | 控制 NVIDIA 驱动程序，管理 GPU 资源                               |
| **`/dev/nvidia-modeset`**   | 负责 GPU 显示模式管理（适用于 Xorg/Wayland）                      |
| **`/dev/nvidia-uvm`**       | 负责 **Unified Virtual Memory (UVM)** 机制，支持 CPU-GPU 共享内存 |
| **`/dev/nvidia-uvm-tools`** | 提供 UVM 相关的工具支持                                           |

- `/dev/nvidia-caps/` 目录

此目录包含 **与 GPU 访问控制相关的设备文件**，用于限制对某些 GPU 功能的访问。

| 设备文件                           | 作用描述                                                                    |
| ---------------------------------- | --------------------------------------------------------------------------- |
| **`/dev/nvidia-caps/nvidia-cap1`** | 仅 `root` 可访问，通常与安全关键的 GPU 功能（如 `nvidia-persistenced`）相关 |
| **`/dev/nvidia-caps/nvidia-cap2`** | 允许所有用户读取，可能用于 GPU 监控等非特权操作                             |

#### 2.1.2 将设备挂载到 LXC 容器中

设备部分的主设备号填写上面获取的主设备号，次设备号填写 `*`即可；3060 显卡的设备号是 `195`，`234`，`238`

```bash
nano /etc/pve/lxc/100.conf
```

添加以下内容：

```bash
lxc.cgroup2.devices.allow: c 195:* rwm
lxc.cgroup2.devices.allow: c 234:* rwm
lxc.cgroup2.devices.allow: c 238:* rwm
lxc.mount.entry: /dev/nvidia0 dev/nvidia0 none bind,optional,create=file
lxc.mount.entry: /dev/nvidiactl dev/nvidiactl none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm dev/nvidia-uvm none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-modeset dev/nvidia-modeset none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-uvm-tools none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-caps/nvidia-cap1 none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm-tools dev/nvidia-caps/nvidia-cap2 none bind,optional,create=file
```

然后重启 LXC 容器即可

```bash
pct reboot 100
```

### 2.2 安装 NVIDIA 驱动

进入 LXC 容器安装 NVIDIA 驱动，LXC 容器中的驱动版本需要和宿主机的版本一致，否则可能会返回 `Failed to initialize NVML: Driver/library version mismatch NVML library version: 535.230`

~~在宿主机可以直接使用 apt 安装，这样能保证驱动是 PVE 兼容的版本；但是在 LXC 容器中可能因为系统、版本不一样，安装的驱动并不是宿主机兼容的版本，所以需要手动下载驱动~~

即使在 PVE 中通过 apt 安装的驱动版本和 LXC 中安装的版本一样，依然可能存在不兼容的问题，所以无论是 LXC容器还是 PVE 宿主机，都建议手动下载安装相同的驱动

#### 2.2.1 下载驱动

- 下载驱动

和宿主机下载驱动一样通过 wget 下载即可

#### 2.2.2 安装驱动

- 授予执行权限

```bash
chmod +x ./NVIDIA-Linux-x86_64-535.216.01.run
```

- 安装驱动

因为 LXC 容器共享宿主机的内核，所以安装时需要指定 `--no-kernel-module` 参数，避免安装内核模块

```bash
./NVIDIA-Linux-x86_64-535.216.01.run --no-kernel-module
```

![homelab-pve-nvidia-driver-install-lxc-install-2.png](https://img.hellowood.dev/picture/homelab-pve-nvidia-driver-install-lxc-install-2.png)

- 重启 LXC 容器

```bash
reboot
```

### 2.3 验证 NVIDIA 驱动

```bash
nvidia-smi
```

正确返回显卡的信息说明驱动已经正确安装

```bash
Sun Mar 30 03:25:12 2025
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.216.01             Driver Version: 535.216.01   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3060        Off | 00000000:01:00.0 Off |                  N/A |
|  0%   43C    P8               6W / 170W |      1MiB / 12288MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+

+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|  No running processes found                                                           |
+---------------------------------------------------------------------------------------+
```

## 三、Docker 容器使用 NVIDIA 显卡

### 3.1 修改 LXC 配置

在 LXC 容器中安装 NVIDIA Container Toolkit，需要修改 LXC 容器的配置，允许容器使用 GPU

- 修改 `/etc/pve/lxc/100.conf` 文件

禁用 AppArmor 安全策略，授予 Docker 容器完全访问权限

```conf
lxc.apparmor.profile: unconfined
```

### 3.1 安装 NVIDIA Container Toolkit

- 添加 NVIDIA Container Toolkit 软件源

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

- 更新并安装 NVIDIA Container Toolkit

```bash
sudo apt update && sudo apt install -y nvidia-container-toolkit
```

### 3.2 配置运行时环境

- 配置 Docker 运行时环境

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

将会修改 `/etc/docker/daemon.json` 文件，添加 nvidia-container-runtime 配置

```bash
INFO[0000] Loading config from /etc/docker/daemon.json
INFO[0000] Wrote updated config to /etc/docker/daemon.json
INFO[0000] It is recommended that docker daemon be restarted.
```

- 重启 Docker 服务

```bash
sudo systemctl restart docker
```

### 容器中使用 NVIDIA 显卡

- 启动容器

```bash
docker run --rm --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi
```

正确返回显卡的信息说明 NVIDIA 显卡已经正确挂载到容器

```bash
Sun Mar 30 03:38:52 2025
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.216.01             Driver Version: 535.216.01   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3060        Off | 00000000:01:00.0 Off |                  N/A |
|  0%   43C    P8               6W / 170W |      1MiB / 12288MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+

+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|  No running processes found                                                           |
+---------------------------------------------------------------------------------------+
```

- Docker Compose 中使用 NVIDIA 显卡

```yaml
version: "3.8"

services:
  cuda-nvidia-smi:
    image: nvidia/cuda:12.2.2-base-ubuntu22.04
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: ["gpu"]
    entrypoint: ["nvidia-smi"]
```

## 参考文档

- [How to Install Nvidia Drivers on Proxmox](https://gist.github.com/Cyberes/bc33b3f4d36742ea7a036a8c7c37061e)
- [egg82/proxmox_nvidia.md](https://gist.github.com/egg82/90164a31db6b71d36fa4f4056bbee2eb#containerlxc)
- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
