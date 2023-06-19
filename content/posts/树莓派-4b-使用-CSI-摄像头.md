---
title: "树莓派 4b 使用 CSI 摄像头"
date: 2023-03-11T21:38:25+08:00
tags:
    - RaspberryPi
    - HomeLab
categories: 
    - RaspberryPi
    - HomeLab
series: 
    - RaspberryPi
featured: true  
---

# 树莓派 4b 使用 CSI 摄像头

树莓派 4b 支持通过 USB 或者摄像头 CSI 接口连接摄像头，因此可以使用树莓派 4b 作为监控

基于安装了 Ubuntu Server 22.04 LTS 的树莓派 4b 进行测试

带有红外补光灯的摄像头功率大概5-7w左右，因此使用树莓派 4b 连接时需要有 5V3A 的电源，否则当开启摄像头后树莓派会不断重启

## 接入摄像头

### 连接摄像头

如图所示，通过排线连接摄像头和树莓派（图片来自 [Getting started with the Camera Module](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera)）

![raspberrypi-4b-camara-setup-connect.jpeg](https://hellowoodes.oss-cn-beijing.aliyuncs.com/picture/raspberrypi-4b-camara-setup-connect.jpeg)


### 开启摄像头

开启摄像头需要先安装 `raspi-config` 软件

```bash
apt-get install -y raspi-config
```

然后运行 `raspi-config`，选择用户 `pi` 进行配置；

![raspberrypi-4b-camara-setup-enable-user-pi-0.png](https://hellowoodes.oss-cn-beijing.aliyuncs.com/picture/raspberrypi-4b-camara-setup-enable-user-pi-0.png)

接着选择第三个接口配置

![raspberrypi-4b-camara-setup-enable-interface-1.png](https://hellowoodes.oss-cn-beijing.aliyuncs.com/picture/raspberrypi-4b-camara-setup-enable-interface-1.png)

然后选择第一个，配置摄像头，选择开启即可；开启完成后，需要关闭树莓派，连接摄像头并重新开机

![raspberrypi-4b-camara-setup-enable-camare-2.png](https://hellowoodes.oss-cn-beijing.aliyuncs.com/picture/raspberrypi-4b-camara-setup-enable-camare-2.png)


### 检查摄像头信息

- 检查连接状态

重启后检查设备连接状态：

```bash
vcgencmd get_camera

supported=1 detected=1, libcamera interfaces=0
```

返回信息提示检查到了一个摄像头并且支持该摄像头

- 查看摄像头信息

查看摄像头信息需要使用 `v4l-utils`

```bash
apt-get install -y v4l-utils
```
通过 `v4l-utils` 列出设备

```bash
v4l2-ctl --list-devices
bcm2835-codec-decode (platform:bcm2835-codec):
        /dev/video10
        /dev/video11
        /dev/video12
        /dev/video18
        /dev/video31
        /dev/media1

bcm2835-isp (platform:bcm2835-isp):
        /dev/video13
        /dev/video14
        /dev/video15
        /dev/video16
        /dev/video20
        /dev/video21
        /dev/video22
        /dev/video23
        /dev/media0
        /dev/media2

mmal service 16.1 (platform:bcm2835-v4l2-0):
        /dev/video0
```

其中的 `/dev/video0` 就是通过排线连接的摄像头

## 使用摄像头

因为 `raspstill` 在 Ubuntu 下并不能直接安装，通过源码编译又需要很多的依赖，并且因为树莓派的性能限制，会比较复杂；因此通过 ffmpeg 来测试

### 安装 ffmpeg

```bash
apt-get install -y ffmpeg
```

### 检查

如果树莓派有连接显示器，可以通过 `ffplay` 进行查看；如果没有连接，则可以通过 `ffmpeg` 拍照查看

- 拍照

```bash
ffmpeg -i /dev/video0 -frames:v 1 -f image2 output.jpg
```

拍照之后可以通过 ftp 或者 scp 等方式将文件复制到本地；也可以直接通过 python 启动一个 HTTP 服务：`python3 -m http.server`，然后访问 8000 端口下载文件

- 录制视频

录制10s的视频，并输出为 mp4 格式

```bash
ffmpeg -f v4l2 -r 30 -s 640x480 -i /dev/video0 -c:v libx264 -preset ultrafast -tune zerolatency -t 10 output.mp4
```

- 查看视频

这里需要有显示器连接，否则无法预览

```bash
ffplay /dev/video0
```


## 参考文档 

- [Getting started with the Camera Module](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)