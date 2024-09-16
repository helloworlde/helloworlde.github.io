---
title: "Ubuntu 22 安装 Intel N100 显卡驱动"
type: post
date: 2024-07-08T08:41:49+08:00
tags:
  - Ubuntu
  - Intel
featured: true
---

最近 N5105 的 HomeLab Server 负载过高，CPU 长期接近100%，因此新购入一台 N100，将视频和图像相关的服务迁移到 N100，但是发现 Ubuntu 22 默认没有显卡驱动，需要手动安装

## 检查驱动状态

使用 intel_gpu_top 检查显卡状态，发现提示没有设备，这是因为没有安装驱动导致的

- 安装 intel-gpu-tools

```bash
sudo apt install intel-gpu-tools
```

- 检查状态

```bash
intel_gpu_top
```

```bash
No device filter specified and no discrete/integrated i915 devices found
```

## 安装驱动

### 配置软件源

- 安装依赖工具

```bash
sudo apt update
sudo apt install -y gpg-agent wget
```

- 添加 Intel 软件源

运行以下命令，将 Intel 软件源添加到 apt 的配置中并更新

```bash
. /etc/os-release
if [[ ! " jammy " =~ " ${VERSION_CODENAME} " ]]; then
  echo "Ubuntu version ${VERSION_CODENAME} not supported"
else
  wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
    sudo gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu ${VERSION_CODENAME}/lts/2350 unified" | \
    sudo tee /etc/apt/sources.list.d/intel-gpu-${VERSION_CODENAME}.list
  sudo apt update
fi
```

### 安装驱动

安装依赖的软件和显卡驱动

```bash
sudo apt install -y \
  linux-headers-$(uname -r) \
  linux-modules-extra-$(uname -r) \
  flex bison \
  intel-fw-gpu intel-i915-dkms xpu-smi
```

- 重启系统

安装完成后重启系统

```bash
sudo reboot
```

### 安装计算和媒体软件包

- 计算和媒体运行时的软件包

这些软件用于 OpenCL、硬件加速编解码、媒体 SDK 等；部分视频软件需要用到

```bash
sudo apt install -y \
  intel-opencl-icd intel-level-zero-gpu level-zero \
  intel-media-va-driver-non-free libmfx1 libmfxgen1 libvpl2 \
  libigdgmm12 vainfo hwinfo clinfo
```

### 配置用户组

#### 检查用户访问权限

用户必须加入特定组才能访问 GPU 的某些功能，渲染组专门允许访问渲染任务的 GPU 资源

```bash
stat -c "%G" /dev/dri/render*
groups ${USER}
```

输出以下信息说明已经有权限访问

```bash
render
root : root
```

#### 添加访问权限

如果当前用户没有权限，可以通过以下命令添加

- 添加渲染节点组权限

```bash
sudo gpasswd -a ${USER} render
```

- 修改 shell 权限组

将用户的有效组 ID 更改为 render 组

```bash
newgrp render
```

## 验证

### 验证 i915 驱动

使用 `hwinfo` 验证

```bash
hwinfo --display
```

输出以下内容

```bash
25: PCI 02.0: 0300 VGA compatible controller (VGA)
  [Created at pci.386]
  Unique ID: _Znp.i4vzlYvwb6C
  SysFS ID: /devices/pci0000:00/0000:00:02.0
  SysFS BusID: 0000:00:02.0
  Hardware Class: graphics card
  Device Name: "Onboard - Video"
  Model: "Intel VGA compatible controller"
  Vendor: pci 0x8086 "Intel Corporation"
  Device: pci 0x46d1
  SubVendor: pci 0x8086 "Intel Corporation"
  SubDevice: pci 0x7270
  Driver: "i915"
  Driver Modules: "i915"
  Memory Range: 0x6000000000-0x6000ffffff (rw,non-prefetchable)
  Memory Range: 0x4000000000-0x400fffffff (ro,non-prefetchable)
  I/O Ports: 0x3000-0x303f (rw)
  Memory Range: 0x000c0000-0x000dffff (rw,non-prefetchable,disabled)
  IRQ: 142 (130402731 events)
  Module Alias: "pci:v00008086d000046D1sv00008086sd00007270bc03sc00i00"
  Driver Info #0:
    Driver Status: i915 is active
    Driver Activation Cmd: "modprobe i915"
  Config Status: cfg=new, avail=yes, need=no, active=unknown

Primary display adapter: #25
```

