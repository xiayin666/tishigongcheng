"""
测试链式调用上下文管理器和执行器
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_context import ChainedCallContext
from practice05.chained_call_executor import execute_chained_tool_call, load_env_vars


def test_context_basic():
    """测试上下文管理器的基本功能"""
    print("=" * 60)
    print("测试1: ChainedCallContext 基本功能")
    print("=" * 60)
    
    # 创建上下文
    context = ChainedCallContext(max_iterations=5)
    print(f"\n初始状态:\n{context}")
    
    # 测试变量存储
    context.set_variable("test_var", "hello")
    context.set_variable("count", 42)
    print(f"\n设置变量后:")
    print(f"  test_var = {context.get_variable('test_var')}")
    print(f"  count = {context.get_variable('count')}")
    print(f"  所有变量: {context.get_all_variables()}")
    
    # 测试调用记录
    context.add_call_record({
        "tool_name": "test_tool",
        "arguments": {"param": "value"},
        "result": {"success": True},
        "success": True
    })
    
    print(f"\n添加调用记录后:\n{context}")
    print(f"调用历史: {context.call_history}")
    
    # 测试迭代
    print(f"\n可以继续: {context.can_continue()}")
    context.next_iteration()
    print(f"下一次迭代后: current_iteration = {context.current_iteration}")
    
    # 测试完成
    context.complete("任务完成！")
    print(f"\n标记完成后:")
    print(f"  is_completed = {context.is_completed}")
    print(f"  final_result = {context.final_result}")
    print(f"  可以继续: {context.can_continue()}")
    
    # 测试序列化
    data = context.to_dict()
    print(f"\n序列化后的数据键: {list(data.keys())}")
    
    # 测试反序列化
    restored_context = ChainedCallContext.from_dict(data)
    print(f"\n恢复后的上下文:\n{restored_context}")
    
    print("\n✓ 基本功能测试通过\n")


def test_context_max_iterations():
    """测试最大迭代次数限制"""
    print("=" * 60)
    print("测试2: 最大迭代次数限制")
    print("=" * 60)
    
    context = ChainedCallContext(max_iterations=3)
    
    for i in range(5):
        print(f"\n迭代 {i+1}:")
        print(f"  current_iteration = {context.current_iteration}")
        print(f"  can_continue = {context.can_continue()}")
        
        if not context.can_continue():
            print(f"  错误信息: {context.error}")
            break
        
        context.next_iteration()
    
    print("\n✓ 最大迭代次数测试通过\n")


def test_context_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试3: 错误处理")
    print("=" * 60)
    
    context = ChainedCallContext(max_iterations=10)
    
    print(f"\n初始状态 - can_continue: {context.can_continue()}")
    
    # 模拟失败
    context.fail("发生了一个错误")
    print(f"标记失败后 - can_continue: {context.can_continue()}")
    print(f"错误信息: {context.error}")
    print(f"是否完成: {context.is_completed}")
    
    print("\n✓ 错误处理测试通过\n")


def test_chained_execution_weather():
    """测试链式执行 - 天气查询"""
    print("=" * 60)
    print("测试4: 链式执行 - 天气查询")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        
        # 设置环境变量
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "帮我查询北京的天气"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=5, 
            verbose=True
        )
        
        print(f"\n{'=' * 60}")
        print(f"执行结果:")
        print(f"{'=' * 60}")
        print(f"成功: {result['success']}")
        if result['success']:
            print(f"结果: {result['result'][:300]}")
        else:
            print(f"错误: {result['error']}")
        
        if result['context']:
            print(f"\n上下文摘要:")
            print(result['context'])
        
        print("\n✓ 天气查询测试完成\n")
        
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件，跳过此测试\n")
    except Exception as e:
        print(f"\n✗ 测试出错: {str(e)}\n")
        import traceback
        traceback.print_exc()


def test_chained_execution_notice():
    """测试链式执行 - 通知撰写"""
    print("=" * 60)
    print("测试5: 链式执行 - 通知撰写")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        
        # 设置环境变量
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "我是行政部的，请帮我写一个五一劳动节放假通知"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=5, 
            verbose=True
        )
        
        print(f"\n{'=' * 60}")
        print(f"执行结果:")
        print(f"{'=' * 60}")
        print(f"成功: {result['success']}")
        if result['success']:
            print(f"\n结果:\n{result['result']}")
        else:
            print(f"错误: {result['error']}")
        
        if result['context']:
            print(f"\n上下文摘要:")
            print(result['context'])
        
        print("\n✓ 通知撰写测试完成\n")
        
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件，跳过此测试\n")
    except Exception as e:
        print(f"\n✗ 测试出错: {str(e)}\n")
        import traceback
        traceback.print_exc()


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("链式调用功能测试")
    print("=" * 60 + "\n")
    
    # 测试上下文管理器
    test_context_basic()
    test_context_max_iterations()
    test_context_error_handling()
    
    # 测试链式执行（需要 .env 文件）
    test_chained_execution_weather()
    test_chained_execution_notice()
    
    print("=" * 60)
    print("所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
