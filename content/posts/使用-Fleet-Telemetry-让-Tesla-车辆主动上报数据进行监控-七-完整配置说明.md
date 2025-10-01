---
date: 2025-09-30
# description: ""
# image: ""
lastmod: 2025-09-30
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明"
type: "post"
---

以下是 Tesla 车辆支持的属性和解释，由 AI 整理，并不完全准确，可以根据需要选择需要上报的数据

- Filed 配置属性

| ID  | Field                                     | Description                       |
| --- | ----------------------------------------- | --------------------------------- | --- |
| 0   | Unknown                                   | 未知或未定义字段                  |
| 1   | DriveRail                                 | 驱动总线状态                      |
| 2   | ChargeState                               | 充电状态（充电/未充电/完成等）    |
| 3   | BmsFullchargecomplete                     | 电池管理系统是否充满              |
| 4   | VehicleSpeed                              | 车辆速度（km/h 或 mph）           |
| 5   | Odometer                                  | 总里程（公里或英里）              |
| 6   | PackVoltage                               | 电池组电压（V）                   |
| 7   | PackCurrent                               | 电池组电流（A）                   |
| 8   | Soc                                       | 电池荷电状态（SOC，%）            |
| 9   | DCDCEnable                                | DC-DC 转换器是否启用              |
| 10  | Gear                                      | 当前档位（P/N/D/R）               |
| 11  | IsolationResistance                       | 电池绝缘电阻                      |
| 12  | PedalPosition                             | 油门踏板位置（%）                 |
| 13  | BrakePedal                                | 刹车踏板状态                      |
| 14  | DiStateR                                  | 后电机状态                        | x   |
| 15  | DiHeatsinkTR                              | 后电机散热片温度                  |
| 16  | DiAxleSpeedR                              | 后轴速度                          |
| 17  | DiTorquemotor                             | 电机扭矩                          |
| 18  | DiStatorTempR                             | 后电机定子温度                    |
| 19  | DiVBatR                                   | 后电机电池电压                    |
| 20  | DiMotorCurrentR                           | 后电机电流                        |
| 21  | Location                                  | GPS 位置（经纬度）                |
| 22  | GpsState                                  | GPS 状态（是否可用）              |
| 23  | GpsHeading                                | GPS 航向（角度）                  |
| 24  | NumBrickVoltageMax                        | 电池模块最大电压个数              |
| 25  | BrickVoltageMax                           | 最大电压值                        |
| 26  | NumBrickVoltageMin                        | 电池模块最小电压个数              |
| 27  | BrickVoltageMin                           | 最小电压值                        |
| 28  | NumModuleTempMax                          | 模块最高温度个数                  |
| 29  | ModuleTempMax                             | 模块最高温度值（℃）               |
| 30  | NumModuleTempMin                          | 模块最低温度个数                  |
| 31  | ModuleTempMin                             | 模块最低温度值（℃）               |
| 32  | RatedRange                                | 额定续航里程（km 或 mi）          |
| 33  | Hvil                                      | 高压互锁状态                      |
| 34  | DCChargingEnergyIn                        | DC 充电输入能量（kWh）            |
| 35  | DCChargingPower                           | DC 充电功率（kW）                 |
| 36  | ACChargingEnergyIn                        | AC 充电输入能量（kWh）            |
| 37  | ACChargingPower                           | AC 充电功率（kW）                 |
| 38  | ChargeLimitSoc                            | 设定充电上限 SOC（%）             |
| 39  | FastChargerPresent                        | 快充桩是否连接                    |
| 40  | EstBatteryRange                           | 估计剩余续航（km 或 mi）          |
| 41  | IdealBatteryRange                         | 理想续航（km 或 mi）              |
| 42  | BatteryLevel                              | 电池电量百分比                    |
| 43  | TimeToFullCharge                          | 充满电剩余时间（min）             |
| 44  | ScheduledChargingStartTime                | 计划充电开始时间                  |
| 45  | ScheduledChargingPending                  | 是否有待处理的计划充电            |
| 46  | ScheduledDepartureTime                    | 计划出发时间                      |
| 47  | PreconditioningEnabled                    | 预调温功能是否启用                |
| 48  | ScheduledChargingMode                     | 计划充电模式                      |
| 49  | ChargeAmps                                | 当前充电电流（A）                 |
| 50  | ChargeEnableRequest                       | 充电请求状态                      |
| 51  | ChargerPhases                             | 充电相数                          |
| 52  | ChargePortColdWeatherMode                 | 充电口防寒模式                    |
| 53  | ChargeCurrentRequest                      | 请求充电电流（A）                 |
| 54  | ChargeCurrentRequestMax                   | 最大请求充电电流（A）             |
| 55  | BatteryHeaterOn                           | 电池加热器状态                    |
| 56  | NotEnoughPowerToHeat                      | 电量不足无法加热                  |
| 57  | SuperchargerSessionTripPlanner            | 超级充电会话信息（路线规划）      |
| 58  | DoorState                                 | 车门状态（开/关）                 |
| 59  | Locked                                    | 车锁状态                          |
| 60  | FdWindow                                  | 前左窗状态                        |
| 61  | FpWindow                                  | 前右窗状态                        |
| 62  | RdWindow                                  | 后左窗状态                        |
| 63  | RpWindow                                  | 后右窗状态                        |
| 64  | VehicleName                               | 车辆名称                          |
| 65  | SentryMode                                | 哨兵模式状态                      |
| 66  | SpeedLimitMode                            | 限速模式状态                      |
| 67  | CurrentLimitMph                           | 当前限速值（mph）                 |
| 68  | Version                                   | 软件版本号                        |
| 69  | TpmsPressureFl                            | 前左轮胎压力                      |
| 70  | TpmsPressureFr                            | 前右轮胎压力                      |
| 71  | TpmsPressureRl                            | 后左轮胎压力                      |
| 72  | TpmsPressureRr                            | 后右轮胎压力                      |
| 73  | SemitruckTpmsPressureRe1L0                | Semi-truck 专2用轮胎压力          |
| 74  | SemitruckTpmsPressureRe1L1                | Semi-truck 专用轮胎压力           |
| 75  | SemitruckTpmsPressureRe1R0                | Semi-truck 专用轮胎压力           |
| 76  | SemitruckTpmsPressureRe1R1                | Semi-truck 专用轮胎压力           |
| 77  | SemitruckTpmsPressureRe2L0                | Semi-truck 专用轮胎压力           |
| 78  | SemitruckTpmsPressureRe2L1                | Semi-truck 专用轮胎压力           |
| 79  | SemitruckTpmsPressureRe2R0                | Semi-truck 专用轮胎压力           |
| 80  | SemitruckTpmsPressureRe2R1                | Semi-truck 专用轮胎压力           |
| 81  | TpmsLastSeenPressureTimeFl                | 前左轮胎最后读取时间              |
| 82  | TpmsLastSeenPressureTimeFr                | 前右轮胎最后读取时间              |
| 83  | TpmsLastSeenPressureTimeRl                | 后左轮胎最后读取时间              |
| 84  | TpmsLastSeenPressureTimeRr                | 后右轮胎最后读取时间              |
| 85  | InsideTemp                                | 车内温度（℃）                     |
| 86  | OutsideTemp                               | 车外温度（℃）                     |
| 87  | SeatHeaterLeft                            | 左前座加热状态                    |
| 88  | SeatHeaterRight                           | 右前座加热状态                    |
| 89  | SeatHeaterRearLeft                        | 左后座加热状态                    |
| 90  | SeatHeaterRearRight                       | 右后座加热状态                    |
| 91  | SeatHeaterRearCenter                      | 中后座加热状态                    |
| 92  | AutoSeatClimateLeft                       | 左前座自动温控状态                |
| 93  | AutoSeatClimateRight                      | 右前座自动温控状态                |
| 94  | DriverSeatBelt                            | 驾驶员安全带状态                  |
| 95  | PassengerSeatBelt                         | 副驾驶安全带状态                  |
| 96  | DriverSeatOccupied                        | 驾驶员是否在座                    |
| 97  | SemitruckPassengerSeatFoldPosition        | Semi-truck 专用乘客座椅折叠位置   |
| 98  | LateralAcceleration                       | 横向加速度（m/s²）                |
| 99  | LongitudinalAcceleration                  | 纵向加速度（m/s²）                |
| 100 | Deprecated_2                              | 已废弃字段                        |
| 101 | CruiseSetSpeed                            | 定速巡航速度                      |
| 102 | LifetimeEnergyUsed                        | 累计消耗电能（kWh）               |
| 103 | LifetimeEnergyUsedDrive                   | Semi-truck 专用累计驱动能量       |
| 104 | SemitruckTractorParkBrakeStatus           | Semi-truck 拖车驻车制动状态       |
| 105 | SemitruckTrailerParkBrakeStatus           | Semi-truck 拖挂车驻车制动状态     |
| 106 | BrakePedalPos                             | 刹车踏板位置（%）                 |
| 107 | RouteLastUpdated                          | 路线最后更新时间（固件 2024.26+） |
| 108 | RouteLine                                 | 当前路线（固件 2024.26+）         |
| 109 | MilesToArrival                            | 距到达里程（固件 2024.26+）       |
| 110 | MinutesToArrival                          | 距到达时间（固件 2024.26+）       |
| 111 | OriginLocation                            | 起点位置（固件 2024.26+）         |
| 112 | DestinationLocation                       | 终点位置（固件 2024.26+）         |
| 113 | CarType                                   | 车型                              |
| 114 | Trim                                      | 车型配置                          |
| 115 | ExteriorColor                             | 车身颜色                          |
| 116 | RoofColor                                 | 车顶颜色                          |
| 117 | ChargePort                                | 充电口状态                        |
| 118 | ChargePortLatch                           | 充电口锁状态                      |
| 119 | Experimental_1                            | 实验性字段                        |
| 120 | Experimental_2                            | 实验性字段                        |
| 121 | Experimental_3                            | 实验性字段                        |
| 122 | Experimental_4                            | 实验性字段                        |
| 123 | GuestModeEnabled                          | 客人模式是否启用                  |
| 124 | PinToDriveEnabled                         | 驾驶 PIN 是否启用                 |
| 125 | PairedPhoneKeyAndKeyFobQty                | 配对钥匙数量                      |
| 126 | CruiseFollowDistance                      | 巡航跟车距离                      |
| 127 | AutomaticBlindSpotCamera                  | 自动盲点摄像头状态                |
| 128 | BlindSpotCollisionWarningChime            | 盲点碰撞提示声                    |
| 129 | SpeedLimitWarning                         | 超速提醒                          |
| 130 | ForwardCollisionWarning                   | 前向碰撞警告                      |
| 131 | LaneDepartureAvoidance                    | 车道偏离辅助                      |
| 132 | EmergencyLaneDepartureAvoidance           | 紧急车道偏离辅助                  |
| 133 | AutomaticEmergencyBrakingOff              | 自动紧急制动关闭状态              |
| 134 | LifetimeEnergyGainedRegen                 | 累计回收能量（kWh）               |
| 135 | DiStateF                                  | 前电机状态                        |
| 136 | DiStateREL                                | 左后电机状态                      |
| 137 | DiStateRER                                | 右后电机状态                      |
| 138 | DiHeatsinkTF                              | 前电机散热片温度                  |
| 139 | DiHeatsinkTREL                            | 左后电机散热片温度                |
| 140 | DiHeatsinkTRER                            | 右后电机散热片温度                |
| 141 | DiAxleSpeedF                              | 前轴速度                          |
| 142 | DiAxleSpeedREL                            | 左后轴速度                        |
| 143 | DiAxleSpeedRER                            | 右后轴速度                        |
| 144 | DiSlaveTorqueCmd                          | 电机扭矩指令                      |
| 145 | DiTorqueActualR                           | 后电机实际扭矩                    |
| 146 | DiTorqueActualF                           | 前电机实际扭矩                    |
| 147 | DiTorqueActualREL                         | 左后电机实际扭矩                  |
| 148 | DiTorqueActualRER                         | 右后电机实际扭矩                  |
| 149 | DiStatorTempF                             | 前电机定子温度                    |
| 150 | DiStatorTempREL                           | 左后电机定子温度                  |
| 151 | DiStatorTempRER                           | 右后电机定子温度                  |
| 152 | DiVBatF                                   | 前电机电池电压                    |
| 153 | DiVBatREL                                 | 左后电机电池电压                  |
| 154 | DiVBatRER                                 | 右后电机电池电压                  |
| 155 | DiMotorCurrentF                           | 前电机电流                        |
| 156 | DiMotorCurrentREL                         | 左后电机电流                      |
| 157 | DiMotorCurrentRER                         | 右后电机电流                      |
| 158 | EnergyRemaining                           | 剩余电量（kWh）                   |
| 159 | ServiceMode                               | 维修模式状态                      |
| 160 | BMSState                                  | 电池管理系统状态                  |
| 161 | GuestModeMobileAccessState                | 客人模式移动端访问状态            |
| 162 | Deprecated_1                              | 已废弃字段                        |
| 163 | DestinationName                           | 目的地名称（固件 2024.26+）       |
| 164 | DiInverterTR                              | 后电机逆变器状态                  |
| 165 | DiInverterTF                              | 前电机逆变器状态                  |
| 166 | DiInverterTREL                            | 左后电机逆变器状态                |
| 167 | DiInverterTRER                            | 右后电机逆变器状态                |
| 168 | Experimental_5                            | 实验性字段                        |
| 169 | Experimental_6                            | 实验性字段                        |
| 170 | Experimental_7                            | 实验性字段                        |
| 171 | Experimental_8                            | 实验性字段                        |
| 172 | Experimental_9                            | 实验性字段                        |
| 173 | Experimental_10                           | 实验性字段                        |
| 174 | Experimental_11                           | 实验性字段                        |
| 175 | Experimental_12                           | 实验性字段                        |
| 176 | Experimental_13                           | 实验性字段                        |
| 177 | Experimental_14                           | 实验性字段                        |
| 178 | Experimental_15                           | 实验性字段                        |
| 179 | DetailedChargeState                       | 详细充电状态                      |
| 180 | CabinOverheatProtectionMode               | 驾驶舱过热保护模式                |
| 181 | CabinOverheatProtectionTemperatureLimit   | 驾驶舱过热保护温度限制            |
| 182 | CenterDisplay                             | 中控显示状态                      |
| 183 | ChargePortDoorOpen                        | 充电口门状态                      |
| 184 | ChargerVoltage                            | 充电器电压                        |
| 185 | ChargingCableType                         | 充电线类型                        |
| 186 | ClimateKeeperMode                         | 空调保持模式                      |
| 187 | DefrostForPreconditioning                 | 预调温化霜状态                    |
| 188 | DefrostMode                               | 化霜模式                          |
| 189 | EfficiencyPackage                         | 高效套件状态                      |
| 190 | EstimatedHoursToChargeTermination         | 预计充电结束时间（小时）          |
| 191 | EuropeVehicle                             | 欧洲车辆标识                      |
| 192 | ExpectedEnergyPercentAtTripArrival        | 预计到达剩余电量百分比            |
| 193 | FastChargerType                           | 快充桩类型                        |
| 194 | HomelinkDeviceCount                       | Homelink 设备数量                 |
| 195 | HomelinkNearby                            | Homelink 设备附近状态             |
| 196 | HvacACEnabled                             | 空调开启状态                      |
| 197 | HvacAutoMode                              | 空调自动模式                      |
| 198 | HvacFanSpeed                              | 风扇速度                          |
| 199 | HvacFanStatus                             | 风扇状态                          |
| 200 | HvacLeftTemperatureRequest                | 左侧温度设定                      |
| 201 | HvacPower                                 | 空调电源状态                      |
| 202 | HvacRightTemperatureRequest               | 右侧温度设定                      |
| 203 | HvacSteeringWheelHeatAuto                 | 方向盘加热自动模式                |
| 204 | HvacSteeringWheelHeatLevel                | 方向盘加热等级                    |
| 205 | OffroadLightbarPresent                    | 越野灯条存在状态                  |
| 206 | PowershareHoursLeft                       | 能量共享剩余小时数                |
| 207 | PowershareInstantaneousPowerKW            | 能量共享瞬时功率（kW）            |
| 208 | PowershareStatus                          | 能量共享状态                      |
| 209 | PowershareStopReason                      | 能量共享停止原因                  |
| 210 | PowershareType                            | 能量共享类型                      |
| 211 | RearDisplayHvacEnabled                    | 后排显示空调状态                  |
| 212 | RearSeatHeaters                           | 后排座椅加热状态                  |
| 213 | RemoteStartEnabled                        | 远程启动是否启用                  |
| 214 | RightHandDrive                            | 是否右舵车辆                      |
| 215 | RouteTrafficMinutesDelay                  | 路线交通延迟时间（分钟）          |
| 216 | SoftwareUpdateDownloadPercentComplete     | 软件更新下载完成百分比            |
| 217 | SoftwareUpdateExpectedDurationMinutes     | 软件更新预计持续时间（分钟）      |
| 218 | SoftwareUpdateInstallationPercentComplete | 软件更新安装完成百分比            |
| 219 | SoftwareUpdateScheduledStartTime          | 软件更新计划开始时间              |
| 220 | SoftwareUpdateVersion                     | 软件更新版本                      |
| 221 | TonneauOpenPercent                        | 货厢盖打开百分比                  |
| 222 | TonneauPosition                           | 货厢盖位置                        |
| 223 | TonneauTentMode                           | 货厢盖帐篷模式                    |
| 224 | TpmsHardWarnings                          | 胎压监测硬警告                    |
| 225 | TpmsSoftWarnings                          | 胎压监测软警告                    |
| 226 | ValetModeEnabled                          | 代客模式启用状态                  |
| 227 | WheelType                                 | 轮毂类型                          |
| 228 | WiperHeatEnabled                          | 雨刷加热状态                      |
| 229 | LocatedAtHome                             | 车辆位于“家”                      |
| 230 | LocatedAtWork                             | 车辆位于“工作”                    |
| 231 | LocatedAtFavorite                         | 车辆位于“收藏地点”                |
| 232 | SettingDistanceUnit                       | 距离单位设置（km/mi）             |
| 233 | SettingTemperatureUnit                    | 温度单位设置（℃/℉）               |
| 234 | Setting24HourTime                         | 24小时制设置                      |
| 235 | SettingTirePressureUnit                   | 胎压单位设置（psi/bar）           |
| 236 | SettingChargeUnit                         | 充电单位设置（kWh/mi）            |
| 237 | ClimateSeatCoolingFrontLeft               | 左前座座椅通风状态                |
| 238 | ClimateSeatCoolingFrontRight              | 右前座座椅通风状态                |
| 239 | LightsHazardsActive                       | 危险灯状态                        |
| 240 | LightsTurnSignal                          | 转向灯状态                        |
| 241 | LightsHighBeams                           | 远光灯状态                        |
| 242 | MediaPlaybackStatus                       | 媒体播放状态                      |
| 243 | MediaPlaybackSource                       | 媒体播放来源                      |
| 244 | MediaAudioVolume                          | 媒体音量                          |
| 245 | MediaNowPlayingDuration                   | 当前播放总时长（秒）              |
| 246 | MediaNowPlayingElapsed                    | 当前播放已过时间（秒）            |
| 247 | MediaNowPlayingArtist                     | 当前播放艺术家                    |
| 248 | MediaNowPlayingTitle                      | 当前播放曲目                      |
| 249 | MediaNowPlayingAlbum                      | 当前播放专辑                      |
| 250 | MediaNowPlayingStation                    | 当前播放电台                      |
| 251 | MediaAudioVolumeIncrement                 | 音量增量                          |
| 252 | MediaAudioVolumeMax                       | 音量最大值                        |
| 253 | SunroofInstalled                          | 天窗安装状态                      |
| 254 | SeatVentEnabled                           | 座椅通风状态                      |
| 255 | RearDefrostEnabled                        | 后窗除霜状态                      |
| 256 | ChargeRateMilePerHour                     | 充电速度（mi/h）                  |
| 257 | Deprecated_3                              | 已废弃字段                        |

