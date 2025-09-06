---
title: "使用阿尔卡特猫棒替换北京移动 GPON 光猫"
type: post
date: 2023-11-27T18:08:46+08:00
lastmod: 2024-09-16
tags:
  - HomeLab
  - Network
featured: true
---

最近移动送了条免费宽带，刚好联通宽带到期了，可以无缝衔接上；之前使用的是 ODI 猫棒+兮克的 SKS3200M-8GPY1XF 交换机，因此想继续使用 ODI 猫棒，但是一番尝试后始终无法成功拨号，于是改成了使用阿尔卡特猫棒

阿尔卡特猫棒型号为 G-010S-P，版本为 6BA1896SPE2C05

![homelab-network-gpon-pon-stick-setup-status.png](https://img.hellowood.dev/picture/homelab-network-gpon-pon-stick-setup-status.png)

## 宽带配置

- 改为桥接模式

首先要将宽带改为桥接模式，在安装时直接让运维小哥改了；如果没有修改可以联系宽带帮忙修改

- 获取光猫的超级管理员密码

北京移动的超级管理员用户名是 `CMCCAdmin`，密码是 `aDm8H%MdA`；但是我尝试登陆时提示失败，然后联系运维小哥，使用光猫的 SN 和宽带账号授权之后可以正常登录了

光猫信息如下：

- 产品名称：吉比特无源光纤接入用户端设备（GPON ONU）
- 产品类型：中国移动智能家庭网关 类型11
- 产品型号：SK-D747
- 电源：12V---1.5A
- CMIIT ID: 2022XXXXXX
- 设备标识：XXXXXX-光猫 SN
- MAC: XXXXXXXXXXX
- SN: 光猫 SN

## 获取认证信息

北京移动的认证使用的是光猫的 SN + PLOAM 密码

- SN

光猫 SN 在光猫背面即可看到，也可以登录后在设备信息中查看

- PLOAM 密码

PLOAM 密码的路径为网络-远程管理-认证，

![homelab-network-gpon-model-info-ploam-password.png](https://img.hellowood.dev/picture/homelab-network-gpon-model-info-ploam-password.png)

- VLAN ID

北京移动的 VLAN ID 为 10

## 配置猫棒

### 配置

猫棒启动后，进入管理后台，这款猫棒默认的地址是 [http://192.168.1.10](http://192.168.1.10)，默认用户名 `root`，密码 `password`

登录后，选择 GPON-互操作兼容配置，配置上面获取到的认证信息

- GPON SN: 光猫的 SN
- Ploam password: 光猫获取到的认证密码
- 默认PVID: VLAN ID `10`

配置后，点击应用配置

![homelab-network-gpon-pon-stick-setup-auth-info.png](https://img.hellowood.dev/picture/homelab-network-gpon-pon-stick-setup-auth-info.png)

### 检查状态

可以在 GPON-光模块信息中查看当前的状态，注册状态/信号状态为 `5 / true`说明认证成功，此时可以在路由器配置 PPPoE 拨号上网了

![homelab-network-gpon-pon-stick-setup-auth-success.png](https://img.hellowood.dev/picture/homelab-network-gpon-pon-stick-setup-auth-success.png)
