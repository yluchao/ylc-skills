# -*- coding: utf-8 -*-
import argparse, json, os
from datetime import datetime

SKELETON = """# {feature} 学习报告（FastAPI）

## 概述
- 端点：{endpoint}
- 目标：TBD

## 架构概览
TBD

## 核心组件
<!-- COMPONENTS_START -->
<!-- COMPONENTS_END -->

## 执行流程
<!-- EXEC_FLOW_START -->
TBD
<!-- EXEC_FLOW_END -->

## 数据流
<!-- DATA_FLOW_START -->
TBD
<!-- DATA_FLOW_END -->

## 特殊机制
<!-- MECHANISMS_START -->
TBD
<!-- MECHANISMS_END -->

## 依赖项
<!-- DEPS_START -->
TBD
<!-- DEPS_END -->

## 错误处理
<!-- ERRORS_START -->
TBD
<!-- ERRORS_END -->

## 性能考虑
<!-- PERF_START -->
TBD
<!-- PERF_END -->

## 安全考虑
<!-- SECURITY_START -->
TBD
<!-- SECURITY_END -->
"""


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    ap.add_argument('--endpoint', default='')
    args = ap.parse_args()

    ensure_dir('docs')
    feature = args.feature

    report = os.path.join('docs', f'{feature}_analysis.md')
    prog = os.path.join('docs', f'{feature}_progress.json')

    with open(report, 'w', encoding='utf-8') as f:
        f.write(SKELETON.format(feature=feature, endpoint=args.endpoint))

    data = {
        'feature': feature,
        'endpoint': args.endpoint,
        'handler': None,
        'queue': [],
        'done': [],
        'chunk_seq': 0,
        'updated_at': datetime.now().astimezone().isoformat(timespec='seconds')
    }
    with open(prog, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'OK report={report} prog={prog}')


if __name__ == '__main__':
    main()
