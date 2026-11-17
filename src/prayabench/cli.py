import argparse
import json
from pathlib import Path

from .scene import PALETTE, load_json
from .tasks import SCALES, TASK_SPECS, TASKS, init_run, init_suite


def main() -> None:
    p = argparse.ArgumentParser(prog='prayabench', description='A visual benchmark for AI building in Minecraft')
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('tasks')
    a.add_argument('--scale', choices=SCALES)
    a.add_argument('--category')
    a.add_argument('--json', action='store_true')
    sub.add_parser('palette')
    a = sub.add_parser('init')
    a.add_argument('directory')
    a.add_argument('--task', choices=TASKS, default='sloped-cafe')
    a = sub.add_parser('init-suite')
    a.add_argument('directory')
    a.add_argument('--scale', choices=SCALES)
    a.add_argument('--category')
    a = sub.add_parser('demo')
    a.add_argument('directory')
    a = sub.add_parser('evaluate')
    a.add_argument('run')
    a.add_argument('build')
    a.add_argument('--out', required=True)
    a = sub.add_parser('summary')
    a.add_argument('reports', nargs='+')
    a.add_argument('--out')
    a = sub.add_parser('compare')
    a.add_argument('run')
    a.add_argument('builds', nargs='+')
    a.add_argument('--out', required=True)
    a.add_argument('--named', action='store_true')
    a.add_argument('--seed', type=int, default=42)
    a = sub.add_parser('compile')
    a.add_argument('run')
    a.add_argument('source')
    a.add_argument('--out', required=True)
    a.add_argument('--image', default='python:3.12-slim')
    a.add_argument('--diagnostic-overbudget', action='store_true')
    a = sub.add_parser('generate')
    a.add_argument('run')
    a.add_argument('--provider', choices=('codex', 'claude', 'agy'), required=True)
    a.add_argument('--model', required=True)
    a.add_argument('--out', required=True)
    a.add_argument('--effort', default='medium', choices=('low', 'medium', 'high', 'xhigh', 'max'))
    a.add_argument('--timeout', type=int, default=390)
    args = p.parse_args()
    try:
        if args.cmd == 'tasks':
            filtered = {
                k: v for k, v in TASK_SPECS.items()
                if (args.scale is None or v['scale'] == args.scale)
                and (args.category is None or v['category'] == args.category)
            }
            if args.json:
                print(json.dumps({
                    k: {
                        'scale': v['scale'],
                        'category': v['category'],
                        'bounds': v['bounds'],
                        'source_limit': v['source_limit'],
                        'terrain': v['terrain'],
                        'brief': v['brief'],
                    }
                    for k, v in filtered.items()
                }, indent=2))
            else:
                for k, v in filtered.items():
                    b = v['bounds']
                    dims = f'{b[3]+1}x{b[4]+1}x{b[5]+1}'
                    print(f'{k} [{v["scale"]} · {v["category"]} · {dims}]: {v["brief"]}')
        elif args.cmd == 'palette':
            print('\n'.join(sorted(PALETTE)))
        elif args.cmd == 'init':
            print(init_run(args.directory, args.task))
        elif args.cmd == 'init-suite':
            created = init_suite(args.directory, scale=args.scale, category=args.category)
            print(f'Initialized {len(created)} task runs in {args.directory}')
        elif args.cmd == 'demo':
            from .demo import demo
            print(demo(args.directory))
        elif args.cmd == 'evaluate':
            from .evaluate import evaluate
            result = evaluate(args.run, args.build, args.out)
            comp = result['completion']
            print(json.dumps({
                'task': result['task'],
                'scale': result['scale'],
                'edited_cells': result['edited_cells'],
                'completion': f'{comp["met_count"]}/{comp["total_count"]}',
                'complete': comp['complete'],
                'findings': result['counts'],
                'report': args.out,
            }, indent=2))
        elif args.cmd == 'summary':
            from .evaluate import summarize_reports
            named = [(Path(r).stem.removesuffix('.checks'), load_json(r)) for r in args.reports]
            summary = summarize_reports(named)
            text = json.dumps(summary, indent=2)
            if args.out:
                Path(args.out).write_text(text)
            print(text)
        elif args.cmd == 'compare':
            from .report import report
            print(report(args.run, args.builds, args.out, blind=not args.named, seed=args.seed))
        elif args.cmd == 'compile':
            from .sandbox import compile_build
            result = compile_build(args.run, args.source, args.out, args.image, diagnostic_overbudget=args.diagnostic_overbudget)
            print(f'Compiled {len(result["cells"])} cells to {args.out}')
        elif args.cmd == 'generate':
            from .providers import generate
            if not 1 <= args.timeout <= 3600:
                raise ValueError('timeout must be 1–3600 seconds')
            print(generate(args.run, args.provider, args.model, args.out, args.effort, args.timeout))
    except (ValueError, RuntimeError, OSError, KeyError) as e:
        p.exit(1, 'prayabench: ' + str(e) + '\n')


if __name__ == '__main__':
    main()
