---
title: "使用 PowerCLI 的 Docker 容器自行构建 ESXi 镜像"
type: post
date: 2023-02-07T21:45:26+08:00
tags:
  - Esxi
  - HomeLab
categories:
  - Esxi
  - HomeLab
series:
  - Esxi
featured: true
---

# 使用 PowerCLI 的 Docker 容器自行构建 ESXi 镜像

参考 [N5105 构建 ESXi 镜像](https://helloworlde.github.io/2022/08/11/N5105-%E6%9E%84%E5%BB%BA-Esxi-%E9%95%9C%E5%83%8F/)，在使用 ESXi 7 时，基于 Windows 系统，使用 PowerCLI 为 ESXi 7 的镜像添加了 NVMe 和 Intel I225V 网卡的驱动；

虽然当时已经可以在 Linux 或者 MacOS 上使用 PowerShell，但是因为 PowerCLI 不支持 Core 版本的 PowerShell，会提示 `Exception: The VMware.ImageBuilder module is not currently supported on the Core edition of PowerShell`；导致只能使用 Windows 构建，对于没有 Windows 系统的用户非常不方便。

PowerCLI 新版本已经支持了 Core 版本的 PowerShell，因此可以通过在 Linux/MacOS/Docker 等平台直接构建 ESXi 镜像；

本次使用 PowerCLI 的 Docker 容器，为 ESXi 8 镜像添加 NVMe 和网卡驱动

## 1. 下载所需的镜像和驱动

### 1.1 申请 ESXi 授权

ESXi 需要先注册申请，等待人工审核通过后就可以下载免费版本；如果没有任何反馈，可以点击申请页下面的 [Contact us](https://www.vmware.com/support/us_support.html) 提工单给 VMWare；

可以在 [VMware vSphere Hypervisor (ESXi) 8.0.0](https://customerconnect.vmware.com/downloads/details?downloadGroup=ESXI800&productId=1345&rPId=99879) 页面申请 8.0 版本的下载；选择 Offline Bundle 的压缩文件

![homelab-esxi-build-image-esxi8-download.png](https://img.hellowood.dev/picture/homelab-esxi-build-image-esxi8-download.png)

### 1.2 下载 NVME 社区驱动

从 [Community NVMe Driver for ESXi](https://flings.vmware.com/community-nvme-driver-for-esxi) 下载 NVME 驱动
![homelab-esxi-build-image-nvme-driver.png](https://img.hellowood.dev/picture/homelab-esxi-build-image-nvme-driver.png)

### 1.3 下载网卡社区驱动

从 [Community Networking Driver for ESXi](https://flings.vmware.com/community-networking-driver-for-esxi) 下载网卡驱动，该驱动包含 Intel I225-V 网卡的驱动

![homelab-esxi-build-image-network-driver.png](https://img.hellowood.dev/picture/homelab-esxi-build-image-network-driver.png)

## 2. 启动 PowerCLI 容器并挂载镜像和驱动

下载完镜像和驱动后，最好放到单独的目录下，方便容器进行挂载；比如镜像和驱动都放在 `~/Downloads/ESXi`路径下

- 启动 PowerCLI 容器并挂载镜像和驱动

将镜像文件挂载到 `/data`目录下，并进入容器的 `bash`

```bash
docker run --name powercli \
   --rm -it \
   -v ~/Downloads/ESXi:/data/ \
   docker.io/vmware/powerclicore \
   bash
```

- 进入 PowerShell

```bash
pwsh
```

```powershell
PowerShell 7.2.7
Copyright (c) Microsoft Corporation.

https://aka.ms/powershell
Type 'help' to get help.

PS /data>
```

## 3. 将驱动添加到镜像文件中

### 3.1 将压缩文件添加到当前 PowerShell Session 中

- 添加 Esxi

```powershell
Add-EsxSoftwareDepot /data/VMware-ESXi-8.0-20513097-depot.zip
```

返回结果：

```powershell
Depot Url
---------
zip:/data/VMware-ESXi-8.0-20513097-depot.zip?index.xml
```

- 添加网卡驱动

```powershell
Add-EsxSoftwareDepot /data/Net-Community-Driver_1.2.7.0-1vmw.700.1.0.15843807_19480755.zip
```

返回结果：

```powershell
Depot Url
---------
zip:/data/Net-Community-Driver_1.2.7.0-1vmw.700.1.0.15843807_19480755.zip?index.xml
```

- 添加 NVME 驱动

```powershell
Add-EsxSoftwareDepot /data/nvme-community-driver_1.0.1.0-3vmw.700.1.0.15843807-component-18902434.zip
```

返回结果：

```powershell
Depot Url
---------
zip:/data/nvme-community-driver_1.0.1.0-3vmw.700.1.0.15843807-component-18902434.zip?index.xml
```

### 3.2 获取当前的镜像

```powershell
Get-EsxImageProfile
```

返回结果如下，其中 Name 在后续使用中需要用到

```powershell
Name                           Vendor          Last Modified   Acceptance Level
----                           ------          -------------   ----------------
ESXi-8.0.0-20513097-no-tools   VMware, Inc.    9/23/2022 6:59… PartnerSupported
ESXi-8.0.0-20513097-standard   VMware, Inc.    9/23/2022 6:59… PartnerSupported
```

### 3.3 复制新的镜像，并添加驱动

- 复制镜像

基于当前的 ESXi 镜像，复制新的镜像，指定名称和租户，便于后面区分

```powershell
New-EsxImageProfile -CloneProfile 'ESXi-8.0.0-20513097-standard'  -name 'ESXi-8.0.0-20513097-standard-nvme-net' -vendor 'hellowood'
```

返回结果如下：

```powershell
Name                           Vendor          Last Modified   Acceptance Level
----                           ------          -------------   ----------------
ESXi-8.0.0-20513097-standard-… hellowood       9/23/2022 6:59… PartnerSupported
```

- 添加网卡驱动

使用复制镜像时使用的名称 `ESXi-8.0.0-20513097-standard-nvme-net`，将网卡驱动 `net-community` 添加到镜像中

```powershell
Add-EsxSoftwarePackage -ImageProfile 'ESXi-8.0.0-20513097-standard-nvme-net' -SoftwarePackage 'net-community'
```

返回结果：

```powershell
Name                           Vendor          Last Modified   Acceptance Level
----                           ------          -------------   ----------------
ESXi-8.0.0-20513097-standard-… hellowood       2/6/2023 5:50:… PartnerSupported
```

- 添加 NVMe 驱动

使用复制镜像时使用的名称 `ESXi-8.0.0-20513097-standard-nvme-net`，将 NVMe 驱动 `nvme
-community` 添加到镜像中

```powershell
Add-EsxSoftwarePackage -ImageProfile 'ESXi-8.0.0-20513097-standard-nvme-net' -SoftwarePackage 'nvme-community'
```

返回结果：

```powershell
Name                           Vendor          Last Modified   Acceptance Level
----                           ------          -------------   ----------------
ESXi-8.0.0-20513097-standard-… hellowood       2/6/2023 5:50:… PartnerSupported
```

### 3.4 将镜像导出为 iso 格式

执行导出后，会在挂载的目录下生成 iso 格式的文件，用于制作启动盘；这样就可以进行安装了

```powershell
Export-EsxImageProfile -ImageProfile 'ESXi-8.0.0-20513097-standard-nvme-net' -ExportToIso -FilePath /data/ESXi-8.0.0-20513097-standard-nvme-net.iso
```

## 参考文档

- [N5105 构建 Esxi 镜像](https://helloworlde.github.io/2022/08/11/N5105-%E6%9E%84%E5%BB%BA-Esxi-%E9%95%9C%E5%83%8F/)
