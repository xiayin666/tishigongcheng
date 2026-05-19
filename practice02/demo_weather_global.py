"""
天气查询功能演示 - 展示全球任意城市查询能力
"""
from weather_tool import get_weather
import json


def pretty_print_weather(city_name, result):
    """美观地打印天气信息"""
    print("\n" + "="*60)
    print(f"🌍 {city_name} 的天气")
    print("="*60)
    
    if result.get('error'):
        print(f"❌ 错误: {result['error']}")
        return
    
    if not result.get('success'):
        print("❌ 查询失败")
        return
    
    # 位置信息
    loc = result.get('location', {})
    print(f"\n📍 位置信息:")
    print(f"   城市: {loc.get('city')}")
    print(f"   国家: {loc.get('country')}")
    print(f"   坐标: ({loc.get('latitude')}, {loc.get('longitude')})")
    
    # 当前天气
    current = result.get('current_weather', {})
    print(f"\n🌤️  当前天气:")
    print(f"   🌡️  温度: {current.get('temperature')}")
    print(f"   💭 体感: {current.get('feels_like')}")
    print(f"   ☁️  天气: {current.get('weather')}")
    print(f"   💧 湿度: {current.get('humidity')}")
    print(f"   💨 风速: {current.get('wind_speed')}")
    print(f"   🌧️  降水: {current.get('precipitation')}")
    print(f"   ⏰ 时间: {current.get('is_day')}")
    
    # 天气预报
    forecast = result.get('forecast', [])
    if forecast:
        print(f"\n📅 未来3天预报:")
        for i, day in enumerate(forecast, 1):
            print(f"\n   第{i}天 ({day.get('date')}):")
            print(f"     ☁️  天气: {day.get('weather')}")
            print(f"     🌡️  温度: {day.get('min_temp')} ~ {day.get('max_temp')}")
            print(f"     🌧️  降水: {day.get('precipitation')}")
            print(f"     🌅 日出: {day.get('sunrise')}")
            print(f"     🌇 日落: {day.get('sunset')}")


def demo():
    """演示天气查询功能"""
    print("\n" + "="*60)
    print("天气查询功能演示 - 支持全球任意城市")
    print("="*60)
    
    # 演示场景1: 中国主要城市
    print("\n\n【场景1】中国主要城市")
    print("-" * 60)
    cities_china = ['北京', '上海', '深圳', '成都']
    for city in cities_china:
        result = get_weather(city)
        pretty_print_weather(city, result)
    
    # 演示场景2: 国际城市（中文名称）
    print("\n\n【场景2】国际城市 - 使用中文名称")
    print("-" * 60)
    cities_intl_cn = ['纽约', '伦敦', '东京', '巴黎']
    for city in cities_intl_cn:
        result = get_weather(city)
        pretty_print_weather(city, result)
    
    # 演示场景3: 国际城市（英文名称）
    print("\n\n【场景3】国际城市 - 使用英文名称")
    print("-" * 60)
    cities_intl_en = ['Sydney', 'Singapore', 'Los Angeles', 'Dubai']
    for city in cities_intl_en:
        result = get_weather(city)
        pretty_print_weather(city, result)
    
    # 演示场景4: 中小城市
    print("\n\n【场景4】中小城市查询")
    print("-" * 60)
    cities_small = ['桂林', '大理', '丽江', '三亚']
    for city in cities_small:
        result = get_weather(city)
        pretty_print_weather(city, result)
    
    # 总结
    print("\n\n" + "="*60)
    print("演示完成！")
    print("="*60)
    print("\n✅ 功能特点:")
    print("   • 支持全球任意城市查询")
    print("   • 支持中文和英文城市名称")
    print("   • 智能匹配算法，自动选择最可能的城市")
    print("   • 提供详细的当前天气和未来预报")
    print("   • 无需API密钥，完全免费")
    print("\n💡 提示:")
    print("   • 可以查询世界上任何有记录的城市")
    print("   • 同名城市会智能选择最可能的那个")
    print("   • 对于歧义城市，可以加上国家名明确指定")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    demo()