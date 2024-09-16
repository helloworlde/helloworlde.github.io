---
title: "Docker 开启外部 HTTP 访问"
type: post
date: 2023-03-05T21:39:29+08:00
tags:
  - Docker
categories:
  - Docker
featured: true
---

在监控容器时，通常需要从 Docker 中获取容器的信息，如果监控服务和其他的服务在同一台宿主机上，通常可以直接通过挂载 socket 的方式进行获取；但是为了监控的准确性，通常会将监控服务和其他服务分开部署，因此需要从外部获取 Docker 容器信息；

Docker 除了支持 socket 方式之外，还支持通过 HTTP 的方式获取容器的信息

## 开启 HTTP 访问

HTTP 访问是通过在启动 Docker 服务的时候添加参数的方式开启的；需要在 docker service 的启动命令中添加 `-H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock`，即允许通过 HTTP 方式和 socket 方式访问

### 配置启动参数

该文件是 docker 服务的定义文件

```bash
vi /usr/lib/systemd/system/docker.service
```

在 Service 的 `ExecStart` 命令中添加 `-H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock`

```bash
[Service]
Type=notify
# the default is not to use systemd for cgroups because the delegate issues still
# exists and systemd currently does not support the cgroup feature set required
# for containers run by docker
ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock -H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStartSec=0
RestartSec=2
Restart=always
```

### 重启 Docker 服务

```bash
systemctl daemon-reload
systemctl restart docker
```

### 检查端口

通过 telnet 命令检查 2375 端口，可以访问说明端口正常

```bash
telnet localhost 2375
Trying ::1...
Connected to localhost.
Escape character is '^]'.
```

### 开启防火墙

在外部访问时还需要开启防火墙，将 2375 端口添加到放行名单中即可；添加后在外部通过 telnet 检查也可以访问说明配置成功了

```bash
firewall-cmd --zone=public --add-port=2375/tcp --permanent
```
