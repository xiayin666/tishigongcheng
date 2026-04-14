"""
Web版本的聊天客户端
使用Python内置的http.server模块创建简单的Web界面
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from practice02.file_tools import AVAILABLE_FUNCTIONS, TOOLS_DEFINITION


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


def call_llm_with_tools(base_url, model, api_key, messages, tools=None):
    """调用LLM API，支持工具调用"""
    from http.client import HTTPConnection
    from urllib.parse import urlparse as url_parse
    
    parsed_url = url_parse(base_url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    path = parsed_url.path + '/chat/completions'
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    
    if tools:
        payload["tools"] = tools
    
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


def execute_function_call(function_name, arguments):
    """执行函数调用"""
    if function_name not in AVAILABLE_FUNCTIONS:
        return {"error": f"未知的函数: {function_name}"}
    
    try:
        func = AVAILABLE_FUNCTIONS[function_name]
        result = func(**arguments)
        return result
    except Exception as e:
        return {"error": f"执行函数时出错: {str(e)}"}


def process_chat_message(user_input, conversation_history=None):
    """处理聊天消息"""
    if conversation_history is None:
        conversation_history = []
    
    env_vars = load_env_file('.env')
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        return {"error": "配置不完整，请检查.env文件"}
    
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

当用户请求执行文件操作或查询天气时，请使用相应的工具。"""
    }
    
    messages = [system_message] + conversation_history + [{"role": "user", "content": user_input}]
    
    # 第一次调用LLM
    response = call_llm_with_tools(base_url, model, api_key, messages, TOOLS_DEFINITION)
    
    if "error" in response:
        return response
    
    choice = response.get('choices', [{}])[0]
    message = choice.get('message', {})
    
    result = {
        "reply": "",
        "tool_calls": [],
        "updated_history": []
    }
    
    # 如果有工具调用
    if 'tool_calls' in message and message['tool_calls']:
        tool_calls = message['tool_calls']
        messages.append(message)
        
        for tool_call in tool_calls:
            tool_id = tool_call.get('id')
            function = tool_call.get('function', {})
            function_name = function.get('name')
            arguments_str = function.get('arguments', '{}')
            
            try:
                arguments = json.loads(arguments_str)
            except:
                arguments = {}
            
            # 执行函数
            tool_result = execute_function_call(function_name, arguments)
            
            # 如果是天气查询，直接格式化返回，不调用LLM
            if function_name == "get_weather":
                if tool_result.get("success"):
                    # 格式化天气数据
                    location = tool_result.get("location", {})
                    current = tool_result.get("current_weather", {})
                    forecast = tool_result.get("forecast", [])
                    
                    # 构建美观的天气报告
                    weather_report = f"以下是{location.get('city', '')}的天气预报：\n\n"
                    
                    # 当前天气
                    weather_report += f"🌤️ **当前天气** ({forecast[0]['date'] if forecast else ''})\n"
                    weather_report += f"- **温度**: {current.get('temperature', 'N/A')}，体感温度 {current.get('feels_like', 'N/A')}\n"
                    weather_report += f"- **天气状况**: {current.get('weather', 'N/A')}\n"
                    weather_report += f"- **湿度**: {current.get('humidity', 'N/A')}\n"
                    weather_report += f"- **风速**: {current.get('wind_speed', 'N/A')}\n"
                    weather_report += f"- **降水**: {current.get('precipitation', 'N/A')}\n"
                    weather_report += f"- **时段**: {current.get('is_day', 'N/A')}\n"
                    
                    # 未来预报
                    if forecast:
                        weather_report += f"\n📅 **未来几天预报**\n"
                        for i, day in enumerate(forecast):
                            if i == 0:
                                continue  # 跳过今天，已经显示过了
                            day_name = "明天" if i == 1 else "后天" if i == 2 else day['date']
                            weather_report += f"\n**{day['date']} ({day_name})**\n"
                            weather_report += f"- 天气: {day.get('weather', 'N/A')}\n"
                            weather_report += f"- 温度: {day.get('min_temp', 'N/A')} ~ {day.get('max_temp', 'N/A')}\n"
                            weather_report += f"- 降水: {day.get('precipitation', 'N/A')}\n"
                            if day.get('sunrise') and day.get('sunset'):
                                sunrise = day['sunrise'].split('T')[1] if 'T' in day['sunrise'] else day['sunrise']
                                sunset = day['sunset'].split('T')[1] if 'T' in day['sunset'] else day['sunset']
                                weather_report += f"- 日出/日落: {sunrise} / {sunset}\n"
                    
                    result["reply"] = weather_report
                else:
                    result["reply"] = f"查询天气失败: {tool_result.get('error', '未知错误')}"
                
                # 不返回 tool_calls，避免前端显示工具调用框
                result["tool_calls"] = []
                result["updated_history"] = conversation_history + [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": result["reply"]}
                ]
                return result
            
            result["tool_calls"].append({
                "function": function_name,
                "arguments": arguments,
                "result": tool_result
            })
            
            # 添加工具响应
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_id,
                "name": function_name,
                "content": json.dumps(tool_result, ensure_ascii=False)
            }
            messages.append(tool_response)
        
        # 第二次调用LLM获取最终回复
        final_response = call_llm_with_tools(base_url, model, api_key, messages, TOOLS_DEFINITION)
        
        if "error" not in final_response:
            final_choice = final_response.get('choices', [{}])[0]
            final_message = final_choice.get('message', {})
            result["reply"] = final_message.get('content', '')
    else:
        # 没有工具调用
        result["reply"] = message.get('content', '')
    
    # 更新对话历史
    result["updated_history"] = conversation_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": result["reply"]}
    ]
    
    return result


class ChatHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_html_page()
        elif parsed_path.path == '/style.css':
            self.send_css_file()
        elif parsed_path.path == '/script.js':
            self.send_js_file()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_message = data.get('message', '')
                history = data.get('history', [])
                
                result = process_chat_message(user_message, history)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404)
    
    def send_html_page(self):
        """发送HTML页面"""
        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件操作智能助手</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 文件操作智能助手</h1>
            <p>Practice02 - 工具调用示例</p>
        </header>
        
        <div class="chat-container">
            <div id="chat-messages" class="chat-messages"></div>
            
            <div class="input-area">
                <textarea id="user-input" placeholder="输入你的问题..." rows="3"></textarea>
                <button id="send-btn" onclick="sendMessage()">发送</button>
            </div>
        </div>
        
        <div class="examples">
            <h3>💡 示例问题：</h3>
            <ul>
                <li><a href="#" onclick="useExample('列出当前目录下的所有文件')">列出当前目录下的所有文件</a></li>
                <li><a href="#" onclick="useExample('在 test_dir 目录下创建一个名为 hello.txt 的文件，内容为 Hello World')">在 test_dir 创建 hello.txt 文件</a></li>
                <li><a href="#" onclick="useExample('读取 test_dir/hello.txt 的内容')">读取 test_dir/hello.txt 的内容</a></li>
                <li><a href="#" onclick="useExample('将 test_dir/hello.txt 重命名为 greeting.txt')">重命名文件</a></li>
                <li><a href="#" onclick="useExample('删除 test_dir/greeting.txt')">删除文件</a></li>
                <li><a href="#" onclick="useExample('北京今天的天气怎么样？')">🌤️ 查询北京的天气</a></li>
                <li><a href="#" onclick="useExample('上海明天会下雨吗？')">🌤️ 查询上海的天气预报</a></li>
            </ul>
        </div>
    </div>
    
    <script src="/script.js"></script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_css_file(self):
        """发送CSS文件"""
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
}

header h1 {
    font-size: 2em;
    margin-bottom: 10px;
}

header p {
    opacity: 0.9;
}

.chat-container {
    display: flex;
    flex-direction: column;
    height: 600px;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #f5f5f5;
}

.message {
    margin-bottom: 15px;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message.user {
    text-align: right;
}

.message.assistant {
    text-align: left;
}

.message-content {
    display: inline-block;
    max-width: 70%;
    padding: 12px 18px;
    border-radius: 18px;
    word-wrap: break-word;
}

.message.user .message-content {
    background: #667eea;
    color: white;
}

.message.assistant .message-content {
    background: white;
    color: #333;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.tool-calls {
    margin-top: 10px;
    padding: 10px;
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    border-radius: 5px;
    font-size: 0.9em;
}

.tool-call-item {
    margin: 5px 0;
    padding: 5px;
    background: white;
    border-radius: 3px;
}

.input-area {
    display: flex;
    padding: 20px;
    background: white;
    border-top: 1px solid #ddd;
    gap: 10px;
}

#user-input {
    flex: 1;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1em;
    resize: none;
    font-family: inherit;
}

