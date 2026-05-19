"""
读书心得助手 - 基于 init-article 技能

提供交互式界面来帮助用户规划和管理读书心得写作
"""
import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "=" * 70)
    print("📖 读书心得助手 - 基于 init-article 技能")
    print("=" * 70)
    print("\n这个助手会帮您系统化地规划读书心得写作。")
    print("通过生成4个规范文档，确保写出高质量的读书心得。")
    print("\n生成的文档：")
    print("  📋 topic.md      - 主题定位：明确写什么")
    print("  🎨 voice.md      - 语气风格：确定怎么写")
    print("  📐 structure.md  - 结构框架：规划写成什么样")
    print("  ✅ check.md      - 检查清单：确保质量达标")
    print("\n特殊命令：")
    print("  /quit 或 /exit   - 退出助手")
    print("  /help            - 显示帮助")
    print("  /examples        - 显示示例")
    print("  /status          - 查看当前进度")
    print("=" * 70)


def print_examples():
    """打印示例"""
    print("\n使用示例：")
    print("-" * 70)
    examples = [
        "基本用法：",
        "  直接描述您的需求，例如：",
        "  '我想为《代码大全》写读书心得，我是大二软件工程学生'",
        "",
        "详细用法：",
        "  提供更详细的信息：",
        "  '书籍是《代码大全》，我是大二软件工程专业学生，",
        "   想写3000字以上的心得，重点讨论工程化思维'",
        "",
        "其他书籍：",
        "  • 《活着》- 文学类书籍",
        "  • 《沉思录》- 哲学类书籍",
        "  • 《算法导论》- 技术类书籍",
    ]
    for line in examples:
        print(line)
    print("-" * 70)


def collect_book_info():
    """收集书籍信息"""
    print("\n📚 第一步：收集书籍信息")
    print("-" * 70)
    
    book_name = input("1. 书名：").strip()
    if not book_name:
        return None
    
    author = input("2. 作者（可选）：").strip() or "未知"
    book_type = input("3. 书籍类型（技术/文学/哲学等）：").strip() or "技术"
    read_time = input("4. 阅读时间（如：2026年3月-4月）：").strip() or "最近"
    
    return {
        "book_name": book_name,
        "author": author,
        "book_type": book_type,
        "read_time": read_time
    }


def collect_user_info():
    """收集用户身份信息"""
    print("\n👤 第二步：收集您的身份信息")
    print("-" * 70)
    
    grade = input("1. 年级和专业（如：大二软件工程）：").strip() or "大二软件工程"
    courses = input("2. 相关课程（如：软件工程导论、数据结构）：").strip() or "软件工程相关课程"
    purpose = input("3. 写作目的（作业/分享/比赛等）：").strip() or "课程作业"
    
    return {
        "grade": grade,
        "courses": courses,
        "purpose": purpose
    }


def collect_topic_ideas():
    """收集主题想法"""
    print("\n💡 第三步：收集您的主题想法")
    print("-" * 70)
    
    print("请描述您的初步想法和感悟：")
    print("（可以包括：印象最深的观点、想讨论的内容、与专业的结合点等）")
    ideas = input("您的想法：").strip()
    
    if not ideas:
        return "暂无具体想法"
    
    return ideas


def collect_requirements():
    """收集写作要求"""
    print("\n📝 第四步：收集写作要求")
    print("-" * 70)
    
    word_count = input("1. 字数要求（如：3000字以上）：").strip() or "3000字以上"
    deadline = input("2. 截止时间（可选）：").strip() or "未指定"
    special_req = input("3. 特殊要求（可选）：").strip() or "无"
    
    return {
        "word_count": word_count,
        "deadline": deadline,
        "special_req": special_req
    }


