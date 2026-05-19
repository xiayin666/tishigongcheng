"""
聊天记录压缩模块
当聊天记录超过阈值时，使用LLM进行总结压缩
"""
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice01.llm_client import call_llm


def compress_chat_history(env_vars, messages, summary_ratio=0.75):
    """
    压缩聊天记录
    
    Args:
        env_vars: 环境变量字典
        messages: 消息列表
        summary_ratio: 需要总结的比例（默认75%）
        
    Returns:
        str: 压缩后的总结文本，如果不需要压缩则返回None
    """
    # 计算需要总结的消息范围
    total_messages = len(messages)
    if total_messages == 0:
        return None
    
    # 计算分割点：前summary_ratio的消息需要总结
    split_index = int(total_messages * summary_ratio)
    
    if split_index == 0 or split_index >= total_messages:
        return None
    
    # 提取需要总结的消息
    messages_to_summarize = messages[:split_index]
    messages_to_keep = messages[split_index:]
    
    print(f"\n{'='*60}")
    print(f"触发聊天记录压缩")
    print(f"总消息数: {total_messages}")
    print(f"总结前 {split_index} 条消息 ({summary_ratio*100:.0f}%)")
    print(f"保留后 {len(messages_to_keep)} 条消息 ({(1-summary_ratio)*100:.0f}%)")
    print(f"{'='*60}\n")
    
    # 构建需要总结的文本
    summary_text = _format_messages_for_summary(messages_to_summarize)
    
    # 调用LLM进行总结
    summary_result = _call_llm_for_summary(env_vars, summary_text)
    
    if summary_result:
        return summary_result
    
    return None


def _format_messages_for_summary(messages):
    """
    将消息格式化为适合总结的文本
    
    Args:
        messages: 消息列表
        
    Returns:
        str: 格式化后的文本
    """
    formatted_lines = []
    
    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        # 跳过工具响应消息的详细参数
        if role == "tool":
            tool_name = msg.get("name", "unknown")
            formatted_lines.append(f"[工具响应 {i}] {tool_name}: {content}")
        elif role == "system":
            # 跳过系统提示词的详细内容
            if "[聊天记录总结]" not in content:
                formatted_lines.append(f"[系统消息 {i}] {content[:100]}...")
        else:
            formatted_lines.append(f"[{role.upper()} {i}] {content}")
    
    return "\n\n".join(formatted_lines)


def _call_llm_for_summary(env_vars, text_to_summarize):
    """
    调用LLM生成总结
    
    Args:
        env_vars: 环境变量字典
        text_to_summarize: 需要总结的文本
        
    Returns:
        str: 总结文本
    """
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    # 构建总结提示词
    system_prompt = """你是一个专业的对话总结助手。请对提供的聊天记录进行简洁、准确的总结。

总结要求：
1. 保留关键信息和重要决策
2. 去除冗余和重复内容
3. 保持时间顺序和逻辑连贯
4. 使用简洁的语言，控制在300字以内
5. 不要遗漏用户的重要需求或问题
6. 不要包含具体的工具调用细节，只关注业务内容

请直接输出总结内容，不要添加其他说明。"""
    
    user_prompt = f"请总结以下聊天记录：\n\n{text_to_summarize}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print("正在调用LLM生成总结...")
    
    try:
        result = call_llm(base_url, model, api_key, user_prompt)
        
        if result and 'choices' in result and len(result['choices']) > 0:
            summary = result['choices'][0].get('message', {}).get('content', '')
            print(f"总结生成成功，长度: {len(summary)} 字符")
            return summary
        else:
            print("LLM返回结果格式异常")
            return None
            
    except Exception as e:
        print(f"调用LLM总结时出错: {str(e)}")
        return None


def should_compress(round_count, context_length, round_threshold=5, length_threshold=3000):
    """
    判断是否需要压缩聊天记录
    
    Args:
        round_count: 当前对话轮数
        context_length: 上下文长度（字符数）
        round_threshold: 轮数阈值（默认5轮）
        length_threshold: 长度阈值（默认3000字符）
        
    Returns:
        bool: 是否需要压缩
    """
    if round_count > round_threshold:
        print(f"对话轮数 ({round_count}) 超过阈值 ({round_threshold})，触发压缩")
        return True
    
    if context_length > length_threshold:
        print(f"上下文长度 ({context_length}) 超过阈值 ({length_threshold})，触发压缩")
        return True
    
    return False
