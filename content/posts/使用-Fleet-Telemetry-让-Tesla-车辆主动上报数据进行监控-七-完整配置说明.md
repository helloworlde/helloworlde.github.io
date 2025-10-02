---
date: 2025-09-30
# description: ""
# image: ""
lastmod: 2025-10-01
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明"
type: "post"
---

以下是 Tesla 车辆支持的属性和解释，由 AI 整理，并不完全准确，可以根据需要选择需要上报的数据

- Filed 配置属性
  | Field | Description | interval_seconds | minimum_delta | resend_interval_seconds |
  | ----------------------------------------- | ----------------------------------- | ---------------- | ------------- | ----------------------- |
  | VehicleSpeed | 车辆速度 (km/h 或 mph) | 1 | 0.01 | - |
  | PedalPosition | 加速踏板位置百分比 (%) | 1 | 0.1 | - |
  | Gear | 当前档位 (P/N/D/R) | 2 | - | - |
  | BrakePedal | 刹车踏板按下状态 | 2 | - | - |
  | BrakePedalPos | 刹车踏板位置百分比 (%) | 2 | 0.001 | - |
  | DiTorquemotor | 电机扭矩输出 (Nm) | 2 | 1 | - |
  | Location | GPS当前位置 (经纬度) | 5 | 0.00002 | 60 |
  | GpsHeading | GPS航向角度 (度) | 5 | 0.0001 | - |
  | Locked | 车辆锁闭状态 | 5 | - | - |
  | DoorState | 车门打开/关闭状态 | 5 | - | - |
  | LightsTurnSignal | 转向灯信号状态 | 10 | - | - |
  | LightsHighBeams | 远光灯开启状态 | 10 | - | - |
  | LightsHazardsActive | 危险警示灯激活状态 | 10 | - | - |
  | ChargeState | 充电状态 (充电中/未充电/完成等) | 10 | - | - |
  | DCChargingPower | DC充电功率 (kW) | 5 | 0.1 | - |
  | ACChargingPower | AC充电功率 (kW) | 5 | 1 | - |
  | ChargeAmps | 当前充电电流 (A) | 10 | 1 | - |
  | ChargeRateMilePerHour | 充电速率 (mi/h) | 10 | 0.1 | - |
  | ChargerVoltage | 充电器电压 (V) | 10 | 0.2 | - |
  | ChargerPhases | 充电相数 | 30 | - | - |
  | FastChargerPresent | 快速充电器连接状态 | 30 | - | - |
  | FastChargerType | 快速充电器类型 | 60 | - | - |
  | ChargingCableType | 充电电缆类型 | 300 | - | - |
  | ChargePort | 充电端口状态 | 60 | - | - |
  | ChargePortDoorOpen | 充电端口门打开状态 | 60 | - | - |
  | ChargePortLatch | 充电端口锁扣状态 | 60 | - | - |
  | DetailedChargeState | 详细充电状态信息 | 60 | - | - |
  | ChargeEnableRequest | 充电启用请求状态 | 60 | - | - |
  | ChargeCurrentRequest | 请求充电电流 (A) | 60 | - | - |
  | ChargeCurrentRequestMax | 最大请求充电电流 (A) | 60 | - | - |
  | ChargeLimitSoc | 充电上限SOC百分比 (%) | 300 | 1 | - |
  | TimeToFullCharge | 充满电预计剩余时间 (min) | 60 | 0.01 | - |
  | EstimatedHoursToChargeTermination | 预计充电完成剩余小时数 | 60 | 0.01 | - |
  | Soc | 电池荷电状态 (SOC，%) | 30 | 0.1 | - |
  | BatteryLevel | 电池电量百分比 (%) | 30 | 0.1 | - |
  | EnergyRemaining | 剩余电池能量 (kWh) | 30 | 0.1 | - |
  | PackVoltage | 电池组电压 (V) | 30 | 0.5 | - |
  | PackCurrent | 电池组电流 (A) | 30 | 0.1 | - |
  | BMSState | 电池管理系统当前状态 | 60 | - | - |
  | BmsFullchargecomplete | 电池管理系统充满电完成状态 | 300 | - | - |
  | DCDCEnable | DC-DC转换器启用状态 | 300 | - | - |
  | BatteryHeaterOn | 电池加热器启用状态 | 60 | - | - |
  | NotEnoughPowerToHeat | 电量不足以加热警告状态 | 300 | - | - |
  | IsolationResistance | 电池隔离电阻 (Ω) | 300 | 1 | 3600 |
  | BrickVoltageMax | 电池砖块最大电压值 (V) | 300 | 0.01 | - |
  | BrickVoltageMin | 电池砖块最小电压值 (V) | 300 | 0.01 | - |
  | NumBrickVoltageMax | 达到最大电压的电池砖块数量 | 300 | 1 | - |
  | NumBrickVoltageMin | 达到最小电压的电池砖块数量 | 300 | 1 | - |
  | ModuleTempMax | 电池模块最高温度 (℃) | 60 | 1 | - |
  | ModuleTempMin | 电池模块最低温度 (℃) | 60 | 1 | - |
  | NumModuleTempMax | 达到最高温度的电池模块数量 | 300 | 1 | - |
  | NumModuleTempMin | 达到最低温度的电池模块数量 | 300 | 1 | - |
  | DiStateF | 前电机运行状态 | 60 | - | - |
  | DiStateR | 后电机运行状态 | 60 | - | - |
  | DiStateREL | 左后电机运行状态 | 60 | - | - |
  | DiStateRER | 右后电机运行状态 | 60 | - | - |
  | DiAxleSpeedF | 前轴转速 (RPM) | 10 | 0.01 | - |
  | DiAxleSpeedR | 后轴转速 (RPM) | 10 | 0.01 | - |
  | DiAxleSpeedREL | 左后轴转速 (RPM) | 60 | 0.01 | - |
  | DiAxleSpeedRER | 右后轴转速 (RPM) | 60 | 0.01 | - |
  | DiTorqueActualF | 前电机实际扭矩 (Nm) | 5 | 1 | - |
  | DiTorqueActualR | 后电机实际扭矩 (Nm) | 5 | 1 | - |
  | DiTorqueActualREL | 左后电机实际扭矩 (Nm) | 5 | 1 | - |
  | DiTorqueActualRER | 右后电机实际扭矩 (Nm) | 5 | 1 | - |
  | DiSlaveTorqueCmd | 从电机扭矩指令 (Nm) | 5 | 1 | - |
  | DiMotorCurrentF | 前电机电流 (A) | 30 | 1 | - |
  | DiMotorCurrentR | 后电机电流 (A) | 30 | 1 | - |
  | DiMotorCurrentREL | 左后电机电流 (A) | 30 | 1 | - |
  | DiMotorCurrentRER | 右后电机电流 (A) | 30 | 1 | - |
  | DiVBatF | 前电机电池电压 (V) | 30 | 0.1 | - |
  | DiVBatR | 后电机电池电压 (V) | 30 | 1 | - |
  | DiVBatREL | 左后电机电池电压 (V) | 30 | 0.1 | - |
  | DiVBatRER | 右后电机电池电压 (V) | 30 | 0.1 | - |
  | DiStatorTempF | 前电机定子温度 (℃) | 60 | 1 | - |
  | DiStatorTempR | 后电机定子温度 (℃) | 60 | 1 | - |
  | DiStatorTempREL | 左后电机定子温度 (℃) | 60 | 1 | - |
  | DiStatorTempRER | 右后电机定子温度 (℃) | 60 | 1 | - |
  | DiHeatsinkTF | 前电机散热片温度 (℃) | 60 | 1 | - |
  | DiHeatsinkTR | 后电机散热片温度 (℃) | 60 | 1 | - |
  | DiHeatsinkTREL | 左后电机散热片温度 (℃) | 60 | 1 | - |
  | DiHeatsinkTRER | 右后电机散热片温度 (℃) | 60 | 1 | - |
  | DiInverterTF | 前电机逆变器温度 (℃) | 60 | 1 | - |
  | DiInverterTR | 后电机逆变器温度 (℃) | 60 | 1 | - |
  | DiInverterTREL | 左后电机逆变器温度 (℃) | 60 | 1 | - |
  | DiInverterTRER | 右后电机逆变器温度 (℃) | 60 | 1 | - |
  | DriveRail | 驱动总线系统状态 | 300 | - | - |
  | Odometer | 车辆总里程 (km/mi) | 300 | 0.1 | - |
  | RatedRange | 额定续航里程 (km/mi) | 300 | 0.1 | - |
  | EstBatteryRange | 估计电池续航里程 (km/mi) | 300 | 0.1 | - |
  | IdealBatteryRange | 理想电池续航里程 (km/mi) | 300 | 0.1 | - |
  | DCChargingEnergyIn | DC充电输入能量 (kWh) | 60 | 0.1 | - |
  | ACChargingEnergyIn | AC充电输入能量 (kWh) | 60 | 0.1 | - |
  | LifetimeEnergyUsed | 累计能量消耗 (kWh) | 300 | 0.1 | - |
  | LifetimeEnergyGainedRegen | 累计再生制动能量回收 (kWh) | 3600 | 0.1 | - |
  | InsideTemp | 车内温度 (℃) | 60 | 0.5 | - |
  | OutsideTemp | 车外温度 (℃) | 60 | 0.5 | - |
  | HvacACEnabled | 空调压缩机启用状态 | 60 | - | - |
  | HvacAutoMode | HVAC自动模式状态 | 60 | - | - |
  | HvacFanSpeed | HVAC风扇速度设置 | 60 | - | - |
  | HvacFanStatus | HVAC风扇运行状态 | 60 | - | - |
  | HvacLeftTemperatureRequest | 左侧HVAC温度设定 (℃) | 60 | 0.5 | - |
  | HvacRightTemperatureRequest | 右侧HVAC温度设定 (℃) | 60 | 0.5 | - |
  | HvacPower | HVAC电源消耗状态 | 60 | - | - |
  | HvacSteeringWheelHeatAuto | 方向盘加热自动模式 | 60 | - | - |
  | HvacSteeringWheelHeatLevel | 方向盘加热等级 | 60 | 1 | - |
  | SeatHeaterLeft | 左前座椅加热等级 | 60 | 1 | - |
  | SeatHeaterRight | 右前座椅加热等级 | 60 | 1 | - |
  | SeatHeaterRearLeft | 左后座椅加热等级 | 60 | 1 | - |
  | SeatHeaterRearRight | 右后座椅加热等级 | 60 | 1 | - |
  | SeatHeaterRearCenter | 中后座椅加热等级 | 60 | 1 | - |
  | AutoSeatClimateLeft | 左前座自动气候控制状态 | 60 | - | - |
  | AutoSeatClimateRight | 右前座自动气候控制状态 | 60 | - | - |
  | ClimateSeatCoolingFrontLeft | 左前座椅冷却状态 | 120 | - | - |
  | ClimateSeatCoolingFrontRight | 右前座椅冷却状态 | 120 | - | - |
  | RearSeatHeaters | 后排座椅加热状态 | 300 | - | - |
  | RearDisplayHvacEnabled | 后排显示屏HVAC控制启用状态 | 300 | - | - |
  | DefrostMode | 除霜模式状态 | 300 | - | - |
  | DefrostForPreconditioning | 预调节化霜状态 | 300 | - | - |
  | RearDefrostEnabled | 后窗除霜启用状态 | 300 | - | - |
  | ClimateKeeperMode | 气候保持模式 | 300 | - | - |
  | CabinOverheatProtectionMode | 驾驶舱过热保护模式 | 300 | - | - |
  | CabinOverheatProtectionTemperatureLimit | 驾驶舱过热保护温度上限 (℃) | 300 | 1 | - |
  | EfficiencyPackage | 高效驾驶套件启用状态 | 300 | - | - |
  | WiperHeatEnabled | 雨刷加热启用状态 | 300 | - | - |
  | DriverSeatBelt | 驾驶员安全带扣紧状态 | 60 | - | - |
  | PassengerSeatBelt | 副驾驶安全带扣紧状态 | 60 | - | - |
  | DriverSeatOccupied | 驾驶员座位占用状态 | 60 | - | - |
  | LateralAcceleration | 横向加速度 (m/s²) | 60 | 0.01 | - |
  | LongitudinalAcceleration | 纵向加速度 (m/s²) | 60 | 0.01 | - |
  | CruiseSetSpeed | 定速巡航设定速度 (km/h) | 30 | 1 | - |
  | CruiseFollowDistance | 自适应巡航跟车距离设置 | 3600 | - | - |
  | SpeedLimitMode | 限速模式启用状态 | 3600 | - | - |
  | CurrentLimitMph | 当前限速值 (mph) | 60 | 1 | - |
  | SpeedLimitWarning | 超速警告设置 | 3600 | - | - |
  | ForwardCollisionWarning | 前向碰撞警告系统状态 | 3600 | - | - |
  | AutomaticEmergencyBrakingOff | 自动紧急制动关闭状态 | 3600 | - | - |
  | LaneDepartureAvoidance | 车道偏离避免系统状态 | 3600 | - | - |
  | EmergencyLaneDepartureAvoidance | 紧急车道偏离避免系统状态 | 3600 | - | - |
  | BlindSpotCollisionWarningChime | 盲点碰撞警告蜂鸣器状态 | 3600 | - | - |
  | AutomaticBlindSpotCamera | 自动盲点摄像头启用状态 | 3600 | - | - |
  | GpsState | GPS信号可用状态 | 3600 | - | - |
  | TpmsPressureFl | 前左轮胎气压 (psi/bar) | 300 | 0.01 | - |
  | TpmsPressureFr | 前右轮胎气压 (psi/bar) | 300 | 0.01 | - |
  | TpmsPressureRl | 后左轮胎气压 (psi/bar) | 300 | 0.01 | - |
  | TpmsPressureRr | 后右轮胎气压 (psi/bar) | 300 | 0.01 | - |
  | TpmsHardWarnings | 胎压监测硬警告信息 | 300 | - | - |
  | TpmsSoftWarnings | 胎压监测软警告信息 | 300 | - | - |
  | TpmsLastSeenPressureTimeFl | 前左胎压最后读取时间 | 300 | - | - |
  | TpmsLastSeenPressureTimeFr | 前右胎压最后读取时间 | 300 | - | - |
  | TpmsLastSeenPressureTimeRl | 后左胎压最后读取时间 | 300 | - | - |
  | TpmsLastSeenPressureTimeRr | 后右胎压最后读取时间 | 300 | - | - |
  | FdWindow | 前左车窗位置状态 | 60 | - | - |
  | FpWindow | 前右车窗位置状态 | 60 | - | - |
  | RdWindow | 后左车窗位置状态 | 60 | - | - |
  | RpWindow | 后右车窗位置状态 | 60 | - | - |
  | SunroofInstalled | 天窗安装状态 | 300 | - | - |
  | TonneauPosition | 货厢盖位置状态 | 300 | - | - |
  | TonneauOpenPercent | 货厢盖打开百分比 (%) | 300 | 1 | - |
  | TonneauTentMode | 货厢盖帐篷模式状态 | 300 | - | - |
  | OffroadLightbarPresent | 越野灯条安装状态 | 3600 | - | - |
  | CenterDisplay | 中控显示屏状态 | 60 | - | - |
  | MediaPlaybackStatus | 媒体播放状态 | 120 | - | - |
  | MediaPlaybackSource | 媒体播放来源 | 120 | - | - |
  | MediaNowPlayingTitle | 当前播放曲目标题 | 300 | - | - |
  | MediaNowPlayingArtist | 当前播放艺术家名称 | 300 | - | - |
  | MediaNowPlayingAlbum | 当前播放专辑名称 | 300 | - | - |
  | MediaNowPlayingStation | 当前播放电台名称 | 300 | - | - |
  | MediaNowPlayingDuration | 当前播放总时长 (秒) | 300 | - | - |
  | MediaNowPlayingElapsed | 当前播放已过时间 (秒) | 300 | - | - |
  | MediaAudioVolume | 媒体音频音量水平 | 300 | 1 | - |
  | MediaAudioVolumeMax | 媒体音频最大音量 | 300 | - | - |
  | MediaAudioVolumeIncrement | 媒体音频音量增量步长 | 300 | - | - |
  | SeatVentEnabled | 座椅通风启用状态 | 300 | - | - |
  | RemoteStartEnabled | 远程启动功能启用状态 | 300 | - | - |
  | ServiceMode | 服务/维修模式状态 | 3600 | - | - |
  | SentryMode | 哨兵模式启用状态 | 300 | - | - |
  | ValetModeEnabled | 代客泊车模式启用状态 | 300 | - | - |
  | GuestModeEnabled | 访客模式启用状态 | 300 | - | - |
  | GuestModeMobileAccessState | 访客模式移动访问权限状态 | 60 | - | - |
  | PinToDriveEnabled | PIN to Drive安全功能启用状态 | 300 | - | - |
  | PairedPhoneKeyAndKeyFobQty | 配对手机钥匙和钥匙扣数量 | 3600 | - | - |
  | HomelinkDeviceCount | HomeLink设备配对数量 | 3600 | - | - |
  | HomelinkNearby | 附近HomeLink设备检测状态 | 3600 | - | - |
  | PowershareStatus | PowerShare功能状态 | 300 | - | - |
  | PowershareType | PowerShare类型 | 300 | - | - |
  | PowershareHoursLeft | PowerShare剩余可用小时数 | 300 | - | - |
  | PowershareInstantaneousPowerKW | PowerShare瞬时功率 (kW) | 300 | 0.1 | - |
  | PowershareStopReason | PowerShare停止原因 | 300 | - | - |
  | SettingDistanceUnit | 距离单位设置 (km/mi) | 3600 | - | - |
  | SettingTemperatureUnit | 温度单位设置 (℃/℉) | 3600 | - | - |
  | Setting24HourTime | 24小时制时间显示设置 | 3600 | - | - |
  | SettingTirePressureUnit | 胎压单位设置 (psi/bar) | 3600 | - | - |
  | SettingChargeUnit | 充电单位设置 (kWh/mi) | 3600 | - | - |
  | RightHandDrive | 右舵驾驶车辆标识 | 3600 | - | - |
  | EuropeVehicle | 欧洲规格车辆标识 | 3600 | - | - |
  | WheelType | 轮毂类型 | 3600 | - | - |
  | CarType | 车辆车型类型 | 3600 | - | - |
  | Trim | 车辆配置等级 | 3600 | - | - |
  | ExteriorColor | 车身外部颜色 | 3600 | - | - |
  | RoofColor | 车顶颜色 | 3600 | - | - |
  | VehicleName | 车辆自定义名称 | 3600 | - | - |
  | Version | 软件版本号 | 3600 | - | - |
  | SoftwareUpdateVersion | 软件更新版本号 | 300 | - | - |
  | SoftwareUpdateDownloadPercentComplete | 软件更新下载完成百分比 (%) | 300 | 1 | - |
  | SoftwareUpdateInstallationPercentComplete | 软件更新安装完成百分比 (%) | 300 | 1 | - |
  | SoftwareUpdateExpectedDurationMinutes | 软件更新预计持续时间 (分钟) | 300 | - | - |
  | SoftwareUpdateScheduledStartTime | 软件更新计划开始时间 | 300 | - | - |
  | SuperchargerSessionTripPlanner | 超级充电会话行程规划信息 | 3600 | - | - |
  | RouteLastUpdated | 导航路线最后更新时间 (固件2024.26+) | 300 | - | - |
  | RouteLine | 当前导航路线数据 (固件2024.26+) | 300 | - | - |
  | MilesToArrival | 导航剩余里程 (mi，固件2024.26+) | 300 | 0.1 | - |
  | MinutesToArrival | 导航剩余时间 (min，固件2024.26+) | 300 | 1 | - |
  | ExpectedEnergyPercentAtTripArrival | 预计行程结束时剩余电量百分比 (%) | 300 | 1 | - |
  | RouteTrafficMinutesDelay | 导航路线交通延迟 (分钟) | 300 | 1 | - |
  | OriginLocation | 导航起点位置 (经纬度，固件2024.26+) | 300 | 0.00001 | - |
  | DestinationLocation | 导航终点位置 (经纬度，固件2024.26+) | 300 | 0.00001 | - |
  | DestinationName | 导航目的地名称 (固件2024.26+) | 60 | - | - |
  | LocatedAtHome | 车辆位于家位置状态 | 300 | - | - |
  | LocatedAtWork | 车辆位于工作位置状态 | 300 | - | - |
  | LocatedAtFavorite | 车辆位于收藏位置状态 | 300 | - | - |
  | Deprecated_2 | 已废弃字段 (请忽略) | 3600 | - | - |
  | Deprecated_3 | 已废弃字段 (请忽略) | 3600 | - | - |

