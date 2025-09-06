---
title: "Ubuntu 22 安装 Google Coral TPU NVME 驱动"
type: post
date: 2024-07-08T09:07:20+08:00
lastmod: 2024-09-16
tags:
  - Ubuntu
  - Coral
featured: true
---

最近折腾图像识别和视频对象检测，因为需要长期低功耗运行，所以购入了 Google Coral TPU

Google Coral TPU 是一款专为边缘应用设计的机器学习加速器，由 Google 设计和开发，它基于 TensorFlow Lite 模型，能够在低功耗的情况下提供快速的神经网络性能，适用于边缘设备，用于目标检测和图像分类(如开源 NVR Frigate)；可以使用 Yolo、MobikeNet 等模型

单个 Coral TPU 芯片有 4T OPS 的算力，每秒可以识别大概 100 帧的视频内容，非常适合低功耗、本地场景，可以有效保护隐私；虽然 Coral 从 2021年开始不再更新，但是在边缘场景下依然是非常合适的选择

Coral TPU 有多种型号，如开发板、USB 配件、M2、Mini PCIE等，这里使用的是 M.2 Accelerator B+M key 的版本。关于 Coral 不同类型的设备更多信息参考 [Products](https://coral.ai/products/)

![](https://lh3.googleusercontent.com/-R0H37d9aKorHo_VYWf8hCfukvbZolBaW2SHW1uDDn1G411r3MqemjxPZa9f44q8OwlfYIkGxSoj-GQbZGd2j7lxtyzSklIQVUWvo9r88mn8CzB-rcw=w2000-rw)

## 要求

- 系统：Linux、Windows
- 环境：python3.6-3.9

## 安装

### 安装 Coral TPU

- 安装 Coral TPU

将 Coral TPU 安装到 M.2 插槽

- 检查连接

等待启动后，检查 NVME 连接

```bash
lspci -nn | grep 089a
```

已经正确识别到了 Coral TPU

```bash
03:00.0 System peripheral [0880]: Global Unichip Corp. Coral Edge TPU [1ac1:089a]
```

### 安装驱动

需要安装 `gasket-dkms` 和 `libedgetpu1-std`；

`gasket-dkms` 是一个动态内核模块支持 (DKMS) 包，它包含了用于与 EdgeTPU 进行通信的驱动程序；`libedgetpu1-std` 是一个 C++ 库，提供了一个更高级别的接口，让应用能够使用 EdgeTPU 进行模型推理

#### 添加 Coral 软件源

```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
```

如果提示 "不支持 'i386' 体系结构，跳过配置文件 'main/binary-i386/Packages' 的获取", 则将 `deb https://packages.cloud.google.com/apt coral-edgetpu-stable main` 改为 `deb [arch=amd64] https://packages.cloud.google.com/apt coral-edgetpu-stable main`

#### 安装 libedgetpu1-std

```bash
apt install libedgetpu1-std
```

#### 安装 gasket-dkms

`gasket-dkms` 在 Ubuntu 22 中无法直接安装，因此需要手动编译安装

- 安装依赖

```bash
sudo apt update
sudo apt upgrade
sudo apt install dkms devscripts debhelper dh-dkms -y
```

- 下载源码

```bash
git clone https://github.com/google/gasket-driver.git
```

- 编译

使用 root 用户进行编译

```bash
sudo -i
cd gasket-driver; debuild -us -uc -tc -b; cd ..
```

会进入项目目录编译并在当前目录生成编译后的软件

```bash
dpkg-buildpackage -us -uc -ui -tc -b
dpkg-buildpackage: info: 源码包 gasket-dkms
dpkg-buildpackage: info: 源码版本 1.0-18
dpkg-buildpackage: info: source distribution unstable
dpkg-buildpackage: info: 源码修改者 Coral <coral-support@google.com>
 dpkg-source --before-build .
dpkg-buildpackage: info: 主机架构 amd64
...
```

- 检查软件信息

编译完成后，会在当前目录下生成 `gasket-dkms_版本_all.deb` 软件包及相关信息文件

```bash
ls -l gasket-dkms*
```

```bash
-rw-r--r-- 1 root root 49162  7月 14 19:07 gasket-dkms_1.0-18_all.deb
-rw-r--r-- 1 root root  1882  7月 14 19:07 gasket-dkms_1.0-18_amd64.build
-rw-r--r-- 1 root root  6700  7月 14 19:07 gasket-dkms_1.0-18_amd64.buildinfo
-rw-r--r-- 1 root root  1017  7月 14 19:07 gasket-dkms_1.0-18_amd64.changes
```

- 安装软件

安装刚才编译的 gasket-dkms

```bash
sudo dpkg -i gasket-dkms_1.0-18_all.deb
```

- 加载 apex 模块

加载 Coral 的驱动程序

```bash
sudo modprobe apex
```

### 添加用户权限

如果用户没有 root 权限，需要将该用户手动添加到 apex 用户组

```bash
sudo sh -c "echo 'SUBSYSTEM==\"apex\", MODE=\"0660\", GROUP=\"apex\"' >> /etc/udev/rules.d/65-apex.rules"
sudo groupadd apex
sudo adduser $USER apex
```

## 检查

- 检查内核模块

```bash
lsmod | grep apex
```

会输出 apex 模块的信息，apex 模块依赖 gasket 模块

```bash
apex                   28672  0
gasket                135168  1 apex
```

- 检查 PCIE 驱动

```bash
ls /dev/apex_0
```

设备存在说明 apex 模块成功加载了 Coral 设备

```bash
/dev/apex_0
```

## 参考文档

- [Install the PCIe driver and Edge TPU runtime](https://coral.ai/docs/m2/get-started/#2a-on-linux)
- [Building gasket-dkms broken on linux kernel 6.5.0 (Ubuntu 23.10)](https://github.com/google-coral/edgetpu/issues/808)

## 安装遇到的问题

- 安装 gasket-dkms 提示错误，需要手动编译源码安装

```bash
apt install gasket-dkms
```

```bash
正在读取软件包列表... 完成
正在分析软件包的依赖关系树... 完成
正在读取状态信息... 完成
下列【新】软件包将被安装：
  gasket-dkms
升级了 0 个软件包，新安装了 1 个软件包，要卸载 0 个软件包，有 0 个软件包未被升级。
需要下载 0 B/48.0 kB 的归档。
解压缩后会消耗 256 kB 的额外空间。
正在选中未选择的软件包 gasket-dkms。
(正在读取数据库 ... 系统当前共安装有 349763 个文件和目录。)
准备解压 .../gasket-dkms_1.0-18_all.deb  ...
正在解压 gasket-dkms (1.0-18) ...
正在设置 gasket-dkms (1.0-18) ...
Loading new gasket-1.0 DKMS files...
Building for 6.5.0-41-generic
Building initial module for 6.5.0-41-generic
ERROR: Cannot create report: [Errno 17] File exists: '/var/crash/gasket-dkms.0.crash'
Error! Bad return status for module build on kernel: 6.5.0-41-generic (x86_64)
Consult /var/lib/dkms/gasket/1.0/build/make.log for more information.
dpkg: 处理软件包 gasket-dkms (--configure)时出错：
 已安装 gasket-dkms 软件包 post-installation 脚本 子进程返回错误状态 10
在处理时有错误发生：
 gasket-dkms
```

- 编译 gasket-dkms 提示 unstable

表示 gasket-dkms 软件包的 Changes 文件中使用了 "unstable" 作为发行版，而 Lintian 认为 "unstable" 不是一个有效的发行版名称，这是因为在 ubuntu 上编译 debian 的软件导致的；这个错误提示并不影响使用，忽略即可

```bash
....
 dpkg-source --after-build .
dpkg-buildpackage: info: binary-only upload (no source included)
Now running lintian gasket-dkms_1.0-18_amd64.changes ...
running with root privileges is not recommended!
E: gasket-dkms changes: bad-distribution-in-changes-file unstable
Finished running lintian.
```
