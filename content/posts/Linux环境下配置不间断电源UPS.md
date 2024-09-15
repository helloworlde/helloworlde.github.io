---
title: "Linux 环境下配置不间断电源 UPS"
type: post
date: 2023-10-04T15:22:56+08:00
tags:
  - HomeLab
  - UPS
series:
  - HomeLab
  - UPS
featured: true
---

UPS (Uninterruptible Power Supply)，是一种含有储能装置的不间断电源。主要用于给部分对电源稳定性要求较高的设备，提供不间断的电源

一般的 UPS 都支持通过 USB 连接到电脑或者 NAS 等设备上，Linux/Mac/Windows 均支持使用 UPS；

因为电路不稳定，存在偶尔断电的情况，因此希望通过 UPS 保护树莓派、路由器、光猫、硬盘录像机等设备；将 UPS 通过 USB 接口连接到树莓派，由树莓派控制其他设备在断电时关机

## 安装 NUT

[NUT](https://networkupstools.org/)(Network UPS Tools) 是一种开源软件工具，其主要功能特点是实时监控与管理不间断电源（UPS）设备，支持多种通信协议，自动执行操作以应对电力故障，适用于多平台，并允许集中管理多个UPS设备，以确保与这些设备连接的计算机和设备在电力问题发生时能够继续正常运行或安全关闭

NUT中的主要软件组件和功能：

- Driver（驱动程序）：NUT包括各种不同制造商的UPS设备的驱动程序，使NUT能够与多种型号的UPS设备通信。这些驱动程序负责与UPS设备建立连接，并获取有关电源状态、电池状态和其他参数的信息。
- upsd（UPS守护进程）：upsd是NUT的核心守护进程，负责与UPS设备通信，并将UPS状态信息提供给其他NUT组件和客户端。它可以通过网络协议（如SNMP、HTTP、XML-RPC等）向其他计算机提供UPS状态信息。
- upsmon（UPS监控守护进程）：upsmon监控守护进程用于监视UPS状态，并在检测到电力问题时执行操作。它可以配置为执行自定义脚本、关闭计算机或发送警报通知，以确保系统的连续性和数据完整性。
- upslog（UPS事件记录器）：upslog用于记录UPS事件和状态信息，以便后续分析和故障排除。它可以生成日志文件，其中包含UPS的运行历史和电力事件。
- nutclient（NUT客户端工具）：NUT提供了一些用于监控和管理UPS的命令行工具，例如upsc用于查询UPS状态，upscmd用于发送命令到UPS，以及upsrw用于修改UPS配置。

- 安装

```bash
apt update && apt install -y nut
```

## 通过 USB 连接 UPS

在将 UPS 通过 USB 连接到树莓派后，可以通过查看 USB 设备进行检查

- 检查 USB 连接

```bash
sudo lsusb
```

其中的 Device 003 就是 UPS，说明 USB 连接正常

```bash
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 002: ID 174c:55aa ASMedia Technology Inc. ASM1051E SATA 6Gb/s bridge, ASM1053E SATA 6Gb/s bridge, ASM1153 SATA 3Gb/s bridge, ASM1153E SATA 6Gb/s bridge
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 0463:ffff MGE UPS Systems UPS
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

- 通过 `nut-scanner` 检查 UPS 设备

```bash
nut-scanner -q
```

正确识别到连接的 UPS 设备，驱动为 `usbhid-ups`，产品为 `SANTAK TG-BOX`

```bash
Neon library not found. XML search disabled.
IPMI library not found. IPMI search disabled.
[nutdev1]
	driver = "usbhid-ups"
	port = "auto"
	vendorid = "0463"
	productid = "FFFF"
	product = "SANTAK TG-BOX"
	serial = "Blank"
	vendor = "EATON"
	bus = "001"
```

## 配置 UPS

###配置 UPS 驱动

驱动程序负责与UPS设备建立连接，并获取有关电源状态、电池状态和其他参数的信息

- 将 UPS 设备添加到 NUT

使用 `nut-scanner` 将连接的 UPS 信息追加到 `/etc/nut/ups.conf` 配置中，其中的 `nutdev1` 是设备的名称，可以自定义

```bash
sudo nut-scanner -q >> /etc/nut/ups.conf
```

- 启动 NUT

使用 `upsdrvctl` 命令启动 NUT

```bash
sudo upsdrvctl start
```

### 配置 UPS 守护进程

upsd 负责与UPS设备通信，并将UPS状态信息提供给其他NUT组件和客户端

- 启动 upsd

```bash
sudo upsd
```

### 查看 UPS 状态

使用 `upsc` 命令查看 UPS 设备的状态；其中的 `ups` 是 `/etc/nut/ups.conf` 中配置的名称

```bash
sudo upsc ups@localhost
```

该命令会返回 UPS 设备的所有信息

```bash
Init SSL without certificate database
battery.charge: 98
battery.charge.low: 20
battery.runtime: 2744
battery.type: PbAc
device.mfr: EATON
device.model: SANTAK TG-BOX 600
device.serial: Blank
...
```

也可以指定名称查看 UPS 状态

```bash
sudo upsc ups@localhost ups.status
```

```bash
Init SSL without certificate database
OL
```

## 配置关机策略

### 配置 upsd 用户

upsd 用户对应的配置文件是 `/etc/nut/upsd.users`，配置用户用于读取 UPS的信息；在以下配置中，用户名是 `upsmon`，密码是 `123456`，运行模式是 `master`，即该设备为主节点（如果有同时使用其他 UPS则可以是 `slave`）

```
[upsmon]
        password = "123456"
        upsmon master
```

- 重启 upsd

```bash
sudo upsd -c reload
```

### 配置关机策略

关机策略使用的是 upsmon，upsmon 监控守护进程用于监视UPS状态，并在检测到电力问题时执行操作，它可以配置为执行自定义脚本、关闭计算机或发送警报通知

- 配置关机策略

修改 `/etc/nut/upsmon.conf`，添加如下配置，使用的是刚才创建的用户信息，这样，当设备监听到 UPS 发出的 `LOWBATT` 命令后，就会执行关闭系统

```
MONITOR ups@localhost 1 monuser 123456 master
```

这个命令告诉NUT要监控名为 "ups" 的UPS设备，该设备位于本地主机上。监控用户 "monuser"，可以使用密码 "123456" 连接到NUT，并具有 "master" 角色的权限。这允许用户通过NUT连接来监视和管理UPS设备

- 启动 upsmon

```bash
sudo upsmon
```

## 执行自定义动作

NUT 通过 `upssched` 支持监听 UPS 事件并执行指定脚本，因此可以用于执行一些自定义的动作，如发送通知等

### 配置 upsmon

修改 `/etc/nut/upsmon.conf` 文件，添加如下配置

- 指定运行命令

该配置用于在发生事件时运行 `/sbin/upssched` 服务

```
NOTIFYCMD /sbin/upssched
```

- 配置触发条件

```
NOTIFYFLAG ONLINE SYSLOG+WALL+EXEC
NOTIFYFLAG ONBATT SYSLOG+WALL+EXEC
NOTIFYFLAG LOWBATT SYSLOG+WALL+EXEC
```

这里监听了 `ONLINE`, `ONBATT`, 和 `LOWBATT`三个事件，分别是电源供电、电池供电和低电量事件；`SYSLOG`声明记录事件日志到系统中，`WALL`声明通知所有在线用户，`EXEC` 声明需要执行命令

### 配置 upssched

配置好 upsmon 后，还需要配置 upssched 执行相关的命令，需要将以下内容添加到 `/etc/nut/upssched.conf` 中

- 配置 upsmon

```
CMDSCRIPT /usr/local/bin/upssched-script.sh

PIPEFN    /run/nut/upssched/upssched.pipe
LOCKFN    /run/nut/upssched/upssched.lock

AT ONBATT  * EXECUTE      battery_on         # 发送断电的消息
AT ONLINE  * EXECUTE      power_online       # 发送来电的消息
AT ONBATT  * START-TIMER  watch_battery 60   # 60 秒后执行监控电池状态
AT ONLINE  * CANCEL-TIMER watch_battery      # 取消 监控电池状态
AT LOWBATT * EXECUTE      low_battery		 # 低电量
```

`CMDSCRIPT` 指定了监听到事件后需要执行的脚本
`PIPEFN`和`LOCKFN`指定了监听事件的管道并加锁，避免被修改
`AT` 和 `EXECUTE` 指定了监听的事件并执行相关的脚本；当监听到 `ONBATT`, `ONLINE` 和 `LOWBATT` 时执行 `CMDSCRIPT`指定的脚本，并将 `battery_on`, `power_online` 和 `low_battery`作为参数
`AT` 和 `START-TIMER` 启动了一个计时器，在 60s 后执行
`AT` 和 `CANCEL-TIMER` 指定如果在启动计时器60s 内发生了 `ONLINE`事件，则取消计时器

- 配置 upssched-script.sh

```bash
#!/bin/bash
BARK_URL=${BARK_URL:-"https://api.day.app/xxxxxx"}

function send_message() {
    message="$1"
    echo "发送通知:${message}"
    curl -X "POST" "$BARK_URL" \
         -H 'Content-Type: application/json; charset=utf-8' \
         -d "{
              \"title\": \"UPS 状态发生变化\",
              \"body\": \"${message}\",
              \"group\": \"UPS\"
            }"
}

