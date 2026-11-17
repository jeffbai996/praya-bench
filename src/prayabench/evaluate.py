"""Inspect geometry and brief completion without executing generated code. No opaque total score."""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from . import __version__
from .scene import (
    ASSETS, FLORA_SOIL, GROUND_FLORA, PALETTE, TALL_FLORA, VEC,
    flush_top, full_block, load_json, name, passable, state_parts, validate_cells,
)
from .tasks import TASK_SPECS, verify_run

LIGHT_BLOCKS = frozenset({
    'lantern', 'soul_lantern', 'sea_lantern', 'end_rod',
    'redstone_lamp', 'glowstone', 'torch', 'wall_torch', 'campfire', 'soul_campfire',
})
BROADLEAF_BLOCKS = frozenset({
    'oak_leaves', 'birch_leaves', 'jungle_leaves', 'acacia_leaves',
    'dark_oak_leaves', 'cherry_leaves', 'mangrove_leaves',
    'azalea_leaves', 'flowering_azalea_leaves',
})


def _can_hang_from(state: str) -> bool:
    b, _ = state_parts(state)
    if b in ('air', 'water') or b in GROUND_FLORA or b.endswith('_carpet'):
        return False
    return (
        full_block(state)
        or b.endswith(('_slab', '_stairs', '_fence', '_wall', '_bars', '_hanging_sign', '_wall_hanging_sign'))
        or b in ('chain', 'iron_chain', 'end_rod')
    )


def _can_support_standing_light(state: str) -> bool:
    b = name(state)
    return (
        flush_top(state)
        or b in ('iron_bars', 'chain', 'iron_chain', 'end_rod')
        or b.endswith(('_fence', '_wall', '_pane'))
    )


def block_from(grid: dict[tuple[int, int, int], list[Any]], pos: tuple[int, int, int]) -> str:
    return grid.get(pos, [0, 0, 0, 'air'])[3]


