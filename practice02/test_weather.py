"""
测试天气查询功能
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.weather_tool import get_weather


def test_weather():
    """测试天气查询"""
    print("=" * 60)
    print("测试天气查询功能 - 支持全球任意城市")
    print("=" * 60)
    
    # 测试中国城市
    print("\n1. 查询北京天气...")
    result = get_weather("北京")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试国际城市（中文）
    print("\n2. 查询纽约天气（中文名称）...")
    result = get_weather("纽约")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试国际城市（英文）
    print("\n3. 查询伦敦天气（英文名称）...")
    result = get_weather("London")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试较小城市
    print("\n4. 查询桂林天气...")
    result = get_weather("桂林")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    test_weather()
