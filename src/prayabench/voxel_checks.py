"""Check how a new voxel case satisfies its scene-specific brief."""
from collections import deque

from .scene import RAIL_BLOCKS, flush_top, full_block, name, passable, state_parts
from .voxel_tasks import EXTRA_VOXEL, VEHICLES, road_center, rotate_xz, vehicle_rect

NEIGHBORS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
PAVING = {'gray_concrete', 'black_concrete'}
WHEELS = {'black_concrete', 'black_wool', 'coal_block'}


def _flood(cells, starts):
    seen = set(starts) & cells
    queue = deque(seen)
    while queue:
        x, y, z = queue.popleft()
        for dx, dy, dz in NEIGHBORS:
            neighbor = (x + dx, y + dy, z + dz)
            if neighbor in cells and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def add_scene_checks(fixture, grid, edits, block, seen, record):
    task = fixture['task']
    if task not in EXTRA_VOXEL:
        return
    if task in VEHICLES:
        _vehicle(task, fixture['facing'], edits, block, record)
    elif task in ('diagonal-road', 'curved-tunnel'):
        _civil(task, edits, block, record)
    elif task == 'junction-wayfinding':
        _sightline(grid, block, record)
    elif task.startswith('specimen-'):
        _tree(task, edits, block, record)
    elif task in ('washroom-fitout', 'roof-hvac'):
        _fitout(task, edits, block, record)
    else:
        _retrofit(task, fixture, grid, edits, block, seen, record)


