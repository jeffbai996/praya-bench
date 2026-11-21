"""Deterministic acceptable reference examples for the 15 v0.4 voxel tasks."""
from __future__ import annotations

import random
from typing import Any

from ._examples_common import VehicleBuilder, VoxelBuilder
from .voxel_tasks import road_center, vehicle_rect


def _box_truck(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('box-truck')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    for lz in (1, 7):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    # Chassis & cab (lz=0..2, max ly=2 < cargo max ly=3) + fuel hoppers & wind deflector snow
    v.box(0, 1, 0, w - 1, 1, 2, 'blue_concrete')
    v.put(1, 1, 0, 'smooth_quartz')
    v.put(2, 1, 0, 'smooth_quartz')
    v.put(0, 1, 0, 'blue_shulker_box')
    v.put(3, 1, 0, 'blue_shulker_box')
    v.put(0, 1, 4, 'hopper')
    v.put(w - 1, 1, 4, 'hopper')
    v.box(0, 2, 1, w - 1, 2, 2, 'blue_concrete')
    for lx in (1, 2):
        v.put(lx, 2, 0, 'gray_stained_glass')
        v.put(lx, 3, 3, 'snow[layers=3]')
    v.put(0, 2, 0, 'gray_stained_glass_pane')
    v.put(3, 2, 0, 'gray_stained_glass_pane')
    # Enclosed cargo box (lz=3..8, ly=1..3)
    v.box(0, 1, 3, w - 1, 1, l - 1, 'light_gray_concrete')
    v.put(1, 1, 3, 'light_gray_concrete')
    v.put(2, 1, 3, 'light_gray_concrete')
    v.box(0, 2, 3, w - 1, 2, l - 1, 'white_concrete')
    v.box(1, 2, 4, 2, 2, l - 2, 'air')
    v.put(1, 2, l - 1, 'white_shulker_box')
    v.put(2, 2, l - 1, 'white_shulker_box')
    v.box(1, 3, 3, 2, 3, l - 1, 'white_concrete')
    for lz in range(3, l):
        v.put(0, 3, lz, 'smooth_quartz_slab[type=bottom]')
        v.put(3, 3, lz, 'smooth_quartz_slab[type=bottom]')
    return v.result()


def _city_bus(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('city-bus')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    for lz in (2, 10):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    # Yellow/blue/white city transit livery
    v.box(0, 1, 0, w - 1, 1, l - 1, 'yellow_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'blue_concrete')
        v.put(w - 1, 1, lz, 'blue_concrete')
    v.put(0, 1, 1, 'blue_concrete')
    v.put(0, 1, 0, 'oak_wall_sign[facing=north]', lines=['14 North Pier', '北碼頭', '-------------', 'City Express'])
    v.box(0, 2, 0, w - 1, 2, l - 1, 'white_concrete')
    v.box(1, 2, 1, 2, 2, l - 2, 'air')
    for lz in range(1, l - 1):
        if lz not in (4, 8):
            v.put(0, 2, lz, 'gray_stained_glass')
            v.put(w - 1, 2, lz, 'gray_stained_glass')
    v.put(1, 2, 0, 'gray_stained_glass')
    v.put(2, 2, 0, 'gray_stained_glass')
    v.put(0, 2, 0, 'gray_stained_glass_pane')
    v.put(3, 2, 0, 'gray_stained_glass_pane')
    v.box(0, 3, 0, w - 1, 3, l - 1, 'white_concrete')
    for lx in (1, 2):
        v.put(lx, 3, 0, 'smooth_quartz_slab[type=bottom]')
        v.put(lx, 3, l - 1, 'smooth_quartz_slab[type=bottom]')
    v.put(1, 3, 6, 'light_gray_shulker_box')
    v.put(2, 3, 6, 'light_gray_shulker_box')
    v.door(w - 1, 2, 4, 'east', 'oak')
    return v.result()


def _ambulance(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('ambulance')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    for lz in (1, 5):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    v.box(0, 1, 0, w - 1, 1, l - 1, 'white_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'red_concrete')
        v.put(w - 1, 1, lz, 'red_concrete')
    v.put(1, 1, 0, 'smooth_quartz')
    v.box(0, 2, 1, w - 1, 2, l - 1, 'white_concrete')
    for lz in (3, 4, 5):
        v.put(1, 2, lz, 'air')
    v.put(0, 2, 0, 'gray_stained_glass_pane')
    v.put(1, 2, 0, 'gray_stained_glass')
    v.put(2, 2, 0, 'gray_stained_glass_pane')
    v.put(0, 2, 4, 'red_shulker_box')
    v.put(2, 2, 4, 'red_shulker_box')
    v.box(0, 3, 2, w - 1, 3, l - 1, 'white_concrete')
    v.put(0, 3, 2, 'redstone_lamp')
    v.put(2, 3, 2, 'redstone_lamp')
    v.put(1, 3, 2, 'smooth_quartz_slab[type=bottom]')
    for lx in (0, 1, 2):
        v.put(lx, 3, 1, 'smooth_quartz_slab[type=bottom]')
    v.door(1, 2, l - 1, 'south', 'iron')
    return v.result()


def _rail_coach(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('rail-coach')
    v = VehicleBuilder(x0, z0, min_y=4, facing=facing)
    for lz in (2, 4, 10, 12):
        for lx in (1, 3):
            v.put(lx, 0, lz, 'black_concrete')
    v.put(w // 2, 1, 0, 'hopper')
    v.put(w // 2, 1, l - 1, 'hopper')
    v.box(0, 1, 1, w - 1, 1, l - 2, 'light_gray_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'red_concrete' if lz in (3, 11) else 'blue_concrete')
        v.put(w - 1, 1, lz, 'red_concrete' if lz in (3, 11) else 'blue_concrete')
    v.box(0, 2, 1, w - 1, 2, l - 2, 'white_concrete')
    v.box(1, 2, 2, w - 2, 2, l - 3, 'air')
    for lz in range(2, l - 2):
        if lz not in (4, 7, 10):
            v.put(0, 2, lz, 'gray_stained_glass')
            v.put(w - 1, 2, lz, 'gray_stained_glass')
    for lx in (1, 2, 3):
        v.put(lx, 2, 1, 'gray_stained_glass')
        v.put(lx, 2, l - 2, 'gray_stained_glass')
    v.box(1, 3, 1, w - 2, 3, l - 2, 'light_gray_concrete')
    for lz in range(1, l - 1):
        v.put(0, 3, lz, 'smooth_stone_slab[type=bottom]')
        v.put(w - 1, 3, lz, 'smooth_stone_slab[type=bottom]')
    for lz in (5, 9):
        v.put(2, 3, lz, 'gray_shulker_box')
    return v.result()


def _harbour_ferry(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('harbour-ferry')
    v = VehicleBuilder(x0, z0, min_y=2, facing=facing)
    # Green-and-ivory double-deck harbour ferry
    v.box(2, 0, 0, 4, 0, 0, 'green_concrete')
    v.box(1, 0, 1, 5, 0, 1, 'green_concrete')
    v.box(0, 0, 2, 6, 0, 13, 'green_concrete')
    v.box(1, 0, 14, 5, 0, 14, 'green_concrete')
    v.box(2, 1, 0, 4, 1, 0, 'smooth_quartz')
    v.box(1, 1, 1, 5, 1, 1, 'smooth_quartz')
    v.box(0, 1, 2, 6, 1, 13, 'smooth_quartz')
    v.box(1, 1, 14, 5, 1, 14, 'smooth_quartz')
    v.box(1, 1, 2, 5, 1, 13, 'oak_planks')
    v.box(1, 2, 3, 5, 2, 12, 'white_concrete')
    v.box(2, 2, 4, 4, 2, 11, 'air')
    for lz in range(4, 12):
        v.put(1, 2, lz, 'light_blue_stained_glass')
        v.put(5, 2, lz, 'light_blue_stained_glass')
    for lx in (2, 3, 4):
        v.put(lx, 2, 2, 'light_blue_stained_glass')
        v.put(lx, 2, 3, 'air')
    v.put(1, 2, 2, 'light_blue_stained_glass_pane')
    v.put(5, 2, 2, 'light_blue_stained_glass_pane')
    v.put(0, 2, 4, 'redstone_torch')
    v.put(6, 2, 4, 'soul_lantern')
    for lz in (2, 3):
        v.put(0, 2, lz, 'smooth_quartz_slab[type=bottom]')
        v.put(6, 2, lz, 'smooth_quartz_slab[type=bottom]')
    v.box(1, 3, 3, 5, 3, 12, 'green_concrete')
    v.box(2, 3, 4, 4, 3, 7, 'air')
    for lx in (2, 3, 4):
        v.put(lx, 3, 3, 'light_blue_stained_glass')
    for lz in (4, 5, 6):
        v.put(1, 3, lz, 'light_blue_stained_glass')
        v.put(5, 3, lz, 'light_blue_stained_glass')
    v.box(2, 4, 3, 4, 4, 7, 'smooth_quartz_slab[type=bottom]')
    v.put(3, 4, 9, 'yellow_concrete')
    v.put(3, 4, 10, 'black_concrete')
    return v.result()


def _washroom_fitout() -> dict[str, Any]:
    b = VoxelBuilder('washroom')
    # Strictly inside x=4..12, z=7..11, y=3..6; keep central aisle x=8, y=3..4 clear.
    # West wall vanity counter : smooth_quartz_slab[type=top] + recessed water_cauldron + tripwire_hook tap
    b.put(4, 3, 7, 'smooth_quartz_slab[type=top]')
    b.head(4, 4, 7, 'soap_dispenser', facing='east')
    b.put(4, 3, 8, 'water_cauldron[level=3]')
    b.put(4, 4, 8, 'tripwire_hook[facing=east]')
    b.put(4, 3, 9, 'smooth_quartz_slab[type=top]')
    b.put(4, 3, 10, 'water_cauldron[level=3]')
    b.put(4, 4, 10, 'tripwire_hook[facing=east]')
    b.put(4, 3, 11, 'smooth_quartz_slab[type=top]')
    b.put(4, 4, 11, 'white_candle[candles=2]')
    # Framed glass mirror against solid x=3 wall (y=4..5, z=8..10) + vanity end_rod lighting at y=6
    for mz in (8, 9, 10):
        b.put(4, 5, mz, 'light_blue_stained_glass_pane')
    b.put(4, 4, 9, 'light_blue_stained_glass_pane')
    b.box(4, 6, 8, 4, 6, 10, 'end_rod[facing=east]')
    # Hand dryer & waste bin along north/west washroom approach
    b.head(5, 4, 11, 'hand_dryer_white', facing='north', wall=True)
    b.head(6, 3, 11, 'trash_bin', facing='north')

    # East bay enclosed toilet stall (x=10..12, z=8..11): solid smooth_quartz partitions + birch_door
    b.box(10, 3, 8, 12, 5, 8, 'smooth_quartz')
    b.box(10, 3, 9, 10, 5, 9, 'smooth_quartz')
    b.box(10, 3, 11, 10, 5, 11, 'smooth_quartz')
    b.door(10, 3, 10, 'west', 'birch')
    b.put(10, 5, 10, 'smooth_quartz')
    # Toilet backing onto east wall x=13: cauldron bowl + raised iron_trapdoor lid + wall stone_button flush
    b.put(12, 3, 10, 'water_cauldron[level=1]')
    b.put(12, 4, 10, 'iron_trapdoor[facing=west,half=bottom,open=true]')
    b.put(12, 5, 10, 'stone_button[face=wall,facing=west]')
    b.head(12, 4, 11, 'toilet_paper_roll', facing='north', wall=True)
    # Ceiling lighting over aisle & stall
    b.put(7, 6, 9, 'sea_lantern')
    b.put(11, 6, 10, 'sea_lantern')
    return b.result()


def _roof_hvac() -> dict[str, Any]:
    b = VoxelBuilder('hvac')
    # Strictly inside x=4..12, z=7..11, y=7..10; keep service lane x=8, y=7..8 clear!
    # West primary 2x2 condenser & air-handling package (white_concrete + smooth_quartz + 4 top fan rails)
    b.box(4, 7, 8, 7, 8, 10, 'smooth_quartz')
    for dx in (5, 6):
        for dz in (8, 9):
            b.put(dx, 9, dz, 'rail[shape=north_south]')
    for x in (4, 7):
        for z in (8, 9, 10):
            b.put(x, 9, z, 'smooth_stone_slab[type=bottom]')
    b.put(5, 9, 10, 'smooth_stone_slab[type=bottom]')
    b.put(6, 9, 10, 'smooth_stone_slab[type=bottom]')
    # North intake louver grilles at z=7 backed by housing at z=8
    for x in (5, 6):
        b.put(x, 7, 7, 'iron_trapdoor[facing=north,half=bottom,open=true]')
        b.put(x, 8, 7, 'iron_bars')
    # East chiller module (x=9..12, z=8..10, y=7..8) + overhead insulated duct bridge at y=9 across x=8
    b.box(9, 7, 8, 11, 8, 10, 'polished_andesite')
    b.put(10, 8, 8, 'iron_block')
    b.put(9, 7, 7, 'iron_bars')
    b.put(10, 7, 7, 'iron_bars')
    for dx in (9, 10):
        for dz in (8, 9):
            b.put(dx, 9, dz, 'detector_rail[shape=north_south]')
    b.box(9, 9, 10, 11, 9, 10, 'smooth_stone_slab[type=bottom]')
    b.put(11, 9, 8, 'smooth_stone_slab[type=bottom]')
    b.put(11, 9, 9, 'smooth_stone_slab[type=bottom]')
    # Overhead galvanized supply duct bridging x=7..9 at y=9, z=10 (keeps x=8, y=7..8 100% open!)
    b.box(7, 9, 10, 9, 9, 10, 'iron_block')
    # HVAC custom heads: split ac_unit, wall_vent & electrical_panel disconnect
    b.head(12, 7, 9, 'ac_unit', facing='east')
    b.head(4, 8, 11, 'wall_vent', facing='south', wall=True)
    b.head(11, 8, 11, 'electrical_panel', facing='south', wall=True)
    return b.result()


def _diagonal_road() -> dict[str, Any]:
    b = VoxelBuilder('road')
    # Use full 5-wide asphalt diagonal transition (|dx|<=2) so the 45-degree dogleg reads as a smooth roadway,
    # flanked outside |dx|<=2 by raised stone-brick kerbs, sidewalks, streetlamps, and verge planting!
    for z in range(4, 20):
        cx = road_center(z)
        for dx in range(-4, 5):
            x = cx + dx
            if not (0 <= x <= 24):
                continue
            b.put(x, 1, z, 'stone')
            if abs(dx) <= 2:
                # Centerline subtle black_concrete crown on straight-to-curve spine, gray_concrete travel lanes
                surf = 'black_concrete' if (dx == 0 and z % 3 != 0) else 'gray_concrete'
                b.put(x, 2, z, surf)
                b.put(x, 3, z, 'air')
                b.put(x, 4, z, 'air')
            elif abs(dx) == 3:
                b.put(x, 2, z, 'smooth_stone')
                b.put(x, 3, z, 'stone_brick_slab[type=bottom]')
                b.put(x, 4, z, 'air')
            else:
                b.put(x, 2, z, 'grass_block')
                if z in (6, 11, 16) and dx == -4:
                    b.put(x, 3, z, 'polished_deepslate_wall')
                    b.put(x, 4, z, 'polished_deepslate_wall')
                    b.put(x, 5, z, 'lantern')
                elif z in (8, 14) and dx == 4:
                    b.put(x, 3, z, 'azalea_leaves[persistent=true]')
                elif (x + z) % 3 == 0:
                    b.put(x, 3, z, 'fern' if z % 2 == 0 else 'dandelion')
    return b.result()


def _curved_tunnel() -> dict[str, Any]:
    b = VoxelBuilder('tunnel')
    # Carve 3-wide stone-brick roadbed + 3-tall bore (y=3..5), lined side walls (|dx|==2) with recessed lighting,
    # and architectural stone-brick/andesite portal collars at z=4 and z=19.
    for z in range(4, 20):
        cx = road_center(z)
        for dx in (-1, 0, 1):
            x = cx + dx
            b.put(x, 2, z, 'stone_bricks')
            for y in (3, 4, 5):
                b.put(x, y, z, 'air')
        for side in (-2, 2):
            wx = cx + side
            if 0 <= wx <= 24:
                b.put(wx, 2, z, 'polished_andesite')
                b.put(wx, 3, z, 'polished_andesite')
                b.put(wx, 4, z, 'sea_lantern' if z % 3 == 1 else 'stone_bricks')
                b.put(wx, 5, z, 'stone_bricks')
                b.put(wx, 6, z, 'chiseled_stone_bricks' if z in (4, 19) else 'stone_bricks')
    return b.result()


def _junction_wayfinding() -> dict[str, Any]:
    b = VoxelBuilder('traffic-sign')
    # Grounded municipal masonry & quartz sign monument at (11, 2..6, 15) + north-facing wayfinding plaque at (11, 5, 14)
    b.box(11, 3, 15, 11, 5, 15, 'stone_bricks', component='traffic-sign')
    b.put(11, 6, 15, 'smooth_quartz_slab[type=bottom]', component='traffic-sign')
    b.sign(11, 5, 14, 'north', ['Ferry', 'Right', '---------', 'Pier 4 ->'], wood='oak', component='traffic-sign')
    # Clean roadside kerb along x=10 (outside protected lane x=5..9), streetlamp behind sign & verge planting
    for z in range(5, 20):
        b.put(10, 2, z, 'smooth_stone')
    b.box(13, 3, 16, 13, 5, 16, 'polished_deepslate_wall', component='lights')
    b.put(13, 6, 16, 'lantern', component='lights')
    for x, z, fl in ((12, 16, 'azalea'), (14, 15, 'fern'), (12, 18, 'cornflower'), (13, 19, 'dandelion')):
        b.put(x, 3, z, fl, component='garden')
    return b.result()


def _specimen_conifer() -> dict[str, Any]:
    b = VoxelBuilder('tree')
    # PNW Douglas-fir / Sitka spruce rooted at (10,3,10); spruce_log + spruce_leaves[persistent=true] only above y=2.
    rng = random.Random('specimen-conifer-praya-v1')
    height = 15
    for y in range(3, 3 + height - 2):
        b.put(10, y, 10, 'spruce_log[axis=y]')
    top_y = 3 + height - 1  # y=17
    # Conical taper with tier notches (widest r=3 at lower boughs, single leader tip at y=16..17)
    radii = [0, 0, 1, 1, 2, 1, 2, 2, 3, 2, 3, 3, 2]
    for j, r in enumerate(radii):
        yy = top_y - j
        lim = r * r + r * 0.65
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                d2 = dx * dx + dz * dz
                if d2 > lim:
                    continue
                if r >= 2 and d2 > (r - 1) ** 2 + (r - 1) * 0.65 and rng.random() < 0.18:
                    continue
                if dx == 0 and dz == 0 and yy < 3 + height - 2:
                    continue
                b.put(10 + dx, yy, 10 + dz, 'spruce_leaves[persistent=true]')
    return b.result()


def _specimen_broadleaf() -> dict[str, Any]:
    b = VoxelBuilder('tree')
    # Organic spreading oak rooted at (10,3,10); oak_log + oak_leaves[persistent=true] only above y=2.
    rng = random.Random('specimen-broadleaf-praya-v1')
    for y in range(3, 9):
        b.put(10, y, 10, 'oak_log[axis=y]')
    # Orthogonal-stepped asymmetric boughs rising to distinct crown domes (100% 6-neighbor connected!)
    limbs = [
        [(11, 6, 10, 'x'), (12, 6, 10, 'x'), (12, 7, 10, 'y'), (13, 7, 10, 'x'), (13, 8, 10, 'y')],
        [(9, 6, 10, 'x'), (8, 6, 10, 'x'), (8, 7, 10, 'y'), (7, 7, 10, 'x'), (7, 8, 10, 'y')],
        [(10, 6, 11, 'z'), (10, 6, 12, 'z'), (10, 7, 12, 'y'), (10, 7, 13, 'z'), (10, 8, 13, 'y')],
        [(10, 7, 9, 'z'), (10, 7, 8, 'z'), (10, 8, 8, 'y')],
    ]
    domes = [
        (10, 10, 10, 2),
        (13, 9, 10, 2),
        (7, 9, 10, 2),
        (10, 9, 13, 2),
        (10, 9, 8, 2),
    ]
    for chain in limbs:
        for lx, ly, lz, ax in chain:
            b.put(lx, ly, lz, f'oak_log[axis={ax}]')
    for px, py, pz, r in domes:
        for dy, lr in ((-1, 2), (0, r + 1), (1, r), (2, max(1, r - 1))):
            lim = lr * lr + lr * 0.55
            for dx in range(-lr, lr + 1):
                for dz in range(-lr, lr + 1):
                    d2 = dx * dx + dz * dz
                    if d2 > lim:
                        continue
                    if lr >= 2 and d2 > (lr - 1) ** 2 + 0.45 and rng.random() < 0.2:
                        continue
                    tx, ty, tz = px + dx, py + dy, pz + dz
                    if b.get_state(tx, ty, tz).startswith('oak_log'):
                        continue
                    b.put(tx, ty, tz, 'oak_leaves[persistent=true]')
    b._prune_disconnected_leaves((10, 3, 10))
    return b.result()


def _facade_depth_retrofit() -> dict[str, Any]:
    b = VoxelBuilder('retrofit')
    # Work strictly in x=4..16, z=5..6, y=3..9; <= 80 changes; >= 12 original front windows (y=5..6,z=7) visible; x=10,y=3..4 clear.
    for px in (4, 16):
        b.box(px, 3, 6, px, 8, 6, 'stone_bricks')
    for px in (9, 11):
        b.box(px, 3, 6, px, 7, 6, 'stone_bricks')
    # Entrance portal canopy at y=5, z=5..6 + flanking hanging lanterns (keeps x=10, y=3..4 100% clear!)
    b.put(10, 5, 6, 'smooth_quartz_slab[type=top]')
    b.box(9, 5, 5, 11, 5, 5, 'deepslate_tile_slab[type=top]')
    b.put(9, 4, 5, 'lantern[hanging=true]')
    b.put(11, 4, 5, 'lantern[hanging=true]')
    # Bracketed inverted-stair window sills at y=4, z=6 (anchored against solid z=7 wall -> zero floating_slab!)
    for x in (5, 6, 7, 8, 12, 13, 14, 15):
        b.put(x, 4, 6, 'smooth_quartz_stairs[facing=south,half=top]')
    # Continuous upper cornice at y=8, z=6 + projecting crown at y=8, z=5 + parapet coping at y=9, z=6
    b.box(4, 8, 6, 16, 8, 6, 'smooth_quartz_stairs[facing=south,half=top]')
    b.box(4, 8, 5, 16, 8, 5, 'deepslate_tile_slab[type=top]')
    b.box(4, 9, 6, 16, 9, 6, 'stone_brick_slab[type=bottom]')
    return b.result()


def _rowhouse_shop_conversion() -> dict[str, Any]:
    b = VoxelBuilder('conversion')
    # Strictly inside x=5..13, z=8..13, y=3..5 (<= 55 edits); keep east stair x=14 clear & preserve Built 2012 at (5,5,8).
    b.box(6, 3, 12, 9, 3, 12, 'smooth_quartz')
    b.put(6, 3, 11, 'smooth_quartz')
    b.head(6, 4, 12, 'espresso_machine', facing='north')
    b.head(7, 4, 12, 'coffee_maker', facing='north')
    b.head(8, 4, 12, 'croissant', facing='north')
    b.head(9, 4, 12, 'pos_terminal', facing='north')
    b.head(6, 4, 11, 'card_reader', facing='east')
    b.put(12, 3, 9, 'spruce_stairs[facing=south,half=bottom]')
    b.put(12, 3, 10, 'oak_slab[type=top]')
    b.put(12, 3, 11, 'spruce_stairs[facing=north,half=bottom]')
    b.head(12, 4, 10, 'latte_cup', facing='west')
    b.dedication_placard(5, 4, 11, 'east', 'Nov. 15,', '2026', label='Renovated', tool='stone_axe')
    b.framed_sign(11, 4, 13, 'north', 'Rowhouse Cafe', 'Esp & Pastry', wood='spruce')
    # Wall-anchored linear end_rods backed by protected west wall x=4 & south wall z=14
    b.put(5, 5, 9, 'end_rod[facing=east]')
    b.put(5, 5, 12, 'end_rod[facing=east]')
    b.put(8, 5, 13, 'end_rod[facing=north]')
    b.put(11, 5, 13, 'end_rod[facing=north]')
    return b.result()


def _inspector_repair() -> dict[str, Any]:
    b = VoxelBuilder('repair')
    b.put(5, 5, 6, 'air')
    b.put(12, 6, 9, 'air')
    b.put(8, 3, 6, 'air')
    b.put(5, 5, 7, 'oak_wall_sign[facing=north]', lines=['Cafe hours'])
    return b.result()


VEHICLE_BUILDERS: dict[str, Any] = {
    'box-truck': _box_truck,
    'city-bus': _city_bus,
    'ambulance': _ambulance,
    'rail-coach': _rail_coach,
    'harbour-ferry': _harbour_ferry,
}

EXTRA_WORLD_BUILDERS: dict[str, Any] = {
    'washroom-fitout': _washroom_fitout,
    'roof-hvac': _roof_hvac,
    'diagonal-road': _diagonal_road,
    'curved-tunnel': _curved_tunnel,
    'junction-wayfinding': _junction_wayfinding,
    'specimen-conifer': _specimen_conifer,
    'specimen-broadleaf': _specimen_broadleaf,
    'facade-depth-retrofit': _facade_depth_retrofit,
    'rowhouse-shop-conversion': _rowhouse_shop_conversion,
    'inspector-repair': _inspector_repair,
}
