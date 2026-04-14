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
    print("测试天气查询功能")
    print("=" * 60)
    
    # 测试北京天气
    print("\n1. 查询北京天气...")
    result = get_weather("北京")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试上海天气
    print("\n2. 查询上海天气...")
    result = get_weather("上海")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试广州天气
    print("\n3. 查询广州天气...")
    result = get_weather("广州")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    test_weather()
