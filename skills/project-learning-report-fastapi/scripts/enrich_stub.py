# -*- coding: utf-8 -*-
import argparse, json, re


def block(stub: str, start: str, end: str, new_inner: str) -> str:
    if start not in stub or end not in stub:
        return stub
    pre, rest = stub.split(start, 1)
    _mid, post = rest.split(end, 1)
    return pre + start + "\n" + new_inner.rstrip() + "\n" + end + post


def fmt_purpose(purpose):
    lines = ['**用途**：']
    if not purpose:
        lines.append('- （待补充）')
    else:
        for p in purpose:
            lines.append(f'- {p}')
    return '\n'.join(lines)


def fmt_methods(methods):
    lines = ['**关键方法**：']
    if not methods:
        lines.append('- （待补充）')
    else:
        for m in methods:
            name = m.get('name','')
            loc = m.get('loc','')
            note = m.get('note','')
            suffix = f"（{note}）" if note else ''
            lines.append(f"- `{name}` — `{loc}`{suffix}")
    return '\n'.join(lines)


def fmt_calls(incoming, outgoing):
    lines = ['**调用关系**：']
    if incoming:
        lines.append('- incoming：')
        for x in incoming:
            frm = x.get('from','')
            loc = x.get('loc','')
            note = x.get('note','')
            suffix = f"（{note}）" if note else ''
            lines.append(f"  - `{frm}` — `{loc}`{suffix}")
    else:
        lines.append('- incoming：（待补充）')

    if outgoing:
        lines.append('- outgoing：')
        for x in outgoing:
            to = x.get('to','')
            loc = x.get('loc','')
            note = x.get('note','')
            suffix = f"（{note}）" if note else ''
            lines.append(f"  - `{to}` — `{loc}`{suffix}")
    else:
        lines.append('- outgoing：（待补充）')

    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    ap.add_argument('--stub', required=True)
    ap.add_argument('--meta', required=True)
    args = ap.parse_args()

    with open(args.stub, 'r', encoding='utf-8') as f:
        stub = f.read()

    with open(args.meta, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    file_loc = meta.get('file')
    if file_loc:
        stub = re.sub(r"\*\*文件\*\*：`[^`]*`", f"**文件**：`{file_loc}`", stub, count=1)

    stub = block(stub, '<!-- PURPOSE_START -->', '<!-- PURPOSE_END -->', fmt_purpose(meta.get('purpose', [])))
    stub = block(stub, '<!-- METHODS_START -->', '<!-- METHODS_END -->', fmt_methods(meta.get('key_methods', [])))
    stub = block(stub, '<!-- CALLS_START -->', '<!-- CALLS_END -->', fmt_calls(meta.get('incoming', []), meta.get('outgoing', [])))

    with open(args.stub, 'w', encoding='utf-8') as f:
        f.write(stub)

    print('OK enriched')


if __name__ == '__main__':
    main()
