"""Small declared block palette and bounded JSON scene format; no code execution."""
import json
import re
from pathlib import Path

MAX_BYTES = 4_000_000
MAX_CELLS = 30_000
ASSETS = ('coffee_maker', 'pos_terminal', 'mailbox_orange')
WOODS = ('oak', 'spruce', 'birch', 'dark_oak', 'acacia', 'jungle', 'cherry', 'mangrove')
COLORS = ('white','light_gray','gray','black','red','orange','yellow','green','lime','blue','light_blue','cyan','purple','magenta','pink','brown')
PALETTE = set('air stone dirt grass_block podzol coarse_dirt gravel sand calcite terracotta bricks brick_wall stone_bricks smooth_stone smooth_quartz quartz_block polished_diorite polished_andesite andesite diorite polished_deepslate deepslate_tiles deepslate_bricks polished_blackstone polished_basalt iron_block iron_bars iron_chain chain glass glass_pane sea_lantern lantern soul_lantern torch wall_torch end_rod redstone_torch redstone_wall_torch redstone_lamp glowstone barrel bookshelf furnace smoker crafting_table chest cauldron water flower_pot potted_fern potted_azalea_bush potted_poppy potted_dandelion azalea flowering_azalea bush sweet_berry_bush fern short_grass tall_grass poppy dandelion cornflower azure_bluet oxeye_daisy lily_of_the_valley peony rose_bush moss_block moss_carpet player_head player_wall_head iron_door iron_trapdoor oak_leaves spruce_leaves birch_leaves azalea_leaves flowering_azalea_leaves candle cake lever stone_button polished_blackstone_button stone_pressure_plate'.split())
for wood in WOODS:
    for suffix in ('planks','log','wood','stairs','slab','fence','fence_gate','trapdoor','door','sign','wall_sign','hanging_sign','wall_hanging_sign','button','pressure_plate'):
        PALETTE.add(f'{wood}_{suffix}')
    PALETTE.update((f'stripped_{wood}_log',f'stripped_{wood}_wood'))
for color in COLORS:
    for suffix in ('concrete','terracotta','wool','carpet','stained_glass','stained_glass_pane','bed'):
        PALETTE.add(f'{color}_{suffix}')
for stone in ('stone','stone_brick','smooth_stone','quartz','smooth_quartz','brick','polished_diorite','polished_andesite','polished_deepslate','deepslate_tile','deepslate_brick','polished_blackstone','sandstone','smooth_sandstone'):
    PALETTE.add(f'{stone}_slab')
    if stone!='smooth_stone':PALETTE.add(f'{stone}_stairs')
    if stone in ('stone_brick','brick','polished_deepslate','deepslate_tile','deepslate_brick','polished_blackstone','sandstone'):PALETTE.add(f'{stone}_wall')
# Deliberately a supported rendering vocabulary, not a full game block registry.
VEC = {'north':(0,0,-1),'south':(0,0,1),'east':(1,0,0),'west':(-1,0,0),'up':(0,1,0),'down':(0,-1,0)}

def state_parts(state):
    match=re.fullmatch(r'(?:minecraft:)?([a-z0-9_]+)(?:\[([a-z0-9_=,]+)\])?',state)
    if not match:raise ValueError('malformed block state')
    props={}
    if match[2]:
        for entry in match[2].split(','):
            bits=entry.split('=')
            if len(bits)!=2 or bits[0] in props:raise ValueError('malformed or duplicate property')
            props[bits[0]]=bits[1]
    return match[1],props

def load_json(path):
    path=Path(path)
    if path.stat().st_size>MAX_BYTES:raise ValueError('input exceeds 4 MB')
    return json.loads(path.read_text())

def validate_cells(obj):
    if not isinstance(obj,dict) or not isinstance(obj.get('cells'),list):raise ValueError('expected {"cells": [...]}')
    if len(obj['cells'])>MAX_CELLS:raise ValueError('too many cells')
    out={}
    for c in obj['cells']:
        if not isinstance(c,list) or not 4<=len(c)<=7:raise ValueError('cell must have 4–7 fields')
        x,y,z,state=c[:4]
        if any(type(v)!=int or abs(v)>1024 for v in (x,y,z)):raise ValueError('coordinates must be bounded integers')
        if not isinstance(state,str) or len(state)>180:raise ValueError('invalid state')
        state_parts(state)
        lines=c[4] if len(c)>4 else None
        if lines is not None and (not isinstance(lines,list) or len(lines)>4 or any(not isinstance(s,str) or len(s)>100 for s in lines)):
            raise ValueError('sign needs at most four short strings')
        component=c[5] if len(c)>5 else ''
        if not isinstance(component,str) or len(component)>100:raise ValueError('invalid component label')
        asset=c[6] if len(c)>6 else None
        if asset is not None and asset not in ASSETS:raise ValueError('unsupported prop asset')
        out[x,y,z]=[x,y,z,state,lines,component,asset]
    return out

def name(state):return state_parts(state)[0]

def passable(state):
    b,p=state_parts(state)
    return b=='air' or b.endswith(('_door','_sign','_carpet','_button','_pressure_plate')) or b in {'short_grass','fern','poppy','dandelion','cornflower','azure_bluet','torch','wall_torch','redstone_torch'}

def full_block(state):
    b,p=state_parts(state)
    if b not in PALETTE or passable(state):return False
    if b.endswith('_slab'):return p.get('type','bottom')=='double'
    if b.endswith(('_stairs','_pane','_bars','_fence','_fence_gate','_wall','_trapdoor','_head','_bed','_leaves')):return False
    if b.startswith('potted_') or b in {'water','chain','iron_chain','lantern','soul_lantern','end_rod','flower_pot','candle','cake','azalea','flowering_azalea','bush','sweet_berry_bush','tall_grass','peony','rose_bush','lily_of_the_valley','oxeye_daisy','lever'}:return False
    return True

def flush_top(state):
    b,p=state_parts(state)
    return full_block(state) or (b.endswith('_slab') and p.get('type') in ('top','double')) or (b.endswith('_stairs') and p.get('half')=='top')
