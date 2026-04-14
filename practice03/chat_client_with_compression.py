"""
支持聊天记录压缩的智能对话客户端
基于practice02的chat_client.py扩展，增加上下文管理和自动压缩功能
"""
import os
import json
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.file_tools import AVAILABLE_FUNCTIONS, TOOLS_DEFINITION
from practice03.chat_history import ChatHistoryManager
from practice03.chat_compressor import compress_chat_history, should_compress


def load_env_file(filepath='.env'):
    """读取.env文件并解析键值对"""
    env_vars = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件 {filepath} 不存在，请从 env.example 复制一份并重命名为 .env")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def call_llm_with_tools(base_url, model, api_key, messages, tools=None):
    """
    使用标准http库调用LLM API，支持工具调用
    
    Args:
        base_url: LLM API的基础URL
        model: 模型名称
        api_key: API密钥
        messages: 消息列表
        tools: 工具定义列表
        
    Returns:
        LLM响应结果
    """
    from http.client import HTTPConnection
    from urllib.parse import urlparse
    
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    path = parsed_url.path + '/chat/completions'
    
    # 构建请求体
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    
    # 如果提供了工具，添加到请求中
    if tools:
        payload["tools"] = tools
    
    body = json.dumps(payload).encode('utf-8')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body)),
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # 创建HTTP连接
        conn = HTTPConnection(host, port, timeout=60)
        
        # 发送POST请求
        conn.request('POST', path, body=body, headers=headers)
        
        # 获取响应
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        
        # 关闭连接
        conn.close()
        
        # 解析响应
        if response.status == 200:
            result = json.loads(response_data)
            return result
        else:
            print(f"请求失败，状态码: {response.status}")
            print(f"响应内容: {response_data}")
            return None
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


def execute_function_call(function_name, arguments):
    """
    执行函数调用
    
    Args:
        function_name: 函数名
        arguments: 函数字典参数
        
    Returns:
        函数执行结果
    """
    if function_name not in AVAILABLE_FUNCTIONS:
        return {"error": f"未知的函数: {function_name}"}
    
    try:
        func = AVAILABLE_FUNCTIONS[function_name]
        result = func(**arguments)
        return result
    except Exception as e:
        return {"error": f"执行函数 {function_name} 时出错: {str(e)}"}


