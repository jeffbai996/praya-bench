"""Inspect multi-scale geometry, lighting, terraforming and brief completion without executing code."""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from . import __version__
from .scene import (
    ASSETS, FLORA_SOIL, GRAVITY_BLOCKS, GROUND_FLORA, PALETTE,
    POST_MOUNTED_ASSETS, RAIL_BLOCKS, TALL_FLORA, VEC,
    flush_top, full_block, load_json, name, passable, state_parts, validate_cells,
)
from .tasks import TASK_SPECS, verify_run

LIGHT_BLOCKS = frozenset({
    'lantern', 'soul_lantern', 'sea_lantern', 'shroomlight',
    'ochre_froglight', 'verdant_froglight', 'pearlescent_froglight',
    'copper_bulb', 'weathered_copper_bulb', 'oxidized_copper_bulb',
    'waxed_copper_bulb', 'waxed_oxidized_copper_bulb',
    'end_rod', 'redstone_lamp', 'glowstone', 'torch', 'wall_torch',
    'campfire', 'soul_campfire',
})
BROADLEAF_BLOCKS = frozenset({
    'oak_leaves', 'birch_leaves', 'jungle_leaves', 'acacia_leaves',
    'dark_oak_leaves', 'cherry_leaves', 'mangrove_leaves',
    'azalea_leaves', 'flowering_azalea_leaves',
})
ROAD_SURFACE_BLOCKS = frozenset({
    'gray_concrete', 'black_concrete', 'light_gray_concrete', 'smooth_stone',
    'stone_bricks', 'cobblestone', 'andesite', 'polished_andesite',
    'deepslate_tiles', 'polished_deepslate', 'stone_brick_slab',
    'smooth_stone_slab', 'stone_brick_stairs', 'andesite_slab', 'andesite_stairs',
})
RAW_SCAR_BLOCKS = frozenset({
    'stone', 'coal_ore', 'iron_ore', 'copper_ore', 'dirt', 'coarse_dirt',
})


def _can_hang_from(state: str) -> bool:
    b, _ = state_parts(state)
    if b in ('air', 'water') or b in GROUND_FLORA or b.endswith('_carpet'):
        return False
    return (
        full_block(state)
        or b.endswith(('_slab', '_stairs', '_fence', '_wall', '_bars', '_hanging_sign', '_wall_hanging_sign'))
        or b in ('chain', 'iron_chain', 'end_rod', 'lightning_rod')
    )


def _can_support_standing_light(state: str) -> bool:
    b = name(state)
    return (
        flush_top(state)
        or b in ('iron_bars', 'chain', 'iron_chain', 'end_rod', 'lightning_rod')
        or b.endswith(('_fence', '_wall', '_pane'))
    )


def _emission(state: str) -> int:
    b = name(state)
    if b in ('sea_lantern', 'glowstone', 'lantern', 'shroomlight', 'ochre_froglight', 'verdant_froglight', 'pearlescent_froglight', 'redstone_lamp', 'copper_bulb', 'waxed_copper_bulb', 'campfire'):
        return 15
    if b in ('end_rod', 'torch', 'wall_torch'):
        return 14
    if b in ('soul_lantern', 'soul_campfire', 'weathered_copper_bulb'):
        return 11
    if b in ('oxidized_copper_bulb', 'waxed_oxidized_copper_bulb', 'candle') or b.endswith('_candle'):
        return 8
    if b in ('redstone_torch', 'redstone_wall_torch'):
        return 7
    return 0


def _transmits_light(state: str) -> bool:
    b, p = state_parts(state)
    if b == 'air' or 'glass' in b:
        return True
    if b.endswith('_door'):
        return False
    if passable(state):
        return True
    if b.endswith('_slab'):
        return p.get('type', 'bottom') != 'double'
    if b.endswith(('_leaves', '_stairs', '_pane', '_bars', '_fence', '_wall', '_trapdoor', '_bed')):
        return True
    if b in ('water', 'chain', 'iron_chain', 'lightning_rod', 'end_rod', 'lantern', 'soul_lantern', 'sea_lantern', 'glowstone', 'shroomlight'):
        return True
    return False


def _surface_info(
    block_fn: Any, x: int, z: int, h: int
) -> tuple[int, str]:
    for y in range(h - 1, -1, -1):
        st = block_fn((x, y, z))
        b, _ = state_parts(st)
        if b == 'air' or passable(st):
            continue
        if b.endswith(('_leaves', '_log', '_wood', '_fence', '_bars', '_pane', '_wall', '_sign', '_hanging_sign', '_wall_hanging_sign')):
            continue
        if b in ('lantern', 'soul_lantern', 'chain', 'iron_chain', 'end_rod', 'lightning_rod', 'player_head', 'player_wall_head'):
            continue
        return y, b
    return 0, 'air'


