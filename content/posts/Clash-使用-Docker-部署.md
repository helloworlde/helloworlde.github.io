---
description: "Clash Docker 部署指南：包含订阅格式转换、subconverter 配置及 Clash Premium 监控开启方法"
title: Clash 使用 Docker 部署
type: post
date: 2022-10-26T11:20:19+08:00
lastmod: 2025-09-06
tags:
  - Clash
  - Docker
  - HomeLab
featured: true
---

使用 Clash Premium 版本请参考 [使用 Docker 部署 Clash Premium](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8docker%E9%83%A8%E7%BD%B2clash-premium/)

在一些场景下无法使用 Clash 客户端进行代理，也无法使用软路由，这时候可以由一台服务器运行 Clash，作为其他客户端的代理；同时 Clash 支持以 Docker 容器的方式运行，方便部署和运维

## 订阅格式转换

机场提供的订阅可能无法被 Clash 直接使用，或者分流配置不合理，需要转换格式；可以使用在线的订阅转换工具，如 [https://acl4ssr-sub.github.io/](https://acl4ssr-sub.github.io/)等，也可以使用开源的服务自行搭建；

为了安全和隐私，可以基于 [https://github.com/CareyWang/sub-web](https://github.com/CareyWang/sub-web) 和 [https://github.com/tindy2013/subconverter](https://github.com/tindy2013/subconverter) 服务搭建，分别是前端和后端服务

- docker-compose.yaml

```yaml
version: "3"

services:
  subweb:
    image: careywong/subweb
    container_name: subweb
    hostname: subweb
    restart: unless-stopped
    ports:
      - 18080:80
    environment:
      - TZ=Asia/Shanghai

  subconverter:
    image: tindy2013/subconverter
    container_name: subconverter
    hostname: subconverter
    restart: unless-stopped
    ports:
      - 25500:25500
    environment:
      - TZ=Asia/Shanghai
```

部署完成后，选择进阶模式，填写后端地址为 subconverter 容器的地址；选择远程配置（推荐 Ytoo/NyanCAT，配置更全面），然后填入订阅链接生成即可得到新的订阅链接

![homelab-clash-proxy-config-convert-to-clash.png](https://img.hellowood.dev/picture/homelab-clash-proxy-config-convert-to-clash.png)

- 自定义配置

如果有自定义配置，可以指定远程配置，参考[外部配置](https://github.com/tindy2013/subconverter/blob/master/README-cn.md#%E5%A4%96%E9%83%A8%E9%85%8D%E7%BD%AE)，指定 `clash_rule_base` 配置模板；不过该方式比较麻烦，自己使用可以直接通过更改 subconverter 默认配置的方式实现；

subconverter 默认的配置是 `/base/pref.toml`文件，其中指定了 clash 的配置文件模板为 `clash_rule_base = "base/all_base.tpl"`，所以修改 `base/all_base.tpl` 文件即可

为了监控 Clash Premium，需要开启 tracing，所以向配置文件 `base/all_base.tpl` 中直接加入相关配置：

```
{% if request.target == "clash" or request.target == "clashr" %}
# 以下是新增内容
profile:
  tracing: true

# ...
{% endif %}
```

随后，将该配置文件复制到宿主机上，通过挂载文件的方式添加到 subconverter 容器，避免容器重启后丢失

```yaml
services:
  subconverter:
    image: tindy2013/subconverter
    # ...
    volumes:
      - ./config/all_base.tpl://base/base/all_base.tpl
```

## 配置文件

在订阅格式转换完成后，就可以通过生成的订阅链接获取配置，这个配置可以直接使用；如果不满足需求可以基于该配置手动修改，配置内容格式如下：

```yaml
# 开启监控
profile:
  tracing: true
port: 7890
socks-port: 7891
#转发端口一定要配置
redir-port: 7892
#允许接管局域网流量
allow-lan: true
#默认代理模式
mode: Rule
log-level: debug
#接口控制端口是9090
external-controller: :9090
#如果服务器对公网开放可以设置密码
secret: ""
#配置由clash接管的dns解析
dns:
  enable: true
  #主要监听定向转发来的数据，后续会在路由表里配置转发端口为1053
  listen: 0.0.0.0:1053
  enhanced-mode: fake-ip
  nameserver:
    - "114.114.114.114"
    - "223.5.5.5"
  fallback:
    - "tls://1.1.1.1:853"
    - "tcp://1.1.1.1:53"
    - "tcp://208.67.222.222:443"
    - "tls://dns.google"

# 代理节点
proxies:
  - {
      name: node1,
      server: 0.0.0.0,
      port: 5601,
      type: ss,
      cipher: aes-256-gcm,
      password: 1234,
      udp: true,
    }

# 代理组
proxy-groups:
  - {
      name: "🚀 节点选择",
      type: select,
      proxies: ["♻️ 自动选择", "🚀 手动切换", DIRECT],
    }

# 分流规则
rules:
  - "DOMAIN-SUFFIX,local,🎯 全球直连"
  - "DOMAIN-SUFFIX,localhost,🎯 全球直连"
  - "IP-CIDR,10.0.0.0/8,🎯 全球直连,no-resolve"
```

## 部署

Clash 有两个版本，一个是 clash，一个是 clash-premium，区别在于 premium 是非开源的，支持数据统计，支持 fake-ip 模式（能够减少一次 DNS 查询），支持订阅

yacd 是一个开源的 Clash 控制面板，功能较丰富

- Docker 命令运行

```bash
docker run --name clash \
	 -d \
	 -v config.yaml:/root/.config/clash/config.yaml \
	 -p 7890:7890 \
	 -p 7891:7891 \
	 -p 9090:9090 \
	 dreamacro/clash-premium

docker run --name yacd \
	-d  \
	-p 80:80 \
	ghcr.io/haishanh/yacd:master
```

![homelab-clash-proxy-yacd-ui.png](https://img.hellowood.dev/picture/homelab-clash-proxy-yacd-ui.png)

- docker-compose 方式运行

```yaml
version: "3"

services:
  clash:
    image: dreamacro/clash-premium
    container_name: clash
    hostname: clash
    restart: unless-stopped
    ports:
      - 7890:7890
      - 7891:7891
      - 9090:9090
    volumes:
      - ./config.yaml:/root/.config/clash/config.yaml
    environment:
      - TZ=Asia/Shanghai

  yacd:
    image: ghcr.io/haishanh/yacd:master
    container_name: yacd
    hostname: yacd
    restart: unless-stopped
    ports:
      - 80:80
    environment:
      - TZ=Asia/Shanghai
    depends_on:
      - clash
```

## 客户端使用

通过容器方式部署的 Clash 可以以代理的方式使用，在手机/电脑或者应用程序中配置代理即可

### 命令行

开启代理

```bash
export https_proxy=http://192.168.2.2:7890
export http_proxy=http://192.168.2.2:7890
export all_proxy=socks5://192.168.2.2:7891
```

关闭代理

```bash
unset http_proxy
unset https_proxy
unset all_proxy
```

### 系统

在网络-代理中添加配置，指定 HTTP/HTTPS/SOCKS 代理为配置的代理即可

![homelab-clash-proxy-config-macos.png](https://img.hellowood.dev/picture/homelab-clash-proxy-config-macos.png)
