# -*- coding: utf-8 -*-
import argparse, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    prog_path = os.path.join('docs', f'{args.feature}_progress.json')
    with open(prog_path, 'r', encoding='utf-8') as f:
        prog = json.load(f)

    if not prog.get('queue'):
        raise SystemExit('queue empty')

    task = prog['queue'][0]
    ttype = task.get('type')
    symbol = task.get('symbol') or 'component'
    loc = task.get('loc') or 'REPLACE_ME.py:0:0'

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    if ttype == 'section':
        md = f"""# SECTION：{symbol}

- REPLACE_ME：请生成该章节内容，遵循原报告模板要求。
- 必须包含必要的小标题与要点（视章节而定）。
"""
    else:
        md = f"""### 组件：{symbol}
**文件**：`{loc}`

<!-- PURPOSE_START -->
**用途**：
- REPLACE_ME
<!-- PURPOSE_END -->

<!-- METHODS_START -->
**关键方法**：
- REPLACE_ME — `REPLACE_ME.py:0:0`
<!-- METHODS_END -->

**关键代码片段**（≤30 行）：
```python
# REPLACE_ME
```

<!-- CALLS_START -->
**调用关系**：
- incoming：REPLACE_ME
- outgoing：REPLACE_ME
<!-- CALLS_END -->
"""

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"OK stub={args.out}")


if __name__ == '__main__':
    main()
