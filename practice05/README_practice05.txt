# Practice05 - Notice Skill 实现

## 功能说明

本目录实现了 **Notice Skill**（通知撰写技能），这是一个基于 LLM 的智能通知生成工具。

### 核心特性

1. **智能部门识别**
   - 当用户未说明部门时，自动使用"XX部"作为占位符
   - 当用户明确部门时，使用该部门名称生成通知

2. **规范化通知格式**
   - 自动生成符合公司规范的通知文档
   - 包含标题、正文、注意事项、落款等完整要素
   - 使用正式、规范的公文语言

3. **灵活的调用方式**
   - 支持连接真实的 LLM 服务生成内容
   - 提供模拟模式用于快速测试和演示

## 参考资源

本实验参考了 GitHub 上的 Skill 概念：
- [karpathy-skill](https://github.com/alchaincyf/karpathy-skill) - Andrej Karpathy 的认知操作系统 Skill 实现

Skill 的核心理念是通过特定的系统提示词配置，让 LLM 以特定的角色、风格或框架来响应用户请求。

## 文件说明

- `notice_skill.py` - Notice Skill 核心实现
  - `create_notice_skill_prompt()` - 根据部门信息创建系统提示词
  - `generate_notice()` - 生成通知的主函数
  - `generate_mock_notice()` - 模拟模式下的通知生成

- `test_notice_skill.py` - 测试脚本
  - 场景1：用户不说明部门
  - 场景2：用户说明部门是"销售部"

## 测试结果

### 场景1：用户不说明部门

**用户请求**：请帮我撰写一份关于五一节放假的通知

**预期结果**：通知以"XX部通知"开头

**实际结果**：✓ 验证通过

生成的通知开头：
```
XX部通知

关于2026年五一劳动节放假安排的通知

各位同事：

根据国家法定节假日安排，结合公司实际情况，现将2026年五一劳动节放假安排通知如下：
...
```

### 场景2：用户说明部门是"销售部"

**用户请求**：我是销售部的，请帮我撰写一份关于五一节放假的通知

**预期结果**：通知以"销售部通知"开头

**实际结果**：✓ 验证通过

生成的通知开头：
```
销售部通知

关于2026年五一劳动节放假安排的通知

各位同事：

根据国家法定节假日安排，结合公司实际情况，现将2026年五一劳动节放假安排通知如下：
...
```

## 使用方法

### 1. 运行测试脚本

```bash
python practice05/test_notice_skill.py
```

测试脚本默认使用模拟模式，无需启动 LLM 服务即可验证功能。

### 2. 使用真实 LLM 服务

如果需要连接真实的 LLM 服务：

1. 确保 `.env` 文件中配置了正确的 LLM 服务地址
2. 启动 LLM 服务（如 LM Studio）
3. 修改测试脚本，将 `use_mock=True` 改为 `use_mock=False`

### 3. 在代码中使用

```python
from practice05.notice_skill import generate_notice

# 加载环境变量
env_vars = {
    'BASE_URL': 'http://127.0.0.1:1234/v1',
    'MODEL': 'qwen/qwen3-vl-4b',
    'API_KEY': 'dummy'
}

# 场景1：不指定部门
result1 = generate_notice(env_vars, "请帮我撰写五一放假通知", user_department=None)

# 场景2：指定部门
result2 = generate_notice(env_vars, "请帮我撰写五一放假通知", user_department="销售部")
```

## 技术实现

### Notice Skill 工作原理

1. **动态系统提示词生成**
   - 根据用户是否提供部门信息，生成不同的系统提示词
   - 在提示词中明确指定通知的开头格式要求

2. **LLM 调用**
   - 使用标准 HTTP 库发送请求到 LLM API
   - 传递系统提示词和用户需求

3. **结果处理**
   - 提取 LLM 返回的通知内容
   - 验证格式是否符合要求

### 关键代码

```python
def create_notice_skill_prompt(user_department=None):
    if user_department:
        department_info = f"用户所在部门：{user_department}"
        start_format = f"通知必须以'{user_department}通知'开头"
    else:
        department_info = "用户未说明所在部门"
        start_format = "通知必须以'XX部通知'开头（使用占位符表示未知部门）"
    
    system_prompt = f"""你是一个专业的公司通知撰写助手...
{department_info}
通知撰写要求：
1. {start_format}
..."""
    return system_prompt
```

## 实验总结

通过本次实验，我们成功实现了：

1. ✓ 理解了 Skill 的概念和实现方式
2. ✓ 创建了 Notice Skill，能够根据用户提供的部门信息生成不同开头的通知
3. ✓ 完成了两个测试场景的验证：
   - 用户不说明部门时，通知以"XX部通知"开头
   - 用户说明部门时，通知以对应部门名称开头
4. ✓ 提供了模拟模式，方便在无 LLM 服务环境下进行测试和演示

Notice Skill 展示了如何通过精心设计的系统提示词，引导 LLM 按照特定规则生成内容，这是构建专业 AI 应用的重要技术。