### 检查 GPU 硬件信息

使用 `xpu-smi` 检查 GPU 的信息

```bash
sudo xpu-smi discovery -d 0
```

输出 GPU 的信息：

```bash
+-----------+--------------------------------------------------------------------------------------+
| Device ID | Device Information                                                                   |
+-----------+--------------------------------------------------------------------------------------+
| 0         | Device Type: GPU                                                                     |
|           | Device Name: Intel(R) UHD Graphics                                                   |
|           | PCI Device ID: 0x46d1                                                                |
|           | Vendor Name: Intel(R) Corporation                                                    |
|           | SOC UUID: 00000000-0000-0200-0000-000046d18086                                       |
|           | Serial Number: unknown                                                               |
|           | Core Clock Rate: 750 MHz                                                             |
|           | Stepping: A0                                                                         |
|           | SKU Type: N/A                                                                        |
|           |                                                                                      |
|           | Driver Version: I915_23.10.49_PSB_231129.51                                          |
|           | Kernel Version: 5.15.0-113-generic                                                   |
|           | GFX Firmware Name: GFX                                                               |
|           | GFX Firmware Version: unknown                                                        |
|           | GFX Firmware Status: unknown                                                         |
|           |                                                                                      |
|           | PCI BDF Address: 0000:00:02.0                                                        |
|           | PCI Slot: N/A                                                                        |
|           | PCIe Generation: -1                                                                  |
|           | PCIe Max Link Width: -1                                                              |
|           |                                                                                      |
|           | Memory Physical Size: 0.00 MiB                                                       |
|           | Max Mem Alloc Size: 4095.99 MiB                                                      |
|           | ECC State: N/A                                                                       |
|           | Number of Memory Channels: N/A                                                       |
|           | Memory Bus Width: N/A                                                                |
|           | Max Hardware Contexts: 65536                                                         |
|           | Max Command Queue Priority: 0                                                        |
|           |                                                                                      |
|           | Number of EUs: 32                                                                    |
|           | Number of Tiles: 1                                                                   |
|           | Number of Slices: 1                                                                  |
|           | Number of Sub Slices per Slice: 2                                                    |
|           | Number of Threads per EU: 7                                                          |
|           | Physical EU SIMD Width: 8                                                            |
|           | Number of Media Engines: 1                                                           |
|           | Number of Media Enhancement Engines: 1                                               |
|           |                                                                                      |
|           | Number of Xe Link ports: N/A                                                         |
|           | Max Tx/Rx Speed per Xe Link port: N/A                                                |
|           | Number of Lanes per Xe Link port: N/A                                                |
+-----------+--------------------------------------------------------------------------------------+
```

### 检查 GPU 使用情况

```bash
intel_gpu_top
```

会输出当前 GPU 的使用情况

```bash
ntel-gpu-top: 8086:46d1 @ /dev/dri/card0 -  253/ 252 MHz;  77% RC6;      109 irqs/s

         ENGINES     BUSY                                                                 MI_SEMA MI_WAIT
       Render/3D    6.50% |████                                                         |      0%      0%
         Blitter    0.00% |                                                             |      0%      0%
           Video   16.39% |██████████                                                   |      0%      0%
    VideoEnhance    4.07% |██▌                                                          |      0%      0%
```

## 参考文档

- [Ubuntu Install Steps](https://dgpu-docs.intel.com/driver/installation.html#ubuntu-install-steps)
- [Verifying Installation](https://dgpu-docs.intel.com/driver/verification.html)
