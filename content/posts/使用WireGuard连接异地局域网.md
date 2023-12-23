---
title: "使用WireGuard连接异地局域网"
date: 2023-09-24T17:56:49+08:00
tags:
    - HomeLab
    - WireGuard
categories: 
    - HomeLab
    - WireGuard   
featured: true
---

# 使用 WireGuard 连接异地局域网

最近使用 Frigate 做家庭监控，因为 Frigate 部署在自己的 HomeLab 服务器里，有几个监控在老家，需要跨地域访问；有以下几种方案：
1. 使用公网映射：将老家的监控映射到公网，但是在公网开放监控并不安全，另外还需要申请公网IP 
2. 使用 TailScale 组网：测试过程中发现 TailScale 需要从香港中转，延迟很高，视频经常断开；自己部署 DERP 服务端同样需要在公网开放多个端口，不安全并且比较麻烦
3. 使用 Cloudflare Tunnel 转发：使用 Tunnel 延迟也很高，并不稳定
4. 使用 WireGuard 组网：对端直接连接，延迟低，仅需要开放一个 UDP 端口，较安全

最终选择使用 WireGuard 组网方案，在老家放了一台树莓派4B，用于运行 WireGuard 进行流量转发；HomeLab 服务器部署了一台 LXC 容器运行 WireGuard，用于连接树莓派；开启了局域网转发后，本地的局域网设备可以和老家的局域网设备互相通信

> 注意：需要对端其中一方有可以直接访问的公网IP

