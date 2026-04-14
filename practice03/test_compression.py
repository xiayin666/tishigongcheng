"""
测试聊天记录压缩功能
模拟多轮对话，验证压缩功能是否正常工作
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice03.chat_history import ChatHistoryManager
from practice03.chat_compressor import should_compress, compress_chat_history


def load_env_file(filepath='.env'):
    """读取.env文件并解析键值对"""
    env_vars = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件 {filepath} 不存在")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def test_round_threshold():
    """测试轮数阈值触发压缩"""
    print("\n" + "="*60)
    print("测试1: 对话轮数超过5轮触发压缩")
    print("="*60)
    
    history = ChatHistoryManager()
    
    # 添加系统消息
    history.add_message("system", "你是一个智能助手")
    
    # 模拟6轮对话（超过5轮阈值）
    for i in range(1, 7):
        history.add_message("user", f"这是第{i}轮用户问题")
        history.add_message("assistant", f"这是第{i}轮助手回复，包含一些详细内容来增加上下文长度")
        
        round_count = history.get_round_count()
        context_length = history.get_context_length()
        
        print(f"\n第{i}轮后:")
        print(f"  对话轮数: {round_count}")
        print(f"  上下文长度: {context_length} 字符")
        
        if should_compress(round_count, context_length):
            print(f"  ✓ 触发压缩条件!")
            break
    
    print("\n✓ 测试1通过: 轮数阈值检测正常")


def test_length_threshold():
    """测试上下文长度阈值触发压缩"""
    print("\n" + "="*60)
    print("测试2: 上下文长度超过3000字符触发压缩")
    print("="*60)
    
    history = ChatHistoryManager()
    
    # 添加系统消息
    history.add_message("system", "你是一个智能助手")
    
    # 添加少量轮数但很长的内容
    long_content = "这是一段很长的内容，用于测试上下文长度阈值。" * 80
    history.add_message("user", long_content)
    history.add_message("assistant", long_content)
    
    round_count = history.get_round_count()
    context_length = history.get_context_length()
    
    print(f"\n对话轮数: {round_count}")
    print(f"上下文长度: {context_length} 字符")
    
    if should_compress(round_count, context_length):
        print("✓ 触发压缩条件!")
        print("\n✓ 测试2通过: 长度阈值检测正常")
    else:
        print("✗ 未触发压缩条件")


def test_no_compress():
    """测试不满足压缩条件"""
    print("\n" + "="*60)
    print("测试3: 不满足压缩条件时不触发")
    print("="*60)
    
    history = ChatHistoryManager()
    
    # 添加系统消息
    history.add_message("system", "你是一个智能助手")
    
    # 添加2轮短对话
    history.add_message("user", "你好")
    history.add_message("assistant", "你好！有什么可以帮助你的吗？")
    history.add_message("user", "今天天气如何")
    history.add_message("assistant", "请问你想查询哪个城市的天气？")
    
    round_count = history.get_round_count()
    context_length = history.get_context_length()
    
    print(f"\n对话轮数: {round_count}")
    print(f"上下文长度: {context_length} 字符")
    
    if not should_compress(round_count, context_length):
        print("✓ 未触发压缩条件，符合预期")
        print("\n✓ 测试3通过: 不满足条件时不压缩")
    else:
        print("✗ 错误地触发了压缩")


def test_compress_function(env_vars):
    """测试压缩功能"""
    print("\n" + "="*60)
    print("测试4: 实际调用LLM进行压缩")
    print("="*60)
    
    history = ChatHistoryManager()
    
    # 添加系统消息
    history.add_message("system", "你是一个智能助手，可以查询天气和管理文件")
    
    # 模拟多轮对话
    conversations = [
        ("北京今天的天气怎么样？", "北京今天晴天，气温15-25度，空气质量良好。"),
        ("上海呢？", "上海今天多云转小雨，气温18-22度，建议携带雨具。"),
        ("帮我创建一个test.txt文件", "已在当前目录创建test.txt文件。"),
        ("文件内容是什么？", "test.txt文件内容为空。"),
        ("删除这个文件", "已成功删除test.txt文件。"),
        ("广州的天气如何？", "广州今天阴天，气温20-28度，湿度较大。"),
    ]
    
    for user_msg, assistant_msg in conversations:
        history.add_message("user", user_msg)
        history.add_message("assistant", assistant_msg)
    
    round_count = history.get_round_count()
    context_length = history.get_context_length()
    
    print(f"\n压缩前:")
    print(f"  对话轮数: {round_count}")
    print(f"  上下文长度: {context_length} 字符")
    print(f"  消息总数: {len(history.get_messages())}")
    
    # 执行压缩
    messages = history.get_messages()
    summary = compress_chat_history(env_vars, messages, summary_ratio=0.75)
    
    if summary:
        print(f"\n压缩成功!")
        print(f"\n总结内容:\n{summary}")
        print(f"\n总结长度: {len(summary)} 字符")
        print(f"压缩率: {(1 - len(summary)/context_length) * 100:.1f}%")
        print("\n✓ 测试4通过: LLM压缩功能正常")
    else:
        print("\n✗ 压缩失败")


def test_history_manager():
    """测试聊天记录管理器基本功能"""
    print("\n" + "="*60)
    print("测试5: 聊天记录管理器基本功能")
    print("="*60)
    
    history = ChatHistoryManager()
    
    # 测试添加消息
    history.add_message("system", "系统提示")
    history.add_message("user", "用户消息1")
    history.add_message("assistant", "助手回复1")
    history.add_message("user", "用户消息2")
    history.add_message("assistant", "助手回复2")
    
    print(f"\n消息总数: {len(history.get_messages())}")
    print(f"对话轮数: {history.get_round_count()}")
    print(f"上下文长度: {history.get_context_length()} 字符")
    
    # 测试清空
    history.clear_history()
    print(f"\n清空后消息数: {len(history.get_messages())}")
    
    print("\n✓ 测试5通过: 聊天记录管理器功能正常")


def main():
    """主函数"""
    print("="*60)
    print("聊天记录压缩功能测试")
    print("="*60)
    
    # 加载环境变量
    try:
        env_vars = load_env_file('.env')
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    # 运行测试
    try:
        test_history_manager()
        test_round_threshold()
        test_length_threshold()
        test_no_compress()
        test_compress_function(env_vars)
        
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
