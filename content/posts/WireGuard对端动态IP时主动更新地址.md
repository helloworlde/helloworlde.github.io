---
title: "WireGuard对端动态IP时主动更新地址"
type: post
date: 2023-09-24T18:37:06+08:00
tags:
    - HomeLab
    - WireGuard
categories: 
    - HomeLab
    - WireGuard   
featured: true
---

# WireGuard 对端动态 IP 时主动更新地址

如果 WireGuard 对端的 `Endpoint` 是一个域名，这个域名只会在启动的时候解析一次，后续不会更新；当这个域名发生变化时，WireGuard 连接就会断开

wireguard-tools 的仓库中提供了检测 IP 变化并更新 `Endpoint` 的脚本 [https://git.zx2c4.com/wireguard-tools/tree/contrib/reresolve-dns/reresolve-dns.sh](https://git.zx2c4.com/wireguard-tools/tree/contrib/reresolve-dns/reresolve-dns.sh)，因此可以使用该脚本，通过定时任务的方式可以实现域名 IP 变化后更新 WireGuard 

- 下载仓库

```bash
git clone https://git.zx2c4.com/wireguard-tools /usr/share/wireguard-tools
```

- 配置更新服务

```bash
sudo cat <<EOL > /etc/systemd/system/wireguard-update-dns.service
[Unit]
Description=Update DNS of all WireGuard endpoints
Wants=network.target
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for i in /etc/wireguard/*.conf; do /usr/share/wireguard-tools/contrib/reresolve-dns/reresolve-dns.sh "\$i"; done'
EOL
```


- 配置定时任务服务

```bash
sudo cat <<EOL > /etc/systemd/system/wireguard-update-dns.timer
[Unit]
Description=Update DNS of all WireGuard endpoints

[Timer]
OnCalendar=*:*:0/30

[Install]
WantedBy=timers.target
EOL
```

- 启动服务

```bash
systemctl enable wireguard-update-dns.service wireguard-update-dns.timer --now
```

这样，就会每隔 30s 检测并更新一次 Endpoint 的地址了