"""
链式调用执行器 - execute_chained_tool_call

实现链式工具调用的完整流程，支持多轮工具调用和状态管理
"""
import json
import os
import sys
from typing import Dict, List, Any, Optional, Callable

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice05.chained_call_context import ChainedCallContext
from practice02.file_tools import AVAILABLE_FUNCTIONS as FILE_FUNCTIONS, TOOLS_DEFINITION as FILE_TOOLS
from practice02.weather_tool import get_weather, WEATHER_TOOL_DEFINITION
from practice04.anythingllm_tool import anythingllm_query, ANYTHINGLLM_TOOL_DEFINITION
from practice05.notice_skill_tool import generate_company_notice, NOTICE_SKILL_TOOL_DEFINITION


# 合并所有可用函数
ALL_AVAILABLE_FUNCTIONS = {}
ALL_AVAILABLE_FUNCTIONS.update(FILE_FUNCTIONS)
ALL_AVAILABLE_FUNCTIONS["get_weather"] = get_weather
ALL_AVAILABLE_FUNCTIONS["anythingllm_query"] = anythingllm_query
ALL_AVAILABLE_FUNCTIONS["generate_company_notice"] = generate_company_notice

# 合并所有工具定义
ALL_TOOLS_DEFINITION = []
ALL_TOOLS_DEFINITION.extend(FILE_TOOLS)
ALL_TOOLS_DEFINITION.append(WEATHER_TOOL_DEFINITION)
ALL_TOOLS_DEFINITION.append(ANYTHINGLLM_TOOL_DEFINITION)
ALL_TOOLS_DEFINITION.append(NOTICE_SKILL_TOOL_DEFINITION)


def call_llm_api(base_url: str, model: str, api_key: str, messages: List[Dict], tools: List[Dict] = None, max_retries: int = 3) -> Dict:
    """
    调用 LLM API（带重试机制）
    
    Args:
        base_url: LLM API 基础 URL
        model: 模型名称
        api_key: API 密钥
        messages: 消息列表
        tools: 工具定义列表（可选）
        max_retries: 最大重试次数
        
    Returns:
        LLM 响应结果
    """
    from http.client import HTTPConnection, HTTPSConnection
    from urllib.parse import urlparse
    import time
    
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
        payload["tool_choice"] = "auto"
    
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body)),
        'Authorization': f'Bearer {api_key}'
    }
    
    last_error = None
    for attempt in range(max_retries):
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
                error_msg = f"请求失败，状态码: {response.status}"
                last_error = {"error": error_msg, "details": response_data}
                
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            last_error = {"error": error_msg}
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：2s, 4s, 8s...
                print(f"  ⚠️ 第{attempt + 1}次尝试失败，{wait_time}秒后重试...")
                time.sleep(wait_time)
            continue
    
    # 所有重试都失败了
    return last_error


def fix_incomplete_json(json_str: str) -> str:
    """
    尝试修复不完整的JSON字符串
    
    Args:
        json_str: 不完整的JSON字符串
        
    Returns:
        修复后的JSON字符串，如果无法修复则返回None
    """
    if not json_str or not json_str.startswith('{'):
        return None
    
    # 计算括号平衡
    brace_count = 0
    bracket_count = 0
    in_string = False
    escape_next = False
    
    for i, char in enumerate(json_str):
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if in_string:
            continue
        
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        elif char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
    
    # 如果括号不平衡，尝试修复
    if brace_count > 0 or bracket_count > 0:
        # 添加缺失的闭合括号
        fixed = json_str
        if brace_count > 0:
            fixed += '}' * brace_count
        if bracket_count > 0:
            fixed += ']' * bracket_count
        
        # 验证修复后的JSON是否有效
        try:
            json.loads(fixed)
            return fixed
        except:
            pass
    
    return None


def detect_duplicate_call(context: ChainedCallContext, tool_name: str, arguments: Dict) -> bool:
    """
    检测是否是重复的工具调用
    
    Args:
        context: 当前上下文
        tool_name: 工具名称
        arguments: 工具参数
        
    Returns:
        True 如果是重复调用，False 否则
    """
    if not context.call_history:
        return False
    
    # 检查最近5次调用是否有相同的工具和参数（扩大检测范围）
    recent_calls = context.call_history[-5:] if len(context.call_history) >= 5 else context.call_history
    
    for call in recent_calls:
        if call.get('tool_name') == tool_name and call.get('success', False):
            # 对于文件路径，进行标准化比较（忽略大小写和斜杠差异）
            old_args = call.get('arguments', {})
            
            # 标准化参数进行比较
            is_same = True
            for key in arguments:
                old_val = old_args.get(key)
                new_val = arguments[key]
                
                # 如果都是字符串，进行标准化比较
                if isinstance(old_val, str) and isinstance(new_val, str):
                    # 对于路径，统一转换为小写并规范化斜杠
                    if 'path' in key.lower() or 'directory' in key.lower():
                        if old_val.lower().replace('\\', '/').rstrip('/') != new_val.lower().replace('\\', '/').rstrip('/'):
                            is_same = False
                            break
                    elif old_val.lower() != new_val.lower():
                        is_same = False
                        break
                elif old_val != new_val:
                    is_same = False
                    break
            
            if is_same:
                return True
    
    return False


