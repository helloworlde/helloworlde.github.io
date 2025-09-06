---
title: Ubuntu 22 环境初始化
type: post
date: 2024-01-07T18:03:00+08:00
lastmod: 2024-12-04
tags:
  - Ubuntu
  - HomeLab
featured: true
---

在搭建 HomeLab 测试使用过程中，可能会经常创建新的 Ubuntu 虚拟机，或初始化树莓派，记录一些常用的初始化配置

## 修改主机名

将主机名改为 `homelab`

```bash
hostnamectl hostname homelab
```

## 引入 SSH 公钥

- 从本地导入

在本地执行，将公钥复制到要登录的机器上

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.2.5
```

## 修改 APT 源

将默认的 APT 源替换为[清华](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)的源

- 修改镜像源

```bash
mv /etc/apt/sources.list /etc/apt/sources.list.backup

sudo bash -c "cat << EOF > /etc/apt/sources.list && apt update
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
EOF"
```

然后使用 update 验证

```bash
apt-get update
```

## 安装常用软件

```bash
apt install -y --fix-missing curl vim git jq unzip net-tools zsh git-lfs
```

## 修改时区

使用 `timedatectl` 修改 `/etc/timezone` 文件配置，将时区改为UTC+8

```bash
sudo timedatectl set-timezone Asia/Shanghai
```

## 安装 zsh

1. 安装 zsh 和 git

```bash
sudo apt install -y zsh git
```

2. 添加 on-my-zsh

```bash
sudo sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

3. 添加 autosuggestions 插件

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

4. 修改 `~/.zshrc`，启用 autosuggestions 插件，将 `plugins=(git)`替换为以下内容

```
plugins=(
git
zsh-autosuggestions
)
```

5. 使配置生效

```bash
source ~/.zshrc
```

## 安装 Docker

- docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

- docker-compose

```bash
sudo apt install docker-compose -y
```

- 配置 docker

```
mkdir -p ~/.docker && touch ~/.docker/config.json

cat <<EOF > ~/.docker/config.json
{
	"auths": {
		"registry.xxx.com": {
			"auth": "xxx"
		}
	},
	"psFormat": "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}"
}
EOF
```

- 安装 loki 日志插件

```bash
docker plugin install grafana/loki-docker-driver --alias loki --grant-all-permissions
```

## vim 配置修改

```bash
cat <<EOT > /etc/vim/vimrc.local
"修复中文乱码"
:set encoding=utf-8
"语法高亮"
syntax on
"自动对齐"
set autoindent
"检测文件类型"
filetype on
EOT
```

## 安装中包

```bash
apt install language-pack-zh-hant language-pack-zh-hans -y
```

## 配置 ssh

```bash
touch /etc/ssh/sshd_config.d/homelab.conf

cat <<EOF > /etc/ssh/sshd_config.d/homelab.conf
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
EOF
```

- 重启 SSH 服务

```bash
 systemctl restart ssh.service
```
