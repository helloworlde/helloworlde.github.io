---
date: 2025-11-17
description: "解决 MicroTik RB5009 容器功能无法启用问题，通过修改 device-mode 路由模式配置实现 Speetest 容器部署。"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
# tags: ["",]
title: "MicroTik RB5009 使用容器部署 Speetest"
keywords:
  - "MicroTik RB5009"
  - "RouterOS container"
  - "device-mode"
  - "Speetest deployment"
  - "Mikrotik Docker"
  - "system/device-mode"
  - "advanced mode"
  - "container=yes"
slug: "microtik-rb5009-container-speetest"
aliases:
  - "/posts/microtik-rb5009-使用容器部署-speetest/"
type: "post"
featured: false
---

## 启用容器功能

## 修改路由模式

RB5009 的模式是 advanced 模式，默认是关闭容器功能的，需要手动启用，否则会提示 `failure: not allowed by device-mode`

```bash
system/device-mode/print
                 mode: advanced
     allowed-versions: 7.13+,6.49.8+
              flagged: no
     flagging-enabled: yes
            scheduler: yes
                socks: yes
                fetch: yes
                 pptp: yes
                 l2tp: yes
       bandwidth-test: yes
          traffic-gen: no
              sniffer: yes
                ipsec: yes
                romon: yes
                proxy: yes
              hotspot: yes
                  smb: yes
                email: yes
             zerotier: yes
            container: no
  install-any-version: no
           partitions: no
          routerboard: no
        attempt-count: 1
```

- 启用容器

在模式中启用容器，然后按下路由器的 reset 按钮，等待路由器重启后生效

```
system/device-mode/update container=yes
  update: turn off power or reboot by pressing reset or mode button in 4m57s to activate changes
-- [Q quit|D dump|C-z pause]

```

## 参考文档

- [Device-mode](https://help.mikrotik.com/docs/spaces/ROS/pages/93749258/Device-mode)
