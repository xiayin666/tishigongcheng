"""
聊天日志管理模块
从压缩的聊天记录中提取5W关键信息并保存到本地文件
"""
import os
import json
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice01.llm_client import call_llm


class ChatLogManager:
    """聊天日志管理器"""
    
    def __init__(self, log_file_path=r"D:\chat-Log\log.txt"):
        """
        初始化日志管理器
        
        Args:
            log_file_path: 日志文件路径
        """
        self.log_file_path = log_file_path
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """确保日志目录存在"""
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"创建日志目录: {log_dir}")
        
        # 如果日志文件不存在，创建空文件
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("# 聊天日志记录\n")
                f.write("# 格式: [时间] Who | What | When | Where | Why\n")
                f.write("=" * 80 + "\n\n")
    
    def extract_key_info(self, env_vars, chat_summary):
        """
        从聊天总结中提取5W关键信息
        
        Args:
            env_vars: 环境变量字典
            chat_summary: 聊天总结文本
            
        Returns:
            list: 提取的关键信息列表，每个元素是一个字典包含5W信息
        """
        base_url = env_vars.get('BASE_URL')
        model = env_vars.get('MODEL')
        api_key = env_vars.get('API_KEY')
        
        # 构建提取提示词
        system_prompt = """你是一个专业的信息提取助手。

**严格指令：你必须只返回JSON数组，不要任何其他文字！**

从聊天记录中提取关键信息，按照5W规则整理为JSON数组格式：
- who: 涉及的人物、角色或主体
- what: 具体的行为、事件或任务
- when: 时间信息（如果没有填"未提及"）
- where: 地点信息（如果没有填"未提及"）
- why: 目的、原因或动机（如果没有填"未提及"）

**输出格式示例（必须严格遵守）：**
[{"who":"用户","what":"查询北京天气","when":"今天","where":"北京","why":"了解出行建议"},{"who":"用户","what":"创建test.txt文件","when":"未提及","where":"当前目录","why":"未提及"}]

**禁止事项：**
- 禁止添加```json标记
- 禁止添加任何解释文字
- 禁止添加编号列表
- 只返回JSON数组本身"""
        
        user_prompt = f"请从以下聊天总结中提取关键信息：\n\n{chat_summary}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        print("正在提取关键信息...")
        
        try:
            result = call_llm(base_url, model, api_key, user_prompt)
            
            if result and 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                
                # 尝试解析JSON
                try:
                    # 清理可能的markdown标记
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    # 查找JSON数组
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = content[start_idx:end_idx]
                        key_infos = json.loads(json_str)
                        print(f"成功提取 {len(key_infos)} 条关键信息")
                        return key_infos
                    else:
                        print("未能找到JSON格式数据")
                        print(f"LLM返回内容: {content[:200]}...")
                        # 使用后备方案
                        print("尝试使用后备方案解析...")
                        key_infos = self._fallback_parse(content, chat_summary)
                        if key_infos:
                            print(f"后备方案成功提取 {len(key_infos)} 条关键信息")
                            return key_infos
                        return []
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    print(f"原始内容: {content[:300]}")
                    # 尝试后备方案：手动解析
                    print("尝试使用后备方案解析...")
                    key_infos = self._fallback_parse(content, chat_summary)
                    if key_infos:
                        print(f"后备方案成功提取 {len(key_infos)} 条关键信息")
                        return key_infos
                    return []
            else:
                print("LLM返回结果格式异常")
                return []
                
        except Exception as e:
            print(f"提取关键信息时出错: {str(e)}")
            return []
    
    def _fallback_parse(self, llm_response, chat_summary):
        """
        后备方案：当LLM不返回JSON时，手动从文本中提取信息
        
        Args:
            llm_response: LLM返回的文本
            chat_summary: 原始聊天总结
            
        Returns:
            list: 提取的关键信息列表
        """
        import re
        
        key_infos = []
        
        # 尝试从文本中提取关键事件（简单启发式方法）
        # 查找包含地点、动作的句子
        lines = chat_summary.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 简单规则：如果行中包含城市名或文件操作
            info = {}
            
            # 检测天气查询
            if '天气' in line:
                info['who'] = '用户'
                info['what'] = '查询天气'
                info['why'] = '了解天气情况'
                
                # 提取城市
                cities = ['北京', '上海', '广州', '深圳', '杭州', '成都']
                for city in cities:
                    if city in line:
                        info['where'] = city
                        break
                
                if 'where' not in info:
                    info['where'] = '未提及'
                
                info['when'] = '今天'
                key_infos.append(info)
            
            # 检测文件操作
            elif '文件' in line or ('创建' in line and '.txt' in line) or '删除' in line:
                info['who'] = '用户'
                
                if '创建' in line:
                    info['what'] = '创建文件'
                elif '删除' in line:
                    info['what'] = '删除文件'
                elif '询问' in line or '内容' in line:
                    info['what'] = '查询文件内容'
                else:
                    info['what'] = '文件操作'
                
                info['where'] = '当前目录'
                info['when'] = '未提及'
                info['why'] = '未提及'
                key_infos.append(info)
        
        return key_infos if key_infos else None
    
    def save_to_log(self, key_infos):
        """
        将关键信息增量保存到日志文件
        
        Args:
            key_infos: 关键信息列表
        """
        if not key_infos:
            print("没有需要保存的信息")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}]\n")
            f.write("-" * 80 + "\n")
            
            for i, info in enumerate(key_infos, 1):
                who = info.get('who', '未提及')
                what = info.get('what', '未提及')
                when = info.get('when', '未提及')
                where = info.get('where', '未提及')
                why = info.get('why', '未提及')
                
                f.write(f"记录 {i}:\n")
                f.write(f"  Who   : {who}\n")
                f.write(f"  What  : {what}\n")
                f.write(f"  When  : {when}\n")
                f.write(f"  Where : {where}\n")
                f.write(f"  Why   : {why}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
        
        print(f"已保存 {len(key_infos)} 条记录到 {self.log_file_path}")
    
    def search_logs(self, query):
        """
        搜索日志文件
        
        Args:
            query: 搜索关键词
            
        Returns:
            str: 匹配的记录内容
        """
        if not os.path.exists(self.log_file_path):
            return "日志文件不存在"
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单关键词匹配
        lines = content.split('\n')
        matched_records = []
        current_record = []
        in_record = False
        
        for line in lines:
            if line.startswith('[') and line.endswith(']'):
                # 新的时间戳，开始新记录
                if current_record and any(query.lower() in l.lower() for l in current_record):
                    matched_records.append('\n'.join(current_record))
                current_record = [line]
                in_record = True
            elif line.startswith('=' * 10):
                # 记录结束
                if current_record and any(query.lower() in l.lower() for l in current_record):
                    matched_records.append('\n'.join(current_record))
                current_record = []
                in_record = False
            elif in_record:
                current_record.append(line)
        
        # 检查最后一条记录
        if current_record and any(query.lower() in l.lower() for l in current_record):
            matched_records.append('\n'.join(current_record))
        
        if matched_records:
            result = f"找到 {len(matched_records)} 条相关记录:\n\n"
            result += "\n".join(matched_records)
            return result
        else:
            return f"未找到与 '{query}' 相关的记录"
    
    def get_recent_logs(self, count=5):
        """
        获取最近的日志记录
        
        Args:
            count: 返回记录数量
            
        Returns:
            str: 最近的日志内容
        """
        if not os.path.exists(self.log_file_path):
            return "日志文件不存在"
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割所有记录
        records = content.split("=" * 80)
        
        # 返回最近的count条记录
        recent = records[-(count+1):]  # +1 因为第一个可能是空字符串
        recent = [r.strip() for r in recent if r.strip()]
        
        if recent:
            return "\n\n" + ("=" * 80 + "\n\n").join(recent)
        else:
            return "暂无日志记录"


def extract_key_info_from_summary(env_vars, chat_summary):
    """
    从聊天总结中提取关键信息（供外部调用）
    
    Args:
        env_vars: 环境变量字典
        chat_summary: 聊天总结文本
        
    Returns:
        list: 提取的关键信息列表
    """
    manager = ChatLogManager()
    return manager.extract_key_info(env_vars, chat_summary)


def search_chat_history(env_vars, user_query, log_manager):
    """
    搜索聊天历史并生成回复
    
    Args:
        env_vars: 环境变量字典
        user_query: 用户查询
        log_manager: 日志管理器实例
        
    Returns:
        str: 搜索结果和回复
    """
    # 提取搜索关键词
    if user_query.startswith('/search'):
        search_keyword = user_query[7:].strip()
    else:
        search_keyword = user_query
    
    print(f"\n搜索聊天历史: '{search_keyword}'")
    
    # 搜索日志
    search_result = log_manager.search_logs(search_keyword)
    
    print(f"搜索结果:\n{search_result}\n")
    
    # 调用LLM生成回复
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    system_prompt = """你是一个智能助手，可以帮助用户搜索和回顾聊天历史。
根据提供的搜索结果，用友好、清晰的语言回答用户的问题。
如果搜索结果为空，礼貌地告知用户没有找到相关记录。"""
    
    user_prompt = f"用户问题: {user_query}\n\n搜索结果:\n{search_result}\n\n请根据以上信息回答用户。"
    
    try:
        result = call_llm(base_url, model, api_key, user_prompt)
        
        if result and 'choices' in result and len(result['choices']) > 0:
            reply = result['choices'][0].get('message', {}).get('content', '')
            return reply
        else:
            return "抱歉，无法生成回复"
    except Exception as e:
        return f"搜索时出错: {str(e)}"