- 下发的配置 JSON

下发的配置中删除了部分过时和 Cybertruck 特有的字段，可按需调整

```json
{
  "config": {
    "delivery_policy": "latest",
    "prefer_typed": true,
    "port": 12345,
    "alert_types": ["service", "customer", "service-fix"],
    "fields": {
      "DriveRail": {
        "interval_seconds": 600
      },
      "ChargeState": {
        "interval_seconds": 600
      },
      "BmsFullchargecomplete": {
        "interval_seconds": 600
      },
      "VehicleSpeed": {
        "interval_seconds": 5,
        "minimum_delta": 0.01
      },
      "Odometer": {
        "interval_seconds": 600,
        "minimum_delta": 0.1
      },
      "PackVoltage": {
        "interval_seconds": 300,
        "minimum_delta": 0.5
      },
      "PackCurrent": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "Soc": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "DCDCEnable": {
        "interval_seconds": 600
      },
      "Gear": {
        "interval_seconds": 5
      },
      "IsolationResistance": {
        "interval_seconds": 600,
        "minimum_delta": 1,
        "resend_interval_seconds": 3600
      },
      "PedalPosition": {
        "interval_seconds": 5,
        "minimum_delta": 0.1
      },
      "BrakePedal": {
        "interval_seconds": 5
      },
      "DiStateR": {
        "interval_seconds": 60
      },
      "DiAxleSpeedR": {
        "interval_seconds": 10,
        "minimum_delta": 0.01
      },
      "DiTorquemotor": {
        "interval_seconds": 5,
        "minimum_delta": 1
      },
      "DiStatorTempR": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiVBatR": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiMotorCurrentR": {
        "interval_seconds": 300,
        "minimum_delta": 1
      },
      "Location": {
        "interval_seconds": 10,
        "minimum_delta": 0.00002,
        "resend_interval_seconds": 300
      },
      "GpsState": {
        "interval_seconds": 3600
      },
      "GpsHeading": {
        "interval_seconds": 10,
        "minimum_delta": 0.0001
      },
      "NumBrickVoltageMax": {
        "interval_seconds": 3600
      },
      "BrickVoltageMax": {
        "interval_seconds": 3600,
        "minimum_delta": 0.01
      },
      "NumBrickVoltageMin": {
        "interval_seconds": 300,
        "minimum_delta": 1
      },
      "BrickVoltageMin": {
        "interval_seconds": 3600,
        "minimum_delta": 0.01
      },
      "NumModuleTempMax": {
        "interval_seconds": 3600,
        "minimum_delta": 1
      },
      "ModuleTempMax": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "NumModuleTempMin": {
        "interval_seconds": 300,
        "minimum_delta": 1
      },
      "ModuleTempMin": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "RatedRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "DCChargingEnergyIn": {
        "interval_seconds": 60
      },
      "DCChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 0.1
      },
      "ACChargingEnergyIn": {
        "interval_seconds": 5,
        "minimum_delta": 0.1
      },
      "ACChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 1
      },
      "ChargeLimitSoc": {
        "interval_seconds": 3600,
        "minimum_delta": 1
      },
      "FastChargerPresent": {
        "interval_seconds": 60
      },
      "EstBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "IdealBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "BatteryLevel": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "TimeToFullCharge": {
        "interval_seconds": 60,
        "minimum_delta": 0.01
      },
      "ChargeAmps": {
        "interval_seconds": 10,
        "minimum_delta": 1
      },
      "ChargeEnableRequest": {
        "interval_seconds": 300
      },
      "ChargerPhases": {
        "interval_seconds": 300
      },
      "ChargeCurrentRequest": {
        "interval_seconds": 300
      },
      "ChargeCurrentRequestMax": {
        "interval_seconds": 300
      },
      "BatteryHeaterOn": {
        "interval_seconds": 60
      },
      "NotEnoughPowerToHeat": {
        "interval_seconds": 3600
      },
      "SuperchargerSessionTripPlanner": {
        "interval_seconds": 3600
      },
      "DoorState": {
        "interval_seconds": 10
      },
      "Locked": {
        "interval_seconds": 10
      },
      "FdWindow": {
        "interval_seconds": 60
      },
      "FpWindow": {
        "interval_seconds": 60
      },
      "RdWindow": {
        "interval_seconds": 60
      },
      "RpWindow": {
        "interval_seconds": 60
      },
      "VehicleName": {
        "interval_seconds": 3600
      },
      "SentryMode": {
        "interval_seconds": 300
      },
      "SpeedLimitMode": {
        "interval_seconds": 3600
      },
      "CurrentLimitMph": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "Version": {
        "interval_seconds": 3600
      },
      "TpmsPressureFl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01
      },
      "TpmsPressureFr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01
      },
      "TpmsPressureRl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01
      },
      "TpmsPressureRr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01
      },
      "TpmsLastSeenPressureTimeFl": {
        "interval_seconds": 300
      },
      "TpmsLastSeenPressureTimeFr": {
        "interval_seconds": 300
      },
      "TpmsLastSeenPressureTimeRl": {
        "interval_seconds": 300
      },
      "TpmsLastSeenPressureTimeRr": {
        "interval_seconds": 300
      },
      "InsideTemp": {
        "interval_seconds": 300,
        "minimum_delta": 0.5
      },
      "OutsideTemp": {
        "interval_seconds": 300,
        "minimum_delta": 0.5
      },
      "SeatHeaterLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "SeatHeaterRight": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "SeatHeaterRearLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "SeatHeaterRearRight": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "SeatHeaterRearCenter": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "AutoSeatClimateLeft": {
        "interval_seconds": 60
      },
      "AutoSeatClimateRight": {
        "interval_seconds": 60
      },
      "DriverSeatBelt": {
        "interval_seconds": 60
      },
      "PassengerSeatBelt": {
        "interval_seconds": 60
      },
      "DriverSeatOccupied": {
        "interval_seconds": 60
      },
      "LateralAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01
      },
      "LongitudinalAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01
      },
      "Deprecated_2": {
        "interval_seconds": 60
      },
      "CruiseSetSpeed": {
        "interval_seconds": 30,
        "minimum_delta": 1
      },
      "LifetimeEnergyUsed": {
        "interval_seconds": 300,
        "minimum_delta": 0.1
      },
      "BrakePedalPos": {
        "interval_seconds": 5,
        "minimum_delta": 0.001
      },
      "RouteLastUpdated": {
        "interval_seconds": 300
      },
      "RouteLine": {
        "interval_seconds": 300
      },
      "MilesToArrival": {
        "interval_seconds": 300
      },
      "MinutesToArrival": {
        "interval_seconds": 300
      },
      "OriginLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001
      },
      "DestinationLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001
      },
      "CarType": {
        "interval_seconds": 3600
      },
      "Trim": {
        "interval_seconds": 3600
      },
      "ExteriorColor": {
        "interval_seconds": 3600
      },
      "RoofColor": {
        "interval_seconds": 3600
      },
      "ChargePort": {
        "interval_seconds": 3600
      },
      "ChargePortLatch": {
        "interval_seconds": 60
      },
      "GuestModeEnabled": {
        "interval_seconds": 300
      },
      "PinToDriveEnabled": {
        "interval_seconds": 300
      },
      "PairedPhoneKeyAndKeyFobQty": {
        "interval_seconds": 3600
      },
      "CruiseFollowDistance": {
        "interval_seconds": 3600
      },
      "AutomaticBlindSpotCamera": {
        "interval_seconds": 3600
      },
      "BlindSpotCollisionWarningChime": {
        "interval_seconds": 3600
      },
      "SpeedLimitWarning": {
        "interval_seconds": 3600
      },
      "ForwardCollisionWarning": {
        "interval_seconds": 3600
      },
      "LaneDepartureAvoidance": {
        "interval_seconds": 3600
      },
      "EmergencyLaneDepartureAvoidance": {
        "interval_seconds": 3600
      },
      "AutomaticEmergencyBrakingOff": {
        "interval_seconds": 3600
      },
      "LifetimeEnergyGainedRegen": {
        "interval_seconds": 3600
      },
      "DiStateF": {
        "interval_seconds": 300
      },
      "DiStateREL": {
        "interval_seconds": 300
      },
      "DiStateRER": {
        "interval_seconds": 300
      },
      "DiHeatsinkTF": {
        "interval_seconds": 300
      },
      "DiHeatsinkTREL": {
        "interval_seconds": 300
      },
      "DiHeatsinkTRER": {
        "interval_seconds": 300
      },
      "DiAxleSpeedF": {
        "interval_seconds": 300
      },
      "DiAxleSpeedREL": {
        "interval_seconds": 300
      },
      "DiAxleSpeedRER": {
        "interval_seconds": 300
      },
      "DiSlaveTorqueCmd": {
        "interval_seconds": 300
      },
      "DiTorqueActualR": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiTorqueActualF": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiTorqueActualREL": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiTorqueActualRER": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiStatorTempF": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiStatorTempREL": {
        "interval_seconds": 60
      },
      "DiStatorTempRER": {
        "interval_seconds": 60
      },
      "DiVBatF": {
        "interval_seconds": 60
      },
      "DiVBatREL": {
        "interval_seconds": 60
      },
      "DiVBatRER": {
        "interval_seconds": 60
      },
      "DiMotorCurrentF": {
        "interval_seconds": 60
      },
      "DiMotorCurrentREL": {
        "interval_seconds": 60
      },
      "DiMotorCurrentRER": {
        "interval_seconds": 60
      },
      "EnergyRemaining": {
        "interval_seconds": 60,
        "minimum_delta": 0.1
      },
      "ServiceMode": {
        "interval_seconds": 3600
      },
      "BMSState": {
        "interval_seconds": 60
      },
      "GuestModeMobileAccessState": {
        "interval_seconds": 60
      },
      "DestinationName": {
        "interval_seconds": 60
      },
      "DiInverterTR": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiInverterTF": {
        "interval_seconds": 60,
        "minimum_delta": 1
      },
      "DiInverterTREL": {
        "interval_seconds": 60
      },
      "DiInverterTRER": {
        "interval_seconds": 60
      },
      "DetailedChargeState": {
        "interval_seconds": 60
      },
      "CabinOverheatProtectionMode": {
        "interval_seconds": 300
      },
      "CabinOverheatProtectionTemperatureLimit": {
        "interval_seconds": 300
      },
      "CenterDisplay": {
        "interval_seconds": 60
      },
      "ChargePortDoorOpen": {
        "interval_seconds": 60
      },
      "ChargerVoltage": {
        "interval_seconds": 300,
        "minimum_delta": 0.2
      },
      "ChargingCableType": {
        "interval_seconds": 3600
      },
      "ClimateKeeperMode": {
        "interval_seconds": 300
      },
      "DefrostForPreconditioning": {
        "interval_seconds": 300
      },
      "DefrostMode": {
        "interval_seconds": 300
      },
      "EfficiencyPackage": {
        "interval_seconds": 300
      },
      "EstimatedHoursToChargeTermination": {
        "interval_seconds": 60,
        "minimum_delta": 0.01
      },
      "EuropeVehicle": {
        "interval_seconds": 3600
      },
      "ExpectedEnergyPercentAtTripArrival": {
        "interval_seconds": 300,
        "minimum_delta": 1
      },
      "FastChargerType": {
        "interval_seconds": 300
      },
      "HomelinkDeviceCount": {
        "interval_seconds": 3600
      },
      "HomelinkNearby": {
        "interval_seconds": 3600
      },
      "HvacACEnabled": {
        "interval_seconds": 60
      },
      "HvacAutoMode": {
        "interval_seconds": 60
      },
      "HvacFanSpeed": {
        "interval_seconds": 60
      },
      "HvacFanStatus": {
        "interval_seconds": 60
      },
      "HvacLeftTemperatureRequest": {
        "interval_seconds": 60
      },
      "HvacPower": {
        "interval_seconds": 60
      },
      "HvacRightTemperatureRequest": {
        "interval_seconds": 60
      },
      "HvacSteeringWheelHeatAuto": {
        "interval_seconds": 60
      },
      "HvacSteeringWheelHeatLevel": {
        "interval_seconds": 60
      },
      "OffroadLightbarPresent": {
        "interval_seconds": 3600
      },
      "PowershareHoursLeft": {
        "interval_seconds": 300
      },
      "PowershareInstantaneousPowerKW": {
        "interval_seconds": 300
      },
      "PowershareStatus": {
        "interval_seconds": 300
      },
      "PowershareStopReason": {
        "interval_seconds": 300
      },
      "PowershareType": {
        "interval_seconds": 300
      },
      "RearDisplayHvacEnabled": {
        "interval_seconds": 300
      },
      "RearSeatHeaters": {
        "interval_seconds": 300
      },
      "RemoteStartEnabled": {
        "interval_seconds": 300
      },
      "RightHandDrive": {
        "interval_seconds": 3600
      },
      "RouteTrafficMinutesDelay": {
        "interval_seconds": 300
      },
      "SoftwareUpdateDownloadPercentComplete": {
        "interval_seconds": 300
      },
      "SoftwareUpdateExpectedDurationMinutes": {
        "interval_seconds": 300
      },
      "SoftwareUpdateInstallationPercentComplete": {
        "interval_seconds": 300
      },
      "SoftwareUpdateScheduledStartTime": {
        "interval_seconds": 300
      },
      "SoftwareUpdateVersion": {
        "interval_seconds": 300
      },
      "TonneauOpenPercent": {
        "interval_seconds": 300
      },
      "TonneauPosition": {
        "interval_seconds": 300
      },
      "TonneauTentMode": {
        "interval_seconds": 300
      },
      "TpmsHardWarnings": {
        "interval_seconds": 300
      },
      "TpmsSoftWarnings": {
        "interval_seconds": 300
      },
      "ValetModeEnabled": {
        "interval_seconds": 300
      },
      "WheelType": {
        "interval_seconds": 3600
      },
      "WiperHeatEnabled": {
        "interval_seconds": 300
      },
      "LocatedAtHome": {
        "interval_seconds": 300
      },
      "LocatedAtWork": {
        "interval_seconds": 300
      },
      "LocatedAtFavorite": {
        "interval_seconds": 300
      },
      "SettingDistanceUnit": {
        "interval_seconds": 3600
      },
      "SettingTemperatureUnit": {
        "interval_seconds": 3600
      },
      "Setting24HourTime": {
        "interval_seconds": 3600
      },
      "SettingTirePressureUnit": {
        "interval_seconds": 3600
      },
      "SettingChargeUnit": {
        "interval_seconds": 3600
      },
      "ClimateSeatCoolingFrontLeft": {
        "interval_seconds": 120
      },
      "ClimateSeatCoolingFrontRight": {
        "interval_seconds": 120
      },
      "LightsHazardsActive": {
        "interval_seconds": 120
      },
      "LightsTurnSignal": {
        "interval_seconds": 60
      },
      "LightsHighBeams": {
        "interval_seconds": 60
      },
      "MediaPlaybackStatus": {
        "interval_seconds": 120
      },
      "MediaPlaybackSource": {
        "interval_seconds": 120
      },
      "MediaAudioVolume": {
        "interval_seconds": 300
      },
      "MediaNowPlayingDuration": {
        "interval_seconds": 300
      },
      "MediaNowPlayingElapsed": {
        "interval_seconds": 300
      },
      "MediaNowPlayingArtist": {
        "interval_seconds": 300
      },
      "MediaNowPlayingTitle": {
        "interval_seconds": 300
      },
      "MediaNowPlayingAlbum": {
        "interval_seconds": 300
      },
      "MediaNowPlayingStation": {
        "interval_seconds": 300
      },
      "MediaAudioVolumeIncrement": {
        "interval_seconds": 300
      },
      "MediaAudioVolumeMax": {
        "interval_seconds": 300
      },
      "SunroofInstalled": {
        "interval_seconds": 300
      },
      "SeatVentEnabled": {
        "interval_seconds": 300
      },
      "RearDefrostEnabled": {
        "interval_seconds": 300
      },
      "ChargeRateMilePerHour": {
        "interval_seconds": 10,
        "minimum_delta": 0.1
      },
      "Deprecated_3": {
        "interval_seconds": 300
      }
    },
    "ca": "{{ca}}",
    "hostname": "{{hostname}}"
  },
  "vins": ["{{vin}}"]
}
```
