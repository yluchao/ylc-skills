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
    meta = {
        'component': task.get('symbol') or 'component',
        'file': task.get('loc') or '',
        'purpose': [],
        'key_methods': [],
        'incoming': [],
        'outgoing': []
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f"OK meta_stub={args.out}")


if __name__ == '__main__':
    main()
