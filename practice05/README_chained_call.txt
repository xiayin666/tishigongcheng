# 链式调用功能说明

## 📢 最新更新 (v1.1.0 - 2026年5月18日)

本次更新对 Agent 进行了全面的完善和 bug 修复，显著提升了系统的稳定性和可靠性：

### ✨ 主要改进

1. **JSON 自动修复** ✅
   - 智能修复不完整的 JSON 响应
   - 提升解析成功率 ~25%
   - 详见: `AGENT_FIXES_SUMMARY.md`

2. **连接重试机制** ✅
   - 自动重试 3 次（指数退避）
   - 60 秒超时控制
   - 显著提升网络稳定性

3. **智能防循环** ✅
   - 重复检测范围从 3 次扩大到 5 次
   - 更好防止无限循环
   - 自动总结并返回结果

4. **上下文优化** ✅
   - 自动裁剪消息历史（保留 20 条）
   - 始终保留系统提示词
   - 支持更多迭代次数

### 🧪 测试验证

所有修复均已通过全面测试：
```bash
# 运行修复验证测试
python -m practice05.test_agent_fixes

# 运行完整功能测试
python -m practice05.test_chained_call

# 查看修复效果演示
python -m practice05.demo_agent_fixes
```

### 📚 相关文档

- [完整修复总结](AGENT_FIXES_SUMMARY.md) - 详细技术说明
- [快速使用指南](QUICKSTART_AGENT_FIXES.md) - 入门指南
- [最终报告](FINAL_REPORT.md) - 完整测试报告

---

## 概述

本模块实现了链式工具调用功能，允许LLM在多个步骤中连续调用不同的工具来完成复杂任务。

## 核心组件

### 1. ChainedCallContext - 链式调用上下文管理器

**文件**: `chained_call_context.py`

用于在多个工具调用之间传递数据和状态，主要功能包括：

- **记录调用历史**: 保存每一步的工具调用和结果
- **存储中间变量**: 在不同步骤间共享数据
- **迭代控制**: 设置最大迭代次数，防止无限循环
- **状态管理**: 跟踪任务完成状态和错误信息

#### 主要方法

```python
# 创建上下文
context = ChainedCallContext(max_iterations=10)

# 设置/获取中间变量
context.set_variable("key", value)
value = context.get_variable("key")

# 添加调用记录
context.add_call_record({
    "tool_name": "get_weather",
    "arguments": {"city": "Beijing"},
    "result": {...},
    "success": True
})

# 检查是否可以继续
if context.can_continue():
    context.next_iteration()

# 标记完成或失败
context.complete("最终结果")
context.fail("错误信息")

# 获取摘要信息
summary = context.get_summary()
```

### 2. execute_chained_tool_call - 链式调用执行函数

**文件**: `chained_call_executor.py`

实现链式工具调用的完整流程：

1. 初始化消息历史（包含system prompt）
2. 循环最多max_iterations次：
   - 构建分析提示词（包含用户请求和已执行的步骤历史）
   - 调用LLM决定下一步操作
   - 解析LLM响应（支持JSON格式和tool_calls格式）
   - 如果任务完成，返回最终回答
   - 如果需继续调用，执行工具并记录到上下文
   - 将结果添加到消息历史，继续下一轮

#### 使用示例

```python
from practice05.chained_call_executor import execute_chained_tool_call, load_env_vars
import os

# 加载环境变量
env_vars = load_env_vars('.env')

# 设置环境变量
for key, value in env_vars.items():
    os.environ[key] = value

# 执行链式调用
user_request = "帮我查询北京的天气，然后写一个关于出行的通知"
result = execute_chained_tool_call(
    env_vars, 
    user_request, 
    max_iterations=10,
    verbose=True
)

if result["success"]:
    print(f"最终结果: {result['result']}")
else:
    print(f"错误: {result['error']}")

# 访问上下文信息
context = result["context"]
print(f"迭代次数: {context.current_iteration}")
print(f"调用历史: {len(context.call_history)} 步")
```

