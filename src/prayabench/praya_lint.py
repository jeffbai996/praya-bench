"""Standalone MIT architectural, sign, access, massing and acceptance checks for reference builds."""
from __future__ import annotations

from collections import deque
from math import ceil
import re
from typing import Any, Callable

from .heads import BANNED_HEADS, POST_MOUNTED_ASSETS
from .scene import FLORA_SOIL, GROUND_FLORA, RAIL_BLOCKS, VEC, flush_top, full_block, name, passable, state_parts

OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east', 'up': 'down', 'down': 'up'}
FREESTANDING_SIGN_COMPS = frozenset({'road-sign', 'street-sign', 'traffic-sign'})
BUILDER_TOOLS = frozenset({'stone_axe', 'wooden_axe', 'iron_pickaxe', 'diamond_pickaxe', 'iron_axe'})

# Paved materials that qualify as finished street-to-entrance routes (grass/dirt do not).
PAVED_SURFACES = frozenset({
    'andesite', 'polished_andesite', 'stone', 'smooth_stone', 'stone_bricks', 'mossy_stone_bricks',
    'chiseled_stone_bricks', 'cobblestone', 'mossy_cobblestone', 'bricks', 'mud_bricks', 'tuff_bricks',
    'polished_tuff', 'diorite', 'polished_diorite', 'granite', 'polished_granite', 'deepslate_tiles',
    'deepslate_bricks', 'polished_deepslate', 'polished_blackstone', 'smooth_quartz', 'quartz_block',
    'quartz_bricks', 'sandstone', 'smooth_sandstone', 'gray_concrete', 'light_gray_concrete',
    'black_concrete', 'white_concrete', 'sea_lantern',
})
UNPAVED_SOIL = FLORA_SOIL | frozenset({'sand', 'red_sand', 'gravel'})

# Commercial/civic/utility tasks where vanilla `bookshelf` may not be used as interior or retail filler.
BOOKSHELF_BANNED_TASKS = frozenset({
    'sloped-cafe', 'shop-renovation', 'rowhouse-shop-conversion', 'grocery-supermarket',
    'canal-crossing', 'medical-clinic', 'utility-substation', 'elevated-rail-station',
    'transit-shelter', 'washroom-fitout', 'roof-hvac', 'civic-office-tower',
})
# Mixed-use buildings where ground-floor retail (`y <= 5`) bans `bookshelf`, while upper flats allow it.
GROUND_FLOOR_BOOKSHELF_BANNED = frozenset({'corner-shophouse', 'midrise-apartments'})

# Enclosed new-build architectural tasks subject to full massing, facade, entry & placard standards.
ENCLOSED_BUILDING_TASKS = frozenset({
    'sloped-cafe', 'small-house', 'utility-substation', 'canal-crossing',
    'corner-shophouse', 'party-wall-infill', 'hillside-pavilion', 'rowhouse-terrace',
    'medical-clinic', 'grocery-supermarket', 'elevated-rail-station',
    'midrise-apartments', 'civic-office-tower',
})

MAX_SIGN_PX = 90
MAX_HANGING_SIGN_PX = 60
_NARROW_2 = set("i!.,:;|'¡")
_NARROW_3 = set("l`")
_NARROW_4 = set("It[] ")
_NARROW_5 = set('fk<>(){}"*')
_WIDE_7 = set("@~")
_DIVIDER_RE = re.compile(r'^[-=~_]{2,16}$')
_ADDRESS_TOP_RE = re.compile(r'^\|\s*\d+[A-Za-z]?(?:\s*\|\s*\d+[A-Za-z]?)*\s*\|$')
_EXTERIOR_FORBIDDEN_RE = re.compile(
    r'(\bmax\s*occupancy\b|\bfire\s*marshal\b|\bemergency\s*exit\b|^exit$|^<\s*exit\s*>$)',
    re.IGNORECASE,
)
_OVERHANG_COMPS = frozenset({
    'roof', 'eave', 'awning', 'canopy', 'balcony', 'soffit', 'pergola', 'light', 'lights',
    'tree', 'garden', 'louvre', 'planter', 'roof-plant', 'sign', 'placard', 'relief',
})
_NOT_BEARING_SUFFIXES = (
    '_slab', '_stairs', '_trapdoor', '_pane', '_door', '_sign', '_hanging_sign',
    '_wall_hanging_sign', '_leaves', '_carpet', '_button', '_pressure_plate',
    '_bed', '_banner', '_torch', '_rail',
)


def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return 0x2E80 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF or 0xFF01 <= cp <= 0xFF60


def char_px(ch: str) -> int:
    if is_cjk(ch):
        return 9
    if ch in _NARROW_2:
        return 2
    if ch in _NARROW_3:
        return 3
    if ch in _NARROW_4:
        return 4
    if ch in _NARROW_5:
        return 5
    if ch in _WIDE_7 or ch in ('←', '→', '↑', '↓'):
        return 7
    return 6


def line_px(text: str) -> int:
    if not text:
        return 0
    return max(0, sum(char_px(c) for c in str(text)) - 1)


def is_divider(line: str) -> bool:
    return bool(_DIVIDER_RE.match((line or '').strip()))


def is_pane_or_bars(b_name: str) -> bool:
    return b_name in ('glass_pane', 'iron_bars') or b_name.endswith('_glass_pane')


def is_horiz_anchor(st: str) -> bool:
    sb = name(st)
    return full_block(st) or sb.endswith(('_stairs', '_fence', '_wall'))


