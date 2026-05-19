"""
支持聊天记录压缩和 Notice Skill 的智能对话客户端
基于practice04的chat_client_with_compression.py扩展，增加通知撰写功能
"""
import os
import json
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.file_tools import AVAILABLE_FUNCTIONS, TOOLS_DEFINITION
from practice04.anythingllm_tool import anythingllm_query, ANYTHINGLLM_TOOL_DEFINITION
from practice05.notice_skill_tool import generate_company_notice, NOTICE_SKILL_TOOL_DEFINITION
from practice03.chat_history import ChatHistoryManager
from practice03.chat_compressor import compress_chat_history, should_compress
from practice03.chat_log_manager import ChatLogManager, extract_key_info_from_summary, search_chat_history

# 合并所有工具定义
ALL_TOOLS_DEFINITION = TOOLS_DEFINITION + [ANYTHINGLLM_TOOL_DEFINITION] + [NOTICE_SKILL_TOOL_DEFINITION]

# 合并所有可用函数
ALL_AVAILABLE_FUNCTIONS = AVAILABLE_FUNCTIONS.copy()
ALL_AVAILABLE_FUNCTIONS["anythingllm_query"] = anythingllm_query
ALL_AVAILABLE_FUNCTIONS["generate_company_notice"] = generate_company_notice


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
    from http.client import HTTPConnection, HTTPSConnection
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
        # 根据协议选择连接类型
        if parsed_url.scheme == 'https':
            conn = HTTPSConnection(host, port, timeout=60)
        else:
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
    if function_name not in ALL_AVAILABLE_FUNCTIONS:
        return {"error": f"未知的函数: {function_name}"}
    
    try:
        func = ALL_AVAILABLE_FUNCTIONS[function_name]
        result = func(**arguments)
        return result
    except Exception as e:
        return {"error": f"执行函数 {function_name} 时出错: {str(e)}"}


def chat_with_context(env_vars, user_input, history_manager, log_manager=None):
    """
    支持上下文和自动压缩的对话
    
    Args:
        env_vars: 环境变量字典
        user_input: 用户输入
        history_manager: 聊天记录管理器
        log_manager: 日志管理器（可选）
        
    Returns:
        最终回复
    """
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    # 检查是否是搜索命令
    if user_input.startswith('/search') or '查找聊天历史' in user_input or '搜索历史' in user_input:
        if log_manager:
            reply = search_chat_history(env_vars, user_input, log_manager)
            print("\n" + "=" * 60)
            print("搜索结果:")
            print("=" * 60)
            print(reply)
            return reply
        else:
            return "日志管理器未初始化，无法搜索历史记录"
    
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

知识库查询工具：
7. anythingllm_query - 向 AnythingLLM 知识库系统发送查询，获取基于文档的专业回答。当用户询问公司内部文档、项目资料、技术文档、知识库内容时使用此工具。

通知撰写工具：
8. generate_company_notice - 生成公司正式通知文档。当用户请求撰写通知、公告、放假安排等公文时使用此工具。可以识别用户是否提供了部门信息，并相应调整通知开头格式。

使用指南：
- 当用户请求执行文件操作或查询天气时，请使用相应的工具
- 当用户询问关于公司文档、项目资料、技术规范、知识库内容等问题时，请使用 anythingllm_query 工具
- 当用户请求撰写通知、公告等公文时，请使用 generate_company_notice 工具
- 使用工具时，请提供准确的参数
- 如果工具返回错误信息，请向用户说明情况
- 对于文件路径，如果用户提供的是相对路径，请基于当前工作目录理解"""
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
        summary = compress_chat_history(env_vars, messages, summary_ratio=0.7)
        
        if summary:
            # 从总结中提取关键信息并保存
            if log_manager:
                print("\n正在从压缩记录中提取关键信息...")
                key_infos = extract_key_info_from_summary(env_vars, summary)
                if key_infos:
                    log_manager.save_to_log(key_infos)
            
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

知识库查询工具：
7. anythingllm_query - 向 AnythingLLM 知识库系统发送查询，获取基于文档的专业回答。当用户询问公司内部文档、项目资料、技术文档、知识库内容时使用此工具。

通知撰写工具：
8. generate_company_notice - 生成公司正式通知文档。当用户请求撰写通知、公告、放假安排等公文时使用此工具。可以识别用户是否提供了部门信息，并相应调整通知开头格式。

使用指南：
- 当用户请求执行文件操作或查询天气时，请使用相应的工具
- 当用户询问关于公司文档、项目资料、技术规范、知识库内容等问题时，请使用 anythingllm_query 工具
- 当用户请求撰写通知、公告等公文时，请使用 generate_company_notice 工具
- 使用工具时，请提供准确的参数
- 如果工具返回错误信息，请向用户说明情况
- 对于文件路径，如果用户提供的是相对路径，请基于当前工作目录理解"""
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
    response = call_llm_with_tools(base_url, model, api_key, messages, ALL_TOOLS_DEFINITION)
    
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
        final_response = call_llm_with_tools(base_url, model, api_key, messages, ALL_TOOLS_DEFINITION)
        
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
    
    # 将环境变量设置到系统中，供工具使用
    for key, value in env_vars.items():
        os.environ[key] = value
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误: .env文件中缺少必要的配置项(BASE_URL, MODEL, API_KEY)")
        return
    
    print("="*60)
    print("智能助手 - 支持聊天记录自动压缩、日志提取和通知撰写")
    print("="*60)
    print("可用工具：")
    print("  - 文件管理（list_files, rename_file, delete_file, create_file, read_file）")
    print("  - 天气查询（get_weather）")
    print("  - 知识库查询（anythingllm_query）")
    print("  - 通知撰写（generate_company_notice）")
    print("特殊命令：")
    print("  - /search <关键词> - 搜索聊天历史")
    print("  - /quit 或 /exit - 退出程序")
    print("="*60)
    
    # 初始化聊天记录管理器
    history_manager = ChatHistoryManager()
    
    # 初始化日志管理器
    log_manager = ChatLogManager()
    
    while True:
        try:
            user_input = input("\n请输入您的问题（输入/quit退出）：").strip()
            
            if not user_input:
                continue
            
            # 检查退出命令
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("\n感谢使用，再见！")
                break
            
            # 处理对话
            chat_with_context(env_vars, user_input, history_manager, log_manager)
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            print("感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