def block_from(grid: dict[tuple[int, int, int], list[Any]], pos: tuple[int, int, int]) -> str:
    return grid.get(pos, [0, 0, 0, 'air'])[3]


def assess(fixture: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    edits = validate_cells(submission)
    base = validate_cells({'cells': fixture['cells']})
    grid = base | edits
    protected = {tuple(p) for p in fixture['protected']}
    issues: list[dict[str, Any]] = []
    task = fixture['task']
    spec = TASK_SPECS.get(task, {})
    reqs = fixture.get('requirements') or spec.get('requirements', {})
    bounds = fixture.get('bounds') or spec.get('bounds', [0, 0, 0, 23, 17, 21])
    bx0, by0, bz0, bx1, by1, bz1 = bounds
    w, h, d = bx1 + 1, by1 + 1, bz1 + 1
    source_limit = fixture.get('source_limit') or spec.get('source_limit', 14000)

    def block(pos: tuple[int, int, int]) -> str:
        return grid.get(pos, [0, 0, 0, 'air'])[3]

    def add(code: str, pos: tuple[int, int, int], detail: str, severity: str = 'error') -> None:
        issues.append({'code': code, 'at': list(pos), 'detail': detail, 'severity': severity})

    source_chars = submission.get('source_characters')
    if submission.get('diagnostic_only') or (isinstance(source_chars, int) and source_chars > source_limit):
        add(
            'source_budget_exceeded',
            (0, 0, 0),
            f'Submission exceeded the {source_limit}-character source contract ({source_chars or "diagnostic"}).',
        )

    unpaired_bed_positions: set[tuple[int, int, int]] = set()

    for pos, c in edits.items():
        x, y, z = pos
        b, p = state_parts(c[3])
        if not (bx0 <= x <= bx1 and by0 <= y <= by1 and bz0 <= z <= bz1):
            add('out_of_bounds', pos, f'Outside the declared scene bounds {bounds}.')
        if pos in protected and (
            c[3] != block_from(base, pos) or c[4] != base.get(pos, [0, 0, 0, 'air', None])[4]
        ):
            add('protected_change', pos, 'Changed protected terrain, infrastructure or historic architecture.')
        if b not in PALETTE:
            add('unsupported_block', pos, f'{b} is outside this evaluator’s declared palette; not a complete game registry verdict.')
        if p.get('facing') and p['facing'] not in VEC:
            add('invalid_facing', pos, 'Unknown facing direction.')
        if b == 'air':
            continue

        below = block((x, y - 1, z))
        above = block((x, y + 1, z))

        if b in GRAVITY_BLOCKS and (passable(below) or name(below) == 'water'):
            add('floating_gravity_block', pos, f'{b} is a gravity block and cannot rest on {below}.')

        if b in RAIL_BLOCKS and not flush_top(below):
            add('floating_fixture', pos, f'{b} requires a flush supporting surface below ({below}).')

        if b.endswith('_wall_hanging_sign'):
            facing = p.get('facing', 'north')
            perp = ((1, 0), (-1, 0)) if facing in ('north', 'south') else ((0, 1), (0, -1))
            side_ok = False
            for dx, dz in perp:
                sb, _ = state_parts(block((x + dx, y, z + dz)))
                if not passable(block((x + dx, y, z + dz))) and not sb.endswith('hanging_sign'):
                    side_ok = True
                    break
            if not side_ok:
                add('unsupported_hanging_sign', pos, 'Wall hanging sign needs a solid or post support on its horizontal bar axis.')
        elif b.endswith('_hanging_sign'):
            if not _can_hang_from(above):
                add('unsupported_hanging_sign', pos, f'Ceiling hanging sign cannot hang from {above}.')
        elif 'wall_sign' in b or b == 'player_wall_head' or b in ('wall_torch', 'redstone_wall_torch'):
            vec = VEC.get(p.get('facing', 'north'), (0, 0, -1))
            back_pos = (x - vec[0], y - vec[1], z - vec[2])
            back = block(back_pos)
            if not full_block(back):
                add('unsupported_wall_fixture', pos, f'Backing is {back}; requires a full wall face.')
            elif back_pos in edits and back_pos[1] >= 4:
                connected = any(
                    name(block((back_pos[0] + nx, back_pos[1] + ny, back_pos[2] + nz))) != 'air'
                    for nx, ny, nz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
                    if (back_pos[0] + nx, back_pos[1] + ny, back_pos[2] + nz) != pos
                )
                if not connected:
                    add('floating_backing_block', pos, 'Wall fixture attaches to an isolated single block floating in air.')

        if b == 'player_head':
            if c[6] in POST_MOUNTED_ASSETS:
                below_name = name(below)
                if (
                    below_name not in ('iron_bars', 'iron_chain', 'chain', 'glass_pane')
                    and not below_name.endswith(('_stained_glass_pane', '_fence'))
                ):
                    add('mailbox_plinth', pos, f'{c[6]} needs a slender bar, chain, fence or glass post.')
            elif not flush_top(below):
                add('floating_prop', pos, f'Prop does not sit flush on {below}.')

        if b.endswith('_sign') and 'wall' not in b and not b.endswith('_hanging_sign'):
            if not flush_top(below) and not name(below).endswith(('_fence', '_wall')):
                add('floating_fixture', pos, f'Standing sign has no ground support ({below}).')
            elif c[5] not in ('road-sign', 'traffic-sign'):
                add('standing_sign', pos, 'Non-traffic signs should mount on architecture.', 'warn')

        if b.endswith(('_sign', '_hanging_sign', '_wall_hanging_sign')) and not any(s.strip() for s in (c[4] or [])):
            add('blank_sign', pos, 'No visible sign text.', 'warn')

        if reqs.get('forbid_new_build_claim') and c[4]:
            joined = ' '.join(c[4]).lower()
            if re.search(r'\bnew\s+(?:build|construction)\b', joined) or (
                re.search(r'\bbuilt\b', joined)
                and re.search(r'\b202[4-9]\b', joined)
                and '2012' not in joined
                and not re.search(r'\b(?:renovat|refit|restor|remodel)', joined)
            ):
                add('contradictory_renovation_date', pos, 'Renovation sign claims recent original construction instead of preserving historic date.')

        if b.endswith('_door'):
            lower = p.get('half', 'lower') == 'lower'
            other = (x, y + (1 if lower else -1), z)
            ob, op = state_parts(block(other))
            if (
                ob != b
                or op.get('half') != ('upper' if lower else 'lower')
                or op.get('facing', 'north') != p.get('facing', 'north')
                or op.get('hinge', 'left') != p.get('hinge', 'left')
            ):
                add('unpaired_door', pos, 'Door is missing its matching aligned half.')
            if lower:
                if not flush_top(below):
                    add('floating_fixture', pos, f'Door threshold has no flush floor below ({below}).')
                facing = p.get('facing', 'north')
                perp = ((1, 0), (-1, 0)) if facing in ('north', 'south') else ((0, 1), (0, -1))
                if any(
                    name(block((x + dx, yy, z + dz))).endswith('glass_pane')
                    for dx, dz in perp
                    for yy in (y, y + 1)
                ):
                    add('door_pane_jamb', pos, 'Glazed wall door jamb uses thin glass panes instead of full blocks.', 'warn')

        if b.endswith('_bed'):
            part = p.get('part', 'foot')
            facing = p.get('facing', 'north')
            vec = VEC.get(facing, (0, 0, -1))
            other = (x + vec[0], y, z + vec[2]) if part == 'foot' else (x - vec[0], y, z - vec[2])
            ob, op = state_parts(block(other))
            if (
                ob != b
                or op.get('part', 'foot') != ('head' if part == 'foot' else 'foot')
                or op.get('facing', 'north') != facing
            ):
                unpaired_bed_positions.add(pos)
                add('unpaired_bed', pos, 'Bed requires matching foot and head halves along its facing direction.')
            if not flush_top(below):
                add('floating_fixture', pos, f'Bed does not sit on a flush floor ({below}).')

        if b in ('lantern', 'soul_lantern'):
            if p.get('hanging') == 'true':
                if not _can_hang_from(above):
                    add('floating_fixture', pos, f'Hanging {b} has no overhead support ({above}).')
            elif not _can_support_standing_light(below):
                add('floating_fixture', pos, f'Standing {b} has no support below ({below}).')

        if b in ('torch', 'redstone_torch') and not _can_support_standing_light(below):
            add('floating_fixture', pos, f'{b} has no support below ({below}).')

        if b.endswith('_carpet') and name(below) in ('air', 'water'):
            add('floating_fixture', pos, f'Carpet floats above {below}.')

        if (b == 'flower_pot' or b.startswith('potted_')) and not flush_top(below):
            add('floating_fixture', pos, f'{b} does not sit flush on {below}.')

        if b in GROUND_FLORA:
            below_b, below_p = state_parts(below)
            tall_upper_ok = (
                b in TALL_FLORA
                and p.get('half') == 'upper'
                and below_b == b
                and below_p.get('half', 'lower') == 'lower'
            )
            if not tall_upper_ok and below_b not in FLORA_SOIL:
                add('invalid_planting', pos, f'{b} is placed on {below}; requires soil, grass or moss.')

        if b.endswith('_trapdoor'):
            vec = VEC.get(p.get('facing', 'north'), (0, 0, -1))
            hinge_back = block((x - vec[0], y, z - vec[2]))
            horiz_full = sum(
                full_block(block((x + dx, y, z + dz)))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            supported_trapdoor = (
                not passable(hinge_back)
                or (p.get('half', 'bottom') != 'top' and flush_top(below))
                or (p.get('half') == 'top' and full_block(above))
                or horiz_full >= 2
            )
            if not supported_trapdoor:
                add('floating_trapdoor', pos, f'{b} floats without hinge backing, floor support or ceiling bearing.')

        if b == 'end_rod':
            vec = VEC.get(p.get('facing', 'up'), (0, 1, 0))
            support = block((x - vec[0], y - vec[1], z - vec[2]))
            if name(support) == 'air':
                add('unsupported_rod', pos, 'No attachment at the rod base.')

        if 'glass' in b and y >= 3:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                npos = (x + dx, y, z + dz)
                if npos in protected and full_block(block_from(base, npos)):
                    add('blind_party_wall_glazing', pos, 'Glazing sits directly against an opaque protected neighbour wall.', 'warn')
                    break

    # --- Terraforming: orphan foliage & subsurface void checks ---
    repair_rect = fixture.get('repair_rect') or spec.get('repair_rect')
    if reqs.get('check_orphan_foliage'):
        _check_orphan_foliage(grid, w, h, d, repair_rect, add)

    subsurface_void_cols = 0
    if reqs.get('no_subsurface_voids'):
        subsurface_void_cols = _check_subsurface_voids(edits, block, repair_rect, w, h, d, add)

    # --- 3D Sky + Block Light check for enclosed dark rooms ---
    if edits:
        _check_interior_darkness(grid, edits, block, w, h, d, add)

    # --- Half-block walkability flood from protected street seeds ---
    levels: dict[tuple[int, int], list[int]] = {}
    for x in range(w):
        for z in range(d):
            out: list[int] = []
            for y in range(h):
                here = block((x, y, z))
                b, p = state_parts(here)
                if passable(here) and passable(block((x, y + 1, z))) and flush_top(block((x, y - 1, z))):
                    out.append(2 * y)
                elif (
                    (b.endswith('_stairs') and p.get('half', 'bottom') == 'bottom')
                    or (b.endswith('_slab') and p.get('type', 'bottom') == 'bottom')
                ) and passable(block((x, y + 1, z))) and passable(block((x, y + 2, z))):
                    out.append(2 * y + (2 if b.endswith('_stairs') else 1))
            levels[x, z] = out

    seed_cols = (
        {(pt[0], pt[1]) for pt in fixture['street_seeds']}
        if 'street_seeds' in fixture
        else {(x, z) for x in range(w) for z in range(min(5, d))}
    )
    seen = {(x, z, hh) for (x, z), hs in levels.items() if (x, z) in seed_cols for hh in hs}
    q = deque(seen)
    while q:
        x, z, hh = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for nh in levels.get((x + dx, z + dz), []):
                cand = (x + dx, z + dz, nh)
                if abs(nh - hh) <= 2 and cand not in seen:
                    seen.add(cand)
                    q.append(cand)

    doors: list[list[int]] = []
    reachable_doors: list[list[int]] = []
    for (x, y, z), c in grid.items():
        b, p = state_parts(c[3])
        if b.endswith('_door') and p.get('half', 'lower') == 'lower':
            doors.append([x, y, z])
            if (x, z, 2 * y) in seen:
                reachable_doors.append([x, y, z])
            else:
                add('unreachable_door', (x, y, z), 'No approximate route from protected street; one-block jumps allowed.')

    required_doors = reqs.get('reachable_doors', 0 if task == 'pocket-park' else 1)
    if required_doors > 0 and not doors:
        add('missing_door', (0, 0, 0), 'Task requires a building entrance.')

    completion = _assess_completion(
        fixture=fixture,
        reqs=reqs,
        grid=grid,
        edits=edits,
        block_fn=block,
        w=w,
        h=h,
        d=d,
        issues=issues,
        reachable_doors=reachable_doors,
        seen=seen,
        seed_cols=seed_cols,
        unpaired_bed_positions=unpaired_bed_positions,
        subsurface_void_cols=subsurface_void_cols,
    )

    return {
        'schema_version': 3,
        'evaluator_version': __version__,
        'task': task,
        'scale': fixture.get('scale') or spec.get('scale', 'small'),
        'bounds': bounds,
        'edited_cells': len(edits),
        'issues': issues,
        'counts': dict(Counter(i['code'] for i in issues)),
        'completion': completion,
        'doors': doors,
        'reachable_doors': reachable_doors,
        'signs': [{'at': list(p), 'text': c[4]} for p, c in edits.items() if c[4] is not None],
        'props': [{'at': list(p), 'asset': c[6]} for p, c in edits.items() if c[6]],
        'review_status': 'Human visual review required',
        'limitations': [
            'Not a game physics engine or accessibility certification.',
            'Supported palette is a rendering vocabulary, not a complete Minecraft registry.',
            'No total score: inspect validity, task completion, geometry and visual quality separately.',
            'Passing completion checks confirms presence and approximate reachability, not architectural quality.',
        ],
    }


def _check_orphan_foliage(
    grid: dict[tuple[int, int, int], list[Any]],
    w: int,
    h: int,
    d: int,
    repair_rect: list[int] | None,
    add: Any,
) -> None:
    leaf_positions: set[tuple[int, int, int]] = set()
    roots: deque[tuple[int, int, int, int]] = deque()
    visited: dict[tuple[int, int, int], int] = {}
    for (x, y, z), c in grid.items():
        if not (0 <= x < w and 0 <= y < h and 0 <= z < d):
            continue
        b = name(c[3])
        if b.endswith('_leaves'):
            leaf_positions.add((x, y, z))
        elif b.endswith(('_log', '_wood')) or b in ('bamboo_block', 'stripped_bamboo_block') or b in FLORA_SOIL:
            roots.append((x, y, z, 0))
            visited[x, y, z] = 0

    while roots:
        x, y, z, dist = roots.popleft()
        if dist >= 6:
            continue
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            np = (x + dx, y + dy, z + dz)
            if np in leaf_positions and np not in visited:
                visited[np] = dist + 1
                roots.append((np[0], np[1], np[2], dist + 1))

    rx0, rz0, rx1, rz1 = repair_rect if repair_rect else (0, 0, w - 1, d - 1)
    orphans = {
        p for p in leaf_positions
        if p not in visited and rx0 <= p[0] <= rx1 and rz0 <= p[2] <= rz1
    }
    seen_orphans: set[tuple[int, int, int]] = set()
    for p in sorted(orphans):
        if p in seen_orphans:
            continue
        cluster = [p]
        seen_orphans.add(p)
        q = deque([p])
        while q:
            cx, cy, cz = q.popleft()
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                nb = (cx + dx, cy + dy, cz + dz)
                if nb in orphans and nb not in seen_orphans:
                    seen_orphans.add(nb)
                    cluster.append(nb)
                    q.append(nb)
        add('orphan_foliage', cluster[0], f'Floating foliage cluster ({len(cluster)} cells) has no trunk or ground connection.')


def _check_subsurface_voids(
    edits: dict[tuple[int, int, int], list[Any]],
    block_fn: Any,
    repair_rect: list[int] | None,
    w: int,
    h: int,
    d: int,
    add: Any,
) -> int:
    rx0, rz0, rx1, rz1 = repair_rect if repair_rect else (0, 0, w - 1, d - 1)
    edited_cols = {(x, z) for (x, _, z) in edits if rx0 <= x <= rx1 and rz0 <= z <= rz1}
    void_locs: list[tuple[int, int, int]] = []
    for x, z in sorted(edited_cols):
        top_soil = None
        for y in range(h - 1, 1, -1):
            b = name(block_fn((x, y, z)))
            if b in FLORA_SOIL:
                top_soil = y
                break
        if top_soil is not None and top_soil >= 3:
            if name(block_fn((x, top_soil - 1, z))) == 'air' or name(block_fn((x, top_soil - 2, z))) == 'air':
                void_locs.append((x, top_soil, z))
    for loc in void_locs[:8]:
        add('subsurface_void', loc, f'Terrain turf sits over a hollow subsurface air cavity ({len(void_locs)} hollow columns total).')
    return len(void_locs)


def _check_interior_darkness(
    grid: dict[tuple[int, int, int], list[Any]],
    edits: dict[tuple[int, int, int], list[Any]],
    block_fn: Any,
    w: int,
    h: int,
    d: int,
    add: Any,
) -> None:
    def idx(x: int, y: int, z: int) -> int:
        return (y * d + z) * w + x

    total = w * h * d
    light = bytearray(total)
    trans = bytearray(total)
    buckets: list[list[tuple[int, int, int]]] = [[] for _ in range(16)]

    for y in range(h):
        for z in range(d):
            for x in range(w):
                st = block_fn((x, y, z))
                i = idx(x, y, z)
                if _transmits_light(st):
                    trans[i] = 1
                em = _emission(st)
                if em > 0:
                    light[i] = em
                    buckets[em].append((x, y, z))

    for x in range(w):
        for z in range(d):
            for y in range(h - 1, -1, -1):
                i = idx(x, y, z)
                if not trans[i] or name(block_fn((x, y, z))) == 'water':
                    break
                if light[i] < 15:
                    light[i] = 15
                    buckets[15].append((x, y, z))

    for lv in range(15, 1, -1):
        nxt = lv - 1
        for x, y, z in buckets[lv]:
            if light[idx(x, y, z)] != lv:
                continue
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                nx, ny, nz = x + dx, y + dy, z + dz
                if 0 <= nx < w and 0 <= ny < h and 0 <= nz < d:
                    ni = idx(nx, ny, nz)
                    if trans[ni] and light[ni] < nxt:
                        light[ni] = nxt
                        buckets[nxt].append((nx, ny, nz))

    edited_cols = {(x, z) for (x, _, z) in edits}
    dark_cells: set[tuple[int, int, int]] = set()
    for x, z in edited_cols:
        if not (0 <= x < w and 0 <= z < d):
            continue
        has_roof_above = False
        for y in range(h - 1, 0, -1):
            st = block_fn((x, y, z))
            if not _transmits_light(st) and name(st) not in FLORA_SOIL and name(st) != 'stone':
                has_roof_above = True
            elif has_roof_above and y + 1 < h:
                if passable(st) and passable(block_fn((x, y + 1, z))) and flush_top(block_fn((x, y - 1, z))):
                    if light[idx(x, y, z)] < 4 and light[idx(x, y + 1, z)] < 4:
                        dark_cells.add((x, y, z))

    visited: set[tuple[int, int, int]] = set()
    for p in sorted(dark_cells):
        if p in visited:
            continue
        cluster = [p]
        visited.add(p)
        q = deque([p])
        while q:
            cx, cy, cz = q.popleft()
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
                nb = (cx + dx, cy + dy, cz + dz)
                if nb in dark_cells and nb not in visited:
                    visited.add(nb)
                    cluster.append(nb)
                    q.append(nb)
        if len(cluster) >= 4:
            add('dark_interior', cluster[0], f'Enclosed interior room is unlit ({len(cluster)} floor cells below light level 4).', 'warn')


def _assess_completion(
    *,
    fixture: dict[str, Any],
    reqs: dict[str, Any],
    grid: dict[tuple[int, int, int], list[Any]],
    edits: dict[tuple[int, int, int], list[Any]],
    block_fn: Any,
    w: int,
    h: int,
    d: int,
    issues: list[dict[str, Any]],
    reachable_doors: list[list[int]],
    seen: set[tuple[int, int, int]],
    seed_cols: set[tuple[int, int]],
    unpaired_bed_positions: set[tuple[int, int, int]],
    subsurface_void_cols: int,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(req_name: str, expected: Any, observed: Any, met: bool) -> None:
        checks.append({
            'requirement': req_name,
            'expected': expected,
            'observed': observed,
            'met': bool(met),
        })

    non_air_edits = sum(1 for c in edits.values() if name(c[3]) != 'air')
    if 'min_edited_cells' in reqs:
        target = reqs['min_edited_cells']
        record('min_edited_cells', target, non_air_edits, non_air_edits >= target)

    if 'min_peak_height' in reqs:
        target = reqs['min_peak_height']
        peak_y = max((y for (_, y, _), c in edits.items() if name(c[3]) != 'air'), default=0)
        record('min_peak_height', target, peak_y, peak_y >= target)

    if reqs.get('reachable_doors', 0) > 0:
        target = reqs['reachable_doors']
        record('reachable_doors', target, len(reachable_doors), len(reachable_doors) >= target)

    if 'south_bank_door_min_z' in reqs:
        min_z = reqs['south_bank_door_min_z']
        cnt = sum(1 for dr in reachable_doors if dr[2] >= min_z)
        record('reachable_south_bank_entrance', f'z>={min_z}', cnt, cnt >= 1)

    if 'summit_door_min_y' in reqs:
        min_y = reqs['summit_door_min_y']
        cnt = sum(1 for dr in reachable_doors if dr[1] >= min_y)
        record('reachable_summit_entrance', f'y>={min_y}', cnt, cnt >= 1)

    if 'upper_storey_min_y' in reqs:
        min_y = reqs['upper_storey_min_y']
        upper_cells = {
            (x, z) for (x, z, hh) in seen
            if (x, z) not in seed_cols and hh >= 2 * min_y
        }
        record('reachable_upper_storey', f'>=8 cells at y>={min_y}', len(upper_cells), len(upper_cells) >= 8)

    for tier_y in reqs.get('reachable_floor_tiers', []):
        tier_cells = {
            (x, z) for (x, z, hh) in seen
            if (x, z) not in seed_cols and hh >= 2 * tier_y
        }
        record(f'reachable_tier:y>={tier_y}', f'>=6 cells at y>={tier_y}', len(tier_cells), len(tier_cells) >= 6)

    if 'aircraft_warning_light_min_y' in reqs:
        min_y = reqs['aircraft_warning_light_min_y']
        beacons = sum(
            1 for (_, y, _), c in edits.items()
            if name(c[3]) in ('redstone_torch', 'redstone_wall_torch') and y >= min_y
        )
        record('aircraft_warning_light', f'>=1 at y>={min_y}', beacons, beacons >= 1)

    if 'reachable_interior_cells' in reqs:
        target = reqs['reachable_interior_cells']
        interior = {(x, z) for (x, z, _) in seen if z >= 7 and (x, z) not in seed_cols}
        record('reachable_interior_path', target, len(interior), len(interior) >= target)

    if 'reachable_promenade_z' in reqs:
        z0, z1 = reqs['reachable_promenade_z']
        prom = {(x, z) for (x, z, _) in seen if z0 <= z <= z1}
        record('reachable_promenade', f'>=10 cells in z={z0}..{z1}', len(prom), len(prom) >= 10)

    if reqs.get('dual_frontage_glazing'):
        north_glass = any(
            'glass' in name(c[3]) for (x, y, z), c in edits.items()
            if y >= 3 and 5 <= z <= 7 and x >= 4
        )
        west_glass = any(
            'glass' in name(c[3]) for (x, y, z), c in edits.items()
            if y >= 3 and 4 <= x <= 6 and z >= 5
        )
        record(
            'dual_frontage_glazing',
            'north and west street fronts',
            {'north': north_glass, 'west': west_glass},
            north_glass and west_glass,
        )

    for asset in reqs.get('assets', []):
        if asset in ASSETS:
            present = sum(1 for c in edits.values() if c[6] == asset and name(c[3]) != 'air')
            record(f'prop:{asset}', 1, present, present >= 1)

    if 'signs' in reqs:
        target = reqs['signs']
        valid_signs = sum(
            1 for c in edits.values()
            if name(c[3]).endswith(('_sign', '_hanging_sign', '_wall_hanging_sign'))
            and any(s.strip() for s in (c[4] or []))
        )
        record('mounted_signs', target, valid_signs, valid_signs >= target)

    if 'beds' in reqs:
        target = reqs['beds']
        paired_feet = sum(
            1 for pos, c in edits.items()
            if name(c[3]).endswith('_bed')
            and state_parts(c[3])[1].get('part', 'foot') == 'foot'
            and pos not in unpaired_bed_positions
        )
        record('paired_beds', target, paired_feet, paired_feet >= target)

    if 'bookshelves' in reqs:
        target = reqs['bookshelves']
        cnt = sum(1 for c in edits.values() if name(c[3]) == 'bookshelf')
        record('bookshelves', target, cnt, cnt >= target)

    if 'seating' in reqs:
        target = reqs['seating']
        seats = sum(
            1 for (_, y, _), c in edits.items()
            if name(c[3]).endswith('_stairs')
            and state_parts(c[3])[1].get('half', 'bottom') == 'bottom'
            and y <= h - 4
        )
        record('seating', target, seats, seats >= target)

    if 'conifer_leaves' in reqs:
        target = reqs['conifer_leaves']
        cnt = sum(1 for c in edits.values() if name(c[3]) == 'spruce_leaves')
        record('conifer_foliage', target, cnt, cnt >= target)

    if 'broadleaf_leaves' in reqs:
        target = reqs['broadleaf_leaves']
        cnt = sum(1 for c in edits.values() if name(c[3]) in BROADLEAF_BLOCKS)
        record('broadleaf_foliage', target, cnt, cnt >= target)

    if 'flora' in reqs:
        target = reqs['flora']
        cnt = sum(
            1 for c in edits.values()
            if name(c[3]) in GROUND_FLORA or name(c[3]).startswith('potted_')
        )
        record('planted_flora', target, cnt, cnt >= target)

    if 'lights' in reqs:
        target = reqs['lights']
        cnt = sum(1 for c in edits.values() if name(c[3]) in LIGHT_BLOCKS)
        record('lighting', target, cnt, cnt >= target)

    if 'water_cells' in reqs:
        target = reqs['water_cells']
        cnt = sum(1 for c in edits.values() if name(c[3]) == 'water')
        record('water_feature', target, cnt, cnt >= target)

    if reqs.get('forbid_new_build_claim'):
        contradictions = sum(1 for i in issues if i['code'] == 'contradictory_renovation_date')
        record('honest_renovation_dating', 0, contradictions, contradictions == 0)

    # --- Terraforming & chunk-error completion checks ---
    if reqs.get('check_orphan_foliage'):
        orphans = sum(1 for i in issues if i['code'] == 'orphan_foliage')
        record('cleared_corrupted_artifacts', 0, orphans, orphans == 0)

    if reqs.get('no_subsurface_voids'):
        record('solid_subsurface_fill', 0, subsurface_void_cols, subsurface_void_cols == 0)

    if 'smooth_chunk_seam' in reqs:
        threshold = float(reqs['smooth_chunk_seam'])
        seam_pairs = fixture.get('seam_pairs') or []
        if seam_pairs:
            matched = 0
            for (ix, iz), (ox, oz) in seam_pairs:
                iy, _ = _surface_info(block_fn, ix, iz, h)
                oy, _ = _surface_info(block_fn, ox, oz, h)
                if abs(iy - oy) <= 1:
                    matched += 1
            ratio = round(matched / len(seam_pairs), 3)
            record('smooth_chunk_seam', threshold, ratio, ratio >= threshold)

    if reqs.get('reconnected_road'):
        ep = fixture.get('road_endpoints') or {'start': [], 'end': []}
        ok = _check_road_connectivity(block_fn, w, h, d, ep['start'], ep['end'])
        record('reconnected_road', True, ok, ok)

    if reqs.get('continuous_waterway'):
        ep = fixture.get('water_endpoints') or {'start': [], 'end': []}
        ok = _check_water_connectivity(block_fn, w, h, d, ep['start'], ep['end'])
        record('continuous_waterway', True, ok, ok)

    if 'surface_top_dressing' in reqs:
        threshold = float(reqs['surface_top_dressing'])
        rrect = fixture.get('repair_rect') or [0, 0, w - 1, d - 1]
        rx0, rz0, rx1, rz1 = rrect
        total_cols = 0
        dressed_cols = 0
        for x in range(rx0, rx1 + 1):
            for z in range(rz0, rz1 + 1):
                total_cols += 1
                _, sb = _surface_info(block_fn, x, z, h)
                if sb != 'air' and sb not in RAW_SCAR_BLOCKS:
                    dressed_cols += 1
        ratio = round(dressed_cols / max(1, total_cols), 3)
        record('surface_top_dressing', threshold, ratio, ratio >= threshold)

    met_count = sum(1 for item in checks if item['met'])
    return {
        'complete': met_count == len(checks),
        'met_count': met_count,
        'total_count': len(checks),
        'checks': checks,
    }


def _check_road_connectivity(
    block_fn: Any, w: int, h: int, d: int, starts: list[list[int]], ends: list[list[int]]
) -> bool:
    road_y: dict[tuple[int, int], int] = {}
    for x in range(w):
        for z in range(d):
            sy, sb = _surface_info(block_fn, x, z, h)
            if sb in ROAD_SURFACE_BLOCKS and passable(block_fn((x, sy + 1, z))):
                road_y[x, z] = sy
    targets = {(pt[0], pt[1]) for pt in ends if (pt[0], pt[1]) in road_y}
    if not targets:
        return False
    visited = {(pt[0], pt[1]) for pt in starts if (pt[0], pt[1]) in road_y}
    q = deque(visited)
    while q:
        x, z = q.popleft()
        if (x, z) in targets:
            return True
        cy = road_y[x, z]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (x + dx, z + dz)
            if nb in road_y and nb not in visited and abs(road_y[nb] - cy) <= 1:
                visited.add(nb)
                q.append(nb)
    return False


def _check_water_connectivity(
    block_fn: Any, w: int, h: int, d: int, starts: list[list[int]], ends: list[list[int]]
) -> bool:
    water_y: dict[tuple[int, int], set[int]] = {}
    for x in range(w):
        for z in range(d):
            ys = {y for y in range(1, h) if name(block_fn((x, y, z))) == 'water'}
            if ys:
                water_y[x, z] = ys
    targets = {(pt[0], pt[1]) for pt in ends if (pt[0], pt[1]) in water_y}
    if not targets:
        return False
    visited = {(pt[0], pt[1]) for pt in starts if (pt[0], pt[1]) in water_y}
    q = deque(visited)
    while q:
        x, z = q.popleft()
        if (x, z) in targets:
            return True
        cys = water_y[x, z]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (x + dx, z + dz)
            if nb in water_y and nb not in visited:
                if any(abs(ny - cy) <= 1 for ny in water_y[nb] for cy in cys):
                    visited.add(nb)
                    q.append(nb)
    return False


def evaluate(run: str | Path, build: str | Path, out: str | Path) -> dict[str, Any]:
    fixture = verify_run(run)
    submission = load_json(build)
    report = assess(fixture, submission)
    report['submission_sha256'] = hashlib.sha256(Path(build).read_bytes()).hexdigest()
    report['evaluator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def summarize_reports(named_reports: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for label, rep in named_reports:
        issues = rep.get('issues', [])
        comp = rep.get('completion') or {'complete': False, 'met_count': 0, 'total_count': 0, 'checks': []}
        errors = sum(1 for i in issues if i.get('severity') == 'error')
        warnings = sum(1 for i in issues if i.get('severity') == 'warn')
        unmet = [c['requirement'] for c in comp.get('checks', []) if not c.get('met')]
        entries.append({
            'label': label,
            'task': rep.get('task', 'unknown'),
            'scale': rep.get('scale', 'unknown'),
            'edited_cells': rep.get('edited_cells', 0),
            'errors': errors,
            'warnings': warnings,
            'complete': bool(comp.get('complete')),
            'completion_met': comp.get('met_count', 0),
            'completion_total': comp.get('total_count', 0),
            'unmet_requirements': unmet,
            'issue_counts': rep.get('counts', {}),
        })
    return {
        'evaluator_version': __version__,
        'note': 'Validity, task completion, visual design and runtime remain separate dimensions; no combined score is computed.',
        'entries': entries,
    }