def compute_walk_levels(
    block_fn: Callable[[tuple[int, int, int]], str],
    w: int,
    h: int,
    d: int,
    paved_only: bool = False,
) -> dict[tuple[int, int], list[int]]:
    """Compute standing heights in half-blocks with 1.8-block slab-aware headroom."""
    levels: dict[tuple[int, int], list[int]] = {}
    for x in range(w):
        for z in range(d):
            out: list[int] = []
            for y in range(0, h):
                support = block_fn((x, y, z))
                sb, sp = state_parts(support)
                if passable(support) or sb in ('water', 'snow') or sb.endswith((
                    '_leaves', '_pane', '_bars', '_fence', '_wall', '_head', '_bed', '_banner', '_candle',
                )) or sb in ('chain', 'iron_chain', 'lantern', 'soul_lantern', 'end_rod', 'lightning_rod', 'scaffolding') or sb.startswith('potted_'):
                    continue
                if paved_only:
                    is_paved = (
                        sb in PAVED_SURFACES
                        or sb.endswith(('_planks', '_stairs', '_slab'))
                    ) and sb not in UNPAVED_SOIL
                    if not is_paved:
                        continue
                bottom_slab = sb.endswith('_slab') and sp.get('type', 'bottom') == 'bottom'
                lv = 2 * y + (1 if bottom_slab else 2)
                clear = True
                top_check = min(h, ceil(lv / 2 + 1.8))
                for hy in range(lv // 2, top_check):
                    st = block_fn((x, hy, z))
                    if passable(st):
                        continue
                    hb, hp = state_parts(st)
                    low, high = 2 * hy, 2 * hy + 2
                    if hb.endswith('_slab'):
                        stype = hp.get('type', 'bottom')
                        if stype == 'top':
                            low += 1
                        elif stype == 'bottom':
                            high -= 1
                    if low < lv + 3.6 and high > lv:
                        clear = False
                        break
                if clear:
                    out.append(lv)
            levels[x, z] = out
    return levels


def flood_walk(
    levels: dict[tuple[int, int], list[int]],
    seed_cols: set[tuple[int, int]],
    w: int,
    d: int,
) -> set[tuple[int, int, int]]:
    seen = {(x, z, hh) for (x, z), hs in levels.items() if (x, z) in seed_cols for hh in hs}
    q = deque(seen)
    while q:
        x, z, hh = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if 0 <= nx < w and 0 <= nz < d:
                for nh in levels.get((nx, nz), ()):
                    cand = (nx, nz, nh)
                    if abs(nh - hh) <= 2 and cand not in seen:
                        seen.add(cand)
                        q.append(cand)
    return seen


def _infer_building_shell_rect(
    edits: dict[tuple[int, int, int], list[Any]],
) -> tuple[int, int, int, int, int, int] | None:
    """Infer main enclosed building envelope ``(x0, z0, x1, z1, y_low, y_high)`` from roofed wall/window cells."""
    all_ys_by_col: dict[tuple[int, int], list[int]] = {}
    for (x, y, z), c in edits.items():
        b = name(c[3])
        if b != 'air' and b not in FLORA_SOIL and b not in GROUND_FLORA and not b.endswith('_leaves'):
            all_ys_by_col.setdefault((x, z), []).append(y)

    # Keep columns belonging to an enclosed/roofed volume (excludes open-air yard fences).
    roofed_cols: set[tuple[int, int]] = set()
    for (x, z), ys in all_ys_by_col.items():
        if max(ys) - min(ys) >= 4:
            roofed_cols.add((x, z))

    wall_pts: list[tuple[int, int, int]] = []
    doors: list[tuple[int, int, int]] = []
    for (x, y, z), c in edits.items():
        b, p = state_parts(c[3])
        comp = c[5] or ''
        if b == 'air' or comp in ('garden', 'tree', 'path', 'steps', 'apron', 'kerb-break', 'bridge'):
            continue
        if b.endswith('_door') and p.get('half', 'lower') == 'lower':
            doors.append((x, y, z))
        if (x, z) not in roofed_cols:
            continue
        if full_block(c[3]) or 'glass' in b or b.endswith('_door'):
            if b not in FLORA_SOIL and b not in ('water', 'gravel', 'sand', 'red_sand') and not b.endswith('_log'):
                if y >= 3:
                    wall_pts.append((x, y, z))
    if len(wall_pts) < 16:
        return None
    if doors:
        cols = {(x, z) for x, _, z in wall_pts}
        best_comp: set[tuple[int, int]] = set()
        seen_c: set[tuple[int, int]] = set()
        for dx, _, dz in doors:
            start = next(((dx + ox, dz + oz) for ox, oz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)) if (dx + ox, dz + oz) in cols), None)
            if start is None or start in seen_c:
                continue
            comp_set = {start}
            seen_c.add(start)
            q = deque([start])
            while q:
                cx, cz = q.popleft()
                for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nb = (cx + ox, cz + oz)
                    if nb in cols and nb not in seen_c:
                        seen_c.add(nb)
                        comp_set.add(nb)
                        q.append(nb)
            if len(comp_set) > len(best_comp):
                best_comp = comp_set
        if len(best_comp) >= 12:
            wall_pts = [(x, y, z) for x, y, z in wall_pts if (x, z) in best_comp]

    col_heights: dict[tuple[int, int], int] = {}
    for x, y, z in wall_pts:
        col_heights[x, z] = col_heights.get((x, z), 0) + 1
    core_cols = [pt for pt, cnt in col_heights.items() if cnt >= 2]
    if len(core_cols) < 8:
        core_cols = list(col_heights)
    xs = [pt[0] for pt in core_cols]
    zs = [pt[1] for pt in core_cols]
    ys = [y for x, y, z in wall_pts if (x, z) in set(core_cols)]
    return (min(xs), min(zs), max(xs), max(zs), min(ys), max(ys))