#user-input:focus {
    outline: none;
    border-color: #667eea;
}

#send-btn {
    padding: 12px 30px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.3s;
}

#send-btn:hover {
    background: #5568d3;
}

#send-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.examples {
    padding: 20px;
    background: #f9f9f9;
    border-top: 1px solid #ddd;
}

.examples h3 {
    margin-bottom: 10px;
    color: #667eea;
}

.examples ul {
    list-style: none;
}

.examples li {
    margin: 5px 0;
}

.examples a {
    color: #667eea;
    text-decoration: none;
    cursor: pointer;
}

.examples a:hover {
    text-decoration: underline;
}

.typing {
    display: inline-block;
    padding: 12px 18px;
    background: white;
    border-radius: 18px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.typing span {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    margin: 0 2px;
    animation: typing 1.4s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/css; charset=utf-8')
        self.end_headers()
        self.wfile.write(css_content.encode('utf-8'))
    
    def send_js_file(self):
        """发送JavaScript文件"""
        js_content = """let conversationHistory = [];

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息到界面
    addMessage(message, 'user');
    input.value = '';
    
    // 显示加载动画
    showTyping();
    
    // 发送到服务器
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            history: conversationHistory
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTyping();
        
        if (data.error) {
            addMessage('错误: ' + data.error, 'assistant');
        } else {
            // 检查是否包含天气查询，如果是则不显示工具调用
            const hasWeatherQuery = data.tool_calls && data.tool_calls.some(call => call.function === 'get_weather');
            
            if (!hasWeatherQuery) {
                // 显示工具调用信息（非天气查询）
                if (data.tool_calls && data.tool_calls.length > 0) {
                    showToolCalls(data.tool_calls);
                }
            }
            
            // 显示助手回复
            addMessage(data.reply, 'assistant');
            
            // 更新对话历史
            conversationHistory = data.updated_history || conversationHistory;
        }
    })
    .catch(error => {
        hideTyping();
        addMessage('请求失败: ' + error.message, 'assistant');
    });
}

function addMessage(content, role) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    
    // 滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showToolCalls(toolCalls) {
    const messagesDiv = document.getElementById('chat-messages');
    const toolDiv = document.createElement('div');
    toolDiv.className = 'message assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const toolCallsDiv = document.createElement('div');
    toolCallsDiv.className = 'tool-calls';
    toolCallsDiv.innerHTML = '<strong>🔧 工具调用:</strong>';
    
    toolCalls.forEach(call => {
        const callDiv = document.createElement('div');
        callDiv.className = 'tool-call-item';
        callDiv.innerHTML = `
            <div><strong>函数:</strong> ${call.function}</div>
            <div><strong>参数:</strong> ${JSON.stringify(call.arguments)}</div>
            <div><strong>结果:</strong> ${JSON.stringify(call.result)}</div>
        `;
        toolCallsDiv.appendChild(callDiv);
    });
    
    contentDiv.appendChild(toolCallsDiv);
    toolDiv.appendChild(contentDiv);
    messagesDiv.appendChild(toolDiv);
    
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTyping() {
    const messagesDiv = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'typing';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    typingDiv.appendChild(contentDiv);
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    document.getElementById('send-btn').disabled = true;
}

function hideTyping() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    document.getElementById('send-btn').disabled = false;
}

function useExample(text) {
    document.getElementById('user-input').value = text;
    sendMessage();
}

// 按Enter发送（Shift+Enter换行）
document.getElementById('user-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});"""
        
        self.send_response(200)
        self.send_header('Content-type', 'application/javascript; charset=utf-8')
        self.end_headers()
        self.wfile.write(js_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[Web Server] {args[0]}")


def main():
    """启动Web服务器"""
    host = 'localhost'
    port = 8080
    
    try:
        server = HTTPServer((host, port), ChatHandler)
        print("=" * 60)
        print("🚀 Web服务器已启动！")
        print("=" * 60)
        print(f"📍 地址: http://{host}:{port}")
        print(f"🌐 在浏览器中打开上述地址即可使用")
        print("=" * 60)
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        server.server_close()
    except Exception as e:
        print(f"启动失败: {e}")


if __name__ == '__main__':
    main()
