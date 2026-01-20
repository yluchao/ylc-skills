# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 **Claude Code 插件市场 (ylc-agent-skills)**，用于托管扩展 Claude Code 能力的自定义技能插件。当前包含：
- `project-learning-report-fastapi` (v0.1.7) - FastAPI 项目深度学习报告生成
- `secure-code-review` (v1.0.0) - 安全代码审查方法论

## 目录结构

```
ylc-skills/
├── .claude-plugin/
│   └── marketplace.json          # 插件注册表配置
├── skills/
│   ├── project-learning-report-fastapi/
│   │   ├── SKILL.md              # 技能定义与主文档
│   │   ├── scripts/              # Python 工作流脚本 (8个)
│   │   └── reference/            # 模板与 schema 文档
│   └── secure-code-review/
│       └── SKILL.md              # 安全代码审查技能
└── README.md                     # 项目说明
```

## 本地开发/测试

在 Claude Code 中本地安装插件：

```bash
/plugin marketplace add ./ylc-skills
/plugin install project-learning-report-fastapi@ylc-skills
/plugin install secure-code-review@ylc-skills
```

## 核心技能：project-learning-report-fastapi

### 工作原则 (LSP-first & Token 优化)

1. **LSP 优先**：所有符号定位、调用链、跳转定义优先使用 LSP 工具（`goToDefinition`, `findReferences`, `documentSymbol`, `incomingCalls`, `outgoingCalls`）。只有当 LSP 无法解析路由字符串时，才使用 Grep。

2. **最小必要读取**：对代码文件的 `Read` 操作必须来源于 LSP 或经由路由字符串映射后的精确文件路径；避免全库扫描或长篇粘贴。

3. **明确分析对象**：先从 `main.py` 获取路由前缀，再使用 LSP 定位 view、service、schema、dao 等定义。

### Python 脚本工作流

所有脚本位于 `skills/project-learning-report-fastapi/scripts/`，需要设置 `PY` 环境变量：

**Python 解释器自动探测**（按优先级）：
1. `./venv/bin/python`
2. `./.venv/bin/python`
3. `python3`
4. `python`

可通过 `PY=/path/to/python` 手动覆写。

| 脚本 | 功能 |
|------|------|
| `init_report.py` | 初始化学习报告，创建报告骨架和进度文件 |
| `set_queue.py` | 设置分析任务队列（handler、service、dao） |
| `show_next.py` | 显示队列中的下一个任务 |
| `new_chunk_stub.py` | 生成 markdown chunk 骨架 |
| `new_meta_stub.py` | 生成任务 metadata JSON 骨架 |
| `enrich_stub.py` | 将 LSP metadata 注入到 markdown chunk |
| `commit_batch.py` | 提交完成的 chunk 到最终报告 |
| `finalize_cleanup.py` | 完成后清理临时文件和进度文件 |

### 完整工作流 (SOP)

```bash
# 0. 设置 Python 解释器（每会话一次）
PY=${PY:-$(find . -maxdepth 2 -name "bin/python" -print -quit 2>/dev/null || command -v python3 || command -v python)}

# A. 初始化报告
$PY scripts/init_report.py --feature "{{feature}}" --endpoint "{{endpoint}}"

# B. 生成任务队列
$PY scripts/set_queue.py --prog "docs/{{feature}}_progress.json" --handler "{handler}:{loc}" --add "service:{svc}:{loc}" --add "dao:{dao}:{loc}" --with-final-sections

# C. 批次循环（每任务执行）
$PY scripts/show_next.py --feature "{{feature}}"           # 显示下一任务
TMPDIR=.claude/tmp/{{feature}}
mkdir -p "$TMPDIR"
$PY scripts/new_chunk_stub.py --feature "{{feature}}" --out "$TMPDIR/chunk.md"
$PY scripts/new_meta_stub.py --feature "{{feature}}" --out "$TMPDIR/task_meta.json"
# 用 LSP/Read 填充 task_meta.json
$PY scripts/enrich_stub.py --feature "{{feature}}" --stub "$TMPDIR/chunk.md" --meta "$TMPDIR/task_meta.json"
# 微调 chunk.md（补代码片段，确保无 REPLACE_ME，包含真实 file.py:line:col）
$PY scripts/commit_batch.py --feature "{{feature}}" --chunk-md "$TMPDIR/chunk.md"

# D. 完成与清理
$PY scripts/finalize_cleanup.py --feature "{{feature}}"
```

### 文件约定

- **最终报告**：`docs/{{feature}}_analysis.md`
- **进度文件**（中间）：`.claude/tmp/{{feature}}_progress.json`（完成后删除）
- **临时目录**（中间）：`.claude/tmp/{{feature}}/`（完成后删除）
  - `chunk.md` - 当前分析的 markdown 内容
  - `task_meta.json` - LSP 元数据摘要

### Metadata Schema

`task_meta.json` 结构（用于注入 LSP 信息）：

```json
{
  "component": "FlowService.execute",
  "file": "app/services/flow.py:45:2",
  "purpose": ["..."],
  "key_methods": [{"name": "...", "loc": "app/x.py:1:1", "note": "..."}],
  "incoming": [{"from": "...", "loc": "app/y.py:2:1", "note": "..."}],
  "outgoing": [{"to": "...", "loc": "app/z.py:3:1", "note": "..."}]
}
```

参考文件：`skills/project-learning-report-fastapi/reference/META_SCHEMA.md`

### 报告模板

参考：`skills/project-learning-report-fastapi/reference/REPORT_TEMPLATE.md`

报告包含以下部分：
- 概述（端点、目标）
- 架构概览
- 核心组件（COMPONENTS）
- 执行流程（EXEC_FLOW）
- 数据流（DATA_FLOW）
- 特殊机制（MECHANISMS）
- 依赖项（DEPS）
- 错误处理（ERRORS）
- 性能考虑（PERF）
- 安全考虑（SECURITY）

## 插件发布与更新

1. 更新 `marketplace.json` 中的版本号
2. 提交并推送到 GitHub
3. 插件用户可通过 `/plugin update <plugin-name>@ylc-skills` 获取更新

---

## secure-code-review 技能

安全代码审查技能用于识别代码中的安全漏洞。主要涵盖：

- **审查范围**：输入验证、输出编码、认证授权、加密和密钥管理
- **审查方法**：静态分析(SAST)、手动审查、代码模式识别
- **常见漏洞模式**：SQL 注入、XSS、命令注入、路径遍历、硬编码密钥
- **支持工具**：SonarQube、Semgrep、CodeQL
- **安全清单**：覆盖输入验证、输出编码、认证、加密、错误处理等

详细内容参考：`skills/secure-code-review/SKILL.md`