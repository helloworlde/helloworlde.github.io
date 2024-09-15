---
title: "将重新训练的 Yolov8 模型编译为 Hailo 8 和 Hailo 8L 支持的模型"
date: 2024-09-08T21:32:21+08:00
tags: 
    - Ubuntu
    - Hailo
    - TPU
series: 
    - Ubuntu
    - Hailo
    - TPU
featured: true
---

在 Ubuntu 22 将自行训练的 Yolov8n 模型编译为 Hailo8/Hailo8L 支持的 hef 格式的模型，在 Hailo8 上使用自行训练的模型进行对象检测

## 1. 环境准备

- anaconda 

参考 [Installing on Linux](https://docs.anaconda.com/anaconda/install/linux/) 安装

## 2. 训练 yolo 模型

### 2.1 安装依赖

- 创建环境
 
单独创建 ultralytics 的环境，用于训练和导出 yolo 模型为其他格式

```bash
conda create -n ultralytics python=3.10
```

- 激活环境

```bash
conda activate ultralytics
```

- 安装 ultralytics

```bash
pip install ultralytics
```

等待安装完成后就可以使用 `yolo` 命令训练和导出模型了

### 2.2 训练模型

训练模型可以参考 roboflow 的博客 [How to Train YOLOv8 Object Detection on a Custom Dataset](https://blog.roboflow.com/how-to-train-yolov8-on-a-custom-dataset/)；为了测试验证流程，先使用官方提供的 yolov8n 当作训练的模型，可以从 [https://github.com/ultralytics/assets/releases/](https://github.com/ultralytics/assets/releases) 下载，以 yolov8n 为例，下载地址为 [https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt)

```bash
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
```

### 2.3 将模型导出为 onnx 格式

```bash
yolo export model=./yolov8n.pt imgsz=640 format=onnx opset=11
```

imgsz=640 指定输入图片的尺寸（图像大小），即 640x640。这个尺寸是模型在推理时处理图像的分辨率

format=onnx 指定导出的模型格式为 ONNX（Open Neural Network Exchange）。ONNX 是一种支持在不同深度学习框架间转换和共享模型的开放格式

opset=11 指定 ONNX 的操作集版本为 11


## 3. 编译为 Hailo 模型

### 3.1 准备环境

#### 3.1.1 创建环境

- 创建环境

单独创建一个 hailo 的环境，避免和 ultralytics 依赖冲突

```bash
conda create -n hailo python=3.10
```

- 激活环境

```bash
conda activate hailo
```

#### 3.1.2 安装 hailo_model_zoo

- 安装 hailo_model_zoo

从 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 下载并安装 hailo_model_zoo

![homelab-tpu-hailo-software-download-hailo-model-zoo.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-hailo-model-zoo.png)

```bash
pip install hailo_model_zoo-2.12.0-py3-none-any.whl
```

#### 3.1.3 准备 Coco 数据集

安装 Coco 数据集，用于评估、优化和编译模型；因为是通过 conda 安装的，代码所在路径是 conda env 路径 + 环境名称 + 包路径，即 `~/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo`

- 准备 val 数据

```bash
python ~/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/datasets/create_coco_tfrecord.py val2017
```

将会下载 coco 的 val 数据到 `~/.hailomz` 路径下；val 数据用于验证模型

```bash
2024-09-08 16:53:52.437311: I tensorflow/core/util/port.cc:110] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2024-09-08 16:53:52.438390: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2024-09-08 16:53:52.458864: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2024-09-08 16:53:52.459101: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-09-08 16:53:52.747289: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
48 / 5000 images have no annotations
val2017 #5000: /home/ubuntu/.hailomz/data/coco/val2017/000000365098.jpg: 100%|████████████████████████████████████████████████████████████████████████████████████████| 5000/5000 [00:09<00:00, 526.82it/s]
```

- 准备 calib 数据

```bash
python ~/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/datasets/create_coco_tfrecord.py calib2017
```

会下载名为 `train2017.zip` 大约 18G 的 Coco 数据集解压并处理，路径是 `～/.hailomz`；calib 数据集用于模型的量化校准

```bash
2024-09-08 16:54:19.758265: I tensorflow/core/util/port.cc:110] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2024-09-08 16:54:19.759360: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2024-09-08 16:54:19.779913: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2024-09-08 16:54:19.780151: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-09-08 16:54:20.070489: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
1021 / 118287 images have no annotations
calib2017 #8192: /home/ubuntu/.hailomz/data/coco/train2017/000000171472.jpg: 100%|████████████████████████████████████████████████████████████████████████████████████| 8192/8192 [00:15<00:00, 529.18it/s]

Done converting 8192 images
```

#### 3.1.4 安装 hailo_dataflow_compiler

- 安装 hailo_dataflow_compiler 依赖

hailo_dataflow_compiler 用于将其他模型编译为 Hailo 支持的模型；在安装 hailo_dataflow_compiler 之前，需要先安装 pygraphviz，如果通过 hailo_dataflow_compiler 安装可能会提示 `fatal error: graphviz/cgraph.h: 没有那个文件或目录`，改成用 conda 安装即可

```bash
conda install pygraphviz
```

从 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 下载并安装 hailo_dataflow_compiler

![homelab-tpu-hailo-software-download-hailo-data-compile.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-hailo-data-compile.png)

```bash
pip install hailo_dataflow_compiler-3.28.0-py3-none-linux_x86_64.whl
```

### 3.2 编译模型

Hailo 不同硬件的模型不通用，所以需要在编译时通过 `--hw-arch` 指定硬件类型，以 Hailo8 为例，需要指定 `--hw-arch hailo8`；如果是 Hailo8L 则指定 `--hw-arch hailo8l`

#### 3.2.1 解析模型

parse 用于将模型从各种框架解析为 HAR 格式（Hailo Archive）的步骤，HAR 是一个 tar.gz 存档文件，其中包含部署到 Hailo 运行时的图结构和权重的表示形式

```bash
hailomz parse --hw-arch hailo8 --ckpt ./best.onnx yolov8n
```

```bash
<Hailo Model Zoo INFO> Start run for network yolov8n ...
<Hailo Model Zoo INFO> Initializing the runner...
[info] Translation started on ONNX model yolov8n
[info] Restored ONNX model yolov8n (completion time: 00:00:00.04)
[info] Extracted ONNXRuntime meta-data for Hailo model (completion time: 00:00:00.26)
[info] NMS structure of yolov8 (or equivalent architecture) was detected.
[info] In order to use HailoRT post-processing capabilities, these end node names should be used: /model.22/cv2.0/cv2.0.2/Conv /model.22/cv3.0/cv3.0.2/Conv /model.22/cv2.1/cv2.1.2/Conv /model.22/cv3.1/cv3.1.2/Conv /model.22/cv2.2/cv2.2.2/Conv /model.22/cv3.2/cv3.2.2/Conv.
[info] Start nodes mapped from original model: 'images': 'yolov8n/input_layer1'.
[info] End nodes mapped from original model: '/model.22/cv2.0/cv2.0.2/Conv', '/model.22/cv3.0/cv3.0.2/Conv', '/model.22/cv2.1/cv2.1.2/Conv', '/model.22/cv3.1/cv3.1.2/Conv', '/model.22/cv2.2/cv2.2.2/Conv', '/model.22/cv3.2/cv3.2.2/Conv'.
[info] Translation completed on ONNX model yolov8n (completion time: 00:00:00.67)
[info] Saved HAR to: /home/ubuntu/workspace/hailo/custom-train/data/model/yolov8n.har
```

#### 3.2.2 量化模型

optimize 输入是 Hailo 模型状态下的 HAR 文件（优化前；具有本机权重），输出将是具有量化权重的量化 HAR 文件

```bash
hailomz optimize --hw-arch hailo8 --har ./yolov8n.har yolov8n
```

输出如下；如果这个过程提示 `FileNotFoundError: no alls found for requested hw_arch`，参考后面问题部分处理

```bash
<Hailo Model Zoo INFO> Start run for network yolov8n ...
<Hailo Model Zoo INFO> Initializing the hailo8 runner...
<Hailo Model Zoo INFO> Preparing calibration data...
[info] Loading model script commands to yolov8n from /home/ubuntu/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/cfg/alls/hailo8/base/yolov8n.alls
[info] Starting Model Optimization
[warning] Reducing optimization level to 0 (the accuracy won't be optimized and compression won't be used) because there's no available GPU
[warning] Running model optimization with zero level of optimization is not recommended for production use and might lead to suboptimal accuracy results
[info] Model received quantization params from the hn
[info] Starting Mixed Precision
[info] Mixed Precision is done (completion time is 00:00:00.26)
[info] Layer Norm Decomposition skipped
[info] Starting Stats Collector
[info] Using dataset with 64 entries for calibration
Calibration: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [00:15<00:00,  4.25entries/s]
[info] Stats Collector is done (completion time is 00:00:15.89)
[info] Starting Fix zp_comp Encoding
[info] Fix zp_comp Encoding is done (completion time is 00:00:00.00)
[info] matmul_equalization skipped
[info] Finetune encoding skipped
[info] Bias Correction skipped
[info] Adaround skipped
[info] Fine Tune skipped
[info] Layer Noise Analysis skipped
[info] Model Optimization is done
[info] Saved HAR to: /home/ubuntu/workspace/hailo/custom-train/data/model/yolov8n.har
```

#### 3.2.3 编译模型

compile 将模型转换为HEF可执行格式

```bash
hailomz compile  yolov8n --hw-arch hailo8 --har ./yolov8n.har
```

输出如下：

```bash
<Hailo Model Zoo INFO> Start run for network yolov8n ...
<Hailo Model Zoo INFO> Initializing the hailo8 runner...
[info] Loading model script commands to yolov8n from /home/ubuntu/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/cfg/alls/hailo8/base/yolov8n.alls
[info] To achieve optimal performance, set the compiler_optimization_level to "max" by adding performance_param(compiler_optimization_level=max) to the model script. Note that this may increase compilation time.
[info] Adding an output layer after conv41
[info] Adding an output layer after conv42
[info] Adding an output layer after conv52
[info] Adding an output layer after conv53
[info] Adding an output layer after conv62
[info] Adding an output layer after conv63
[info] Loading network parameters
[warning] Output order different size
[info] Starting Hailo allocation and compilation flow
[info] Using Single-context flow
[info] Resources optimization guidelines: Strategy -> GREEDY Objective -> MAX_FPS
[info] Resources optimization params: max_control_utilization=75%, max_compute_utilization=75%, max_compute_16bit_utilization=75%, max_memory_utilization (weights)=75%, max_input_aligner_utilization=75%, max_apu_utilization=75%
[info] Using Single-context flow
[info] Resources optimization guidelines: Strategy -> GREEDY Objective -> MAX_FPS
[info] Resources optimization params: max_control_utilization=75%, max_compute_utilization=75%, max_compute_16bit_utilization=75%, max_memory_utilization (weights)=75%, max_input_aligner_utilization=75%, max_apu_utilization=75%

Validating context_0 layer by layer (100%)

 +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
 +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
 +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
 +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
 +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +

● Finished

[info] Solving the allocation (Mapping), time per context: 59m 59s
Context:0/0 Iteration 4: Trying parallel mapping...
          cluster_0  cluster_1  cluster_2  cluster_3  cluster_4  cluster_5  cluster_6  cluster_7  prepost
 worker0  V          V          V          V          V          V          V          V          V
 worker1  *          *          *          *          *          *          *          *          V
 worker2  *          *          *          *          *          *          *          *          V
 worker3  *          *          *          *          *          *          *          *          V

  00:05
Reverts on cluster mapping: 0
Reverts on inter-cluster connectivity: 0
Reverts on pre-mapping validation: 0
Reverts on split failed: 0

[info] Iterations: 4
Reverts on cluster mapping: 0
Reverts on inter-cluster connectivity: 0
Reverts on pre-mapping validation: 0
Reverts on split failed: 0
[info] +-----------+---------------------+---------------------+--------------------+
[info] | Cluster   | Control Utilization | Compute Utilization | Memory Utilization |
[info] +-----------+---------------------+---------------------+--------------------+
[info] | cluster_0 | 68.8%               | 40.6%               | 15.6%              |
[info] | cluster_1 | 81.3%               | 57.8%               | 37.5%              |
[info] | cluster_2 | 81.3%               | 96.9%               | 93%                |
[info] | cluster_3 | 50%                 | 56.3%               | 32%                |
[info] | cluster_4 | 62.5%               | 45.3%               | 29.7%              |
[info] | cluster_5 | 75%                 | 76.6%               | 98.4%              |
[info] | cluster_6 | 81.3%               | 56.3%               | 37.5%              |
[info] | cluster_7 | 100%                | 73.4%               | 38.3%              |
[info] +-----------+---------------------+---------------------+--------------------+
[info] | Total     | 75%                 | 62.9%               | 47.8%              |
[info] +-----------+---------------------+---------------------+--------------------+
[info] Successful Mapping (allocation time: 23s)
[info] Compiling context_0...
[info] Bandwidth of model inputs: 9.375 Mbps, outputs: 9.22852 Mbps (for a single frame)
[info] Bandwidth of DDR buffers: 0.0 Mbps (for a single frame)
[info] Bandwidth of inter context tensors: 0.0 Mbps (for a single frame)
[info] Building HEF...
[info] Successful Compilation (compilation time: 14s)
[info] Saved HAR to: /home/ubuntu/workspace/hailo/custom-train/data/model/yolov8n.har
<Hailo Model Zoo INFO> HEF file written to yolov8n.hef
```

## 4. 验证模型

### 4.1 使用 hailortcli 检测

在编译完成后，会生成 `.hef` 格式的模型文件，此时可以用 `hailortcli` 解析模型的信息

#### 4.1.1 安装 HailoRT 

从 [Developer Zone](https://hailo.ai/developer-zone/software-downloads/) 下载并安装 HailoRT，通过 dpkg 安装

```bash
sudo dpkg --install hailort_4.18.0_amd64.deb
```

![homelab-tpu-hailo-software-download-page.png](https://img.hellowood.dev/picture/homelab-tpu-hailo-software-download-page.png)

#### 4.1.2 检测模型信息

- 获取模型信息

```bash
hailortcli parse-hef ./yolov8n.hef
```

信息如下：

```bash
Architecture HEF was compiled for: HAILO8
Network group name: yolov8n, Single Context
    Network name: yolov8n/yolov8n
        VStream infos:
            Input  yolov8n/input_layer1 UINT8, NHWC(640x640x3)
            Output yolov8n/yolov8_nms_postprocess FLOAT32, HAILO NMS(number of classes: 80, maximum bounding boxes per class: 100, maximum frame size: 160320)
            Operation:
                Op YOLOV8
                Name: YOLOV8-Post-Process
                Score threshold: 0.200
                IoU threshold: 0.70
                Classes: 80
                Cross classes: false
                Max bboxes per class: 100
                Image height: 640
                Image width: 640
```

- 运行模型

使用 hailortcli 运行模型，查看模型性能

```bash
hailortcli run /home/ubuntu/workspace/project/hailo/model/yolov8n.hef --measure-temp
```

运行结果表明可以处理的图片帧率为 184.58 

```bash
Running streaming inference (/home/ubuntu/workspace/project/hailo/model/yolov8n.hef):
  Transform data: true
    Type:      auto
    Quantized: true
Network yolov8n/yolov8n: 100% | 924 | FPS: 184.58 | ETA: 00:00:00
> Inference result:
 Network group: yolov8n
    Frames count: 924
    FPS: 184.59
    Send Rate: 1814.58 Mbit/s
    Recv Rate: 1803.24 Mbit/s

  Device: 0000:04:00.0
    Minimum chip temperature: 35.3433C
    Average chip temperature: 38.2565C
    Maximum chip temperature: 39.289C
```

### 4.2 使用 Python 进行对象检测

使用 Hailo 提供的 Demo，使用编译后的模型进行对象检测

#### 4.2.1 下载 Demo 

```bash
git clone https://github.com/hailo-ai/Hailo-Application-Code-Examples.git
```

#### 4.2.2 运行对象检测 Demo

进入到对象检测 Demo 路径下

```bash
cd Hailo-Application-Code-Examples/runtime/python/object_detection
```

运行 Demo

```bash
python object_detection.py -n /home/ubuntu/workspace/project/hailo/model/yolov8n.hef -i ./zidane.jpg -l coco.txt
```

会提示将标注后到图片输出到指定的路径

```bash
2024-09-08 17:42:27.549 | INFO     | __main__:infer:175 - Inference was successful! Results have been saved in output_images
```

## 问题

1. FileNotFoundError: no alls found for requested hw_arch

这个错误是因为没有模型对应的 alls 文件，这个文件在 [https://github.com/hailo-ai/hailo_model_zoo/](https://github.com/hailo-ai/hailo_model_zoo/) 仓库可以找到，路径是 `hailo_model_zoo/cfg/alls`；可以直接 clone 仓库到本地，然后将文件复制到虚拟环境中

因为还依赖 `postprocess_config`目录下的 `xxx_nms_config.json` 文件，所以直接复制 `hailo_model_zoo/cfg` 目录

```bash
git clone https://github.com/hailo-ai/hailo_model_zoo.git
cd hailo_model_zoo
rm -rf /home/ubuntu/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/cfg
cp -r hailo_model_zoo/hailo_model_zoo/cfg /home/ubuntu/anaconda3/envs/hailo/lib/python3.10/site-packages/hailo_model_zoo/cfg
```

2. 安装 pygraphviz 失败，提示 `fatal error: graphviz/cgraph.h: 没有那个文件或目录`

改用 conda 安装: `conda install pygraphviz` 即可

```bash
      gcc -pthread -B /home/ubuntu/anaconda3/envs/hailo-zoo/compiler_compat -Wno-unused-result -Wsign-compare -DNDEBUG -fwrapv -O2 -Wall -fPIC -O2 -isystem /home/ubuntu/anaconda3/envs/hailo-zoo/include -fPIC -O2 -isystem /home/ubuntu/anaconda3/envs/hailo-zoo/include -fPIC -DSWIG_PYTHON_STRICT_BYTE_CHAR -I/home/ubuntu/anaconda3/envs/hailo-zoo/include/python3.10 -c pygraphviz/graphviz_wrap.c -o build/temp.linux-x86_64-cpython-310/pygraphviz/graphviz_wrap.o
      pygraphviz/graphviz_wrap.c:9: warning: "SWIG_PYTHON_STRICT_BYTE_CHAR" redefined
          9 | #define SWIG_PYTHON_STRICT_BYTE_CHAR
            |
      <command-line>: note: this is the location of the previous definition
      pygraphviz/graphviz_wrap.c:3023:10: fatal error: graphviz/cgraph.h: 没有那个文件或目录
       3023 | #include "graphviz/cgraph.h"
            |          ^~~~~~~~~~~~~~~~~~~
      compilation terminated.
      error: command '/usr/bin/gcc' failed with exit code 1
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for pygraphviz
Failed to build pygraphviz
ERROR: ERROR: Failed to build installable wheels for some pyproject.toml based projects (pygraphviz)
```

3. FileNotFoundError: Couldn't find dataset in /home/ubuntu/.hailomz/data/models_files/coco/2021-06-18/coco_calib2017.tfrecord

通过 创建的 tfrecord 的路径可能和实际不一样，如要求的路径是 `~/.hailomz/data/models_files/coco/2021-06-18/coco_calib2017.tfrecord`，实际的路径是 `~/.hailomz/data/models_files/coco/2023-08-03/coco_calib2017.tfrecord`，通过指定 `clibpath` 参数即可:

```bash
hailomz optimize --hw-arch hailo8l --har ./yolov8n.har yolov8n --calib-path ~/.hailomz/data/models_files/coco/2023-08-03/coco_calib2017.tfrecord
```