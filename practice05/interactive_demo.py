"""
链式调用交互式演示

提供一个简单的交互式界面来体验链式调用功能
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_executor import execute_chained_tool_call, load_env_vars


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "=" * 60)
    print("链式调用交互式演示")
    print("=" * 60)
    print("\n这个演示展示了如何使用链式调用完成复杂任务。")
    print("LLM 可以连续调用多个工具，逐步完成任务。")
    print("\n可用工具：")
    print("  - 天气查询 (get_weather)")
    print("  - 通知撰写 (generate_company_notice)")
    print("  - 知识库查询 (anythingllm_query)")
    print("  - 文件管理 (list_files, read_file, etc.)")
    print("\n特殊命令：")
    print("  /quit 或 /exit - 退出演示")
    print("  /help - 显示帮助")
    print("  /examples - 显示示例请求")
    print("=" * 60)


def print_examples():
    """打印示例请求"""
    print("\n示例请求：")
    print("-" * 60)
    examples = [
        "简单查询",
        "  • 北京今天天气怎么样？",
        "",
        "多步查询",
        "  • 帮我查北京、上海、广州的天气，告诉我哪里最适合旅游",
        "",
        "条件判断",
        "  • 先查北京天气，如果晴天就写户外活动通知，雨天写室内活动通知",
        "",
        "通知撰写",
        "  • 我是行政部的，帮我写一个五一劳动节放假通知",
        "",
        "知识库查询",
        "  • 查询公司的项目开发规范文档",
        "",
        "复杂任务",
        "  • 查询北京的天气情况，然后根据天气写一个出行建议通知",
    ]
    for line in examples:
        print(line)
    print("-" * 60)


def main():
    """主函数"""
    # 加载环境变量
    try:
        env_vars = load_env_vars('.env')
        for key, value in env_vars.items():
            os.environ[key] = value
    except FileNotFoundError:
        print("\n⚠ 错误: 未找到 .env 文件")
        print("请从 env.example 复制一份并重命名为 .env")
        return
    except Exception as e:
        print(f"\n⚠ 错误: {str(e)}")
        return
    
    print_welcome()
    
    while True:
        try:
            user_input = input("\n请输入您的请求（输入 /help 查看帮助）: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("\n感谢使用，再见！👋\n")
                break
            
            if user_input.lower() == '/help':
                print_welcome()
                continue
            
            if user_input.lower() == '/examples':
                print_examples()
                continue
            
            # 执行链式调用
            print(f"\n{'=' * 60}")
            print(f"正在处理: {user_input}")
            print(f"{'=' * 60}\n")
            
            result = execute_chained_tool_call(
                env_vars,
                user_input,
                max_iterations=5,
                verbose=True
            )
            
            # 显示结果
            print(f"\n{'=' * 60}")
            if result["success"]:
                print("✅ 任务完成！")
                print(f"{'=' * 60}")
                print(f"\n最终结果:\n{result['result']}")
                
                # 显示执行统计
                context = result["context"]
                print(f"\n{'=' * 60}")
                print("执行统计:")
                print(f"{'=' * 60}")
                print(f"  • 迭代次数: {context.current_iteration}")
                print(f"  • 工具调用: {len(context.call_history)} 次")
                print(f"  • 中间变量: {len(context.variables)} 个")
                
                if context.call_history:
                    print(f"\n调用历史:")
                    for i, step in enumerate(context.call_history, 1):
                        print(f"  {i}. {step['tool_name']} - {'✓' if step['success'] else '✗'}")
            else:
                print("❌ 任务失败")
                print(f"{'=' * 60}")
                print(f"错误信息: {result['error']}")
                
                if result["context"]:
                    context = result["context"]
                    print(f"\n已执行 {context.current_iteration} 次迭代")
                    print(f"已调用 {len(context.call_history)} 次工具")
            
            print(f"{'=' * 60}")
            
        except KeyboardInterrupt:
            print("\n\n⚠ 程序被用户中断")
            print("感谢使用，再见！👋\n")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