- 下发的配置 JSON

下发的配置中删除了部分过时和 Cybertruck 特有的字段，可按需调整

```json
{
  "config": {
    "delivery_policy": "latest",
    "prefer_typed": true,
    "port": 12345,
    "alert_types": ["service", "customer", "service-fix"],
    "ca": "{{ca}}",
    "hostname": "{{hostname}}",
    "vins": ["{{vin}}"],
    "fields": {
      "VehicleSpeed": {
        "interval_seconds": 1,
        "minimum_delta": 0.01,
        "description": "车辆速度 (km/h 或 mph)"
      },
      "PedalPosition": {
        "interval_seconds": 1,
        "minimum_delta": 0.1,
        "description": "加速踏板位置百分比 (%)"
      },
      "Gear": {
        "interval_seconds": 2,
        "description": "当前档位 (P/N/D/R)"
      },
      "BrakePedal": {
        "interval_seconds": 2,
        "description": "刹车踏板按下状态"
      },
      "BrakePedalPos": {
        "interval_seconds": 2,
        "minimum_delta": 0.001,
        "description": "刹车踏板位置百分比 (%)"
      },
      "DiTorquemotor": {
        "interval_seconds": 2,
        "minimum_delta": 1,
        "description": "电机扭矩输出 (Nm)"
      },
      "Location": {
        "interval_seconds": 5,
        "minimum_delta": 0.00002,
        "resend_interval_seconds": 60,
        "description": "GPS当前位置 (经纬度)"
      },
      "GpsHeading": {
        "interval_seconds": 5,
        "minimum_delta": 0.0001,
        "description": "GPS航向角度 (度)"
      },
      "Locked": {
        "interval_seconds": 5,
        "description": "车辆锁闭状态"
      },
      "DoorState": {
        "interval_seconds": 5,
        "description": "车门打开/关闭状态"
      },
      "LightsTurnSignal": {
        "interval_seconds": 10,
        "description": "转向灯信号状态"
      },
      "LightsHighBeams": {
        "interval_seconds": 10,
        "description": "远光灯开启状态"
      },
      "LightsHazardsActive": {
        "interval_seconds": 10,
        "description": "危险警示灯激活状态"
      },
      "ChargeState": {
        "interval_seconds": 10,
        "description": "充电状态 (充电中/未充电/完成等)"
      },
      "DCChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 0.1,
        "description": "DC充电功率 (kW)"
      },
      "ACChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "AC充电功率 (kW)"
      },
      "ChargeAmps": {
        "interval_seconds": 10,
        "minimum_delta": 1,
        "description": "当前充电电流 (A)"
      },
      "ChargeRateMilePerHour": {
        "interval_seconds": 10,
        "minimum_delta": 0.1,
        "description": "充电速率 (mi/h)"
      },
      "ChargerVoltage": {
        "interval_seconds": 10,
        "minimum_delta": 0.2,
        "description": "充电器电压 (V)"
      },
      "ChargerPhases": {
        "interval_seconds": 30,
        "description": "充电相数"
      },
      "FastChargerPresent": {
        "interval_seconds": 30,
        "description": "快速充电器连接状态"
      },
      "FastChargerType": {
        "interval_seconds": 60,
        "description": "快速充电器类型"
      },
      "ChargingCableType": {
        "interval_seconds": 300,
        "description": "充电电缆类型"
      },
      "ChargePort": {
        "interval_seconds": 60,
        "description": "充电端口状态"
      },
      "ChargePortDoorOpen": {
        "interval_seconds": 60,
        "description": "充电端口门打开状态"
      },
      "ChargePortLatch": {
        "interval_seconds": 60,
        "description": "充电端口锁扣状态"
      },
      "DetailedChargeState": {
        "interval_seconds": 60,
        "description": "详细充电状态信息"
      },
      "ChargeEnableRequest": {
        "interval_seconds": 60,
        "description": "充电启用请求状态"
      },
      "ChargeCurrentRequest": {
        "interval_seconds": 60,
        "description": "请求充电电流 (A)"
      },
      "ChargeCurrentRequestMax": {
        "interval_seconds": 60,
        "description": "最大请求充电电流 (A)"
      },
      "ChargeLimitSoc": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "充电上限SOC百分比 (%)"
      },
      "TimeToFullCharge": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "充满电预计剩余时间 (min)"
      },
      "EstimatedHoursToChargeTermination": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "预计充电完成剩余小时数"
      },
      "Soc": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "电池荷电状态 (SOC，%)"
      },
      "BatteryLevel": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "电池电量百分比 (%)"
      },
      "EnergyRemaining": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "剩余电池能量 (kWh)"
      },
      "PackVoltage": {
        "interval_seconds": 30,
        "minimum_delta": 0.5,
        "description": "电池组电压 (V)"
      },
      "PackCurrent": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "电池组电流 (A)"
      },
      "BMSState": {
        "interval_seconds": 60,
        "description": "电池管理系统当前状态"
      },
      "BmsFullchargecomplete": {
        "interval_seconds": 300,
        "description": "电池管理系统充满电完成状态"
      },
      "DCDCEnable": {
        "interval_seconds": 300,
        "description": "DC-DC转换器启用状态"
      },
      "BatteryHeaterOn": {
        "interval_seconds": 60,
        "description": "电池加热器启用状态"
      },
      "NotEnoughPowerToHeat": {
        "interval_seconds": 300,
        "description": "电量不足以加热警告状态"
      },
      "IsolationResistance": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 3600,
        "description": "电池隔离电阻 (Ω)"
      },
      "BrickVoltageMax": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "电池砖块最大电压值 (V)"
      },
      "BrickVoltageMin": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "电池砖块最小电压值 (V)"
      },
      "NumBrickVoltageMax": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "达到最大电压的电池砖块数量"
      },
      "NumBrickVoltageMin": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "达到最小电压的电池砖块数量"
      },
      "ModuleTempMax": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "电池模块最高温度 (℃)"
      },
      "ModuleTempMin": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "电池模块最低温度 (℃)"
      },
      "NumModuleTempMax": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "达到最高温度的电池模块数量"
      },
      "NumModuleTempMin": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "达到最低温度的电池模块数量"
      },
      "DiStateF": {
        "interval_seconds": 60,
        "description": "前电机运行状态"
      },
      "DiStateR": {
        "interval_seconds": 60,
        "description": "后电机运行状态"
      },
      "DiStateREL": {
        "interval_seconds": 60,
        "description": "左后电机运行状态"
      },
      "DiStateRER": {
        "interval_seconds": 60,
        "description": "右后电机运行状态"
      },
      "DiAxleSpeedF": {
        "interval_seconds": 10,
        "minimum_delta": 0.01,
        "description": "前轴转速 (RPM)"
      },
      "DiAxleSpeedR": {
        "interval_seconds": 10,
        "minimum_delta": 0.01,
        "description": "后轴转速 (RPM)"
      },
      "DiAxleSpeedREL": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "左后轴转速 (RPM)"
      },
      "DiAxleSpeedRER": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "右后轴转速 (RPM)"
      },
      "DiTorqueActualF": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "前电机实际扭矩 (Nm)"
      },
      "DiTorqueActualR": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "后电机实际扭矩 (Nm)"
      },
      "DiTorqueActualREL": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "左后电机实际扭矩 (Nm)"
      },
      "DiTorqueActualRER": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "右后电机实际扭矩 (Nm)"
      },
      "DiSlaveTorqueCmd": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "description": "从电机扭矩指令 (Nm)"
      },
      "DiMotorCurrentF": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "前电机电流 (A)"
      },
      "DiMotorCurrentR": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "后电机电流 (A)"
      },
      "DiMotorCurrentREL": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "左后电机电流 (A)"
      },
      "DiMotorCurrentRER": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "右后电机电流 (A)"
      },
      "DiVBatF": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "前电机电池电压 (V)"
      },
      "DiVBatR": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "后电机电池电压 (V)"
      },
      "DiVBatREL": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "左后电机电池电压 (V)"
      },
      "DiVBatRER": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "description": "右后电机电池电压 (V)"
      },
      "DiStatorTempF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "前电机定子温度 (℃)"
      },
      "DiStatorTempR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "后电机定子温度 (℃)"
      },
      "DiStatorTempREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "左后电机定子温度 (℃)"
      },
      "DiStatorTempRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "右后电机定子温度 (℃)"
      },
      "DiHeatsinkTF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "前电机散热片温度 (℃)"
      },
      "DiHeatsinkTR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "后电机散热片温度 (℃)"
      },
      "DiHeatsinkTREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "左后电机散热片温度 (℃)"
      },
      "DiHeatsinkTRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "右后电机散热片温度 (℃)"
      },
      "DiInverterTF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "前电机逆变器温度 (℃)"
      },
      "DiInverterTR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "后电机逆变器温度 (℃)"
      },
      "DiInverterTREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "左后电机逆变器温度 (℃)"
      },
      "DiInverterTRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "右后电机逆变器温度 (℃)"
      },
      "DriveRail": {
        "interval_seconds": 300,
        "description": "驱动总线系统状态"
      },
      "Odometer": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "车辆总里程 (km/mi)"
      },
      "RatedRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "额定续航里程 (km/mi)"
      },
      "EstBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "估计电池续航里程 (km/mi)"
      },
      "IdealBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "理想电池续航里程 (km/mi)"
      },
      "DCChargingEnergyIn": {
        "interval_seconds": 60,
        "minimum_delta": 0.1,
        "description": "DC充电输入能量 (kWh)"
      },
      "ACChargingEnergyIn": {
        "interval_seconds": 60,
        "minimum_delta": 0.1,
        "description": "AC充电输入能量 (kWh)"
      },
      "LifetimeEnergyUsed": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "累计能量消耗 (kWh)"
      },
      "LifetimeEnergyGainedRegen": {
        "interval_seconds": 3600,
        "minimum_delta": 0.1,
        "description": "累计再生制动能量回收 (kWh)"
      },
      "InsideTemp": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "description": "车内温度 (℃)"
      },
      "OutsideTemp": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "description": "车外温度 (℃)"
      },
      "HvacACEnabled": {
        "interval_seconds": 60,
        "description": "空调压缩机启用状态"
      },
      "HvacAutoMode": {
        "interval_seconds": 60,
        "description": "HVAC自动模式状态"
      },
      "HvacFanSpeed": {
        "interval_seconds": 60,
        "description": "HVAC风扇速度设置"
      },
      "HvacFanStatus": {
        "interval_seconds": 60,
        "description": "HVAC风扇运行状态"
      },
      "HvacLeftTemperatureRequest": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "description": "左侧HVAC温度设定 (℃)"
      },
      "HvacRightTemperatureRequest": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "description": "右侧HVAC温度设定 (℃)"
      },
      "HvacPower": {
        "interval_seconds": 60,
        "description": "HVAC电源消耗状态"
      },
      "HvacSteeringWheelHeatAuto": {
        "interval_seconds": 60,
        "description": "方向盘加热自动模式"
      },
      "HvacSteeringWheelHeatLevel": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "方向盘加热等级"
      },
      "SeatHeaterLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "左前座椅加热等级"
      },
      "SeatHeaterRight": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "右前座椅加热等级"
      },
      "SeatHeaterRearLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "左后座椅加热等级"
      },
      "SeatHeaterRearRight": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "右后座椅加热等级"
      },
      "SeatHeaterRearCenter": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "中后座椅加热等级"
      },
      "AutoSeatClimateLeft": {
        "interval_seconds": 60,
        "description": "左前座自动气候控制状态"
      },
      "AutoSeatClimateRight": {
        "interval_seconds": 60,
        "description": "右前座自动气候控制状态"
      },
      "ClimateSeatCoolingFrontLeft": {
        "interval_seconds": 120,
        "description": "左前座椅冷却状态"
      },
      "ClimateSeatCoolingFrontRight": {
        "interval_seconds": 120,
        "description": "右前座椅冷却状态"
      },
      "RearSeatHeaters": {
        "interval_seconds": 300,
        "description": "后排座椅加热状态"
      },
      "RearDisplayHvacEnabled": {
        "interval_seconds": 300,
        "description": "后排显示屏HVAC控制启用状态"
      },
      "DefrostMode": {
        "interval_seconds": 300,
        "description": "除霜模式状态"
      },
      "DefrostForPreconditioning": {
        "interval_seconds": 300,
        "description": "预调节化霜状态"
      },
      "RearDefrostEnabled": {
        "interval_seconds": 300,
        "description": "后窗除霜启用状态"
      },
      "ClimateKeeperMode": {
        "interval_seconds": 300,
        "description": "气候保持模式"
      },
      "CabinOverheatProtectionMode": {
        "interval_seconds": 300,
        "description": "驾驶舱过热保护模式"
      },
      "CabinOverheatProtectionTemperatureLimit": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "驾驶舱过热保护温度上限 (℃)"
      },
      "EfficiencyPackage": {
        "interval_seconds": 300,
        "description": "高效驾驶套件启用状态"
      },
      "WiperHeatEnabled": {
        "interval_seconds": 300,
        "description": "雨刷加热启用状态"
      },
      "DriverSeatBelt": {
        "interval_seconds": 60,
        "description": "驾驶员安全带扣紧状态"
      },
      "PassengerSeatBelt": {
        "interval_seconds": 60,
        "description": "副驾驶安全带扣紧状态"
      },
      "DriverSeatOccupied": {
        "interval_seconds": 60,
        "description": "驾驶员座位占用状态"
      },
      "LateralAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "横向加速度 (m/s²)"
      },
      "LongitudinalAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "description": "纵向加速度 (m/s²)"
      },
      "CruiseSetSpeed": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "description": "定速巡航设定速度 (km/h)"
      },
      "CruiseFollowDistance": {
        "interval_seconds": 3600,
        "description": "自适应巡航跟车距离设置"
      },
      "SpeedLimitMode": {
        "interval_seconds": 3600,
        "description": "限速模式启用状态"
      },
      "CurrentLimitMph": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "description": "当前限速值 (mph)"
      },
      "SpeedLimitWarning": {
        "interval_seconds": 3600,
        "description": "超速警告设置"
      },
      "ForwardCollisionWarning": {
        "interval_seconds": 3600,
        "description": "前向碰撞警告系统状态"
      },
      "AutomaticEmergencyBrakingOff": {
        "interval_seconds": 3600,
        "description": "自动紧急制动关闭状态"
      },
      "LaneDepartureAvoidance": {
        "interval_seconds": 3600,
        "description": "车道偏离避免系统状态"
      },
      "EmergencyLaneDepartureAvoidance": {
        "interval_seconds": 3600,
        "description": "紧急车道偏离避免系统状态"
      },
      "BlindSpotCollisionWarningChime": {
        "interval_seconds": 3600,
        "description": "盲点碰撞警告蜂鸣器状态"
      },
      "AutomaticBlindSpotCamera": {
        "interval_seconds": 3600,
        "description": "自动盲点摄像头启用状态"
      },
      "GpsState": {
        "interval_seconds": 3600,
        "description": "GPS信号可用状态"
      },
      "TpmsPressureFl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "前左轮胎气压 (psi/bar)"
      },
      "TpmsPressureFr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "前右轮胎气压 (psi/bar)"
      },
      "TpmsPressureRl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "后左轮胎气压 (psi/bar)"
      },
      "TpmsPressureRr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "description": "后右轮胎气压 (psi/bar)"
      },
      "TpmsHardWarnings": {
        "interval_seconds": 300,
        "description": "胎压监测硬警告信息"
      },
      "TpmsSoftWarnings": {
        "interval_seconds": 300,
        "description": "胎压监测软警告信息"
      },
      "TpmsLastSeenPressureTimeFl": {
        "interval_seconds": 300,
        "description": "前左胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeFr": {
        "interval_seconds": 300,
        "description": "前右胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeRl": {
        "interval_seconds": 300,
        "description": "后左胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeRr": {
        "interval_seconds": 300,
        "description": "后右胎压最后读取时间"
      },
      "FdWindow": {
        "interval_seconds": 60,
        "description": "前左车窗位置状态"
      },
      "FpWindow": {
        "interval_seconds": 60,
        "description": "前右车窗位置状态"
      },
      "RdWindow": {
        "interval_seconds": 60,
        "description": "后左车窗位置状态"
      },
      "RpWindow": {
        "interval_seconds": 60,
        "description": "后右车窗位置状态"
      },
      "SunroofInstalled": {
        "interval_seconds": 300,
        "description": "天窗安装状态"
      },
      "TonneauPosition": {
        "interval_seconds": 300,
        "description": "货厢盖位置状态"
      },
      "TonneauOpenPercent": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "货厢盖打开百分比 (%)"
      },
      "TonneauTentMode": {
        "interval_seconds": 300,
        "description": "货厢盖帐篷模式状态"
      },
      "OffroadLightbarPresent": {
        "interval_seconds": 3600,
        "description": "越野灯条安装状态"
      },
      "CenterDisplay": {
        "interval_seconds": 60,
        "description": "中控显示屏状态"
      },
      "MediaPlaybackStatus": {
        "interval_seconds": 120,
        "description": "媒体播放状态"
      },
      "MediaPlaybackSource": {
        "interval_seconds": 120,
        "description": "媒体播放来源"
      },
      "MediaNowPlayingTitle": {
        "interval_seconds": 300,
        "description": "当前播放曲目标题"
      },
      "MediaNowPlayingArtist": {
        "interval_seconds": 300,
        "description": "当前播放艺术家名称"
      },
      "MediaNowPlayingAlbum": {
        "interval_seconds": 300,
        "description": "当前播放专辑名称"
      },
      "MediaNowPlayingStation": {
        "interval_seconds": 300,
        "description": "当前播放电台名称"
      },
      "MediaNowPlayingDuration": {
        "interval_seconds": 300,
        "description": "当前播放总时长 (秒)"
      },
      "MediaNowPlayingElapsed": {
        "interval_seconds": 300,
        "description": "当前播放已过时间 (秒)"
      },
      "MediaAudioVolume": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "媒体音频音量水平"
      },
      "MediaAudioVolumeMax": {
        "interval_seconds": 300,
        "description": "媒体音频最大音量"
      },
      "MediaAudioVolumeIncrement": {
        "interval_seconds": 300,
        "description": "媒体音频音量增量步长"
      },
      "SeatVentEnabled": {
        "interval_seconds": 300,
        "description": "座椅通风启用状态"
      },
      "RemoteStartEnabled": {
        "interval_seconds": 300,
        "description": "远程启动功能启用状态"
      },
      "ServiceMode": {
        "interval_seconds": 3600,
        "description": "服务/维修模式状态"
      },
      "SentryMode": {
        "interval_seconds": 300,
        "description": "哨兵模式启用状态"
      },
      "ValetModeEnabled": {
        "interval_seconds": 300,
        "description": "代客泊车模式启用状态"
      },
      "GuestModeEnabled": {
        "interval_seconds": 300,
        "description": "访客模式启用状态"
      },
      "GuestModeMobileAccessState": {
        "interval_seconds": 60,
        "description": "访客模式移动访问权限状态"
      },
      "PinToDriveEnabled": {
        "interval_seconds": 300,
        "description": "PIN to Drive安全功能启用状态"
      },
      "PairedPhoneKeyAndKeyFobQty": {
        "interval_seconds": 3600,
        "description": "配对手机钥匙和钥匙扣数量"
      },
      "HomelinkDeviceCount": {
        "interval_seconds": 3600,
        "description": "HomeLink设备配对数量"
      },
      "HomelinkNearby": {
        "interval_seconds": 3600,
        "description": "附近HomeLink设备检测状态"
      },
      "PowershareStatus": {
        "interval_seconds": 300,
        "description": "PowerShare功能状态"
      },
      "PowershareType": {
        "interval_seconds": 300,
        "description": "PowerShare类型"
      },
      "PowershareHoursLeft": {
        "interval_seconds": 300,
        "description": "PowerShare剩余可用小时数"
      },
      "PowershareInstantaneousPowerKW": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "PowerShare瞬时功率 (kW)"
      },
      "PowershareStopReason": {
        "interval_seconds": 300,
        "description": "PowerShare停止原因"
      },
      "SettingDistanceUnit": {
        "interval_seconds": 3600,
        "description": "距离单位设置 (km/mi)"
      },
      "SettingTemperatureUnit": {
        "interval_seconds": 3600,
        "description": "温度单位设置 (℃/℉)"
      },
      "Setting24HourTime": {
        "interval_seconds": 3600,
        "description": "24小时制时间显示设置"
      },
      "SettingTirePressureUnit": {
        "interval_seconds": 3600,
        "description": "胎压单位设置 (psi/bar)"
      },
      "SettingChargeUnit": {
        "interval_seconds": 3600,
        "description": "充电单位设置 (kWh/mi)"
      },
      "RightHandDrive": {
        "interval_seconds": 3600,
        "description": "右舵驾驶车辆标识"
      },
      "EuropeVehicle": {
        "interval_seconds": 3600,
        "description": "欧洲规格车辆标识"
      },
      "WheelType": {
        "interval_seconds": 3600,
        "description": "轮毂类型"
      },
      "CarType": {
        "interval_seconds": 3600,
        "description": "车辆车型类型"
      },
      "Trim": {
        "interval_seconds": 3600,
        "description": "车辆配置等级"
      },
      "ExteriorColor": {
        "interval_seconds": 3600,
        "description": "车身外部颜色"
      },
      "RoofColor": {
        "interval_seconds": 3600,
        "description": "车顶颜色"
      },
      "VehicleName": {
        "interval_seconds": 3600,
        "description": "车辆自定义名称"
      },
      "Version": {
        "interval_seconds": 3600,
        "description": "软件版本号"
      },
      "SoftwareUpdateVersion": {
        "interval_seconds": 300,
        "description": "软件更新版本号"
      },
      "SoftwareUpdateDownloadPercentComplete": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "软件更新下载完成百分比 (%)"
      },
      "SoftwareUpdateInstallationPercentComplete": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "软件更新安装完成百分比 (%)"
      },
      "SoftwareUpdateExpectedDurationMinutes": {
        "interval_seconds": 300,
        "description": "软件更新预计持续时间 (分钟)"
      },
      "SoftwareUpdateScheduledStartTime": {
        "interval_seconds": 300,
        "description": "软件更新计划开始时间"
      },
      "SuperchargerSessionTripPlanner": {
        "interval_seconds": 3600,
        "description": "超级充电会话行程规划信息"
      },
      "RouteLastUpdated": {
        "interval_seconds": 300,
        "description": "导航路线最后更新时间 (固件2024.26+)"
      },
      "RouteLine": {
        "interval_seconds": 300,
        "description": "当前导航路线数据 (固件2024.26+)"
      },
      "MilesToArrival": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "description": "导航剩余里程 (mi，固件2024.26+)"
      },
      "MinutesToArrival": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "导航剩余时间 (min，固件2024.26+)"
      },
      "ExpectedEnergyPercentAtTripArrival": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "预计行程结束时剩余电量百分比 (%)"
      },
      "RouteTrafficMinutesDelay": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "description": "导航路线交通延迟 (分钟)"
      },
      "OriginLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001,
        "description": "导航起点位置 (经纬度，固件2024.26+)"
      },
      "DestinationLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001,
        "description": "导航终点位置 (经纬度，固件2024.26+)"
      },
      "DestinationName": {
        "interval_seconds": 60,
        "description": "导航目的地名称 (固件2024.26+)"
      },
      "LocatedAtHome": {
        "interval_seconds": 300,
        "description": "车辆位于家位置状态"
      },
      "LocatedAtWork": {
        "interval_seconds": 300,
        "description": "车辆位于工作位置状态"
      },
      "LocatedAtFavorite": {
        "interval_seconds": 300,
        "description": "车辆位于收藏位置状态"
      },
      "Deprecated_2": {
        "interval_seconds": 3600,
        "description": "已废弃字段 (请忽略)"
      },
      "Deprecated_3": {
        "interval_seconds": 3600,
        "description": "已废弃字段 (请忽略)"
      }
    }
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
