# -*- coding: utf-8 -*-
import argparse, json
from datetime import datetime


def parse_add(s: str):
    parts = s.split(':', 2)
    if len(parts) != 3:
        raise ValueError('Expected type:symbol:loc')
    return {'type': parts[0], 'symbol': parts[1], 'loc': parts[2]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prog', required=True)
    ap.add_argument('--endpoint', default=None)
    ap.add_argument('--handler', default=None)
    ap.add_argument('--handler-loc', default=None)
    ap.add_argument('--add', action='append', default=[])
    ap.add_argument('--reset', action='store_true')
    ap.add_argument('--with-final-sections', action='store_true')
    args = ap.parse_args()

    with open(args.prog, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if args.endpoint is not None:
        data['endpoint'] = args.endpoint

    if args.handler and args.handler_loc:
        data['handler'] = {'symbol': args.handler, 'loc': args.handler_loc}

    if args.reset:
        data['queue'] = []
        data['done'] = []

    if data.get('handler'):
        h = data['handler']
        handler_task = {'type': 'handler', 'symbol': h['symbol'], 'loc': h['loc']}
        if handler_task not in data['queue'] and handler_task not in data['done']:
            data['queue'].append(handler_task)

    for item in args.add:
        task = parse_add(item)
        if task not in data['queue'] and task not in data['done']:
            data['queue'].append(task)

    if args.with_final_sections:
        finals = [
            {'type': 'section', 'symbol': 'ExecutionFlow', 'loc': ''},
            {'type': 'section', 'symbol': 'DataFlow', 'loc': ''},
            {'type': 'section', 'symbol': 'ErrorsSecurityPerf', 'loc': ''},
            {'type': 'section', 'symbol': 'Dependencies', 'loc': ''},
        ]
        for t in finals:
            if t not in data['queue'] and t not in data['done']:
                data['queue'].append(t)

    data['updated_at'] = datetime.now().astimezone().isoformat(timespec='seconds')

    with open(args.prog, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK queue={len(data['queue'])} done={len(data['done'])}")


if __name__ == '__main__':
    main()
