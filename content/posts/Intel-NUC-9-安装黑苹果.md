---
title: Intel NUC 9 安装黑苹果
type: post
date: 2022-12-08T21:51:48+08:00
tags:
  - Hackintosh
  - NUC
  - MacOS
featured: true
---

- 为什么要用黑苹果

手里有两台 MacBook Pro，分别是 18年的 i9 16G版本和20年的 i7 16G版本，升级到 Ventura 版本后响应变慢，同时公司的监控和通讯软件占用了大量内存，出现了严重的卡顿，切换应用等待三四秒之后才能操作；因为 MBP 无法升级内存，并且新款的 Mac 性价比并不高，因此，想通过黑苹果组建一台可以升级内存的电脑；

黑苹果的中文教程有很多，但是不少都是引流到公众号或者QQ群，下载镜像或相关软件都需要收费；这些人利用信息差，将免费和开源的拿去收费，吃相实在难看

- NUC 9

[NUC 9](https://www.intel.cn/content/www/cn/zh/products/sku/190107/intel-nuc-9-extreme-kit-nuc9i9qnx/specifications.html?erpm_id=12169418_ts1669688200770) 是 Intel 在 2020 年第一季度推出的 ITX 主机，代号 Ghost Canyon（幽灵峡谷），因为与同期的 MBP 配置类似，可以安装黑苹果

恰巧 NUC 9 最近降价了，i5版本的价格在 2k 左右，i9版本4k左右；单独购买 i9 的计算卡大概2k，因此购买 i5版本，然后自己更换 i9版本的算力卡性价比更高；兼容的软硬件参考 [兼容硬件列表](https://compatibleproducts.intel.com/ProductDetails?EPMID=190107&erpm_id=12169418_ts1669688262169)

黑苹果兼容的显卡并不多，主要以 AMD 为主，参考[黑苹果免驱显卡大全2022年9月最新版 更新至RX 6900 XT](https://www.zp0719.com/hackintoshgpu)；并且 NUC9 只支持长度不超过 20cm 的显卡，因此，能够选购的显卡非常有限（如憾讯的 6600/6600XT 竞技版，华擎的 6600/6600XT 单风扇版等）

- 黑苹果安装流程

黑苹果的安装过程大致分为四步，首先刻录 macOS 移动磁盘，然后将机型适用的 EFI 写入到移动磁盘，修改 BIOS 设置，接着启动安装macOS，安装完成后将 EFI 写入到系统即可；这里基于 macOS 进行安装，NUC 9 是 i5版本，没有安装独立显卡

## 将 macOS 刻录到移动磁盘

### 1. 格式化并分区移动磁盘

首先将移动硬盘连接到电脑，打开磁盘工具；点击显示，选择显示所有设备；

![homelab-nuc-hackintosh-show-all-disk.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-show-all-disk.png)

然后选择移动磁盘这个设备，选择抹掉，名称可以是任意名称，如 macOS，后续会在刻录镜像的时候用到；格式选择 "Mac OS 扩展（日志式）"；方案选择 GUID 分区图；这样就会将移动磁盘分为两个分区，一个是 EFI分区，另一个是系统镜像分区
![homelab-nuc-hackintosh-format-disk.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-format-disk.png)

### 2. 下载 macOS

建议使用 Big Sur 或者 Monterey 版本，Venture 版本的蓝牙和无线无法使用

首先需要在 App Store 下载对应版本的系统安装器，在 App Store 只能搜索到当前或更新版本的安装器，如果想使用旧版本，可以通过 Google 或[在线的 App Store](https://www.apple.com/us/search/macOS?src=serp) 搜索对应版本并跳转到 App Store 进行下载；如 [macOS Monterey](https://apps.apple.com/us/app/macos-monterey/id1576738294?mt=12)

![homelab-macos-iso-search-in-app-store.png](https://img.hellowood.dev/picture/homelab-macos-iso-search-in-app-store.png)

![homelab-macos-iso-download-from-app-store.png](https://img.hellowood.dev/picture/homelab-macos-iso-download-from-app-store.png)

随后会跳转到软件更新中自动下载，下载完成后在应用里可以看到 "安装 macOS Monterey"

![homelab-macos-iso-downloading.png](https://img.hellowood.dev/picture/homelab-macos-iso-downloading.png)

### 3. 将 macOS 刻录到移动磁盘

下载完 macOS 安装器后，即可通过安装器将镜像刻录到移动磁盘；在命令行执行以下命令，Volume 即为刚才分区时命名的分区名称

```bash
sudo /Applications/Install\ macOS\ Monterey.app/Contents/Resources/createinstallmedia --volume /Volumes/macOS
```

等待执行完成即可

```bash
Password:
Ready to start.
To continue we need to erase the volume at /Volumes/macOS.
If you wish to continue type (Y) then press return: y
Erasing disk: 0%... 10%... 20%... 30%... 100%
Making disk bootable...
Copying to disk: 0%... 10%... 20%... 30%... 40%... 50%... 60%... 70%... 80%... 90%... 100%
Install media now available at "/Volumes/Install macOS Monterey"
```

## 将 NUC9 的 EFI 添加到移动硬盘

使用到的 EFI 是基于 [OpenCore](https://dortania.github.io/OpenCore-Install-Guide/) 创建的，OpenCore 是一个开源的引导加载程序；用于引导启动 macOS 并提供所需的驱动及配置文件

### 1. 挂载 EFI

可以基于 OpenCore 的配置文件，自行配置 EFI 的相关驱动和配置，但是会比较复杂，这里使用开源的已经配置好的 EFI，如 [liu976336402/NUC9-hackintosh](https://github.com/liu976336402/NUC9-hackintosh/releases)，从 GitHub 下载 Release 中对应显卡的压缩文件到本地（可以选择 UHD630 或者 6600XT）；或着使用关键字 "NUC9 hackintosh EFI" 进行搜索；

如果想自己从头开始制作，可以参考 OpenCore 官方文档的 [Adding The Base OpenCore Files](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/opencore-efi.html) 及之后的 [Gathering files](https://dortania.github.io/OpenCore-Install-Guide/ktext.html)，[Getting started with ACPI](https://dortania.github.io/Getting-Started-With-ACPI/)，[config.plist Setup](https://dortania.github.io/OpenCore-Install-Guide/config.plist/) 部分；或者参考中文文档 [国光的黑苹果安装教程：手把手教你配置 OpenCore](https://apple.sqlsec.com/3-%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C/3-1/)

macOS 默认不会挂载 EFI分区，所以需要先将 EFI 分区挂载到系统

- 查找分区

首先使用 `diskutil` 查找移动磁盘 EFI的分区

```bash
diskutil list
```

发现 `external` 的磁盘是 `/dev/disk2`，其 EFI 分区的 `IDENTIFIER` 是 `disk2s1`

```bash
/dev/disk0 (internal, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      GUID_partition_scheme                        *500.3 GB   disk0
   1:                        EFI EFI                     314.6 MB   disk0s1
   2:                 Apple_APFS Container disk1         500.0 GB   disk0s2

/dev/disk1 (synthesized):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      APFS Container Scheme -                      +500.0 GB   disk1
                                 Physical Store disk0s2
   1:                APFS Volume Macintosh HD            8.8 GB     disk1s1
   2:              APFS Snapshot com.apple.os.update-... 8.8 GB     disk1s1s1
   3:                APFS Volume Preboot                 1.8 GB     disk1s2
   4:                APFS Volume Recovery                1.1 GB     disk1s3
   5:                APFS Volume VM                      2.1 GB     disk1s4
   6:                APFS Volume Macintosh HD - 数据     456.5 GB   disk1s5

/dev/disk2 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      GUID_partition_scheme                        *64.0 GB    disk2
   1:                        EFI EFI                     209.7 MB   disk2s1
   2:                  Apple_HFS Install macOS Monterey  63.7 GB    disk2s2
```

- 挂载 EFI

创建一个 Volume 分区并将 EFI 挂载到这个分区

```bash
sudo mkdir /Volumes/efi
sudo mount -t msdos /dev/disk2s1 /Volumes/efi
```

挂载成功后打开 Finder，可以看到已经挂载的 EFI 分区

![homelab-nuc-hackintosh-mount-efi.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-mount-efi.png)

### 2. 添加 EFI

将下载的 EFI 文件夹添加到 EFI 分区中（注意是整个 EFI 文件夹添加到 EFI 分区）

![homelab-nuc-hackintosh-move-efi-to-efi.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-move-efi-to-efi.png)

至此，磁盘镜像的准备工作已经完成

## 配置 BIOS

在启动出现骷髅头的时候，按下 F2进入到 BIOS，建议先按 F9恢复为默认，然后再修改；

需要修改以下几项：

- Advanced-STORAGE-SATA Mode Selection: AHCI
- Boot-Secure Boot：Disabled
- Boot-Boot Priority-Fast Boot: 取消勾选
- Boot-Boot Priority-Boot USB Devices First: 勾选
- Boot-Boot Priority-USB: 勾选

配置完后按 F10 保存并退出，重启后即可开始安装；如果有其他系统或者启动项，建议全部禁用，仅保留移动磁盘，避免后续重启时自动选择错误

## 安装 macOS

启动后，会看到可选的启动项，选择 "Install macOS Monterey"；

进入后，先选择磁盘工具，修改磁盘配置，可以将磁盘分区或者整个磁盘作为 macOS 的系统盘（建议使用整个磁盘，安装前不要有其他的系统存在），然后格式化磁盘为 AFPS格式，完成后退出磁盘工具；选择安装 Monterey；

注意，磁盘工具无法找到未分区的部分，如果有安装 Windows，建议先使用 Windows 将未分区的部分设置为简单卷；然后在磁盘工具中先格式化为 ExFat 格式，然后再格式化为 AFPS 格式

接下来安装系统指引一步步安装即可，安装过程中可能会有多次重启；等待大约半小时即可安装完成

![homelab-nuc-hackintosh-monterey-info.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-monterey-info.png)

## 配置 EFI 启动项

安装完成后，安装 [OpenCore Configurator](https://macdownload.informer.com/opencore-configurator/) 软件，选择 Tools - Mount EFI
![homelab-nuc-hackintosh-mount-efi-by-configurator.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-mount-efi-by-configurator.png)

将移动磁盘和 macOS 系统的 EFI 分区都挂载到电脑

![homelab-nuc-hackintosh-mount-efi-partition.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-mount-efi-partition.png)

然后将移动磁盘中的 EFI 分区复制到 macOS 系统的 EFI 即可

![homelab-nuc-hackintosh-move-partition-files.png](https://img.hellowood.dev/picture/homelab-nuc-hackintosh-move-partition-files.png)

## 使用体验

安装 Monterey 版本后，基本功能都正常，Wi-Fi/蓝牙/Type C/USB/网卡/通用控制等都可以正常使用；但是 CPU 没有正确识别；只使用核显画面不流畅，安装不支持的华硕 6500XT 显卡后可以使用，但是变得非常卡顿（应该是驱动问题导致），更换为 6600 后表现正常；AirDrop 能够发现其他的设备，但是无法传输文件

安装了 Ventura 后，Wi-Fi/蓝牙无法使用

## 参考文档

- [OpenCore-Install-Guide](https://dortania.github.io/OpenCore-Install-Guide/)
- [Hackintool](https://github.com/benbaker76/Hackintool)
- [bemble/Hackintosh-NUC9I7QNX-OpenCore](https://github.com/bemble/Hackintosh-NUC9I7QNX-OpenCore)
- [liu976336402/NUC9-hackintosh](https://github.com/liu976336402/NUC9-hackintosh)
- [corpnewt/ProperTree](https://github.com/corpnewt/ProperTree)
- [corpnewt/MountEFI](https://github.com/corpnewt/MountEFI)
- [国光的黑苹果安装教程：手把手教你配置 OpenCore](https://apple.sqlsec.com/)
- [intel NUC9 完美黑苹果Big Sur 11.2保姆级教程](https://zhuanlan.zhihu.com/p/526991674)
