# Practice04 - AnythingLLM 集成

## 功能说明

本目录在 practice03 的基础上增加了 AnythingLLM 知识库查询功能。

### 新增功能

1. **anythingllm_query 工具**
   - 使用 subprocess 模块调用 curl 命令
   - 访问 AnythingLLM API (http://localhost:3001)
   - 支持向知识库发送查询并获取基于文档的回答
   - 使用 API 密钥进行认证

2. **更新的聊天客户端**
   - 添加了 anythingllm_query 工具定义
   - 更新了系统提示词，明确何时使用该工具
   - 当用户询问公司文档、项目资料、技术文档等内容时自动使用

## 配置要求

### 1. 环境变量

确保 `.env` 文件中包含以下配置：

```env
ANYTHINGLLM_KEY=T6KJ476-2DA4NZN-J9YHTHB-YX8HTP7
```

### 2. AnythingLLM 服务

- 确保 AnythingLLM 服务正在运行 (http://localhost:3001)
- 确保已创建至少一个工作空间
- 记录工作空间的 slug 名称（默认为 "main"）

## 文件说明

- `anythingllm_tool.py` - AnythingLLM 查询工具实现
- `chat_client_with_compression.py` - 支持 AnythingLLM 的聊天客户端
- `test_anythingllm.py` - AnythingLLM 工具测试脚本

## 使用方法

### 1. 测试 AnythingLLM 工具

```bash
python practice04/test_anythingllm.py
```

注意：如果收到 "Workspace xxx is not a valid workspace" 错误，请修改测试文件中的 `workspace_slug` 参数为你实际的工作空间名称。

### 2. 运行聊天客户端

```bash
python practice04/chat_client_with_compression.py
```

### 3. 示例对话

用户可以询问：
- "我们项目的技术规范是什么？"
- "查询公司内部关于 Python 开发的文档"
- "列出当前目录下的所有文件"
- "北京今天的天气怎么样？"

系统会根据问题类型自动选择合适的工具：
- 知识库相关问题 → 使用 anythingllm_query
- 文件操作 → 使用文件管理工具
- 天气查询 → 使用 get_weather 工具

## API 端点

使用的 AnythingLLM API 端点：
- POST `/api/v1/workspace/{workspace_slug}/stream-chat`

请求体：
```json
{
  "message": "你的问题"
}
```

响应格式：
```json
{
  "textResponse": "AI 的回答",
  "sources": [...],
  ...
}
```

## 注意事项

1. 确保 AnythingLLM 服务正在运行
2. 确认工作空间名称正确
3. API 密钥必须有效
4. 网络连接正常
