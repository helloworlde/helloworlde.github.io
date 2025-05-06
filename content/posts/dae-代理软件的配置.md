---
date: 2025-04-29
# description: ""
# image: ""
lastmod: 2025-05-06
showTableOfContents: false
tags:
  - Proxy
  - Dae
  - HomeLab
  - OpenWrt
title: "Dae 代理软件的配置"
type: "post"
featured: true
---

dae 的配置使用的是自定义的 `.dae` 格式的文件，语法类似 NGINX 配置的变体；dae 的文档介绍有限，很多配置需要翻阅源码才知道如何配置，因此记录一下

## 一、配置文件结构

Dae的配置文件分为以下几个主要部分：

| 配置         | 说明                                                                       |
| ------------ | -------------------------------------------------------------------------- |
| global       | 全局配置，包括日志级别、监听地址、端口等                                   |
| dns          | DNS配置，包括上游 DNS 服务器、DNS 分流策略等                               |
| subscription | 节点订阅配置，用于从订阅服务器获取节点信息，解析到的节点会被添加到 node 中 |
| node         | 节点配置，包括节点的地址、端口、协议、加密方式等                           |
| group        | 节点分组，根据过滤规则对节点进行分组，用于 routing 分流到不同的节点        |
| routing      | 路由规则，根据规则决定流量的处理策略，包括直连、分流代理到特定的分组或节点 |

格式：

```nginx
# 全局配置
global {
}

# DNS 配置
dns {
}

# 订阅地址
subscription {
}

# 节点
node {
}

# 节点分组
group {
}

# 路由配置
routing {
}
```

## 二、配置

### 2.1 global

- 示例配置

```nginx
global {
    # Log level: error, warn, info, debug, trace.
    log_level: info
    # 代理流量的 LAN 接口
    lan_interface: eth0,enp2s0
    # 代理 WAN 接口，代理本机流量
    wan_interface: auto

    # 代理模式：ip/domain/domain+/domain++
    dial_mode: domain++
}
```

- 配置说明

| 配置项名称                     | 说明                                                                                                                       |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| tproxy_port                    | TProxy 端口，仅供 eBPF 使用，通常无需修改，默认为 12345                                                                    |
| tproxy_port_protect            | 是否保护 TProxy 端口不被非法访问；若设为 false，用户需自行配置 iptables，默认为 true                                       |
| pprof_port                     | 启用 pprof 的端口，设为非零值开启                                                                                          |
| so_mark_from_dae               | 设置 dae 发出的流量的 SO_MARK，避免与 iptables tproxy 规则冲突                                                             |
| log_level                      | 日志等级，默认为 info，支持 error/warn/info/debug/trace                                                                    |
| disable_waiting_network        | 禁用等待网络连接后再拉取订阅功能，默认为 false                                                                             |
| enable_local_tcp_fast_redirect | 启用本地 TCP 快速重定向（实验功能），可能导致部分代理/客户端异常，默认为 false                                             |
| lan_interface                  | 要绑定的局域网接口，支持多个接口以英文逗号分隔，通常配置为 eth0                                                            |
| wan_interface                  | 要绑定的广域网接口，auto 表示自动检测，支持多个接口                                                                        |
| auto_config_kernel_parameter   | 是否自动配置 Linux 内核参数（如 ip_forward 等），默认为 true                                                               |
| tcp_check_url                  | 用于 TCP 节点连通性检查的网址，推荐选择响应快的 anycast 地址，默认值 http://cp.cloudflare.com,1.1.1.1,2606:4700:4700::1111 |
| tcp_check_http_method          | TCP 检查所使用的 HTTP 方法，默认 HEAD 流量更节省，支持 GET/POST 等                                                         |
| udp_check_dns                  | 用于检查 UDP（及 TCP DNS）连通性的 DNS 服务器地址，默认为 dns.google:53,8.8.8.8,2001:4860:4860::8888                       |
| check_interval                 | 节点连通性检测的时间间隔，默认为 30s                                                                                       |
| check_tolerance                | 节点切换容差阈值；仅当新延迟 ≤ 旧延迟 - 容差时才切换节点， 默认 50ms                                                       |
| dial_mode                      | 代理模式，默认为 domain，支持 ip/domain/domain+/domain++                                                                   |
| allow_insecure                 | 是否允许不安全的 TLS 证书（如自签证书）；不推荐启用，默认为 false                                                          |
| sniffing_timeout               | 嗅探超时等待首个数据包的时间，dial_mode 为 ip 时该值无效，默认为 100ms                                                     |
| tls_implementation             | TLS 实现方式：tls 使用 Go 原生库，utls 模拟浏览器，默认为 tls，支持 tls/utls                                               |
| utls_imitate                   | 当 tls_implementation 为 utls 时，指定模拟的浏览器类型，值为chrome_auto                                                    |
| mptcp                          | 是否启用 Multipath TCP，用于多链路负载均衡与故障转移，默认 false                                                           |
| bandwidth_max_tx               | 最大上行带宽（用于部分协议性能优化），单位支持 b/kb/mb/gb/tb                                                               |
| bandwidth_max_rx               | 最大下行带宽，单位支持 b/kb/mb/gb/tb                                                                                       |

