---
date: 2025-04-20
# description: ""
# image: ""
lastmod: 2025-04-20
showTableOfContents: false
tags:
  - Ubuntu
  - AMD
  - Driver
title: "Ubuntu 24 安装 AMD 780M 显卡驱动和 ROCm"
type: "post"
featured: true
---

ROCm (Radeon Open Compute) 是由 AMD 开发的开源软件平台，专为加速计算而设计，开源用于深度学习、机器学习和图形处理等应用程序。定位和 NVIDIA 的 CUDA 相同

## 安装 ROCm

### 添加 rocm 源

- 添加 gpg 密钥

```bash
sudo mkdir --parents --mode=0755 /etc/apt/keyrings
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | \
    gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/nul
```

- 添加源

分别添加 AMDGPU 驱动程序的软件源和 ROCm 软件源，并设置软件源的优先级，确保在有多个版本可用时，系统会优先安装来自 AMD 官方仓库的软件包

```bash
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/amdgpu/6.4/ubuntu jammy main" \
    | sudo tee /etc/apt/sources.list.d/amdgpu.list
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.4 noble main" \
    | sudo tee --append /etc/apt/sources.list.d/rocm.list
echo -e 'Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600' \
    | sudo tee /etc/apt/preferences.d/rocm-pin-600
```

- 更新软件包

```bash
sudo apt update
```

### 安装 ROCm

- 安装 ROCm

使用 apt 安装 ROCm 时会自动安装相关的依赖项，包括驱动、内核模块和相关工具

```bash
sudo apt install rocm
```

### 检查

- rocminfo 查看显卡信息

rocminfo 是一个用于查询 ROCm 设备信息的工具，它可以列出系统中可用的 ROCm 平台和设备，以及每个设备的属性和特性。

```bash
rocminfo
```

```bash
ROCk module is loaded
=====================
HSA System Attributes
=====================
Runtime Version:         1.15
Runtime Ext Version:     1.7
System Timestamp Freq.:  1000.000000MHz
Sig. Max Wait Duration:  18446744073709551615 (0xFFFFFFFFFFFFFFFF) (timestamp count)
Machine Model:           LARGE
System Endianness:       LITTLE
Mwaitx:                  DISABLED
XNACK enabled:           NO
DMAbuf Support:          YES
VMM Support:             YES
 # ...
```

- clinfo

clinfo 是一个用于查询 OpenCL 设备信息的工具。它可以列出系统中可用的 OpenCL 平台和设备，以及每个设备的属性和特性。
使用 clinfo 可以查看设备的名称、供应商、版本、计算单元数量、最大工作项数量、最大工作组大小、最大内存分配等信息。这对于选择适合的 OpenCL 设备和优化程序性能非常有用

```bash
clinfo
```

```bash
Number of platforms:				 1
  Platform Profile:				 FULL_PROFILE
  Platform Version:				 OpenCL 2.1 AMD-APP (3649.0)
  Platform Name:				 AMD Accelerated Parallel Processing
  Platform Vendor:				 Advanced Micro Devices, Inc.
  Platform Extensions:				 cl_khr_icd cl_amd_event_callback


  Platform Name:				 AMD Accelerated Parallel Processing
Number of devices:				 1
  Device Type:					 CL_DEVICE_TYPE_GPU
  Vendor ID:					 1002h
  Board name:					 AMD Radeon Graphics

# ...
```

- rocm-smi

rocm-smi 是一个用于监视和管理 ROCm 设备的工具。它可以显示设备的当前状态、温度、功耗、内存使用情况等信息

```bash
rocm-smi
```

```bash
============================================ ROCm System Management Interface ============================================
====================================================== Concise Info ======================================================
Device  Node  IDs              Temp    Power     Partitions          SCLK  MCLK     Fan  Perf  PwrCap       VRAM%  GPU%
              (DID,     GUID)  (Edge)  (Socket)  (Mem, Compute, ID)
==========================================================================================================================
0       1     0x1900,   58154  45.0°C  20.054W   N/A, N/A, 0         None  2400Mhz  0%   auto  Unsupported  4%     0%
==========================================================================================================================
================================================== End of ROCm SMI Log ===================================================
```
