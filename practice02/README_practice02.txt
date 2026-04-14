Practice02 - 文件操作工具调用示例
=====================================

## 项目结构

practice02/
├── __init__.py          # Python包初始化文件
├── file_tools.py        # 5个文件操作工具函数
├── chat_client.py       # 支持工具调用的LLM聊天客户端
└── test_tools.py        # 工具功能测试脚本

## 5个文件操作工具

1. **list_files(directory)** - 列出目录下的文件
   - 返回文件名、大小、创建时间、修改时间等信息

2. **rename_file(directory, old_name, new_name)** - 重命名文件
   - 将指定目录下的文件从旧名称改为新名称

3. **delete_file(directory, filename)** - 删除文件
   - 删除指定目录下的指定文件

4. **create_file_with_content(directory, filename, content)** - 创建文件
   - 在指定目录下创建新文件并写入内容

5. **read_file_content(directory, filename)** - 读取文件
   - 读取指定目录下指定文件的内容

## 使用方法

### 1. 准备工作
确保已经配置好 .env 文件（从 env.example 复制）

### 2. 测试工具功能
运行测试脚本验证所有工具是否正常工作：
```bash
python practice02/test_tools.py
```

### 3. 运行聊天客户端
启动支持工具调用的智能助手：
```bash
python practice02/chat_client.py
```

### 4. 示例对话
你可以问助手以下问题：

- "列出当前目录下的所有文件"
- "在 test_dir 目录下创建一个名为 hello.txt 的文件，内容为 'Hello World'"
- "读取 test_dir/hello.txt 的内容"
- "将 test_dir/hello.txt 重命名为 greeting.txt"
- "删除 test_dir/greeting.txt"

## 工作原理

1. 用户输入问题
2. LLM 分析问题，决定是否需要调用工具
3. 如果需要，LLM 返回工具调用请求
4. 程序执行相应的工具函数
5. 将工具执行结果返回给 LLM
6. LLM 根据结果生成最终回复

## 技术要点

- 使用 Python 标准库 http.client 进行 HTTP 请求
- 实现了 OpenAI 兼容的工具调用协议
- 支持多轮工具调用
- 完整的错误处理和日志输出
