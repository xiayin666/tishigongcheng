"""
聊天记录管理模块
提供聊天历史的存储、统计和管理功能
"""
import json


class ChatHistoryManager:
    """聊天记录管理器"""
    
    def __init__(self):
        """初始化聊天记录管理器"""
        self.messages = []  # 存储所有消息
    
    def add_message(self, role, content):
        """
        添加一条消息到历史记录
        
        Args:
            role: 消息角色 (system/user/assistant/tool)
            content: 消息内容
        """
        message = {
            "role": role,
            "content": content
        }
        self.messages.append(message)
    
    def add_tool_call_message(self, message):
        """
        添加工具调用消息
        
        Args:
            message: 包含tool_calls的消息对象
        """
        self.messages.append(message)
    
    def add_tool_response(self, tool_call_id, name, content):
        """
        添加工具响应消息
        
        Args:
            tool_call_id: 工具调用ID
            name: 工具名称
            content: 工具返回内容
        """
        message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": content
        }
        self.messages.append(message)
    
    def get_messages(self):
        """获取所有消息"""
        return self.messages
    
    def get_round_count(self):
        """
        获取对话轮数（user-assistant为一轮）
        
        Returns:
            int: 对话轮数
        """
        round_count = 0
        for msg in self.messages:
            if msg.get("role") == "user":
                round_count += 1
        return round_count
    
    def get_context_length(self):
        """
        获取上下文总长度（字符数）
        
        Returns:
            int: 总字符数
        """
        total_length = 0
        for msg in self.messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_length += len(content)
            elif isinstance(content, list):
                # 处理可能的列表格式
                total_length += len(json.dumps(content, ensure_ascii=False))
        return total_length
    
    def clear_history(self):
        """清空历史记录"""
        self.messages = []
    
    def get_summary_marker(self, summary_text):
        """
        生成总结标记消息
        
        Args:
            summary_text: 总结文本
            
        Returns:
            dict: 总结消息对象
        """
        return {
            "role": "system",
            "content": f"[聊天记录总结]\n{summary_text}\n[总结结束]"
        }
