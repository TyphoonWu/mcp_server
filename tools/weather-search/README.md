## Installation

1. Install dependencies:
```bash
npm install
```

2. Build the project:
```bash
npm run build
```

3. Debug project:
```bash
npx @modelcontextprotocol/inspector node build/index.js
```

### weather URL
#### https://weather.cma.cn/web/weather/map.html#

#### https://weather.cma.cn/api/map/weather/1
```json
{
    "msg": "success",
    "code": 0,
    "data": {
        "lastUpdate": "2025/06/14 12:00",
        "date": "2025/06/14",
        "city": [
            [
                "54511",    // 站点编号
                "北京",     // 城市名
                "中国",     // 国家
                0,          //未知
                39.81,      // 纬度
                116.47,     // 经度
                24.0,       // 最高温度
                "中雨",     // 天气
                8,          // 风力
                "东北风",   // 风向
                "微风",     // 风级
                19.0,       // 最底温度
                "雷阵雨",   // 天气2
                4,          // 风力2
                "西北风",   // 风向2
                "微风",     // 风级2
                "ABJ",      // 城市代码
                "110115"    // 区县代码
            ]
        ]
    }
}
```

#### https://weather.cma.cn/api/now/54511
```json
{
  "msg": "success",
  "code": 0,
  "data": {
    "location": {
      "id": "54511",
      "name": "北京",
      "path": "中国, 北京, 北京"
    },
    "now": {
      "precipitation": 0.5,
      "temperature": 19.9,
      "pressure": 996,
      "humidity": 95,
      "windDirection": "西北风",
      "windDirectionDegree": 357,
      "windSpeed": 1.4,
      "windScale": "微风",
      "feelst": 22.1
    },
    "alarm": [
      {
        "id": "11000041600000_20250614083511",
        "title": "北京市气象台2025年6月14日08时25分发布暴雨蓝色预警信号",
        "signaltype": "暴雨",
        "signallevel": "蓝色",
        "effective": "2025/06/14 08:25",
        "eventType": "11B03",
        "severity": "BLUE",
        "type": "p0002004"
      },
      {
        "id": "11000041600000_20250614074851",
        "title": "北京市气象台2025年6月14日07时35分发布雷电蓝色预警信号",
        "signaltype": "雷电",
        "signallevel": "蓝色",
        "effective": "2025/06/14 07:35",
        "eventType": "11B14",
        "severity": "BLUE",
        "type": "p0012004"
      }
    ],
    "jieQi": "",
    "lastUpdate": "2025/06/14 17:05"
  }
}
```