def generate_auto_answer(user_request: str, context: ChainedCallContext) -> str:
    """
    基于已有的工具调用结果，自动生成答案
    
    Args:
        user_request: 用户原始请求
        context: 链式调用上下文
        
    Returns:
        自动生成的答案文本
    """
    # 收集所有工具调用结果（包括失败的）
    all_calls = context.call_history
    successful_calls = [call for call in all_calls if call.get('success')]
    failed_calls = [call for call in all_calls if not call.get('success')]
    
    if not all_calls:
        return "抱歉，未能获取到足够的信息来回答您的问题。"
    
    # 根据不同的工具类型生成不同的答案
    answer_parts = []
    
    # 检查是否有天气查询
    weather_calls = [call for call in successful_calls if call['tool_name'] == 'get_weather']
    if weather_calls:
        for call in weather_calls:
            result = call['result']
            if isinstance(result, dict):
                location = result.get('location', {})
                current = result.get('current_weather', {})
                forecast = result.get('forecast', [])
                
                city = location.get('city', '未知城市')
                temp = current.get('temperature', 'N/A')
                feels_like = current.get('feels_like', 'N/A')
                humidity = current.get('humidity', 'N/A')
                weather = current.get('weather', 'N/A')
                wind = current.get('wind_speed', 'N/A')
                
                answer_parts.append(f"📍 {city}天气情况：")
                answer_parts.append(f"   • 温度：{temp}（体感 {feels_like}）")
                answer_parts.append(f"   • 天气：{weather}")
                answer_parts.append(f"   • 湿度：{humidity}")
                answer_parts.append(f"   • 风速：{wind}")
                
                # 如果有预报，添加预报信息
                if forecast:
                    answer_parts.append(f"\n   未来预报：")
                    for day in forecast[:2]:  # 只显示前2天
                        date = day.get('date', 'N/A')
                        max_t = day.get('max_temp', 'N/A')
                        min_t = day.get('min_temp', 'N/A')
                        w = day.get('weather', 'N/A')
                        answer_parts.append(f"   - {date}: {w}, {min_t} ~ {max_t}")
                
                # 根据天气给出出行建议
                answer_parts.append(f"\n💡 出行建议：")
                if '雨' in weather or '雪' in weather:
                    answer_parts.append("   • 建议携带雨具/雪具")
                    answer_parts.append("   • 路面可能湿滑，注意交通安全")
                if '晴' in weather or '主要晴朗' in weather:
                    answer_parts.append("   • 天气良好，适合户外活动")
                    answer_parts.append("   • 注意防晒")
                
                temp_value = float(temp.replace('°C', '').replace('-', '')) if '°C' in temp else 20
                if temp_value < 10:
                    answer_parts.append("   • 温度较低，注意保暖")
                elif temp_value > 25:
                    answer_parts.append("   • 温度较高，注意防暑降温")
                else:
                    answer_parts.append("   • 温度适中，穿着舒适")
                
                answer_parts.append("")  # 空行分隔
    
    # 检查是否有失败的天气查询
    failed_weather = [call for call in failed_calls if call['tool_name'] == 'get_weather']
    if failed_weather:
        for call in failed_weather:
            error_msg = call.get('error', '未知错误')
            arguments = call.get('arguments', {})
            city = arguments.get('city', '未知城市')
            answer_parts.append(f"❌ {city}天气查询失败：{error_msg}")
            answer_parts.append(f"   提示：请尝试使用英文城市名或检查城市名称是否正确")
            answer_parts.append("")
    
    # 检查是否有文件列表查询
    file_list_calls = [call for call in successful_calls if call['tool_name'] == 'list_files']
    if file_list_calls:
        for call in file_list_calls:
            result = call['result']
            if isinstance(result, dict):
                directory = result.get('directory', '未知目录')
                total_items = result.get('total_items', 0)
                files = result.get('files', [])
                
                answer_parts.append(f"📁 目录: {directory}")
                answer_parts.append(f"   共 {total_items} 个项目")
                answer_parts.append("")
                
                # 分类显示文件和文件夹
                dirs = [f for f in files if f.get('is_directory')]
                regular_files = [f for f in files if not f.get('is_directory')]
                
                if dirs:
                    answer_parts.append(f"   📂 文件夹 ({len(dirs)}个):")
                    for d in dirs[:10]:  # 最多显示10个
                        name = d.get('name', 'N/A')
                        modified = d.get('modified_time', 'N/A')
                        answer_parts.append(f"      - {name} (修改于: {modified})")
                    if len(dirs) > 10:
                        answer_parts.append(f"      ... 还有 {len(dirs) - 10} 个文件夹")
                    answer_parts.append("")
                
                if regular_files:
                    answer_parts.append(f"   📄 文件 ({len(regular_files)}个):")
                    for f in regular_files[:15]:  # 最多显示15个
                        name = f.get('name', 'N/A')
                        size = f.get('size_human', 'N/A')
                        modified = f.get('modified_time', 'N/A')
                        answer_parts.append(f"      - {name} ({size}, 修改于: {modified})")
                    if len(regular_files) > 15:
                        answer_parts.append(f"      ... 还有 {len(regular_files) - 15} 个文件")
                    answer_parts.append("")
    
    # 检查是否有文件读取
    file_read_calls = [call for call in successful_calls if call['tool_name'] == 'read_file']
    if file_read_calls:
        for call in file_read_calls:
            result = call['result']
            if isinstance(result, dict):
                filepath = result.get('file_path', '未知文件')
                content = result.get('content', '')
                lines = result.get('lines_count', 0)
                
                answer_parts.append(f"📄 文件: {filepath}")
                answer_parts.append(f"   共 {lines} 行")
                answer_parts.append(f"\n   内容预览:")
                # 显示前20行
                preview_lines = content.split('\n')[:20]
                for i, line in enumerate(preview_lines, 1):
                    answer_parts.append(f"   {i:3d} | {line}")
                if lines > 20:
                    answer_parts.append(f"   ... (还有 {lines - 20} 行)")
                answer_parts.append("")
    
    # 检查是否有知识库查询
    kb_calls = [call for call in successful_calls if call['tool_name'] == 'anythingllm_query']
    if kb_calls:
        for call in kb_calls:
            result = call['result']
            if isinstance(result, dict):
                response = result.get('response', '')
                if response:
                    answer_parts.append(f"📚 知识库查询结果：\n{response}\n")
    
    # 检查是否有通知生成
    notice_calls = [call for call in successful_calls if call['tool_name'] == 'generate_company_notice']
    if notice_calls:
        for call in notice_calls:
            result = call['result']
            if isinstance(result, dict):
                notice = result.get('notice', '')
                if notice:
                    answer_parts.append(f"📝 生成的通知：\n{notice}\n")
    
    # 如果没有任何特定格式的答案，返回通用总结
    if not answer_parts:
        answer_parts.append("已执行以下操作：")
        for i, call in enumerate(all_calls, 1):
            status = "✓" if call.get('success') else "✗"
            answer_parts.append(f"{i}. [{status}] 调用 {call['tool_name']}")
            if call.get('error'):
                answer_parts.append(f"   错误：{call['error']}")
    
    # 组合答案
    final_answer = "\n".join(answer_parts).strip()
    
    # 如果没有具体的建议，添加一个通用的总结
    if '建议' not in final_answer and '出行' in user_request:
        final_answer += "\n\n💡 总体建议：请根据以上天气情况合理安排出行计划。"
    
    return final_answer


