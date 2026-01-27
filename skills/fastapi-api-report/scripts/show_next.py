# -*- coding: utf-8 -*-
import argparse, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feature', required=True)
    args = ap.parse_args()

    prog_path = os.path.join('docs', f'{args.feature}_progress.json')
    with open(prog_path, 'r', encoding='utf-8') as f:
        prog = json.load(f)

    q = prog.get('queue') or []
    if not q:
        print('NEXT queue empty')
        return

    task = q[0]
    print(f"NEXT type={task.get('type','')} symbol={task.get('symbol','')} loc={task.get('loc','')} remaining={len(q)-1}")


if __name__ == '__main__':
    main()
