import argparse
import json
from pathlib import Path
from .tasks import TASKS,init_run
from .scene import PALETTE

def main():
    p=argparse.ArgumentParser(prog='prayabench',description='A visual benchmark for AI building in Minecraft')
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('tasks');sub.add_parser('palette')
    a=sub.add_parser('init');a.add_argument('directory');a.add_argument('--task',choices=TASKS,default='sloped-cafe')
    a=sub.add_parser('demo');a.add_argument('directory')
    a=sub.add_parser('evaluate');a.add_argument('run');a.add_argument('build');a.add_argument('--out',required=True)
    a=sub.add_parser('compare');a.add_argument('run');a.add_argument('builds',nargs='+');a.add_argument('--out',required=True);a.add_argument('--named',action='store_true');a.add_argument('--seed',type=int,default=42)
    a=sub.add_parser('compile');a.add_argument('run');a.add_argument('source');a.add_argument('--out',required=True);a.add_argument('--image',default='python:3.12-slim')
    a=sub.add_parser('generate');a.add_argument('run');a.add_argument('--provider',choices=('codex','claude','agy'),required=True);a.add_argument('--model',required=True);a.add_argument('--out',required=True);a.add_argument('--effort',default='medium',choices=('low','medium','high','xhigh','max'));a.add_argument('--timeout',type=int,default=390)
    args=p.parse_args()
    try:
        if args.cmd=='tasks':
            for k,v in TASKS.items():print(k+': '+v)
        elif args.cmd=='palette':print('\n'.join(sorted(PALETTE)))
        elif args.cmd=='init':print(init_run(args.directory,args.task))
        elif args.cmd=='demo':
            from .demo import demo
            print(demo(args.directory))
        elif args.cmd=='evaluate':
            from .evaluate import evaluate
            result=evaluate(args.run,args.build,args.out);print(json.dumps({'edited_cells':result['edited_cells'],'findings':result['counts'],'report':args.out},indent=2))
        elif args.cmd=='compare':
            from .report import report
            print(report(args.run,args.builds,args.out,blind=not args.named,seed=args.seed))
        elif args.cmd=='compile':
            from .sandbox import compile_build
            result=compile_build(args.run,args.source,args.out,args.image);print(f'Compiled {len(result["cells"])} cells to {args.out}')
        elif args.cmd=='generate':
            from .providers import generate
            if not 1<=args.timeout<=3600:raise ValueError('timeout must be 1–3600 seconds')
            print(generate(args.run,args.provider,args.model,args.out,args.effort,args.timeout))
    except (ValueError,RuntimeError,OSError,KeyError) as e:p.exit(1,'prayabench: '+str(e)+'\n')

if __name__=='__main__':main()
