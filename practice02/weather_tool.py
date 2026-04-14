"""
天气查询工具
使用免费的天气API查询天气信息
"""
import json
from http.client import HTTPSConnection
from urllib.parse import urlencode


def get_weather(city: str = "Beijing") -> dict:
    """
    查询指定城市的天气信息
    
    Args:
        city: 城市名称，默认为北京
        
    Returns:
        包含天气信息的字典
    """
    try:
        from urllib.parse import quote
        
        # 常见城市名称映射（中文 -> 英文）
        city_name_map = {
            '北京': 'Beijing',
            '上海': 'Shanghai',
            '广州': 'Guangzhou',
            '深圳': 'Shenzhen',
            '成都': 'Chengdu',
            '杭州': 'Hangzhou',
            '重庆': 'Chongqing',
            '西安': 'Xi\'an',
            '武汉': 'Wuhan',
            '南京': 'Nanjing',
        }
        
        # 如果是中文城市名，转换为英文
        search_city = city_name_map.get(city, city)
        encoded_city = quote(search_city)
        
        # 使用 Open-Meteo API（免费，无需API密钥）
        # 首先获取城市的经纬度
        conn = HTTPSConnection("geocoding-api.open-meteo.com", timeout=10)
        conn.request("GET", f"/v1/search?name={encoded_city}&count=5&language=en&format=json")
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        
        if response.status != 200:
            return {"error": f"获取城市信息失败，状态码: {response.status}"}
        
        geocode_result = json.loads(data)
        
        if not geocode_result.get('results'):
            return {"error": f"未找到城市: {city}"}
        
        # 选择最匹配的城市（优先选择人口最多的）
        results = geocode_result['results']
        # 按人口排序，如果没有人口信息则按名称精确匹配
        results_with_population = []
        for loc in results:
            # 检查是否是主要城市（有人口数据或者是省会/直辖市）
            has_population = 'population' in loc
            is_capital = loc.get('admin1_id') == loc.get('admin2_id')  # 直辖市
            name_exact_match = loc['name'] == city or loc['name'].lower() == city.lower()
            
            # 计算优先级分数
            score = 0
            if has_population:
                score += loc.get('population', 0)
            if is_capital:
                score += 10000000  # 首都/直辖市优先
            if name_exact_match:
                score += 5000000  # 名称完全匹配优先
            
            results_with_population.append((score, loc))
        
        # 按分数降序排序，选择最高的
        results_with_population.sort(key=lambda x: x[0], reverse=True)
        location = results_with_population[0][1]
        latitude = location['latitude']
        longitude = location['longitude']
        city_name = location['name']
        country = location.get('country', '')
        
        # 查询天气数据
        weather_params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum',
            'timezone': 'auto',
            'forecast_days': 3
        }
        
        query_string = urlencode(weather_params)
        
        conn = HTTPSConnection("api.open-meteo.com", timeout=10)
        conn.request("GET", f"/v1/forecast?{query_string}")
        response = conn.getresponse()
        weather_data = response.read().decode('utf-8')
        conn.close()
        
        if response.status != 200:
            return {"error": f"获取天气数据失败，状态码: {response.status}"}
        
        weather_result = json.loads(weather_data)
        
        # 解析当前天气
        current = weather_result.get('current', {})
        daily = weather_result.get('daily', {})
        
        # 天气代码映射
        weather_codes = {
            0: "晴朗",
            1: "主要晴朗",
            2: "多云",
            3: "阴天",
            45: "雾",
            48: "雾凇",
            51: "毛毛雨",
            53: "中度毛毛雨",
            55: "大毛毛雨",
            61: "小雨",
            63: "中雨",
            65: "大雨",
            71: "小雪",
            73: "中雪",
            75: "大雪",
            95: "雷雨",
            96: "雷雨伴冰雹",
            99: "强雷雨伴冰雹"
        }
        
        current_weather_code = current.get('weather_code', -1)
        weather_description = weather_codes.get(current_weather_code, "未知")
        
        # 构建结果 - 直接返回天气预报的原始数据
        result = {
            "success": True,
            "message": f"{city_name}的天气预报",
            "location": {
                "city": city_name,
                "country": country,
                "latitude": latitude,
                "longitude": longitude
            },
            "current_weather": {
                "temperature": f"{current.get('temperature_2m', 'N/A')}°C",
                "feels_like": f"{current.get('apparent_temperature', 'N/A')}°C",
                "humidity": f"{current.get('relative_humidity_2m', 'N/A')}%",
                "weather": weather_description,
                "is_day": "白天" if current.get('is_day', 1) == 1 else "夜晚",
                "wind_speed": f"{current.get('wind_speed_10m', 'N/A')} km/h",
                "precipitation": f"{current.get('precipitation', 'N/A')} mm"
            },
            "forecast": []
        }
        
        # 添加未来几天的预报
        if daily:
            for i in range(min(3, len(daily.get('time', [])))):
                day_code = daily['weather_code'][i] if i < len(daily['weather_code']) else -1
                day_weather = weather_codes.get(day_code, "未知")
                
                forecast_day = {
                    "date": daily['time'][i],
                    "weather": day_weather,
                    "max_temp": f"{daily['temperature_2m_max'][i]}°C" if i < len(daily['temperature_2m_max']) else "N/A",
                    "min_temp": f"{daily['temperature_2m_min'][i]}°C" if i < len(daily['temperature_2m_min']) else "N/A",
                    "precipitation": f"{daily['precipitation_sum'][i]} mm" if i < len(daily['precipitation_sum']) else "N/A",
                    "sunrise": daily['sunrise'][i] if i < len(daily['sunrise']) else "N/A",
                    "sunset": daily['sunset'][i] if i < len(daily['sunset']) else "N/A"
                }
                result["forecast"].append(forecast_day)
        
        return result
        
    except Exception as e:
        return {"error": f"查询天气时出错: {str(e)}"}


# 工具定义（用于发送给 LLM）
WEATHER_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气和未来几天天气预报",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称，例如：北京、上海、广州等"
                }
            },
            "required": ["city"]
        }
    }
}
