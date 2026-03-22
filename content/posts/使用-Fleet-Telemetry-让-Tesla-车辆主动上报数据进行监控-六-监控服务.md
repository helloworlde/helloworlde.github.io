---
date: 2025-09-29
description: "Tesla 车辆主动上报监控实战：Fleet Telemetry Prometheus 指标配置与 Grafana 可视化面板部署教程"
# image: ""
lastmod: 2026-03-22
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务"
keywords:
  - "Fleet Telemetry"
  - "Tesla"
  - "Prometheus"
  - "Grafana"
  - "metrics"
  - "dashboard"
  - "vehicle monitoring"
  - "observability"
slug: "fleet-telemetry-tesla-vehicle-monitoring-service"
aliases:
  - "/posts/使用-fleet-telemetry-让-tesla-车辆主动上报数据进行监控-六-监控服务/"
type: "post"
---

Fleet Telemetry 提供 Prometheus 监控接口，可以通过访问 `http://<host>:9091/metrics` 查看监控指标

首先在 Prometheus 中添加 Fleet Telemetry 的监控配置

```yaml
- job_name: "fleet-telemetry"
  static_configs:
    - targets: ["fleet.example.com:9091"]
```

然后将 Fleet Telemetry 的监控面板添加到 Grafana 中，将文件 [test/integration/grafana/provisioning/dashboards/dashboard.json](https://github.com/teslamotors/fleet-telemetry/blob/main/test/integration/grafana/provisioning/dashboards/dashboard.json) 的 JSON 内容导入到 Grafana 中，就可以看到相关的监控面板

![Grafana 中导入 Fleet Telemetry 监控面板的 Tesla 车辆数据](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-1.png)

![Grafana 监控面板展示特斯拉车辆实时数据](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-2.png)

## 参考文档

- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(一)申请证书](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-vehicle-monitoring-certificate/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(二)添加虚拟钥匙](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-virtual-key/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(三)部署服务](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-vehicle-monitoring-deployment/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(四)下发配置](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-vehicle-monitoring-push-config/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(五)数据处理](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-data-processing/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-vehicle-monitoring-service/)
- [使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明](https://blog.hellowood.dev/posts/fleet-telemetry-tesla-active-reporting-configuration/)