`dial_mode` 支持以下几种模式：

| 模式名称 | 说明                                                                                   |
| -------- | -------------------------------------------------------------------------------------- |
| ip       | 直接使用 DNS 返回的 IP 代理，该模式下会禁用嗅探                                        |
| domain   | 嗅探域名进行代理，需要客户端使用 dae 作为 DNS                                          |
| domain+  | 基于 domain 模式，嗅探域名进行代理，但是不验证真实性，适用于不使用 dae 作为 DNS 的场景 |
| domain++ | 基于 domain+ 模式，强制进行域名嗅探并重新分流，会消耗更多的 CPU                        |

### 2.2 dns

- 示例配置：

完整的 DNS 分流参考 [DNS](URL_ADDRESS.com/daeuniverse/dae/blob/main/docs/zh/configuration/dns.md)

```nginx
dns {
  # 上游 DNS
  upstream {
    # 阿里云 DNS，用于国内域名查询
    alidns: 'udp://223.5.5.5:53'
    # Cloudflare DNS，用于非国内的 DNS 查询
    cfdns: 'tcp+udp://1.1.1.1:53'
  }

  # DNS 查询规则
  routing {
    # 根据 DNS 查询，决定使用哪个 DNS 上游，按由上到下的顺序匹配
    request {
      # 国内域名使用阿里云
      qname(geosite:cn) -> alidns
      # fallback 即默认兜底 DNS
      fallback: cfdns
    }
  }
}
```

- 配置说明

| 配置项名称       | 说明                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------ |
| ipversion_prefer | 首选 IP 协议版本，若为 4，域名有 A 和 AAAA 记录时仅响应 A 记录，AAAA 返回空          |
| fixed_domain_ttl | 指定域名的固定 TTL，设为 0 表示不缓存，始终请求上游 DNS                              |
| upstream         | 配置上游 DNS 服务器，支持多种协议（udp/tcp/http3/h3/https/tls 等），也支持自定义路径 |
| routing.request  | 指定 DNS 查询规则，如对中国域名使用 alidns，其余使用 googledns                       |
| routing.response | （可选）根据响应结果决定是否接受或重新使用其他 DNS 上游再查询                        |

### 2.3 subscription

dae 的配置订阅处于早期阶段，兼容性较差，dae 会过滤包含 `://` 的行作为节点进行检测，因此订阅内容必须是符合 SIP008 格式或者 base64/urlencode 编码或者 txt 格式的节点列表

- 示例配置

配置分为两部分，tag 和订阅地址，tag 是订阅地址的唯一标识，用于 group 分组筛选节点

```nginx
subscription {
    # 订阅地址
    sub_airport_1: 'https://node.freeclashnode.com/uploads/2025/05/0-20250505.txt'
}
```

- 订阅地址说明

| 配置项名称           | 说明                                                                             |
| -------------------- | -------------------------------------------------------------------------------- |
| https/http           | 在线订阅地址，如 `https://node.freeclashnode.com/uploads/2025/05/0-20250505.txt` |
| file                 | 订阅文件路径，如 `/etc/dae/static_subscription.sub`                              |
| https-file/http-file | 在线订阅地址，并自动保存到本地，路径是 `config_dir/persist.d/订阅tag.sub`        |