def assess(fixture: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    edits = validate_cells(submission)
    base = validate_cells({'cells': fixture['cells']})
    grid = base | edits
    protected = {tuple(p) for p in fixture['protected']}
    issues: list[dict[str, Any]] = []
    task = fixture['task']
    reqs = fixture.get('requirements') or TASK_SPECS.get(task, {}).get('requirements', {})

    def block(pos: tuple[int, int, int]) -> str:
        return grid.get(pos, [0, 0, 0, 'air'])[3]

    def add(code: str, pos: tuple[int, int, int], detail: str, severity: str = 'error') -> None:
        issues.append({'code': code, 'at': list(pos), 'detail': detail, 'severity': severity})

    source_chars = submission.get('source_characters')
    if submission.get('diagnostic_only') or (isinstance(source_chars, int) and source_chars > 14000):
        add(
            'source_budget_exceeded',
            (0, 0, 0),
            f'Submission exceeded the 14000-character source contract ({source_chars or "diagnostic"}).',
        )

    unpaired_bed_positions: set[tuple[int, int, int]] = set()

    for pos, c in edits.items():
        x, y, z = pos
        b, p = state_parts(c[3])
        if not (0 <= x <= 23 and 0 <= y <= 17 and 0 <= z <= 21):
            add('out_of_bounds', pos, 'Outside the declared scene.')
        if pos in protected and (
            c[3] != block_from(base, pos) or c[4] != base.get(pos, [0, 0, 0, 'air', None])[4]
        ):
            add('protected_change', pos, 'Changed protected terrain or historic architecture.')
        if b not in PALETTE:
            add('unsupported_block', pos, f'{b} is outside this evaluator’s declared palette; not a complete game registry verdict.')
        if p.get('facing') and p['facing'] not in VEC:
            add('invalid_facing', pos, 'Unknown facing direction.')
        if b == 'air':
            continue

        below = block((x, y - 1, z))
        above = block((x, y + 1, z))

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
            d = VEC.get(p.get('facing', 'north'), (0, 0, -1))
            back = block((x - d[0], y - d[1], z - d[2]))
            if not full_block(back):
                add('unsupported_wall_fixture', pos, f'Backing is {back}; requires a full wall face.')

        if b == 'player_head':
            if c[6] == 'mailbox_orange':
                if name(below) not in ('iron_bars', 'iron_chain', 'chain', 'glass_pane') and not name(below).endswith('_stained_glass_pane'):
                    add('mailbox_plinth', pos, 'Mailbox needs a slender bar, chain or glass post.')
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
            d = VEC.get(facing, (0, 0, -1))
            other = (x + d[0], y, z + d[2]) if part == 'foot' else (x - d[0], y, z - d[2])
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
            d = VEC.get(p.get('facing', 'north'), (0, 0, -1))
            hinge_back = block((x - d[0], y, z - d[2]))
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
            d = VEC.get(p.get('facing', 'up'), (0, 1, 0))
            support = block((x - d[0], y - d[1], z - d[2]))
            if name(support) == 'air':
                add('unsupported_rod', pos, 'No attachment at the rod base.')

        if 'glass' in b and y >= 3:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                npos = (x + dx, y, z + dz)
                if npos in protected and full_block(block_from(base, npos)):
                    add('blind_party_wall_glazing', pos, 'Glazing sits directly against an opaque protected neighbour wall.', 'warn')
                    break

    # Half-block-height approximation. Sources are ONLY protected street columns;
    # interior paving cannot seed a disconnected building as reachable.
    levels: dict[tuple[int, int], list[int]] = {}
    for x in range(24):
        for z in range(22):
            out: list[int] = []
            for y in range(18):
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
        else {(x, z) for x in range(24) for z in range(5)}
    )
    seen = {(x, z, h) for (x, z), hs in levels.items() if (x, z) in seed_cols for h in hs}
    q = deque(seen)
    while q:
        x, z, h = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for hh in levels.get((x + dx, z + dz), []):
                cand = (x + dx, z + dz, hh)
                if abs(hh - h) <= 2 and cand not in seen:
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
        task=task,
        reqs=reqs,
        edits=edits,
        issues=issues,
        reachable_doors=reachable_doors,
        seen=seen,
        seed_cols=seed_cols,
        unpaired_bed_positions=unpaired_bed_positions,
    )

    return {
        'schema_version': 2,
        'evaluator_version': __version__,
        'task': task,
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


def _assess_completion(
    *,
    task: str,
    reqs: dict[str, Any],
    edits: dict[tuple[int, int, int], list[Any]],
    issues: list[dict[str, Any]],
    reachable_doors: list[list[int]],
    seen: set[tuple[int, int, int]],
    seed_cols: set[tuple[int, int]],
    unpaired_bed_positions: set[tuple[int, int, int]],
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

    if reqs.get('reachable_doors', 0) > 0:
        target = reqs['reachable_doors']
        record('reachable_doors', target, len(reachable_doors), len(reachable_doors) >= target)

    if 'south_bank_door_min_z' in reqs:
        min_z = reqs['south_bank_door_min_z']
        cnt = sum(1 for d in reachable_doors if d[2] >= min_z)
        record('reachable_south_bank_entrance', f'z>={min_z}', cnt, cnt >= 1)

    if 'summit_door_min_y' in reqs:
        min_y = reqs['summit_door_min_y']
        cnt = sum(1 for d in reachable_doors if d[1] >= min_y)
        record('reachable_summit_entrance', f'y>={min_y}', cnt, cnt >= 1)

    if 'upper_storey_min_y' in reqs:
        min_y = reqs['upper_storey_min_y']
        upper_cells = {
            (x, z) for (x, z, h) in seen
            if (x, z) not in seed_cols and h >= 2 * min_y
        }
        record('reachable_upper_storey', f'>=8 cells at y>={min_y}', len(upper_cells), len(upper_cells) >= 8)

    if 'reachable_interior_cells' in reqs:
        target = reqs['reachable_interior_cells']
        interior = {(x, z) for (x, z, _) in seen if z >= 8 and (x, z) not in seed_cols}
        record('reachable_interior_path', target, len(interior), len(interior) >= target)

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
            1 for (x, y, z), c in edits.items()
            if name(c[3]).endswith('_stairs')
            and state_parts(c[3])[1].get('half', 'bottom') == 'bottom'
            and y <= 8
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

    if reqs.get('forbid_new_build_claim'):
        contradictions = sum(1 for i in issues if i['code'] == 'contradictory_renovation_date')
        record('honest_renovation_dating', 0, contradictions, contradictions == 0)

    met_count = sum(1 for item in checks if item['met'])
    return {
        'complete': met_count == len(checks),
        'met_count': met_count,
        'total_count': len(checks),
        'checks': checks,
    }


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
