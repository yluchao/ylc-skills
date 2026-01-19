# -*- coding: utf-8 -*-
import argparse, os, re, shutil


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    args = ap.parse_args()

    report = os.path.join('docs', f'{args.feature}_analysis.md')
    prog = os.path.join('docs', f'{args.feature}_progress.json')
    tmpdir = os.path.join('.claude', 'tmp', args.feature)

    if not os.path.exists(report):
        raise SystemExit('missing report')

    text = open(report, 'r', encoding='utf-8').read()
    required = ['## 概述', '## 架构概览', '## 核心组件', '## 执行流程', '## 数据流', '## 依赖项', '## 错误处理', '## 性能考虑', '## 安全考虑']
    for r in required:
        if r not in text:
            raise SystemExit(f'missing section: {r}')

    if not re.search(r'`[^`]+\.py:\d+:\d+`', text):
        raise SystemExit('missing any `file.py:line:col` location in report')

    if os.path.exists(prog):
        try:
            os.remove(prog)
        except Exception:
            pass

    if os.path.isdir(tmpdir):
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

    print(f"OK finalized report={report} (intermediate files removed)")


if __name__ == '__main__':
    main()