#### 2.3.1 配置格式

- SIP008 格式：

是 Shadowsocks/ShadowsocksR 的默认格式

```json
{
  "version": 1,
  "servers": [
    {
      "server": "example.com",
      "server_port": 8388,
      "method": "aes-256-gcm",
      "password": "your_password",
      "remarks": "节点1"
    },
    {
      "server": "1.2.3.4",
      "server_port": 443,
      "method": "chacha20-ietf-poly1305",
      "password": "another_password",
      "remarks": "节点2",
      "plugin": "obfs-local",
      "plugin_opts": "obfs=tls;obfs-host=www.bing.com"
    }
  ]
}
```

- txt 格式

```text
trojan://password@remote_host:remote_port
hysteria2://letmein@example.com:123,5000-6000/?insecure=1&obfs=salamander&obfs-password=gawrgura&pinSHA256=deadbeef&sni=real.example.com
```

- base64 编码

是 txt 格式 base64 编码后的内容

```text
dHJvamFuOi8vcGFzc3dvcmRAcmVtb3RlX2hvc3Q6cmVtb3RlX3BvcnQKaHlzdGVyaWEyOi8vbGV0bWVpbkBleGFtcGxlLmNvbToxMjMsNTAwMC02MDAwLz9pbnNlY3VyZT0xJm9iZnM9c2FsYW1hbmRlciZvYmZzLXBhc3N3b3JkPWdhd3JndXJhJnBpblNIQTI1Nj1kZWFkYmVlZiZzbmk9cmVhbC5leGFtcGxlLmNvbQ==
```

- urlencode 格式

是 txt 格式 urlencode 编码后的内容

```text
trojan%3A%2F%2Fpassword%40remote_host%3Aremote_port
hysteria2%3A%2F%2Fletmein%40example.com%3A123%2C5000-6000%2F%3Finsecure%3D1%26obfs%3Dsalamander%26obfs-password%3Dgawrgura%26pinSHA256%3Ddeadbeef%26sni%3Dreal.example.com
```

### 2.4 node

- 示例配置

