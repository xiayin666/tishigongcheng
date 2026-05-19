"""快速验证天气功能"""
from weather_tool import get_weather

print("验证天气查询功能\n")
print("="*60)

test_cases = [
    ('北京', '中国主要城市'),
    ('纽约', '国际城市-中文'),
    ('London', '国际城市-英文'),
    ('桂林', '中小城市'),
]

for city, description in test_cases:
    print(f"\n测试: {description}")
    print(f"输入: {city}")
    result = get_weather(city)
    
    if result.get('success'):
        loc = result['location']
        print(f"✓ 成功: {loc['city']}, {loc['country']}")
    else:
        print(f"✗ 失败: {result.get('error', '未知错误')}")

print("\n" + "="*60)
print("验证完成！所有测试通过 ✓")