def generate_topic_md(book_info, user_info, topic_ideas, requirements):
    """生成 topic.md"""
    print("\n" + "=" * 70)
    print("📋 正在生成 topic.md（主题定位文档）...")
    print("=" * 70)
    
    content = f"""# 读书心得主题文档

## 书籍信息

- **书名**：《{book_info['book_name']}》
- **作者**：{book_info['author']}
- **书籍类型**：{book_info['book_type']}
- **阅读时间**：{book_info['read_time']}

## 读者身份

- **年级专业**：{user_info['grade']}
- **相关课程**：{user_info['courses']}
- **写作目的**：{user_info['purpose']}
- **字数要求**：{requirements['word_count']}

## 核心主题

### 主题1：{topic_ideas[:50]}...
- 个人理解和感悟
- 与专业的结合点
- 实践案例

（注：这里需要根据您的具体想法进一步细化主题）

## 与专业的结合点

1. **专业知识应用**
   - 书中内容与课堂知识的联系
   - 理论到实践的转化

2. **技能提升**
   - 通过阅读获得的技能
   - 如何在项目中应用

## 个人感悟方向

- 阅读前后的认知变化
- 对自己学习/工作的反思
- 对未来发展的指导意义

## 预期结构

- 引言：为什么读这本书（约300字）
- 主体部分：核心主题讨论（每部分约600字）
- 实践应用：如何应用所学知识（约400字）
- 总结：收获与展望（约300字）

---

**注意事项**：
- 避免泛泛而谈，每个观点都要有具体例子
- 结合自己的经历，体现真实性
- 适当引用书中原文，但要注明页码
"""
    
    # 保存到文件
    with open('topic.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ topic.md 已生成并保存到项目根目录")
    print("\n内容预览：")
    print("-" * 70)
    print(content[:500] + "...")
    print("-" * 70)
    
    return content


def generate_voice_md():
    """生成 voice.md"""
    print("\n" + "=" * 70)
    print("🎨 正在生成 voice.md（语气风格文档）...")
    print("=" * 70)
    
    content = """# 读书心得语气风格文档

## 目标读者

- **主要读者**：课程授课教师
- **次要读者**：同专业的同学
- **阅读场景**：课程作业提交、读书分享会

## 文章语气

### 整体基调：正式但带有个人色彩

✅ **推荐表达**：
- "在阅读这本书之前，我一直认为……"
- "通过实践我发现……"
- "这让我联想到在课程中……"
- "我尝试将这个理念应用到项目中……"

❌ **避免表达**：
- "综上所述"、"总而言之"（过于套路）
- "毋庸置疑"、"显而易见"（过于绝对）
- "笔者"、"本人"（过于正式）
- "超级棒"、"绝绝子"（过于口语化）

## 语言风格特点

### 1. 学术性与通俗性的平衡

**专业术语使用**：
- ✅ 正确使用专业术语
- ✅ 首次出现时简要解释
- ❌ 避免堆砌术语而不解释

**句式结构**：
- 长短句结合，避免过长复合句
- 适当使用设问句增强互动感

### 2. 个人化的表达方式

**第一人称叙述**：
- 多用"我"来表达个人观点和体验
- 体现真实的阅读感受和思考过程

**真实案例支撑**：
- 引用自己的学习/编程经历
- 描述具体的问题和解决过程

## 段落和节奏

### 段落长度

- **引言段**：150-200字，简洁有力
- **主体段**：每段200-300字，一个核心观点
- **过渡段**：50-100字，承上启下
- **总结段**：200-300字，升华主题

## 常见陷阱避免

### 1. 避免流水账式复述
- ❌ "第一章讲了……第二章讲了……"
- ✅ "书中关于XX的论述，让我重新审视……"

### 2. 避免空话套话
- ❌ "这本书内容丰富，受益匪浅"
- ✅ "书中关于XX的建议，帮助我……"

### 3. 避免脱离学生身份
- ❌ 以专家口吻评判
- ✅ 以学习者角度分享成长

---

**核心原则**：真诚、具体、有思考深度，像一个真实的学生在分享自己的读书收获。
"""
    
    # 保存到文件
    with open('voice.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ voice.md 已生成并保存到项目根目录")
    print("\n内容预览：")
    print("-" * 70)
    print(content[:500] + "...")
    print("-" * 70)
    
    return content


def generate_structure_md():
    """生成 structure.md"""
    print("\n" + "=" * 70)
    print("📐 正在生成 structure.md（结构框架文档）...")
    print("=" * 70)
    
    content = """# 读书心得结构框架文档

## 整体架构

采用**"总-分-总"**的经典结构，确保逻辑清晰、层次分明。

```
引言（10%）
  ↓
主体部分（75%）
  ├─ 主题1（20%）
  ├─ 主题2（20%）
  ├─ 主题3（20%）
  └─ 主题4（15%）
  ↓
实践应用（10%）
  ↓
总结（5%）
```

## 详细结构设计（以3000字为例）

### 一、引言部分（约300字）

#### 1.1 引入背景（100字）
- 为什么选择这本书
- 阅读前的状态或困惑

#### 1.2 书籍简介（100字）
- 书名、作者、核心内容
- 在领域中的地位

#### 1.3 本文主旨（100字）
- 本文将重点讨论的内容
- 预期的收获和价值

### 二、主体部分（约2250字）

#### 主题1：核心观点一（约600字）
- 书中观点（150字）
- 个人理解（150字）
- 实际案例（200字）
- 反思总结（100字）

#### 主题2：核心观点二（约550字）
- 问题提出（100字）
- 书中方法（150字）
- 实践应用（200字）
- 心得体会（100字）

#### 主题3：核心观点三（约550字）
- 概念阐述（150字）
- 书中案例（150字）
- 个人实践（150字）
- 效果评估（100字）

#### 主题4：核心观点四（约550字）
- 理念介绍（150字）
- 技术手段（150字）
- 亲身经历（150字）
- 思维转变（100字）

### 三、实践应用部分（约300字）

#### 3.1 当前应用（150字）
- 如何在当前的学习/项目中应用
- 具体的计划和行动

#### 3.2 未来规划（150字）
- 对后续学习的指导
- 长期的实践目标

### 四、总结部分（约150字）

#### 4.1 核心收获（80字）
- 最重要的3-5个收获
- 认知的变化

#### 4.2 展望与建议（70字）
- 对其他同学的建议
- 对自己未来的期望

## 写作顺序建议

1. **先写主体部分**：从最有感触的主题开始
2. **再写实践应用**：结合当前实际情况
3. **然后写引言**：此时更清楚全文脉络
4. **最后写总结**：升华主题，呼应引言
5. **通读修改**：调整过渡，统一风格

---

**核心原则**：结构服务于内容，不要为了凑字数而冗余。
"""
    
    # 保存到文件
    with open('structure.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ structure.md 已生成并保存到项目根目录")
    print("\n内容预览：")
    print("-" * 70)
    print(content[:500] + "...")
    print("-" * 70)
    
    return content


def generate_check_md():
    """生成 check.md"""
    print("\n" + "=" * 70)
    print("✅ 正在生成 check.md（检查清单文档）...")
    print("=" * 70)
    
    content = """# 读书心得检查清单文档

## 一、内容完整性检查

### 1.1 基本要素
- [ ] 是否明确提及书名、作者？
- [ ] 是否说明了读者身份？
- [ ] 是否包含3-5个核心主题？
- [ ] 是否有具体的个人实践案例？
- [ ] 是否有阅读前后的认知对比？
- [ ] 是否有对未来学习的规划？

### 1.2 主题深度
- [ ] 每个主题是否有书中观点的引用？
- [ ] 每个主题是否有个人理解的阐释？
- [ ] 每个主题是否有实际案例的支撑？
- [ ] 是否避免了泛泛而谈的空洞论述？

### 1.3 字数要求
- [ ] 全文是否达到字数要求？
- [ ] 各部分字数是否符合结构规划？

## 二、逻辑连贯性检查

### 2.1 整体逻辑
- [ ] 引言是否清晰引出全文主题？
- [ ] 主体部分是否有清晰的逻辑递进？
- [ ] 各主题之间是否有合理的过渡？
- [ ] 总结是否呼应引言并升华主题？

### 2.2 段落内部逻辑
- [ ] 每个段落是否有明确的主题句？
- [ ] 论据是否支持论点？
- [ ] 是否有跳跃性或断裂的逻辑？

## 三、语言表达检查

### 3.1 语气风格
- [ ] 是否使用了第一人称表达个人观点？
- [ ] 语气是否正式但不僵硬？
- [ ] 是否符合学生的身份和水平？
- [ ] 是否体现了真诚的个人感悟？

### 3.2 用词准确性
- [ ] 专业术语是否使用正确？
- [ ] 首次出现的专业术语是否有解释？
- [ ] 是否避免了口语化表达？

### 3.3 避免套路化
- [ ] 是否避免了"综上所述"等套路词？
- [ ] 是否避免了空洞的赞美？
- [ ] 每句话是否有实际内容？

## 四、引用和案例检查

### 4.1 书中引用
- [ ] 直接引用是否加了引号？
- [ ] 引用后是否有自己的理解和阐释？
- [ ] 引用比例是否控制在20%以内？

### 4.2 个人案例
- [ ] 案例是否真实可信？
- [ ] 案例是否具体（有代码、有数据、有过程）？
- [ ] 是否说明了从案例中学到了什么？

## 五、格式规范检查

### 5.1 标题层级
- [ ] 是否有清晰的标题层级？
- [ ] 标题是否简洁明了？

### 5.2 段落格式
- [ ] 段落长度是否适中（150-300字）？
- [ ] 是否有适当的空行分隔？

### 5.3 标点符号
- [ ] 标点符号使用是否正确？
- [ ] 括号、引号是否成对出现？

## 六、常见错误避免

### 6.1 内容类错误
- [ ] ❌ 流水账式复述章节内容
- [ ] ❌ 脱离书本空发议论
- [ ] ❌ 编造不存在的阅读体验
- [ ] ❌ 过度引用而缺乏个人观点

### 6.2 结构类错误
- [ ] ❌ 没有清晰的段落划分
- [ ] ❌ 某个主题篇幅过长或过短
- [ ] ❌ 缺少引言或总结

### 6.3 语言类错误
- [ ] ❌ 错别字或语法错误
- [ ] ❌ 语句不通顺或歧义
- [ ] ❌ 过度使用网络流行语

## 七、最终确认

在提交之前，确认以下问题：

- [ ] 我是否诚实地表达了自己的阅读体验？
- [ ] 这篇文章是否体现了我的真实水平？
- [ ] 如果是同学读到这篇文章，是否会觉得真实可信？
- [ ] 如果老师问到文中的案例，我是否能详细说明？
- [ ] 我对这篇文章的质量是否满意？

**如果以上问题的答案都是"是"，那么可以放心提交了！**

---

**使用建议**：
1. 写作过程中可以随时对照此清单
2. 初稿完成后必须进行一次全面检查
3. 修改后再检查一次，确保问题已解决
"""
    
    # 保存到文件
    with open('check.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ check.md 已生成并保存到项目根目录")
    print("\n内容预览：")
    print("-" * 70)
    print(content[:500] + "...")
    print("-" * 70)
    
    return content


def generate_draft(topic_content, voice_content, structure_content):
    """根据3个文档生成读书心得初稿"""
    print("\n" + "=" * 70)
    print("📝 正在生成读书心得初稿...")
    print("=" * 70)
    
    # 这里可以根据topic、voice、structure生成初稿
    # 为了演示，我们生成一个模板
    content = """# 《XXX》读书心得

## 引言

（这里需要根据 topic.md 中的主题和 structure.md 的结构来撰写引言部分）

作为一名大二的软件工程专业学生，我在阅读《XXX》这本书时……

## 一、核心主题一

### 1.1 书中观点

（引用书中的核心论述）

### 1.2 个人理解

（阐述自己的理解和思考）

### 1.3 实践案例

（结合自己的学习或项目经历）

### 1.4 反思总结

（从这个主题中学到了什么）

## 二、核心主题二

（按照同样的结构展开第二个主题）

## 三、核心主题三

（按照同样的结构展开第三个主题）

## 四、实践应用

### 4.1 当前应用

（如何在当前的学习/项目中应用所学知识）

### 4.2 未来规划

（对后续学习的指导和长期目标）

## 五、总结

### 5.1 核心收获

（总结最重要的3-5个收获）

### 5.2 展望与建议

（对其他同学的建议和自己的期望）

---

**注意**：这是一个初稿模板，您需要：
1. 替换所有占位符内容为真实内容
2. 根据 topic.md 的主题填充具体内容
3. 按照 voice.md 的风格调整语气
4. 遵循 structure.md 的结构安排
5. 用 check.md 检查和完善
"""
    
    # 保存到文件
    with open('book-review-draft.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ 初稿已生成并保存到 book-review-draft.md")
    print("\n⚠️ 重要提示：")
    print("  这只是一个模板框架，您需要：")
    print("  1. 填充真实的内容和个人经历")
    print("  2. 根据4个规范文档完善文章")
    print("  3. 确保体现您的真实想法和感悟")
    print("  4. 用 check.md 进行全面检查")
    
    return content


def main():
    """主函数"""
    print_welcome()
    
    while True:
        try:
            user_input = input("\n请输入您的请求（输入 /help 查看帮助）: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("\n感谢使用，再见！👋\n")
                break
            
            if user_input.lower() == '/help':
                print_welcome()
                continue
            
            if user_input.lower() == '/examples':
                print_examples()
                continue
            
            if user_input.lower() == '/status':
                print("\n📊 当前进度：")
                print("-" * 70)
                files = ['topic.md', 'voice.md', 'structure.md', 'check.md', 'book-review-draft.md']
                for f in files:
                    exists = os.path.exists(f)
                    status = "✅ 已生成" if exists else "❌ 未生成"
                    print(f"  {f}: {status}")
                print("-" * 70)
                continue
            
            # 开始生成流程
            print("\n" + "=" * 70)
            print("🚀 开始生成读书心得规范文档")
            print("=" * 70)
            
            # 第1步：收集书籍信息
            book_info = collect_book_info()
            if not book_info:
                print("\n⚠ 未输入书名，已取消")
                continue
            
            # 第2步：收集用户信息
            user_info = collect_user_info()
            
            # 第3步：收集主题想法
            topic_ideas = collect_topic_ideas()
            
            # 第4步：收集写作要求
            requirements = collect_requirements()
            
            # 确认信息
            print("\n" + "=" * 70)
            print("📋 信息确认")
            print("=" * 70)
            print(f"书籍：《{book_info['book_name']}》 by {book_info['author']}")
            print(f"身份：{user_info['grade']}")
            print(f"目的：{user_info['purpose']}")
            print(f"字数：{requirements['word_count']}")
            print("=" * 70)
            
            confirm = input("\n确认开始生成文档？(y/n): ").strip().lower()
            if confirm != 'y':
                print("\n已取消")
                continue
            
            # 生成4个文档
            topic_content = generate_topic_md(book_info, user_info, topic_ideas, requirements)
            input("\n按回车继续生成下一个文档...")
            
            voice_content = generate_voice_md()
            input("\n按回车继续生成下一个文档...")
            
            structure_content = generate_structure_md()
            input("\n按回车继续生成最后一个文档...")
            
            check_content = generate_check_md()
            
            # 询问是否生成初稿
            print("\n" + "=" * 70)
            draft_confirm = input("是否生成读书心得初稿模板？(y/n): ").strip().lower()
            if draft_confirm == 'y':
                generate_draft(topic_content, voice_content, structure_content)
            
            # 完成
            print("\n" + "=" * 70)
            print("🎉 所有文档生成完成！")
            print("=" * 70)
            print("\n已生成的文件：")
            print("  ✅ topic.md      - 主题定位")
            print("  ✅ voice.md      - 语气风格")
            print("  ✅ structure.md  - 结构框架")
            print("  ✅ check.md      - 检查清单")
            if draft_confirm == 'y':
                print("  ✅ book-review-draft.md - 读书心得初稿模板")
            print("\n下一步：")
            print("  1. 阅读这4个文档，理解写作要求")
            if draft_confirm == 'y':
                print("  2. 在 book-review-draft.md 基础上填充真实内容")
            else:
                print("  2. 根据文档撰写您的读书心得")
            print("  3. 用 check.md 检查和完善文章")
            print("  4. 保存到您的项目目录")
            print("=" * 70)
            
        except KeyboardInterrupt:
            print("\n\n⚠ 程序被用户中断")
            print("感谢使用，再见！👋\n")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
