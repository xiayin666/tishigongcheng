"""
测试改进后的天气查询功能
支持全球任意城市查询
"""
from weather_tool import get_weather
import json


def test_city(city_name):
    """测试单个城市的天气查询"""
    print(f"\n{'='*50}")
    print(f"查询城市: {city_name}")
    print('='*50)
    
    result = get_weather(city_name)
    
    if result.get('error'):
        print(f"❌ 错误: {result['error']}")
        return
    
    if not result.get('success'):
        print(f"❌ 查询失败")
        return
    
    # 显示位置信息
    location = result.get('location', {})
    print(f"📍 位置: {location.get('city')}, {location.get('country')}")
    print(f"   经纬度: {location.get('latitude')}, {location.get('longitude')}")
    
    # 显示当前天气
    current = result.get('current_weather', {})
    print(f"\n🌤️  当前天气:")
    print(f"   温度: {current.get('temperature')}")
    print(f"   体感温度: {current.get('feels_like')}")
    print(f"   天气状况: {current.get('weather')}")
    print(f"   湿度: {current.get('humidity')}")
    print(f"   风速: {current.get('wind_speed')}")
    print(f"   降水: {current.get('precipitation')}")
    print(f"   时间: {current.get('is_day')}")
    
    # 显示预报
    forecast = result.get('forecast', [])
    if forecast:
        print(f"\n📅 未来天气预报:")
        for day in forecast:
            print(f"   {day.get('date')}:")
            print(f"     天气: {day.get('weather')}")
            print(f"     温度: {day.get('min_temp')} ~ {day.get('max_temp')}")
            print(f"     降水: {day.get('precipitation')}")
            print(f"     日出: {day.get('sunrise')}")
            print(f"     日落: {day.get('sunset')}")


if __name__ == '__main__':
    print("🌍 天气查询功能测试 - 支持全球任意城市")
    
    # 测试不同类型的城市
    test_cities = [
        # 中国城市
        '北京',
        '上海',
        '深圳',
        '成都',
        
        # 国际城市（中文）
        '纽约',
        '伦敦',
        '东京',
        
        # 国际城市（英文）
        'Paris',
        'Sydney',
        'Singapore',
        
        # 较小的城市
        '桂林',
        '大理',
    ]
    
    for city in test_cities:
        test_city(city)
    
    print(f"\n{'='*50}")
    print("✅ 测试完成！")
    print("天气查询功能已升级，支持全球任意城市查询")
    print("可以使用中文或英文城市名称")
    print('='*50)