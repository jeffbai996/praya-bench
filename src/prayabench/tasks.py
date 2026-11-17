"""Synthetic fixtures and task contracts. No saved-world exports, third-party textures or account context."""
import hashlib
import json
from pathlib import Path
from typing import Any

from . import __version__
from .scene import PALETTE

TASK_SPECS: dict[str, dict[str, Any]] = {
    'sloped-cafe': {
        'category': 'commercial-slope',
        'terrain': 'Lateral east-rising slope: ground(x, z) = 2 + x // 8.',
        'brief': (
            'Build an attractive one-storey coffee shop around x=2..14,z=7..17, facing north. '
            'Include a level floor, supported plinth, roof, facade depth, recessed glazing, a service counter '
            'with coffee_maker and pos_terminal props, two customer seats and a table. Connect its entrance to '
            'the sloped pavement. At x=16..22,z=7..18 add a connected pocket garden, tiered conifer, bench and '
            'mailbox_orange on a slender post.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 120,
            'reachable_doors': 1,
            'assets': ['coffee_maker', 'pos_terminal', 'mailbox_orange'],
            'signs': 1,
            'conifer_leaves': 8,
            'seating': 2,
        },
    },
    'small-house': {
        'category': 'residential-two-storey',
        'terrain': 'Flat grass plot at y=2 behind north pavement z=3..4.',
        'brief': (
            'Build a complete two-storey compact house around x=3..16,z=7..18. Include a living room, kitchen, '
            'bedroom with a paired two-cell bed, bathroom, connected interior stairs with headroom to a reachable '
            'upper floor, a roof, varied elevations, a reachable front entrance and a small planted front garden. '
            'Furnish rooms so a player can use the circulation space.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 180,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'beds': 1,
            'flora': 3,
        },
    },
    'pocket-park': {
        'category': 'landscape-civic',
        'terrain': 'Flat grass plot at y=2 behind north pavement z=3..4.',
        'brief': (
            'Build a small welcoming park at z>=5. Include a continuous path from the pavement into the park, '
            'two benches, two different believable trees including a conifer and a broadleaf tree, planted beds, '
            'a mailbox_orange on a slender post, and one informative sign mounted on a proper support. Preserve '
            'a clear walking route and avoid isolated floating fixtures.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 60,
            'reachable_doors': 0,
            'reachable_interior_cells': 12,
            'assets': ['mailbox_orange'],
            'signs': 1,
            'conifer_leaves': 8,
            'broadleaf_leaves': 8,
            'seating': 2,
            'flora': 4,
        },
    },
    'shop-renovation': {
        'category': 'adaptive-reuse',
        'terrain': 'Flat plot at y=2 with a protected historic shop shell at x=3..15, z=7..17, y=2..8.',
        'brief': (
            'Fit out the supplied older shop shell: a service counter with coffee_maker and pos_terminal props, '
            'two customer seats/table, lights and mounted hours signage. Preserve all protected original shell '
            'cells including the historic Built 2012 placard. Do not describe this as new construction. Keep the '
            'door reachable. You may add interior blocks and front/side landscaping outside x=3..15,z=7..17 but '
            'must not replace protected shell cells.'
        ),
        'extra': (
            '\nThe exact existing shell and protected cells are listed in fixture.json; the shell occupies '
            'x=3..15,z=7..17,y=2..8. Door at [8,3,7], placard at [4,5,8].\n'
        ),
        'requirements': {
            'min_edited_cells': 35,
            'reachable_doors': 1,
            'assets': ['coffee_maker', 'pos_terminal'],
            'signs': 1,
            'seating': 2,
            'lights': 2,
            'forbid_new_build_claim': True,
        },
    },
    'canal-crossing': {
        'category': 'spanning-infrastructure',
        'terrain': 'Embankments at y=3 cut by a protected stone-lined water canal at z=7..10 (water surface y=2).',
        'brief': (
            'Span the protected east-west canal (z=7..10) with a continuous walkable footbridge from the north '
            'bank (z=5..6) to the south bank (z=11..21), keeping bridge structure at y>=4 over the water channel '
            'with continuous side railings/parapets. On the south bank around x=5..17,z=13..20, build a roofed '
            'waterside tea kiosk with a reachable entrance door, service counter with coffee_maker and pos_terminal '
            'props, waterside seating, lanterns and mounted signage.'
        ),
        'extra': (
            '\nProtected zones: north road/pavement z=0..4 (all y) and the canal channel z=7..10 for y=0..3 '
            '(stone bed/walls and water at y=1..2). Do not fill the canal; span above y>=4. Both banks sit at y=3.\n'
        ),
        'requirements': {
            'min_edited_cells': 130,
            'reachable_doors': 1,
            'south_bank_door_min_z': 12,
            'assets': ['coffee_maker', 'pos_terminal'],
            'signs': 1,
            'seating': 2,
            'lights': 2,
        },
    },
    'corner-shophouse': {
        'category': 'urban-corner-mixed-use',
        'terrain': 'Dual-frontage flat corner lot at y=2; north street z=0..4 and west side lane x=0..3 are protected.',
        'brief': (
            'Build a two-storey mixed-use corner shophouse at x=4..17,z=5..17 addressing both the north main '
            'street and the west side lane. Ground floor: corner bakery/cafe with display glazing on both north '
            'and west street fronts, street entrance, counter with coffee_maker and pos_terminal props, and '
            'seating. Upper floor: reachable studio apartment with a paired two-cell bed, connected stairs with '
            'headroom, windows and roof. Add a rear/east court with mailbox_orange on a slender post.'
        ),
        'extra': (
            '\nProtected street rights-of-way: z=0..4 (north road and pavement) AND x=0..3 (west side lane and '
            'sidewalk) across all y. Build only at x>=4 and z>=5.\n'
        ),
        'requirements': {
            'min_edited_cells': 220,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'dual_frontage_glazing': True,
            'assets': ['coffee_maker', 'pos_terminal', 'mailbox_orange'],
            'signs': 1,
            'beds': 1,
        },
    },
    'party-wall-infill': {
        'category': 'zero-lot-line-infill',
        'terrain': 'Narrow urban slot x=5..16 flanked by protected neighbour party walls at x=0..4 and x=17..23 (z=5..17, y=2..10).',
        'brief': (
            'Infill the narrow urban gap x=5..16 between two protected neighbour party-wall buildings with a '
            'two-storey bookshop and upstairs reading loft. Do not modify either neighbour wall or place blind '
            'windows directly against opaque party walls; bring daylight from a recessed north street facade '
            'and a planted rear courtyard at z=17..21. Include ground-floor bookshelf stacks, checkout counter '
            'with pos_terminal, mounted shop signage, and stairs with headroom to a reachable upper reading room '
            'with seating and lights.'
        ),
        'extra': (
            '\nProtected structures: north street z=0..4 (all y), west neighbour building x=0..4,z=5..17,y=0..10, '
            'and east neighbour building x=17..23,z=5..17,y=0..10. Writable infill slot: x=5..16,z=5..21 (plus '
            'rear yard behind z>=18).\n'
        ),
        'requirements': {
            'min_edited_cells': 180,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'assets': ['pos_terminal'],
            'bookshelves': 4,
            'signs': 1,
            'seating': 2,
            'flora': 2,
            'lights': 2,
        },
    },
    'hillside-pavilion': {
        'category': 'steep-terrain-terracing',
        'terrain': '2D hillside rising south and east from y=2 at z<=5 up to y=8..9 at z>=16.',
        'brief': (
            'Build a stepped hillside route from the north pavement (z=3..4, y=2) up the steep slope to a roofed '
            'summit lookout/tea pavilion on the upper crest (z=15..20, y>=8). Retain cut/fill terrace edges with '
            'masonry walls rather than floating slabs, include a mid-slope rest landing with a bench and lanterns, '
            'mounted wayfinding/pavilion signage, conifers, and a reachable pavilion entrance door on the summit (y>=8).'
        ),
        'extra': (
            '\nTerrain varies in both x and z: call ground(x, z) to query exact surface elevation at each column '
            '(rises from y=2 at z<=5 to y=8 at x<15,z>=16 and y=9 at x>=15,z>=16).\n'
        ),
        'requirements': {
            'min_edited_cells': 140,
            'reachable_doors': 1,
            'summit_door_min_y': 8,
            'signs': 1,
            'seating': 1,
            'lights': 2,
            'conifer_leaves': 6,
        },
    },
}

