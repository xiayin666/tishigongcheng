import os
from http.client import HTTPConnection
from urllib.parse import urlparse
import json


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


def call_llm(base_url, model, api_key, prompt="你好"):
    """使用标准http库调用LLM API"""
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    path = parsed_url.path + '/chat/completions'
    
    # 构建请求体
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    body = json.dumps(payload).encode('utf-8')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body)),
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # 创建HTTP连接
        conn = HTTPConnection(host, port, timeout=30)
        
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


def main():
    # 加载.env文件
    env_vars = load_env_file('.env')
    
    base_url = env_vars.get('BASE_URL')
    model = env_vars.get('MODEL')
    api_key = env_vars.get('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误: .env文件中缺少必要的配置项(BASE_URL, MODEL, API_KEY)")
        return
    
    print(f"正在连接到 LLM...")
    print(f"BASE_URL: {base_url}")
    print(f"MODEL: {model}")
    print(f"API_KEY: {api_key}")
    print("-" * 50)
    
    # 调用LLM
    result = call_llm(base_url, model, api_key, "你好，请介绍一下你自己")
    
    if result:
        print("\nLLM 响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 提取回复内容
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            print(f"\n助手回复:\n{content}")


if __name__ == '__main__':
    main()
