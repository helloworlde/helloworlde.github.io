---
title: "使用 Cloudflare Tunnels 通过 Web SSH 访问服务器"
type: post
date: 2023-10-06T15:25:13+08:00
tags:
  - HomeLab
  - Cloudflare
featured: true
---

Cloudflre 的 Zero Trust 支持通过 Tunnels 访问 SSH 类型的应用，可以通过 Web SSH 的方式访问服务器；支持多种登陆认证方式，安全性远高于直接暴露公网端口

## 创建 SSH 应用

- 创建应用

在 Cloudflare 控制台 > Zero Trust > Access > Applications 选择 Add an application 创建新的应用；应用类型为 Self-hosted

![homelab-cloudflare-ssh-application-create.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-application-create.png)

- 配置应用信息

指定应用名称，并为应用配置域名；session 的过期时间可以按需配置

![homelab-cloudflare-ssh-configuration-application.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-configuration-application.png)

- 指定访问策略

需要配置访问策略，只允许特定的邮箱登陆；如果需要使用其他的认证方式，如 GitHub/Google SSO 等，可以在 Cloudflare 控制台 > Zero Trust > Settings > Authentication > Login Methods 中添加

![homelab-cloudflare-ssh-configuration-policy.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-configuration-policy.png)

- 修改应用类型

在 Additional settings 中，将 Browser rendering 的类型改为 SSH；然后选择保存，这样就配置好 SSH 应用了

![homelab-cloudflare-ssh-set-application-type.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-set-application-type.png)

## 配置 Tunnels

关于 Tunnels 配置安装请参考 [使用Cloudflare-Tunnels提供服务公网访问](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-cloudflare-tunnel-%E4%BD%9C%E4%B8%BA%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86%E8%AE%BF%E9%97%AE%E5%86%85%E7%BD%91%E6%9C%8D%E5%8A%A1/)

- 添加 SSH 服务转发

将 SSH 的路由配置添加到 `/etc/cloudflared/config.yml` 文件中

```yaml
tunnel: xxxxxxxxxx
credentials-file: /root/.cloudflared/xxxxxxxxxx.json
ingress:
  - hostname: terminal.mydomain.com
    service: ssh://localhost:22
  - service: http_status:403
```

- 重启 cloudflared

重启后即通过该 Tunnel 访问 SSH 服务

```bash
sudo systemctl restart cloudflared
```

## 访问

访问刚才配置的 SSH 服务的域名；会提示使用邮箱或者配置的方式进行登陆

![homelab-cloudflare-ssh-application-login.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-application-login.png)

登陆后需要输入服务器的用户名和密码（或者私钥）进行登陆

![homelab-cloudflare-ssh-login-page.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-login-page.png)

## 配置短期证书

在使用时，需要输入用户进行登陆，如果用户不允许密码登陆，还需要使用私钥进行验证；这种方式非常不方便；因此 Cloudflare 提供了短期证书的方式进行认证登陆，用于替代 SSH 密钥

### 创建用户

如果通过 Web SSH 访问服务器，那么用户必须和使用 SSO 登陆的用户名一致，比如 SSO 登陆账户是 abc，那么服务器也只能使用同名的用户进行短期证书登陆，其他用户名是不支持的

- 创建同名用户

```bash
sudo adduser abc
```

如果想让该用户拥有 root 权限，需要将该用户添加到 wheel 用户组(CentOS 等系统) 或者 sudo 用户组（Ubuntu 等系统）

```bash
# CentOS 等 RedHat 系列
usermod -aG wheel abc

# Ubuntu 等
usermod -aG sudo abc
```

### 生成公钥证书

在 Cloudflare 控制台 > Zero Trust > Access > Service Auth > SSH 选择刚才创建的 SSH 应用，然后生成证书

![homelab-cloudflare-service-auth-ssh-generate-key.png](https://img.hellowood.dev/picture/homelab-cloudflare-service-auth-ssh-generate-key.png)

### 配置公钥

将刚才生成的公钥添加在要登陆的服务器上，路径可以自己配置，最好和 SSH 的配置放在一起

- 将公钥添加到 `/etc/ssh/cloudflare-ca.pub`

```bash
cat <<EOF > /etc/ssh/cloudflare-ca.pub
生成的公钥内容,如 ecdsa-sha2-nistp256 xxxxxxxx open-ssh-ca@cloudflareaccess.org
EOF
```

- 修改 SSH 配置

需要开启公钥认证，并且指定刚才添加的公钥为可信任的 CA 公钥；将以下内容添加到 `/etc/ssh/sshd_config` 文件中

```bash
PubkeyAuthentication yes
TrustedUserCAKeys /etc/ssh/cloudflare-ca.pub
```

- 连接 SSH 用户

用 `cloudflare` 生成用户配置，并写入到 `~/.ssh/config`文件中

```bash
cloudflared access ssh-config --hostname terminal.mydomain.com --short-lived-cert >> ~/.ssh/config
```

或者可以手动修改写入配置

```bash
Match host terminal.mydomain.com exec "/usr/local/bin/cloudflared access ssh-gen --hostname %h"
    HostName terminal.mydomain.com
    ProxyCommand /usr/local/bin/cloudflared access ssh --hostname %h
    IdentityFile ~/.cloudflared/terminal.mydomain.com-cf_key
    CertificateFile ~/.cloudflared/terminal.mydomain.com-cf_key-cert.pub
```

### 重启 SSH

```bash
sudo systemctl restart ssh
```

重启完成后，访问配置的 SSH 域名，通过 SSO 登陆后，即可进入到 Web SSH 命令行界面；登陆的用户为 SSO 登陆用户 abc

![homelab-cloudflare-service-auth-ssh-login.png](https://img.hellowood.dev/picture/homelab-cloudflare-service-auth-ssh-login.png)

![homelab-cloudflare-ssh-login-page.png](https://img.hellowood.dev/picture/homelab-cloudflare-ssh-login-page.png)
