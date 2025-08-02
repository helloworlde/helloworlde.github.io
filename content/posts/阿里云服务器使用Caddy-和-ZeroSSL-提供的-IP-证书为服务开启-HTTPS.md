---
date: 2025-07-31
# description: ""
# image: ""
lastmod: 2025-07-31
showTableOfContents: false
tags:
  - HomeLab
  - Caddy
  - Cert
featured: true
type: post
title: "阿里云服务器使用 Caddy 和 ZeroSSL 提供的 IP 证书为服务开启 HTTPS"
---

国内购买的服务器在没有域名备案的情况下通过域名请求会被拦截，只能通过 IP 访问，但是一些服务如 DoH 等必须通过可信的 HTTPS 访问，刚好 ZeroSSL 支持为 IP 申请证书，这样就可以直接使用 IP 安全访问云主机里部署服务

为了方便管理和访问，使用 Caddy 作为反向代理，将所有请求都通过 Caddy 处理，这样只需要在 Caddy 配置一次可信的 HTTPS 证书即可；关于 Caddy 的使用可以参考 [使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)

假设公网 IPv4 地址为 `100.0.0.1`，使用这个 IP 申请证书和配置 Caddy；申请证书时需要通过 80 端口进行验证，所以需要 80 和 443 端口在公网可以访问

## 启动 Caddy

ZeroSSL 需要访问 `http://100.0.0.1/.well-known/pki-validation/xxx.txt` 路径进行验证，xxx.txt 是在申请证书时生成的，所以需要在 Caddy 中配置这个路径

- 认证文件

将 xxx.txt 放到 `static` 目录下，为了方便直接将 `static` 目录映射到 Caddy 容器的 `/var/www/html/.well-known/pki-validation`，文件目录如下：

```bash
├── Caddyfile
├── docker-compose.yaml
└── static
    └── xxx.txt
```

- Caddyfile

```conf
{
    log {
        output stdout
        format console
        level info
    }
}

http://100.0.0.1:80 {
   root * /var/www/html
   file_server
}

https://100.0.0.1:443 {
    respond "https"
}
```

- docker-compose.yml

```yaml
services:
  caddy:
    image: caddy
    container_name: caddy
    ports:
      - "80:80" #http
      - "443:443" # https
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./static:/var/www/html/.well-known/pki-validation # 认证文件
      - ./certs:/certs # TLS 证书
    restart: unless-stopped
```

通过 `docker compose up` 启动

## 申请 ZeroSSL 证书

如何申请 ZeroSSL 的证书可以参考官方文档 [Creating an SSL Certificate](https://help.zerossl.com/hc/en-us/articles/360060119373-Creating-an-SSL-Certificate)，有非常详细的步骤

![Appply Cert](https://help.zerossl.com/hc/article_attachments/360100919013/5fc511d381350.png)

IP 证书只能使用文件的方式认证，参考 [Method 3: HTTP File Upload](https://help.zerossl.com/hc/en-us/articles/360058295354-Verify-Domains-for-an-SSL-Certificate) ；这里需要将 Caddy 挂载的文件改成对应的名称，如图中的 AAAXXXX.txt，添加到容器中进行认证

![Verify](https://help.zerossl.com/hc/article_attachments/360100919293)

## 配置 SSL 证书

证书申请完成后，选择 Nginx 格式下载到本地解压，有以下文件：

- ca_bundle.crt：中间证书链，连接服务器证书和受信任的根证书，确保客户端能建立完整信任链
- certificate.crt：服务器证书，标识域名，是 ZeroSSL 颁发的正式证书，用于客户端验证身份
- private.key：私钥，用于 TLS 握手中的加密/签名，必须和证书匹配，必须保密

```bash
.
├── ca_bundle.crt
├── certificate.crt
└── private.key
```

### 合并证书

将服务器证书与中间证书链拼接为完整证书链（fullchain），以供 Web 服务器（如 Nginx、Apache、Caddy 等）等正确使用，否则会提示 `TLS handshake error from 100.0.0.1:443: local error: tls: bad record MAC` 错误

```bash
cat certificate.crt ca_bundle.crt > fullchain.crt
```

### 为 Caddy 配置证书

修改 Caddyfile，为 HTTPS 请求指定证书路径

- Caddyfile

```conf
{
    debug
    log {
        output stdout
        format console
    }
    # 声明默认的 SNI，避免 SNI 识别不正确
    default_sni 100.0.0.1
}

https://100.0.0.1:443 {
    tls /certs/fullchain.crt /certs/private.key

    # 配置路由
    route /whoami {
        reverse_proxy http://localhost:8081
    }
}
```

重启 Caddy 使路由生效，这样就可以直接通过 IP 访问 HTTPS 服务了