def _is_interior_cell(
    pos: tuple[int, int, int],
    state: str,
    comp: str,
    shell_rect: tuple[int, int, int, int, int, int] | None,
    block_fn: Callable[[tuple[int, int, int]], str],
    h: int,
) -> bool:
    x, y, z = pos
    if comp in ('facade', 'porch', 'apron', 'garden', 'kerb-break', 'park-sign', 'street-sign', 'road-sign', 'traffic-sign'):
        return False
    if comp in ('placard', 'interior', 'pos', 'gondola'):
        # Still verify there is a ceiling/roof overhead so exterior walls labeled 'placard' don't cheat!
        has_overhead = any(
            name(block_fn((x, yy, z))) != 'air' and not name(block_fn((x, yy, z))).endswith('_leaves')
            for yy in range(y + 1, min(h, y + 10))
        )
        if has_overhead and shell_rect is not None:
            x0, z0, x1, z1, _, _ = shell_rect
            return x0 < x < x1 and z0 < z < z1
        return has_overhead
    if shell_rect is not None:
        x0, z0, x1, z1, _, _ = shell_rect
        if x <= x0 or x >= x1 or z <= z0 or z >= z1:
            return False
    return any(
        name(block_fn((x, yy, z))) != 'air' and not name(block_fn((x, yy, z))).endswith('_leaves')
        for yy in range(y + 1, min(h, y + 10))
    )


