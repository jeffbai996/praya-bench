"""Synthetic fixtures. No saved-world exports, third-party textures or account context."""
import hashlib
import json
from pathlib import Path
from . import __version__
from .scene import PALETTE

TASKS = {
 'sloped-cafe': 'Build an attractive one-storey coffee shop around x=2..14,z=7..17, facing north. Include a level floor, supported plinth, roof, facade depth, recessed glazing, a service counter with coffee_maker and pos_terminal props, two customer seats and a table. Connect its entrance to the sloped pavement. At x=16..22,z=7..18 add a connected pocket garden, tiered conifer, bench and mailbox_orange on a slender post.',
 'small-house': 'Build a complete two-storey compact house around x=3..16,z=7..18. Include a living room, kitchen, bedroom and bathroom, connected interior stairs with headroom, a roof, varied elevations, a reachable front entrance and a small planted front garden. Furnish rooms so a player can use the circulation space.',
 'pocket-park': 'Build a small welcoming park at z>=5. Include a continuous path from the pavement, two benches, two different believable trees including a conifer, planted beds, a mailbox_orange on a slender post, and one informative sign mounted on a proper existing support. Preserve a clear walking route and avoid isolated floating fixtures.',
 'shop-renovation': 'Fit out the supplied older shop shell: a service counter with coffee_maker and pos_terminal props, two customer seats/table, lights and mounted hours signage. Preserve all protected original shell cells including the historic Built 2012 placard. Do not describe this as new construction. Keep the door reachable. You may add interior blocks and landscaping but must not replace protected shell cells.'
}
CONTRACT = '''You are completing a one-pass offline Minecraft-style voxel construction benchmark.
Return ONLY Python source defining build(put, box, head, sign, ground).
No imports, tools, file access, external calls, Markdown or top-level calls.
Use loops/functions and range,min,max,abs,int,len,enumerate,zip,list,dict,set,
tuple,round,sorted,str. Maximum source length: 14000 characters.

Coordinates: x=0..23,y=0..17,z=0..21. North=-z. Terrain top BLOCK is
ground(x)=2+x//8 on sloped-cafe, otherwise 2. Below is stone/dirt; above is air.
z=0..2 is road; z=3..4 is pavement. Those rows are immutable. Build at z>=5.
Player height is two blocks. Supply paired lower/upper halves for doors.
Use supported block names from palette.txt. Standard Minecraft state syntax.

put(x,y,z,state,component=''): one block.
box(x0,y0,z0,x1,y1,z1,state,component=''): inclusive cuboid.
head(x,y,z,asset,state='player_head[rotation=0]',component=''): semantic prop;
assets: coffee_maker, pos_terminal, mailbox_orange. No external skin textures.
sign(x,y,z,state,lines,component=''): at most four short text lines.
Later writes replace earlier writes. Air explicitly removes a writable cell.

Construction rules: all fixtures have plausible supports. Place wall signs/heads
on proper architectural surfaces, not panes or arbitrary filler blocks. Props
sit flush on counters/tables. Mailboxes use slender bars/chains, not solid-block
plinths. Only appropriate road/traffic signage stands on a post. Door jambs in
glazed walls are full blocks. Keep vertical lights clean and supported, or omit
them. Furnish usable spaces and treat rear/side elevations intentionally.
Signs need short legible business-specific text. Any Chinese script is allowed.
Preserve historic construction dates during renovations; label renovation work
separately. New construction may have a small interior Built placard.
No aircraft beacon is needed on these low-rise buildings.
'''

def fixture(task):
    if task not in TASKS:raise ValueError('unknown task')
    cells={}; protected=set()
    def put(x,y,z,s,lines=None):cells[x,y,z]=[x,y,z,s,lines,'fixture',None]
    for x in range(24):
        for z in range(22):
            top=2+x//8 if task=='sloped-cafe' else 2
            for y in range(top+1):put(x,y,z,('gray_concrete' if z<3 else 'smooth_stone' if z<5 else 'grass_block') if y==top else 'stone' if y<top-1 else 'dirt')
            if z<5:
                for y in range(18):protected.add((x,y,z))
    if task=='shop-renovation':
        for x in range(3,16):
            for z in range(7,18):
                put(x,2,z,'stone_bricks');put(x,8,z,'stone_bricks')
                if x in (3,15) or z in (7,17):
                    for y in range(3,8):put(x,y,z,'white_concrete')
        for y in (3,4):put(8,y,7,f'oak_door[facing=north,half={"lower" if y==3 else "upper"}]')
        put(4,5,8,'oak_wall_sign[facing=south]',['Built','-----','2012',''])
        for pos in cells:
            if 3<=pos[0]<=15 and 7<=pos[2]<=17:protected.add(pos)
        # Pre-existing steps through the front setback, preserving original shell.
        for z in (5,6):put(8,2,z,'smooth_stone')
    return {'task':task,'bounds':[0,0,0,23,17,21], 'cells':list(cells.values()),'protected':[list(p) for p in sorted(protected)]}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def init_run(path,task):
    path=Path(path);path.mkdir(parents=True,exist_ok=False)
    f=fixture(task)
    (path/'fixture.json').write_text(json.dumps(f,indent=2))
    extra=''
    if task=='shop-renovation':extra='\nThe exact existing shell and protected cells are listed in fixture.json; the shell occupies x=3..15,z=7..17,y=2..8. Door at [8,3,7], placard at [4,5,8].\n'
    (path/'prompt.txt').write_text(CONTRACT+'\nTASK: '+task+'\n'+TASKS[task]+extra)
    (path/'palette.txt').write_text('\n'.join(sorted(PALETTE))+'\n')
    hashes={n:sha(path/n) for n in ('fixture.json','prompt.txt','palette.txt')}
    (path/'manifest.json').write_text(json.dumps({'schema_version':1,'package_version':__version__,
        'task':task,'hashes':hashes,'source_limit':14000,'scene_cell_limit':30000},indent=2))
    return path

def verify_run(path):
    from .scene import load_json
    path=Path(path);m=load_json(path/'manifest.json')
    if set(m['hashes'])!={'fixture.json','prompt.txt','palette.txt'}:raise ValueError('unexpected manifest inputs')
    for n,h in m['hashes'].items():
        if sha(path/n)!=h:raise ValueError('frozen input changed: '+n)
    return load_json(path/'fixture.json')
