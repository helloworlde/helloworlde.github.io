---
date: 2025-09-27
# description: ""
# image: ""
lastmod: 2025-10-01
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置"
type: "post"
---

## 一、配置车辆

配置车辆时需要使用鉴权，因此需要先获取 access_token；或者。access_token 可以参考下面的方式手动获取，也可以使用 [https://github.com/helloworlde/tesla-access-token](https://github.com/helloworlde/tesla-access-token) 项目在 Cloudflare 部署 Worker 进行获取(注意：这个 Worker 绝对不能公开访问，使用前务必通过 Cloudflare Access 配置鉴权策略，保证仅自己可见)

### 1.1 获取 access_token

需要用户授权的 OAuth Token，用于调用 tesla-http-proxy 向车辆下发配置；这里的 access_token 类型是 '第三方令牌'，详细参考 [第三方令牌](https://developer.tesla.cn/docs/fleet-api/authentication/third-party-tokens)

- 用户授权

首先需要使用之前申请的应用的 client_id 和 redirect_uri 访问下面的链接，进行用户授权；需要替换 `${CLIENT_ID}`、`${REDIRECT_URI}` 和 `${STATE}`，其中 `${STATE}` 可以使用随机字符串，如 123456 等；这里的 scope 需要包含 `vehicle_cmds` 和 `vehicle_device_data`，用于下发配置和接收车辆数据

```bash
https://auth.tesla.cn/oauth2/v3/authorize?client_id=${CLIENT_ID}&locale=zh-CN&prompt=login&redirect_uri=${REDIRECT_URI}&response_type=code&scope=openid%20offline_access%20user_data%20vehicle_device_data%20vehicle_location%20vehicle_cmds%20vehicle_charging_cmds%20energy_device_data%20energy_cmds&state=${STATE}
```

然后会进入登录页面，成功登录后会跳转到 `${REDIRECT_URI}`，并且携带 `code` 参数，这个 code 用于获取 access_token:

```bash
${REDIRECT_URI}?locale=zh-CN&code=CN_xxxx&state=${STATE}&issuer=https%3A%2F%2Fauth.tesla.cn%2Foauth2%2Fv3
```

![homelab-tesla-fleet-telemetry-login-for-token.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-login-for-token.png)

- 获取 access_token

使用上面的请求参数中的 code，访问 [代码交换](https://developer.tesla.cn/docs/fleet-api/authentication/third-party-tokens#step-3-code-exchange) 接口获取 access_token

需要替换 `${CLIENT_ID}`、`${CLIENT_SECRET}`、`${REDIRECT_URI}` 和 `${CODE}`，其中 `${CODE}` 是上面获取到的 code

```bash
curl --location 'https://auth.tesla.cn/oauth2/v3/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=authorization_code' \
--data-urlencode 'client_id=${CLIENT_ID}' \
--data-urlencode 'client_secret=${CLIENT_SECRET}' \
--data-urlencode 'audience=https://fleet-api.prd.cn.vn.cloud.tesla.cn' \
--data-urlencode 'redirect_uri=${REDIRECT_URI}' \
--data-urlencode 'scope=openid offline_access user_data vehicle_device_data vehicle_location vehicle_cmds vehicle_charging_cmds energy_device_data energy_cmds' \
--data-urlencode 'code=${CODE}'
```

响应中的 access_token 就是用于鉴权的令牌，有效期是 8个小时

```json
{
  "access_token": "eyXXXX",
  "id_token": "eyXXXX",
  "expires_in": 28800,
  "state": "xxxxx",
  "token_type": "Bearer"
}
```

### 1.2 下发配置

下发配置需要调用 Fleet 车辆端点的 API，但是该 API 不允许直接调用，必须用公钥加密后才可以；因此需要使用 tesla-http-proxy 作为代理，或者自己加密 body 后调用 `fleet_telemetry_config_jws` 接口

配置的内容是一个 JSON 文件，指定需要上报的数据和上报的频率等信息，相关的字段可以参考 [protos/vehicle_data.proto](https://github.com/teslamotors/fleet-telemetry/blob/main/protos/vehicle_data.proto#L9)

- 获取 CA 证书

需要将 Certbot 申请的证书的 CA 下发给车辆，用于验证域名；需要将 `chain.pem` 的内容转换成一行添加到请求 body 中:

```bash
awk '{printf "%s\\n",$0}' chain.pem
```

输出内容格式如下：

```bash
-----BEGIN CERTIFICATE-----\nxxxxxxxxx\n-----END CERTIFICATE-----
```

- 下发配置

下发的配置中需要指定车辆的 VIN 码、监听的端口、上报的数据和频率等信息，该接口的解释说明参考 [fleet_telemetry_config create](https://developer.tesla.cn/docs/fleet-api/endpoints/vehicle-endpoints#fleet-telemetry-config-create)

其中的 fields 字段指定需要上报的数据和上报的频率等信息，详细可以参考 [protos/vehicle_data.proto](https://github.com/teslamotors/fleet-telemetry/blob/main/protos/vehicle_data.proto#L9)，完整的字段配置和说明可以参考文档末尾的部分

这里仅配置速度、里程、电量和档位等字段，其他的字段可以根据需要添加；`interval_seconds` 指定上报的时间间隔，`minimum_delta` 指定数据变化的最小值，只有变化超过该值才会上报数据(仅限于数值类型，并且 `prefer_typed` 设置为 true 才会生效)

```bash
curl --location 'https://fleet.example.com:4443/api/1/vehicles/fleet_telemetry_config' \
--header 'Authorization: Bearer ${ACCESS_TOKEN}' \
--header 'Content-Type: application/json' \
--data '{
    "config": {
        "delivery_policy": "latest",
        "prefer_typed": true,
        "port": 12345,
        "alert_types": [
            "service",
            "customer",
            "service-fix"
        ],
        "fields": {
            "VehicleSpeed": {
                "interval_seconds": 5,
                "minimum_delta": 0.01
            },
            "Odometer": {
                "interval_seconds": 600,
                "minimum_delta": 0.1
            },
            "Soc": {
                "interval_seconds": 300,
                "minimum_delta": 0.1
            }
            "Gear": {
                "interval_seconds": 5
            }
        },
        "ca": "CA 证书内容",
        "hostname": "fleet.example.com"
    },
    "vins": [
        "{{VIN}}"
    ]
}'
```

下发配置成功后会返回响应, 更新了一辆车的配置：

```json
{
  "response": {
    "updated_vehicles": 1
  }
}
```

### 1.3 获取配置

可以通过下面的接口获取当前车辆的配置，参考 [fleet_telemetry_config get](https://developer.tesla.cn/docs/fleet-api/endpoints/vehicle-endpoints#fleet-telemetry-config-get)

```bash
curl --location 'https://tesla-proxy.hellowood.dev/api/1/vehicles/${VIN}/fleet_telemetry_config' \
--header 'Authorization: Bearer ${ACCESS_TOKEN}'
```

当返回的响应中 `synced` 字段为 true 说明配置生效了，`config` 字段中是当前车辆的配置内容； 如果 `synced` 字段为 false 说明配置还没有生效，可能是车辆没有连接到服务器，或者配置有问题等，可以让车辆休眠、重启 Fleet Telemetry 或者再次下发配置

```json
{
  "response": {
    "synced": true,
    "config": {
      "hostname": "fleet.example.com",
      "ca": "CA 证书内容",
      "port": 12345,
      "prefer_typed": true,
      "delivery_policy": "latest",
      "fields": {
        "VehicleSpeed": {
          "interval_seconds": 5,
          "minimum_delta": 0.01
        },
        "Odometer": {
          "interval_seconds": 600,
          "minimum_delta": 0.1
        },
        "Soc": {
          "interval_seconds": 300,
          "minimum_delta": 0.1
        },
        "Gear": {
          "interval_seconds": 5
        }
      },
      "alert_types": ["service", "customer", "service-fix"],
      "iss": "xxx",
      "aud": "com.tesla.fleet.TelemetryClient"
    },
    "limit_reached": false,
    "key_paired": true
  }
}
```

## 参考文档

- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(一)申请证书](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%80-%E7%94%B3%E8%AF%B7%E8%AF%81%E4%B9%A6/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%8C-%E6%B7%BB%E5%8A%A0%E8%99%9A%E6%8B%9F%E9%92%A5%E5%8C%99/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%89-%E9%83%A8%E7%BD%B2%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%9B%9B-%E4%B8%8B%E5%8F%91%E9%85%8D%E7%BD%AE/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%BA%94-%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E5%85%AD-%E7%9B%91%E6%8E%A7%E6%9C%8D%E5%8A%A1/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明](https://blog.hellowood.dev/posts/%E4%BD%BF%E7%94%A8-fleet-telemetry-%E8%AE%A9-tesla-%E8%BD%A6%E8%BE%86%E4%B8%BB%E5%8A%A8%E4%B8%8A%E6%8A%A5%E6%95%B0%E6%8D%AE%E8%BF%9B%E8%A1%8C%E7%9B%91%E6%8E%A7-%E4%B8%83-%E5%AE%8C%E6%95%B4%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E/)
