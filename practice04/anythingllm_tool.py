"""
AnythingLLM 查询工具
使用 subprocess 调用 curl 命令访问 AnythingLLM API
"""
import subprocess
import json
import os


def anythingllm_query(message: str, workspace_slug: str = None) -> dict:
    """
    向 AnythingLLM 发送查询消息并获取回复
    
    Args:
        message: 要发送给 AnythingLLM 的消息内容
        workspace_slug: 工作空间标识符（可选，默认为 'main'）
        
    Returns:
        包含 AnythingLLM 回复的字典
    """
    try:
        # 从环境变量获取 API Key
        api_key = os.getenv('ANYTHINGLLM_KEY')
        if not api_key:
            return {"error": "未找到 ANYTHINGLLM_KEY 环境变量"}
        
        # 设置默认工作空间
        if not workspace_slug:
            workspace_slug = "042211f4-0b84-4045-adf0-a0b9df4df708"  # 我的工作区
        
        # AnythingLLM API 地址
        base_url = "http://localhost:3001/api/v1"
        
        # 尝试多个端点，优先使用非流式API
        endpoints_to_try = [
            f"{base_url}/workspace/{workspace_slug}/chat",  # 非流式聊天
            f"{base_url}/workspace/{workspace_slug}/stream-chat",  # 流式聊天（备用）
        ]
        
        last_error = None
        connection_failed = False
        
        for url in endpoints_to_try:
            try:
                # 构建请求体
                payload = {
                    "message": message,
                    "mode": "query"  # 查询模式，优先从知识库检索
                }
                
                # 构建 curl 命令
                curl_command = [
                    "curl",
                    "-X", "POST",
                    url,
                    "-H", f"Authorization: Bearer {api_key}",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(payload, ensure_ascii=False),
                    "--max-time", "60",  # 最大超时时间
                    "--connect-timeout", "5"  # 连接超时5秒
                ]
                
                # 执行 curl 命令
                result = subprocess.run(
                    curl_command,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8'
                )
                
                # 检查执行结果
                if result.returncode != 0:
                    error_msg = result.stderr
                    
                    # 检测是否是连接失败
                    if "Failed to connect" in error_msg or "Connection refused" in error_msg:
                        connection_failed = True
                        last_error = f"无法连接到 AnythingLLM 服务 (localhost:3001)。请确认 AnythingLLM 是否正在运行。"
                        break  # 连接失败不需要尝试其他端点
                    
                    last_error = f"curl 命令执行失败: {error_msg[:200]}"
                    continue
                
                # 解析响应
                response_text = result.stdout.strip()
                
                # 如果是空响应，跳过
                if not response_text:
                    last_error = "返回空响应"
                    continue
                
                # 处理流式响应
                lines = response_text.split('\n')
                
                # 尝试解析所有行，收集完整响应
                full_response = ""
                parsed_data = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 处理 SSE 格式 (data: {...})
                    if line.startswith('data: '):
                        line = line[6:]
                    
                    # 跳过 [DONE] 标记
                    if line == '[DONE]':
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # 检查是否有错误（error 为 True 时才表示错误）
                        if isinstance(data, dict) and data.get('error') is True:
                            last_error = f"AnythingLLM 返回错误: {data.get('message', '未知错误')}"
                            break
                        
                        # 提取文本内容
                        if isinstance(data, dict):
                            if 'textResponse' in data:
                                full_response += data['textResponse']
                                parsed_data = data
                            elif 'response' in data:
                                full_response += data['response']
                                parsed_data = data
                            elif 'content' in data:
                                full_response += data['content']
                                parsed_data = data
                    except json.JSONDecodeError:
                        # 如果不是JSON，可能是纯文本响应
                        if not line.startswith('{'):
                            full_response += line + "\n"
                
                # 如果有完整的响应，返回
                if full_response.strip():
                    return {
                        "success": True,
                        "response": full_response.strip(),
                        "raw_response": parsed_data if parsed_data else full_response
                    }
                
                # 如果没有解析出内容，但有原始响应
                if response_text:
                    return {
                        "success": True,
                        "response": response_text,
                        "raw_response": response_text
                    }
                
                last_error = "未能从响应中提取内容"
                
            except subprocess.TimeoutExpired:
                last_error = "请求超时（60秒）"
                continue
            except Exception as e:
                last_error = f"请求出错: {str(e)}"
                continue
        
        # 所有端点都失败了
        return {"error": f"所有尝试均失败。最后错误: {last_error}"}
            
    except Exception as e:
        return {"error": f"查询 AnythingLLM 时出错: {str(e)}"}


# AnythingLLM 工具定义（用于发送给 LLM）
ANYTHINGLLM_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "anythingllm_query",
        "description": "向 AnythingLLM 知识库系统发送查询，获取基于文档的专业回答。当用户询问公司内部文档、项目资料、技术文档、知识库内容时使用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "要查询的问题或消息内容"
                },
                "workspace_slug": {
                    "type": "string",
                    "description": "工作空间标识符（可选，默认为 main）"
                }
            },
            "required": ["message"]
        }
    }
}