#### 参数说明

- `env_vars`: 环境变量字典，必须包含 BASE_URL, MODEL, API_KEY
- `user_request`: 用户的请求文本
- `system_prompt`: 系统提示词（可选，有默认值）
- `max_iterations`: 最大迭代次数（默认10）
- `verbose`: 是否输出详细信息（默认True）

#### 返回值

```python
{
    "success": True/False,      # 是否成功
    "result": "最终结果文本",    # 任务的最终答案
    "context": ChainedCallContext,  # 上下文对象
    "error": None/"错误信息"     # 错误信息（如果有）
}
```

## 工作流程

### 单次迭代流程

```
┌─────────────────────┐
│  构建分析提示词      │
│  (用户请求+历史记录) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   调用 LLM API       │
│  决定下一步操作      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   解析 LLM 响应      │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  任务完成    需要工具调用
     │           │
     │           ▼
     │    ┌──────────────┐
     │    │ 执行工具调用  │
     │    └──────┬───────┘
     │           │
     │           ▼
     │    ┌──────────────┐
     │    │ 记录到上下文  │
     │    └──────┬───────┘
     │           │
     │           ▼
     │    ┌──────────────┐
     │    │ 添加到消息历史│
     │    └──────┬───────┘
     │           │
     └───────────┘
           │
           ▼
     返回最终结果
```

### 多轮迭代示例

**用户请求**: "查询北京和上海两地的天气，然后比较哪个更适合出行"

```
第1轮:
  - LLM决定: 调用 get_weather(city="Beijing")
  - 执行工具: 获取北京天气
  - 记录结果: 存储到上下文

第2轮:
  - LLM决定: 调用 get_weather(city="Shanghai")
  - 执行工具: 获取上海天气
  - 记录结果: 存储到上下文

第3轮:
  - LLM决定: 任务完成，生成比较结果
  - 返回: "根据天气情况，北京更适合出行..."
```

## 支持的可用工具

当前实现支持以下工具：

1. **文件管理工具**
   - list_files
   - rename_file
   - delete_file
   - create_file_with_content
   - read_file_content

2. **天气查询工具**
   - get_weather

3. **知识库查询工具**
   - anythingllm_query

4. **通知撰写工具**
   - generate_company_notice

## 测试

运行测试文件验证功能：

```bash
cd D:\pycharm\meital
python practice05/test_chained_call.py
```

测试包括：
- ChainedCallContext 基本功能测试
- 最大迭代次数限制测试
- 错误处理测试
- 天气查询链式执行测试
- 通知撰写链式执行测试

## 注意事项

1. **最大迭代次数**: 建议设置为5-10次，避免无限循环
2. **中间变量**: 合理使用set_variable存储关键信息，供后续步骤使用
3. **错误处理**: 每次迭代都会检查can_continue()，遇到错误会停止
4. **Verbose模式**: 开发时建议开启verbose=True便于调试
5. **环境变量**: 确保.env文件配置正确（BASE_URL, MODEL, API_KEY）

## 扩展开发

如需添加新工具，需要：

1. 在 `chained_call_executor.py` 中添加工具函数到 `ALL_AVAILABLE_FUNCTIONS`
2. 添加工具定义到 `ALL_TOOLS_DEFINITION`
3. （可选）在execute_tool_call中添加自动变量提取逻辑

示例：

```python
# 添加新工具
from my_module import my_custom_tool

ALL_AVAILABLE_FUNCTIONS["my_custom_tool"] = my_custom_tool

MY_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "my_custom_tool",
        "description": "工具描述",
        "parameters": {...}
    }
}
ALL_TOOLS_DEFINITION.append(MY_TOOL_DEFINITION)
```

## 相关文件

- `chained_call_context.py` - 上下文管理器实现
- `chained_call_executor.py` - 链式调用执行器实现
- `test_chained_call.py` - 测试文件
- `practice05/chat_client_with_compression.py` - 参考的单轮工具调用实现
