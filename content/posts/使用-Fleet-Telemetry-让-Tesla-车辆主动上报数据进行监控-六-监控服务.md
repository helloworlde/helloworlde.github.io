---
date: 2025-09-29
# description: ""
# image: ""
lastmod: 2025-10-01
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(六)监控服务"
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

![homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-1.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-1.png)

![homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-2.png](https://img.hellowood.dev/picture/homelab-tesla-fleet-telemetry-monitor-grafana-dashboard-2.png)
