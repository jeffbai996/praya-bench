"""Executed only inside the restricted container. This is not a host sandbox."""
import ast
import json
import sys

def compile_source(source,task):
    if len(source)>14000:raise ValueError('source exceeds 14000 characters')
    tree=ast.parse(source)
    if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef) or tree.body[0].name!='build':raise ValueError('expected only def build(...)')
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.ClassDef,ast.With,ast.Try,ast.While,ast.AsyncFunctionDef)):
            raise ValueError('unsupported construct: '+type(n).__name__)
        if isinstance(n,ast.FunctionDef) and n.decorator_list:raise ValueError('decorators forbidden')
        if isinstance(n,ast.Attribute) and n.attr.startswith('_'):raise ValueError('private attributes forbidden')
        if isinstance(n,ast.Name) and n.id.startswith('__'):raise ValueError('private names forbidden')
    cells={};writes=0
    def put(x,y,z,state,component=''):
        nonlocal writes
        writes+=1
        if writes>60000:raise ValueError('write budget exceeded')
        if any(type(v)!=int or abs(v)>1024 for v in (x,y,z)):raise ValueError('bounded integer coordinates required')
        if not isinstance(state,str) or len(state)>180:raise ValueError('state exceeds limit')
        if not isinstance(component,str) or len(component)>100:raise ValueError('component exceeds limit')
        cells[x,y,z]=[x,y,z,state,None,component,None]
        if len(cells)>30000:raise ValueError('cell budget exceeded')
    def box(x0,y0,z0,x1,y1,z1,state,component=''):
        spans=[x1-x0+1,y1-y0+1,z1-z0+1]
        if any(n<0 or n>1024 for n in spans) or spans[0]*spans[1]*spans[2]>60000:raise ValueError('box exceeds budget')
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):put(x,y,z,state,component)
    def head(x,y,z,asset,state='player_head[rotation=0]',component=''):
        if asset not in ('coffee_maker','pos_terminal','mailbox_orange'):raise ValueError('unknown asset')
        put(x,y,z,state,component);cells[x,y,z][6]=asset
    def sign(x,y,z,state,lines,component=''):
        if not isinstance(lines,list) or len(lines)>4 or any(not isinstance(s,str) or len(s)>100 for s in lines):raise ValueError('sign text exceeds limit')
        put(x,y,z,state,component);cells[x,y,z][4]=lines
    safe={'range':range,'min':min,'max':max,'abs':abs,'int':int,'len':len,'enumerate':enumerate,
          'zip':zip,'list':list,'dict':dict,'set':set,'tuple':tuple,'round':round,'sorted':sorted,'str':str}
    ns={'__builtins__':safe}
    exec(compile(tree,'submission','exec'),ns)
    ns['build'](put,box,head,sign,lambda x:2+x//8 if task=='sloped-cafe' else 2)
    return {'cells':list(cells.values())}

if __name__=='__main__':
    try:
        data=json.loads(sys.stdin.read(100000))
        output=json.dumps(compile_source(data['source'],data['task']))
        if len(output)>4_000_000:raise ValueError('output exceeds limit')
        print(output)
    except Exception as e:
        print(json.dumps({'error':str(e)[:400]}));sys.exit(1)
