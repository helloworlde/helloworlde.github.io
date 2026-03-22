---
date: 2026-03-16T08:52:57+08:00
description: "Xray-core VLESS Reality Vision 自建代理 Docker 部署教程，含 UUID 私钥配置及 ClashX Meta 使用指南，解决双重加密识别问题"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
tags:
  - Proxy
  - HomeLab
  - OpenWrt
title: "使用 VLESS Reality Vision 协议在 VPS 服务器自建代理"
type: "post"
---

VLESS Reality Vision 是目前 Xray-core 中最推荐的代理组合方案，三个组件各司其职：

- VLESS 负责代理协议层，用 UUID 认证用户身份并转发流量，设计极简，本身不做加密
- Reality 负责传输安全层，代替传统 TLS。核心思路是：握手时伪装成访问真实网站（如 www.bing.com）的正常 TLS 连接，认证通过后才接管流量，否则直接转发给真实网站。外部观察者看到的是一条普通的 HTTPS 请求，无法区分。服务端不需要域名和证书，用公私钥对做认证
- Vision 负责流控优化层，解决"TLS in TLS"问题。代理流量本身是 TLS 加密的，外面再套一层 Reality（也是 TLS），会形成双重加密的流量特征，容易被识别。Vision 在检测到内层 TLS 握手完成后，自动剥离外层加密直接传输，消除双重特征的同时也提升了性能

三者组合在一起的效果：从外部网络看，代理流量与普通用户访问网站的 HTTPS 请求完全一致，既难以识别，也难以封锁

使用 docker 搭建 VLESS Reality Vision 代理服务，并在 ClashX Meta 和 Dae 客户端中使用；作为 UDP 协议被阻塞时作为 hysteria2 的备用方案

## 服务端搭建 VLESS Reality Vision 代理服务

- 生成 uuid

```bash
docker run --rm ghcr.io/xtls/xray-core:latest uuid
```

将会生成一个 UUID，需要添加到配置中

```bash
9a1c99b3-cd96-4b10-b8e0-b8b68c936743
```

- 生成私钥/公钥

```bash
docker run --rm ghcr.io/xtls/xray-core:latest x25519
```

将会生成一个私钥和密码，私钥用于服务端，密码用于客户端

```bash
PrivateKey: kD-jITzOOSkI5ObIuz_5PNNxHZw_fwUV_hZLFlnBJ1w
Password: yvTDx4mhHdfxxO01S2xCVqg73JrER6mOUi7yD-gcvw4
Hash32: Fl9CapDasJopM9u9Y549B5eZlX-lZr-HNtKr_rafhzY
```

- 编辑配置文件

文件路径是 `config/config.json`

```json
{
  "log": {
    "loglevel": "debug"
  },
  "inbounds": [
    {
      "port": 7443, // 监听端口 需要开放防火墙端口
      "protocol": "vless",
      "settings": {
        "clients": [
          // 如果有多个 client, 可以配置多个
          {
            "id": "9a1c99b3-cd96-4b10-b8e0-b8b68c936743", // 填入刚才生成的 UUID
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.bing.com:443", // 目标网站, 格式：域名:端口
          "xver": 0,
          "serverNames": [
            "www.bing.com" // 目标网站域名
          ],
          "privateKey": "kD-jITzOOSkI5ObIuz_5PNNxHZw_fwUV_hZLFlnBJ1w", // 填入刚才生成的 Private Key
          "shortIds": [
            "1234567890abcdef" // 随机生成的 shortId，8-16位16进制字符串, 可以通过 openssl rand -hex 16 生成
          ]
        }
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom"
    }
  ]
}
```

- 启动 Reality

通过 docker-compose 启动

```yaml
services:
  xray:
    image: ghcr.io/xtls/xray-core:latest
    container_name: xray
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./config:/usr/local/etc/xray # 存放配置文件
      - ./dat:/usr/local/share/xray # 存放 geoip/geosite 等路由规则数据文件
    environment:
      - TZ=Asia/Shanghai
```

通过 `docker compose up -d` 启动，查看日志，启动成功后会输出类似如下日志：

