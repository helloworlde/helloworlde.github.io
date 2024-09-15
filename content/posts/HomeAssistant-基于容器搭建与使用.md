---
title: "HomeAssistant 基于容器搭建与使用"
type: post
date: 2022-11-13T21:51:48+08:00
tags:
  - HomeAssistant
  - HomeLab
categories:
  - HomeAssistant
  - HomeLab
series:
  - HomeAssistant
featured: true
---


[HomeAssistant](https://www.home-assistant.io/) 是免费开源的智能家庭自动化控制系统，支持接入多种平台，如 HomeKit，米家，ESPHome 等；国内大部分应用场景是将米家的设备通过 HomeAssistant 接入苹果生态，或者使用第三方组件，监控水电气等

## 基于容器搭建

HomeAssistant 支持多种运行方式，如以OS方式运行，或者使用二进制或容器等方式运行；容器等方式更方便管理

### 使用 Docker 直接运行

在 Linux 服务器使用容器启动 HomeAssistant，HomeAssistant 的所有配置和数据都在 `/config` 目录下，为了持久化数据，将当前路径挂载到 HomeAssistant 的 config 目录下；因为 HomeAssistant 需要访问局域网内的其他设备，因此，建议容器的网络模式使用 `host`，或者通过 `macvlan` 驱动为其单独创建网络

```bash
docker run -d \
 --name="home-assistant"
 -v ${pwd}:/config \
 -v /etc/localtime:/etc/localtime:ro \
 --net=host \
 homeassistant/home-assistant
```

### 使用 Docker Compose 启动

- docker-compose.yaml

```bash
version: '3'

services:
  homeassistant:
    container_name: homeassistant
    image: "homeassistant/home-assistant"
    privileged: true
    network_mode: host
    restart: always
    healthcheck:
      test: ["CMD", "wget", "-q","--spider", "http://localhost:8123"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 90s
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "./config:/config"
```

启动后，通过访问服务器的 8123 接口，使用用户名 `admin` 和密码 `admin` 访问即可进入 HomeAssistant

![homelab-homeassistant-login.png](https://img.hellowood.dev/picture/homelab-homeassistant-login.png)

## 添加 HACS

[HACS](https://hacs.xyz/) 是 HomeAssistant 社区的应用商店，支持通过 HomeAssistant 直接安装插件或 UI 组件；安装方式参考 [Download](https://hacs.xyz/docs/setup/download)；HomeAssistant 以容器方式运行时，需要进入到容器执行安装脚本

- 进入容器

```bash
docker exec -it homeassistant bash
```

- 安装 HACS

```bash
wget -O - https://get.hacs.xyz | bash -
```

脚本执行成功后重启 HomeAssistant 即可在左侧菜单栏看到 HACS，说明安装成功

![homelab-homeassistant-hacs-install.png](https://img.hellowood.dev/picture/homelab-homeassistant-hacs-install.png)
