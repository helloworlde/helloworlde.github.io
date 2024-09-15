---
title: "Ubuntu 22 运行 Google Coral TPU 示例"
type: post
date: 2024-07-09T09:30:21+08:00
tags:
  - Ubuntu
  - Coral
series:
  - Ubuntu
  - Coral
featured: true
---

在 Ubuntu 22 上运行 Google Coral TPU 的示例项目

## 配置运行环境

Coral 只支持 Python 3.6～3.9 的环境，而 Ubuntu 22 的 Python 版本为 3.10；因此需要使用 Anaconda 创建独立的运行环境

### 安装 Anaconda

参考 [Installing on Linux](https://docs.anaconda.com/anaconda/install/linux/) 安装

### 初始化环境

使用 Python 3.8 版本创建运行环境

```bash
conda create -n coral python=3.8
```

待创建完成后激活该环境

```bash
conda activate coral
```

## 运行 Demo

### 下载项目

- 创建 Coral 的工作目录，并克隆项目到本地

```bash
mkdir coral && cd coral
git clone https://github.com/google-coral/pycoral.git
```

### 下载依赖

#### 下载模型、图片依赖

```bash
cd pycoral
bash examples/install_requirements.sh classify_image.py
```

#### 安装项目依赖

需要安装 pycoral 和 tflite-runtime，但是在 Ubuntu 22 上无法通过 `sudo apt-get install python3-pycoral` 直接安装 `python3-pycoral`，因此需要指定依赖地址安装；相关版本可以从 [https://github.com/google-coral/pycoral/releases/](https://github.com/google-coral/pycoral/releases/) 查找

- 安装 tflite-runtime

因为是指定地址单独安装的，所以要先安装 tflite-runtime，然后再安装 pycoral

```bash
pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/tflite_runtime-2.5.0.post1-cp38-cp38-linux_x86_64.whl
```

- 安装 pycoral

```bash
pip install https://github.com/google-coral/pycoral/releases/download/v2.0.0/pycoral-2.0.0-cp38-cp38-linux_x86_64.whl
```

- 安装其他依赖

项目运行还需要 numpy 和 Pillow 依赖

```bash
pip install numpy
pip install Pillow
```

### 运行项目

运行图像分类 demo

```bash
python3 examples/classify_image.py \
--model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--labels test_data/inat_bird_labels.txt \
--input test_data/parrot.jpg
```

可以看到输出结果是一只鹦鹉，置信度是 0.75781，推理耗时大约 2.7ms

```bash
----INFERENCE TIME----
Note: The first inference on Edge TPU is slow because it includes loading the model into Edge TPU memory.
11.8ms
2.8ms
2.7ms
2.8ms
2.7ms
-------RESULTS--------
Ara macao (Scarlet Macaw): 0.75781
```

## 参考文档

- [Run a model on the Edge TPU](https://coral.ai/docs/m2/get-started/#4-run-a-model-on-the-edge-tpu)
- [Update "Install the PyCoral library" instructions](https://github.com/google-coral/edgetpu/issues/771)
