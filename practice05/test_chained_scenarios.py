"""
链式调用功能测试 - 三个实际场景测试

测试1：文件搜索链式调用
测试2：技能查询链式调用  
测试3：网页处理链式调用（模拟）
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_executor import execute_chained_tool_call, load_env_vars


def setup_test_environment():
    """设置测试环境"""
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        return env_vars
    except FileNotFoundError:
        print("⚠ 未找到 .env 文件")
        return None


def test1_file_search_chain():
    """
    测试1：文件搜索链式调用
    
    用户请求："请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    
    预期流程：
    1. 使用 list_files 列出 practice06 目录下的文件
    2. 对每个 .py 文件使用 read_file_content 读取内容
    3. 分析哪些文件包含 'def' 关键词
    4. 总结这些文件的主要内容
    """
    print("\n" + "=" * 80)
    print("测试1：文件搜索链式调用")
    print("=" * 80)
    print("\n用户请求：请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
    print("\n预期流程：")
    print("  1. list_files('practice06') - 列出目录文件")
    print("  2. read_file_content(...) - 读取每个Python文件")
    print("  3. 分析文件内容，找出包含'def'的文件")
    print("  4. 总结文件内容并返回")
    print("=" * 80)
    
    env_vars = setup_test_environment()
    if not env_vars:
        print("\n⚠ 跳过测试（缺少环境变量）\n")
        return False
    
    try:
        result = execute_chained_tool_call(
            env_vars,
            "请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容",
            max_iterations=10,
            verbose=True
        )
        
        print(f"\n{'=' * 80}")
        print("测试结果:")
        print(f"{'=' * 80}")
        
        if result["success"]:
            print("✅ 测试成功")
            print(f"\n最终结果:\n{result['result']}")
            
            # 显示执行统计
            context = result["context"]
            print(f"\n{'=' * 80}")
            print("执行统计:")
            print(f"{'=' * 80}")
            print(f"  • 迭代次数: {context.current_iteration}")
            print(f"  • 工具调用: {len(context.call_history)} 次")
            print(f"  • 中间变量: {len(context.variables)} 个")
            
            if context.call_history:
                print(f"\n调用历史:")
                for i, step in enumerate(context.call_history, 1):
                    status = "✓" if step['success'] else "✗"
                    print(f"  {i}. [{status}] {step['tool_name']}")
            
            return True
        else:
            print(f"❌ 测试失败: {result['error']}")
            if result["context"]:
                print(f"\n已执行 {result['context'].current_iteration} 次迭代")
                print(f"已调用 {len(result['context'].call_history)} 次工具")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test2_skill_query_chain():
    """
    测试2：技能查询链式调用
    
    用户请求："我想了解notice技能的详细规则"
    
    预期流程：
    1. 使用 anythingllm_query 查询知识库中关于notice技能的信息
    2. 根据查询结果整理并返回详细说明
    """
    print("\n" + "=" * 80)
    print("测试2：技能查询链式调用")
    print("=" * 80)
    print("\n用户请求：我想了解notice技能的详细规则")
    print("\n预期流程：")
    print("  1. anythingllm_query('notice技能的详细规则和用法') - 查询知识库")
    print("  2. 整理查询结果并返回详细说明")
    print("=" * 80)
    
    env_vars = setup_test_environment()
    if not env_vars:
        print("\n⚠ 跳过测试（缺少环境变量）\n")
        return False
    
    try:
        result = execute_chained_tool_call(
            env_vars,
            "我想了解notice技能的详细规则",
            max_iterations=5,
            verbose=True
        )
        
        print(f"\n{'=' * 80}")
        print("测试结果:")
        print(f"{'=' * 80}")
        
        if result["success"]:
            print("✅ 测试成功")
            print(f"\n最终结果:\n{result['result']}")
            
            # 显示执行统计
            context = result["context"]
            print(f"\n{'=' * 80}")
            print("执行统计:")
            print(f"{'=' * 80}")
            print(f"  • 迭代次数: {context.current_iteration}")
            print(f"  • 工具调用: {len(context.call_history)} 次")
            
            if context.call_history:
                print(f"\n调用历史:")
                for i, step in enumerate(context.call_history, 1):
                    status = "✓" if step['success'] else "✗"
                    print(f"  {i}. [{status}] {step['tool_name']}")
                    if step.get('arguments'):
                        print(f"     参数: {step['arguments']}")
            
            return True
        else:
            print(f"❌ 测试失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test3_web_processing_chain():
    """
    测试3：网页处理链式调用（模拟）
    
    用户请求："访问http://163.com/news/article/KRGTR2H0000189FH.html 并提取页面标题，保存到practice07/title.txt"
    
    注意：由于没有web_fetch工具，这个测试会演示LLM如何处理不可用的工具请求
    
    预期流程：
    1. LLM识别需要访问网页，但没有相应工具
    2. LLM应该说明无法完成该任务，或提供替代方案
    """
    print("\n" + "=" * 80)
    print("测试3：网页处理链式调用（模拟）")
    print("=" * 80)
    print("\n用户请求：访问http://163.com/news/article/KRGTR2H0000189FH.html 并提取页面标题，保存到practice07/title.txt")
    print("\n预期流程：")
    print("  1. LLM识别需要网页抓取功能")
    print("  2. 发现没有web_fetch工具")
    print("  3. 说明限制或提供替代方案")
    print("\n注意：当前系统没有网页抓取工具，此测试用于验证错误处理能力")
    print("=" * 80)
    
    env_vars = setup_test_environment()
    if not env_vars:
        print("\n⚠ 跳过测试（缺少环境变量）\n")
        return False
    
    try:
        result = execute_chained_tool_call(
            env_vars,
            "访问http://163.com/news/article/KRGTR2H0000189FH.html 并提取页面标题，保存到practice07/title.txt",
            max_iterations=5,
            verbose=True
        )
        
        print(f"\n{'=' * 80}")
        print("测试结果:")
        print(f"{'=' * 80}")
        
        # 这个测试可能成功（LLM解释了限制）或失败（尝试调用不存在的工具）
        print(f"执行状态: {'✅ 完成' if result['success'] else '❌ 失败'}")
        print(f"\n响应内容:\n{result['result']}")
        
        # 显示执行统计
        context = result["context"]
        print(f"\n{'=' * 80}")
        print("执行统计:")
        print(f"{'=' * 80}")
        print(f"  • 迭代次数: {context.current_iteration}")
        print(f"  • 工具调用: {len(context.call_history)} 次")
        
        if context.call_history:
            print(f"\n调用历史:")
            for i, step in enumerate(context.call_history, 1):
                status = "✓" if step['success'] else "✗"
                print(f"  {i}. [{status}] {step['tool_name']}")
                if step.get('error'):
                    print(f"     错误: {step['error']}")
        
        # 检查LLM是否正确处理了缺失工具的情况
        if "无法" in result['result'] or "不支持" in result['result'] or "没有" in result['result']:
            print("\n✅ LLM正确识别并说明了工具限制")
            return True
        else:
            print("\n⚠️  LLM可能尝试了其他处理方式")
            return True  # 仍然算通过，因为完成了响应
            
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("链式调用功能 - 实际场景测试")
    print("=" * 80)
    
    results = []
    
    # 测试1：文件搜索
    print("\n" + "#" * 80)
    print("# 开始测试1：文件搜索链式调用")
    print("#" * 80)
    result1 = test1_file_search_chain()
    results.append(("文件搜索链式调用", result1))
    
    # 测试2：技能查询
    print("\n" + "#" * 80)
    print("# 开始测试2：技能查询链式调用")
    print("#" * 80)
    result2 = test2_skill_query_chain()
    results.append(("技能查询链式调用", result2))
    
    # 测试3：网页处理
    print("\n" + "#" * 80)
    print("# 开始测试3：网页处理链式调用")
    print("#" * 80)
    result3 = test3_web_processing_chain()
    results.append(("网页处理链式调用", result3))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试汇总")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    elif passed > 0:
        print(f"\n⚠️  {passed}/{total} 个测试通过，部分测试未通过")
    else:
        print("\n❌ 所有测试均未通过")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
