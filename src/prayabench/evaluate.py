"""Inspect geometry without executing generated code. No opaque total score."""
from collections import Counter,deque
import hashlib
import json
from pathlib import Path
from . import __version__
from .scene import validate_cells,load_json,state_parts,name,full_block,flush_top,passable,PALETTE,VEC
from .tasks import verify_run

def assess(fixture,submission):
    edits=validate_cells(submission);base=validate_cells({'cells':fixture['cells']})
    grid=base|edits;protected={tuple(p) for p in fixture['protected']};issues=[]
    def block(pos):return grid.get(pos,[0,0,0,'air'])[3]
    def add(code,pos,detail,severity='error'):issues.append({'code':code,'at':list(pos),'detail':detail,'severity':severity})
    for pos,c in edits.items():
        x,y,z=pos;b,p=state_parts(c[3])
        if not(0<=x<=23 and 0<=y<=17 and 0<=z<=21):add('out_of_bounds',pos,'Outside the declared scene.')
        if pos in protected and (c[3]!=block_from(base,pos) or c[4]!=base.get(pos,[0]*4+[None])[4]):add('protected_change',pos,'Changed protected terrain or historic architecture.')
        if b not in PALETTE:add('unsupported_block',pos,f'{b} is outside this evaluator’s declared palette; not a complete game registry verdict.')
        if p.get('facing') and p['facing'] not in VEC:add('invalid_facing',pos,'Unknown facing direction.')
        if b=='air':continue
        below=block((x,y-1,z))
        if 'wall_sign' in b or b=='player_wall_head' or b in ('wall_torch','redstone_wall_torch'):
            d=VEC.get(p.get('facing','north'),(0,0,-1));back=block((x-d[0],y-d[1],z-d[2]))
            if not full_block(back):add('unsupported_wall_fixture',pos,f'Backing is {back}; requires a full wall face.')
        if b=='player_head':
            if c[6]=='mailbox_orange':
                if name(below) not in ('iron_bars','iron_chain','chain','glass_pane') and not name(below).endswith('_stained_glass_pane'):add('mailbox_plinth',pos,'Mailbox needs a slender bar, chain or glass post.')
            elif not flush_top(below):add('floating_prop',pos,f'Prop does not sit flush on {below}.')
        if b.endswith('_sign') and 'wall' not in b:
            if c[5] not in ('road-sign','traffic-sign'):add('standing_sign',pos,'Non-traffic signs should mount on architecture.','warn')
        if b.endswith('_sign') and not any(c[4] or []):add('blank_sign',pos,'No visible sign text.','warn')
        if b.endswith('_door'):
            lower=p.get('half','lower')=='lower';other=(x,y+(1 if lower else -1),z);ob,op=state_parts(block(other))
            if ob!=b or op.get('half')!=('upper' if lower else 'lower'):add('unpaired_door',pos,'Door is missing its matching half.')
        if b=='end_rod':
            d=VEC.get(p.get('facing','up'),(0,1,0));support=block((x-d[0],y-d[1],z-d[2]))
            if name(support)=='air':add('unsupported_rod',pos,'No attachment at the rod base.')
    # Half-block-height approximation. Sources are ONLY the original street rows;
    # interior paving cannot seed a disconnected building as reachable.
    levels={}
    for x in range(24):
        for z in range(22):
            out=[]
            for y in range(18):
                here=block((x,y,z));b,p=state_parts(here)
                if passable(here) and passable(block((x,y+1,z))) and flush_top(block((x,y-1,z))):out.append(2*y)
                elif (b.endswith('_stairs') or b.endswith('_slab') and p.get('type','bottom')=='bottom') and passable(block((x,y+1,z))) and passable(block((x,y+2,z))):out.append(2*y+(2 if b.endswith('_stairs') else 1))
            levels[x,z]=out
    seen={(x,z,h) for (x,z),hs in levels.items() if z<=4 for h in hs};q=deque(seen)
    while q:
        x,z,h=q.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for hh in levels.get((x+dx,z+dz),[]):
                p=(x+dx,z+dz,hh)
                if abs(hh-h)<=2 and p not in seen:seen.add(p);q.append(p)
    doors=[]
    for (x,y,z),c in grid.items():
        b,p=state_parts(c[3])
        if b.endswith('_door') and p.get('half','lower')=='lower':
            doors.append([x,y,z])
            if (x,z,2*y) not in seen:add('unreachable_door',(x,y,z),'No approximate route from protected street; one-block jumps allowed.')
    required_doors=fixture['task']!='pocket-park'
    if required_doors and not doors:add('missing_door',(0,0,0),'Task requires a building entrance.')
    return {'schema_version':1,'evaluator_version':__version__,'task':fixture['task'],
        'edited_cells':len(edits),'issues':issues,'counts':dict(Counter(i['code'] for i in issues)),
        'doors':doors,'signs':[{'at':list(p),'text':c[4]} for p,c in edits.items() if c[4] is not None],
        'props':[{'at':list(p),'asset':c[6]} for p,c in edits.items() if c[6]],
        'review_status':'Human visual review required',
        'limitations':['Not a game physics engine or accessibility certification.',
            'Supported palette is a rendering vocabulary, not a complete Minecraft registry.',
            'No total score: inspect task completion, geometry and visual quality separately.',
            'A clean issue list does not prove a complete or attractive build.']}

def block_from(grid,pos):return grid.get(pos,[0,0,0,'air'])[3]

def evaluate(run,build,out):
    fixture=verify_run(run);submission=load_json(build);report=assess(fixture,submission)
    report['submission_sha256']=hashlib.sha256(Path(build).read_bytes()).hexdigest()
    report['evaluator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(out).write_text(json.dumps(report,indent=2,ensure_ascii=False))
    return report
