---
title: 使用 MacOS 制作 MacOS 的 ISO 镜像
type: post
date: 2022-11-20T21:51:48+08:00
lastmod: 2024-12-04
tags:
  - MacOS
featured: true
---

需要在虚拟机中使用 macOS，但是没有 ISO 镜像，可以使用 macOS 系统制作 ISO 镜像

## 在 APP Store 下载安装器

首先需要在 App Store 下载对应版本的系统安装器，在 App Store 只能搜索到当前或更新版本的安装器，如果想使用旧版本，可以通过 Google 或[在线的 App Store](https://www.apple.com/us/search/macOS?src=serp) 搜索对应版本并跳转到 App Store 进行下载；如 [macOS Monterey](https://apps.apple.com/us/app/macos-monterey/id1576738294?mt=12)

![homelab-macos-iso-search-in-app-store.png](https://img.hellowood.dev/picture/homelab-macos-iso-search-in-app-store.png)

![homelab-macos-iso-download-from-app-store.png](https://img.hellowood.dev/picture/homelab-macos-iso-download-from-app-store.png)

随后会跳转到软件更新中自动下载，下载完成后在应用里可以看到 "安装 macOS Monterey"

![homelab-macos-iso-downloading.png](https://img.hellowood.dev/picture/homelab-macos-iso-downloading.png)

## 制作 ISO 镜像

安装完成后，可以通过命令行制作 ISO 镜像

### 1 创建 dmg 镜像文件

通过 `hdiutil` 在 `/tmp` 目录下创建一个临时的 Monterey dmg 文件，文件大小要大于等于安装器的大小，并指定挂载的数据卷名称为 `Monterey`

```bash
hdiutil create -o /tmp/Monterey -size 14500m -volname Monterey -layout SPUD -fs HFS+J
```

将会提示创建 dmg 文件成功 ：

```bash
created: /tmp/Monterey.dmg
```

### 2 将 dmg 挂载为数据卷

```bash
hdiutil attach /tmp/Monterey.dmg -noverify -mountpoint /Volumes/Monterey
```

挂载到 disk2

```bash
/dev/disk2          	Apple_partition_scheme
/dev/disk2s1        	Apple_partition_map
/dev/disk2s2        	Apple_HFS                      	/Volumes/Monterey
```

### 3 使用安装器将系统写入到数据卷

```bash
sudo /Applications/Install\ macOS\ Monterey.app/Contents/Resources/createinstallmedia --volume /Volumes/Monterey --nointeraction
```

待写入完成，会提示已将镜像写入到数据卷，数据卷名称为 `Install macOS Monterey`

```bash
Erasing disk: 0%... 10%... 20%... 30%... 100%
Making disk bootable...
Copying to disk: 0%... 10%... 20%... 30%... 40%... 50%... 60%... 70%... 100%
Install media now available at "/Volumes/Install macOS Monterey"
```

### 4 取消挂载安装器

```bash
hdiutil detach /volumes/Install\ macOS\ Monterey
```

### 5 将 dmg 格式转换为 iso 格式

需要先将 dmg 格式的文件转换为 cdr 格式，然后重命名为 iso 格式，指定生成的文件路径为下载目录

```bash
hdiutil convert /tmp/Monterey.dmg -format UDTO -o ~/Downloads/Monterey.cdr
mv ~/Downloads/Monterey.cdr ~/Downloads/Monterey.iso
```

```bash
正在读取Driver Descriptor Map（DDM：0）…
正在读取Apple（Apple_partition_map：1）…
正在读取（Apple_Free：2）…
正在读取disk image（Apple_HFS：3）…

已耗时：37.448s
速度：387.2MB/秒
节省：0.0%
created: /Users/hehuimin/Downloads/Monterey.cdr
```

这样就创建好了 iso 格式的文件，可以直接用于制作启动镜像或者虚拟机