case $1 in
    battery_on)
        battery_charge=$(upsc ups@localhost battery.charge)
        send_message "UPS 电池已启用，目前电量: ${battery_charge}"
        ;;
    power_online)
        battery_charge=$(upsc ups@localhost battery.charge)
        send_message "UPS 已恢复供电，目前电量: ${battery_charge}"
        ;;
    watch_battery)
        battery_charge=$(upsc ups@localhost battery.charge)
        send_message "UPS 目前电量: ${battery_charge}"
        ;;
    low_battery)
        battery_charge=$(upsc ups@localhost battery.charge)
        send_message "UPS 低电量: ${battery_charge}，开始关机"
        ;;
    *)
        logger -t upssched-cmd "其他未知指令: $1"
        ;;
esac
```

这段脚本用于接收事件，并执行动作；这里通过 Bark 发送了通知

## 记录 UPS 日志

ups 支持通过 `upslog` 记录 UPS 日志

```bash
sudo upslog -l /var/log/ups.log -i 1 -s ups@localhost -f "%TIME @Y-@m-@d @H:@M:@S%, battery.charge:%VAR battery.charge%, input.voltage:%VAR input.voltage%, ups.load:%VAR ups.load%, ups.status:[%VAR ups.status%], ups.temperature:%VAR ups.temperature%, input.frequency:%VAR input.frequency%"
```

这段命令中，通过 `-l`指定了输出文件为 `/var/log/ups.log`，`-i 1` 表示1s输出一次，`-s ups@localhost`指定了 UPS 位置，`-f` 指定了日志输出格式

输出日志参考：

```bash
2023-10-06 19:58:38, battery.charge:78, input.voltage:NA, ups.load:8, ups.status:[OL], ups.temperature:NA, input.frequency:NA
```

## 配置 UPS 监控

NUT 支持通过 HTTP 接口对外提供 UPS 的信息，因此可以用于监控 UPS; [https://github.com/helloworlde/nut_exporter](https://github.com/helloworlde/nut_exporter) 提供了 Prometheus Exporter，可以使用 Prometheus 和 Grafana 对 UPS 进行监控

![homelab-ups-grafana-dashboard-3.png](https://img.hellowood.dev/picture/homelab-ups-grafana-dashboard-3.png)

![homelab-ups-grafana-dashboard-2.png](https://img.hellowood.dev/picture/homelab-ups-grafana-dashboard-2.png)

### 修改 NUT 运行模式

配置文件是 `/etc/nut/nut.conf`；将模式修改为 `netserver`的目的是允许通过局域网访问 UPS 的设备信息，用于其他设备监控、监听 UPS 的状态；如果不需要监听则不需要配置

```bash
MODE=netserver
```

### 配置 upsd

修改 upsd 对应的配置文件 `/etc/nut/upsd.conf`，添加监听的地址和端口；添加局域网 IP 是用于局域网内其他设备进行监控，否则可能会拒绝连接

```
LISTEN 127.0.0.1 3493
LISTEN ::1 3493
LISTEN 192.168.31.11 3493
```

- 重启 upsd

```bash
sudo upsd -c reload
```

### 配置 NUT Exporter

- 配置 `docker-compose.yaml`

```yaml
version: "3"

