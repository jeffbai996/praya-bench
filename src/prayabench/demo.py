"""Deterministic synthetic examples; these are NOT model benchmark results."""
import json
from pathlib import Path
from .tasks import init_run
from .report import report
from .evaluate import evaluate

def example(gabled):
    cells={}
    def put(x,y,z,state,lines=None,asset=None):cells[x,y,z]=[x,y,z,state,lines,'demo',asset]
    def box(x0,y0,z0,x1,y1,z1,state):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):put(x,y,z,state)
    box(3,2,8,13,4,17,'stone_bricks')
    box(3,5,8,13,8,17,'white_concrete' if gabled else 'bricks')
    box(4,5,9,12,8,16,'air');box(3,9,8,13,9,17,'spruce_planks')
    for x in (3,13):
        for z in range(10,16):
            for y in (6,7):put(x,y,z,'gray_stained_glass')
    for x in (5,6,10,11):
        for y in (6,7):put(x,y,8,'gray_stained_glass')
    for y,half in ((5,'lower'),(6,'upper')):put(8,y,8,f'oak_door[facing=north,half={half}]')
    box(7,4,6,9,4,7,'smooth_stone')
    for x in range(7,10):put(x,4,5,'stone_brick_stairs[facing=south]')
    for x in range(2,15):
        for z in range(7,19):
            y=10+min(x-2,14-x) if gabled else 10
            put(x,y,z,'deepslate_tile_stairs[facing='+('east' if x<8 else 'west')+']' if gabled else 'deepslate_tile_slab[type=bottom]')
            if gabled and z in (8,17) and 3<=x<=13:
                for yy in range(10,y):put(x,yy,z,'spruce_planks')
    box(4,5,14,6,5,15,'smooth_quartz')
    put(4,6,15,'player_head[rotation=0]',asset='coffee_maker');put(6,6,14,'player_head[rotation=0]',asset='pos_terminal')
    put(11,5,12,'spruce_stairs[facing=south]');put(11,5,14,'spruce_stairs[facing=north]');put(11,5,13,'oak_slab[type=top]')
    put(6,8,7,'oak_wall_sign[facing=north]',['Corner Coffee','手沖咖啡','',''])
    put(10,6,7,'oak_wall_sign[facing=north]',['Coffee & cake','Mon–Sat','08:00–17:00',''])
    put(4,6,16,'oak_wall_sign[facing=east]',['Built','-----','Demo fixture',''])
    for z in range(5,18):put(18,4,z,'smooth_stone')
    for x in range(18,21):put(x,5,11,'spruce_stairs[facing=north]')
    put(18,5,7,'iron_bars');put(18,6,7,'player_head[rotation=0]',asset='mailbox_orange')
    box(20,5,16,20,12,16,'spruce_log[axis=y]')
    for y,radius in ((9,2),(10,2),(11,1),(12,1),(13,0)):
        for x in range(20-radius,21+radius):
            for z in range(16-radius,17+radius):
                if (x,z)!=(20,16) or y==13:put(x,y,z,'spruce_leaves[persistent=true]')
    for x in (16,22):
        for z in (6,9,12):put(x,5,z,'poppy' if x==16 else 'dandelion')
    return {'cells':list(cells.values()),'provenance':'Deterministic package demo; not a model run.'}

def demo(out):
    out=Path(out);init_run(out,'sloped-cafe')
    files=[]
    for name,gable in [('reference-gable',True),('reference-flat',False)]:
        p=out/(name+'.json');p.write_text(json.dumps(example(gable),indent=2));files.append(p)
        evaluate(out,p,out/(name+'.checks.json'))
    report(out,files,out/'index.html',blind=False)
    return out/'index.html'
