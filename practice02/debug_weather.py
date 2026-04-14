"""
调试天气API，查看原始返回数据
"""
import json
from http.client import HTTPSConnection
from urllib.parse import quote


def debug_weather_api(city="北京"):
    """调试天气API"""
    print("=" * 60)
    print(f"调试城市: {city}")
    print("=" * 60)
    
    # 第一步：地理编码
    encoded_city = quote(city)
    print(f"\n1. 地理编码请求:")
    print(f"   URL: https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=zh&format=json")
    
    conn = HTTPSConnection("geocoding-api.open-meteo.com", timeout=10)
    conn.request("GET", f"/v1/search?name={encoded_city}&count=5&language=zh&format=json")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    conn.close()
    
    print(f"   状态码: {response.status}")
    print(f"\n   原始响应:")
    geocode_result = json.loads(data)
    print(json.dumps(geocode_result, ensure_ascii=False, indent=2))
    
    if geocode_result.get('results'):
        print(f"\n   找到 {len(geocode_result['results'])} 个结果:")
        for i, loc in enumerate(geocode_result['results'], 1):
            print(f"   {i}. {loc['name']}, {loc.get('country', '')} - 纬度:{loc['latitude']}, 经度:{loc['longitude']}")
        
        # 使用第一个结果查询天气
        location = geocode_result['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        
        print(f"\n2. 天气查询 (使用第一个结果):")
        print(f"   纬度: {latitude}, 经度: {longitude}")
        
        from urllib.parse import urlencode
        weather_params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
            'timezone': 'auto',
            'forecast_days': 3
        }
        
        query_string = urlencode(weather_params)
        print(f"   URL: https://api.open-meteo.com/v1/forecast?{query_string}")
        
        conn = HTTPSConnection("api.open-meteo.com", timeout=10)
        conn.request("GET", f"/v1/forecast?{query_string}")
        response = conn.getresponse()
        weather_data = response.read().decode('utf-8')
        conn.close()
        
        print(f"   状态码: {response.status}")
        print(f"\n   天气原始响应:")
        weather_result = json.loads(weather_data)
        print(json.dumps(weather_result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    debug_weather_api("北京")
    print("\n\n")
    debug_weather_api("Beijing")
