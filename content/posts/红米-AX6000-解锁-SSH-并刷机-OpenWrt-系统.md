---
date: 2025-04-20
# description: ""
# image: ""
lastmod: 2025-04-20
showTableOfContents: false
title: "红米 AX6000 解锁 SSH 并刷机 OpenWrt 系统"
type: "post"
tags:
  - MiWiFi
  - Router
  - HomeLab
  - OpenWrt
featured: true
---

红米 AX6000 是 WiFi6 早期阶段性能极强并且有性价比的路由器，缺点是不支持 2.5G网口；在使用两年后刷为 OpenWrt 用于安装 OpenClash 等软件

## 启用 telnet 并解锁 SSH

刷机需要登录到路由器操作，因此需要先启用 telnet 并解锁 SSH；解锁过程比较简单，直接访问对应的地址就可以

### 确认固件版本

登录路由器后台，需要确认固件版本是否是 1.0.48、1.0.60 或者 1.0.67，只有这三个版本支持；如果不是这三个版本，需要下载其中某个版本刷入；最新的固件版本是 1.0.67，并且这款路由器已经没有新版本更新了

固件地址可以参考: [https://openwrt.org/toh/xiaomi/redmi_ax6000#install_vulnerable_version](https://openwrt.org/toh/xiaomi/redmi_ax6000#install_vulnerable_version)

### 启用 telnet 

- 获取 stock

stock 是小米路由器访问的鉴权 token，每次登录后生成新的，登录后可以浏览器的地址栏 URL 中直接获取，比如：066801299c1f7845d1871e50c4a307df

- 开启开发/调试模式

将 `{token}` 替换为 URL获取的 stock，浏览器访问 URL: 

```bash
http://192.168.31.1/cgi-bin/luci/;stok={token}/api/misystem/set_sys_time?timezone=%20%27%20%3B%20echo%20pVoAAA%3D%3D%20%7C%20base64%20-d%20%7C%20mtd%20write%20-%20crash%20%3B%20
```


这个操作会将 `\xa5\x5a\x00\x00` 写入分区，用于开启开发/调试模式，返回 code 0 表示操作成功

```json
{
  "code": 0
}
```

然后访问重启路由器

```bash
http://192.168.31.1/cgi-bin/luci/;stok={token}/api/misystem/set_sys_time?timezone=%20%27%20%3b%20reboot%20%3b%20
```


- 修改 Bdata, 开启 telnet 

再次获取 stock, 访问以下 URL 开启 telnet/ssh/uart 访问，返回 0 表示成功

```bash
http://192.168.31.1/cgi-bin/luci/;stok={token}/api/misystem/set_sys_time?timezone=%20%27%20%3B%20bdata%20set%20telnet_en%3D1%20%3B%20bdata%20set%20ssh_en%3D1%20%3B%20bdata%20commit%20%3B%20
```

然后再次访问 URL 重启路由器

```bash
http://192.168.31.1/cgi-bin/luci/;stok={token}/api/misystem/set_sys_time?timezone=%20%27%20%3b%20reboot%20%3b%20
``` 

### 启用 ssh

- 通过 telnet 访问命令行

经过上述操作后，通过 telnet 即可进入路由器的命令行：

```bash
telnet 192.168.31.1
```

- 开启并固化 ssh

如果只需要刷为 OpenWrt，这一步不需要执行；如果不想刷机了，只想开启 ssh，可以通过设置启动脚本的方式自定开启 ssh 

```bash
echo -e 'admin\nadmin' | passwd root
nvram set ssh_en=1
nvram set telnet_en=1
nvram set uart_en=1
nvram set boot_wait=on
nvram commit
sed -i 's/channel=.*/channel="debug"/g' /etc/init.d/dropbear
/etc/init.d/dropbear restart
mkdir /data/auto_ssh
cd /data/auto_ssh
curl -O https://fastly.jsdelivr.net/gh/lemoeo/AX6S@main/auto_ssh.sh
chmod +x auto_ssh.sh
uci set firewall.auto_ssh=include
uci set firewall.auto_ssh.type='script'
uci set firewall.auto_ssh.path='/data/auto_ssh/auto_ssh.sh'
uci set firewall.auto_ssh.enabled='1'
uci commit firewall
uci set system.@system[0].timezone='CST-8'
uci set system.@system[0].webtimezone='CST-8'
uci set system.@system[0].timezoneindex='2.84'
uci commit
mtd erase crash
reboot
```

## 刷入 OpenWrt 

AX6000 有两种分区方式，stock 方式和 U-Boot 方式；U-Boot 方式会覆盖路由器的分区，存储空间会增加，但是无法恢复为官方的模式；如果想后续刷回小米的固件，建议使用 stock 方式

刷入 OpenWrt 需要先刷入中间固件，然后再刷入升级固件；

- 通过 ssh/telnet 登录路由器

```bash
telnet 192.168.31.1
```

- 确认固件类型

AX6000 有两种固件类型，通过 `/proc/cmdline` 可以获取

```bash
cat /proc/cmdline
console=ttyS0,115200n1 loglevel=8 firmware=1 uart_en=1
```

我的 firmware=1，如果是 firmware=0，参考 [redmi_ax6000#installing_openwrt_stock_layout](https://openwrt.org/toh/xiaomi/redmi_ax6000#installing_openwrt_stock_layout) 操作

```bash
nvram set boot_wait=on
nvram set uart_en=1
nvram set flag_boot_rootfs=0
nvram set flag_last_success=0
nvram set flag_boot_success=1
nvram set flag_try_sys1_failed=0
nvram set flag_try_sys2_failed=0
nvram commit
```

### 刷入过渡固件

- 下载固件

最新的固件地址可以从 [redmi_ax6000#installation](https://openwrt.org/toh/xiaomi/redmi_ax6000#installation) 的 `Firmware OpenWrt Install URL` 获取下载地址

```bash
curl -O https://downloads.openwrt.org/releases/24.10.0/targets/mediatek/filogic/openwrt-24.10.0-mediatek-filogic-xiaomi_redmi-router-ax6000-stock-initramfs-factory.ubi
```

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9600k  100 9600k    0     0  53023      0  0:03:05  0:03:05 --:--:-- 82171
```

- 刷入 OpenWrt 固件

```bash
ubiformat /dev/mtd8 -y -f /tmp/openwrt-24.10.0-mediatek-filogic-xiaomi_redmi-router-ax6000-stock-initramfs-factory.ubi
```

```bash
ubiformat: mtd8 (nand), size 31457280 bytes (30.0 MiB), 240 eraseblocks of 131072 bytes (128.0 KiB), min. I/O size 2048 bytes
libscan: scanning eraseblock 239 -- 100 % complete
ubiformat: 240 eraseblocks have valid erase counter, mean value is 0
ubiformat: flashing eraseblock 74 -- 100 % complete
ubiformat: formatting eraseblock 239 -- 100 % complete
```

然后执行 `reboot` 重启

- 配置从系统 0 启动

重启后会进入 OpenWrt initramfs 系统，地址由 `192.168.31.1` 变为 `192.168.1.1`；然后执行以下命令配置固定从系统 0 启动，即 OpenWrt 系统

```bash
fw_setenv boot_wait on
fw_setenv uart_en 1
fw_setenv flag_boot_rootfs 0
fw_setenv flag_last_success 1
fw_setenv flag_boot_success 1
fw_setenv flag_try_sys1_failed 8
fw_setenv flag_try_sys2_failed 8
fw_setenv mtdparts "nmbm0:1024k(bl2),256k(Nvram),256k(Bdata),2048k(factory),2048k(fip),256k(crash),256k(crash_log),30720k(ubi),30720k(ubi1),51200k(overlay)"
```

### 刷入升级固件

- 下载 OpenWrt 升级固件

```bash
wget https://downloads.openwrt.org/releases/24.10.0/targets/mediatek/filogic/openwrt-24.10.0-mediatek-filogic-xiaomi_redmi-router-ax6000-stock-squashfs-sysupgrade.bin
```

- 刷入升级固件

```bash
sysupgrade -n /tmp/openwrt-24.10.0-mediatek-filogic-xiaomi_redmi-router-ax6000-stock-squashfs-sysupgrade.bin
```

```bash
verifying sysupgrade tar file integrity
Sun Apr 20 07:51:18 UTC 2025 upgrade: Commencing upgrade. Closing all shell sessions.
```

完成后会自动重启，访问 192.168.1.1 即可进入 OpenWrt 

## 配置 WiFi 启用 160Mhz 频段

默认启用的 WiFi 是 80Mhz，如果要启用 160Mhz 频段，需要将模式改为 AX，信道改为 64，国家改为 US，即可启用，其他配置会启用失败

## 参考文档

- [红米AX6000拆机，最便宜的四核2.0GHz](https://www.acwifi.net/19676.html)
- [Xiaomi Redmi AX6000](https://openwrt.org/toh/xiaomi/redmi_ax6000)
- [Redmi AX6S 解锁 SSH、刷入 OpenWRT 教程](https://github.com/lemoeo/AX6S)