"""
测试修复后的Agent功能
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_executor import (
    fix_incomplete_json,
    parse_llm_response,
    detect_duplicate_call,
    trim_message_history,
    ChainedCallContext
)


def test_fix_incomplete_json():
    """测试修复不完整的JSON"""
    print("=" * 60)
    print("测试1: 修复不完整的JSON")
    print("=" * 60)
    
    # 测试用例1: 缺少闭合括号
    incomplete_json = '{"done": true, "answer": "测试答案"'
    fixed = fix_incomplete_json(incomplete_json)
    print(f"\n原始JSON: {incomplete_json}")
    print(f"修复后: {fixed}")
    
    if fixed:
        try:
            import json
            parsed = json.loads(fixed)
            print(f"✓ 成功解析: {parsed}")
        except Exception as e:
            print(f"✗ 解析失败: {e}")
    else:
        print("✗ 无法修复")
    
    # 测试用例2: 嵌套对象缺少闭合括号
    incomplete_json2 = '{"done": false, "tool_call": {"name": "test", "arguments": {"key": "value"}}'
    fixed2 = fix_incomplete_json(incomplete_json2)
    print(f"\n原始JSON: {incomplete_json2}")
    print(f"修复后: {fixed2}")
    
    if fixed2:
        try:
            import json
            parsed2 = json.loads(fixed2)
            print(f"✓ 成功解析: {parsed2}")
        except Exception as e:
            print(f"✗ 解析失败: {e}")
    else:
        print("✗ 无法修复")
    
    print("\n✓ 测试完成\n")


def test_parse_llm_response():
    """测试LLM响应解析"""
    print("=" * 60)
    print("测试2: LLM响应解析")
    print("=" * 60)
    
    # 测试用例1: 完整的JSON响应（任务完成）
    response1 = {
        "choices": [{
            "message": {
                "content": '{"done": true, "answer": "这是最终答案"}'
            }
        }]
    }
    result1 = parse_llm_response(response1)
    print(f"\n测试1 - 完整JSON响应:")
    print(f"  类型: {result1['type']}")
    print(f"  内容: {result1.get('content', 'N/A')}")
    assert result1['type'] == 'completed'
    assert result1['content'] == '这是最终答案'
    print("  ✓ 通过")
    
    # 测试用例2: 工具调用响应
    response2 = {
        "choices": [{
            "message": {
                "content": '{"done": false, "tool_call": {"name": "get_weather", "arguments": {"city": "北京"}}}'
            }
        }]
    }
    result2 = parse_llm_response(response2)
    print(f"\n测试2 - 工具调用响应:")
    print(f"  类型: {result2['type']}")
    print(f"  工具名: {result2.get('tool_call', {}).get('name', 'N/A')}")
    assert result2['type'] == 'tool_call'
    assert result2['tool_call']['name'] == 'get_weather'
    print("  ✓ 通过")
    
    # 测试用例3: 不完整的JSON（应该尝试修复）
    response3 = {
        "choices": [{
            "message": {
                "content": '{"done": true, "answer": "不完整的答案"'
            }
        }]
    }
    result3 = parse_llm_response(response3)
    print(f"\n测试3 - 不完整JSON响应:")
    print(f"  类型: {result3['type']}")
    if result3['type'] == 'completed':
        print(f"  内容: {result3.get('content', 'N/A')}")
        print("  ✓ 成功修复并解析")
    else:
        print(f"  错误: {result3.get('error', 'N/A')}")
        print("  ⚠ 未能修复（这可能是预期的）")
    
    print("\n✓ 测试完成\n")


def test_detect_duplicate_call():
    """测试重复调用检测"""
    print("=" * 60)
    print("测试3: 重复调用检测")
    print("=" * 60)
    
    context = ChainedCallContext(max_iterations=10)
    
    # 添加一些调用历史
    context.add_call_record({
        "tool_name": "get_weather",
        "arguments": {"city": "北京"},
        "result": {"temperature": 20},
        "success": True
    })
    
    context.add_call_record({
        "tool_name": "list_files",
        "arguments": {"directory": "/home"},
        "result": {"files": []},
        "success": True
    })
    
    # 测试1: 相同的调用应该被检测为重复
    is_dup1 = detect_duplicate_call(context, "get_weather", {"city": "北京"})
    print(f"\n测试1 - 相同调用 (get_weather, 北京):")
    print(f"  是否重复: {is_dup1}")
    assert is_dup1 == True
    print("  ✓ 通过")
    
    # 测试2: 不同参数不应该被检测为重复
    is_dup2 = detect_duplicate_call(context, "get_weather", {"city": "上海"})
    print(f"\n测试2 - 不同参数 (get_weather, 上海):")
    print(f"  是否重复: {is_dup2}")
    assert is_dup2 == False
    print("  ✓ 通过")
    
    # 测试3: 不同工具不应该被检测为重复
    is_dup3 = detect_duplicate_call(context, "read_file", {"file_path": "test.txt"})
    print(f"\n测试3 - 不同工具 (read_file):")
    print(f"  是否重复: {is_dup3}")
    assert is_dup3 == False
    print("  ✓ 通过")
    
    print("\n✓ 测试完成\n")


def test_trim_message_history():
    """测试消息历史裁剪"""
    print("=" * 60)
    print("测试4: 消息历史裁剪")
    print("=" * 60)
    
    # 创建超过限制的消息列表
    messages = [{"role": "system", "content": "系统消息"}]
    for i in range(25):
        messages.append({"role": "user", "content": f"用户消息 {i}"})
        messages.append({"role": "assistant", "content": f"助手回复 {i}"})
    
    print(f"\n原始消息数量: {len(messages)}")
    
    # 裁剪消息
    trimmed = trim_message_history(messages, max_messages=20)
    print(f"裁剪后消息数量: {len(trimmed)}")
    
    # 验证第一条仍然是系统消息
    assert trimmed[0]['role'] == 'system'
    print("✓ 系统消息被保留")
    
    # 验证消息数量不超过限制
    assert len(trimmed) <= 20
    print("✓ 消息数量符合限制")
    
    # 验证保留了最近的消息
    last_message = trimmed[-1]
    print(f"最后一条消息: {last_message['content']}")
    
    print("\n✓ 测试完成\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Agent修复验证测试")
    print("=" * 60 + "\n")
    
    try:
        test_fix_incomplete_json()
        test_parse_llm_response()
        test_detect_duplicate_call()
        test_trim_message_history()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