def run_praya_lints(
    *,
    task: str,
    vehicle: bool,
    reqs: dict[str, Any],
    base: dict[tuple[int, int, int], list[Any]],
    edits: dict[tuple[int, int, int], list[Any]],
    grid: dict[tuple[int, int, int], list[Any]],
    protected: set[tuple[int, int, int]],
    block_fn: Callable[[tuple[int, int, int]], str],
    levels: dict[tuple[int, int], list[int]],
    w: int,
    h: int,
    d: int,
    add: Callable[[str, tuple[int, int, int], str, str], None],
) -> dict[str, Any]:
    """Run ported Builder CAD, massing, door, sign, head, elevation & roof checks.

    Returns summary metrics consumed by ``_assess_completion``.
    """
    shell_rect = None if vehicle else _infer_building_shell_rect(edits)
    # On renovations of protected shells (`shop-renovation`, `rowhouse-shop-conversion`), include protected walls in shell_rect.
    if not vehicle and task in ('shop-renovation', 'rowhouse-shop-conversion'):
        shell_rect = _infer_building_shell_rect(grid)

    wool_count = 0
    bookshelf_violations = 0
    address_signs: list[tuple[int, int, int]] = []
    built_placards: list[tuple[int, int, int]] = []
    renovated_placards: list[tuple[int, int, int]] = []
    operational_signs: list[tuple[int, int, int]] = []

    for pos, c in sorted(edits.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        x, y, z = pos
        st = c[3]
        b, p = state_parts(st)
        lines = c[4]
        comp = c[5] or ''
        asset = c[6]
        frame = c[7] if len(c) > 7 else None

        # Item frame attachment check (can live on an 'air' cell)
        if frame is not None:
            ff = frame.get('facing', 'north')
            dx, dy, dz = VEC.get(ff, (0, 0, -1))
            back_st = block_fn((x - dx, y - dy, z - dz))
            bb = name(back_st)
            fixed_ok = bool(frame.get('fixed')) and (bb.endswith(('_wall', '_glass_pane')) or bb in ('glass_pane', 'iron_bars'))
            if not (full_block(back_st) or fixed_ok):
                add('floating_attachment', pos, f'item_frame[facing={ff}] attaches to non-solid {back_st}.', 'error')

        if b == 'air':
            continue

        if asset in BANNED_HEADS:
            add('banned_exit_head', pos, f'{asset} is banned; use emergency_exit_light_caged on interior walls.', 'error')

        # Bookshelf-filler ban
        if b == 'bookshelf':
            if task in BOOKSHELF_BANNED_TASKS or (task in GROUND_FLOOR_BOOKSHELF_BANNED and y <= 5):
                bookshelf_violations += 1
                add('bookshelf_filler', pos, 'Vanilla bookshelf filler is banned in commercial/civic fit-outs; build real counters/gondolas with custom heads.', 'error')

        # Wool structural massing ban (non-vehicles)
        if not vehicle and b.endswith('_wool'):
            wool_count += 1

        # Indoor wild flora check
        if not vehicle and b in GROUND_FLORA and shell_rect is not None:
            x0, z0, x1, z1, _, _ = shell_rect
            if x0 < x < x1 and z0 < z < z1 and _is_interior_cell(pos, st, comp, shell_rect, block_fn, h):
                add('indoor_wild_flora', pos, f'Wild {b} inside enclosed floorplate; use potted plants or plant_pot heads indoors.', 'error')

        # Low-rise rooftop redstone_torch antenna mast ban
        if not vehicle and b in ('redstone_torch', 'redstone_wall_torch') and h < 32 and y >= 7:
            add('rooftop_antenna_mast', pos, 'Omit redstone_torch aircraft beacons and antenna masts on low/mid-rise buildings (y < 30).', 'error')

        # Wall-mounted tripwire_hook / button / lever / ladder backing
        if b in ('tripwire_hook', 'ladder') or ((b.endswith('_button') or b == 'lever') and p.get('face') == 'wall'):
            f = p.get('facing', 'north')
            if f in VEC:
                dx, dy, dz = VEC[f]
                back_st = block_fn((x - dx, y - dy, z - dz))
                if not full_block(back_st):
                    add('floating_attachment', pos, f'{b}[facing={f}] requires a full solid wall block behind it ({back_st}).', 'error')

        # Door pane-jamb ban (upgraded to error), door_blocked, and door_drop
        if b.endswith('_door') and p.get('half', 'lower') == 'lower':
            facing = p.get('facing', 'north')
            perp = ((1, 0), (-1, 0)) if facing in ('north', 'south') else ((0, 1), (0, -1))
            for dx, dz in perp:
                for yy in (y, y + 1):
                    nb_b = name(block_fn((x + dx, yy, z + dz)))
                    if is_pane_or_bars(nb_b):
                        add('pane_beside_door', (x + dx, yy, z + dz), f'{nb_b} sits beside {b}; flank doors with full stained glass or stripped wood jambs.', 'error')
            if not vehicle and facing in VEC:
                dx, _, dz = VEC[facing]
                f_blk = not passable(block_fn((x + dx, y, z + dz))) or not passable(block_fn((x + dx, y + 1, z + dz)))
                b_blk = not passable(block_fn((x - dx, y, z - dz))) or not passable(block_fn((x - dx, y + 1, z - dz)))
                if f_blk and b_blk:
                    add('door_blocked', pos, f'{b} is blocked by non-passable blocks on both sides.', 'error')
                else:
                    lv = 2 * y
                    sides_ok = True
                    for sx, sz in ((x + dx, z + dz), (x - dx, z - dz)):
                        if not (0 <= sx < w and 0 <= sz < d):
                            continue
                        near = [nl for nl in levels.get((sx, sz), ()) if abs(nl - lv) <= 2]
                        if not near:
                            rail_b = name(block_fn((sx, y, sz)))
                            if rail_b.endswith(('_bars', '_pane', '_fence', '_wall')) and flush_top(block_fn((sx, y - 1, sz))):
                                continue  # Guarded Juliet balcony
                            sides_ok = False
                    if not sides_ok:
                        add('door_drop', pos, 'Door opens onto an unstepped >1-block drop or obstructed threshold.', 'error')

        # Walkable stair headroom & dead-end check (ported from cad.lint_cells)
        if not vehicle and b.endswith('_stairs') and p.get('half', 'bottom') == 'bottom' and p.get('shape', 'straight') == 'straight':
            f = p.get('facing', 'north')
            if f in ('north', 'south', 'east', 'west') and comp not in ('roof', 'trim', 'cornice', 'awning', 'furniture', 'relief', 'gondola', 'bench'):
                dx, _, dz = VEC[f]
                up_st = block_fn((x + dx, y + 1, z + dz))
                dn_st = block_fn((x - dx, y - 1, z - dz))
                up_b, up_p = state_parts(up_st)
                dn_b, dn_p = state_parts(dn_st)
                has_up = up_b.endswith('_stairs') and up_p.get('half', 'bottom') == 'bottom' and up_p.get('facing') == f
                has_dn = dn_b.endswith('_stairs') and dn_p.get('half', 'bottom') == 'bottom' and dn_p.get('facing') == f
                has_roof = any(name(block_fn((x, y + k, z))) != 'air' for k in range(1, min(9, h - y)))
                if (comp in ('stair', 'stairs') or has_up or has_dn) and has_roof:
                    h1 = block_fn((x, y + 1, z))
                    h2 = block_fn((x, y + 2, z)) if y + 2 < h else 'air'
                    ht = block_fn((x - dx, y + 2, z - dz)) if y + 2 < h else 'air'
                    ht_b, ht_p = state_parts(ht)
                    if not passable(h1) or not passable(h2):
                        add('stair_headroom', pos, f'Stair {b} has blocked headroom ({h1}, {h2}).', 'error')
                    elif not passable(ht) and not (ht_b.endswith('_slab') and ht_p.get('type') == 'top'):
                        add('stair_headroom', pos, f'Stair {b} hits overhead ceiling {ht} while ascending.', 'error')
                    if not has_up and 0 <= x + dx < w and 0 <= z + dz < d and y + 2 < h:
                        t_lo = block_fn((x + dx, y + 1, z + dz))
                        t_hi = block_fn((x + dx, y + 2, z + dz))
                        t_flr = block_fn((x + dx, y, z + dz))
                        if not passable(t_lo) or not passable(t_hi) or name(t_flr) == 'air':
                            add('stair_dead_end', pos, f'Top of stair flight at {pos} has no clear landing.', 'error')
                    if not has_dn and 0 <= x - dx < w and 0 <= z - dz < d and y + 1 < h:
                        b_lo = block_fn((x - dx, y, z - dz))
                        b_hi = block_fn((x - dx, y + 1, z - dz))
                        if not passable(b_lo) or not passable(b_hi):
                            add('stair_dead_end', pos, f'Bottom of stair flight at {pos} starts against a blocked cell.', 'error')

        # Floating carpet / pressure plate
        if not vehicle and b.endswith(('_carpet', '_pressure_plate')):
            dn_st = block_fn((x, y - 1, z))
            if not flush_top(dn_st) and not name(dn_st).endswith(('_fence', '_wall')):
                add('floating_carpet', pos, f'{b} floats above {dn_st} without a flush surface or post.', 'error')

        # Floating glass panes & iron bars (ported from cad.lint_cells)
        if not vehicle and is_pane_or_bars(b):
            dn_st = block_fn((x, y - 1, z))
            up_st = block_fn((x, y + 1, z)) if y + 1 < h else 'air'
            dn_b, dn_p = state_parts(dn_st)
            bad_dn = (
                dn_b == 'air'
                or dn_b in ('player_head', 'player_wall_head')
                or dn_b.endswith(('_carpet', '_pressure_plate'))
                or (dn_b.endswith('_slab') and dn_p.get('type', 'bottom') == 'bottom')
            )
            if bad_dn:
                up_ok = full_block(up_st) or is_pane_or_bars(name(up_st))
                visited_p = {(x, z)}
                qp = [(x, z)]
                solid_contacts = 0
                while qp and len(visited_p) <= 256:
                    cx, cz = qp.pop()
                    for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, nz = cx + ox, cz + oz
                        nb = block_fn((nx, y, nz))
                        nb_b = name(nb)
                        if is_pane_or_bars(nb_b) and (nx, nz) not in visited_p:
                            visited_p.add((nx, nz))
                            qp.append((nx, nz))
                        elif full_block(nb) or nb_b.endswith('_stairs'):
                            solid_contacts += 1
                if not (up_ok and solid_contacts >= 2):
                    add('floating_pane', pos, f'{b} hovers over {dn_b} without a solid sill/counter or framed jambs.', 'error')

        # Floating slabs (ported from cad.lint_cells)
        if not vehicle and b.endswith('_slab'):
            stype = p.get('type', 'bottom')
            dn_st = block_fn((x, y - 1, z))
            up_st = block_fn((x, y + 1, z)) if y + 1 < h else 'air'
            dn_b = name(dn_st)
            if stype == 'bottom':
                dn_ok = dn_b != 'air' and dn_b not in ('player_head', 'player_wall_head') and not dn_b.endswith(('_carpet', '_pressure_plate'))
                if not dn_ok:
                    horiz = [block_fn((x + ox, y, z + oz)) for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                    step_dn = [block_fn((x + ox, y - 1, z + oz)) for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                    cant_ok = any(is_horiz_anchor(hs) or name(hs).endswith('_slab') for hs in horiz) or any(
                        full_block(ss) or name(ss).endswith(('_slab', '_stairs')) for ss in step_dn
                    )
                    if not cant_ok:
                        add('floating_slab', pos, f'{b}[type=bottom] floats above {dn_b} without bearing or cantilever.', 'error')
            elif stype == 'top':
                up_ok = full_block(up_st) or name(up_st).endswith(('_stairs', '_fence', '_wall'))
                visited_s = {(x, z)}
                qs = [(x, z)]
                anchors = 0
                roof_step = False
                while qs and len(visited_s) <= 256:
                    cx, cz = qs.pop()
                    for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, nz = cx + ox, cz + oz
                        nb = block_fn((nx, y, nz))
                        nb_b, nb_p = state_parts(nb)
                        if nb_b.endswith('_slab') and nb_p.get('type', 'bottom') == 'top':
                            if (nx, nz) not in visited_s:
                                visited_s.add((nx, nz))
                                qs.append((nx, nz))
                        elif is_horiz_anchor(nb):
                            anchors += 1
                        elif nb_b.endswith('_slab') and nb_p.get('type', 'bottom') == 'bottom':
                            roof_step = True
                        nb_up = block_fn((nx, y + 1, nz)) if y + 1 < h else 'air'
                        if nb_b == 'air' and name(nb_up).endswith('_slab') and state_parts(nb_up)[1].get('type', 'bottom') == 'bottom':
                            roof_step = True
                if dn_b in ('player_head', 'player_wall_head') or is_pane_or_bars(dn_b):
                    direct_frame = sum(1 for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if is_horiz_anchor(block_fn((x + ox, y, z + oz))))
                    if not up_ok and direct_frame < 2:
                        add('floating_slab', pos, f'{b}[type=top] hovers over {dn_b} without side piers or overhead bearing.', 'error')
                elif not (up_ok or roof_step or anchors >= 1):
                    add('floating_slab', pos, f'{b}[type=top] floats in mid-air without any anchor.', 'error')

        # Sign content, zone, pixel-width, and placard rules
        if b.endswith(('_sign', '_hanging_sign', '_wall_hanging_sign')) and lines is not None:
            padded = [str(s) for s in lines[:4]]
            while len(padded) < 4:
                padded.append('')
            nonempty = [i for i, s in enumerate(padded) if s.strip()]
            if nonempty:
                is_interior = _is_interior_cell(pos, st, comp, shell_rect, block_fn, h)
                zone = 'interior' if is_interior else 'exterior'
                limit = MAX_HANGING_SIGN_PX if b.endswith(('_hanging_sign', '_wall_hanging_sign')) else MAX_SIGN_PX
                for idx_l, s in enumerate(padded):
                    px = line_px(s)
                    if px > limit:
                        add('pixel_overflow', pos, f'Sign line {idx_l + 1} ({s!r}) is ~{px}px wide (max {limit}px).', 'error')

                hdr0 = padded[0].strip()
                is_built_hdr = hdr0 == 'Built'
                is_ren_hdr = hdr0 in ('Renovated', 'Interior fit-out')
                if (is_built_hdr or is_ren_hdr) and (len(padded) >= 2 and (is_divider(padded[1]) or padded[1].strip())):
                    if not is_interior:
                        add('exterior_dedication_placard', pos, 'Built/Renovated placards belong on a solid interior wall, never on an exterior facade.', 'error')
                    else:
                        dn_st = block_fn((x, y - 1, z))
                        if flush_top(dn_st) or name(dn_st).endswith(('_carpet', '_pressure_plate')):
                            add('low_dedication_placard', pos, 'Mount Built/Renovated placards at eye height or higher (floor_y + 2+), never on the lowest wall block.', 'error')
                        else:
                            # Check for builder tool item_frame directly above at (x, y + 1, z)
                            up_cell = grid.get((x, y + 1, z))
                            up_frame = up_cell[7] if (up_cell and len(up_cell) > 7) else None
                            has_tool_frame = (
                                isinstance(up_frame, dict)
                                and not up_frame.get('invisible', False)
                                and up_frame.get('item') in BUILDER_TOOLS
                                and up_frame.get('facing') == p.get('facing', 'north')
                            )
                            if has_tool_frame:
                                if is_built_hdr:
                                    built_placards.append(pos)
                                else:
                                    renovated_placards.append(pos)

                if zone == 'exterior':
                    for s in padded:
                        if _EXTERIOR_FORBIDDEN_RE.search(s.strip()):
                            add('exterior_code_sign', pos, f'Interior safety/code text ({s.strip()!r}) must never be placed on exterior walls.', 'error')
                            break
                    if _ADDRESS_TOP_RE.match(hdr0) and is_divider(padded[1]) and padded[2].strip():
                        # Eye-height check: 1..3 blocks above ground/threshold below
                        dn1 = block_fn((x, y - 1, z))
                        dn2 = block_fn((x, y - 2, z))
                        dn3 = block_fn((x, y - 3, z))
                        if flush_top(dn2) or flush_top(dn3) or flush_top(dn1):
                            address_signs.append(pos)

                if not (is_built_hdr or is_ren_hdr or (_ADDRESS_TOP_RE.match(hdr0) and is_divider(padded[1]))):
                    operational_signs.append(pos)

                if not vehicle and task not in ('inspector-repair', 'junction-wayfinding'):
                    if nonempty == [1, 2]:
                        add('unframed_middle_two', pos, 'Frame short two-line signs with matching dash rules on rows 1 and 4.', 'error')

    if wool_count >= 4:
        first_wool = next(pos for pos, c in edits.items() if name(c[3]).endswith('_wool'))
        add('wool_massing', first_wool, f'Building uses {wool_count} wool blocks as massing; use concrete, stone, brick, or timber.', 'error')

    # Also recognize protected historic Built placards already present in renovation shells
    for pos, c in base.items():
        if c[4] and c[4][0].strip() == 'Built':
            built_placards.append(pos)

    # Unplanted base check (walls/piers/posts stopping 1..3 air blocks short of sloping ground)
    if not vehicle and task not in ('curved-tunnel', 'inspector-repair', 'washroom-fitout', 'roof-hvac', 'rowhouse-shop-conversion'):
        for (x, y, z), c in sorted(edits.items()):
            if (x, y - 1, z) in edits:
                continue
            b = name(c[3])
            comp = c[5] or ''
            if b in ('air', 'water', 'lantern', 'soul_lantern', 'end_rod', 'player_head', 'player_wall_head') or b in GROUND_FLORA or b.startswith('potted_') or b.endswith(('_log', '_wood')):
                continue
            if comp in _OVERHANG_COMPS or b.endswith(_NOT_BEARING_SUFFIXES):
                continue
            if c[4] is not None or c[6] is not None or (len(c) > 7 and c[7] is not None):
                continue
            gap = 0
            while gap <= 3 and y - 1 - gap >= 0 and (x, y - 1 - gap, z) not in edits:
                below_b = name(block_fn((x, y - 1 - gap, z)))
                if below_b == 'air' or below_b in GROUND_FLORA:
                    gap += 1
                else:
                    break
            if 1 <= gap <= 3 and y - 1 - gap >= 0 and (x, y - 1 - gap, z) not in edits:
                land_b = name(block_fn((x, y - 1 - gap, z)))
                if land_b not in ('air', 'water'):
                    add('unplanted_base', (x, y, z), f'{b} stops {gap} block(s) short of ground ({land_b}); carry foundation/post to grade.', 'error')

    # Massing, elevation articulation, planar-face, recessed-entry & rooftop-equipment checks
    massing_ok = True
    elevations_ok = True
    worst_blank_ratio = 0.0
    side_ratios: dict[str, float] = {}
    recessed_entry_ok = True
    roof_equip_ok = True

    if task in ENCLOSED_BUILDING_TASKS and shell_rect is not None:
        x0, z0, x1, z1, y_low, y_high = shell_rect
        bw, bd, bh = x1 - x0 + 1, z1 - z0 + 1, y_high - y_low + 2
        short_s, long_s = min(bw, bd), max(bw, bd)
        if short_s < 6 or long_s < 8:
            massing_ok = False
            add('footprint_too_small', (x0, y_low, z0), f'Building footprint is {bw}x{bd}; minimum building body is 6x8.', 'error')
        if bh > 3 * short_s + 2:
            massing_ok = False
            add('tower_proportion', (x0, y_high, z0), f'Height {bh} exceeds 3 * {short_s} + 2 slender proportion limit.', 'error')

        # Chimney height check
        chimneys: dict[tuple[int, int], list[int]] = {}
        for (cx, cy, cz), c in edits.items():
            if (c[5] or '') == 'chimney' and name(c[3]) != 'air':
                chimneys.setdefault((cx, cz), []).append(cy)
        for (cx, cz), cys in chimneys.items():
            clear = 0
            for cy in sorted(cys, reverse=True):
                if any(
                    name(block_fn((cx + ox, cy, cz + oz))) != 'air'
                    and (grid.get((cx + ox, cy, cz + oz), [0, 0, 0, 'air', None, ''])[5] or '') != 'chimney'
                    for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                ):
                    break
                clear += 1
            if clear > 3:
                massing_ok = False
                add('chimney_too_tall', (cx, max(cys), cz), f'Chimney stands {clear} blocks clear of roof (max 3).', 'error')

        # Raised walkway ("drawbridge") check
        if task != 'hillside-pavilion':
            raised_cells = 0
            for (px, py, pz), c in edits.items():
                if (c[5] or '') in ('path', 'steps') and name(c[3]) != 'air':
                    if all(
                        (px, py - k, pz) in edits and name(edits[px, py - k, pz][3]) != 'air'
                        and (edits[px, py - k, pz][5] or '') in ('path', 'steps', 'foundation')
                        for k in (1, 2)
                    ) and all(
                        name(block_fn((px + ox, py, pz + oz))) == 'air'
                        for ox, oz in ((1, 0), (-1, 0))
                    ):
                        raised_cells += 1
            if raised_cells >= 3:
                massing_ok = False
                add('raised_walkway', (x0, y_low, z0), f'{raised_cells} walkway cells sit on >=2 blocks of narrow fill; grade entrance to sidewalk.', 'error')

        # Per-side blank-elevation ratio & planar-facade relief check (stepping inward cleanly on podium+tower buildings)
        wall_y1 = min(y_high, y_low + max(3, bh - 3))
        # Precompute per-y horizontal wall bounds so stepped upper shafts are measured at their own facade plane!
        y_bounds: dict[int, tuple[int, int, int, int]] = {}
        for yy in range(y_low, wall_y1 + 1):
            pts_y = [
                (px, pz) for (px, py, pz), c in edits.items()
                if py == yy and x0 <= px <= x1 and z0 <= pz <= z1
                and (full_block(c[3]) or 'glass' in name(c[3]) or name(c[3]).endswith('_door'))
                and name(c[3]) not in FLORA_SOIL
            ]
            if len(pts_y) >= 6:
                y_bounds[yy] = (
                    min(p[0] for p in pts_y), min(p[1] for p in pts_y),
                    max(p[0] for p in pts_y), max(p[1] for p in pts_y),
                )

        for side_name, rep_pos in (
            ('north', (x0, y_low + 1, z0)),
            ('south', (x0, y_low + 1, z1)),
            ('west', (x0, y_low + 1, z0)),
            ('east', (x1, y_low + 1, z0)),
        ):
            # Exempt zero-lot-line party walls abutting protected neighbour buildings
            base_span = range(x0, x1 + 1) if side_name in ('north', 'south') else range(z0, z1 + 1)
            party_adj = 0
            for t in base_span:
                for yy in range(y_low, min(wall_y1 + 1, y_low + 5)):
                    nx, nz = (t, z0 - 1) if side_name == 'north' else (t, z1 + 1) if side_name == 'south' else (x0 - 1, t) if side_name == 'west' else (x1 + 1, t)
                    if (nx, yy, nz) in protected and full_block(base.get((nx, yy, nz), [0, 0, 0, 'air'])[3]):
                        party_adj += 1
            if party_adj >= len(list(base_span)):
                continue

            def side_coord(yy: int, t: int, dp: int) -> tuple[int, int]:
                bx0, bz0, bx1, bz1 = y_bounds.get(yy, (x0, z0, x1, z1))
                if side_name == 'north':
                    return (t, bz0 + dp)
                if side_name == 'south':
                    return (t, bz1 - dp)
                if side_name == 'west':
                    return (bx0 + dp, t)
                return (bx1 - dp, t)

            def span_for_y(yy: int) -> range:
                bx0, bz0, bx1, bz1 = y_bounds.get(yy, (x0, z0, x1, z1))
                return range(bx0, bx1 + 1) if side_name in ('north', 'south') else range(bz0, bz1 + 1)

            face_mats: dict[str, int] = {}
            has_proud_or_recessed_relief = False
            for yy in range(y_low, wall_y1 + 1):
                sp = list(span_for_y(yy))
                for t in sp:
                    sx0, sz0 = side_coord(yy, t, 0)
                    if (sx0, yy, sz0) in edits:
                        sb0 = name(edits[sx0, yy, sz0][3])
                        if sb0 != 'air' and full_block(edits[sx0, yy, sz0][3]) and 'glass' not in sb0:
                            face_mats[sb0] = face_mats.get(sb0, 0) + 1
                inner_sp = sp[1:-1] if len(sp) > 2 else sp
                for t in inner_sp:
                    ox, oz = side_coord(yy, t, -1)
                    px, pz = side_coord(yy, t, 0)
                    ix, iz = side_coord(yy, t, 1)
                    b_out = name(edits[ox, yy, oz][3]) if (ox, yy, oz) in edits else 'air'
                    b_pln = name(block_fn((px, yy, pz)))
                    b_in = name(edits[ix, yy, iz][3]) if (ix, yy, iz) in edits else 'air'
                    if b_out != 'air' and b_out not in FLORA_SOIL and b_out not in GROUND_FLORA:
                        has_proud_or_recessed_relief = True
                    elif (b_pln == 'air' or is_pane_or_bars(b_pln) or b_pln.endswith('_leaves')) and (
                        'glass' in b_in or b_in.endswith('_door') or (full_block(block_fn((ix, yy, iz))) and b_in not in FLORA_SOIL)
                    ):
                        has_proud_or_recessed_relief = True
            dom_mat = max(face_mats, key=face_mats.__getitem__) if face_mats else ''

            total_face = 0
            blank_face = 0
            for yy in range(y_low, wall_y1 + 1):
                for t in span_for_y(yy):
                    slice_blocks = [name(block_fn((*side_coord(yy, t, dp)[0:1], yy, side_coord(yy, t, dp)[1]))) for dp in (-1, 0, 1)]
                    b_outer, b_plane, b_inner = slice_blocks[0], slice_blocks[1], slice_blocks[2]
                    if b_outer == 'air' and b_plane == 'air' and b_inner == 'air':
                        continue
                    total_face += 1
                    articulated = (
                        any('glass' in sb or sb.endswith(('_door', '_trapdoor', '_bars', '_stairs', '_slab', '_wall', '_fence', '_leaves'))
                            or sb in ('end_rod', 'sea_lantern', 'lantern', 'iron_bars', 'chain', 'iron_chain')
                            or sb.startswith('stripped_')
                            for sb in (b_outer, b_plane))
                        or (b_plane == 'air' and ('glass' in b_inner or b_inner.endswith('_door')))
                        or (b_outer != 'air' and b_outer not in GROUND_FLORA and b_outer not in FLORA_SOIL)
                        or (b_plane not in ('air', dom_mat))
                    )
                    if not articulated:
                        blank_face += 1
            ratio = round(blank_face / max(1, total_face), 3)
            side_ratios[side_name] = ratio
            worst_blank_ratio = max(worst_blank_ratio, ratio)
            max_blank = float(reqs.get('max_blank_elevation_ratio', 0.62))
            if ratio > max_blank:
                elevations_ok = False
                add('blank_elevation', rep_pos, f'{side_name.capitalize()} elevation is {int(ratio * 100)}% uniform blank wall (max {int(max_blank * 100)}%).', 'error')
            if not has_proud_or_recessed_relief:
                elevations_ok = False
                add('planar_facade', rep_pos, f'{side_name.capitalize()} elevation is completely planar (single block plane); add recessed bays/doors, sills, shutters, canopies, or pilasters.', 'error')

        # 1-block recessed ground-floor exterior entrance check on new-build buildings
        ext_doors = [
            (dx, dy, dz, state_parts(c[3])[1].get('facing', 'north'))
            for (dx, dy, dz), c in edits.items()
            if name(c[3]).endswith('_door')
            and state_parts(c[3])[1].get('half', 'lower') == 'lower'
            and dy <= y_low + 2
        ]
        if ext_doors:
            street_doors = [dr for dr in ext_doors if dr[3] in ('north', 'west')] or ext_doors[:1]
            for dx, dy, dz, df in street_doors:
                vx, _, vz = VEC.get(df, (0, 0, -1))
                recessed = False
                for sign_dir in (1, -1):
                    ox, oz = dx + sign_dir * vx, dz + sign_dir * vz
                    if passable(block_fn((ox, dy, oz))) and passable(block_fn((ox, dy + 1, oz))):
                        has_soffit = any(name(block_fn((ox, dy + ky, oz))) != 'air' for ky in (2, 3))
                        perp = ((1, 0), (-1, 0)) if vx == 0 else ((0, 1), (0, -1))
                        has_flank = any(
                            not passable(block_fn((ox + step * px, dy, oz + step * pz)))
                            for px, pz in perp
                            for step in (1, 2, 3)
                        )
                        if has_soffit and has_flank:
                            recessed = True
                            break
                if not recessed:
                    recessed_entry_ok = False
                    add('flush_exterior_door', (dx, dy, dz), 'Exterior entrance door sits flat in an unframed wall; recess 1 block inside a framed portal or porch.', 'error')

    # Roof-equipment form check (reject featureless rooftop cubes; verify fan/solar/AC motif where required)
    if reqs.get('flat_roof_equipment') and shell_rect is not None:
        x0, z0, x1, z1, _, y_high = shell_rect
        top_zone_y = max(y_high - 3, 6)
        has_fan_rails = sum(1 for (_, y, _), c in edits.items() if y >= top_zone_y and name(c[3]) in RAIL_BLOCKS) >= 2
        has_solar = sum(1 for (_, y, _), c in edits.items() if y >= top_zone_y and name(c[3]) == 'daylight_detector') >= 2
        has_hvac_head = any(c[6] in ('ac_unit', 'wall_vent') and y >= top_zone_y for (_, y, _), c in edits.items())
        has_louvers = sum(
            1 for (_, y, _), c in edits.items()
            if y >= top_zone_y and (name(c[3]) in ('iron_bars', 'iron_trapdoor') or name(c[3]).endswith('_trapdoor'))
        ) >= 2
        if not (has_fan_rails or has_solar or has_hvac_head):
            roof_equip_ok = False
            add('roof_equipment_form', (x0, y_high, z0), 'Flat roof lacks credible mechanical/solar treatment (2x2 quartz+rail fan unit, daylight_detector array, or ac_unit/wall_vent heads).', 'error')
        # Also catch solid featureless mechanical blocks on roof if neither rails, louvers, nor heads accompany them
        roof_solids = [
            pos for pos, c in edits.items()
            if pos[1] >= y_high - 1 and name(c[3]) in ('iron_block', 'polished_andesite', 'light_gray_concrete', 'gray_concrete', 'smooth_stone')
        ]
        if len(roof_solids) >= 12 and not (has_fan_rails or has_louvers or has_hvac_head):
            roof_equip_ok = False
            add('roof_equipment_form', roof_solids[0], 'Rooftop mechanical bulkhead is a featureless solid block; add 2x2 fan rails, intake louvers, or HVAC heads.', 'error')

    return {
        'address_signs': len(address_signs),
        'built_placards': len(built_placards),
        'renovated_placards': len(renovated_placards),
        'operational_signs': len(operational_signs),
        'bookshelf_violations': bookshelf_violations,
        'massing_ok': massing_ok,
        'elevations_ok': elevations_ok,
        'side_blank_ratios': side_ratios,
        'worst_blank_ratio': worst_blank_ratio,
        'recessed_entry_ok': recessed_entry_ok,
        'roof_equip_ok': roof_equip_ok,
    }
