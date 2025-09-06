---
title: "Ubuntu 22 安装 AMD 显卡驱动"
date: 2024-09-19T09:14:35+08:00
lastmod: 2025-09-06
tags:
  - Ubuntu
  - AMD
  - Driver
featured: true
type: post
---

在 Ubuntu 22 安装 AMD 的显卡驱动，用于视频解码、ffmpeg 等场景

1. 下载 amdgpu-install

访问 [Linux® Drivers for AMD Radeon™ and Radeon PRO™ Graphics](https://www.amd.com/en/support/download/linux-drivers.html#linux-for-radeon-pro)，找到 Ubuntu 对应的驱动安装软件；右击 Download 按钮复制下载地址，即可得到下载链接；然后使用 curl 或者 wget 在 Ubuntu 下载，如：

```bash
wget https://repo.radeon.com/amdgpu-install/6.1.3/ubuntu/focal/amdgpu-install_6.1.60103-1_all.deb
```

![homelab-ubuntu-22-install-amd-graphics-driver.png](https://img.hellowood.dev/picture/homelab-ubuntu-22-install-amd-graphics-driver.png)

2. 安装下载软件

使用 apt 安装刚才下载的软件

```bash
apt install ./amdgpu-install_6.1.60103-1_all.deb
```

3. 安装显卡驱动

使用 amdgpu-install 安装显卡驱动

```bash
amdgpu-install -y --usecase=graphics
```

## 参考文档

- [Radeon™ Software for Linux® Installation](https://amdgpu-install.readthedocs.io/en/latest/index.html)