TASKS: dict[str, str] = {k: v['brief'] for k, v in TASK_SPECS.items()}

CONTRACT = '''You are completing a one-pass offline Minecraft-style voxel construction benchmark.
Return ONLY Python source defining build(put, box, head, sign, ground).
No imports, tools, file access, external calls, Markdown or top-level calls.
Use loops/functions and range,min,max,abs,int,float,bool,len,sum,any,all,
enumerate,zip,reversed,list,dict,set,tuple,round,sorted,str.
Maximum source length: 14000 characters.

Coordinates: x=0..23,y=0..17,z=0..21. North=-z.
ground(x, z=5) returns the fixture terrain surface block y at (x, z); ground(x)
also works on 1D/flat plots, while 2D tasks require ground(x, z).
z=0..2 is north road; z=3..4 is north pavement. Protected street and structure
cells listed in fixture.json are immutable.
Player height is two blocks. Supply paired lower/upper halves for doors with
matching facing, and paired foot/head cells for beds.
Use supported block names from palette.txt. Standard Minecraft state syntax.

put(x,y,z,state,component=''): one block.
box(x0,y0,z0,x1,y1,z1,state,component=''): inclusive cuboid.
head(x,y,z,asset,state='player_head[rotation=0]',component=''): semantic prop;
assets: coffee_maker, pos_terminal, mailbox_orange. No external skin textures.
sign(x,y,z,state,lines,component=''): at most four short text lines.
Later writes replace earlier writes. Air explicitly removes a writable cell.

Construction rules: all fixtures have plausible supports. Place wall signs/heads
on full solid surfaces, not panes or arbitrary filler blocks. Ceiling hanging
signs attach overhead; wall hanging signs attach to side supports. Props sit
flush on counters/tables. Mailboxes use slender bars/chains/panes, not solid-block
plinths. Plant flowers/ferns/bushes on soil, grass or moss. Only road/traffic
signage stands on a ground post. Door jambs in glazed walls are full blocks.
Keep vertical lights clean and supported, or omit them. Furnish usable spaces
and treat exposed elevations intentionally; avoid blind windows against opaque
party walls. Signs need short legible business-specific text. Any Chinese script
is allowed. Preserve historic construction dates during renovations; label
renovation work separately and never claim an older shell is newly built.
No aircraft beacon is needed on these low-rise buildings.
'''


