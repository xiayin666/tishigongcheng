"""
测试 JSON 格式的 LLM 响应解析
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_executor import parse_llm_response


def test_parse_completed_task():
    """测试解析任务完成的JSON响应"""
    print("=" * 60)
    print("测试1: 解析任务完成的JSON响应")
    print("=" * 60)
    
    # 模拟LLM返回的完成响应
    response = {
        'choices': [{
            'message': {
                'content': '{"done": true, "answer": "北京今天天气晴朗，温度25°C，适合户外活动。"}'
            }
        }]
    }
    
    result = parse_llm_response(response)
    print(f"解析结果类型: {result['type']}")
    print(f"回答内容: {result['content']}")
    
    assert result['type'] == 'completed', "应该识别为完成状态"
    assert '北京' in result['content'], "应该包含正确的回答内容"
    print("✓ 测试通过\n")


def test_parse_tool_call_json():
    """测试解析工具调用的JSON响应"""
    print("=" * 60)
    print("测试2: 解析工具调用的JSON响应")
    print("=" * 60)
    
    # 模拟LLM返回的工具调用响应
    response = {
        'choices': [{
            'message': {
                'content': '{"done": false, "tool_call": {"name": "get_weather", "arguments": {"city": "Beijing"}}}'
            }
        }]
    }
    
    result = parse_llm_response(response)
    print(f"解析结果类型: {result['type']}")
    print(f"工具名称: {result['tool_call']['name']}")
    print(f"参数: {result['tool_call']['arguments']}")
    
    assert result['type'] == 'tool_call', "应该识别为工具调用"
    assert result['tool_call']['name'] == 'get_weather', "工具名称应该正确"
    assert result['tool_call']['arguments']['city'] == 'Beijing', "参数应该正确"
    print("✓ 测试通过\n")


def test_parse_with_code_block():
    """测试解析包含代码块的JSON响应"""
    print("=" * 60)
    print("测试3: 解析包含代码块的JSON响应")
    print("=" * 60)
    
    # 模拟LLM返回的带代码块的响应
    response = {
        'choices': [{
            'message': {
                'content': '''```json
{
  "done": false,
  "tool_call": {
    "name": "anythingllm_query",
    "arguments": {
      "message": "项目开发规范"
    }
  }
}
```'''
            }
        }]
    }
    
    result = parse_llm_response(response)
    print(f"解析结果类型: {result['type']}")
    print(f"工具名称: {result['tool_call']['name']}")
    print(f"参数: {result['tool_call']['arguments']}")
    
    assert result['type'] == 'tool_call', "应该识别为工具调用"
    assert result['tool_call']['name'] == 'anythingllm_query', "工具名称应该正确"
    assert result['tool_call']['arguments']['message'] == '项目开发规范', "参数应该正确"
    print("✓ 测试通过\n")


def test_parse_error_response():
    """测试解析错误响应"""
    print("=" * 60)
    print("测试4: 解析错误响应")
    print("=" * 60)
    
    response = {
        'error': 'API调用失败'
    }
    
    result = parse_llm_response(response)
    print(f"解析结果类型: {result['type']}")
    print(f"错误信息: {result['error']}")
    
    assert result['type'] == 'error', "应该识别为错误"
    assert result['error'] == 'API调用失败', "错误信息应该正确"
    print("✓ 测试通过\n")


def test_parse_plain_text_completion():
    """测试解析纯文本完成响应（向后兼容）"""
    print("=" * 60)
    print("测试5: 解析纯文本完成响应（向后兼容）")
    print("=" * 60)
    
    response = {
        'choices': [{
            'message': {
                'content': '这是一个普通的回复，没有使用JSON格式。'
            }
        }]
    }
    
    result = parse_llm_response(response)
    print(f"解析结果类型: {result['type']}")
    print(f"回答内容: {result['content']}")
    
    assert result['type'] == 'completed', "应该识别为完成状态"
    assert '普通' in result['content'], "应该包含原始内容"
    print("✓ 测试通过\n")


def test_build_analysis_prompt():
    """测试构建分析提示词"""
    print("=" * 60)
    print("测试6: 构建分析提示词")
    print("=" * 60)
    
    from practice05.chained_call_context import ChainedCallContext
    
    context = ChainedCallContext(max_iterations=10)
    context.set_variable("weather_data", {"city": "Beijing", "temp": 25})
    context.add_call_record({
        "tool_name": "get_weather",
        "arguments": {"city": "Beijing"},
        "result": {"temperature": "25°C"},
        "success": True
    })
    
    from practice05.chained_call_executor import build_analysis_prompt, ALL_TOOLS_DEFINITION
    
    prompt = build_analysis_prompt("查询北京天气并写报告", context, ALL_TOOLS_DEFINITION)
    
    print("生成的提示词预览（前500字符）:")
    print(prompt[:500])
    print("...\n")
    
    # 验证提示词包含关键部分
    assert "用户原始请求" in prompt, "应该包含用户请求部分"
    assert "查询北京天气并写报告" in prompt, "应该包含具体的用户请求"
    assert "已执行的工具调用历史" in prompt, "应该包含调用历史部分"
    assert "get_weather" in prompt, "应该显示已调用的工具"
    assert "决策规则说明" in prompt, "应该包含决策规则"
    assert "done" in prompt and "true" in prompt and "false" in prompt, "应该包含JSON格式说明"
    assert "tool_call" in prompt, "应该包含工具调用格式说明"
    assert "可用工具列表" in prompt, "应该包含可用工具列表"
    
    print("✓ 测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("JSON格式解析功能测试")
    print("=" * 60 + "\n")
    
    try:
        test_parse_completed_task()
        test_parse_tool_call_json()
        test_parse_with_code_block()
        test_parse_error_response()
        test_parse_plain_text_completion()
        test_build_analysis_prompt()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n新功能特性：")
        print("1. ✓ 支持JSON格式的LLM响应解析")
        print("2. ✓ 支持代码块中的JSON提取")
        print("3. ✓ 明确的任务完成/继续标识（done字段）")
        print("4. ✓ 结构化的工具调用格式")
        print("5. ✓ 向后兼容纯文本响应")
        print("6. ✓ 增强的提示词包含决策规则和格式说明")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
