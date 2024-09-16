---
title: "Frigate 使用 Hailo 8 或 Hailo 8L 进行对象识别"
type: post
date: 2024-09-01T11:25:24+08:00
tags:
  - NVR
  - HomeLab
  - Frigate
  - Hailo
  - TPU
featured: true
---

Hailo8/Hailo-8L 是一家以色列的边缘人工智能公司发布的边缘加速器，定位和 [Google Coral TPU](https://coral.ai/products/) 完全一致；Hailo-8 算力为 26 TOPS，Hailo-8L 算力为 13 TOPS

| 特性               | Google Coral TPU                                 | Hailo8                                                                 | Hailo8L                                                                |
| ------------------ | ------------------------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **支持框架**       | TensorFlow, TensorFlow Lite                      | TensorFlow, TensorFlow Lite, Keras, PyTorch, ONNX                      | TensorFlow, TensorFlow Lite, Keras, PyTorch, ONNX                      |
| **支持模型**       | MobileNet, Inception, EfficientNet 等            | ResNet-50, MobileNet_v2, SSD, YOLOv3, YOLOv5 等                        | ResNet-50, MobileNet_v2, SSD, YOLOv3, YOLOv5 等                        |
| **模型功能**       | 对象识别、对象分类，语义分割，姿态识别，音频分类 | 对象识别、对象分类，语义分割，姿态识别，深度估计，人脸检测，人脸识别等 | 对象识别、对象分类，语义分割，姿态识别，深度估计，人脸检测，人脸识别等 |
| **硬件性能**       | 4 TOPS                                           | 26 TOPS                                                                | 13 TOPS                                                                |
| **发布时间**       | 2019年                                           | 2021年                                                                 | 2023年                                                                 |
| **功耗**           | 0.5-2 W                                          | 2.5-4.6 W                                                              | 1.8-3.2 W                                                              |
| **每W性能**        | 8 TOPS/W                                         | 10.4 TOPS/W                                                            | 7.2 TOPS/W                                                             |
| **当前价格**       | 约300~1000¥                                      | 约 1300¥                                                               | 约550¥                                                                 |
| **支持的操作系统** | Linux, Windows, MacOS                            | Linux, Windows                                                         | Linux, Windows                                                         |
| **可扩展性**       | 不支持多芯片                                     | 支持多芯片并行处理                                                     | 支持多芯片并行处理                                                     |
| **应用领域**       | 物联网设备、嵌入式系统                           | 工业自动化、智能监控、自动驾驶                                         | 工业自动化、智能监控、智能零售                                         |

Frigate 的最新的代码已经合并了 Hailo8L 的 PR，预计将会在 0.15 版本中正式发布，PR 参考 [Initial support for Hailo-8L](https://github.com/blakeblackshear/frigate/pull/12431) 和 [Hailo amd64 support](https://github.com/blakeblackshear/frigate/pull/12820)；虽然 PR 中支持的设备是 Hailo-8L，但是经过测试验证，只需要替换对应的模型，Hailo-8 也是可以正常运行的（Hailo-8 和 Hailo-8L 的模型不能互相使用）

## Frigate 使用 Hailo8/8L

使用之前，需要确保 Hailo 的 PCIE Driver 已经正确安装，参考 [Ubuntu22 安装初始化 Hailo 8系列 TPU 加速器](https://blog.hellowood.dev/posts/ubuntu22-%E5%AE%89%E8%A3%85%E5%88%9D%E5%A7%8B%E5%8C%96-hailo-8%E7%B3%BB%E5%88%97-tpu-%E5%8A%A0%E9%80%9F%E5%99%A8/)

### 将 Hailo 设备挂载到容器

- docker-compose.yaml

注意，`ghcr.io/helloworlde/frigate:0.15-f4d311c-h8l` 是基于 4.18 版本的驱动的，而 Frigate 的仓库是基于 4.17 版本的驱动，如果驱动和容器中的运行环境版本不一致，可能会导致 Hailo 调用失败；最新的镜像版本可以在 [Packages](https://github.com/blakeblackshear/frigate/pkgs/container/frigate) 中查找

```yaml
services:
  frigate-hailo:
    container_name: frigate-hailo
    privileged: true
    restart: unless-stopped
    image: ghcr.io/helloworlde/frigate:0.15-f4d311c-h8l
    shm_size: 512mb
    devices:
      - /dev/hailo0:/dev/hailo0
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

### 修改配置文件

配置文件路径是 `./config/config.yml`；指定了 detector 使用 hailo8l，并且指定了模型的路径；如果该路径下没有模型，会自动从 S3 下载；默认使用的是 ssd_mobilenet_v1 模型

```yaml
database:
  path: /data/db/frigate.db

cameras:
  bedroom:
    ffmpeg:
      inputs:
        - path: rtsp://admin:123456@192.168.31.100:554/stream1&channel=1
          roles:
            - record
            - detect

objects:
  track:
    - person
    - cat

detectors:
  hailo8l:
    type: hailo8l
    device: PCIe
    model:
      path: /config/model_cache/h8l_cache/ssd_mobilenet_v1.hef

model:
  width: 300
  height: 300
  input_tensor: nhwc
  input_pixel_format: bgr
  model_type: ssd
```

如果使用的是 Hailo-8，则需要下载 Hailo-8 的模型到本地挂载到容器中，并修改配置为模型对应的配置；Hailo-8 的模型可以从 [Public Pre-Trained Models](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_object_detection.rst) 下载，以 yolov8n 为例，修改 path、width 和 height 即可

```yaml
detectors:
  hailo8l:
    type: hailo8l
    device: PCIe
    model:
      path: /config/model_cache/h8_cache/yolov8n.hef

model:
  width: 640
  height: 640
  input_tensor: nhwc
  input_pixel_format: bgr
```

使用 12个 1080p 的监控，以 5fps 进行视频内容识别，使用 hailo-8 和 yolox 模型的推理速度约为 60ms，使用 hailo-8/8L 和 ssd_mobilenet_v1 模型的推理速度约为 15ms，而 Google Coral TPU 的推理速度约为 8ms；在当前的 Frigate 版本下，使用 Google Coral TPU 和小模型检测对象更快

![homelab-frigate-tpu-hailo-8-system-metrics.png](https://img.hellowood.dev/picture/homelab-frigate-tpu-hailo-8-system-metrics.png)

## 遇到的问题

### Invalid general ioctl code 0x400c6705

使用官方的镜像启动后包错，提示 hailo_platform.pyhailort.\_pyhailort.HailoRTStatusException，检查 dmesg 发现错误信息为 `Invalid general ioctl code 0x400c6705`，这是因为驱动版本不一致导致的；官方镜像中的版本为 4.17，而本地安装的驱动版本为 4.18，导致命令无法识别；重新安装 4.17 版本的驱动，或者将 Frigate 镜像中的 HailoRT 版本改为相同的即可

frigate 日志：

```python
frigate-hailo  | 2024-08-24 21:51:44.835191724  [2024-08-24 21:51:44] frigate.detectors.plugins.hailo8l ERROR   : HailoRTException during initialization: PCIe driver failure. run 'dmesg | grep hailo' for more information
frigate-hailo  | 2024-08-24 21:51:44.836911083  Traceback (most recent call last):
frigate-hailo  | 2024-08-24 21:51:44.836918597    File "/usr/local/lib/python3.9/dist-packages/hailo_platform/pyhailort/pyhailort.py", line 2610, in _open_vdevice
frigate-hailo  | 2024-08-24 21:51:44.836919078      self._vdevice = _pyhailort.VDevice.create(self._params, device_ids)
frigate-hailo  | 2024-08-24 21:51:44.836928015  hailo_platform.pyhailort._pyhailort.HailoRTStatusException: 36
frigate-hailo  | 2024-08-24 21:51:44.837285278
frigate-hailo  | 2024-08-24 21:51:44.837286139  The above exception was the direct cause of the following exception:
frigate-hailo  | 2024-08-24 21:51:44.837286440
frigate-hailo  | 2024-08-24 21:51:44.837286760  Traceback (most recent call last):
frigate-hailo  | 2024-08-24 21:51:44.837302350    File "/usr/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
frigate-hailo  | 2024-08-24 21:51:44.837302841      self.run()
frigate-hailo  | 2024-08-24 21:51:44.837308171    File "/usr/lib/python3.9/multiprocessing/process.py", line 108, in run
frigate-hailo  | 2024-08-24 21:51:44.837308732      self._target(*self._args, **self._kwargs)
frigate-hailo  | 2024-08-24 21:51:44.837309313    File "/opt/frigate/frigate/object_detection.py", line 102, in run_detector
frigate-hailo  | 2024-08-24 21:51:44.837309904      object_detector = LocalObjectDetector(detector_config=detector_config)
frigate-hailo  | 2024-08-24 21:51:44.837318260    File "/opt/frigate/frigate/object_detection.py", line 53, in __init__
frigate-hailo  | 2024-08-24 21:51:44.837318961      self.detect_api = create_detector(detector_config)
frigate-hailo  | 2024-08-24 21:51:44.837319482    File "/opt/frigate/frigate/detectors/__init__.py", line 18, in create_detector
frigate-hailo  | 2024-08-24 21:51:44.837319943      return api(detector_config)
frigate-hailo  | 2024-08-24 21:51:44.837320514    File "/opt/frigate/frigate/detectors/plugins/hailo8l.py", line 73, in __init__
frigate-hailo  | 2024-08-24 21:51:44.837322888      self.target = VDevice()
frigate-hailo  | 2024-08-24 21:51:44.837328058    File "/usr/local/lib/python3.9/dist-packages/hailo_platform/pyhailort/pyhailort.py", line 2603, in __init__
frigate-hailo  | 2024-08-24 21:51:44.837328599      self._open_vdevice()
frigate-hailo  | 2024-08-24 21:51:44.837329281    File "/usr/local/lib/python3.9/dist-packages/hailo_platform/pyhailort/pyhailort.py", line 2610, in _open_vdevice
frigate-hailo  | 2024-08-24 21:51:44.837329902      self._vdevice = _pyhailort.VDevice.create(self._params, device_ids)
frigate-hailo  | 2024-08-24 21:51:44.837330623    File "/usr/local/lib/python3.9/dist-packages/hailo_platform/pyhailort/pyhailort.py", line 111, in __exit__
frigate-hailo  | 2024-08-24 21:51:44.837331394      self._raise_indicative_status_exception(value)
frigate-hailo  | 2024-08-24 21:51:44.837338017    File "/usr/local/lib/python3.9/dist-packages/hailo_platform/pyhailort/pyhailort.py", line 146, in _raise_indicative_status_exception
frigate-hailo  | 2024-08-24 21:51:44.837338959      raise HailoRTPCIeDriverException("PCIe driver failure. run 'dmesg | grep hailo' for more information") from libhailort_exception
frigate-hailo  | 2024-08-24 21:51:44.837357273  hailo_platform.pyhailort.pyhailort.HailoRTPCIeDriverException: PCIe driver failure. run 'dmesg | grep hailo' for more information
```

查看 dmesg 日志：

```bash
dmesg | grep hailo
```

```bash
[   67.062136] hailo_pci: loading out-of-tree module taints kernel.
[   67.062191] hailo_pci: module verification failed: signature and/or required key missing - tainting kernel
[   67.068815] hailo: Init module. driver version 4.18.0
[   67.069665] hailo 0000:04:00.0: Probing on: 1e60:2864...
[   67.069670] hailo 0000:04:00.0: Probing: Allocate memory for device extension, 11632
...

[  188.404620] hailo 0000:04:00.0: Invalid general ioctl code 0x400c6705 (nr: 5)
```

修改为相同版本镜像后 Hailo 成功加载:

```python
frigate-hailo  | 2024-08-24 22:02:33.745564255  [2024-08-24 22:02:33] frigate.detectors.plugins.hailo8l INFO    : A model file already exists at /config/model_cache/h8l_cache/ssd_mobilenet_v1.hef not downloading one.
frigate-hailo  | 2024-08-24 22:02:33.871380296  [2024-08-24 22:02:33] frigate.detectors.plugins.hailo8l INFO    : Hailo device initialized successfully
```

## 参考文档

- [HAILO8L 对象识别模型](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_object_detection.rst)
- [HAILO8 对象识别模型](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_object_detection.rst)
- [修改 Frigate HailoRT 版本为 4.18](https://github.com/helloworlde/frigate/commit/f4d311c4c8fbeb8cd9e16b5bfbb60f3d276a00dd)
- [HailoRTPCIeDriverException: PCIe driver failure](https://community.hailo.ai/t/hailortpciedriverexception-pcie-driver-failure/2358/2)
