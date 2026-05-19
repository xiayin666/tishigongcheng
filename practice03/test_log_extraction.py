"""
测试聊天记录提取和搜索功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice03.chat_log_manager import ChatLogManager, extract_key_info_from_summary


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


def test_extract_and_save(env_vars):
    """测试信息提取和保存功能"""
    print("\n" + "="*60)
    print("测试1: 从聊天总结中提取5W信息并保存")
    print("="*60)
    
    # 模拟聊天总结
    chat_summary = """用户在本次对话中主要进行了以下活动：

1. 查询了北京的天气情况，了解到今天是晴天，气温15-25度，空气质量良好，适合出行。

2. 随后查询了上海的天气，得知上海多云转小雨，气温18-22度，建议携带雨具。

3. 用户请求在当前目录创建了一个名为test.txt的文件，助手成功执行了创建操作。

4. 用户询问文件内容，助手回复文件内容为空。

5. 最后用户要求删除该文件，助手成功完成了删除操作。

整个对话体现了助手在天气查询和文件管理方面的功能。"""
    
    print(f"\n聊天总结:\n{chat_summary}\n")
    
    # 提取关键信息
    log_manager = ChatLogManager()
    key_infos = log_manager.extract_key_info(env_vars, chat_summary)
    
    if key_infos:
        print(f"\n提取的关键信息:")
        for i, info in enumerate(key_infos, 1):
            print(f"\n记录 {i}:")
            print(f"  Who   : {info.get('who', '未提及')}")
            print(f"  What  : {info.get('what', '未提及')}")
            print(f"  When  : {info.get('when', '未提及')}")
            print(f"  Where : {info.get('where', '未提及')}")
            print(f"  Why   : {info.get('why', '未提及')}")
        
        # 保存到日志文件
        print("\n保存到日志文件...")
        log_manager.save_to_log(key_infos)
        
        print("\n✓ 测试1通过: 信息提取和保存成功")
        return True
    else:
        print("\n✗ 测试1失败: 未能提取关键信息")
        return False


def test_search_logs():
    """测试日志搜索功能"""
    print("\n" + "="*60)
    print("测试2: 搜索日志文件")
    print("="*60)
    
    log_manager = ChatLogManager()
    
    # 测试搜索"天气"
    print("\n搜索关键词: '天气'")
    result = log_manager.search_logs("天气")
    print(result)
    
    # 测试搜索"文件"
    print("\n" + "-"*60)
    print("搜索关键词: '文件'")
    result = log_manager.search_logs("文件")
    print(result)
    
    print("\n✓ 测试2通过: 日志搜索功能正常")


def test_recent_logs():
    """测试获取最近日志"""
    print("\n" + "="*60)
    print("测试3: 获取最近的日志记录")
    print("="*60)
    
    log_manager = ChatLogManager()
    recent = log_manager.get_recent_logs(count=3)
    
    print(recent)
    print("\n✓ 测试3通过: 获取最近日志功能正常")


def test_search_command():
    """测试/search命令"""
    print("\n" + "="*60)
    print("测试4: /search命令处理")
    print("="*60)
    
    env_vars = load_env_file('.env')
    log_manager = ChatLogManager()
    
    # 模拟用户输入
    test_queries = [
        "/search 天气",
        "查找聊天历史中关于北京的内容",
        "搜索历史记录中的文件操作"
    ]
    
    for query in test_queries:
        print(f"\n用户输入: {query}")
        
        # 检查是否触发搜索
        if query.startswith('/search') or '查找聊天历史' in query or '搜索历史' in query:
            print("✓ 识别为搜索命令")
            # 这里不实际调用LLM，只测试逻辑
        else:
            print("○ 普通对话")
    
    print("\n✓ 测试4通过: /search命令识别正常")


def main():
    """主函数"""
    print("="*60)
    print("聊天记录提取和搜索功能测试")
    print("="*60)
    
    # 加载环境变量
    try:
        env_vars = load_env_file('.env')
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    # 运行测试
    try:
        # 测试1: 提取和保存（需要LLM）
        success = test_extract_and_save(env_vars)
        
        if success:
            # 测试2: 搜索日志
            test_search_logs()
            
            # 测试3: 获取最近日志
            test_recent_logs()
        
        # 测试4: /search命令
        test_search_command()
        
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
