"""
Notice Skill - 通知撰写技能

这个 skill 让 LLM 能够根据用户的部门信息撰写正式的公司通知。
如果用户没有提供部门信息，会自动询问或使用默认部门。
"""

import json
from http.client import HTTPConnection
from urllib.parse import urlparse


def call_llm(base_url, model, api_key, messages):
    """
    调用 LLM API
    
    Args:
        base_url: LLM API 基础 URL
        model: 模型名称
        api_key: API 密钥
        messages: 消息列表
        
    Returns:
        LLM 响应结果
    """
    parsed_url = urlparse(base_url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    path = parsed_url.path + '/chat/completions'
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    
    body = json.dumps(payload).encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body)),
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn = HTTPConnection(host, port, timeout=60)
        conn.request('POST', path, body=body, headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()
        
        if response.status == 200:
            return json.loads(response_data)
        else:
            return {"error": f"请求失败，状态码: {response.status}", "details": response_data}
    except Exception as e:
        return {"error": f"发生错误: {str(e)}"}


def create_notice_skill_prompt(user_department=None):
    """
    创建 notice skill 的系统提示词
    
    Args:
        user_department: 用户所在的部门（可选）
        
    Returns:
        系统提示词
    """
    if user_department:
        department_info = f"用户所在部门：{user_department}"
        start_format = f"通知必须以'{user_department}通知'开头"
    else:
        department_info = "用户未说明所在部门"
        start_format = "通知必须以'XX部通知'开头（使用占位符表示未知部门）"
    
    system_prompt = f"""你是一个专业的公司通知撰写助手。你的任务是根据用户需求撰写正式的公司通知。

{department_info}

通知撰写要求：
1. {start_format}
2. 使用正式、规范的公文语言
3. 结构清晰，包含标题、正文、落款等要素
4. 内容要具体明确，包括时间、地点、事项等关键信息
5. 语气要得体，符合公司内部通知的风格
6. 如果是节假日通知，需要包含放假时间、注意事项等信息

请根据用户的具体需求，生成一份完整、规范的通知文档。"""
    
    return system_prompt


def generate_notice(env_vars, user_request, user_department=None, use_mock=False):
    """
    使用 notice skill 生成通知
    
    Args:
        env_vars: 环境变量字典
        user_request: 用户的需求描述
        user_department: 用户所在部门（可选）
        use_mock: 是否使用模拟模式（用于测试）
        
    Returns:
        生成的通知内容
    """
    # 如果使用模拟模式，返回模拟结果
    if use_mock:
        return generate_mock_notice(user_request, user_department)
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    # 创建系统提示词
    system_prompt = create_notice_skill_prompt(user_department)
    
    # 构建消息列表
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request}
    ]
    
    print("=" * 60)
    print("正在使用 Notice Skill 生成通知...")
    print("=" * 60)
    if user_department:
        print(f"用户部门: {user_department}")
    else:
        print("用户部门: 未说明")
    print(f"用户需求: {user_request}")
    print("=" * 60)
    
    # 调用 LLM
    response = call_llm(base_url, model, api_key, messages)
    
    if "error" in response:
        print(f"错误: {response['error']}")
        return None
    
    # 提取回复内容
    choice = response.get('choices', [{}])[0]
    message = choice.get('message', {})
    content = message.get('content', '')
    
    return content


def generate_mock_notice(user_request, user_department=None):
    """
    生成模拟的通知（用于测试，无需连接 LLM 服务）
    
    Args:
        user_request: 用户需求
        user_department: 用户部门
        
    Returns:
        模拟的通知内容
    """
    if user_department:
        header = f"{user_department}通知"
    else:
        header = "XX部通知"
    
    mock_notice = f"""{header}

关于2026年五一劳动节放假安排的通知

各位同事：

根据国家法定节假日安排，结合公司实际情况，现将2026年五一劳动节放假安排通知如下：

一、放假时间
2026年5月1日（星期五）至5月5日（星期二）放假调休，共5天。
4月26日（星期日）、5月9日（星期六）上班。

二、注意事项
1. 请各部门在放假前做好工作安排，确保业务正常运转；
2. 离开办公室前，请关闭电脑、空调等电器设备，关好门窗；
3. 节假日期间外出请注意人身和财产安全；
4. 保持手机畅通，如有紧急工作需要，能够及时联系。

三、值班安排
节假日期间，各部门需安排人员值班，具体值班表由各部门自行安排并报备行政部。

祝大家节日快乐，阖家幸福！

特此通知。

{header.split('通知')[0]}
2026年4月23日"""
    
    return mock_notice