def chat_with_context(env_vars, user_input, history_manager):
    """
    支持上下文和自动压缩的对话
    
    Args:
        env_vars: 环境变量字典
        user_input: 用户输入
        history_manager: 聊天记录管理器
        
    Returns:
        最终回复
    """
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    # 系统提示词（只在第一次对话时添加）
    if len(history_manager.get_messages()) == 0:
        system_message = {
            "role": "system",
            "content": """你是一个智能助手，可以使用以下工具来帮助用户：

文件管理工具：
1. list_files - 列出目录下的文件及其属性
2. rename_file - 重命名文件
3. delete_file - 删除文件
4. create_file_with_content - 创建新文件并写入内容
5. read_file_content - 读取文件内容

天气查询工具：
6. get_weather - 查询指定城市的当前天气和未来几天预报

当用户请求执行文件操作或查询天气时，请使用相应的工具。使用工具时，请提供准确的参数。
如果工具返回错误信息，请向用户说明情况。
对于文件路径，如果用户提供的是相对路径，请基于当前工作目录理解。"""
        }
        history_manager.add_message("system", system_message["content"])
    
    # 添加用户消息
    history_manager.add_message("user", user_input)
    
    # 检查是否需要压缩
    round_count = history_manager.get_round_count()
    context_length = history_manager.get_context_length()
    
    if should_compress(round_count, context_length):
        # 执行压缩
        messages = history_manager.get_messages()
        summary = compress_chat_history(env_vars, messages, summary_ratio=0.75)
        
        if summary:
            # 清空历史记录
            history_manager.clear_history()
            
            # 添加系统提示词
            system_message = {
                "role": "system",
                "content": """你是一个智能助手，可以使用以下工具来帮助用户：

文件管理工具：
1. list_files - 列出目录下的文件及其属性
2. rename_file - 重命名文件
3. delete_file - 删除文件
4. create_file_with_content - 创建新文件并写入内容
5. read_file_content - 读取文件内容

天气查询工具：
6. get_weather - 查询指定城市的当前天气和未来几天预报

当用户请求执行文件操作或查询天气时，请使用相应的工具。使用工具时，请提供准确的参数。
如果工具返回错误信息，请向用户说明情况。
对于文件路径，如果用户提供的是相对路径，请基于当前工作目录理解。"""
            }
            history_manager.add_message("system", system_message["content"])
            
            # 添加总结
            summary_marker = history_manager.get_summary_marker(summary)
            history_manager.add_message("system", summary_marker["content"])
            
            # 重新添加当前用户消息
            history_manager.add_message("user", user_input)
            
            print(f"\n聊天记录已压缩，当前轮数: {history_manager.get_round_count()}")
            print(f"当前上下文长度: {history_manager.get_context_length()} 字符\n")
    
    # 获取当前消息历史
    messages = history_manager.get_messages()
    
    print("=" * 60)
    print("正在调用 LLM...")
    print("=" * 60)
    
    # 第一次调用 LLM
    response = call_llm_with_tools(base_url, model, api_key, messages, TOOLS_DEFINITION)
    
    if not response:
        print("LLM 调用失败")
        return None
    
    # 检查是否有工具调用
    choice = response.get('choices', [{}])[0]
    message = choice.get('message', {})
    
    # 如果有工具调用
    if 'tool_calls' in message and message['tool_calls']:
        tool_calls = message['tool_calls']
        print(f"\nLLM 请求调用 {len(tool_calls)} 个工具:")
        
        # 添加工具调用到消息历史
        history_manager.add_tool_call_message(message)
        
        # 执行每个工具调用
        for tool_call in tool_calls:
            tool_id = tool_call.get('id')
            function = tool_call.get('function', {})
            function_name = function.get('name')
            arguments_str = function.get('arguments', '{}')
            
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                arguments = {}
            
            print(f"\n  工具: {function_name}")
            print(f"  参数: {json.dumps(arguments, ensure_ascii=False, indent=4)}")
            
            # 执行函数
            result = execute_function_call(function_name, arguments)
            print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=4)}")
            
            # 添加工具响应到消息历史
            history_manager.add_tool_response(
                tool_id, 
                function_name, 
                json.dumps(result, ensure_ascii=False)
            )
        
        print("\n" + "=" * 60)
        print("将工具结果发送给 LLM 获取最终回复...")
        print("=" * 60)
        
        # 第二次调用 LLM，传入工具执行结果
        messages = history_manager.get_messages()
        final_response = call_llm_with_tools(base_url, model, api_key, messages, TOOLS_DEFINITION)
        
        if final_response:
            final_choice = final_response.get('choices', [{}])[0]
            final_message = final_choice.get('message', {})
            final_content = final_message.get('content', '')
            
            # 添加助手回复到历史
            history_manager.add_message("assistant", final_content)
            
            print("\n" + "=" * 60)
            print("助手回复:")
            print("=" * 60)
            print(final_content)
            return final_content
    else:
        # 没有工具调用，直接返回回复
        content = message.get('content', '')
        
        # 添加助手回复到历史
        history_manager.add_message("assistant", content)
        
        print("\n" + "=" * 60)
        print("助手回复:")
        print("=" * 60)
        print(content)
        return content


def main():
    """主函数"""
    # 加载环境变量
    try:
        env_vars = load_env_file('.env')
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误: .env文件中缺少必要的配置项(BASE_URL, MODEL, API_KEY)")
        return
    
    print("="*60)
    print("智能助手 - 支持聊天记录自动压缩")
    print("="*60)
    print("\n功能特点:")
    print("  ✓ 支持多轮对话上下文")
    print("  ✓ 自动检测对话轮数和上下文长度")
    print("  ✓ 超过5轮或3000字符时自动压缩历史")
    print("  ✓ 保留最近25%的原始对话内容")
    print("\n可用工具:")
    print("  1. list_files - 列出目录文件")
    print("  2. rename_file - 重命名文件")
    print("  3. delete_file - 删除文件")
    print("  4. create_file_with_content - 创建文件")
    print("  5. read_file_content - 读取文件")
    print("  6. get_weather - 查询天气")
    print("\n示例问题:")
    print("  - 列出当前目录下的所有文件")
    print("  - 北京今天的天气怎么样？")
    print("  - 在 test_dir 目录下创建一个名为 hello.txt 的文件")
    print("-" * 60)
    
    # 创建聊天记录管理器
    history_manager = ChatHistoryManager()
    
    # 交互式对话
    while True:
        try:
            user_input = input("\n请输入你的问题 (输入 'quit' 或 'exit' 退出, 'clear' 清空历史): ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break
            
            if user_input.lower() in ['clear', 'cls']:
                history_manager.clear_history()
                print("聊天记录已清空")
                continue
            
            if not user_input.strip():
                continue
            
            # 显示当前状态
            round_count = history_manager.get_round_count()
            context_length = history_manager.get_context_length()
            print(f"\n[当前状态] 对话轮数: {round_count}, 上下文长度: {context_length} 字符")
            
            chat_with_context(env_vars, user_input, history_manager)
            
        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
