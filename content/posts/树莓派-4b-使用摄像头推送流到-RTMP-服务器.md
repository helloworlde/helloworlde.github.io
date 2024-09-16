---
title: "树莓派 4b 使用摄像头推送流到 RTMP 服务器"
type: post
date: 2023-03-11T21:36:47+08:00
tags:
  - RaspberryPi
  - HomeLab
categories:
  - RaspberryPi
  - HomeLab
featured: true
---

使用树莓派 4b，基于 Ubuntu 22.04，将摄像头的监控内容推送到 RTMP 服务器，用于其他服务从 RTMP 获取视频，进行视频分析和事件告警ss
树莓派摄像头使用排线进行连接，通过 ffmpeg 将视频流推送到 [SRS](https://ossrs.io/lts/zh-cn/docs/v4/doc/introduction) 服务器（SRS是一个简单高效的实时视频服务器，支持RTMP/WebRTC/HLS/HTTP-FLV/SRT/GB28181）

树莓派连接摄像头可以参考 [树莓派 4b 使用摄像头](https://blog.hellowood.dev)

## 安装 ffmpeg

```bash
apt-get update && apt-get install -y ffmpeg
```

## 安装 SRS

SRS 使用 Docker Compose 进行部署；用于处理 ffmpeg 推送的视频流

- docker-compose.yaml

```yaml
version: "3"

services:
  srs:
    image: "registry.cn-hangzhou.aliyuncs.com/ossrs/srs:4"
    restart: unless-stopped
    container_name: "srs"
    hostname: srs
    ports:
      - "1935:1935"
      - "1985:1985"
      - "8080:8080"
    volumes:
      - "./data:/srs"
```

## 使用 ffmpeg 推送流到 SRS

通过 ffmpeg 将视频内容推送到 SRS

```bash
ffmpeg -f v4l2 -input_format mjpeg -video_size 1280x720 -framerate 30 -i /dev/video0 -c:v libx264 -preset veryfast -tune zerolatency -b:v 2M -minrate 2M -maxrate 2M -bufsize 1M -g 60 -an -f flv rtmp://192.168.2.5/live/livestream
```

其各个参数含义如下：

- `-f v4l2`：输入设备为 V4L2 （Video for Linux 2）摄像头。
- `-input_format mjpeg`：输入视频格式为 MJPEG。
- `-video_size 1280x720`：设置视频分辨率为 1280x720。
- `-framerate 30`：设置帧率为 30 帧每秒。
- `-i /dev/video0`：指定输入设备为 /dev/video0。
- `-c:v libx264`：选择 H.264 编码器用于视频编码。
- `-preset veryfast`：选用压缩速度优先的预设（veryfast 表示非常快）。
- `-tune zerolatency`：调整编码器以最小化延迟。
- `-b:v 2M`：设置视频编码的目标比特率为 2 Mbps。
- `-minrate 2M -maxrate 2M -bufsize 1M`：设置最小、最大比特率和缓存大小，以确保稳定的视频传输。
- `-g 60`：设置 GOP （Group of Pictures）大小为 60 帧。
- `-an`：不使用音频流。
- `-f flv`：输出格式为 Flash 视频（FLV）。
- `rtmp://192.168.2.5/live/livestream`：指定输出 URL，将视频流推送到 IP 地址为 192.168.2.5 的服务器上，路径为 /live/livestream。

然后访问 [http://192.168.2.5:8080/players/srs_player.html?autostart=true&stream=livestream.flv&port=8080&schema=http](http://rasp.local:8088/players/srs_player.html?autostart=true&stream=livestream.flv&port=8080&schema=http) 查看视频内容

## 使用 Docker 容器运行 ffmpeg

也可以通过 Docker 容器的方式运行 ffmpeg，基于 Ubuntu 的镜像安装 ffmpeg 即可

```bash
version: '3'

services:
  srs:
    image: "registry.cn-hangzhou.aliyuncs.com/ossrs/srs:4"
    restart: unless-stopped
    container_name: "srs"
    hostname: srs
    ports:
      - "1935:1935"
      - "1985:1985"
      - "8088:8080"
    volumes:
      - "./data:/srs"

  ffmpeg:
    image: "hellowoodes/ffmpeg-rasp"
    restart: unless-stopped
    container_name: "ffmpeg"
    hostname: ffmpeg
    extra_hosts:
      - "host.docker.internal:host-gateway"
    command: >
      sh -c "ffmpeg -f v4l2 \
              -input_format mjpeg \
              -video_size 1920x1080 \
              -framerate 24 \
              -i /dev/video0 \
              -c:v libx264 \
              -preset veryfast \
              -tune zerolatency \
              -b:v 2M \
              -minrate 2M \
              -maxrate 2M \
              -bufsize 1M \
              -g 60 \
              -an \
              -f flv \
              rtmp://host.docker.internal/live/livestream"
    volumes:
      - /etc/localtime:/etc/localtime:ro
    devices:
      - /dev/video0:/dev/video0
```
