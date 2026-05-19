"""
链式调用使用示例

演示如何使用链式调用功能完成复杂任务
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_executor import execute_chained_tool_call, load_env_vars


def example_1_simple_weather():
    """示例1: 简单天气查询（单步）"""
    print("=" * 60)
    print("示例1: 简单天气查询")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "北京今天天气怎么样？"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=3,
            verbose=True
        )
        
        if result["success"]:
            print(f"\n✓ 成功获取天气信息")
        else:
            print(f"\n✗ 失败: {result['error']}")
            
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件\n")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}\n")


def example_2_multi_step_task():
    """示例2: 多步骤任务 - 查询多个城市天气并比较"""
    print("=" * 60)
    print("示例2: 多步骤任务 - 查询多个城市天气并比较")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "请帮我查询北京、上海、广州三个城市的天气，然后告诉我哪个城市最适合周末出游"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=8,
            verbose=True
        )
        
        if result["success"]:
            print(f"\n✓ 任务完成")
            print(f"\n最终建议:\n{result['result']}")
            
            # 查看执行过程
            context = result["context"]
            print(f"\n执行统计:")
            print(f"  - 迭代次数: {context.current_iteration}")
            print(f"  - 工具调用次数: {len(context.call_history)}")
            print(f"  - 存储的变量数: {len(context.variables)}")
        else:
            print(f"\n✗ 失败: {result['error']}")
            
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件\n")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}\n")


def example_3_notice_with_department():
    """示例3: 带部门信息的通知撰写"""
    print("=" * 60)
    print("示例3: 带部门信息的通知撰写")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "我是人力资源部的，需要写一个关于下周一公司团建活动的通知，时间是上午9点在公司门口集合"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=5,
            verbose=True
        )
        
        if result["success"]:
            print(f"\n✓ 通知生成成功")
            print(f"\n生成的通知:\n{result['result']}")
        else:
            print(f"\n✗ 失败: {result['error']}")
            
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件\n")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}\n")


def example_4_knowledgebase_query():
    """示例4: 知识库查询"""
    print("=" * 60)
    print("示例4: 知识库查询")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "请查询一下我们公司的项目开发规范文档"
        print(f"\n用户请求: {user_request}\n")
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=5,
            verbose=True
        )
        
        if result["success"]:
            print(f"\n✓ 查询成功")
            print(f"\n查询结果:\n{result['result']}")
        else:
            print(f"\n✗ 失败: {result['error']}")
            
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件\n")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}\n")


def example_5_complex_workflow():
    """示例5: 复杂工作流 - 结合多个工具"""
    print("=" * 60)
    print("示例5: 复杂工作流 - 结合多个工具")
    print("=" * 60)
    
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
        
        user_request = "先查询北京的天气，如果天气好就帮我写一个户外活动通知，如果天气不好就写一个室内活动通知。我是行政部的。"
        print(f"\n用户请求: {user_request}\n")
        print("这个任务需要：")
        print("  1. 查询天气")
        print("  2. 根据天气情况判断")
        print("  3. 撰写相应类型的通知")
        print()
        
        result = execute_chained_tool_call(
            env_vars, 
            user_request, 
            max_iterations=10,
            verbose=True
        )
        
        if result["success"]:
            print(f"\n✓ 复杂工作流执行成功")
            print(f"\n最终结果:\n{result['result']}")
            
            # 详细分析执行过程
            context = result["context"]
            print(f"\n{'=' * 60}")
            print("执行过程分析:")
            print(f"{'=' * 60}")
            print(f"总迭代次数: {context.current_iteration}")
            print(f"工具调用历史:")
            for i, step in enumerate(context.call_history, 1):
                print(f"\n步骤 {i}:")
                print(f"  工具: {step.get('tool_name')}")
                print(f"  成功: {step.get('success')}")
                if step.get('error'):
                    print(f"  错误: {step['error']}")
            
            print(f"\n中间变量:")
            for key, value in context.variables.items():
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"  {key}: {value_str}")
        else:
            print(f"\n✗ 失败: {result['error']}")
            
    except FileNotFoundError:
        print("\n⚠ 未找到 .env 文件\n")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("链式调用使用示例")
    print("=" * 60 + "\n")
    
    examples = [
        ("简单天气查询", example_1_simple_weather),
        ("多步骤任务", example_2_multi_step_task),
        ("通知撰写", example_3_notice_with_department),
        ("知识库查询", example_4_knowledgebase_query),
        ("复杂工作流", example_5_complex_workflow),
    ]
    
    for name, func in examples:
        print(f"\n{'#' * 60}")
        print(f"# 运行示例: {name}")
        print(f"{'#' * 60}\n")
        
        try:
            func()
        except Exception as e:
            print(f"示例执行出错: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n")
        input("按回车键继续下一个示例...")
    
    print("=" * 60)
    print("所有示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
