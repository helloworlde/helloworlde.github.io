---
title: "Windows 使用 Yuzu 模拟 Nintendo Switch"
type: post
date: 2022-11-20T21:51:48+08:00
tags:
  - Games
categories:
  - Games
series:
  - Games
featured: true
---


[yuzu](https://yuzu-emu.org/) 是一款开源的 Ninetendo Swithc 模拟器，支持在 Linux 或者 Windows 平台运行，能够模拟 Switch 平台的大部分游戏

这里使用 Windows 平台进行安装，测试后发现 yuzu 能够较好的体验 Switch 的游戏，对于性能较好的机器，可以流畅运行游戏，并且没有 Switch 切换场景或者读取游戏时长时间的加载等待；对于没有 Switch 的可以作为尝鲜体验的工具，不过实际游戏效果体验不如 Switch 好

## 安装 yuzu 模拟器

进入 yuzu 的[下载](https://yuzu-emu.org/downloads/)页面，发现要求先安装 [Microsoft Visual C++](https://aka.ms/vs/17/release/vc_redist.x64.exe)，没有下载选项；只有当安装完 Microsoft Visual C++ 后，才会出现下载按钮

![nintendo-switch-yuzu-download-page-2.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-download-page-2.png)

下载后安装

![nintendo-switch-yuzu-install.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-install.png)

## 配置密钥

安装完成后进入，会发现提示密钥缺失；需要使用 Switch 设备的密钥，这些key 是用来解密 XCI 或者 NCA 格式的游戏文件的；

![nintendo-switch-yuzu-miss-keys.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-miss-keys.png)

如果有 Switch ，可以参考 [Dumping Decryption Keys from a Switch Console](https://yuzu-emu.org/wiki/dumping-decryption-keys-from-a-switch-console/) 进行导出；

如果没有 Switch，可以使用 [https://github.com/MostlyWhat/prod.keys/blob/main/prod.keys](https://raw.githubusercontent.com/MostlyWhat/prod.keys/main/prod.keys)

在 yuzu 模拟器菜单中，选择文件-打开 yuzu 文件夹，将下载到的文件保存到 keys 目录下，然后关闭并重新打开 yuzu 模拟器；再次打开后没有提示缺失密钥，说明密钥已经生效

## 导入游戏

- 下载游戏

yuzu 支持大部分的游戏，模拟器需要 XCI 或者 NCA 格式的游戏文件，可以从 [Game Compatibility List
](https://yuzu-emu.org/game/) 检测是否支持；如何从 Switch 中导出游戏文件参考 [Dumping Cartridge Games](https://yuzu-emu.org/help/quickstart/#dumping-cartridge-games)

如果没有 Switch，可以从其他平台搜索游戏的 XCI 或者 NCA 格式的文件；如 [https://nsw2u.in/](https://nsw2u.in/) 或者 [https://www.ziperto.com/](https://www.ziperto.com/nintendo/nintendo-switch-xci/) 下载（建议使用迅雷或其他下载工具下载）

- 导入游戏

当下载完成后在 yuzu 主页将游戏文件导入；即可开始体验游戏

![nintendo-switch-yuzu-add-game.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-add-game.png)

## 测试

使用《塞尔达传说-荒野之息》测试；

![nintendo-switch-yuzu-game-zelda-test2.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-game-zelda-test2.png)

通过 Macbook Pro 在没有安装独立显卡的 NUC9 i5 版本上以远程桌面的方式测试，发现运行卡顿，fps 大约在10-20之间，延迟大约 60-100ms；体验不佳；
配置：

- CPU：Intel i5-9300H，占用 40% 左右
- 显卡：Intel UHD 630 核显，占用 75% 左右
- 内存：DDR4 16G 2666Mhz，占用 3300M 左右

![nintendo-switch-yuzu-resource-usage.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-resource-usage.png)

通过 Macbook Pro 在另一台性能较好的台式机上通过远程桌面方式测试，能够稳定运行在 30帧，延迟在 30ms 左右，相对体验较好

- CPU：intel i9-12900K，占用 16% 左右
- 显卡：Nvdia 3070Ti，占用 38% 左右
- 内存：DDR4 32G 3200Mhz，占用 2600M 左右

![nintendo-switch-yuzu-resource-usage-2.png](https://img.hellowood.dev/picture/nintendo-switch-yuzu-resource-usage-2.png)
