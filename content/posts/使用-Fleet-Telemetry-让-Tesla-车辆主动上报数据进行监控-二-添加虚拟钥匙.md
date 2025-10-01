---
date: 2025-09-25
# description: ""
# image: ""
lastmod: 2025-10-01
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙"
type: "post"
---

让 Tesla 主动上报数据到 Fleet Telemetry，需要将网站的公钥作为虚拟钥匙添加到车机中；需要通过 API 下发配置，因此需要创建一个开发者账号，详细操作可以参考 [什么是 Fleet API](https://developer.tesla.cn/docs/fleet-api/getting-started/what-is-fleet-api)

## 一、申请开发者账号和应用

创建开发者账号需要 [Tesla 账号](https://www.tesla.cn/teslaaccount/profile-settings)设置中绑定邮箱，并且开启两步验证；然后访问 [Tesla Developer](https://developer.tesla.cn/zh_CN/dashboard) 创建应用，输入应用名称和说明等信息

![homelab-tesla-fleet-telemetry-create-application-1.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-create-application-1.png)

OAuth 授权类型选择 "授权码和机器对机器"，然后添加允许的源 URL、重定向 URL 和返回的 URL，这里的 URL 需要和后面部署的 Fleet Telemetry 服务器地址一致

![homelab-tesla-fleet-telemetry-create-application-2.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-create-application-2.png)

选择权限范围，可以直接选择所有的权限

![homelab-tesla-fleet-telemetry-create-application-3.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-create-application-3.png)

创建成功后会得到 Client ID 和 Client Secret，需要保存下来，后续获取 Token 需要使用

## 二、生成公钥/私钥对

需要生成一个公钥/私钥对，公钥需要托管在网站上让特斯拉访问，用于验证域名所有权；私钥用于通过 tesla-http-proxy 向车辆发送配置指令

- 生成私钥

```bash
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem
```

- 生成公钥

```bash
openssl ec -in private-key.pem -pubout -out public-key.pem
```

## 三、托管公钥

然后需要将公钥托管在网站的 `/.well-known/appspecific/` 路径下，确保可以通过 `https://fleet.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem` 访问到公钥文件；可以使用 Caddy 进行托管，关于 Caddy 的配置可以参考 [阿里云服务器使用 Caddy 和 ZeroSSL 提供的 IP 证书为服务开启 HTTPS](https://blog.hellowood.dev/posts/%E9%98%BF%E9%87%8C%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BD%BF%E7%94%A8caddy-%E5%92%8C-zerossl-%E6%8F%90%E4%BE%9B%E7%9A%84-ip-%E8%AF%81%E4%B9%A6%E4%B8%BA%E6%9C%8D%E5%8A%A1%E5%BC%80%E5%90%AF-https/)

需要将 `public-key.pem` 文件复制到 `static/com.tesla.3p.public-key.pem`，然后挂载到 Caddy 的 `/var/www/html/.well-known/appspecific/` 目录下

- docker-compose.yaml

```yaml
services:
  caddy:
    image: caddy
    container_name: caddy
    hostname: caddy
    ports:
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./certs:/certs # Certbot 生成的证书
      - ./static:/var/www/html/.well-known/appspecific/:ro # 用于托管公钥
    restart: unless-stopped
```

- Caddyfile

创建 `Caddyfile` 文件，内容如下：

```conf
fleet.example.com {
    # 这里的证书就是 Certbot 申请的证书
    tls /certs/fullchain.pem /certs/privkey.pem

    # 挂载的目录
    root * /var/www/html

    route {
        # 处理特定文件
        handle /.well-known/appspecific/* {
            file_server
        }
    }
}
```

完整的目录结构如下：

```bash
.
├── Caddyfile
├── certs
│   ├── fullchain.pem
│   └── privkey.pem
├── docker-compose.yaml
└── static
    └── com.tesla.3p.public-key.pem
```

启动容器，然后通过浏览器访问 `https://fleet.example.com/.well-known/appspecific/com.tesla.3p.public-key.pem`，可以下载到公钥说明托管成功

## 四、虚拟密钥添加到车辆

当公钥托管成功之后，就可以访问 `https://www.tesla.com/_ak/fleet.example.com`，将虚拟密钥添加到车辆，用于后续访问车辆信息、通信等；访问该链接后，通过页面打开 Tesla App，然后选择对应的车辆，添加虚拟钥匙；添加成功后，车辆的钥匙中会出现 `fleet.example.com` 虚拟钥匙

![homelab-tesla-fleet-telemetry-add-virtual-key.svg](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-add-virtual-key.svg)

## 参考文档

- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(一)申请证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%80-%E7%94%B3%E8%AF%B7%E8%AF%81%E4%B9%A6/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%8C-%E6%B7%BB%E5%8A%A0%E8%99%9A%E6%8B%9F%E9%92%A5%E5%8C%99/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%89-%E9%83%A8%E7%BD%B2%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%9B%9B-%E4%B8%8B%E5%8F%91%E9%85%8D%E7%BD%AE/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%94-%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%85%AD-%E7%9B%91%E6%8E%A7%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%83-%E5%AE%8C%E6%95%B4%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E/)