node 分为两部分，tag 和 URI，tag 是节点的唯一标识，用于 group 分组，URI 是节点的连接信息，根据不同的协议有不同的格式，具体参考：[其他代理协议](https://github.com/daeuniverse/dae/blob/main/docs/zh/proxy-protocols.md)

```nginx
node {
    # HTTPS/VMess/VLESS/Shadowsocks/Trojan/Tuic/Juicity/Hysteria2 等格式
    hy2: "hysteria2://user:password@host:443/?insecure=false"
}
```

### 2.5 group

- 示例配置：

详细参考: [https://github.com/daeuniverse/dae/blob/main/example.dae](https://github.com/daeuniverse/dae/blob/main/example.dae)

```nginx
# 节点分组
group {
    # 分组一，名称是 proxy，用于 routing 选择
    # 没有过滤条件，使用所有节点
    proxy {
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }

    # AI 分组，用于 claude 等对地区有限制的服务商
    ai {
        # 从 subscription 的 sub_airport_1 中过滤名称包含新加坡的作为这个分组的可用节点
        filter: subtag(sub_airport_1) && name(keyword: '新加坡')
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }
}
```

- 配置说明

| 配置项名称            | 说明                                                                                                                                                                                                                                                                                                                                    |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| group                 | 出站节点分组，可基于策略从全局节点池中选取节点，如果没有任何过滤条件，则选择所有节点                                                                                                                                                                                                                                                    |
| filter                | 分组节点的过滤条件：1. `subtag(tag_name)`：按订阅标签过滤；2. `name(name1, name2)`：按节点名称精确过滤；3. `keyword:`、`regex:`：关键字或正则匹配名称；过滤条件可组合，如`subtag(regex: '^my_', another_sub) && !name(keyword: 'ExpireAt:')`; 节点可用 `add_latency:` 指定延迟偏移以影响选择排序 , 用于从全局节点池中筛选进入该组的节点 |
| policy                | 分组内节点的负载均衡选择策略: 1.`random`：每次连接随机选择一个节点; 2. `fixed(0)`：始终使用第一个节点; 3. `min`：使用最近一次延迟最小的节点; 4. `min_moving_avg`：使用延迟移动平均值最小的节点; 5. `min_avg10`：使用最近 10 次平均延迟最小的节点，定义该分组的节点选择策略                                                              |
| tcp_check_url         | （可选）默认继承自 global；如设置：`http://test.steampowered.com` , 覆盖全局设置的 TCP 节点连通性检查 URL，适用于特殊分组（如 steam）测试目标优化。                                                                                                                                                                                     |
| tcp_check_http_method | 自定义 HTTP 请求方法，通常用于规避计费、污染等问题，默认为 HEAD                                                                                                                                                                                                                                                                         |
| udp_check_dns         | 自定义 UDP 连通性测试 DNS，适用于分组层面特殊连接测试策略。                                                                                                                                                                                                                                                                             |
| check_interval        | 节点连通性测试间隔，默认 30s                                                                                                                                                                                                                                                                                                            |
| check_tolerance       | 延迟容忍度，仅当新节点延迟明显优于旧节点时才触发切换，默认为 50ms                                                                                                                                                                                                                                                                       |

### 2.6 routing

- 示例配置

分流规则分为两部分，左侧为匹配规则，右侧为匹配到规则后使用的节点分组，规则按从上到下的顺序匹配；内置的出站规则有 `block`, `direct`, `must_direct`, `must_rules`(must_rules 表示不将DNS流量重定向至 dae 并继续匹配) , 除此之外必须使用 group 定义的节点分组，如 前面定义的 `proxy`, `ai` 等

```nginx
# 分流规则
routing {
    # DNS/SSH 等相关进程强制直连
    pname(dnsmasq, dropbear) -> must_direct
    # DNS 地址或域名，强制直连
    dip(8.8.8.8) -> must_direct
    dip(1.1.1.1) -> must_direct
    domain(dns.alidns.com) -> must_direct
    domain(dns.google) -> must_direct
    domain(cloudflare-dns.com) -> must_direct

    # 目标 IP 多播、广播地址，直连
    dip(224.0.0.0/3, 'ff00::/8') -> direct
    # 目标 IP geoip 中的内网地址，直连
    dip(geoip:private) -> direct

    # 目标 IP 中国 IP，直连
    dip(geoip:cn) -> direct
    # 中国域名，直连
    domain(geosite:cn) -> direct

    # 广告域名，拒绝
    domain(geosite:category-ads) -> block

    # AI 域名，AI 分组代理
    domain(suffix: claude.ai) -> ai
    domain(suffix: openai.com) -> ai

    # 未命中上面的规则的走 proxy 代理
    fallback: proxy
}
```

- 常用匹配规则语法

完整的分流规则参考 [路由](https://github.com/daeuniverse/dae/blob/main/docs/zh/configuration/routing.md)

| 规则      | 说明                                       | 举例                                                                                                              |
| --------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| fallback  | 未匹配规则时使用的默认出站                 | `fallback: my_group`                                                                                              |
| pname     | 匹配进程名（仅适用于本机进程）             | `pname(curl) -> direct`                                                                                           |
| domain    | 匹配域名，支持多种方式                     | `domain(keyword: facebook) -> my_group`, `domain(geosite:cn) -> direct`, `domain(suffix: v2raya.org) -> my_group` |
| dip       | 匹配目标 IP，可用单个/多个 IP、CIDR、geoip | `dip(8.8.8.8) -> direct`, `dip(geoip:cn) -> direct`                                                               |
| sip       | 匹配源 IP，可用单个 IP、CIDR、多值         | `sip(192.168.0.0/24) -> my_group`                                                                                 |
| dport     | 匹配目标端口，支持单端口或范围             | `dport(80) -> direct`, `dport(10080-30000) -> direct`                                                             |
| sport     | 匹配源端口，支持单端口或范围               | `sport(38563) -> direct`, `sport(10080-30000) -> direct`                                                          |
| l4proto   | 匹配四层协议                               | `l4proto(tcp) -> my_group`, `l4proto(udp) -> direct`                                                              |
| ipversion | 匹配 IP 协议版本                           | `ipversion(4) -> block`, `ipversion(6) -> ipv6_group`                                                             |
| mac       | 匹配源 MAC 地址                            | `mac('02:42:ac:11:00:02') -> direct`                                                                              |

## 三、完整示例配置

- config.dae

```nginx
# 完整配置参考 https://github.com/daeuniverse/dae/blob/main/example.dae
global {
    # 修改日志级别为 debug，方便调试
    log_level: debug
    # lan 口绑定 eth0
    lan_interface: eth0
    # 用强制 SNI 嗅探进行分流
    dial_mode: domain++
}

# DNS 配置
dns {
  # 使用 IPv4 的 DNS，避免部分 node 不支持 IPv6 导致请求失败
  ipversion_prefer: 4
  # 上游 DNS
  upstream {
    # 阿里云 DNS，用于国内域名查询
    alidns: 'udp://223.5.5.5:53'
    # 本地 DNS，用于内网自定义的  DNS 查询
    adguard: 'udp://10.0.0.1:53'
    # Cloudflare DNS，用于非国内的 DNS 查询
    cfdns: 'tcp+udp://1.1.1.1:53'
  }

  # DNS 查询规则
  routing {
    # 根据 DNS 查询，决定使用哪个 DNS 上游，按由上到下的顺序匹配
    request {
      # svc.local 结尾的域名，用本地的 DNS 查询
      qname(suffix: svc.local) -> adguard
      # 对于中国大陆域名使用 alidns，其他使用 cfdns 查询。
      qname(geosite:cn) -> alidns
      # fallback 即默认兜底 DNS
      fallback: cfdns
    }
  }
}

# 如果使用订阅地址，必须是符合 SIP008 格式或者 base64/urlencode 编码或者 txt 格式的节点列表，详细参考: https://blog.hellowood.dev/posts/dae-%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E7%9A%84%E9%85%8D%E7%BD%AE/

# subscription 的节点解析过滤后作为 node，tag 是
subscription {
  sub_airport_1: 'https://订阅地址'
}

# 自己搭建的节点，直接配置到 node 方便调试
node {
    # HTTPS/VMess/VLESS/Shadowsocks/Trojan/Tuic/Juicity/Hysteria2 等格式
    hy2: "hysteria2://user:password@host:443/?insecure=false"
}

# 节点分组
group {
    # 分组一，名称是 proxy，用于 routing 选择
    # 没有过滤条件，使用所有节点
    proxy {
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }

    # AI 分组，用于 claude 等对地区有限制的服务商
    ai {
        # 从 subscription 的 sub_airport_1 中过滤名称包含新加坡的作为这个分组的可用节点
        filter: subtag(sub_airport_1) && name(keyword: '新加坡')
        # 节点选择策略使用 最小移动平均延迟节点
        policy: min_moving_avg
    }
}

# 分流规则
routing {
    # DNS/SSH 等相关进程强制直连
    pname(dnsmasq, dropbear) -> must_direct
    # DNS 地址或域名，强制直连
    dip(8.8.8.8) -> must_direct
    dip(1.1.1.1) -> must_direct
    domain(dns.alidns.com) -> must_direct
    domain(dns.google) -> must_direct
    domain(cloudflare-dns.com) -> must_direct

    # 目标 IP 多播、广播地址，直连
    dip(224.0.0.0/3, 'ff00::/8') -> direct
    # 目标 IP geoip 中的内网地址，直连
    dip(geoip:private) -> direct

    # 目标 IP 中国 IP，直连
    dip(geoip:cn) -> direct
    # 中国域名，直连
    domain(geosite:cn) -> direct

    # 广告域名，拒绝
    domain(geosite:category-ads) -> block

    # AI 域名，AI 分组代理
    domain(suffix: claude.ai) -> ai
    domain(suffix: openai.com) -> ai

    # 未命中上面的规则的走 proxy 代理
    fallback: proxy
}
```