关于 WireGuard 的介绍可以参考 [WireGuard](https://www.wireguard.com/) 

![homelab-wireguard-vpn-for-sub-network.svg](https://img.hellowood.dev/picture/homelab-wireguard-vpn-for-sub-network.svg)

## 安装配置 WireGuard 

### 安装 wireguard

因为 LXC 容器和树莓派都使用的是 Ubuntu 22.04 的系统，因此直接使用 apt 安装即可

```bash
apt update && apt install -y wireguard-tools
```

### 生成密钥对

详细操作参考 [Key Generation](https://www.wireguard.com/quickstart/#key-generation)

- 创建文件夹并修改权限

```bash
mkdir wireguard && cd wireguard
umask 077
```

`umask 077` 的作用是设置系统默认文件和文件夹的权限为只有创建用户拥有全部权限（读、写和执行）

- 创建 OpenWrt 密钥对

先创建私钥，然后使用私钥创建公钥

```bash
wg genkey > homelab_private_key
wg pubkey < homelab_private_key > homelab_public_key
```

- 创建预共享密钥

```bash
wg genpsk > pre_share_key
```

- 创建对端密钥对

```bash
wg genkey > rasp_private_key
wg pubkey < rasp_private_key > rasp_public_key
```

### 生成 WireGuard 配置文件

使用生成的密钥对修改配置文件，这里使用 `10.0.1.0/24` 网段作为 WireGuard 的通信网段

- HomeLab 节点的配置文件

HomeLab 的 IP 地址为`10.0.1.0`，提供用于连接的端口`12345`暴露在公网，配置文件保存在 `/etc/wireguard/wg0.conf`

```
[Interface]
Address = 10.0.1.0/24
ListenPort = 12345
PrivateKey = homelab_private_key的值
MTU = 1450

[Peer]
PublicKey = rasp_public_key的值
PresharedKey = pre_share_key的值
AllowedIPs = 10.0.1.1/32
```

- rasp 节点的配置文件

rasp 节点作为 HomeLab 的对端，IP地址为 `10.0.1.1`启动后连接 HomeLab 节点，配置文件保存在 `/etc/wireguard/wg0.conf`

```
[Interface]
Address = 10.0.1.1/32
PrivateKey = rasp_private_key的值
DNS = 223.5.5.5,1.1.1.1
MTU = 1450

[Peer]
PublicKey = homelab_public_key的值
PresharedKey = pre_share_key的值
AllowedIPs = 10.0.1.0/24
Endpoint = 公网IP:12345
PersistentKeepalive = 15
```

### 启动验证 

在 HomeLab 和 Rasp 节点先后使用 wireguard-tools 的命令  `wg-quick`启动 WireGuard 进行测试验证

- 启动 WireGuard

`wg-quick` 指定的接口为 `wg0`，名称需要与`/etc/wireguard/wg0.conf` 文件名一致；`wg-quick` 会自动查找`/ect/wireguard/`路径下与接口名称一样的配置文件；或者可以在启动命令中指定配置文件地址

```bash
wg-quick up wg0
```

- 检查连接状态

```bash
wg show
```

会返回 WireGuard 的连接状态，如果 HomeLab 节点能看到对端的 IP 端口，并且transfer received 有数据传输说明连接成功了，可以使用 ping 进行检测

```bash
interface: wg0
  public key: xxx=
  private key: (hidden)
  listening port: 53486

peer: xxx=
  preshared key: (hidden)
  endpoint: xxx.xxx.xxx.xxx:12345
  allowed ips: 10.0.1.0/24
  latest handshake: 1 minute, 19 seconds ago
  transfer: 535.98 KiB received, 1.07 KiB sent
  persistent keepalive: every 15 seconds
```

```bash
➜  ~ ping 10.0.1.0
PING 10.0.1.0 (10.0.1.0) 56(84) bytes of data.
64 bytes from 10.0.1.0: icmp_seq=1 ttl=64 time=43.0 ms
64 bytes from 10.0.1.0: icmp_seq=2 ttl=64 time=43.0 ms
^C
--- 10.0.1.0 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 42.979/42.997/43.016/0.018 ms
➜  ~ ping 10.0.1.1
PING 10.0.1.1 (10.0.1.1) 56(84) bytes of data.
64 bytes from 10.0.1.1: icmp_seq=1 ttl=64 time=0.175 ms
64 bytes from 10.0.1.1: icmp_seq=2 ttl=64 time=0.138 ms
^C
--- 10.0.1.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1015ms
rtt min/avg/max/mdev = 0.138/0.156/0.175/0.018 ms
```

## 配置局域网转发

需要在 HomeLab 和 Rasp 节点都开启配置转发，才能访问到对方的局域网设备

### 配置允许局域网数据转发

- 检测是否开启转发

`sysctl` 是一个用来在系统运作中查看及调整系统参数的工具，`-p` 用于读取配置文件中的参数值；没有返回信息说明没有开启转发

```bash
sysctl -p
```

- 开启转发

需要在 `/etc/sysctl.conf` 文件中开启数据转发

```bash
vi /etc/sysctl.conf
```

添加以下内容（如果没有 IPV6 可以只添加 IPV4的配置），保存后实时生效

```
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
```

这两个参数控制着Linux系统是否允许将接收到的IP数据包进行路由转发。当这个参数的值为1时，表示允许IP数据包转发，这通常用于将Linux系统配置成路由器或者网关，允许它将数据包从一个网络接口路由到另一个网络接口

- 检查转发配置

再次使用 `sysctl -p` 检查，配置已经生效，此时设备已经可以将数据转发局域网内的其他设备

```bash
sysctl -p
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

### 配置 WireGuard 允许转发

#### 添加 iptable 规则

在 `wg0.conf` 的 `[Interface]` 中添加 `PostUp`和 `PostDown` 配置，用于在 WireGuard 启动后允许设备进行转发，在 WrieGuard 关闭后删除规则

```
[Interface]
...
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

- PostUp
`iptables -A FORWARD -i %i -j ACCEPT`: 此命令添加一个规则，允许从接口`%i`（即wg0）进入的数据包通过防火墙的FORWARD链
`iptables -A FORWARD -o %i -j ACCEPT`: 此命令添加一个规则，允许从接口`%i`（即wg0）出去的数据包通过防火墙的FORWARD链
`iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE`: 此命令添加一个NAT（网络地址转换）规则，将从eth0出去的数据包的源地址修改为设备的地址，以便它们可以正确路由回来。这通常用于创建网络地址转换（NAT）以允许多台内部设备共享单个公共IP地址。

- PostDown
`iptables -D FORWARD -i %i -j ACCEPT`: 此命令删除允许从接口`%i`（即wg0）进入的数据包通过防火墙的FORWARD链的规则
`iptables -D FORWARD -o %i -j ACCEPT`: 此命令删除允许从接口`%i`（即wg0）出去的数据包通过防火墙的FORWARD链的规则
`iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE`: 此命令删除之前添加的NAT规则，将从eth0出去的数据包的源地址修改为设备的地址的规则

#### 添加允许访问的 IP 范围

除了配置转发规则外，还需要添加允许访问的 IP 地址范围，这样对应网段的数据才会通过 WireGuard 进行转发

- HomeLab

需要在 HomeLab 的配置文件的 `[Peer]` 的 `AllowedIPs`中，添加 Rasp 所在局域网的网段信息，即`192.168.31.0/24`

```
[Peer]
PublicKey = rasp_public_key的值
PresharedKey = pre_share_key的值
AllowedIPs = 10.0.1.1/32,192.168.31.0/24
```

- Rasp

需要在 Rasp 的配置文件的 `[Peer]` 的 `AllowedIPs`中，添加 HomeLab 所在局域网的网段信息，即`192.168.2.0/24`

```
[Peer]
PublicKey = homelab_public_key的值
PresharedKey = pre_share_key的值
AllowedIPs = 10.0.1.1/32,192.168.2.0/24
Endpoint = 公网IP:12345
PersistentKeepalive = 15
```

#### 重启 WireGuard 检测

这样，当重启 WireGuard 后，就可以在 HomeLab 或者 Rasp 访问到对方局域网的其他设备了

```bash
wg-quick down wg0
wg-quick up wg0
```

在 Rasp 上可以 ping 通对方路由的 IP 地址，说明连接成功

```bash
ping 192.168.2.1
PING 192.168.2.1 (192.168.2.1) 56(84) bytes of data.
64 bytes from 192.168.2.1: icmp_seq=1 ttl=63 time=43.5 ms
^C
--- 192.168.2.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 43.548/43.548/43.548/0.000 ms
```

## 配置静态路由规则

完成以上步骤后，HomeLab 的 LXC 容器和 Rasp 都可以访问到对方的局域网的设备，但是局域网内的其他设备还无法访问到对方局域网的设备，这是因为没有路由规则，所以需要手动配置静态路由规则

### 查看路由规则

在 HomeLab 的容器上检查路由规则，发现 Rasp 所在局域网的流量是由 wg0 接口转发的，但是在其他设备上并没有这个规则，因此其他设备需要知道路由转发规则后才可以访问

```bash
ip route
```

```bash
default via 192.168.2.1 dev eth0 proto static
10.0.1.0/24 dev wg0 proto kernel scope link src 10.0.1.0
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown
192.168.2.0/24 dev eth0 proto kernel scope link src 192.168.2.5
192.168.31.0/24 dev wg0 scope link
```

### OpenWrt 配置路由规则

如果主路由或者网关路由器是 OpenWrt，则可以直接配置静态路由规则

- 添加路由规则

在 `/etc/rc.local` 添加路由规则，在启动后自动执行命令添加路由规则

```bash
vi /etc/rc.local
```

```bash
route -n add -net 192.168.31.0 -netmask 255.255.255.0 192.168.2.5
```

这里将 `192.168.31.0/24` 网段的数据都转发给了 LXC 容器 `192.168.2.5` 处理；`192.168.2.5` 收到数据后会通过 WireGuard 转发给 Rasp，再由 Rasp 将数据转发给对应的设备

- 配置防火墙

修改`/etc/config/firewall` 防火墙策略，允许转发：

```bash
vi /etc/config/firewall
```

```
config defaults
        option syn_flood '0'
        option input 'ACCEPT'
        option output 'ACCEPT'
        # REJECT 改为 ACCEPT
        option forward 'ACCEPT'
        # 1 改为 0
        option drop_invalid '0'
        option disable_ipv6 '0'

config zone
        option name 'lan'
        option network 'lan'
        option input 'ACCEPT'
        option output 'ACCEPT'
        #REJECT 改为 ACCEPT        
        option forward 'ACCEPT'
```

### 其他设备配置规则

如果路由器不是 OpenWrt，或者不能添加静态路由规则，或者仅需要个别设备访问，可以在设备上直接添加路由规则：

- Linux 设备

```bash
ip route add 192.168.31.0/24 via 192.168.2.5
```

- MacOS 设备

```bash
sudo route -n add -net 192.168.31.0 -netmask 255.255.255.0 192.168.2.5
```

## 完整 WireGuard 配置

- HomeLab

```
[Interface]
Address = 10.0.1.0/24
ListenPort = 12345
PrivateKey = homelab_private_key
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = rasp_public_key
PresharedKey = pre_share_key
AllowedIPs = 10.0.1.1/32,192.168.31.0/24
```

- Rasp 

```
[Interface]
Address = 10.0.1.1/32
PrivateKey = rasp_private_key
DNS = 223.5.5.5,1.1.1.1
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE


[Peer]
PublicKey = homelab_public_key
PresharedKey = pre_share_key
AllowedIPs = 10.0.1.0/24,192.168.2.1/24
Endpoint = 公网IP:12345
PersistentKeepalive = 15
```