def build_analysis_prompt(user_request: str, context: ChainedCallContext, available_tools: list = None) -> str:
    """
    构建分析提示词，包含用户请求、已执行的步骤历史和决策规则
    
    Args:
        user_request: 用户的原始请求
        context: 链式调用上下文
        available_tools: 可用工具列表（可选）
        
    Returns:
        分析提示词字符串
    """
    prompt_parts = [
        "# 任务分析",
        f"\n## 用户原始请求\n{user_request}\n",
        "=" * 60
    ]
    
    # 如果有中间变量，显示出来
    if context.variables:
        prompt_parts.append("\n## 当前可用的中间变量")
        for key, value in context.variables.items():
            value_str = json.dumps(value, ensure_ascii=False)
            # 如果值太长，截断显示
            if len(value_str) > 300:
                value_str = value_str[:300] + "... (已截断)"
            prompt_parts.append(f"- {key}: {value_str}")
    
    # 如果有调用历史，显示出来
    if context.call_history:
        prompt_parts.append(f"\n## 已执行的工具调用历史（共 {len(context.call_history)} 步）")
        for i, step in enumerate(context.call_history, 1):
            prompt_parts.append(f"\n### 步骤 {i}")
            prompt_parts.append(f"- **工具名称**: {step.get('tool_name', 'N/A')}")
            prompt_parts.append(f"- **参数**: ```json\n{json.dumps(step.get('arguments', {}), ensure_ascii=False, indent=2)}\n```")
            
            result = step.get('result')
            if result:
                result_str = json.dumps(result, ensure_ascii=False, indent=2)
                # 如果结果太长，截断显示
                if len(result_str) > 500:
                    result_str = result_str[:500] + "\n... (已截断)"
                prompt_parts.append(f"- **结果**: ```json\n{result_str}\n```")
            
            if step.get('error'):
                prompt_parts.append(f"- **错误**: {step['error']}")
            
            success_status = "✓ 成功" if step.get('success') else "✗ 失败"
            prompt_parts.append(f"- **状态**: {success_status}")
    
    # 添加可用工具信息
    if available_tools:
        prompt_parts.append("\n## 可用工具列表")
        for tool in available_tools:
            if isinstance(tool, dict) and 'function' in tool:
                func = tool['function']
                prompt_parts.append(f"\n### {func['name']}")
                prompt_parts.append(f"- **描述**: {func.get('description', '无描述')}")
                if 'parameters' in func and 'properties' in func['parameters']:
                    prompt_parts.append("- **参数**:")
                    for param_name, param_info in func['parameters']['properties'].items():
                        required = "(必需)" if param_name in func['parameters'].get('required', []) else "(可选)"
                        prompt_parts.append(f"  - `{param_name}` {required}: {param_info.get('description', '无描述')}")
    
    # 添加决策规则说明
    prompt_parts.append("\n" + "=" * 60)
    prompt_parts.append("\n## ⚠️ 极其重要的决策规则")
    prompt_parts.append("\n**核心原则：获取到所需信息后，立即停止调用工具并返回答案！**")
    prompt_parts.append("\n请根据以上信息，决定下一步操作。你必须严格按照以下 JSON 格式返回决策：")
    
    # 如果有调用历史，添加强烈警告
    if context.call_history:
        prompt_parts.append("\n### 🚨 特别警告")
        prompt_parts.append("- **检查上面的调用历史**：如果你已经调用过某个工具并获得了结果，**绝对不要**再次调用相同的工具！")
        prompt_parts.append("- **你已经拥有了必要的信息**，现在应该基于这些信息给出最终答案")
        prompt_parts.append("- **重复调用是严重错误**，会导致任务失败")
        prompt_parts.append("- 例如：如果已经调用了 `get_weather` 并获得天气数据，就**必须**立即返回出行建议，而不是再次查询天气")
    prompt_parts.append("\n### 情况1：任务已完成")
    prompt_parts.append("如果你已经有足够的信息来回答用户的原始请求，请返回：")
    prompt_parts.append("```json")
    prompt_parts.append('{')
    prompt_parts.append('  "done": true,')
    prompt_parts.append('  "answer": "你的最终回答内容，应该完整、清晰地回答用户的问题"')
    prompt_parts.append('}')
    prompt_parts.append("```")
    
    prompt_parts.append("\n### 情况2：需要继续调用工具")
    prompt_parts.append("如果你需要获取更多信息才能完成任务，请返回：")
    prompt_parts.append("```json")
    prompt_parts.append('{')
    prompt_parts.append('  "done": false,')
    prompt_parts.append('  "tool_call": {')
    prompt_parts.append('    "name": "工具名称",')
    prompt_parts.append('    "arguments": {')
    prompt_parts.append('      "参数名1": "参数值1",')
    prompt_parts.append('      "参数名2": "参数值2"')
    prompt_parts.append('    }')
    prompt_parts.append('  }')
    prompt_parts.append('}')
    prompt_parts.append("```")
    
    prompt_parts.append("\n## 重要提示")
    prompt_parts.append("1. **必须**返回有效的 JSON 格式，不要添加额外的文本或解释")
    prompt_parts.append("2. 如果任务完成，`done` 设为 `true`，并提供完整的 `answer`")
    prompt_parts.append("3. 如果需要调用工具，`done` 设为 `false`，并指定 `tool_call` 的 `name` 和 `arguments`")
    prompt_parts.append("4. 确保工具名称和参数与可用工具列表中的定义完全匹配")
    prompt_parts.append("5. 参考已执行的调用历史，避免重复调用相同的工具获取相同的信息")
    prompt_parts.append("6. 如果之前的工具调用失败，考虑使用不同的参数或尝试其他工具")
    
    return "\n".join(prompt_parts)