```bash
xray  | Xray 26.2.6 (Xray, Penetrates Everything.) Custom (go1.25.7 linux/amd64)
xray  | A unified platform for anti-censorship.
xray  | 2026/03/18 09:12:05.696721 Using confdir from arg: /usr/local/etc/xray/
xray  | 2026/03/18 09:12:05.702068 [Info] infra/conf/serial: Reading config: &{Name:/usr/local/etc/xray/config.json Format:json}
xray  | 2026/03/18 09:12:05.712070 [Debug] app/log: Logger started
xray  | 2026/03/18 09:12:05.712176 [Debug] app/proxyman/inbound: creating stream worker on 0.0.0.0:443
xray  | 2026/03/18 09:12:05.712221 [Info] transport/internet/tcp: listening TCP on 0.0.0.0:443
xray  | 2026/03/18 09:12:05.712226 [Warning] core: Xray 26.2.6 started
```

## 客户端配置

### ClashX Meta

通过 proxy-providers 方式配置，详细可以参考 [使用 Docker 部署 Clash Premium](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8docker%E9%83%A8%E7%BD%B2clash-premium/)

- xtls.yaml

将配置文件放到 GitHub [Gist](https://gist.github.com/) 中，通过远程订阅的方式获取

```yaml
proxies:
  - name: xtls-node
    type: vless
    server: xxxx
    port: 443
    uuid: 9a1c99b3-cd96-4b10-b8e0-b8b68c936743
    network: tcp
    udp: true
    tls: true
    skip-cert-verify: true
    flow: xtls-rprx-vision
    client-fingerprint: chrome
    servername: www.bing.com
    reality-opts:
      public-key: kD-jITzOOSkI5ObIuz_5PNNxHZw_fwUV_hZLFlnBJ1w
      short-id: 1234567890abcdef
```

- config.yaml

将配置文件添加到 proxy-providers 中，通过 http 方式获取

```yaml
# 配置文件地址，参考 https://wiki.metacubex.one/config/proxy-providers/
proxy-providers:
  proxy:
    type: http
    url: "https://raw.githubusercontent.com/xxx/raw/xxx/xtls.yaml"
    interval: 3600
    path: ./node/xtls.yaml
    health-check:
      enable: true
      interval: 300
      url: http://www.gstatic.com/generate_204

proxy-groups:
  - name: "PROXY"
    type: url-test
    use:
      - proxy # 上面的 proxy-providers 中的 proxy 名称
    url: "http://www.gstatic.com/generate_204"
    interval: 180

rules:
  - RULE-SET,google,PROXY # 使用名称 google 的规则集，PROXY 策略组
```

这样就配置好了，可以添加到 ClashX Meta 中，更新配置后就可以生效

### dae 代理配置

关于 dae 的配置和使用，可以参考 [Dae 代理软件的配置](https://blog.hellowood.dev/posts/dae-%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E7%9A%84%E9%85%8D%E7%BD%AE/)， [OpenWrt 安装使用 Dae 作为代理](https://blog.hellowood.dev/posts/openwrt-%E5%AE%89%E8%A3%85%E4%BD%BF%E7%94%A8-dae-%E4%BD%9C%E4%B8%BA%E4%BB%A3%E7%90%86/)

- config.dae

需要注意，uuid/public-key/short-id/servername 等配置均需要与服务端配置一致，否则无法连接

在 node 中添加 xtls-node 节点，格式为 `vless://uuid@server:port?encryption=none&flow=xtls-rprx-vision&security=reality&sni=servername&fp=chrome&pbk=public-key&sid=short-id&type=tcp`

```
node {
    xtls-node: 'vless://9a1c99b3-cd96-4b10-b8e0-b8b68c936743@xxxx:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.bing.com&fp=chrome&pbk=kD-jITzOOSkI5ObIuz_5PNNxHZw_fwUV_hZLFlnBJ1w&sid=1234567890abcdef&type=tcp'
}
```

添加完成后重启 dae 即可

## 参考文档

- [代理集合](https://wiki.metacubex.one/config/proxy-providers/)
- [VLESS](https://wiki.metacubex.one/config/proxies/vless/)
- [REALITY](https://github.com/XTLS/REALITY)
- [Xray-core](https://github.com/XTLS/Xray-core)