def ground_at(task: str, x: int, z: int = 5) -> int:
    if task not in TASK_SPECS:
        raise ValueError(f'unknown task: {task}')
    xc = max(0, min(23, int(x)))
    zc = max(0, min(21, int(z)))
    if task == 'sloped-cafe':
        return 2 + xc // 8
    if task == 'canal-crossing':
        return 2 if 7 <= zc <= 10 else 3
    if task == 'hillside-pavilion':
        if zc <= 5:
            return 2
        return 2 + min(6, (zc - 4) // 2) + (1 if xc >= 15 else 0)
    return 2


def ground_grid(task: str) -> list[list[int]]:
    return [[ground_at(task, x, z) for z in range(22)] for x in range(24)]


def fixture(task: str) -> dict[str, Any]:
    if task not in TASK_SPECS:
        raise ValueError('unknown task')
    spec = TASK_SPECS[task]
    cells: dict[tuple[int, int, int], list[Any]] = {}
    protected: set[tuple[int, int, int]] = set()

    def put(x: int, y: int, z: int, s: str, lines: list[str] | None = None) -> None:
        cells[x, y, z] = [x, y, z, s, lines, 'fixture', None]

    for x in range(24):
        for z in range(22):
            top = ground_at(task, x, z)
            if task == 'canal-crossing' and 7 <= z <= 10:
                put(x, 0, z, 'stone_bricks')
                put(x, 1, z, 'water')
                put(x, 2, z, 'water')
                for y in range(4):
                    protected.add((x, y, z))
            else:
                for y in range(top + 1):
                    if y == top:
                        if z < 3 or (task == 'corner-shophouse' and x < 2):
                            surf = 'gray_concrete'
                        elif z < 5 or (task == 'corner-shophouse' and x < 4):
                            surf = 'smooth_stone'
                        elif task == 'canal-crossing' and z in (6, 11):
                            surf = 'stone_bricks'
                        else:
                            surf = 'grass_block'
                    elif y < top - 1:
                        surf = 'stone'
                    else:
                        surf = 'stone_bricks' if (task == 'canal-crossing' and z in (6, 11)) else 'dirt'
                    put(x, y, z, surf)
            if z < 5 or (task == 'corner-shophouse' and x < 4):
                for y in range(18):
                    protected.add((x, y, z))

    if task == 'shop-renovation':
        for x in range(3, 16):
            for z in range(7, 18):
                put(x, 2, z, 'stone_bricks')
                put(x, 8, z, 'stone_bricks')
                if x in (3, 15) or z in (7, 17):
                    for y in range(3, 8):
                        put(x, y, z, 'white_concrete')
        for y in (3, 4):
            put(8, y, 7, f'oak_door[facing=north,half={"lower" if y == 3 else "upper"}]')
        put(4, 5, 8, 'oak_wall_sign[facing=south]', ['Built', '-----', '2012', ''])
        for pos in list(cells):
            if 3 <= pos[0] <= 15 and 7 <= pos[2] <= 17:
                protected.add(pos)
        for z in (5, 6):
            put(8, 2, z, 'smooth_stone')

    elif task == 'party-wall-infill':
        for x in range(0, 5):
            for z in range(5, 18):
                for y in range(2, 10):
                    if x in (0, 4) or z in (5, 17) or y in (2, 9):
                        put(x, y, z, 'bricks' if y < 9 else 'stone_bricks')
                if x == 4 or z in (5, 17):
                    put(x, 10, z, 'stone_brick_slab[type=bottom]')
                for y in range(0, 11):
                    protected.add((x, y, z))
        for x in range(17, 24):
            for z in range(5, 18):
                for y in range(2, 10):
                    if x in (17, 23) or z in (5, 17) or y in (2, 9):
                        put(x, y, z, 'stone_bricks' if y < 9 else 'smooth_stone')
                if x == 17 or z in (5, 17):
                    put(x, 10, z, 'smooth_stone_slab[type=bottom]')
                for y in range(0, 11):
                    protected.add((x, y, z))

    street_seeds = [
        [x, z]
        for x in range(24)
        for z in range(22)
        if z <= 4 or (task == 'corner-shophouse' and x <= 3)
    ]

    return {
        'task': task,
        'category': spec['category'],
        'bounds': [0, 0, 0, 23, 17, 21],
        'ground': ground_grid(task),
        'street_seeds': street_seeds,
        'requirements': spec['requirements'],
        'cells': list(cells.values()),
        'protected': [list(p) for p in sorted(protected)],
    }


def sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def init_run(path: str | Path, task: str) -> Path:
    if task not in TASK_SPECS:
        raise ValueError('unknown task')
    out_path = Path(path)
    out_path.mkdir(parents=True, exist_ok=False)
    f = fixture(task)
    (out_path / 'fixture.json').write_text(json.dumps(f, indent=2))
    spec = TASK_SPECS[task]
    (out_path / 'prompt.txt').write_text(CONTRACT + '\nTASK: ' + task + '\n' + spec['brief'] + spec['extra'])
    (out_path / 'palette.txt').write_text('\n'.join(sorted(PALETTE)) + '\n')
    hashes = {n: sha(out_path / n) for n in ('fixture.json', 'prompt.txt', 'palette.txt')}
    (out_path / 'manifest.json').write_text(json.dumps({
        'schema_version': 2,
        'package_version': __version__,
        'task': task,
        'category': spec['category'],
        'hashes': hashes,
        'source_limit': 14000,
        'scene_cell_limit': 30000,
    }, indent=2))
    return out_path


def verify_run(path: str | Path) -> dict[str, Any]:
    from .scene import load_json
    run_path = Path(path)
    m = load_json(run_path / 'manifest.json')
    if set(m['hashes']) != {'fixture.json', 'prompt.txt', 'palette.txt'}:
        raise ValueError('unexpected manifest inputs')
    for n, h in m['hashes'].items():
        if sha(run_path / n) != h:
            raise ValueError('frozen input changed: ' + n)
    return load_json(run_path / 'fixture.json')
