"""
Notice Skill Tool - 通知撰写工具

提供生成公司通知的功能，支持根据部门信息自动调整通知格式。
"""

import os
from practice05.notice_skill import generate_notice


def load_env_vars():
    """加载环境变量"""
    env_vars = {}
    for key in ['BASE_URL', 'MODEL', 'API_KEY']:
        value = os.environ.get(key)
        if value:
            env_vars[key] = value
    return env_vars


def extract_department_from_request(request):
    """
    从用户请求中提取部门信息
    
    Args:
        request: 用户的请求文本
        
    Returns:
        部门名称，如果未找到则返回 None
    """
    # 常见的部门关键词模式
    department_patterns = [
        r'我是(.+?)(?:部|部门|公司)的',
        r'(?:部|部门)[:：]\s*(.+?)(?:[,，。\s]|$)',
        r'(.+?)(?:部|部门)通知',
    ]
    
    import re
    for pattern in department_patterns:
        match = re.search(pattern, request)
        if match:
            dept = match.group(1).strip()
            # 过滤掉一些不合适的匹配
            if dept and len(dept) > 0 and dept not in ['一个', '这个', '那个']:
                return dept
    
    return None


def generate_company_notice(request, department=None):
    """
    生成公司通知
    
    Args:
        request: 用户的需求描述
        department: 用户所在部门（可选）
        
    Returns:
        生成的通知内容字典
    """
    try:
        env_vars = load_env_vars()
        
        if not env_vars:
            return {
                "error": "环境变量未配置，无法调用 LLM 服务",
                "notice": None
            }
        
        # 如果没有提供部门，尝试从请求中提取
        if not department:
            department = extract_department_from_request(request)
        
        # 调用 notice skill 生成通知
        notice_content = generate_notice(env_vars, request, user_department=department, use_mock=True)
        
        if notice_content:
            return {
                "success": True,
                "notice": notice_content,
                "department": department or "未指定"
            }
        else:
            return {
                "error": "生成通知失败",
                "notice": None
            }
            
    except Exception as e:
        return {
            "error": f"执行时出错: {str(e)}",
            "notice": None
        }


# 工具定义（用于 LLM 工具调用）
NOTICE_SKILL_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "generate_company_notice",
        "description": "生成公司正式通知文档。当用户请求撰写通知、公告、放假安排等公文时使用此工具。可以识别用户是否提供了部门信息，并相应调整通知开头格式。",
        "parameters": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "用户对通知的具体需求描述，例如'五一节放假通知'"
                },
                "department": {
                    "type": "string",
                    "description": "用户所在的部门名称（可选），如果用户提到了自己的部门则传入，否则为null"
                }
            },
            "required": ["request"]
        }
    }
}
