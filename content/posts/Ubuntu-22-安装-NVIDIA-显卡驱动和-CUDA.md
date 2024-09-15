---
title: "Ubuntu 22 安装 NVIDIA 显卡驱动和 CUDA"
type: post
date: 2024-07-08T08:58:48+08:00
tags:
  - Ubuntu
  - NVIDIA
  - CUDA
series:
  - Ubuntu
  - NVIDIA
  - CUDA
featured: true
---


在 Ubuntu 22 上使用 NVIDIA 的显卡运行图像识别的训练，需要安装驱动和 CUDA

## 安装驱动

### 获取支持的驱动

- 更新 Ubuntu 依赖

```bash
sudo apt update
```

- 安装 ubuntu-drivers-common

`ubuntu-drivers-common` 是 Ubuntu 用于管理和安装第三方硬件驱动程序的工具，能够管理和安装硬件驱动程序

```bash
sudo apt install ubuntu-drivers-common
```

- 获取支持的驱动列表

`ubuntu-drivers` 获取适用于系统的 NVIDIA 驱动程序列表

```bash
sudo ubuntu-drivers devices
```

在输出信息中，可以看到设备是 `GeForce RTX 3070 Ti`, 推荐使用的驱动是 `nvidia-driver-555`

```bash
== /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0 ==
modalias : pci:v000010DEd00002482sv000010DEsd0000146Abc03sc00i00
vendor   : NVIDIA Corporation
model    : GA104 [GeForce RTX 3070 Ti]
driver   : nvidia-driver-550 - third-party non-free
driver   : nvidia-driver-520 - third-party non-free
driver   : nvidia-driver-525 - third-party non-free
driver   : nvidia-driver-555 - third-party non-free recommended
driver   : nvidia-driver-545-open - distro non-free
driver   : nvidia-driver-470-server - distro non-free
driver   : nvidia-driver-470 - distro non-free
driver   : nvidia-driver-535-open - distro non-free
driver   : nvidia-driver-515 - third-party non-free
driver   : nvidia-driver-535-server - distro non-free
driver   : nvidia-driver-550-open - third-party non-free
driver   : nvidia-driver-535 - third-party non-free
driver   : nvidia-driver-545 - third-party non-free
driver   : nvidia-driver-535-server-open - distro non-free
driver   : nvidia-driver-555-open - third-party non-free
driver   : xserver-xorg-video-nouveau - distro free builtin
```

### 安装 NVIDIA 驱动

- 安装驱动

```bash
apt install nvidia-driver-555
```

- 重启系统

等待安装完成后重启系统

```bash
sudo reboot
```

### 检查驱动状态

重新启动后，允许 `` 检查驱动状态

```bash
sudo nvidia-smi
```

可以看到，驱动的版本是 `555.42.06`，说明已经安装成功

```bash
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 555.42.06              Driver Version: 555.42.06      CUDA Version: 12.5     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3070 Ti     Off |   00000000:01:00.0  On |                  N/A |
| 30%   36C    P8              9W /  310W |       4MiB /   8192MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

## 安装 CUDA

### 安装 gcc

安装 CUDA 时需要使用 gcc，因此需要先安装 gcc

- 安装 gcc

```bash
sudo apt install gcc
```

- 检查 gcc

```bash
gcc -v
```

将会返回 gcc 的安装信息

```bash
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-linux-gnu/11/lto-wrapper
OFFLOAD_TARGET_NAMES=nvptx-none:amdgcn-amdhsa
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Ubuntu 11.4.0-1ubuntu1~22.04' --with-bugurl=file:///usr/share/doc/gcc-11/README.Bugs --enable-languages=c,ada,c++,go,brig,d,fortran,objc,obj-c++,m2 --prefix=/usr --with-gcc-major-version-only --program-suffix=-11 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --enable-bootstrap --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-vtable-verify --enable-plugin --enable-default-pie --with-system-zlib --enable-libphobos-checking=release --with-target-system-zlib=auto --enable-objc-gc=auto --enable-multiarch --disable-werror --enable-cet --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none=/build/gcc-11-XeT9lY/gcc-11-11.4.0/debian/tmp-nvptx/usr,amdgcn-amdhsa=/build/gcc-11-XeT9lY/gcc-11-11.4.0/debian/tmp-gcn/usr --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu --with-build-config=bootstrap-lto-lean --enable-link-serialization=2
Thread model: posix
Supported LTO compression algorithms: zlib zstd
gcc version 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04)
```

### 安装 CUDA

- 选择驱动版本

访问 [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads) 选择操作系统、架构、版本等信息，将会生成对应的 CUDA 安装命令

![homelab-NVIDIA-cuda-driver-download-page.png](https://img.hellowood.dev/picture/homelab-NVIDIA-cuda-driver-download-page.png)

- 安装 CUDA

使用 CUDA 网站提供的命令进行下载安装

```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-5
```

- 配置环境变量

安装完成后，还需要配置环境变量；将以下内容添加到 `~/.bashrc`；我使用的是 zsh，所以添加到 `~/.zshrc` 文件中

```bash
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64\
                         ${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

- 重启系统

配置完成后，重启系统

```bash
sudo reboot
```

### 检查 CUDA 状态

重启完成后，在命令行执行 `nvcc`命令检查

```bash
nvcc -V
```

会输出相关的 CUDA 信息

```bash
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on Thu_Jun__6_02:18:23_PDT_2024
Cuda compilation tools, release 12.5, V12.5.82
Build cuda_12.5.r12.5/compiler.34385749_0
```

## 参考文档

- [How to Install CUDA on Ubuntu 22.04 | Step-by-Step](https://www.cherryservers.com/blog/install-cuda-ubuntu)
- [CUDA Toolkit Downloads](https://developer.nvidia.com/cuda-downloads)