def parse_llm_response(response: Dict) -> Dict[str, Any]:
    """
    解析 LLM 响应，支持 JSON 格式和 tool_calls 格式
    
    Args:
        response: LLM 响应字典
        
    Returns:
        解析结果，包含以下字段：
        - type: 'completed' (任务完成) 或 'tool_call' (需要调用工具) 或 'error' (错误)
        - content: 回复内容（如果任务完成）
        - tool_call: 工具调用信息（如果需要调用工具），包含 name 和 arguments
        - error: 错误信息（如果有）
    """
    if "error" in response:
        return {
            "type": "error",
            "error": response["error"]
        }
    
    choice = response.get('choices', [{}])[0]
    message = choice.get('message', {})
    content = message.get('content', '')
    
    # 首先尝试解析 JSON 格式
    if content:
        try:
            # 尝试提取 JSON（可能包含在代码块中）
            json_str = content.strip()
            
            # 检查是否是不完整的JSON（以 { 开头但没有正确闭合）
            if json_str.startswith('{') and not json_str.endswith('}'):
                # 尝试修复不完整的JSON
                fixed_json = fix_incomplete_json(json_str)
                if fixed_json:
                    json_str = fixed_json
                else:
                    # 无法修复，返回错误
                    return {
                        "type": "error",
                        "error": f"LLM 返回了不完整的 JSON 响应"
                    }
            
            # 如果包含 ```json 代码块，提取其中的内容
            if '```json' in json_str:
                start_idx = json_str.find('```json') + 7
                end_idx = json_str.find('```', start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
            elif '```' in json_str:
                start_idx = json_str.find('```') + 3
                end_idx = json_str.find('```', start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
            
            # 解析 JSON
            parsed_json = json.loads(json_str)
            
            # 检查是否是完成的格式
            if isinstance(parsed_json, dict):
                if parsed_json.get('done') == True and 'answer' in parsed_json:
                    return {
                        "type": "completed",
                        "content": parsed_json['answer']
                    }
                
                # 检查是否是工具调用格式
                elif parsed_json.get('done') == False and 'tool_call' in parsed_json:
                    tool_call = parsed_json['tool_call']
                    if 'name' in tool_call and 'arguments' in tool_call:
                        return {
                            "type": "tool_call",
                            "tool_call": {
                                "name": tool_call['name'],
                                "arguments": tool_call['arguments']
                            }
                        }
            
            # 如果JSON格式不符合预期，尝试作为普通文本处理
            return {
                "type": "completed",
                "content": content
            }
            
        except json.JSONDecodeError as e:
            # JSON 解析失败，可能是不完整的JSON
            if '{' in content and '}' not in content:
                # 尝试修复不完整的JSON
                fixed_json = fix_incomplete_json(content)
                if fixed_json:
                    try:
                        parsed_json = json.loads(fixed_json)
                        if isinstance(parsed_json, dict):
                            if parsed_json.get('done') == True and 'answer' in parsed_json:
                                return {
                                    "type": "completed",
                                    "content": parsed_json['answer']
                                }
                            elif parsed_json.get('done') == False and 'tool_call' in parsed_json:
                                tool_call = parsed_json['tool_call']
                                if 'name' in tool_call and 'arguments' in tool_call:
                                    return {
                                        "type": "tool_call",
                                        "tool_call": {
                                            "name": tool_call['name'],
                                            "arguments": tool_call['arguments']
                                        }
                                    }
                    except:
                        pass
                return {
                    "type": "error",
                    "error": f"LLM 返回了不完整的 JSON: {str(e)}"
                }
            # 继续检查是否有 tool_calls
            pass
    
    # 检查是否有 tool_calls（OpenAI 格式）
    if 'tool_calls' in message and message['tool_calls']:
        # 将第一个 tool_call 转换为我们的格式
        first_tool_call = message['tool_calls'][0]
        function = first_tool_call.get('function', {})
        return {
            "type": "tool_call",
            "tool_call": {
                "name": function.get('name'),
                "arguments": json.loads(function.get('arguments', '{}'))
            }
        }
    
    # 没有工具调用，认为是任务完成（纯文本回复）
    if content:
        return {
            "type": "completed",
            "content": content
        }
    
    # 既没有内容也没有工具调用，返回错误
    return {
        "type": "error",
        "error": "LLM 响应为空或格式不正确"
    }


def execute_tool_call(tool_call: Dict) -> Dict[str, Any]:
    """
    执行单个工具调用
    
    Args:
        tool_call: 工具调用信息
        
    Returns:
        执行结果
    """
    function = tool_call.get('function', {})
    function_name = function.get('name')
    arguments_str = function.get('arguments', '{}')
    
    try:
        arguments = json.loads(arguments_str)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"参数解析失败: {arguments_str}"
        }
    
    if function_name not in ALL_AVAILABLE_FUNCTIONS:
        return {
            "success": False,
            "error": f"未知的函数: {function_name}"
        }
    
    try:
        func = ALL_AVAILABLE_FUNCTIONS[function_name]
        result = func(**arguments)
        return {
            "success": True,
            "result": result,
            "tool_name": function_name,
            "arguments": arguments
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"执行函数 {function_name} 时出错: {str(e)}",
            "tool_name": function_name,
            "arguments": arguments
        }


def trim_message_history(messages: List[Dict], max_messages: int = 20) -> List[Dict]:
    """
    裁剪消息历史，保留最重要的消息
    
    Args:
        messages: 消息列表
        max_messages: 最大消息数量
        
    Returns:
        裁剪后的消息列表
    """
    if len(messages) <= max_messages:
        return messages
    
    # 始终保留第一条系统消息
    system_message = None
    if messages and messages[0].get('role') == 'system':
        system_message = messages[0]
        messages = messages[1:]
    
    # 保留最近的消息
    recent_messages = messages[-(max_messages - 1):] if system_message else messages[-max_messages:]
    
    # 重新组合消息
    if system_message:
        return [system_message] + recent_messages
    else:
        return recent_messages


def execute_chained_tool_call(
    env_vars: Dict[str, str],
    user_request: str,
    system_prompt: str = None,
    max_iterations: int = 5,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    执行链式工具调用的完整流程
    
    流程：
    1. 初始化消息历史，包含system prompt
    2. 循环最多max_iterations次：
       - 构建分析提示词（包含用户请求和已执行的步骤历史）
       - 调用LLM决定下一步操作
       - 解析LLM响应（支持JSON格式和tool_calls格式）
       - 如果任务完成，返回最终回答
       - 如果需继续调用，执行工具并记录到上下文
       - 将结果添加到消息历史，继续下一轮
    
    Args:
        env_vars: 环境变量字典，包含 BASE_URL, MODEL, API_KEY
        user_request: 用户的请求
        system_prompt: 系统提示词（可选，默认使用通用提示词）
        max_iterations: 最大迭代次数
        verbose: 是否输出详细信息
        
    Returns:
        执行结果字典，包含：
        - success: 是否成功
        - result: 最终结果
        - context: 链式调用上下文对象
        - error: 错误信息（如果有）
    """
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        return {
            "success": False,
            "error": "缺少必要的环境变量 (BASE_URL, MODEL, API_KEY)",
            "result": None,
            "context": None
        }
    
    # 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    
    # 默认系统提示词
    if not system_prompt:
        system_prompt = """你是一个智能助手，可以使用多种工具来帮助用户完成复杂任务。

## 可用工具
1. **文件管理工具**：list_files, rename_file, delete_file, create_file_with_content, read_file_content
2. **天气查询工具**：get_weather - 查询指定城市的天气
3. **知识库查询工具**：anythingllm_query - 查询 AnythingLLM 知识库（公司内部文档、项目资料等）
4. **通知撰写工具**：generate_company_notice - 生成公司正式通知

### 📚 知识库查询最佳实践
- **何时使用**：当用户询问公司内部文档、项目规范、技术资料、历史项目等信息时
- **查询技巧**：
  - 使用具体、明确的问题，而不是模糊的关键词
  - 例如："项目开发规范有哪些要求？" 比 "开发规范" 更好
  - 例如："notice技能的使用规则和示例" 比 "notice" 更好
- **如果第一次查询没有结果**：
  - 尝试换一种问法或更具体的描述
  - 可以多次查询不同的相关问题
  - 不要重复完全相同的查询

## ⚠️ 核心规则：何时停止调用工具

**当你已经获得足够信息来回答用户问题时，必须立即返回最终答案（done: true），不要再调用工具！**

### 判断标准：
- ✅ 已获取所有必要信息 → 立即返回答案（done: true）
- ❌ 还在重复查询已知信息 → 错误！应该总结并返回
- ✅ 工具已返回完整数据 → 基于数据给出建议/总结
- ❌ 已有天气数据还继续调用 get_weather → 错误！

### 典型场景示例：

**场景1：天气查询 + 建议**
- 第1步：调用 get_weather("成都") → 获得天气数据
- 第2步：**必须停止**，基于天气数据给出出行建议（done: true）
- ❌ 错误做法：再次调用 get_weather("成都")

**场景2：多城市比较**
- 第1步：调用 get_weather("北京")
- 第2步：调用 get_weather("上海")  
- 第3步：**必须停止**，比较两地天气并给出建议（done: true）
- ❌ 错误做法：继续调用 get_weather("北京")

## 链式调用规则

### 1. 工具调用的顺序依赖关系
- **先查询后处理**：如果需要处理文件内容，必须先使用 list_files 查找文件，再使用 read_file_content 读取内容
- **先获取信息后决策**：如果需要根据某些信息做决策，必须先调用工具获取该信息
- **逐步推进**：每个步骤都应该建立在前一步的结果之上
- **避免重复**：检查 call_history，不要重复调用相同的工具获取相同的信息

### 2. 如何根据中间结果决定后续操作
- **分析工具返回的结果**：仔细阅读工具的 output，提取关键信息
- **判断是否满足任务需求**：如果已有足够信息，立即返回最终答案（done: true）
- **识别缺失信息**：如果信息不足，确定还需要什么数据，调用相应工具
- **利用中间变量**：之前步骤中存储的 variables 可以在后续决策中使用
- **错误处理**：如果工具调用失败，尝试其他方法或调整参数重新调用

### 3. 上下文变量的使用方式
- **自动存储**：某些工具执行后会自动提取关键信息存入 variables
  - get_weather → weather_location
  - anythingllm_query → knowledgebase_response
  - generate_company_notice → generated_notice
- **手动引用**：在决策时可以参考 "当前可用的中间变量" 部分
- **跨步骤传递**：variables 在整个链式调用过程中持续存在，可用于后续步骤

## 链式调用示例

### 示例1：文件搜索和内容分析
用户请求："请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"

**第1步**：列出目录下的文件
```json
{
  "done": false,
  "tool_call": {
    "name": "list_files",
    "arguments": {"directory": "practice06"}
  }
}
```

**第2步**：读取第一个Python文件的内容
```json
{
  "done": false,
  "tool_call": {
    "name": "read_file_content",
    "arguments": {"file_path": "practice06/example.py"}
  }
}
```

**第3步**：继续读取其他文件...

**最后一步**：总结所有文件内容
```json
{
  "done": true,
  "answer": "在practice06目录中找到3个包含'def'的文件：\n1. example.py - 包含函数定义...\n2. utils.py - 包含工具函数...\n3. main.py - 主程序入口..."
}
```

### 示例2：技能查询
用户请求："我想了解notice技能的详细规则"

**第1步**：查询知识库
```json
{
  "done": false,
  "tool_call": {
    "name": "anythingllm_query",
    "arguments": {"message": "notice技能的详细规则和用法"}
  }
}
```

**第2步**：根据查询结果回答问题（注意：已经有答案了，必须停止！）
```json
{
  "done": true,
  "answer": "Notice技能是一个通知撰写工具，主要规则包括：..."
}
```

### 示例3：天气查询 + 出行建议（重要示例！）
用户请求："成都今天天气怎么样？给我出行建议"

**第1步**：查询天气
```json
{
  "done": false,
  "tool_call": {
    "name": "get_weather",
    "arguments": {"city": "成都"}
  }
}
```

**第2步**：已获得天气数据，必须停止并给出建议！
```json
{
  "done": true,
  "answer": "成都今天天气：毛毛雨，温度15.6°C，湿度80%。\n\n出行建议：\n1. 建议携带雨具\n2. 温度适中，穿着长袖衣物\n3. 路面可能湿滑，注意交通安全"
}
```

❌ **错误示范**（绝对不要这样做）：
```json
// 错误！已经有天气数据了，不应该再次查询
{
  "done": false,
  "tool_call": {
    "name": "get_weather",
    "arguments": {"city": "成都"}
  }
}
```

### 示例4：网页处理和文件保存
用户请求："访问http://163.com/news/article/xxx.html 并提取页面标题，保存到practice07/title.txt"

**第1步**：访问网页（假设有web_fetch工具）
```json
{
  "done": false,
  "tool_call": {
    "name": "web_fetch",
    "arguments": {"url": "http://163.com/news/article/xxx.html"}
  }
}
```

**第2步**：创建文件保存标题
```json
{
  "done": false,
  "tool_call": {
    "name": "create_file_with_content",
    "arguments": {
      "file_path": "practice07/title.txt",
      "content": "提取的页面标题"
    }
  }
}
```

**第3步**：确认任务完成
```json
{
  "done": true,
  "answer": "已成功提取页面标题并保存到 practice07/title.txt"
}
```

## 工作流程
1. 分析用户需求，拆解为多个子任务
2. 按顺序执行每个子任务，每次调用一个工具
3. 根据工具返回结果决定下一步操作
4. **当获得足够信息时，立即返回最终答案（done: true）**
5. 整合所有信息返回最终答案

## JSON 输出格式要求
**⚠️ 极其重要：你必须严格按照 JSON 格式返回决策，不要添加任何额外文本！**

- 任务完成时返回: `{"done": true, "answer": "最终回答"}`
- 需要调用工具时返回: `{"done": false, "tool_call": {"name": "工具名", "arguments": {...}}}`

**常见错误**：
- ❌ 在JSON前后添加解释文字
- ❌ 已有数据还继续调用相同工具
- ❌ 忘记设置 done 字段
- ❌ 返回格式不是有效的JSON

## 注意事项
- 对于复杂任务，可能需要多步操作（通常3-8步）
- 每一步都应该有明确的目标和预期结果
- 参考已执行的调用历史，避免重复操作
- 如果遇到问题，尝试其他方法或向用户说明情况
- **不要**在 JSON 之外添加任何额外的文本或解释
- 确保工具名称和参数与可用工具列表中的定义完全匹配
- **记住：获取到所需信息后，立即停止调用工具并返回答案！**"""
    
    # 初始化消息历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    if verbose:
        print("=" * 60)
        print("开始执行链式工具调用")
        print("=" * 60)
        print(f"用户请求: {user_request}")
        print(f"最大迭代次数: {max_iterations}")
        print("=" * 60)
    
    # 主循环
    while context.can_continue():
        context.next_iteration()
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"第 {context.current_iteration} 轮迭代")
            print(f"{'=' * 60}")
        
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context, ALL_TOOLS_DEFINITION)
        
        # 添加用户消息（第一轮是原始请求，后续是分析提示词）
        if context.current_iteration == 1:
            messages.append({"role": "user", "content": user_request})
        else:
            messages.append({"role": "user", "content": analysis_prompt})
        
        if verbose:
            print(f"\n调用 LLM...")
        
        # 调用 LLM
        response = call_llm_api(base_url, model, api_key, messages, ALL_TOOLS_DEFINITION)
        
        if "error" in response:
            error_msg = response["error"]
            context.fail(f"LLM 调用失败: {error_msg}")
            if verbose:
                print(f"\n错误: {error_msg}")
            break
        
        # 解析 LLM 响应
        parsed = parse_llm_response(response)
        
        if parsed["type"] == "error":
            context.fail(parsed["error"])
            if verbose:
                print(f"\n错误: {parsed['error']}")
            break
        
        elif parsed["type"] == "completed":
            # 任务完成
            final_answer = parsed["content"]
            context.complete(final_answer)
            
            if verbose:
                print(f"\n{'=' * 60}")
                print("任务完成！")
                print(f"{'=' * 60}")
                print(f"\n最终结果:\n{final_answer}")
            
            break
        
        elif parsed["type"] == "tool_call":
            # 需要调用工具
            tool_call_info = parsed["tool_call"]
            tool_name = tool_call_info["name"]
            arguments = tool_call_info["arguments"]
            
            if verbose:
                print(f"\nLLM 决定调用工具:")
                print(f"  工具: {tool_name}")
                print(f"  参数: {json.dumps(arguments, ensure_ascii=False, indent=4)}")
            
            # ⚠️ 检测重复调用
            if detect_duplicate_call(context, tool_name, arguments):
                if verbose:
                    print(f"\n⚠️  检测到重复调用！LLM试图再次调用 {tool_name} 使用相同参数")
                    print(f"   强制结束循环，基于已有信息生成答案...")
                
                # 基于已有的工具调用结果，自动生成答案
                auto_answer = generate_auto_answer(user_request, context)
                context.complete(auto_answer)
                
                if verbose:
                    print(f"\n{'=' * 60}")
                    print("任务完成！（自动总结）")
                    print(f"{'=' * 60}")
                    print(f"\n最终结果:\n{auto_answer}")
                break
            
            # 构造工具调用对象（兼容 execute_tool_call 函数）
            tool_call_obj = {
                "id": f"call_{context.current_iteration}",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(arguments, ensure_ascii=False)
                }
            }
            
            # 执行工具
            result = execute_tool_call(tool_call_obj)
            
            if verbose:
                if result["success"]:
                    result_str = json.dumps(result["result"], ensure_ascii=False, indent=4)
                    if len(result_str) > 500:
                        result_str = result_str[:500] + "... (已截断)"
                    print(f"  结果: {result_str}")
                else:
                    print(f"  错误: {result['error']}")
            
            # 记录到上下文
            context.add_call_record({
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result.get("result") if result["success"] else None,
                "error": result.get("error") if not result["success"] else None,
                "success": result["success"]
            })
            
            # 添加助手回复到消息历史（包含 JSON 决策）
            assistant_message = {
                "role": "assistant",
                "content": json.dumps({
                    "done": False,
                    "tool_call": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }, ensure_ascii=False)
            }
            messages.append(assistant_message)
            
            # 添加工具响应到消息历史
            tool_result = result["result"] if result["success"] else result["error"]
            messages.append({
                "role": "user",
                "content": f"工具 {tool_name} 执行结果:\n{json.dumps(tool_result, ensure_ascii=False, indent=2)}"
            })
            
            # 裁剪消息历史，防止上下文过长
            messages = trim_message_history(messages, max_messages=20)
            
            # 如果工具执行成功，可以尝试提取有用的信息存储为变量
            if result["success"] and result["result"]:
                # 可以根据工具名称自动提取关键信息
                if tool_name == "get_weather":
                    if isinstance(result["result"], dict) and "location" in result["result"]:
                        context.set_variable("weather_location", result["result"]["location"].get("city"))
                elif tool_name == "anythingllm_query":
                    if isinstance(result["result"], dict) and "response" in result["result"]:
                        context.set_variable("knowledgebase_response", result["result"]["response"])
                elif tool_name == "generate_company_notice":
                    if isinstance(result["result"], dict) and "notice" in result["result"]:
                        context.set_variable("generated_notice", result["result"]["notice"])
    
    # 循环结束，检查结果
    if context.is_completed and context.final_result:
        return {
            "success": True,
            "result": context.final_result,
            "context": context,
            "error": None
        }
    else:
        error_msg = context.error or "未知错误"
        return {
            "success": False,
            "result": context.final_result,
            "context": context,
            "error": error_msg
        }


# 便捷函数：加载环境变量
def load_env_vars(filepath='.env') -> Dict[str, str]:
    """
    从 .env 文件加载环境变量
    
    Args:
        filepath: .env 文件路径
        
    Returns:
        环境变量字典
    """
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


if __name__ == "__main__":
    """测试链式调用执行器"""
    try:
        # 加载环境变量
        env_vars = load_env_vars('.env')
        
        # 设置环境变量到系统
        for key, value in env_vars.items():
            os.environ[key] = value
        
        print("链式调用执行器测试")
        print("=" * 60)
        
        # 测试用例1：简单的天气查询
        test_request = "帮我查询北京的天气"
        print(f"\n测试1: {test_request}")
        result = execute_chained_tool_call(env_vars, test_request, max_iterations=5, verbose=True)
        
        if result["success"]:
            print(f"\n✓ 成功: {result['result'][:200]}")
        else:
            print(f"\n✗ 失败: {result['error']}")
        
        print("\n" + "=" * 60)
        print("测试完成")
        
    except Exception as e:
        print(f"测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
