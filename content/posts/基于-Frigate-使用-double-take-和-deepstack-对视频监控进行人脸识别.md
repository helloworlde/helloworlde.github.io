---
title: "基于 Frigate 使用 Double Take 和 DeepStack 对视频监控进行人脸识别"
type: post
date: 2024-08-16T09:29:49+08:00
tags:
  - NVR
  - HomeLab
  - Frigate
series:
  - NVR
  - HomeLab
  - Frigate
featured: true
---

Double Take 是一个训练和识别人脸的工具，支持对 Frigate 中检测到的人物对象进行人脸识别，可以用于统计监控中出现的人物信息。不过经过测试，只适用于门禁、闸机等有清晰人脸的场景，日常的监控因安装位置、角度等原因无法提供清晰的人脸，因此识别的准确度和有效性并不高

![homelab-frigate-double-take-face-double-take-detect.png](https://img.hellowood.dev/picture/homelab-frigate-double-take-face-double-take-detect.png)

Double Take 的原理是通过监听 Frigate 识别到对象后发出的 MQTT 消息，根据消息获取对应事件的快照，并将其发送给识别的服务，如 Deepstack/CodeProject.AI 等，然后根据识别结果显示该事件中出现的人脸信息

Double Take 作者似乎已经放弃维护了，上次更新还是在两年前(2022-10-28)，尽管作者在今年的一月份(2024-1-7)声明计划[开发 2.0 版本](https://github.com/jakowenko/double-take/issues/343)，但是截止到8月份也没有任何进展，看起来作者在21年成为 24G.com 这家公司的 DevOps 总监后便没有精力投入到开源项目中了；不过，另外一位作者 skrashevich 在其 fork 的仓库 [skrashevich/double-take](https://github.com/skrashevich/double-take)中提交了不少 2.0 版本的计划的功能

## 部署依赖服务

Double Take 依赖 Frigate、MQTT 和人脸识别服务，部署在使用 Intel CPU 的 NUC 上，系统是 Ubuntu 22，地址是 192.168.31.254

### 部署 MQTT

MQTT 使用 emqx 提供的镜像进行部署，方便本地使用，参考[通过 Docker 运行 EMQX](https://docs.emqx.com/zh/emqx/latest/deploy/install-docker-ce.html)

- docker-compose.yaml

```yaml
services:
  mqtt:
    image: emqx/emqx
    container_name: mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "8083:8083"
      - "8084:8084"
      - "8883:8883"
      - "18083:18083"
```

启动后访问 18083端口，[http://192.168.31.254:18083/](http://192.168.31.254:18083/)，默认的用户名密码是 `admin`，密码是 `public`

![homelab-frigate-double-take-face-mqtt.png](https://img.hellowood.dev/picture/homelab-frigate-double-take-face-mqtt.png)

### 部署 Frigate

为了快速使用，Frigate 使用 Intel GPU 进行识别，如果监控不多，大多数的 NUC 和台式机都是可以满足识别诉求

- `docker-compose.yaml`

将显卡挂载到容器中，用于对象识别；同时将数据目录映射到宿主机，保存相关的数据，避免容器销毁后数据丢失

```yaml
services:
  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: 512mb
    devices:
      - /dev/dri/renderD128
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./config/:/config
      - ./data/db/:/data/db
      - ./data/storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    ports:
      - 5000:5000
    environment:
      - TZ=Asia/Shanghai
```

- `config/config.yml`

Frigate 的配置文件，详细参考 [Full Reference Config](https://docs.frigate.video/configuration/reference/)

```yaml
mqtt:
  enabled: True
  host: 192.168.31.254
  port: 1883

database:
  path: /data/db/frigate.db

# 监听 RTSP 地址
cameras:
  door:
    ffmpeg:
      inputs:
        - path: rtsp://admin:12345678@192.168.2.252:554/stream1&channel=1
          roles:
            - record
            - detect

# 使用 GPU 进行检测
detectors:
  ov:
    type: openvino
    device: GPU

# OpenVINO 需要指定模型信息
model:
  width: 300
  height: 300
  input_tensor: nhwc
  input_pixel_format: bgr
  path: /openvino-model/ssdlite_mobilenet_v2.xml
  labelmap_path: /openvino-model/coco_91cl_bkgr.txt

# 使用 GPU 加速 ffmpeg
ffmpeg:
  hwaccel_args: preset-vaapi

# 检测对象
objects:
  track:
    - person

# 保留快照
snapshots:
  enabled: True
  bounding_box: False
```

启动后，访问 [http://192.168.31.254:5000](http://192.168.31.254:5000) 进入 Frigate
![homelab-frigate-double-take-face-frigate.png](https://img.hellowood.dev/picture/homelab-frigate-double-take-face-frigate.png)

## 人脸识别服务

Double Take 支持多种探测器，分别是：CompreFace、Amazon Rekognition、DeepStack、CodeProject.AI Server 和 Facebox(Machine Box)，其中 Amazon Rekognition 和 Facebox(Machine Box) 需要上传或者上传部分数据，不符合隐私保护的诉求；其他项目对比如下

| 对比项目     | CompreFace               | DeepStack                    | CodeProject.AI Server                    |
| :----------- | :----------------------- | :--------------------------- | :--------------------------------------- |
| 图形化界面   | 有                       | 无                           | 有                                       |
| 支持模型     | 人脸相关模型             | 人脸检测、对象识别、对象分类 | 人脸检测、对象识别、对象分类、自定义模型 |
| 自定义模型   | 不支持                   | 支持自定义模型               | 支持自定义模型                           |
| 最后更新时间 | 2023-11-14               | 2022-07-01                   | 2024-05-22                               |
| 是否支持 GPU | 支持                     | 支持                         | 支持                                     |
| 加速器支持   | 不支持                   | Jetson                       | Google Coral TPU                         |
| 人脸检测     | 检测不准确，需有明确人脸 | 检测准确，正脸/侧脸均可识别  | 检测准确，正脸/侧脸均可识别              |
| 人脸识别     | 准确度高                 | 小面积人脸识别不准确         | 小面积人脸识别不准确                     |

DeepStack 使用最简单，因此使用 DeepStack 进行测试

- docker-compose.yaml

```yaml
services:
  deepstack:
    image: deepquestai/deepstack
    container_name: deepstack
    restart: unless-stopped
    environment:
      - VISION-FACE=True
    volumes:
      - ./data:/datastore
    ports:
      - "5002:5000"
```

## Double Take

### 部署 Double Take

- docker-compose.yaml

```yaml
services:
  double-take:
    container_name: double-take
    image: skrashevich/double-take
    restart: unless-stopped
    volumes:
      - ./data:/.storage
    ports:
      - 3000:3000
```

### 配置 Double Take

启动 Double Take，添加配置

![homelab-frigate-double-take-face-double-take-config.png](https://img.hellowood.dev/picture/homelab-frigate-double-take-face-double-take-config.png)

```yaml
mqtt:
  host: 192.168.2.254

  topics:
    frigate: frigate/events
    matches: double-take/matches
    cameras: double-take/cameras

detect:
  match:
    save: true
    # 最低置信度
    confidence: 60
    # 保留时间，单位是小时
    purge: 168
  unknown:
    save: true # 保留未识别的

frigate:
  url: http://192.168.2.254:5000
  # 识别对象
  labels:
    - person
# 使用 deepstack 识别
detectors:
  deepstack:
    url: http://192.168.2.254:5002
    timeout: 15
```

保存配置后重新启动 Double Take，当监控中出现人脸时会自动进行检测；可以选择部分进行训练，或者上传已经准备好的照片进行训练，当下次出现时即可进行识别

![homelab-frigate-double-take-face-double-take-detect.png](https://img.hellowood.dev/picture/homelab-frigate-double-take-face-double-take-detect.png)

## 参考文档

- [Third Party Extensions](https://docs.frigate.video/integrations/third_party_extensions)
- [double-take](https://github.com/skrashevich/double-take)
- [CompreFace](https://github.com/exadel-inc/CompreFace)
- [DeepStack](https://github.com/johnolafenwa/DeepStack)
- [CodeProject.AI](https://www.codeproject.com/AI/docs/index.html)
- [Facebox](https://machinebox.io/)
- [Amazon Rekognition](https://aws.amazon.com/cn/rekognition/)
