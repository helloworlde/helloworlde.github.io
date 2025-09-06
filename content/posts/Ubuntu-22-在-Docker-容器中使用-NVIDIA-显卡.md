---
title: "Ubuntu 22 在 Docker 容器中使用 NVIDIA 显卡"
type: post
date: 2024-08-06T09:15:33+08:00
lastmod: 2024-09-16
tags:
  - Ubuntu
  - NVIDIA
  - CUDA
featured: true
---

在容器中运行需要使用 NVIDIA 显卡进行加速的服务，如图像识别、LLM 等，需要将显卡挂载到容器中

## 安装 NVIDIA 容器工具包

- 添加软件源

需要添加 NVIDIA 容器工具包的软件源和 gpg 签名

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

- 更新软件并安装 NVIDIA 容器工具包

```bash
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

## 配置 Docker

- 使用 nvidia-ctk 修改 Docker 配置

修改 Docker 配置，允许将显卡挂载到容器中

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

```bash
WARN[0000] Ignoring runtime-config-override flag for docker
INFO[0000] Loading config from /etc/docker/daemon.json
INFO[0000] Wrote updated config to /etc/docker/daemon.json
INFO[0000] It is recommended that docker daemon be restarted.
```

这样会自动修改 `/etc/docker/daemon.json` 文件，添加显卡 `runtimes` 相关的内容：

```json
{
  "runtimes": {
    "nvidia": {
      "args": [],
      "path": "nvidia-container-runtime"
    }
  }
}
```

- 重启 Docker

```bash
sudo systemctl restart docker
```

## 使用

以 NIVDIA 官方提供的测试镜像为例

- docker 命令行使用

```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

将会使用 `nvidia-smi` 输出显卡相关的信息:

```bash
Wed Aug  7 01:12:17 2024
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.183.01             Driver Version: 535.183.01   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3070 Ti     Off | 00000000:01:00.0 Off |                  N/A |
| 30%   33C    P8               7W / 310W |   6758MiB /  8192MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+

+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
+---------------------------------------------------------------------------------------+
```

- docker-compose 使用

在 deploy 中指定要挂载的显卡数量，可以是数字或者 `all`；

```yaml
services:
  test:
    image: nvidia/cuda:12.3.1-base-ubuntu20.04
    command: nvidia-smi
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

也可以只挂载特定的显卡，通过 `device_ids` 指定：

```yaml
services:
  test:
    image: tensorflow/tensorflow:latest-gpu
    command: python -c "import tensorflow as tf;tf.test.gpu_device_name()"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ["0", "3"]
              capabilities: [gpu]
```

## 参考文档

- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [Turn on GPU access with Docker Compose](https://docs.docker.com/compose/gpu-support/)
