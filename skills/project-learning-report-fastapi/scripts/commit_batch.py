# -*- coding: utf-8 -*-
import argparse, json, os, re
from datetime import datetime


def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def has_real_loc(text: str) -> bool:
    if 'REPLACE_ME' in text:
        return False
    return bool(re.search(r'`[^`]+\.py:\d+:\d+`', text))


def insert_between(report: str, start: str, end: str, payload: str, mode: str='append') -> str:
    if start not in report or end not in report:
        raise ValueError(f'missing marker {start}/{end}')
    pre, rest = report.split(start, 1)
    mid, post = rest.split(end, 1)
    mid = mid.strip('\n')
    payload = payload.strip('\n')
    if mode == 'replace':
        new_mid = payload
    else:
        new_mid = (mid + "\n\n" + payload).strip() if mid and mid != 'TBD' else payload
    return pre + start + "\n" + new_mid + "\n" + end + post


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    ap.add_argument('--chunk-md', required=True)
    args = ap.parse_args()

    feature = args.feature
    report_path = os.path.join('docs', f'{feature}_analysis.md')
    prog_path = os.path.join('docs', f'{feature}_progress.json')

    prog = json.loads(read_text(prog_path))
    q = prog.get('queue') or []
    if not q:
        print('NOOP queue empty')
        return

    task = q[0]
    ttype = task.get('type','')
    symbol = task.get('symbol','')

    chunk = read_text(args.chunk_md).strip() + '\n'
    if 'REPLACE_ME' in chunk:
        raise ValueError('Chunk still contains REPLACE_ME')
    if ttype != 'section' and not has_real_loc(chunk):
        raise ValueError('Chunk must have real `path.py:line:col`')

    report = read_text(report_path)

    if ttype == 'section':
        if symbol == 'ExecutionFlow':
            report = insert_between(report, '<!-- EXEC_FLOW_START -->', '<!-- EXEC_FLOW_END -->', chunk, mode='replace')
        elif symbol == 'DataFlow':
            report = insert_between(report, '<!-- DATA_FLOW_START -->', '<!-- DATA_FLOW_END -->', chunk, mode='replace')
        elif symbol == 'ErrorsSecurityPerf':
            report = insert_between(report, '<!-- ERRORS_START -->', '<!-- ERRORS_END -->', chunk, mode='replace')
            report = insert_between(report, '<!-- PERF_START -->', '<!-- PERF_END -->', chunk, mode='replace')
            report = insert_between(report, '<!-- SECURITY_START -->', '<!-- SECURITY_END -->', chunk, mode='replace')
        elif symbol == 'Dependencies':
            report = insert_between(report, '<!-- DEPS_START -->', '<!-- DEPS_END -->', chunk, mode='replace')
        else:
            report = insert_between(report, '<!-- MECHANISMS_START -->', '<!-- MECHANISMS_END -->', chunk, mode='replace')
    else:
        report = insert_between(report, '<!-- COMPONENTS_START -->', '<!-- COMPONENTS_END -->', chunk, mode='append')

    write_text(report_path, report)

    prog['chunk_seq'] = int(prog.get('chunk_seq') or 0) + 1
    prog['queue'] = q[1:]
    done_item = dict(task)
    done_item['at'] = datetime.now().astimezone().isoformat(timespec='seconds')
    prog.setdefault('done', []).append(done_item)
    prog['updated_at'] = datetime.now().astimezone().isoformat(timespec='seconds')
    write_text(prog_path, json.dumps(prog, ensure_ascii=False, indent=2) + '\n')

    print(f"OK committed type={ttype} symbol={symbol} remaining={len(prog['queue'])}")


if __name__ == '__main__':
    main()
