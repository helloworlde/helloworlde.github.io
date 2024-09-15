---
title: "Linux Docker容器开启IPv6"
type: post
date: 2024-04-21T21:25:04+08:00
tags:
  - HomeLab
  - Docker
categories:
  - HomeLab
  - Docker
featured: true
---

# Linux Docker 容器开启 IPv6

局域网开启了 IPv6 后，发现 Docker 因为没有开启 IPv6 无法访问了，因此需要为 Docker 开启 IPv6，根据官方文档提示，IPv6 仅在运行于 Linux 主机上的 Docker 守护进程上受支持

Docker 支持只给特定的网络开启 IPv6，也支持给 bridge 网络开启 IPv6

## 只给特定的网络开启 IPv6

这种方式不会修改默认的网络配置，指定特定的网络生效

- 修改配置
  修改 `/etc/docker/daemon.json` 文件，开启 IPv6 网络

```json
{
  "experimental": true,
  "ip6tables": true
}
```

- 重启 docker

```bash
sudo systemctl restart docker
```

- 创建 IPv6 网络

创建名为 `homelab-v6` 的 IPv6 网络，并指定子网范围

```bash
docker network create --ipv6 --subnet 2001:0DB8::/112 homelab-v6
```

- 测试验证

启动一个 busybox 容器，ping 阿里巴巴的 IPv6 DNS 地址 `2400:3200::1`，发现可以正常访问，说明已经成功开启 IPv6

```bash
docker run --network=homelab-v6 --rm -it busybox ping -6 -c1 2400:3200::1
PING 2400:3200::1 (2400:3200::1): 56 data bytes
64 bytes from 2400:3200::1: seq=0 ttl=117 time=2040.345 ms

--- 2400:3200::1 ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 2040.345/2040.345/2040.345 ms
```

## 给 bridge 开启 IPv6

给 bridge 开启 IPv6 相当于默认给所有没有指定网络的容器都开启了 IPv6；此时需要在配置文件中指定 IPv6 子网范围

- 修改配置

修改 `/etc/docker/daemon.json` 文件，添加以下内容：

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "2001:db8:1::/64",
  "experimental": true,
  "ip6tables": true
}
```

- 重启 Docker

```bash
sudo systemctl restart docker
```

- 测试验证

```bash
docker run --network=bridge --rm -it busybox ping -6 -c1 2400:3200::1
PING 2400:3200::1 (2400:3200::1): 56 data bytes
64 bytes from 2400:3200::1: seq=0 ttl=117 time=7.906 ms

--- 2400:3200::1 ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 7.906/7.906/7.906 ms
```

## macvlan 网络开启 IPv6

macvlan 网络 IPv6 和给特定的网络开启 IPv6 一样，在创建网络的时候指定相应的 CIDR 和网关地址即可

- 创建网络

```bash
docker network create -d macvlan \
    --subnet=192.168.2.0/24 \
    --gateway=192.168.2.1 \
    --subnet=fd00::/80 \
    --gateway=fd00::1 \
    --ipv6 -o parent=eth0 homelab-macvlan
```

- 使用

```yaml
version: "3"

networks:
  homelab-macvlan:
    external:
      name: homelab-macvlan

services:
  coredns:
    image: alpine
    container_name: alpine
    command: ping -6 -c100 2400:3200::1

    networks:
      homelab-macvlan:
        ipv4_address: 192.168.2.249
        ipv6_address: fd00::2
```

- 测试

```bash
docker-compose up
Starting alpine ... done
Attaching to alpine
alpine     | PING 2400:3200::1 (2400:3200::1): 56 data bytes
alpine     | 64 bytes from 2400:3200::1: seq=4 ttl=119 time=6.293 ms
alpine     | 64 bytes from 2400:3200::1: seq=5 ttl=119 time=6.301 ms
```

## 参考文档

- [Enable IPv6 support](https://docs.docker.com/config/daemon/ipv6/)
