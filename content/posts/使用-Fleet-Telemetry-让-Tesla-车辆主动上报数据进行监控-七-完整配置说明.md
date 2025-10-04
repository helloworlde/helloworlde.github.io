---
date: 2025-09-30
# description: ""
# image: ""
lastmod: 2025-10-04
showTableOfContents: false
tags:
  - Tesla
featured: true
title: "使用 Fleet Telemetry 让 Tesla 车辆主动上报数据进行监控-(七)完整配置说明"
type: "post"
---

以下是 Tesla 车辆支持的属性和解释，由 AI 整理，并不完全准确，可以根据需要选择需要上报的数据；详细的数据和警报可以参考 [可用数据](https://developer.tesla.cn/docs/fleet-api/fleet-telemetry/available-data) 和 [车辆警报](https://developer.tesla.cn/docs/fleet-api/fleet-telemetry/available-data#%E8%BD%A6%E8%BE%86%E8%AD%A6%E6%8A%A5)

- Filed 配置属性

| 属性                                      | 类型     | 描述                                                                                                                                                                                                          |
| :---------------------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ACChargingEnergyIn                        | 充电     | 在交流 (AC) 充电会话期间增加的电能，单位为 kWh。这是从充电器端测量的。在直流 (DC) 充电期间应忽略此字段                                                                                                        |
| ACChargingPower                           | 充电     | 总交流充电器输入功率                                                                                                                                                                                          |
| BMSState                                  | 充电     | **电池管理系统 (BMS)** 的运行状态                                                                                                                                                                             |
| BatteryHeaterOn                           | 充电     | 电池是否正在主动加热。这可能发生在寒冷天气或为超级充电进行预处理时                                                                                                                                            |
| BatteryLevel                              | 充电     | 车辆的**充电状态 (State of Charge, SoC)**，占总电池容量的百分比                                                                                                                                               |
| BmsFullchargecomplete                     | 充电     | 指示 BMS 已完成充满电                                                                                                                                                                                         |
| BrickVoltageMax                           | 充电     | **电池砖 (Brick)** 的最大电压                                                                                                                                                                                 |
| BrickVoltageMin                           | 充电     | **电池砖 (Brick)** 的最小电压                                                                                                                                                                                 |
| ChargeAmps                                | 充电     | 交流充电器感测到的输入线电流                                                                                                                                                                                  |
| ChargeCurrentRequest                      | 充电     | 请求给车辆充电的安培数                                                                                                                                                                                        |
| ChargeCurrentRequestMax                   | 充电     | 可用于充电的最大可用安培数                                                                                                                                                                                    |
| ChargeEnableRequest                       | 充电     | 充电是否被启用                                                                                                                                                                                                |
| ChargeLimitSoc                            | 充电     | 充电将终止时的**充电状态 (SoC)**，占电池容量的百分比                                                                                                                                                          |
| ChargePort                                | 充电     | 安装的充电端口的类型                                                                                                                                                                                          |
| ChargePortColdWeatherMode                 | 充电     | 指示充电端口是否处于寒冷天气模式                                                                                                                                                                              |
| ChargePortDoorOpen                        | 充电     | 仅根据车门电位计指示充电端口门是否打开                                                                                                                                                                        |
| ChargePortLatch                           | 充电     | 感测到的充电端口锁门状态。早期的 Model 3 车辆在寒冷天气（低于 5 摄氏度）下不会锁门                                                                                                                            |
| ChargeRateMilePerHour                     | 充电     | 以当前充电速率每小时增加的**续航里程数（英里）**                                                                                                                                                              |
| ChargeState                               | 充电     | 车辆的非详细充电状态。详细充电状态数据请参阅 `DetailedChargeState`                                                                                                                                            |
| ChargerPhases                             | 充电     | 连接的充电器可用的**相数**                                                                                                                                                                                    |
| ChargerVoltage                            | 充电     | 交流充电器感测到的输入电压的 **RMS（均方根）** 值。即使未充电，此字段也会频繁变化。建议设置 `minimum_delta`（适用于固件版本 2024.44.32 及更高版本）。从固件版本 2025.2.6 开始，`minimum_delta` 默认设置为 0.3 |
| ChargingCableType                         | 充电     | 连接到车辆的充电电缆类型。如果未连接充电电缆，将返回 `Invalid`                                                                                                                                                |
| DCChargingEnergyIn                        | 充电     | 在充电会话期间增加的电能，单位为 kWh。这是在电池端测量的。交流和直流充电都可以依赖此数据                                                                                                                      |
| DCChargingPower                           | 充电     | 在直流 (DC) 充电会话期间增加的千瓦数                                                                                                                                                                          |
| DCDCEnable                                | 充电     | **功率转换系统 (PCS)** 的 DCDC 启用线的状态                                                                                                                                                                   |
| DetailedChargeState                       | 充电     | 详细的充电状态，而不是提供很少细节的 `ChargeState`。此字段在固件版本 2024.38 中添加                                                                                                                           |
| EnergyRemaining                           | 充电     | 电池组中**剩余的标称电能**，单位为 kWh                                                                                                                                                                        |
| EstBatteryRange                           | 充电     | 考虑到当前充电状态和驾驶条件，车辆的**估计续航里程**                                                                                                                                                          |
| EstimatedHoursToChargeTermination         | 充电     | 达到所需充电状态所需的**小时数**。所需充电状态由 `ChargeLimitSoc` 定义                                                                                                                                        |
| ExpectedEnergyPercentAtTripArrival        | 充电     | 预计到达目的地时的**电能百分比**。如果未设置导航目的地，将返回 `Invalid`                                                                                                                                      |
| FastChargerPresent                        | 充电     | 是否存在**快速充电器**                                                                                                                                                                                        |
| FastChargerType                           | 充电     | 连接到车辆的**快速充电器类型**                                                                                                                                                                                |
| IdealBatteryRange                         | 充电     | 假设**理想条件**（速度、天气等）下车辆的当前续航里程                                                                                                                                                          |
| LifetimeEnergyUsed                        | 充电     | **放电期间**丢失的总电能计数，单位为 kWh                                                                                                                                                                      |
| LifetimeEnergyUsedDrive                   | 充电     | 此字段已损坏，不返回数据                                                                                                                                                                                      |
| ModuleTempMax                             | 充电     | **热敏电阻**测得的最高温度                                                                                                                                                                                    |
| ModuleTempMin                             | 充电     | **热敏电阻**测得的最低温度                                                                                                                                                                                    |
| NotEnoughPowerToHeat                      | 充电     | 如果电池没有足够的可用功率来加热自身                                                                                                                                                                          |
| NumBrickVoltageMax                        | 充电     | 具有最大电压的电池砖编号（从 1 开始索引）                                                                                                                                                                     |
| NumBrickVoltageMin                        | 充电     | 具有最小电压的电池砖编号（从 1 开始索引）                                                                                                                                                                     |
| NumModuleTempMax                          | 充电     | 具有最高热敏电阻温度的模块 ID                                                                                                                                                                                 |
| NumModuleTempMin                          | 充电     | 具有最低热敏电阻温度的模块 ID                                                                                                                                                                                 |
| PackCurrent                               | 充电     | 在高压电池的 **高压接触器** 处测量的电流                                                                                                                                                                      |
| PackVoltage                               | 充电     | 在高压接触器的**电池侧**测量的电压                                                                                                                                                                            |
| PowershareHoursLeft                       | 充电     | 通过 **Powershare** 剩余的小时数                                                                                                                                                                              |
| PowershareInstantaneousPowerKW            | 充电     | 显示在 **V2X (Vehicle-to-Everything)** 模式下，来自功率转换系统 2 (PCS2) 的当前交流有功功率输出。正值表示电池放电（功率流出电池）                                                                             |
| PowershareStatus                          | 充电     | **Powershare** 的状态                                                                                                                                                                                         |
| PowershareStopReason                      | 充电     | **Powershare** 停止的原因                                                                                                                                                                                     |
| PowershareType                            | 充电     | 当前激活的 **Powershare** 类型                                                                                                                                                                                |
| PreconditioningEnabled                    | 充电     | 车辆是否正在**预处理**                                                                                                                                                                                        |
| RatedRange                                | 充电     | 考虑到当前充电状态，车辆的**官方额定续航里程**                                                                                                                                                                |
| ScheduledChargingMode                     | 充电     | **预定充电**的模式                                                                                                                                                                                            |
| ScheduledChargingPending                  | 充电     | 是否已预定充电会话                                                                                                                                                                                            |
| ScheduledChargingStartTime                | 充电     | 预定开始充电的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                                  |
| Soc                                       | 充电     | 车辆的**可用充电状态 (SoC)**，占总电池容量的百分比                                                                                                                                                            |
| SuperchargerSessionTripPlanner            | 充电     | 当前超级充电会话是否是**行程规划**的一部分                                                                                                                                                                    |
| TimeToFullCharge                          | 充电     | 距离充电完成的**小时数**。如果充电会话是行程的一部分，则是直到准备好继续的时间。否则，是直到用户设定的限制（由 `ChargeLimitSoc` 指定）的时间                                                                  |
| AutoSeatClimateLeft                       | 气候     | 左前座椅是否启用了**自动座椅温控**                                                                                                                                                                            |
| AutoSeatClimateRight                      | 气候     | 右前座椅是否启用了**自动座椅温控**                                                                                                                                                                            |
| CabinOverheatProtectionMode               | 气候     | **座舱过热保护**的模式                                                                                                                                                                                        |
| CabinOverheatProtectionTemperatureLimit   | 气候     | **座舱过热保护**的温度限制，表示为低、中或高                                                                                                                                                                  |
| ClimateKeeperMode                         | 气候     | **温控保持模式**                                                                                                                                                                                              |
| ClimateSeatCoolingFrontLeft               | 气候     | 左前座椅请求的**座椅通风**等级                                                                                                                                                                                |
| ClimateSeatCoolingFrontRight              | 气候     | 右前座椅请求的**座椅通风**等级                                                                                                                                                                                |
| DefrostForPreconditioning                 | 气候     | 车辆是否因为**预处理**而正在除霜                                                                                                                                                                              |
| DefrostMode                               | 气候     | 车辆**除霜**的状态                                                                                                                                                                                            |
| HvacACEnabled                             | 气候     | **交流 (AC) 制冷**是否启用                                                                                                                                                                                    |
| HvacAutoMode                              | 气候     | **HVAC 自动模式**的状态                                                                                                                                                                                       |
| HvacFanSpeed                              | 气候     | **HVAC 风扇速度**                                                                                                                                                                                             |
| HvacFanStatus                             | 气候     | 座舱气流鼓风机设定速度段                                                                                                                                                                                      |
| HvacLeftTemperatureRequest                | 气候     | 车辆左前侧请求的温度。以**摄氏度**报告。这与等效的 `vehicle_data` 字段略有不同，因为它基于车辆的侧面而不是乘客/驾驶员                                                                                         |
| HvacPower                                 | 气候     | **HVAC 系统**的电源状态                                                                                                                                                                                       |
| HvacRightTemperatureRequest               | 气候     | 车辆右前侧请求的温度。以**摄氏度**报告。这与等效的 `vehicle_data` 字段略有不同，因为它基于车辆的侧面而不是乘客/驾驶员                                                                                         |
| HvacSteeringWheelHeatAuto                 | 气候     | **方向盘加热**是否设置为自动                                                                                                                                                                                  |
| HvacSteeringWheelHeatLevel                | 气候     | **方向盘加热**的等级                                                                                                                                                                                          |
| InsideTemp                                | 气候     | 座舱的**估计温度**（摄氏度）。此字段经常以小增量变化，建议设置最小增量 (minimum delta)                                                                                                                        |
| OutsideTemp                               | 气候     | 基于车速的**过滤环境温度**                                                                                                                                                                                    |
| RearDefrostEnabled                        | 气候     | **后窗除霜**是否启用                                                                                                                                                                                          |
| RearDisplayHvacEnabled                    | 气候     | **后排显示屏**上的 HVAC 是否启用                                                                                                                                                                              |
| SeatHeaterLeft                            | 气候     | 左前**座椅加热器**的等级。值范围从 0（关闭）到 3（高）                                                                                                                                                        |
| SeatHeaterRearCenter                      | 气候     | 后排中央**座椅加热器**的等级。值范围从 0（关闭）到 3（高）                                                                                                                                                    |
| SeatHeaterRearLeft                        | 气候     | 后排左侧**座椅加热器**的等级。值范围从 0（关闭）到 3（高）                                                                                                                                                    |
| SeatHeaterRearRight                       | 气候     | 后排右侧**座椅加热器**的等级。值范围从 0（关闭）到 3（高）                                                                                                                                                    |
| SeatHeaterRight                           | 气候     | 右前**座椅加热器**的等级。值范围从 0（关闭）到 3（高）                                                                                                                                                        |
| SeatVentEnabled                           | 气候     | **前排座椅通风**是否启用                                                                                                                                                                                      |
| WiperHeatEnabled                          | 气候     | **雨刮器加热器**是否开启                                                                                                                                                                                      |
| BrakePedal                                | 驾驶     | **刹车踏板**的状态                                                                                                                                                                                            |
| BrakePedalPos                             | 驾驶     | 在 **ESP (电子稳定程序)** 中测得的**主缸压力**                                                                                                                                                                |
| CruiseSetSpeed                            | 驾驶     | **巡航控制**的设定点                                                                                                                                                                                          |
| DriveRail                                 | 驾驶     | 驱动电源的开启/关闭状态。所有与驱动相关的 ECU 均已就绪/供电。通常意味着踩下刹车踏板 + 钥匙认证或正在驾驶                                                                                                      |
| Gear                                      | 驾驶     | 检测由**驱动逆变器**报告的当前操作档位                                                                                                                                                                        |
| LateralAcceleration                       | 驾驶     | 车辆的**横向加速度**，单位为 G                                                                                                                                                                                |
| LongitudinalAcceleration                  | 驾驶     | 车辆的**纵向加速度**，单位为 G                                                                                                                                                                                |
| PedalPosition                             | 驾驶     | **加速踏板**的位置                                                                                                                                                                                            |
| RouteTrafficMinutesDelay                  | 驾驶     | 当前活动导航路线上的**交通延迟分钟数**                                                                                                                                                                        |
| VehicleSpeed                              | 驾驶     | 车辆的**速度**，单位为英里每小时                                                                                                                                                                              |
| DestinationLocation                       | 位置     | 当前导航路线**目的地**的坐标。如果未设置导航目的地，将返回 `Invalid`                                                                                                                                          |
| DestinationName                           | 位置     | 当前活动导航**目的地**的名称。如果未设置目的地，将报告 `Invalid`                                                                                                                                              |
| GpsHeading                                | 位置     | 车辆的**方向**。0 代表北，90 代表东，以此类推                                                                                                                                                                 |
| GpsState                                  | 位置     | **GPS 锁定**是否已获得                                                                                                                                                                                        |
| LocatedAtFavorite                         | 位置     | 车辆是否位于活动驾驶员配置文件的**收藏地点**                                                                                                                                                                  |
| LocatedAtHome                             | 位置     | 车辆是否位于活动驾驶员配置文件的**已保存的家庭位置**                                                                                                                                                          |
| LocatedAtWork                             | 位置     | 车辆是否位于活动驾驶员配置文件的**已保存的工作位置**                                                                                                                                                          |
| Location                                  | 位置     | 车辆的**纬度和经度**。从固件版本 2025.2.6 开始，可以为位置值指定最小增量 (minimum delta)。距离变化以米为单位测量                                                                                              |
| MilesToArrival                            | 位置     | 到达导航目的地所需的**英里数**。如果未设置导航目的地，将返回 `Invalid`                                                                                                                                        |
| MinutesToArrival                          | 位置     | 到达导航目的地所需的**分钟数**。如果未设置导航目的地，将返回 `Invalid`                                                                                                                                        |
| OriginLocation                            | 位置     | 当前导航路线**起点**的坐标                                                                                                                                                                                    |
| RouteLastUpdated                          | 位置     | 此字段已损坏，不返回数据                                                                                                                                                                                      |
| RouteLine                                 | 位置     | 当前活动导航路线的 **Base64 编码的折线 (polyline)**。要提取坐标，需解码 Base64 并使用 Google 的折线解码算法。使用**精度 6**                                                                                   |
| MediaAudioVolume                          | 媒体     | 车内**音频的音量**，测量范围为 0-11                                                                                                                                                                           |
| MediaAudioVolumeIncrement                 | 媒体     | 音量增加或减少的**增量大小**                                                                                                                                                                                  |
| MediaAudioVolumeMax                       | 媒体     | 可选择的**最大音量**                                                                                                                                                                                          |
| MediaNowPlayingAlbum                      | 媒体     | 当前曲目的**专辑**                                                                                                                                                                                            |
| MediaNowPlayingArtist                     | 媒体     | 当前曲目的**艺术家**                                                                                                                                                                                          |
| MediaNowPlayingDuration                   | 媒体     | 当前曲目的**长度**，单位为毫秒。对于没有时长的广播电台，报告 18000000                                                                                                                                         |
| MediaNowPlayingElapsed                    | 媒体     | 当前曲目的**播放位置**，单位为毫秒。收听广播电台时返回的值可能没有意义                                                                                                                                        |
| MediaNowPlayingStation                    | 媒体     | 正在播放媒体的**电台**                                                                                                                                                                                        |
| MediaNowPlayingTitle                      | 媒体     | 当前曲目的**标题**                                                                                                                                                                                            |
| MediaPlaybackSource                       | 媒体     | 当前用于播放媒体的**来源**                                                                                                                                                                                    |
| MediaPlaybackStatus                       | 媒体     | 媒体**播放的状态**                                                                                                                                                                                            |
| DiAxleSpeedF                              | 动力总成 | **前驱动逆变器**电机速度（轴级归一化）                                                                                                                                                                        |
| DiAxleSpeedR                              | 动力总成 | **后驱动逆变器**电机速度（轴级归一化）                                                                                                                                                                        |
| DiAxleSpeedREL                            | 动力总成 | **后左驱动逆变器**电机速度（轴级归一化）                                                                                                                                                                      |
| DiAxleSpeedRER                            | 动力总成 | **后右驱动逆变器**电机速度（轴级归一化）                                                                                                                                                                      |
| DiHeatsinkTF                              | 动力总成 | **前驱动逆变器散热片**温度                                                                                                                                                                                    |
| DiHeatsinkTR                              | 动力总成 | **后驱动逆变器散热片**温度                                                                                                                                                                                    |
| DiHeatsinkTREL                            | 动力总成 | **后左驱动逆变器散热片**温度                                                                                                                                                                                  |
| DiHeatsinkTRER                            | 动力总成 | **后右驱动逆变器散热片**温度                                                                                                                                                                                  |
| DiInverterTF                              | 动力总成 | **前驱动逆变器**测量的出口温度                                                                                                                                                                                |
| DiInverterTR                              | 动力总成 | **后驱动逆变器**测量的出口温度                                                                                                                                                                                |
| DiInverterTREL                            | 动力总成 | **后左驱动逆变器**测量的出口温度                                                                                                                                                                              |
| DiInverterTRER                            | 动力总成 | **后右驱动逆变器**测量的出口温度                                                                                                                                                                              |
| DiMotorCurrentF                           | 动力总成 | **前驱动逆变器**电机电流                                                                                                                                                                                      |
| DiMotorCurrentR                           | 动力总成 | **后驱动逆变器**电机电流                                                                                                                                                                                      |
| DiMotorCurrentREL                         | 动力总成 | **后左驱动逆变器**电机电流                                                                                                                                                                                    |
| DiMotorCurrentRER                         | 动力总成 | **后右驱动逆变器**电机电流                                                                                                                                                                                    |
| DiSlaveTorqueCmd                          | 动力总成 | 对**辅助驱动单元**的扭矩指令                                                                                                                                                                                  |
| DiStateF                                  | 动力总成 | **前驱动逆变器**状态                                                                                                                                                                                          |
| DiStateR                                  | 动力总成 | **后驱动逆变器**状态                                                                                                                                                                                          |
| DiStateREL                                | 动力总成 | **后左驱动逆变器**状态                                                                                                                                                                                        |
| DiStateRER                                | 动力总成 | **后右驱动逆变器**状态                                                                                                                                                                                        |
| DiStatorTempF                             | 动力总成 | **前驱动单元**定子温度                                                                                                                                                                                        |
| DiStatorTempR                             | 动力总成 | **后驱动单元**定子温度                                                                                                                                                                                        |
| DiStatorTempREL                           | 动力总成 | **后左驱动单元**定子温度                                                                                                                                                                                      |
| DiStatorTempRER                           | 动力总成 | **后右驱动单元**定子温度                                                                                                                                                                                      |
| DiTorqueActualF                           | 动力总成 | **前驱动单元**实际控制的扭矩（参考至车轴/车轮）                                                                                                                                                               |
| DiTorqueActualR                           | 动力总成 | **后驱动单元**实际控制的扭矩（参考至车轴/车轮）                                                                                                                                                               |
| DiTorqueActualREL                         | 动力总成 | **后左驱动单元**实际控制的扭矩（参考至车轴/车轮）                                                                                                                                                             |
| DiTorqueActualRER                         | 动力总成 | **后右驱动单元**实际控制的扭矩（参考至车轴/车轮）                                                                                                                                                             |
| DiTorquemotor                             | 动力总成 | 命令给驱动单元的扭矩（参考至车轴/车轮）                                                                                                                                                                       |
| DiVBatF                                   | 动力总成 | **前驱动逆变器**测量的电池电压                                                                                                                                                                                |
| DiVBatR                                   | 动力总成 | **后驱动逆变器**测量的电池电压                                                                                                                                                                                |
| DiVBatREL                                 | 动力总成 | **后左驱动逆变器**测量的电池电压                                                                                                                                                                              |
| DiVBatRER                                 | 动力总成 | **后右驱动逆变器**测量的电池电压                                                                                                                                                                              |
| Hvil                                      | 动力总成 | **高压互锁 (High Voltage Interlock)** 的状态                                                                                                                                                                  |
| AutomaticBlindSpotCamera                  | 安全     | 指示**盲点摄像头**是否启用                                                                                                                                                                                    |
| AutomaticEmergencyBrakingOff              | 安全     | 指示**自动紧急制动 (AEB)** 是否禁用                                                                                                                                                                           |
| BlindSpotCollisionWarningChime            | 安全     | **盲点碰撞警告蜂鸣器**是否启用                                                                                                                                                                                |
| CruiseFollowDistance                      | 安全     | 车辆控制中选择的**巡航跟车距离**                                                                                                                                                                              |
| DriverSeatBelt                            | 安全     | 指示驾驶员**是否解开安全带**                                                                                                                                                                                  |
| EmergencyLaneDepartureAvoidance           | 安全     | **紧急车道偏离辅助**是否启用                                                                                                                                                                                  |
| ForwardCollisionWarning                   | 安全     | 车辆设置中选择的**前方碰撞警告**灵敏度                                                                                                                                                                        |
| LaneDepartureAvoidance                    | 安全     | 车辆设置中选择的**车道辅助**等级                                                                                                                                                                              |
| Locked                                    | 安全     | 车辆是否**已锁定**                                                                                                                                                                                            |
| PassengerSeatBelt                         | 安全     | 此字段错误地报告**第二排中央安全带**是否已扣上                                                                                                                                                                |
| PinToDriveEnabled                         | 安全     | **Pin to Drive（输入密码才能驾驶）** 模式是否启用。Pin to Drive 要求在将车辆从驻车档换出之前输入密码                                                                                                          |
| SpeedLimitWarning                         | 安全     | 车辆设置中选择的**速度辅助**等级                                                                                                                                                                              |
| IsolationResistance                       | 服务     | **高压 (HV) 总线与底盘之间**的电阻                                                                                                                                                                            |
| SemitruckTpmsPressureRe1L0                | 服务     | **半挂车 (Semitruck) 中轴左轮胎**的最后测量胎压，单位为大气压。L0 和 L1 报告同一轮胎的两次测量值                                                                                                              |
| SemitruckTpmsPressureRe1L1                | 服务     | **半挂车中轴左轮胎**的最后测量胎压，单位为大气压。L0 和 L1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe1R0                | 服务     | **半挂车中轴右轮胎**的最后测量胎压，单位为大气压。R0 和 R1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe1R1                | 服务     | **半挂车中轴右轮胎**的最后测量胎压，单位为大气压。R0 和 R1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe2L0                | 服务     | **半挂车后轴左轮胎**的最后测量胎压，单位为大气压。L0 和 L1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe2L1                | 服务     | **半挂车后轴左轮胎**的最后测量胎压，单位为大气压。L0 和 L1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe2R0                | 服务     | **半挂车后轴右轮胎**的最后测量胎压，单位为大气压。R0 和 R1 报告同一轮胎的两次测量值                                                                                                                           |
| SemitruckTpmsPressureRe2R1                | 服务     | **半挂车后轴右轮胎**的最后测量胎压，单位为大气压。R0 和 R1 报告同一轮胎的两次测量值                                                                                                                           |
| TpmsHardWarnings                          | 服务     | 指示轮胎压力需要检查，并且**严重超出标称范围**（胎压硬性警告）                                                                                                                                                |
| TpmsLastSeenPressureTimeFl                | 服务     | **左前轮胎压**最后测量的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                        |
| TpmsLastSeenPressureTimeFr                | 服务     | **右前轮胎压**最后测量的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                        |
| TpmsLastSeenPressureTimeRl                | 服务     | **左后轮胎压**最后测量的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                        |
| TpmsLastSeenPressureTimeRr                | 服务     | **右后轮胎压**最后测量的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                        |
| TpmsPressureFl                            | 服务     | **左前轮胎**的最后测量胎压，单位为大气压                                                                                                                                                                      |
| TpmsPressureFr                            | 服务     | **右前轮胎**的最后测量胎压，单位为大气压                                                                                                                                                                      |
| TpmsPressureRl                            | 服务     | **左后轮胎**的最后测量胎压，单位为大气压                                                                                                                                                                      |
| TpmsPressureRr                            | 服务     | **右后轮胎**的最后测量胎压，单位为大气压                                                                                                                                                                      |
| TpmsSoftWarnings                          | 服务     | 指示轮胎压力需要检查，并且**略微超出标称范围**（胎压软性警告）                                                                                                                                                |
| Setting24HourTime                         | 用户偏好 | 显示时间是否偏好**24 小时制**                                                                                                                                                                                 |
| SettingChargeUnit                         | 用户偏好 | 显示充电续航里程的首选单位                                                                                                                                                                                    |
| SettingDistanceUnit                       | 用户偏好 | 车辆显示距离时使用的单位                                                                                                                                                                                      |
| SettingTemperatureUnit                    | 用户偏好 | 显示温度数据的首选单位                                                                                                                                                                                        |
| SettingTirePressureUnit                   | 用户偏好 | 显示压力数据的首选单位                                                                                                                                                                                        |
| CarType                                   | 车辆配置 | 车辆的**型号**                                                                                                                                                                                                |
| EfficiencyPackage                         | 车辆配置 | 车辆的**效率套件**。由于可能的值因车型和平台而异，因此以字符串形式返回                                                                                                                                        |
| EuropeVehicle                             | 车辆配置 | 此车辆是否被归类为**欧洲车辆**                                                                                                                                                                                |
| ExteriorColor                             | 车辆配置 | 车辆的**外部颜色**                                                                                                                                                                                            |
| OffroadLightbarPresent                    | 车辆配置 | 报告是否检测到**越野灯条**                                                                                                                                                                                    |
| RearSeatHeaters                           | 车辆配置 | 安装在车辆上的**后排座椅加热套件**                                                                                                                                                                            |
| RemoteStartEnabled                        | 车辆配置 | 车辆是否在**没有物理钥匙**的情况下被驾驶                                                                                                                                                                      |
| RightHandDrive                            | 车辆配置 | 车辆是否为**右舵驾驶**车辆                                                                                                                                                                                    |
| RoofColor                                 | 车辆配置 | **车顶**的颜色                                                                                                                                                                                                |
| SunroofInstalled                          | 车辆配置 | **天窗**的安装状态                                                                                                                                                                                            |
| Trim                                      | 车辆配置 | 车辆的**装饰/配置**                                                                                                                                                                                           |
| VehicleName                               | 车辆配置 | 车辆的**昵称**                                                                                                                                                                                                |
| Version                                   | 车辆配置 | 车辆当前的**固件版本**。在早于 2024.44 的固件版本中，此字段返回的是可用软件更新的版本。此数据现可通过 `SoftwareUpdateVersion` 获取                                                                            |
| WheelType                                 | 车辆配置 | 车辆上安装的**车轮类型**                                                                                                                                                                                      |
| CenterDisplay                             | 车辆状态 | **中央显示屏**的状态                                                                                                                                                                                          |
| CurrentLimitMph                           | 车辆状态 | 允许车辆行驶的**最大速度**（英里每小时）                                                                                                                                                                      |
| DoorState                                 | 车辆状态 | 当前**打开的车门**。在固件版本早于 2024.44.32 中，此字段中的乘客前门和驾驶员后门是互换的                                                                                                                      |
| DriverSeatOccupied                        | 车辆状态 | 驾驶员**在位状态**，取决于平台上的多种来源组合确定                                                                                                                                                            |
| FdWindow                                  | 车辆状态 | **前驾驶员侧车窗**的状态                                                                                                                                                                                      |
| FpWindow                                  | 车辆状态 | **前乘客侧车窗**的状态                                                                                                                                                                                        |
| GuestModeEnabled                          | 车辆状态 | **访客模式**是否启用                                                                                                                                                                                          |
| GuestModeMobileAccessState                | 车辆状态 | **访客模式**的状态                                                                                                                                                                                            |
| HomelinkDeviceCount                       | 车辆状态 | 附近 **Homelink 设备**的数量                                                                                                                                                                                  |
| HomelinkNearby                            | 车辆状态 | 附近是否有 **Homelink 设备**                                                                                                                                                                                  |
| LightsHazardsActive                       | 车辆状态 | 车辆的**危险警示灯**是否激活                                                                                                                                                                                  |
| LightsHighBeams                           | 车辆状态 | 车辆的**远光灯**是否激活                                                                                                                                                                                      |
| LightsTurnSignal                          | 车辆状态 | **转向灯**的状态。左、右、双闪、无                                                                                                                                                                            |
| Odometer                                  | 车辆状态 | 车辆已行驶的**里程数**（英里）。从固件版本 2025.2.6 开始，`Odometer` 的最小增量默认设置为 0.1                                                                                                                 |
| PairedPhoneKeyAndKeyFobQty                | 车辆状态 | 与车辆配对的**手机钥匙和实体钥匙卡**的数量                                                                                                                                                                    |
| RdWindow                                  | 车辆状态 | **后驾驶员侧车窗**的状态                                                                                                                                                                                      |
| RpWindow                                  | 车辆状态 | **后乘客侧车窗**的状态                                                                                                                                                                                        |
| SemitruckPassengerSeatFoldPosition        | 车辆状态 | **半挂车乘客座椅**位置的状态                                                                                                                                                                                  |
| SemitruckTractorParkBrakeStatus           | 车辆状态 | **半挂车牵引车驻车制动**的状态                                                                                                                                                                                |
| SemitruckTrailerParkBrakeStatus           | 车辆状态 | **半挂车拖车驻车制动**的状态                                                                                                                                                                                  |
| SentryMode                                | 车辆状态 | **哨兵模式**的当前状态                                                                                                                                                                                        |
| ServiceMode                               | 车辆状态 | **服务模式**是否启用                                                                                                                                                                                          |
| SoftwareUpdateDownloadPercentComplete     | 车辆状态 | 软件更新已**下载的百分比**。注意：在下载一个软件更新期间，此值会多次从 0% 达到 100%                                                                                                                           |
| SoftwareUpdateExpectedDurationMinutes     | 车辆状态 | 软件更新**预计所需**的分钟数                                                                                                                                                                                  |
| SoftwareUpdateInstallationPercentComplete | 车辆状态 | 软件更新**安装完成的百分比**。在整个软件更新期间，车辆不会一直连接到 Fleet Telemetry                                                                                                                          |
| SoftwareUpdateScheduledStartTime          | 车辆状态 | 软件更新预定开始安装的时间。时间戳字段报告不正确。将报告的值视为太平洋时间将得出车辆时区的日期和时间                                                                                                          |
| SoftwareUpdateVersion                     | 车辆状态 | **可用软件更新**的版本                                                                                                                                                                                        |
| SpeedLimitMode                            | 车辆状态 | **限速模式**是否启用                                                                                                                                                                                          |
| TonneauOpenPercent                        | 车辆状态 | Cybertruck 的**货箱盖**开启的百分比                                                                                                                                                                           |
| TonneauPosition                           | 车辆状态 | Cybertruck 的**货箱盖**状态                                                                                                                                                                                   |
| TonneauTentMode                           | 车辆状态 | Cybertruck 的**货箱盖**与**帐篷模式**的关系状态                                                                                                                                                               |
| ValetModeEnabled                          | 车辆状态 | **代客泊车模式**是否启用                                                                                                                                                                                      |

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
        "resend_interval_seconds": 86400,
        "description": "车辆速度 (km/h 或 mph)"
      },
      "PedalPosition": {
        "interval_seconds": 1,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "加速踏板位置百分比 (%)"
      },
      "Gear": {
        "interval_seconds": 2,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前档位 (P/N/D/R)"
      },
      "BrakePedal": {
        "interval_seconds": 2,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "刹车踏板按下状态"
      },
      "BrakePedalPos": {
        "interval_seconds": 2,
        "minimum_delta": 0.001,
        "resend_interval_seconds": 86400,
        "description": "刹车踏板位置百分比 (%)"
      },
      "DiTorquemotor": {
        "interval_seconds": 2,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "电机扭矩输出 (Nm)"
      },
      "位置": {
        "interval_seconds": 5,
        "minimum_delta": 0.00002,
        "resend_interval_seconds": 60,
        "description": "GPS当前位置 (经纬度)"
      },
      "GpsHeading": {
        "interval_seconds": 5,
        "minimum_delta": 0.0001,
        "resend_interval_seconds": 86400,
        "description": "GPS航向角度 (度)"
      },
      "Locked": {
        "interval_seconds": 5,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆锁闭状态"
      },
      "DoorState": {
        "interval_seconds": 5,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车门打开/关闭状态"
      },
      "LightsTurnSignal": {
        "interval_seconds": 10,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "转向灯信号状态"
      },
      "LightsHighBeams": {
        "interval_seconds": 10,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "远光灯开启状态"
      },
      "LightsHazardsActive": {
        "interval_seconds": 10,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "危险警示灯激活状态"
      },
      "ChargeState": {
        "interval_seconds": 10,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电状态 (充电中/未充电/完成等)"
      },
      "DCChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "DC充电功率 (kW)"
      },
      "ACChargingPower": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "AC充电功率 (kW)"
      },
      "ChargeAmps": {
        "interval_seconds": 10,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "当前充电电流 (A)"
      },
      "ChargeRateMilePerHour": {
        "interval_seconds": 10,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "充电速率 (mi/h)"
      },
      "ChargerVoltage": {
        "interval_seconds": 10,
        "minimum_delta": 0.2,
        "resend_interval_seconds": 86400,
        "description": "充电器电压 (V)"
      },
      "ChargerPhases": {
        "interval_seconds": 30,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电相数"
      },
      "FastChargerPresent": {
        "interval_seconds": 30,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "快速充电器连接状态"
      },
      "FastChargerType": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "快速充电器类型"
      },
      "ChargingCableType": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电电缆类型"
      },
      "ChargePort": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电端口状态"
      },
      "ChargePortDoorOpen": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电端口门打开状态"
      },
      "ChargePortLatch": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电端口锁扣状态"
      },
      "DetailedChargeState": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "详细充电状态信息"
      },
      "ChargeEnableRequest": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电启用请求状态"
      },
      "ChargeCurrentRequest": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "请求充电电流 (A)"
      },
      "ChargeCurrentRequestMax": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "最大请求充电电流 (A)"
      },
      "ChargeLimitSoc": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "充电上限SOC百分比 (%)"
      },
      "TimeToFullCharge": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "充满电预计剩余时间 (min)"
      },
      "EstimatedHoursToChargeTermination": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "预计充电完成剩余小时数"
      },
      "Soc": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "电池荷电状态 (SOC，%)"
      },
      "BatteryLevel": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "电池电量百分比 (%)"
      },
      "EnergyRemaining": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "剩余电池能量 (kWh)"
      },
      "PackVoltage": {
        "interval_seconds": 30,
        "minimum_delta": 0.5,
        "resend_interval_seconds": 86400,
        "description": "电池组电压 (V)"
      },
      "PackCurrent": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "电池组电流 (A)"
      },
      "BMSState": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "电池管理系统当前状态"
      },
      "BmsFullchargecomplete": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "电池管理系统充满电完成状态"
      },
      "DCDCEnable": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "DC-DC转换器启用状态"
      },
      "BatteryHeaterOn": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "电池加热器启用状态"
      },
      "NotEnoughPowerToHeat": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
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
        "resend_interval_seconds": 86400,
        "description": "电池砖块最大电压值 (V)"
      },
      "BrickVoltageMin": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "电池砖块最小电压值 (V)"
      },
      "NumBrickVoltageMax": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "达到最大电压的电池砖块数量"
      },
      "NumBrickVoltageMin": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "达到最小电压的电池砖块数量"
      },
      "ModuleTempMax": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "电池模块最高温度 (℃)"
      },
      "ModuleTempMin": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "电池模块最低温度 (℃)"
      },
      "NumModuleTempMax": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "达到最高温度的电池模块数量"
      },
      "NumModuleTempMin": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "达到最低温度的电池模块数量"
      },
      "DiStateF": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前电机运行状态"
      },
      "DiStateR": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后电机运行状态"
      },
      "DiStateREL": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "左后电机运行状态"
      },
      "DiStateRER": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "右后电机运行状态"
      },
      "DiAxleSpeedF": {
        "interval_seconds": 10,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "前轴转速 (RPM)"
      },
      "DiAxleSpeedR": {
        "interval_seconds": 10,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "后轴转速 (RPM)"
      },
      "DiAxleSpeedREL": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "左后轴转速 (RPM)"
      },
      "DiAxleSpeedRER": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "右后轴转速 (RPM)"
      },
      "DiTorqueActualF": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "前电机实际扭矩 (Nm)"
      },
      "DiTorqueActualR": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机实际扭矩 (Nm)"
      },
      "DiTorqueActualREL": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后电机实际扭矩 (Nm)"
      },
      "DiTorqueActualRER": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后电机实际扭矩 (Nm)"
      },
      "DiSlaveTorqueCmd": {
        "interval_seconds": 5,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "从电机扭矩指令 (Nm)"
      },
      "DiMotorCurrentF": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "前电机电流 (A)"
      },
      "DiMotorCurrentR": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机电流 (A)"
      },
      "DiMotorCurrentREL": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后电机电流 (A)"
      },
      "DiMotorCurrentRER": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后电机电流 (A)"
      },
      "DiVBatF": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "前电机电池电压 (V)"
      },
      "DiVBatR": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机电池电压 (V)"
      },
      "DiVBatREL": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "左后电机电池电压 (V)"
      },
      "DiVBatRER": {
        "interval_seconds": 30,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "右后电机电池电压 (V)"
      },
      "DiStatorTempF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "前电机定子温度 (℃)"
      },
      "DiStatorTempR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机定子温度 (℃)"
      },
      "DiStatorTempREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后电机定子温度 (℃)"
      },
      "DiStatorTempRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后电机定子温度 (℃)"
      },
      "DiHeatsinkTF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "前电机散热片温度 (℃)"
      },
      "DiHeatsinkTR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机散热片温度 (℃)"
      },
      "DiHeatsinkTREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后电机散热片温度 (℃)"
      },
      "DiHeatsinkTRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后电机散热片温度 (℃)"
      },
      "DiInverterTF": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "前电机逆变器温度 (℃)"
      },
      "DiInverterTR": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "后电机逆变器温度 (℃)"
      },
      "DiInverterTREL": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后电机逆变器温度 (℃)"
      },
      "DiInverterTRER": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后电机逆变器温度 (℃)"
      },
      "DriveRail": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "驱动总线系统状态"
      },
      "Odometer": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "车辆总里程 (km/mi)"
      },
      "RatedRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "额定续航里程 (km/mi)"
      },
      "EstBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "估计电池续航里程 (km/mi)"
      },
      "IdealBatteryRange": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "理想电池续航里程 (km/mi)"
      },
      "DCChargingEnergyIn": {
        "interval_seconds": 60,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "DC充电输入能量 (kWh)"
      },
      "ACChargingEnergyIn": {
        "interval_seconds": 60,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "AC充电输入能量 (kWh)"
      },
      "LifetimeEnergyUsed": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "累计能量消耗 (kWh)"
      },
      "LifetimeEnergyGainedRegen": {
        "interval_seconds": 3600,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "累计再生制动能量回收 (kWh)"
      },
      "InsideTemp": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "resend_interval_seconds": 86400,
        "description": "车内温度 (℃)"
      },
      "OutsideTemp": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "resend_interval_seconds": 86400,
        "description": "车外温度 (℃)"
      },
      "HvacACEnabled": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "空调压缩机启用状态"
      },
      "HvacAutoMode": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "HVAC自动模式状态"
      },
      "HvacFanSpeed": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "HVAC风扇速度设置"
      },
      "HvacFanStatus": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "HVAC风扇运行状态"
      },
      "HvacLeftTemperatureRequest": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "resend_interval_seconds": 86400,
        "description": "左侧HVAC温度设定 (℃)"
      },
      "HvacRightTemperatureRequest": {
        "interval_seconds": 60,
        "minimum_delta": 0.5,
        "resend_interval_seconds": 86400,
        "description": "右侧HVAC温度设定 (℃)"
      },
      "HvacPower": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "HVAC电源消耗状态"
      },
      "HvacSteeringWheelHeatAuto": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "方向盘加热自动模式"
      },
      "HvacSteeringWheelHeatLevel": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "方向盘加热等级"
      },
      "SeatHeaterLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左前座椅加热等级"
      },
      "SeatHeaterRight": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右前座椅加热等级"
      },
      "SeatHeaterRearLeft": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "左后座椅加热等级"
      },
      "SeatHeaterRearRight": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "右后座椅加热等级"
      },
      "SeatHeaterRearCenter": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "中后座椅加热等级"
      },
      "AutoSeatClimateLeft": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "左前座自动气候控制状态"
      },
      "AutoSeatClimateRight": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "右前座自动气候控制状态"
      },
      "ClimateSeatCoolingFrontLeft": {
        "interval_seconds": 120,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "左前座椅冷却状态"
      },
      "ClimateSeatCoolingFrontRight": {
        "interval_seconds": 120,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "右前座椅冷却状态"
      },
      "RearSeatHeaters": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后排座椅加热状态"
      },
      "RearDisplayHvacEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后排显示屏HVAC控制启用状态"
      },
      "DefrostMode": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "除霜模式状态"
      },
      "DefrostForPreconditioning": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "预调节化霜状态"
      },
      "RearDefrostEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后窗除霜启用状态"
      },
      "ClimateKeeperMode": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "气候保持模式"
      },
      "CabinOverheatProtectionMode": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "驾驶舱过热保护模式"
      },
      "CabinOverheatProtectionTemperatureLimit": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "驾驶舱过热保护温度上限 (℃)"
      },
      "EfficiencyPackage": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "高效驾驶套件启用状态"
      },
      "WiperHeatEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "雨刷加热启用状态"
      },
      "DriverSeatBelt": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "驾驶员安全带扣紧状态"
      },
      "PassengerSeatBelt": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "副驾驶安全带扣紧状态"
      },
      "DriverSeatOccupied": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "驾驶员座位占用状态"
      },
      "LateralAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "横向加速度 (m/s²)"
      },
      "LongitudinalAcceleration": {
        "interval_seconds": 60,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "纵向加速度 (m/s²)"
      },
      "CruiseSetSpeed": {
        "interval_seconds": 30,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "定速巡航设定速度 (km/h)"
      },
      "CruiseFollowDistance": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "自适应巡航跟车距离设置"
      },
      "SpeedLimitMode": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "限速模式启用状态"
      },
      "CurrentLimitMph": {
        "interval_seconds": 60,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "当前限速值 (mph)"
      },
      "SpeedLimitWarning": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "超速警告设置"
      },
      "ForwardCollisionWarning": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前向碰撞警告系统状态"
      },
      "AutomaticEmergencyBrakingOff": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "自动紧急制动关闭状态"
      },
      "LaneDepartureAvoidance": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车道偏离避免系统状态"
      },
      "EmergencyLaneDepartureAvoidance": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "紧急车道偏离避免系统状态"
      },
      "BlindSpotCollisionWarningChime": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "盲点碰撞警告蜂鸣器状态"
      },
      "AutomaticBlindSpotCamera": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "自动盲点摄像头启用状态"
      },
      "GpsState": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "GPS信号可用状态"
      },
      "TpmsPressureFl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "前左轮胎气压 (psi/bar)"
      },
      "TpmsPressureFr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "前右轮胎气压 (psi/bar)"
      },
      "TpmsPressureRl": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "后左轮胎气压 (psi/bar)"
      },
      "TpmsPressureRr": {
        "interval_seconds": 300,
        "minimum_delta": 0.01,
        "resend_interval_seconds": 86400,
        "description": "后右轮胎气压 (psi/bar)"
      },
      "TpmsHardWarnings": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "胎压监测硬警告信息"
      },
      "TpmsSoftWarnings": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "胎压监测软警告信息"
      },
      "TpmsLastSeenPressureTimeFl": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前左胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeFr": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前右胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeRl": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后左胎压最后读取时间"
      },
      "TpmsLastSeenPressureTimeRr": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后右胎压最后读取时间"
      },
      "FdWindow": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前左车窗位置状态"
      },
      "FpWindow": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "前右车窗位置状态"
      },
      "RdWindow": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后左车窗位置状态"
      },
      "RpWindow": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "后右车窗位置状态"
      },
      "SunroofInstalled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "天窗安装状态"
      },
      "TonneauPosition": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "货厢盖位置状态"
      },
      "TonneauOpenPercent": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "货厢盖打开百分比 (%)"
      },
      "TonneauTentMode": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "货厢盖帐篷模式状态"
      },
      "OffroadLightbarPresent": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "越野灯条安装状态"
      },
      "CenterDisplay": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "中控显示屏状态"
      },
      "MediaPlaybackStatus": {
        "interval_seconds": 120,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "媒体播放状态"
      },
      "MediaPlaybackSource": {
        "interval_seconds": 120,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "媒体播放来源"
      },
      "MediaNowPlayingTitle": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放曲目标题"
      },
      "MediaNowPlayingArtist": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放艺术家名称"
      },
      "MediaNowPlayingAlbum": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放专辑名称"
      },
      "MediaNowPlayingStation": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放电台名称"
      },
      "MediaNowPlayingDuration": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放总时长 (秒)"
      },
      "MediaNowPlayingElapsed": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前播放已过时间 (秒)"
      },
      "MediaAudioVolume": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "媒体音频音量水平"
      },
      "MediaAudioVolumeMax": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "媒体音频最大音量"
      },
      "MediaAudioVolumeIncrement": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "媒体音频音量增量步长"
      },
      "SeatVentEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "座椅通风启用状态"
      },
      "RemoteStartEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "远程启动功能启用状态"
      },
      "ServiceMode": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "服务/维修模式状态"
      },
      "SentryMode": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "哨兵模式启用状态"
      },
      "ValetModeEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "代客泊车模式启用状态"
      },
      "GuestModeEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "访客模式启用状态"
      },
      "GuestModeMobileAccessState": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "访客模式移动访问权限状态"
      },
      "PinToDriveEnabled": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "PIN to Drive安全功能启用状态"
      },
      "PairedPhoneKeyAndKeyFobQty": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "配对手机钥匙和钥匙扣数量"
      },
      "HomelinkDeviceCount": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "HomeLink设备配对数量"
      },
      "HomelinkNearby": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "附近HomeLink设备检测状态"
      },
      "PowershareStatus": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "PowerShare功能状态"
      },
      "PowershareType": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "PowerShare类型"
      },
      "PowershareHoursLeft": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "PowerShare剩余可用小时数"
      },
      "PowershareInstantaneousPowerKW": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "PowerShare瞬时功率 (kW)"
      },
      "PowershareStopReason": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "PowerShare停止原因"
      },
      "SettingDistanceUnit": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "距离单位设置 (km/mi)"
      },
      "SettingTemperatureUnit": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "温度单位设置 (℃/℉)"
      },
      "Setting24HourTime": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "24小时制时间显示设置"
      },
      "SettingTirePressureUnit": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "胎压单位设置 (psi/bar)"
      },
      "SettingChargeUnit": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "充电单位设置 (kWh/mi)"
      },
      "RightHandDrive": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "右舵驾驶车辆标识"
      },
      "EuropeVehicle": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "欧洲规格车辆标识"
      },
      "WheelType": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "轮毂类型"
      },
      "CarType": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆车型类型"
      },
      "Trim": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆配置等级"
      },
      "ExteriorColor": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车身外部颜色"
      },
      "RoofColor": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车顶颜色"
      },
      "VehicleName": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆自定义名称"
      },
      "Version": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "软件版本号"
      },
      "SoftwareUpdateVersion": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "软件更新版本号"
      },
      "SoftwareUpdateDownloadPercentComplete": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "软件更新下载完成百分比 (%)"
      },
      "SoftwareUpdateInstallationPercentComplete": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "软件更新安装完成百分比 (%)"
      },
      "SoftwareUpdateExpectedDurationMinutes": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "软件更新预计持续时间 (分钟)"
      },
      "SoftwareUpdateScheduledStartTime": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "软件更新计划开始时间"
      },
      "SuperchargerSessionTripPlanner": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "超级充电会话行程规划信息"
      },
      "RouteLastUpdated": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "导航路线最后更新时间 (固件2024.26+)"
      },
      "RouteLine": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "当前导航路线数据 (固件2024.26+)"
      },
      "MilesToArrival": {
        "interval_seconds": 300,
        "minimum_delta": 0.1,
        "resend_interval_seconds": 86400,
        "description": "导航剩余里程 (mi，固件2024.26+)"
      },
      "MinutesToArrival": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "导航剩余时间 (min，固件2024.26+)"
      },
      "ExpectedEnergyPercentAtTripArrival": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "预计行程结束时剩余电量百分比 (%)"
      },
      "RouteTrafficMinutesDelay": {
        "interval_seconds": 300,
        "minimum_delta": 1,
        "resend_interval_seconds": 86400,
        "description": "导航路线交通延迟 (分钟)"
      },
      "OriginLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001,
        "resend_interval_seconds": 86400,
        "description": "导航起点位置 (经纬度，固件2024.26+)"
      },
      "DestinationLocation": {
        "interval_seconds": 300,
        "minimum_delta": 0.00001,
        "resend_interval_seconds": 86400,
        "description": "导航终点位置 (经纬度，固件2024.26+)"
      },
      "DestinationName": {
        "interval_seconds": 60,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "导航目的地名称 (固件2024.26+)"
      },
      "LocatedAtHome": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆位于家位置状态"
      },
      "LocatedAtWork": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆位于工作位置状态"
      },
      "LocatedAtFavorite": {
        "interval_seconds": 300,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "车辆位于收藏位置状态"
      },
      "Deprecated_2": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
        "description": "已废弃字段 (请忽略)"
      },
      "Deprecated_3": {
        "interval_seconds": 3600,
        "minimum_delta": null,
        "resend_interval_seconds": 86400,
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
