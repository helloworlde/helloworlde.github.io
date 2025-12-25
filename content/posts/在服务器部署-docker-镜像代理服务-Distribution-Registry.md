---
date: 2025-12-09
# description: ""
# image: ""
lastmod: 2025-12-09
showTableOfContents: false
tags:
  - Docker
  - HomeLab
featured: true
title: "在服务器部署 Docker 镜像代理服务 Distribution Registry"
type: "post"
---

使用 Docker 部署服务的时候，Docker 官方镜像时常拉取失败，第三方的镜像仓库同样不稳定，在多次遇到问题后最终选择在海外的 VPS 上自己搭建 Docker 镜像代理服务，提升拉取镜像的成功率和速度

镜像代理使用 CNCF 的 [Distribution Registry](https://distribution.github.io/distribution/about/) 项目搭建，使用 Docker Compose 进行部署

## 部署 Distribution Registry

一个 Distribution Registry 只能代理一个上游镜像仓库，这里以代理 Docker 官方镜像仓库为例，如果要代理其他仓库，则需要在配置中指定对应的上游后启动多个实例

### 配置

- config.yml

```yaml
version: 0.1
storage:
  cache:
    blobdescriptor: inmemory # blob 描述信息缓存到内存
  filesystem:
    rootdirectory: /var/lib/registry # layer/manifest 等数据存储路径
http:
  addr: 0.0.0.0:5000 # 监听地址和端口
proxy:
  remoteurl: https://registry-1.docker.io # 代理的上游镜像仓库地址
  username: username # 如果上游仓库需要认证，可以在这里配置用户名和密码
  password: password
```

### 部署

- docker-compose.yml

需要将 config.yml 挂载到容器的 `/etc/docker/registry/config.yml` 路径下

```yaml
services:
  docker-registry:
    image: registry:2
    container_name: docker-registry
    restart: always
    volumes:
      - "/etc/localtime:/etc/localtime"
      - "./data:/var/lib/registry"
      - "./config.yml:/etc/docker/registry/config.yml"
    ports:
      - "5000:5000"
    environment:
      - REGISTRY_LOG_LEVEL=warn
      - OTEL_TRACES_EXPORTER=none
```

### 验证镜像仓库

启动服务后，通过 Traefix/Nginx/Caddy 等反向代理将 5000 端口映射到域名或 IP 地址上，然后拉取镜像进行验证，如域名是 `docker.example.com`，则执行如下命令（docker 的一些公共镜像需要添加 `library` 名称）

```bash
docker pull docker.example.com/library/nginx:latest
latest: Pulling from library/nginx
1733a4cd5954: Pull complete
5b219a92f92a: Pull complete
ee3a09d2248a: Pull complete
7382b41547b8: Pull complete
9ee60c6c0558: Pull complete
114e699da838: Pull complete
5b5fa0b64d74: Pull complete
Digest: sha256:fb01117203ff38c2f9af91db1a7409459182a37c87cced5cb442d1d8fcc66d19
Status: Downloaded newer image for docker.example.com/library/nginx:latest
docker.example.com/library/nginx:latest
```

registry 的日志如下：

```shell
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:38 +0800] "GET /v2/ HTTP/1.1" 200 2 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:38 +0800] "HEAD /v2/library/nginx/manifests/latest HTTP/1.1" 200 10229 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:39 +0800] "GET /v2/library/nginx/manifests/sha256:fb01117203ff38c2f9af91db1a7409459182a37c87cced5cb442d1d8fcc66d19 HTTP/1.1" 200 10229 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:39 +0800] "GET /v2/library/nginx/manifests/sha256:547c8c6863a88abd0c987779413489ff0e9a693c24d2d88ce9eb8515e0ae0335 HTTP/1.1" 200 2290 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:40 +0800] "GET /v2/library/nginx/blobs/sha256:ee3a09d2248a2df379f9868e31e578994110589e1f118a98396aeebcc9316b8d HTTP/1.1" 200 628 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:40 +0800] "GET /v2/library/nginx/blobs/sha256:576306625d797a52045ad158b601d5a011f7a7f16e4ccc909809f02dd6047c37 HTTP/1.1" 200 8734 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:41 +0800] "GET /v2/library/nginx/blobs/sha256:7382b41547b8efa59d4103ac9610d7e359eb989e675faf7e0d3e7445496bba94 HTTP/1.1" 200 953 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:42 +0800] "GET /v2/library/nginx/blobs/sha256:9ee60c6c0558552ff0a2548f4b6941e4aa276937fb1cd8c76a94e73fe75d69ba HTTP/1.1" 200 402 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:40 +0800] "GET /v2/library/nginx/blobs/sha256:5b219a92f92aeb674b0b29811b447d120ce69b41d21cfca56f90ad323aff91a2 HTTP/1.1" 200 29992957 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:40 +0800] "GET /v2/library/nginx/blobs/sha256:1733a4cd59540b3470ff7a90963bcdea5b543279dd6bdaf022d7883fdad221e5 HTTP/1.1" 200 29776496 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:43 +0800] "GET /v2/library/nginx/blobs/sha256:114e699da838b7a4a5dd75807233341d8f9a392ee2360d4bfe2b0680df4965f8 HTTP/1.1" 200 1207 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
docker-registry  | 172.20.0.7 - - [23/Dec/2025:09:19:43 +0800] "GET /v2/library/nginx/blobs/sha256:5b5fa0b64d74b2ce9915f89c1be1b98a3400a7ca4fb4654cec353db54342c2a9 HTTP/1.1" 200 1397 "" "docker/29.1.3 go/go1.25.5 git-commit/fbf3ed2 kernel/6.8.0-87-generic os/linux arch/amd64 UpstreamClient(Docker-Client/29.1.3 \\(linux\\))"
```

## Docker 配置 mirror

在 `/etc/docker/daemon.json` 中添加如下内容

```json
{
  "registry-mirrors": ["https://docker.example.com"]
}
```

如果不能提供 HTTPS 服务，可以使用如下配置忽略证书验证（不推荐）

```json
{
  "insecure-registries": ["docker.example.com:5000"]
}
```

然后重启 Docker 服务

```bash
systemctl daemon-reload
systemctl restart docker
```

## 参考文档

- [Configuring a registry](https://distribution.github.io/distribution/about/configuration/)
