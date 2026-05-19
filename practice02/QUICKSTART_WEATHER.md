# 天气查询功能 - 快速开始

## 🚀 立即体验

### 1. 测试基本功能

```bash
cd practice02
python test_weather.py
```

这将测试：
- 北京天气（中文城市名）
- 纽约天气（中文国际城市名）
- London天气（英文城市名）
- 桂林天气（较小的中国城市）

### 2. 查看全球城市支持

```bash
python test_global_weather.py
```

这将演示查询多个不同类型的城市，包括中国城市、国际城市等。

## 💡 在代码中使用

```python
from weather_tool import get_weather
import json

# 简单查询
result = get_weather('北京')
print(json.dumps(result, ensure_ascii=False, indent=2))

# 查询国际城市
result = get_weather('New York')
print(f"温度: {result['current_weather']['temperature']}")
print(f"天气: {result['current_weather']['weather']}")

# 查看预报
for day in result['forecast']:
    print(f"{day['date']}: {day['weather']}")
```

## 🌍 支持的城市类型

### ✅ 中国城市
- 主要城市：北京、上海、广州、深圳、成都等
- 省会城市：杭州、南京、武汉、西安等
- 中小城市：桂林、大理、丽江等

### ✅ 国际城市（中文名）
- 纽约、伦敦、巴黎、东京、首尔
- 新加坡、悉尼、墨尔本、迪拜等

### ✅ 国际城市（英文名）
- New York, London, Paris, Tokyo
- Sydney, Singapore, Los Angeles等

### ✅ 任何有地理记录的城市
只要Open-Meteo数据库中有记录的城市都可以查询！

## 📊 返回数据说明

```python
{
  "success": true,
  "location": {
    "city": "城市名",
    "country": "国家",
    "latitude": 纬度,
    "longitude": 经度
  },
  "current_weather": {
    "temperature": "当前温度",
    "feels_like": "体感温度",
    "weather": "天气状况",
    "humidity": "湿度",
    "wind_speed": "风速",
    "precipitation": "降水量",
    "is_day": "白天/夜晚"
  },
  "forecast": [
    {
      "date": "日期",
      "weather": "天气",
      "max_temp": "最高温",
      "min_temp": "最低温",
      "precipitation": "降水",
      "sunrise": "日出时间",
      "sunset": "日落时间"
    }
  ]
}
```

## 🎯 使用技巧

### 1. 处理歧义城市
如果城市名有歧义，可以加上国家：
```python
get_weather('美国纽约')  # 明确指定美国
get_weather('英国London')  # 明确指定英国
```

### 2. 中英文混用
系统会自动识别和处理：
```python
get_weather('北京')      # 中文
get_weather('Beijing')   # 英文
# 两者都能正确识别
```

### 3. 错误处理
```python
result = get_weather('不存在的城市')
if result.get('error'):
    print(f"查询失败: {result['error']}")
else:
    # 处理成功结果
    pass
```

## 🔧 API说明

### 函数签名
```python
def get_weather(city: str = "Beijing") -> dict
```

### 参数
- `city`: 城市名称（字符串），支持中文和英文

### 返回值
- `dict`: 包含天气信息的字典
  - `success`: 布尔值，表示是否成功
  - `message`: 提示信息
  - `location`: 位置信息
  - `current_weather`: 当前天气
  - `forecast`: 未来天气预报（3天）
  - `error`: 如果失败，包含错误信息

## ⚙️ 技术细节

### API提供商
- **地理编码**: Open-Meteo Geocoding API
- **天气数据**: Open-Meteo Weather API
- **网址**: https://open-meteo.com/

### 优势
- ✅ 完全免费
- ✅ 无需API密钥
- ✅ 全球覆盖
- ✅ 高可靠性

### 智能匹配
系统使用多维度评分算法：
1. 人口规模权重
2. 行政级别识别
3. 名称匹配度
4. 国家/地区判断
5. 国际大都市识别

确保即使有同名城市，也能选择最可能的那个。

## ❓ 常见问题

**Q: 为什么有些小城市查不到？**
A: 只要该城市在Open-Meteo的地理数据库中有记录就能查到。极小的村庄可能没有记录。

**Q: 同名城市怎么办？**
A: 系统会根据人口、行政级别等因素智能选择最可能的城市。你也可以在查询时加上国家名来明确指定。

**Q: 需要网络连接吗？**
A: 是的，需要访问Open-Meteo的API服务器。

**Q: 支持多少个城市？**
A: 理论上支持全球所有在Open-Meteo数据库中的城市，数量非常庞大。

**Q: 数据更新频率如何？**
A: 天气数据每小时更新，预报数据每天更新多次。

## 📝 下一步

- 查看详细文档：`WEATHER_UPGRADE.md`
- 查看源代码：`weather_tool.py`
- 在聊天客户端中试用：`python chat_client.py`

---

**享受全球天气查询功能！** 🌤️🌍