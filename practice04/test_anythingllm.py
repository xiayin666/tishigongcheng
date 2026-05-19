"""
测试 AnythingLLM 查询工具
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
def load_env_file(filepath='.env'):
    """读取.env文件并解析键值对"""
    if not os.path.exists(filepath):
        print(f"警告: 文件 {filepath} 不存在")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    return True

from practice04.anythingllm_tool import anythingllm_query


def test_anythingllm_query():
    """测试 anythingllm_query 函数"""
    # 加载环境变量
    print("=" * 60)
    print("测试 AnythingLLM 查询工具")
    print("=" * 60)
    
    if not load_env_file():
        print("无法加载环境变量，测试终止")
        return
    
    api_key = os.getenv('ANYTHINGLLM_KEY')
    if api_key:
        print(f"✓ 成功加载 ANYTHINGLLM_KEY: {api_key[:10]}...")
    else:
        print("❌ 未找到 ANYTHINGLLM_KEY")
        return
    
    # 测试1: 基本查询
    print("\n测试1: 发送基本查询")
    print("-" * 60)
    # 注意：请根据实际 AnythingLLM 中的工作空间名称修改 workspace_slug 参数
    result = anythingllm_query("你好，请介绍一下自己", workspace_slug="042211f4-0b84-4045-adf0-a0b9df4df708")
    print(f"结果: {result}")
    
    if 'error' in result:
        print(f"❌ 测试失败: {result['error']}")
    else:
        print(f"✓ 测试成功")
        response = result.get('response')
        if response:
            print(f"回复: {response}")
        else:
            print(f"原始响应: {result.get('raw_response')}")
    
    # 测试2: 技术问题查询
    print("\n\n测试2: 技术问题查询")
    print("-" * 60)
    result = anythingllm_query("Python 中的装饰器是什么？", workspace_slug="042211f4-0b84-4045-adf0-a0b9df4df708")
    print(f"结果: {result}")
    
    if 'error' in result:
        print(f"❌ 测试失败: {result['error']}")
    else:
        print(f"✓ 测试成功")
        response = result.get('response')
        if response:
            print(f"回复: {str(response)[:200]}...")
        else:
            print(f"原始响应: {result.get('raw_response')}")


if __name__ == '__main__':
    test_anythingllm_query()