services:
  nut-exporter:
    image: hellowoodes/nut-exporter
    container_name: nut-exporter
    hostname: nut-exporter
    restart: unless-stopped
    command: --log.level=debug
    ports:
      - "9199:9199"
    environment:
      - NUT_EXPORTER_SERVER=${NUT_EXPORTER_SERVER}
      - NUT_EXPORTER_USERNAME=${NUT_EXPORTER_USERNAME}
      - NUT_EXPORTER_PASSWORD=${NUT_EXPORTER_PASSWORD}
      - NUT_EXPORTER_VARIABLES=${NUT_EXPORTER_VARIABLES}
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
```

- 配置 `.env`

Server 的地址即为树莓派局域网的IP地址，用户名和密码是 upsd 的用户和密码；`NUT_EXPORTER_VARIABLES`是需要抓取的监控指标类型，不同的设备可能指标不一样；可以通过 `upsc ups@localhost` 获取所有的指标名称进行替换

```
NUT_EXPORTER_SERVER=192.168.31.11
NUT_EXPORTER_USERNAME=monuser
NUT_EXPORTER_PASSWORD=123456
NUT_EXPORTER_VARIABLES=battery.charge,battery.charge.low,battery.runtime,battery.type,device.mfr,device.model,device.serial,device.type,driver.name,driver.parameter.pollfreq,driver.parameter.pollinterval,driver.parameter.port,driver.parameter.product,driver.parameter.productid,driver.parameter.serial,driver.parameter.synchronous,driver.parameter.vendor,driver.parameter.vendorid,driver.version,driver.version.data,driver.version.internal,input.transfer.high,input.transfer.low,outlet.1.desc,outlet.1.id,outlet.1.status,outlet.1.switchable,outlet.desc,outlet.id,outlet.switchable,output.frequency.nominal,output.voltage,output.voltage.nominal,ups.beeper.status,ups.delay.shutdown,ups.delay.start,ups.firmware,ups.load,ups.mfr,ups.model,ups.power.nominal,ups.productid,ups.serial,ups.status,ups.timer.shutdown,ups.timer.start,ups.type,ups.vendorid
```

- 配置 Prometheus

```yaml
- job_name: ups-exporter
  honor_timestamps: true
  scrape_interval: 15s
  scrape_timeout: 10s
  metrics_path: /ups_metrics
  scheme: http
  static_configs:
    - targets:
        - 192.168.31.11:9199
```

- 配置 Grafana 面板

导入 [https://github.com/helloworlde/nut_exporter/blob/master/dashboard/dashboard.json](https://github.com/helloworlde/nut_exporter/blob/master/dashboard/dashboard.json) 即可
