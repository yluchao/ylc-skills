---

name: project-learning-report-fastapi

description: 生成 FastAPI 项目学习报告,接口、方法执行报告，完成后自动清理，仅保留最终报告。

allowed-tools: Read, Grep, Glob, LSP, Write, Bash

---

# FastAPI 学习报告（原模板对齐 + 分批写入 + venv 兼容 + Repo 内临时文件 + 完成后清理）

## 为什么你会遇到 “Write(/tmp/...) Error writing file”

Claude Code 的 `Write` 往往**只允许写入仓库工作区内路径**，对 `/tmp/...` 这类绝对路径可能禁止或无权限。

因此本版本将临时文件改到仓库内：`.claude/tmp/{{feature}}/chunk.md` 与 `.claude/tmp/{{feature}}/task_meta.json`。

---

## 执行前自检（必须）

> 目标：**不要假设项目一定存在 `./venv`**。
> 
> 本 SOP 支持两种方式选择 Python：
> 1) **手动覆写**：在命令前设置 `PY=/path/to/python`
> 2) **自动探测**（默认）：`./venv/bin/python` → `./.venv/bin/python` → `python3` → `python`

```bash
# 选择项目 Python 解释器（可覆写）
# - 若已显式设置 PY 且可执行，则直接使用
# - 否则按优先级自动探测
if [ -n "${PY:-}" ] && [ -x "$PY" ]; then
  :
elif [ -x "./venv/bin/python" ]; then
  PY="./venv/bin/python"
elif [ -x "./.venv/bin/python" ]; then
  PY="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PY="$(command -v python)"
else
  echo "ERROR: 找不到可用的 Python 解释器。请先创建/激活虚拟环境，或手动指定 PY=/path/to/python"
  exit 1
fi

# 自检：确保可执行
test -x "$PY" || (echo "ERROR: PY 不可执行：$PY" && exit 1)

echo "Using PY=$PY"
```

---

## 文件约定

- 最终报告：`docs/{{feature}}_analysis.md`

- 进度文件（中间）：`docs/{{feature}}_progress.json`（完成后删除）

- 临时目录（中间）：`.claude/tmp/{{feature}}/`（完成后删除）

  - `chunk.md`

  - `task_meta.json`

> 统一约定：
> - `PY`：项目 Python 解释器（**可覆写 + 自动探测**；见上方自检脚本）
> - `TMPDIR=.claude/tmp/{{feature}}`

---

## 快速流程（Claude Code 自动调度 SOP）

### 0) 一次性设置（每轮会话建议先执行）

> 执行一次即可，后续 A/B/C/D 均直接使用 `$PY`。

```bash
# 建议：复用“执行前自检（必须）”中的探测逻辑
# 若你已运行过自检且终端仍在同一会话，可跳过此段
if [ -n "${PY:-}" ] && [ -x "$PY" ]; then
  :
elif [ -x "./venv/bin/python" ]; then
  PY="./venv/bin/python"
elif [ -x "./.venv/bin/python" ]; then
  PY="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PY="$(command -v python)"
else
  echo "ERROR: 找不到可用的 Python 解释器。请先创建/激活虚拟环境，或手动指定 PY=/path/to/python"
  exit 1
fi
export PY

echo "Using PY=$PY"
```

> 手动覆写示例（当项目 Python 不在默认位置时）：
>
> ```bash
> PY="./services/api/.venv/bin/python"
> export PY
> ```

### A) 初始化（只做一次）

```bash
$PY scripts/init_report.py --feature "{{feature}}" --endpoint "{{endpoint}}"
```

### B) 生成队列（一次）

```bash
$PY scripts/set_queue.py --prog "docs/{{feature}}_progress.json"   --handler "{handler_symbol}" --handler-loc "{handler_loc}"   --add "service:{svc_symbol}:{svc_loc}"   --add "dao:{dao_symbol}:{dao_loc}"   --with-final-sections
```

### C) 批次循环（每次只做一个任务）

显示下一任务：

```bash
$PY scripts/show_next.py --feature "{{feature}}"
```

生成 chunk 骨架：

```bash
TMPDIR=.claude/tmp/{{feature}}
mkdir -p "$TMPDIR"
$PY scripts/new_chunk_stub.py --feature "{{feature}}" --out "$TMPDIR/chunk.md"
```

生成 meta JSON 骨架：

```bash
TMPDIR=.claude/tmp/{{feature}}
mkdir -p "$TMPDIR"
$PY scripts/new_meta_stub.py --feature "{{feature}}" --out "$TMPDIR/task_meta.json"
```

用 LSP/Read 填充 `$TMPDIR/task_meta.json`（Write 现在可写，因为在仓库内路径）

注入 meta 到 chunk：

```bash
TMPDIR=.claude/tmp/{{feature}}
$PY scripts/enrich_stub.py --feature "{{feature}}" --stub "$TMPDIR/chunk.md" --meta "$TMPDIR/task_meta.json"
```

用 Write 微调 `$TMPDIR/chunk.md`（补代码片段≤30行，确保无 REPLACE_ME，包含真实 `file.py:line:col`）

提交本批：

```bash
TMPDIR=.claude/tmp/{{feature}}
$PY scripts/commit_batch.py --feature "{{feature}}" --chunk-md "$TMPDIR/chunk.md"
```

### D) 完成与清理（必须）

```bash
$PY scripts/finalize_cleanup.py --feature "{{feature}}"
```

---

## 原始报告模板

- [reference/REPORT_TEMPLATE.md](reference/REPORT_TEMPLATE.md)

- 并确保所有方法/符号位置包含 `file.py:line:col`