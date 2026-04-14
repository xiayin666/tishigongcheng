"""
测试完整的聊天流程，包括天气查询
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.chat_client import chat_with_tools, load_env_file


def test_weather_chat():
    """测试天气查询对话"""
    try:
        env_vars = load_env_file('.env')
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    print("=" * 60)
    print("测试1: 查询北京天气")
    print("=" * 60)
    result = chat_with_tools(env_vars, "北京今天的天气怎么样？")
    
    print("\n" + "=" * 60)
    print("测试2: 查询上海天气")
    print("=" * 60)
    result = chat_with_tools(env_vars, "上海明天会下雨吗？")


if __name__ == '__main__':
    test_weather_chat()
