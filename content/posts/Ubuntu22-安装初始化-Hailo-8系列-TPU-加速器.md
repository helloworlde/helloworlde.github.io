---
title: "Ubuntu22 安装初始化 Hailo 8系列 TPU 加速器"
date: 2024-09-01T11:22:23+08:00
tags: 
    - Ubuntu
    - Hailo
    - TPU
series: 
    - Ubuntu
    - Hailo
    - TPU
featured: true
---

> Hailo 是一家位于以色列的边缘人工智能处理器的先驱芯片制造商，该公司成立于2017年；专注于为边缘设备开发高效的深度学习处理器。Hailo 的核心产品是其自研的 Hailo-8 人工智能处理器，这款芯片特别设计用于在资源受限的边缘设备上运行复杂的深度学习模型

> Hailo-8 能够在嵌入式系统中支持实时处理应用，如计算机视觉、自动驾驶、智能城市监控、医疗设备和工业物联网等

> Hailo 在 2024年6月4日宣布被 Raspberry Pi 选中，为 Raspberry Pi AI Kit 提供 AI 加速器；支持使用 Hailo-8 和 Hailo-8L 进行加速，参考 [Raspberry Pi Selects Hailo to Enable Advanced AI Capabilities for Raspberry Pi 5](https://hailo.ai/zh-hans/company-overview/newsroom/news-zh-hans/raspberry-pi-selects-hailo-to-enable-advanced-ai-capabilities-for-raspberry-pi-5/)


Hailo8 发布于 2021年，算力为 26 TOPS，Hailo8L 发布于 2023 年，算力为 13 TOPS；两款产品除了算力外，其他特性差别不大，均支持 TensorFlow，TensorFlow Lite，Keras，PyTorch & ONNX 框架，主机架构支持 X86 和 ARM，操作系统支持 Linux 和 Windows；更多信息参考官网介绍：
- [Hailo-8 AI处理器](https://hailo.ai/zh-hans/products/ai-accelerators/hailo-8-ai-accelerator/#hailo-8-features)
- [Hailo-8L M.2 Entry-Level Acceleration Module](https://hailo.ai/zh-hans/products/ai-accelerators/hailo-8l-m-2-ai-acceleration-module-for-ai-light-applications/#hailo8lm2-features)
- [hailo-8-product-brief](https://hailo.ai/files/hailo-8-product-brief-en/)
- [hailo-8l-m-2-et-product-brief](https://hailo.ai/files/hailo-8l-m-2-et-product-brief-en/)

# Hailo 环境配置

Hailo 相关软件功能如图：

![](https://hailo.ai/wp-content/uploads/2023/09/HailoRT-Diagram.png)

## 驱动

### 安装驱动

- 安装依赖

安装驱动依赖一些软件，需要提前安装 

```bash
apt update && apt install -y dpkg
```

- 下载驱动

Hailo 的软件下载比较麻烦，需要注册其 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 账号之后才能下载

软件选择 HailoRT，然后选择对应的平台和版本，选择 'HailoRT – PCIe driver Ubuntu package (deb)' 进行下载，下载完成后即可开始安装

![homelab-tpu-hailo-software-download-page.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-page.png)

- 安装 Pcie 驱动 

```bash
sudo dpkg --install hailort-pcie-driver_4.18.0_all.deb
```

```bash
正在选中未选择的软件包 hailort-pcie-driver。
(正在读取数据库 ... 系统当前共安装有 187606 个文件和目录。)
准备解压 hailort-pcie-driver_4.18.0_all.deb  ...
Verifying secureboot is disabled.
正在解压 hailort-pcie-driver (4.18.0) ...
正在设置 hailort-pcie-driver (4.18.0) ...

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

build-essential/mantic,now 12.10ubuntu1 amd64 [已安装，自动]
Do you wish to use DKMS? [Y/n]:

Please reboot your computer for the installation to take effect.
```

安装完成后需要重启设备

### 检查设备和驱动

- 检查 PCIE 设备

使用 lspci 检查设备是否识别

```bash
lspci | grep Hailo
```

返回 Hailo 设备信息，说明识别正常

```bash
04:00.0 Co-processor: Hailo Technologies Ltd. Hailo-8 AI Processor (rev 01)
```

- 检查驱动 

检查驱动是否正常加载

```bash
lsmod | grep hailo_pci
```

```bash
hailo_pci              90112  0
```

- 检查驱动加载日志

```bash
dmesg | grep hailo
```

```bash
[   67.014969] hailo_pci: loading out-of-tree module taints kernel.
[   67.015023] hailo_pci: module verification failed: signature and/or required key missing - tainting kernel
[   67.016534] hailo: Init module. driver version 4.18.0
[   67.017366] hailo 0000:04:00.0: Probing on: 1e60:2864...
[   67.017369] hailo 0000:04:00.0: Probing: Allocate memory for device extension, 11632
[   67.017390] hailo 0000:04:00.0: enabling device (0000 -> 0002)
[   67.017917] hailo 0000:04:00.0: Probing: Device enabled
[   67.017944] hailo 0000:04:00.0: Probing: mapped bar 0 - 0000000021c328c7 16384
[   67.017950] hailo 0000:04:00.0: Probing: mapped bar 2 - 0000000073c01cdb 4096
[   67.017956] hailo 0000:04:00.0: Probing: mapped bar 4 - 00000000b456be2c 16384
[   67.017964] hailo 0000:04:00.0: Probing: Setting max_desc_page_size to 4096, (page_size=4096)
[   67.017995] hailo 0000:04:00.0: Probing: Enabled 64 bit dma
[   67.017997] hailo 0000:04:00.0: Probing: Using specialized dma_ops=iommu_dma_ops
[   67.018000] hailo 0000:04:00.0: Probing: Using userspace allocated vdma buffers
[   67.018008] hailo 0000:04:00.0: Disabling ASPM L0s
[   67.018011] hailo 0000:04:00.0: Successfully disabled ASPM L0s
[   67.170741] hailo 0000:04:00.0: Firmware was loaded successfully
[   67.188598] hailo 0000:04:00.0: Probing: Added board 1e60-2864, /dev/hailo0
```

以上信息说明设备和驱动正常识别和加载

## 安装 HailoRT

HialoRT 是 Hailo 的运行时库 (Runtime Library)，基于 C/C++ API，用于控制和与 Hailo 设备之间的数据传输

### 安装 HailoRT

- 下载 HailoRT 

和下载驱动一样，从 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 下载 'HailoRT – Ubuntu package (deb) for amd64'

![homelab-tpu-hailo-software-download-page.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-page.png)

- 安装 HailoRT

通过 dpkg 安装 HailoRT

```bash
sudo dpkg --install hailort_4.18.0_amd64.deb
```

```bash
正在选中未选择的软件包 hailort。
(正在读取数据库 ... 系统当前共安装有 187563 个文件和目录。)
准备解压 hailort_4.18.0_amd64.deb  ...
正在解压 hailort (4.18.0) ...
正在设置 hailort (4.18.0) ...
Do you wish to activate hailort service? (required for most pyHailoRT use cases) [y/N]:
Starting hailort.service
Created symlink /etc/systemd/system/multi-user.target.wants/hailort.service → /lib/systemd/system/hailort.service.
```

### 检查 HailoRT 

- hailort 命令行工具

安装完成后，会在系统中安装 [hailortcli tool](https://hailo.ai/developer-zone/documentation/hailort-v4-18-0/?sp_referrer=cli%2Fcli.html) 命令行应用，用于控制Hailo设备、在设备上运行推理以及收集推理统计数据和设备事件

```bash
hailortcli --help 
```

```bash
HailoRT CLI
Usage: hailortcli [OPTIONS] SUBCOMMAND

Options:
  -h,--help                   Print this help message and exit
  -v,--version                Display program version information and exit


Subcommands:
  run                         Run a compiled network
  run2                        Run networks
  scan                        Shows all available devices
  benchmark                   Measure basic performance on compiled network
  measure-power               Measures power consumption
  sensor-config               Config sensor attached to the Hailo chip
  fw-config                   User firmware configuration tool
  fw-logger                   Download fw logs to a file
  fw-update                   Firmware update tool (only for flash based devices)
  ssb-update                  Second stage boot update command (only for flash based devices)
  monitor                     Monitor of networks - Presents information about the running networks. To enable monitor, set in the application process the environment variable 'HAILO_MONITOR' to 1.
  udp-rate-limiter            Limit the UDP rate
  parse-hef                   Parse HEF to get information about its components
  fw-control                  Useful firmware control operations
```

- 扫描设备

使用 scan 命令查找当前支持的设备

```bash
hailortcli scan
```

会返回设备的接口信息

```bash
Hailo Devices:
[-] Device: 0000:04:00.0
```

- 获取设备信息

```bash
hailortcli fw-control identify
```

会返回设备的类型、名称等信息

```bash
Executing on device: 0000:04:00.0
Identifying board
Control Protocol Version: 2
Firmware Version: 4.18.0 (release,app,extended context switch buffer)
Logger Version: 0
Board Name: Hailo-8
Device Architecture: HAILO8L
Serial Number: HLDDLBB242602137
Part Number: HM21LB1C2LAE
Product Name: HAILO-8L AI ACC M.2 B+M KEY MODULE EXT TMP
```

## 安装 python 运行时环境

hailort 是用于向 Hailo-8/8L 设备加载模型以及发送和接收数据的 Python API

### 安装

- 下载 Wheel 文件

同样在 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 下载名为 'HailoRT – Python package (whl) for Python 3.10, x86_64' 的 Wheel 文件

![homelab-tpu-hailo-software-download-page.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-page.png)

- 创建虚拟环境

为了不影响其他服务，使用 anaconda 创建独立的虚拟环境并激活（anaconda 的安装请参考 [Installation](https://docs.anaconda.com/anaconda/install/)）

```bash
conda create -n hailo python=3.10 
```

```bash
conda activate hailo
```

- 安装 hailort 

```bash
pip install ./hailort-4.18.0-cp310-cp310-linux_x86_64.whl
```

```bash
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
Processing ./hailort-4.18.0-cp310-cp310-linux_x86_64.whl
Requirement already satisfied: argcomplete in /root/anaconda3/envs/hailo/lib/python3.10/site-packages (from hailort==4.18.0) (3.5.0)
Collecting contextlib2 (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/76/56/6d6872f79d14c0cb02f1646cbb4592eef935857c0951a105874b7b62a0c3/contextlib2-21.6.0-py2.py3-none-any.whl (13 kB)
Collecting future (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/da/71/ae30dadffc90b9006d77af76b393cb9dfbfc9629f339fc1574a1c52e6806/future-1.0.0-py3-none-any.whl (491 kB)
Collecting netaddr (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/12/cc/f4fe2c7ce68b92cbf5b2d379ca366e1edae38cccaad00f69f529b460c3ef/netaddr-1.3.0-py3-none-any.whl (2.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.3/2.3 MB 21.3 MB/s eta 0:00:00
Collecting netifaces (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/a6/91/86a6eac449ddfae239e93ffc1918cf33fd9bab35c04d1e963b311e347a73/netifaces-0.11.0.tar.gz (30 kB)
  Preparing metadata (setup.py) ... done
Collecting numpy==1.23.3 (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/c7/31/0298a8f62a8c82b8c542f78f3761e67cb8bf0450b3e61bbe66c5c54c1a81/numpy-1.23.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.1/17.1 MB 68.6 MB/s eta 0:00:00
Collecting verboselogs (from hailort==4.18.0)
  Downloading https://pypi.tuna.tsinghua.edu.cn/packages/b8/9d/c5c3cb0093642042fd604b53928ac65e7650fdc5a8a97814288e29beab84/verboselogs-1.7-py2.py3-none-any.whl (11 kB)
Building wheels for collected packages: netifaces
  Building wheel for netifaces (setup.py) ... done
  Created wheel for netifaces: filename=netifaces-0.11.0-cp310-cp310-linux_x86_64.whl size=14503 sha256=ecf67c60820415fd4ce4c22881dc5f4cf4028a72fb174c0a6eaef541161b91e0
  Stored in directory: /root/.cache/pip/wheels/4d/17/5b/ee74d1589e153ace1f92c660912b8fbadf855ee73acafbb038
Successfully built netifaces
Installing collected packages: verboselogs, netifaces, numpy, netaddr, future, contextlib2, hailort
Successfully installed contextlib2-21.6.0 future-1.0.0 hailort-4.18.0 netaddr-1.3.0 netifaces-0.11.0 numpy-1.23.3 verboselogs-1.7
```

### 检查 python 运行时环境

在命令行启动 python 运行代码进行检查

- 获取设备信息

```python
from hailo_platform import Device

dev = Device()
info = dev.control.get_extended_device_information()
print(info)
```

会返回设备的信息

```bash
Neural Network Core Clock Rate: 400.0MHz
Device supported features:
Ethernet: Disabled
MIPI: Disabled
PCIE: Enabled
Current Monitoring: Disabled
MDIO: Disabled
Boot source: PCIE
LCS: 3
SoC ID: ba9246dda6cf3517451947603e2c891fa8cdf372b4afdd45cf7c44d1e765068b
ULT ID: 0060c1c336506950fb7ac071
PM Values: 022e010000028c010000020d020000c389f741291cf54101
```

- 获取设备温度

```python
from hailo_platform import Device

dev = Device()
temperature = dev.control.get_chip_temperature()

print('sample_count: ' + str(temperature.sample_count))
print('ts0_temperature: ' + str(temperature.ts0_temperature))
print('ts1_temperature: ' + str(temperature.ts1_temperature))
```

```bash
sample_count: 52028
ts0_temperature: 41.21126937866211
ts1_temperature: 41.0089225769043
```

## 参考文档

- [Hailo人工智能软件套件](https://hailo.ai/zh-hans/products/hailo-software/hailo-ai-software-suite/#sw-hailort)
- [Hailo-8L 入门级AI加速器](https://hailo.ai/zh-hans/products/ai-accelerators/hailo-8l-ai-accelerator-for-ai-light-applications/#hailo8l-features)
- [Hailo-8 AI处理器](https://hailo.ai/zh-hans/products/ai-accelerators/hailo-8-ai-accelerator/)
- [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 
- [Installation](https://hailo.ai/developer-zone/documentation/hailort-v4-18-0/?sp_referrer=install/install.html)
- [Hacker’s guide to the Raspberry Pi AI kit on Ubuntu](https://ubuntu.com/blog/hackers-guide-to-the-raspberry-pi-ai-kit-on-ubuntu)
- [Hailo-8 Edge AI Accelerator Deployment Guide](https://tlab.hongo.wide.ad.jp/2024/03/04/hailo-8-edge-ai-accelerator-deployment-guide/)