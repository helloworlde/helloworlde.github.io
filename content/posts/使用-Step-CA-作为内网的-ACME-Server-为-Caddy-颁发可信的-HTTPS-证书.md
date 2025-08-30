---
date: 2025-08-16
# description: ""
# image: ""
lastmod: 2025-08-16
showTableOfContents: false
tags:
  - HomeLab
  - Caddy
  - Cert
featured: true
title: "使用 Step CA 作为内网的 ACME Server 为 Caddy 颁发可信的 HTTPS 证书"
type: "post"
---

有一些服务如用于登录的 PocketId 等需要使用 HTTPS 进行访问，但是 Caddy 生成的证书是自签名的，访问时会提示不受信任；因此需要使用一个可信的 CA 来颁发证书；这里使用 [Step CA](https://smallstep.com/docs/platform/) 作为 ACME Server，为 Caddy 颁发可信的 HTTPS 证书

## 部署 Step CA

### 使用 Docker 部署 Step CA

- 创建挂载目录

需要注意的是，CA 证书的根证书和中间证书一旦生成就不能更改，否则会影响到所有使用该 CA 颁发的证书，因此一定要挂载到一个持久化的目录下安全保存

```bash
mkdir -p data/config data/certs data/secrets data/db
```

- 修改目录权限

Step CA 默认使用 UID 1000 的用户运行，因此需要将挂载目录的权限修改为 1000:1000，避免 Step CA 因权限问题无法写入证书和配置文件

```bash
sudo chown -R 1000:1000 data/config data/certs data/secrets data/db
```

- docker-compose.yml

```yaml
services:
  step-ca:
    image: smallstep/step-ca:latest
    container_name: step-ca
    restart: always
    user: 1000:1000
    ports:
      - "9000:9000"
    volumes:
      - ./data/config:/home/step/config:rw
      - ./data/certs:/home/step/certs:rw
      - ./data/secrets:/home/step/secrets:rw
      - ./data/db:/home/step/db:rw
    environment:
      - DOCKER_STEPCA_INIT_NAME=Homelab Internal CA
      - DOCKER_STEPCA_INIT_DNS_NAMES=ca.svc.homelab,*.svc.homelab,localhost
      - DOCKER_STEPCA_INIT_REMOTE_MANAGEMENT=true
      - DOCKER_STEPCA_INIT_ADMIN_SUBJECT=hellowood
      - DOCKER_STEPCA_INIT_PASSWORD=123456
      - DOCKER_STEPCA_INIT_ACME=true
```

目录说明：
| 容器路径 | 作用 |
|----------|------|
| `/home/step/config` | 存放 CA 配置文件（`ca.json` 等），控制 CA 的行为和 provisioner 配置 |
| `/home/step/certs` | 存放 CA 根证书、颁发的证书以及中间证书等 |
| `/home/step/secrets` | 存放 CA 私钥、管理员 JWK 私钥等敏感信息 |
| `/home/step/db` | 存放数据库文件，用于持久化证书、账户、provisioner 等状态信息 |

环境变量如下：

| 变量                                   | 作用                                                                                                      |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `DOCKER_STEPCA_INIT_NAME`              | CA 名称，写入根证书的 Organization 字段                                                                   |
| `DOCKER_STEPCA_INIT_DNS_NAMES`         | CA 根证书的有效域名列表                                                                                   |
| `DOCKER_STEPCA_INIT_REMOTE_MANAGEMENT` | 是否启用远程管理，允许 step-cli 在容器外通过 admin JWK 对 CA 进行管理操作，如添加 provisioner、管理证书等 |
| `DOCKER_STEPCA_INIT_ADMIN_SUBJECT`     | 超级管理员账号名，用于执行管理命令的用户                                                                  |
| `DOCKER_STEPCA_INIT_PASSWORD`          | 超级管理员密码，用于解锁 admin JWK                                                                        |
| `DOCKER_STEPCA_INIT_ACME`              | 是否初始化 ACME provisioner，允许 ACME 客户端（如 Caddy、Traefik）申请证书                                |

- 启动 Step CA

```bash
docker compose up -d
```

可以看到自动生成了根证书和中间证书，相关日志如下：

```bash
step-ca  |
step-ca  | Generating root certificate... done!
step-ca  | Generating intermediate certificate... done!
step-ca  |
step-ca  | ✔ Root certificate: /home/step/certs/root_ca.crt
step-ca  | ✔ Root private key: /home/step/secrets/root_ca_key
step-ca  | ✔ Root fingerprint: b201194735cb48db79eaf2f7aa2135e2a5ced7d3dd316d7613bcfaf9eac6d6f8
step-ca  | ✔ Intermediate certificate: /home/step/certs/intermediate_ca.crt
step-ca  | ✔ Intermediate private key: /home/step/secrets/intermediate_ca_key
step-ca  | badger 2025/08/16 10:11:32 INFO: All 0 tables opened in 0s
step-ca  | badger 2025/08/16 10:11:32 INFO: Storing value log head: {Fid:0 Len:30 Offset:3311}
step-ca  | badger 2025/08/16 10:11:32 INFO: [Compactor: 173] Running compaction: {level:0 score:1.73 dropPrefixes:[]} for level: 0
step-ca  | badger 2025/08/16 10:11:32 INFO: LOG Compact 0->1, del 1 tables, add 1 tables, took 1.522094ms
step-ca  | badger 2025/08/16 10:11:32 INFO: [Compactor: 173] Compaction for level: 0 DONE
step-ca  | badger 2025/08/16 10:11:32 INFO: Force compaction on level 0 done
step-ca  | ✔ Database folder: /home/step/db
step-ca  | ✔ Default configuration: /home/step/config/defaults.json
step-ca  | ✔ Certificate Authority configuration: /home/step/config/ca.json
step-ca  | ✔ Admin provisioner: admin (JWK)
step-ca  | ✔ Super admin subject: hellowood
step-ca  |
step-ca  | Your PKI is ready to go. To generate certificates for individual services see 'step help ca'.
step-ca  |
step-ca  | FEEDBACK 😍 🍻
step-ca  |   The step utility is not instrumented for usage statistics. It does not phone
step-ca  |   home. But your feedback is extremely valuable. Any information you can provide
step-ca  |   regarding how you’re using `step` helps. Please send us a sentence or two,
step-ca  |   good or bad at feedback@smallstep.com or join GitHub Discussions
step-ca  |   https://github.com/smallstep/certificates/discussions and our Discord
step-ca  |   https://u.step.sm/discord.
step-ca  |
step-ca  | 👉 Your CA administrative username is: hellowood
step-ca  | 👉 Your CA administrative password is: Ihaveapen1!
step-ca  | 🤫 This will only be displayed once.
step-ca  | badger 2025/08/16 10:11:32 INFO: All 1 tables opened in 0s
step-ca  | badger 2025/08/16 10:11:32 INFO: Replaying file id: 0 at offset: 3341
step-ca  | badger 2025/08/16 10:11:32 INFO: Replay took: 3.326µs
step-ca  | 2025/08/16 10:11:32 Building new tls configuration using step-ca x509 Signer Interface
step-ca  | 2025/08/16 10:11:32 Starting Smallstep CA/0.28.4 (linux/amd64)
step-ca  | 2025/08/16 10:11:32 Documentation: https://u.step.sm/docs/ca
step-ca  | 2025/08/16 10:11:32 Community Discord: https://u.step.sm/discord
step-ca  | 2025/08/16 10:11:32 Config file: /home/step/config/ca.json
step-ca  | 2025/08/16 10:11:32 The primary server URL is https://ca.svc.homelab:9000
step-ca  | 2025/08/16 10:11:32 Root certificates are available at https://ca.svc.homelab:9000/roots.pem
step-ca  | 2025/08/16 10:11:32 Additional configured hostnames: *.svc.homelab, localhost
step-ca  | 2025/08/16 10:11:32 X.509 Root Fingerprint: b201194735cb48db79eaf2f7aa2135e2a5ced7d3dd316d7613bcfaf9eac6d6f8
step-ca  | 2025/08/16 10:11:32 Serving HTTPS on :9000 ...
```

启动完成后访问 `https://100.0.0.2:9000/health`，返回 OK 表示 Step CA 正确启动

```bash
curl -k https://100.0.0.2:9000/health

{"status":"ok"}
```

访问 `https://100.0.0.2:9000/acme/acme/directory` 查看 ACME 目录信息

```bash
curl -k https://100.0.0.2:9000/acme/acme/directory

{"newNonce":"https://100.0.0.2:9000/acme/acme/new-nonce","newAccount":"https://100.0.0.2:9000/acme/acme/new-account","newOrder":"https://100.0.0.2:9000/acme/acme/new-order","revokeCert":"https://100.0.0.2:9000/acme/acme/revoke-cert","keyChange":"https://100.0.0.2:9000/acme/acme/key-change"}
```

### 添加域名解析

将 `ca.svc.homelab` 域名解析到 Step CA 的 IP 地址，方便 Caddy 作为 ACME Server 使用，可以通过 DNS 服务器或者 `/etc/hosts` 文件添加解析

```
100.0.0.2 ca.svc.homelab
```

## 信任 Step CA 的根证书

想要其他服务使用 Step CA 颁发的证书能正确访问，需要将 Root CA 证书添加到设备的受信任的根证书中

- 获取 CA 证书

Step CA 正确启动后会在 `data/certs/` 目录下生成 `root_ca.crt` 和 `intermediate_ca.crt` 两个证书文件；其中 `root_ca.crt` 是根证书，`intermediate_ca.crt` 是中间证书；需要将 `root_ca.crt` 添加到设备的受信任的根证书中；文件目录结构如下，`data/certs/root_ca.crt` 就是根证书

```bash
.
├── data
│   ├── certs
│   │   ├── intermediate_ca.crt
│   │   ├── root_ca.crt
│   ├── config
│   │   ├── ca.json
│   │   └── defaults.json
│   └── secrets
│       ├── intermediate_ca_key
│       ├── password
│       └── root_ca_key
└── docker-compose.yaml
```

- 将根证书添加到 Ubuntu

需要将根证书文件复制到 `/usr/local/share/ca-certificates/` 目录下，然后运行 `update-ca-certificates` 命令更新证书列表，使证书生效，这样访问 Step CA 颁发的证书时就不会再提示不受信任

```bash
sudo cp data/certs/root_ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

- 将根证书添加到 macOS

将 root_ca.crt 文件下载到 macOS 上，使用钥匙串访问打开，然后在登录-证书中选择信任该证书

![homelab-caddy-step-ca-cert-trust-root-ca-01.png](https://img.hellowood.dev/picture/homelab-caddy-step-ca-cert-trust-root-ca-01.png)

![homelab-caddy-step-ca-cert-trust-root-ca-02.png](https://img.hellowood.dev/picture/homelab-caddy-step-ca-cert-trust-root-ca-02.png)

其他操作系统或者软件可以参考 [step certificate install](https://smallstep.com/docs/step-cli/reference/certificate/install/) 中的相关内容进行安装

## Caddy 使用 Step CA 作为 ACME Server

Caddy 支持自定义 ACME Server，因此可以直接使用 Step CA 作为 ACME Server 来颁发证书

关于 Caddy 的安装和配置可以参考 [使用 Caddy 作为 HomeLab 内网服务的代理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-caddy-%E4%BD%9C%E4%B8%BA-homelab-%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1%E7%9A%84%E4%BB%A3%E7%90%86/)

### 启动 Caddy

使用 docker compose 启动 Caddy；同时启动一个 whoami 服务用于测试

- docker-compose.yml

```yaml
services:
  caddy:
    image: caddy
    container_name: caddy
    hostname: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "2019:2019"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./certs:/certs
      - ./data:/data/caddy
      - ./config:/config/caddy

  whoami:
    image: traefik/whoami
    restart: unless-stopped
    container_name: whoami
    hostname: whoami
    ports:
      - 8081:80
```

### 配置 ACME Server

- 将 Step CA 的根证书挂载到 Caddy 容器中

需要将 Step CA 的根证书挂载到 Caddy 容器中，用于 Caddy 验证 Step CA 颁发的证书；将 Step CA 的 `data/certs/root_ca.crt` 复制到 `certs/` 目录下

- Caddyfile 配置 ACME Server

```conf
{
    log {
        output stdout
        format console
        level info
    }
    admin 0.0.0.0:2019

    # ACME Server 配置
    email admin@mail.svc.homelab
    acme_ca https://ca.svc.homelab:9000/acme/acme/directory
    acme_ca_root /certs/root_ca.crt
}

whoami.svc.homelab {
  reverse_proxy 100.0.0.2:8080
}
```

### 启动 Caddy

目录结构如下：

```bash
.
├── Caddyfile
├── config
├── certs
│   ├── root_ca.crt
├── data
└── docker-compose.yaml
```

使用 `docker compose up -d` 启动 Caddy 服务，Caddy 会自动向 Step CA 请求证书，相关日志如下：

```bash
caddy  | 2025/08/16 13:44:18.098	INFO	tls.issuance.acme	done waiting on internal rate limiter	{"identifiers": ["whoami.svc.homelab"], "ca": "https://ca.svc.homelab:9000/acme/acme/directory", "account": "admin@mail.svc.homelab"}
caddy  | 2025/08/16 13:44:18.098	INFO	tls.issuance.acme	using ACME account	{"account_id": "https://ca.svc.homelab:9000/acme/acme/account/hlJdKH3lry6PQukHyahRQWQ06wwdBM5J", "account_contact": ["mailto:admin@mail.svc.homelab"]}
caddy  | 2025/08/16 13:44:18.105	INFO	trying to solve challenge	{"identifier": "whoami.svc.homelab", "challenge_type": "tls-alpn-01", "ca": "https://ca.svc.homelab:9000/acme/acme/directory"}
caddy  | 2025/08/16 13:44:18.108	INFO	tls	served key authentication certificate	{"server_name": "whoami.svc.homelab", "challenge": "tls-alpn-01", "remote": "172.18.0.1:51640", "distributed": false}
caddy  | 2025/08/16 13:44:18.364	INFO	authorization finalized	{"identifier": "whoami.svc.homelab", "authz_status": "valid"}
caddy  | 2025/08/16 13:44:18.364	INFO	validations succeeded; finalizing order	{"order": "https://ca.svc.homelab:9000/acme/acme/order/WmFkMDixawSZl1bw6gq0xX9CnyOEnLQc"}
caddy  | 2025/08/16 13:44:18.372	INFO	successfully downloaded available certificate chains	{"count": 1, "first_url": "https://ca.svc.homelab:9000/acme/acme/certificate/04rWrksSgX9IHiyBCgHajOeXs2xjUu6K"}
caddy  | 2025/08/16 13:44:18.374	INFO	tls.obtain	certificate obtained successfully	{"identifier": "whoami.svc.homelab", "issuer": "ca.svc.homelab:9000-acme-acme-directory"}
caddy  | 2025/08/16 13:44:18.374	INFO	tls.obtain	releasing lock	{"identifier": "whoami.svc.homelab"}
```

### 验证 HTTPS 证书

访问 `https://whoami.svc.homelab`，可以正常访问，并且证书是有效的：

```bash
curl -I https://whoami.svc.homelab

HTTP/2 200
alt-svc: h3=":443"; ma=2592000
content-type: text/plain; charset=utf-8
date: Sat, 16 Aug 2025 13:49:41 GMT
via: 1.1 Caddy
content-length: 273
```

- 查看证书信息

通过 openssl 命令查看证书信息，由 `Homelab Internal CA` 颁发，有效期为1天，Caddy 会自动续期

```bash
echo | openssl s_client -connect whoami.svc.homelab:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer

notBefore=Aug 16 13:43:18 2025 GMT
notAfter=Aug 17 13:44:18 2025 GMT
subject=
issuer=O=Homelab Internal CA, CN=Homelab Internal CA Intermediate CA
```

### 泛域名申请证书

Caddy 泛域名申请证书比较麻烦，需要支持 dns-01 challenge 的 DNS 服务器，并且需要开启`rfc2136` 插件；在 HomeLab 场景下，更推荐使用 Step CA 直接生成泛域名证书，然后挂载到 Caddy 中使用

#### 创建泛域名证书

可以进入到 Step CA 容器，使用以下命令创建证书：

```bash
docker exec -it step-ca bash
```

进入到 `/home/step/certs` 目录后，使用以下命令创建泛域名证书：

```bash
step certificate create "*.svc.homelab" _wildcard.svc.homelab.crt _wildcard.svc.homelab.key \
  --profile leaf \
  --ca /home/step/certs/root_ca.crt \
  --ca-key /home/step/secrets/root_ca_key \
  --no-password --insecure \
  --not-after 87600h

Please enter the password to decrypt /home/step/secrets/root_ca_key:
✔ Would you like to overwrite _wildcard.svc.homelab.crt [y/n]: y█
✔ Would you like to overwrite _wildcard.svc.homelab.crt [y/n]: y
Your certificate has been saved in _wildcard.svc.homelab.crt.
Your private key has been saved in _wildcard.svc.homelab.key.
```

#### 挂载到 Caddy

- Caddyfile

```conf
*.svc.homelab {
  tls /certs/_wildcard.svc.homelab.crt /certs/_wildcard.svc.homelab.key
  reverse_proxy 100.0.0.2:8080
}
```

启动后查看证书信息，此时证书变成了泛域名证书：

```bash
echo | openssl s_client -connect whoami.svc.homelab:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer

notBefore=Aug 16 08:43:55 2025 GMT
notAfter=Aug 14 08:43:51 2035 GMT
subject=CN=*.svc.homelab
issuer=O=Homelab Internal CA, CN=Homelab Internal CA Root CA
```

使用之后还是太复杂，不适合 HomeLab 场景，还是使用 mkcert 生成证书直接使用更简单，将根证书添加到设备的受信任的根证书中即可
