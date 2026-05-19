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
        city: 城市名称，可以是中文或英文，支持全球任意城市
        
    Returns:
        包含天气信息的字典
    """
    try:
        from urllib.parse import quote
        
        # 常见城市名称映射（中文 -> 英文）- 作为备选方案
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
            '天津': 'Tianjin',
            '苏州': 'Suzhou',
            '青岛': 'Qingdao',
            '郑州': 'Zhengzhou',
            '长沙': 'Changsha',
            '沈阳': 'Shenyang',
            '济南': 'Jinan',
            '哈尔滨': 'Harbin',
            '大连': 'Dalian',
            '昆明': 'Kunming',
            '福州': 'Fuzhou',
            '厦门': 'Xiamen',
            '南昌': 'Nanchang',
            '合肥': 'Hefei',
            '石家庄': 'Shijiazhuang',
            '南宁': 'Nanning',
            '贵阳': 'Guiyang',
            '太原': 'Taiyuan',
            '长春': 'Changchun',
            '兰州': 'Lanzhou',
            '乌鲁木齐': 'Urumqi',
            '呼和浩特': 'Hohhot',
            '银川': 'Yinchuan',
            '西宁': 'Xining',
            '拉萨': 'Lhasa',
            '海口': 'Haikou',
            '三亚': 'Sanya',
            '宁波': 'Ningbo',
            '温州': 'Wenzhou',
            '东莞': 'Dongguan',
            '佛山': 'Foshan',
            '珠海': 'Zhuhai',
            '无锡': 'Wuxi',
            '常州': 'Changzhou',
            '徐州': 'Xuzhou',
            '烟台': 'Yantai',
            '潍坊': 'Weifang',
            '洛阳': 'Luoyang',
            '开封': 'Kaifeng',
            '桂林': 'Guilin',
            '柳州': 'Liuzhou',
            '遵义': 'Zunyi',
            # 国际城市
            '纽约': 'New York',
            '伦敦': 'London',
            '巴黎': 'Paris',
            '东京': 'Tokyo',
            '首尔': 'Seoul',
            '新加坡': 'Singapore',
            '悉尼': 'Sydney',
            '墨尔本': 'Melbourne',
            '洛杉矶': 'Los Angeles',
            '旧金山': 'San Francisco',
            '芝加哥': 'Chicago',
            '多伦多': 'Toronto',
            '温哥华': 'Vancouver',
            '柏林': 'Berlin',
            '罗马': 'Rome',
            '马德里': 'Madrid',
            '莫斯科': 'Moscow',
            '迪拜': 'Dubai',
            '曼谷': 'Bangkok',
            '吉隆坡': 'Kuala Lumpur',
            '雅加达': 'Jakarta',
            '孟买': 'Mumbai',
            '德里': 'Delhi',
            '开罗': 'Cairo',
            '约翰内斯堡': 'Johannesburg',
            '里约热内卢': 'Rio de Janeiro',
            '圣保罗': 'Sao Paulo',
            '墨西哥城': 'Mexico City',
        }
        
        # 如果是中文城市名，先尝试转换为英文
        search_city = city_name_map.get(city, city)
        encoded_city = quote(search_city)
        
        # 使用 Open-Meteo API（免费，无需API密钥）
        # 首先获取城市的经纬度 - 支持全球任意城市查询
        conn = HTTPSConnection("geocoding-api.open-meteo.com", timeout=15)
        conn.request("GET", f"/v1/search?name={encoded_city}&count=10&language=zh&format=json")
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
        if not results:
            # 如果第一次搜索没有结果，尝试用原始城市名再搜索一次
            if search_city != city:
                encoded_original = quote(city)
                conn = HTTPSConnection("geocoding-api.open-meteo.com", timeout=15)
                conn.request("GET", f"/v1/search?name={encoded_original}&count=10&language=zh&format=json")
                response = conn.getresponse()
                data = response.read().decode('utf-8')
                conn.close()
                
                if response.status == 200:
                    retry_result = json.loads(data)
                    if retry_result.get('results'):
                        results = retry_result['results']
        
        if not results:
            return {"error": f"未找到城市: {city}，请尝试使用其他城市名称"}
        
        # 按相关性和人口排序，选择最佳匹配
        results_with_population = []
        for loc in results:
            # 计算匹配分数
            score = 0
            
            # 人口权重（限制最大值避免过大影响）
            if 'population' in loc:
                population = loc.get('population', 0)
                # 对于大城市给予更高权重
                if population > 1000000:
                    score += min(population, 50000000) * 2  # 百万以上人口城市加倍
                else:
                    score += min(population, 10000000)
            
            # 行政级别权重（省会/直辖市/州府优先）
            admin_level = loc.get('admin1_id', '')
            if admin_level and loc.get('admin2_id') == admin_level:
                score += 5000000  # 直辖市/省会加分
            
            # 名称精确匹配权重
            loc_name = loc.get('name', '').lower()
            search_lower = search_city.lower()
            original_lower = city.lower()
            
            if loc_name == search_lower or loc_name == original_lower:
                score += 8000000  # 完全匹配高分
            elif search_lower in loc_name or original_lower in loc_name:
                score += 3000000  # 部分匹配中等分
            
            # 国家匹配权重（根据搜索词判断）
            country_code = loc.get('country_code', '').upper()
            country_name = loc.get('country', '').lower()
            
            # 如果搜索词包含国家信息，优先匹配
            if '美国' in city or 'usa' in search_lower or 'us' in search_lower:
                if country_code in ['US']:
                    score += 10000000  # 美国城市高优先级
            elif '英国' in city or 'uk' in search_lower or 'britain' in search_lower:
                if country_code in ['GB', 'UK']:
                    score += 10000000
            elif '中国' in city or 'cn' in search_lower or 'china' in search_lower:
                if country_code in ['CN', 'TW', 'HK', 'MO']:
                    score += 10000000
            else:
                # 默认情况下，对常见国家的城市给予适度加分
                if country_code in ['CN', 'TW', 'HK', 'MO']:
                    score += 1000000  # 中国地区加分
                elif country_code in ['US']:
                    score += 800000   # 美国地区加分
                elif country_code in ['GB', 'UK']:
                    score += 600000   # 英国地区加分
                elif country_code in ['JP']:
                    score += 500000   # 日本地区加分
                elif country_code in ['KR']:
                    score += 400000   # 韩国地区加分
            
            # 对于知名国际大都市额外加分
            major_cities = [
                'new york', 'london', 'paris', 'tokyo', 'beijing', 'shanghai',
                'los angeles', 'chicago', 'hong kong', 'singapore', 'sydney',
                'moscow', 'berlin', 'rome', 'madrid', 'dubai', 'bangkok'
            ]
            if loc_name in major_cities and population and population > 5000000:
                score += 3000000  # 国际大都市加分
            
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
        "description": "查询全球任意城市的当前天气和未来几天天气预报，支持中文和英文城市名称",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "要查询天气的城市名称，可以是中文或英文，例如：北京、上海、New York、London等"
                }
            },
            "required": ["city"]
        }
    }
}