def _vehicle(task, facing, edits, block, record):
    x0, z0, width, length = vehicle_rect(task)
    _, _, height, _ = VEHICLES[task]
    min_y = 2 if task == 'harbour-ferry' else 4 if task == 'rail-coach' else 3
    canonical = {rotate_xz(x, z, facing): (x - x0, z - z0)
                 for x in range(x0, x0 + width) for z in range(z0, z0 + length)}
    occupied = {p: c for p, c in edits.items() if name(c[3]) not in ('air', 'water')}
    local = {}
    for (x, y, z), cell in occupied.items():
        if (x, z) in canonical and min_y <= y < min_y + height:
            across, along = canonical[x, z]
            local[across, y - min_y, along] = cell
    record('vehicle_envelope', 0, len(occupied) - len(local), len(occupied) == len(local))
    reached = _flood(set(local), [next(iter(local))] if local else [])
    record('one_connected_body', 'all vehicle cells', len(reached), bool(local) and len(reached) == len(local))
    projections = {(x, z) for x, _, z in local}
    extents = [len({x for x, z in projections}), len({z for x, z in projections})]
    record('vehicle_footprint', [width, length], extents, extents == [width, length])
    windshield = sum(z <= 2 and y >= 1 and 'glass' in name(c[3]) for (x, y, z), c in local.items())
    record('front_glazing', 'at least 2 blocks', windshield, windshield >= 2)
    families = ('_wall_sign', '_wall_banner', '_pane', '_slab', '_stairs', '_trapdoor', '_button', 'hopper', 'snow')
    details = sorted({family for c in local.values() for family in families if name(c[3]).endswith(family)})
    record('partial_block_detail', 'at least 2 types', details, len(details) >= 2)

    if task != 'harbour-ferry':
        wheel_edges = (1, 3) if task == 'rail-coach' else (0, width - 1)
        axle_rows = [z for z in range(length) if all(
            (x, 0, z) in local and name(local[x, 0, z][3]) in WHEELS for x in wheel_edges)]
        record('separated_wheelsets', '2 or more rows at least 3 blocks apart', axle_rows,
               len(axle_rows) >= 2 and axle_rows[-1] - axle_rows[0] >= 3)
        low_cells = {(x, z) for x, y, z in local if y == 0}
        expected_contact = {(x, z) for x in wheel_edges for z in axle_rows}
        record('wheel_clearance', 0, len(low_cells - expected_contact), bool(low_cells) and low_cells == expected_contact)
        if task == 'rail-coach':
            rails = [name(block((tx, min_y - 1, tz))) == 'rail'
                     for x, z in expected_contact for tx, tz in [rotate_xz(x + x0, z + z0, facing)]]
            record('rail_alignment', 'all wheel contacts over rails', sum(rails), bool(rails) and all(rails))
    if task == 'box-truck':
        cab, cargo = (max((y for _, y, z in local if test(z)), default=-1)
                      for test in (lambda z: z < 3, lambda z: z >= 3))
        enclosed = all(any((x, 3, z) in local and full_block(local[x, 3, z][3]) for x in range(1, width - 1))
                       and all((edge, 2, z) in local and full_block(local[edge, 2, z][3]) for edge in (0, width - 1))
                       for z in range(3, length))
        record('cab_and_cargo_box', 'lower cab and covered cargo box', {'cab': cab, 'cargo': cargo}, 1 <= cab < cargo and enclosed)
    elif task in ('city-bus', 'ambulance'):
        target_face = (('east', 'south', 'west', 'north') if task == 'city-bus' else
                       ('south', 'west', 'north', 'east'))[('north', 'east', 'south', 'west').index(facing)]
        doors = 0
        for (x, y, z), cell in local.items():
            b, p = state_parts(cell[3])
            on_side = x == width - 1 and 2 <= z < length - 1 if task == 'city-bus' else z == length - 1
            upper = local.get((x, y + 1, z), [0, 0, 0, 'air'])
            if on_side and b.endswith('_door') and p.get('half') == 'lower' and p.get('facing') == target_face:
                ub, up = state_parts(upper[3])
                doors += ub == b and up.get('half') == 'upper' and up.get('facing') == target_face
        record('kerbside_door' if task == 'city-bus' else 'rear_access_door', target_face, doors, doors > 0)
        if task == 'city-bus':
            boards = [c[4] for (x, y, z), c in local.items()
                      if z == 0 and c[4] and any(line.strip() for line in c[4])
                      and state_parts(c[3])[1].get('facing') == facing]
            record('destination_board', 'front-facing and legible', boards, bool(boards))
        else:
            lights = sum(y >= 2 and name(c[3]) in ('redstone_torch', 'redstone_wall_torch', 'redstone_lamp')
                         for (_, y, _), c in local.items())
            record('emergency_lights', 'at least 2', lights, lights >= 2)
    elif task == 'rail-coach':
        couplings = [z for z in (0, length - 1)
                     if (width // 2, 1, z) in local and name(local[width // 2, 1, z][3]) in ('iron_bars', 'hopper', 'chain', 'iron_chain')]
        record('both_couplings', [0, length - 1], couplings, len(couplings) == 2)
    else:
        hull_rows = {z for (x, y, z), c in local.items() if y == 0 and full_block(c[3])}
        record('waterline_hull', 'at least 12 lengthwise rows', len(hull_rows), len(hull_rows) >= 12)
        wheelhouse = sum(z < length // 2 and y >= 2 and 'glass' in name(c[3]) for (_, y, z), c in local.items())
        record('glazed_wheelhouse', 'at least 4 bow-half blocks', wheelhouse, wheelhouse >= 4)
        lamp_names = {'lantern', 'soul_lantern', 'redstone_torch', 'redstone_wall_torch', 'redstone_lamp'}
        sides = {x for (x, y, z), c in local.items() if x in (0, width - 1) and y >= 1 and name(c[3]) in lamp_names}
        record('navigation_lights', 'one per side', len(sides), len(sides) == 2)


def _civil(task, edits, block, record):
    tunnel = task == 'curved-tunnel'
    pavement = {'stone_bricks'} if tunnel else PAVING
    columns = {(x, z) for z in range(4, 20) for x in range(road_center(z) - 1, road_center(z) + 2)}
    bad = [(x, z) for x, z in sorted(columns)
           if name(block((x, 2, z))) not in pavement or not full_block(block((x, 1, z)))]
    record('continuous_three_wide_paving', 'all 48 columns supported', bad, not bad)
    obstructed = [(x, y, z) for x, z in sorted(columns) for y in range(3, 6 if tunnel else 5)
                  if name(block((x, y, z))) != 'air']
    record('unobstructed_cross_section', 0, obstructed, not obstructed)
    if tunnel:
        holes = [(x, z) for x, z in sorted(columns) if not full_block(block((x, 6, z)))]
        record('intact_bore_roof', 0, holes, not holes)
    else:
        surplus = [(x, y, z) for (x, y, z), c in edits.items()
                   if name(c[3]) in PAVING and (y != 2 or not 4 <= z < 20 or abs(x - road_center(z)) > 2)]
        record('paving_in_corridor', 0, surplus, not surplus)


def _sightline(grid, block, record):
    cell = grid.get((11, 5, 14), [0, 0, 0, 'air', None])
    b, p = state_parts(cell[3])
    oriented = (b == 'oak_sign' and p.get('rotation') == '8'
                or b == 'oak_wall_sign' and p.get('facing') == 'north')
    text = {s.strip().casefold() for s in cell[4] or []}
    record('north_facing_wayfinding', ['ferry', 'right'], sorted(text), oriented and {'ferry', 'right'} <= text)
    blockers = [(11, 5, z) for z in range(5, 14) if name(block((11, 5, z))) != 'air']
    record('clear_approach_sightline', 0, blockers, not blockers)
    support_z = 15 if b == 'oak_wall_sign' else 14
    top = 5 if b == 'oak_wall_sign' else 4
    anchored = all(
        full_block(block((11, y, support_z)))
        or (b == 'oak_sign' and (name(block((11, y, support_z))).endswith(('_wall', '_fence', '_pane')) or name(block((11, y, support_z))) in ('iron_bars', 'iron_chain', 'chain')))
        for y in range(2, top + 1)
    )
    record('grounded_sign_support', 'continuous post to grade', anchored, anchored)


def _tree(task, edits, block, record):
    wood = 'spruce' if task == 'specimen-conifer' else 'oak'
    logs = {p for p, c in edits.items() if name(c[3]) == wood + '_log' and p[1] > 2}
    leaves = {p for p, c in edits.items() if name(c[3]) == wood + '_leaves' and p[1] > 2}
    root = (10, 3, 10)
    tree = logs | leaves
    reached = _flood(tree, [root] if root in logs else [])
    trunk = next((y - 3 for y in range(3, 21) if (10, y, 10) not in logs), 18)
    record('rooted_trunk', 'at least 5 vertical logs', trunk, trunk >= 5 and full_block(block((10, 2, 10))))
    record('continuous_tree', 'all wood and foliage connected', len(reached), bool(tree) and tree == reached)
    stray = [p for p, c in edits.items() if name(c[3]) != 'air' and p not in tree]
    record('tree_materials', 0, len(stray), not stray)
    persistent = all(state_parts(edits[p][3])[1].get('persistent') == 'true' for p in leaves)
    profile = {y: sum(1 for p in leaves if p[1] == y) for y in {p[1] for p in leaves}}
    record('persistent_canopy', '3 foliage heights, at least 24 leaves', sorted(profile.items()),
           persistent and len(leaves) >= 24 and len(profile) >= 3)
    if wood == 'spruce':
        peak = max(profile, default=0)
        record('tapered_crown', 'top of crown narrower than lower tier', profile.get(peak, 0),
               0 < profile.get(peak, 0) <= 5 and max(profile.values(), default=0) >= 12)
    else:
        span = max((p[0] for p in leaves), default=0) - min((p[0] for p in leaves), default=0) + 1
        branches = {(x, z) for x, y, z in logs if 5 <= y and (x, z) != (10, 10)}
        record('spreading_crown_and_branches', '7+ blocks across and 3+ off-trunk columns',
               {'span': span, 'branch_columns': len(branches)}, span >= 7 and len(branches) >= 3)


def _fitout(task, edits, block, record):
    low, high = (3, 6) if task == 'washroom-fitout' else (7, 10)
    stray = [p for p in edits if not (4 <= p[0] <= 12 and low <= p[1] <= high and 7 <= p[2] <= 11)]
    blocked = [(8, y, z) for y in (low, low + 1) for z in range(7, 12) if not passable(block((8, y, z)))]
    record('work_zone', 0, stray, not stray)
    record('clear_service_aisle', 0, blocked, not blocked)
    if task == 'washroom-fitout':
        # Washroom standard: counter-set basin + tripwire_hook tap + mirror,
        # and partitioned toilet stall with door + water_cauldron bowl + open iron_trapdoor lid + flush button.
        sinks = [
            (x, y, z) for (x, y, z), c in edits.items()
            if 4 <= x <= 6 and y == 3 and name(c[3]) == 'water_cauldron'
            and name(block((x, 4, z))) == 'tripwire_hook'
            and any(flush_top(block((x + dx, 3, z + dz))) and name(block((x + dx, 3, z + dz))) != 'water_cauldron'
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 4 <= x + dx <= 6 and 7 <= z + dz <= 11)
        ]
        mirrors = [
            (x, y, z) for (x, y, z), c in edits.items()
            if x == 4 and 'glass' in name(c[3]) and y in (4, 5) and full_block(block((3, y, z)))
            and any(abs(z - sz) <= 1 for _, _, sz in sinks)
        ]
        toilets = []
        for (x, y, z), c in edits.items():
            if 10 <= x <= 12 and y == 3 and name(c[3]) == 'water_cauldron':
                lid_b, lid_p = state_parts(block((x, 4, z)))
                has_lid = lid_b == 'iron_trapdoor' and lid_p.get('open') == 'true'
                has_flush = any(name(block((x, fy, z))).endswith('_button') for fy in (4, 5))
                if has_lid and has_flush:
                    toilets.append((x, y, z))
        stall_doors = [
            (x, y, z) for (x, y, z), c in edits.items()
            if 9 <= x <= 12 and y == 3 and name(c[3]).endswith('_door')
            and state_parts(c[3])[1].get('half', 'lower') == 'lower'
        ]
        partitions = sum(1 for (x, y, z), c in edits.items() if 9 <= x <= 12 and y in (3, 4) and full_block(c[3]))
        lamp = [p for p, c in edits.items() if name(c[3]) in ('lantern', 'sea_lantern', 'end_rod', 'wall_torch', 'shroomlight')]
        record('vanity_basin_tap_and_mirror', 'counter basin + tripwire_hook tap + west mirror',
               {'basins': sinks, 'mirrors': mirrors}, bool(sinks) and bool(mirrors))
        record('partitioned_toilet_stall', 'cauldron bowl + raised iron lid + flush button + stall door/walls',
               {'toilets': toilets, 'doors': stall_doors, 'partitions': partitions},
               bool(toilets) and bool(stall_doors) and partitions >= 4)
        record('washroom_lamp', 'at least one', lamp, bool(lamp))
    else:
        housing_mats = {
            'white_concrete', 'smooth_quartz', 'quartz_block', 'light_gray_concrete',
            'iron_block', 'polished_andesite', 'smooth_stone',
        }
        housing = {
            p for p, c in edits.items()
            if name(c[3]) in housing_mats or name(c[3]).endswith('shulker_box')
        }
        grounded = [p for p in housing if p[1] == 7 and full_block(block((p[0], 6, p[2])))]
        connected = _flood(housing, grounded)
        record('connected_roof_housing', '8+ grounded connected housing blocks', len(connected),
               len(connected) >= 8 and connected == housing)
        grille = [
            (x, y, z) for (x, y, z), c in edits.items()
            if z == 7 and (
                name(c[3]) == 'iron_bars'
                or (name(c[3]) == 'iron_trapdoor'
                    and state_parts(c[3])[1].get('facing') == 'north'
                    and state_parts(c[3])[1].get('open') == 'true')
            ) and (x, y, z + 1) in housing
        ]
        record('front_grille', '2+ backed grille blocks', grille, len(grille) >= 2)
        fan_rails = [(x, y, z) for (x, y, z), c in edits.items() if name(c[3]) in RAIL_BLOCKS and (x, y - 1, z) in housing]
        hvac_heads = [p for p, c in edits.items() if c[6] in ('ac_unit', 'wall_vent')]
        record('praya_fan_and_hvac_form', '2+ top fan rails and ac_unit/wall_vent props',
               {'fan_rails': len(fan_rails), 'hvac_heads': len(hvac_heads)},
               len(fan_rails) >= 2 and len(hvac_heads) >= 1)


def _retrofit(task, fixture, grid, edits, block, seen, record):
    base = {tuple(c[:3]): c for c in fixture['cells']}
    changed = {
        p for p, c in edits.items()
        if (c[3], c[4], c[6], c[7] if len(c) > 7 else None) != (
            base.get(p, [0, 0, 0, 'air', None, '', None, None])[3],
            base.get(p, [0, 0, 0, 'air', None, '', None, None])[4],
            base.get(p, [0, 0, 0, 'air', None, '', None, None])[6] if len(base.get(p, [])) > 6 else None,
            base.get(p, [0, 0, 0, 'air', None, '', None, None])[7] if len(base.get(p, [])) > 7 else None,
        )
    }
    if task == 'inspector-repair':
        allowed = {(5, 5, 6), (12, 6, 9), (5, 5, 7), (8, 3, 6)}
        record('minimal_repair', 'only 4 specified positions', len(changed), changed <= allowed)
        record('removed_floating_fixtures', 2, sum(name(block(p)) == 'air' for p in ((5, 5, 6), (12, 6, 9))),
               all(name(block(p)) == 'air' for p in ((5, 5, 6), (12, 6, 9))))
        sign = grid.get((5, 5, 7), [0, 0, 0, 'air', None])
        record('relocated_sign', 'Cafe hours', sign[4], sign[4] == ['Cafe hours'] and sign[3] == 'oak_wall_sign[facing=north]')
        record('reopened_entrance', True, (8, 8, 6) in seen, name(block((8, 3, 6))) == 'air' and (8, 8, 6) in seen)
    elif task == 'facade-depth-retrofit':
        outside = [p for p in changed if not (4 <= p[0] <= 16 and 3 <= p[1] <= 9 and 5 <= p[2] <= 6)]
        piers = sum(all(full_block(block((x, y, 6))) for y in range(3, 8)) for x in (4, 16))
        projection = [x for x in range(5, 16) if not passable(block((x, 8, 5)))]
        windows = sum('glass' in name(block((x, y, 7))) and all(name(block((x, y, z))) == 'air' for z in (5, 6))
                      for x in range(5, 16) for y in (5, 6))
        entry = all(passable(block((10, y, z))) for y in (3, 4) for z in (5, 6))
        record('bounded_retrofit', 'within work zone, ≤80 changes', {'changes': len(changed), 'outside': outside}, len(changed) <= 80 and not outside)
        record('grounded_side_piers', 2, piers, piers == 2)
        record('continuous_facade_projection', 11, len(projection), len(projection) == 11)
        record('visible_original_windows', 12, windows, windows >= 12)
        record('clear_original_entrance', True, entry, entry)
    else:
        outside = [p for p in changed if not (5 <= p[0] <= 13 and 3 <= p[1] <= 5 and 8 <= p[2] <= 13)]
        record('bounded_conversion', 'within work zone, ≤55 changes', {'changes': len(changed), 'outside': outside}, len(changed) <= 55 and not outside)
        upper = (14, 13, 16) in seen
        record('upper_stair_access', True, upper, upper)
