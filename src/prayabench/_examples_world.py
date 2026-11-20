"""Deterministic acceptable reference examples for the 15 v0.4 voxel tasks."""
from __future__ import annotations

from typing import Any

from ._examples_common import VehicleBuilder, VoxelBuilder
from .voxel_tasks import road_center, vehicle_rect


def _box_truck(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('box-truck')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    # Wheels ONLY at ly=0 on outer edges (axle span 6 >= 3)
    for lz in (1, 7):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    # Chassis & cab (lz=0..2, max ly=2 < cargo max ly=3)
    v.box(0, 1, 0, w - 1, 1, 2, 'blue_concrete')
    v.put(1, 1, 0, 'light_gray_concrete')
    v.put(2, 1, 0, 'light_gray_concrete')
    v.put(0, 1, 0, 'blue_shulker_box')
    v.put(3, 1, 0, 'blue_shulker_box')
    v.box(0, 2, 1, w - 1, 2, 2, 'blue_concrete')
    for lx in (1, 2):
        v.put(lx, 2, 0, 'gray_stained_glass')
    v.put(0, 2, 0, 'gray_stained_glass_pane')
    v.put(3, 2, 0, 'gray_stained_glass_pane')
    # Enclosed cargo box (lz=3..8, ly=1..3)
    v.box(0, 1, 3, w - 1, 1, l - 1, 'light_gray_concrete')
    v.box(0, 2, 3, w - 1, 2, l - 1, 'white_concrete')
    v.box(1, 2, 4, 2, 2, l - 2, 'air')
    # Rear cargo doors & sculpted roof
    v.put(1, 2, l - 1, 'white_shulker_box')
    v.put(2, 2, l - 1, 'white_shulker_box')
    v.box(1, 3, 3, 2, 3, l - 1, 'white_concrete')
    for lz in range(3, l):
        v.put(0, 3, lz, 'smooth_stone_slab[type=bottom]')
        v.put(3, 3, lz, 'smooth_stone_slab[type=bottom]')
    return v.result()


def _city_bus(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('city-bus')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    # Wheels ONLY at ly=0 on outer edges (axle span 8 >= 3)
    for lz in (2, 10):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    # Lower transit livery body (ly=1)
    v.box(0, 1, 0, w - 1, 1, l - 1, 'white_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'blue_concrete')
        v.put(w - 1, 1, lz, 'blue_concrete')
    # Front route display wall sign backed by solid blue_concrete at (0, 1, 1)
    v.put(0, 1, 1, 'blue_concrete')
    v.put(0, 1, 0, 'oak_wall_sign[facing=north]', lines=['Route 14', 'North Pier'])
    # Mid cabin windows (ly=2) & panoramic front windshield
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
    # Roof deck & AC pods (ly=3)
    v.box(0, 3, 0, w - 1, 3, l - 1, 'white_concrete')
    for lx in (1, 2):
        v.put(lx, 3, 0, 'smooth_stone_slab[type=bottom]')
        v.put(lx, 3, l - 1, 'smooth_stone_slab[type=bottom]')
    v.put(1, 3, 6, 'light_gray_shulker_box')
    v.put(2, 3, 6, 'light_gray_shulker_box')
    # Right kerbside passenger door (lx=w-1, lz=4, ly=2..3, facing=east rotated)
    v.door(w - 1, 2, 4, 'east', 'oak')
    return v.result()


def _ambulance(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('ambulance')
    v = VehicleBuilder(x0, z0, min_y=3, facing=facing)
    # Wheels ONLY at ly=0 on edges (0, 2), axle span 4 >= 3
    for lz in (1, 5):
        for lx in (0, w - 1):
            v.put(lx, 0, lz, 'black_concrete')
    # Lower body (ly=1) with red medical stripe
    v.box(0, 1, 0, w - 1, 1, l - 1, 'white_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'red_concrete')
        v.put(w - 1, 1, lz, 'red_concrete')
    v.put(1, 1, 0, 'light_gray_concrete')
    # Cab & patient module (ly=2)
    v.box(0, 2, 1, w - 1, 2, l - 1, 'white_concrete')
    v.put(1, 2, 3, 'air')
    v.put(1, 2, 4, 'air')
    v.put(1, 2, 5, 'air')
    v.put(0, 2, 0, 'gray_stained_glass_pane')
    v.put(1, 2, 0, 'gray_stained_glass')
    v.put(2, 2, 0, 'gray_stained_glass_pane')
    v.put(0, 2, 4, 'red_shulker_box')
    v.put(2, 2, 4, 'red_shulker_box')
    # Roof & red emergency lightbar (ly=3 >= 2)
    v.box(0, 3, 2, w - 1, 3, l - 1, 'white_concrete')
    v.put(0, 3, 2, 'redstone_lamp')
    v.put(2, 3, 2, 'redstone_lamp')
    v.put(1, 3, 2, 'smooth_stone_slab[type=bottom]')
    v.put(0, 3, 1, 'smooth_stone_slab[type=bottom]')
    v.put(1, 3, 1, 'smooth_stone_slab[type=bottom]')
    v.put(2, 3, 1, 'smooth_stone_slab[type=bottom]')
    # Rear patient doors (lx=1, lz=l-1, ly=2..3, facing=south rotated)
    v.door(1, 2, l - 1, 'south', 'oak')
    return v.result()


def _rail_coach(facing: str) -> dict[str, Any]:
    x0, z0, w, l = vehicle_rect('rail-coach')
    v = VehicleBuilder(x0, z0, min_y=4, facing=facing)
    # Twin bogie wheels ONLY at ly=0 on rail lines lx in (1, 3)
    for lz in (2, 4, 10, 12):
        for lx in (1, 3):
            v.put(lx, 0, lz, 'black_concrete')
    # Front and rear couplings at (w//2, 1, 0) and (w//2, 1, l-1)
    v.put(w // 2, 1, 0, 'hopper')
    v.put(w // 2, 1, l - 1, 'hopper')
    # Coach underframe & lower livery (ly=1, lz=1..l-2)
    v.box(0, 1, 1, w - 1, 1, l - 2, 'light_gray_concrete')
    for lz in range(1, l - 1):
        v.put(0, 1, lz, 'blue_concrete')
        v.put(w - 1, 1, lz, 'blue_concrete')
    # Passenger saloon walls & glazing (ly=2)
    v.box(0, 2, 1, w - 1, 2, l - 2, 'white_concrete')
    v.box(1, 2, 2, w - 2, 2, l - 3, 'air')
    for lz in range(2, l - 2):
        if lz not in (4, 7, 10):
            v.put(0, 2, lz, 'gray_stained_glass')
            v.put(w - 1, 2, lz, 'gray_stained_glass')
    for lx in (1, 2, 3):
        v.put(lx, 2, 1, 'gray_stained_glass')
        v.put(lx, 2, l - 2, 'gray_stained_glass')
    # Aerodynamic commuter roof (ly=3) with rooftop HVAC boxes
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
    # Tapered displacement hull at ly=0 (world y=2 in water; 15 lengthwise rows >= 12)
    v.box(2, 0, 0, 4, 0, 0, 'blue_concrete')
    v.box(1, 0, 1, 5, 0, 1, 'blue_concrete')
    v.box(0, 0, 2, 6, 0, 13, 'blue_concrete')
    v.box(1, 0, 14, 5, 0, 14, 'blue_concrete')
    # Main deck & white gunwales (ly=1)
    v.box(2, 1, 0, 4, 1, 0, 'white_concrete')
    v.box(1, 1, 1, 5, 1, 1, 'white_concrete')
    v.box(0, 1, 2, 6, 1, 13, 'white_concrete')
    v.box(1, 1, 14, 5, 1, 14, 'white_concrete')
    v.box(1, 1, 2, 5, 1, 13, 'oak_planks')
    # Lower passenger cabin (ly=2, lz=2..12) with bow observation glazing at lz=2
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
    # Bow & stern deck railings (slabs) + Port/Starboard navigation lights at lx=0 and lx=6 (ly=2 >= 1)
    v.put(0, 2, 4, 'redstone_torch')
    v.put(6, 2, 4, 'soul_lantern')
    for lz in (2, 3):
        v.put(0, 2, lz, 'smooth_quartz_slab[type=bottom]')
        v.put(6, 2, lz, 'smooth_quartz_slab[type=bottom]')
    # Upper wheelhouse & cabin roof (ly=3, bow half lz=3..12, solid deck under funnel)
    v.box(1, 3, 3, 5, 3, 12, 'white_concrete')
    v.box(2, 3, 4, 4, 3, 7, 'air')
    for lx in (2, 3, 4):
        v.put(lx, 3, 3, 'light_blue_stained_glass')
    for lz in (4, 5, 6):
        v.put(1, 3, lz, 'light_blue_stained_glass')
        v.put(5, 3, lz, 'light_blue_stained_glass')
    # Wheelhouse roof & yellow harbour funnel (ly=4, connected to solid cabin roof at ly=3)
    v.box(2, 4, 3, 4, 4, 7, 'smooth_quartz_slab[type=bottom]')
    v.put(3, 4, 9, 'yellow_concrete')
    v.put(3, 4, 10, 'gray_concrete')
    return v.result()


def _washroom_fitout() -> dict[str, Any]:
    b = VoxelBuilder()
    # Strictly inside x=4..12, z=7..11, y=3..6; keep aisle x=8, y=3..4 passable
    # West vanity counter + water_cauldron sink + glass mirror against x=3 wall
    b.put(4, 3, 8, 'smooth_quartz')
    b.put(4, 3, 9, 'water_cauldron')
    b.put(4, 3, 10, 'smooth_quartz')
    b.put(4, 4, 9, 'light_blue_stained_glass_pane')
    b.put(4, 5, 9, 'light_blue_stained_glass_pane')
    # Standing vanity lantern (no roof at y=7 in fixture)
    b.put(4, 4, 8, 'lantern')
    b.put(4, 4, 10, 'potted_fern')
    # East WC stall with privacy screen, cistern tank, stair seat & trapdoor lid
    b.box(10, 3, 8, 10, 4, 10, 'white_concrete')
    b.put(10, 5, 10, 'sea_lantern')
    b.put(12, 3, 10, 'white_concrete')
    b.put(12, 4, 10, 'white_concrete')
    b.put(11, 3, 10, 'smooth_quartz_stairs[facing=east,half=bottom]')
    b.put(11, 4, 10, 'birch_trapdoor[facing=west,half=bottom,open=false]')
    return b.result()


def _roof_hvac() -> dict[str, Any]:
    b = VoxelBuilder()
    # Strictly inside x=4..12, z=7..11, y=7..10; keep aisle x=8, y=7..8 passable
    # West primary air-handling unit (>= 8 connected grounded housing blocks)
    b.box(4, 7, 8, 7, 8, 10, 'polished_andesite')
    b.put(5, 8, 8, 'iron_block')
    b.put(6, 8, 8, 'iron_block')
    # Front intake grilles at z=7 backed by housing at z=8
    b.put(5, 8, 7, 'iron_bars')
    b.put(6, 8, 7, 'iron_bars')
    b.put(5, 7, 7, 'iron_trapdoor[facing=north,open=true]')
    b.put(6, 7, 7, 'iron_trapdoor[facing=north,open=true]')
    b.box(4, 9, 8, 7, 9, 10, 'smooth_stone_slab[type=bottom]')
    b.put(5, 9, 9, 'hopper')
    # East condenser module + overhead duct bridge at y=9 (above passable aisle y=7..8!)
    b.box(9, 7, 8, 11, 8, 10, 'iron_block')
    b.put(9, 7, 7, 'iron_bars')
    b.put(10, 7, 7, 'iron_bars')
    b.box(9, 9, 8, 11, 9, 10, 'smooth_stone_slab[type=bottom]')
    b.put(7, 9, 9, 'iron_block')
    b.put(8, 9, 9, 'iron_block')
    b.put(9, 9, 9, 'iron_block')
    return b.result()


def _diagonal_road() -> dict[str, Any]:
    b = VoxelBuilder()
    # Smoothly connect stubs across z=4..19 along road_center(z)
    for z in range(4, 20):
        cx = road_center(z)
        for dx in (-2, -1, 0, 1, 2):
            x = cx + dx
            b.put(x, 1, z, 'stone')
            b.put(x, 2, z, 'gray_concrete' if abs(dx) <= 1 else 'smooth_stone')
            b.put(x, 3, z, 'air')
            b.put(x, 4, z, 'air')
    return b.result()


def _curved_tunnel() -> dict[str, Any]:
    b = VoxelBuilder()
    # Carve full 3-wide, 3-tall bore (y=3..5) with stone_bricks floor at y=2, preserving roof y>=6
    for z in range(4, 20):
        cx = road_center(z)
        for dx in (-1, 0, 1):
            x = cx + dx
            b.put(x, 2, z, 'stone_bricks')
            for y in (3, 4, 5):
                b.put(x, y, z, 'air')
        # Recessed wall lighting along west lining (|dx|==2 is writable below y=7)
        if z % 4 == 2:
            b.put(cx - 2, 4, z, 'sea_lantern')
            b.put(cx + 2, 4, z, 'sea_lantern')
    return b.result()


def _junction_wayfinding() -> dict[str, Any]:
    b = VoxelBuilder()
    # Grounded masonry sign gantry post at (11, 3..5, 15) + north-facing sign at (11, 5, 14)
    b.box(11, 3, 15, 11, 5, 15, 'stone_bricks')
    b.put(11, 6, 15, 'stone_brick_slab[type=bottom]')
    b.sign(11, 5, 14, 'north', ['Ferry', 'Right'], component='traffic-sign')
    return b.result()


def _specimen_conifer() -> dict[str, Any]:
    b = VoxelBuilder()
    # Only spruce_log + spruce_leaves[persistent=true] above y=2; rooted at (10,3,10), >=5 trunk, conical spire
    for y in range(3, 12):
        b.put(10, y, 10, 'spruce_log[axis=y]')
    # Tiered conical spruce layers: widest y=5 (>= 12 leaves), sharp single-leaf spire at y=13 (<= 5)
    layers = [
        (5, 2, 3),
        (6, 2, 2),
        (7, 2, 2),
        (8, 1, 2),
        (9, 1, 1),
        (10, 1, 2),
        (11, 1, 1),
    ]
    for y, r, max_manhattan in layers:
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx == 0 and dz == 0:
                    continue
                if abs(dx) + abs(dz) <= max_manhattan:
                    b.put(10 + dx, y, 10 + dz, 'spruce_leaves[persistent=true]')
    b.put(10, 12, 10, 'spruce_leaves[persistent=true]')
    b.put(10, 13, 10, 'spruce_leaves[persistent=true]')
    return b.result()


def _specimen_broadleaf() -> dict[str, Any]:
    b = VoxelBuilder()
    # Only oak_log + oak_leaves[persistent=true] above y=2; rooted at (10,3,10), spreading branches & >=7 x-span
    for y in range(3, 9):
        b.put(10, y, 10, 'oak_log[axis=y]')
    # Four spreading structural boughs at y=6..7 (>= 3 off-trunk branch log columns)
    for dx, dz, axis in ((-1, 0, 'x'), (1, 0, 'x'), (0, -1, 'z'), (0, 1, 'z')):
        b.put(10 + dx, 6, 10 + dz, f'oak_log[axis={axis}]')
        b.put(10 + 2 * dx, 7, 10 + 2 * dz, f'oak_log[axis={axis}]')
    # Layered spreading oak crown spanning x=6..14 (span 9 >= 7)
    crown_tiers = [
        (7, 3, 4),
        (8, 4, 5),
        (9, 3, 4),
        (10, 2, 3),
        (11, 1, 1),
    ]
    for y, r, max_m in crown_tiers:
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if (10 + dx, y, 10 + dz) in b.cells:
                    continue
                if abs(dx) + abs(dz) <= max_m:
                    b.put(10 + dx, y, 10 + dz, 'oak_leaves[persistent=true]')
    return b.result()


def _facade_depth_retrofit() -> dict[str, Any]:
    b = VoxelBuilder()
    # Strictly inside x=4..16, z=5..6, y=3..9; <= 80 edits; keep entry x=10, y=3..4 clear & >= 12 windows open
    # Grounded stone-brick flanking piers at x=4 and x=16 (z=6, y=3..8)
    for px in (4, 16):
        b.box(px, 3, 6, px, 8, 6, 'stone_bricks')
    # Grounded entry frame pilasters at x=9 and x=11 (z=6, y=3..4 -> leaves all 20 windows at y=5..6 uncovered!)
    for px in (9, 11):
        b.box(px, 3, 6, px, 4, 6, 'stone_bricks')
    # Projecting entrance canopy at y=5, z=5 + hanging entry lanterns
    b.box(9, 5, 5, 11, 5, 5, 'deepslate_tile_slab[type=top]')
    b.put(9, 4, 5, 'lantern[hanging=true]')
    b.put(11, 4, 5, 'lantern[hanging=true]')
    # Continuous projecting upper cornice at x=4..16, y=8, z=5 + roof coping at y=9, z=6
    b.box(4, 8, 5, 16, 8, 5, 'deepslate_tile_slab[type=bottom]')
    b.box(4, 9, 6, 16, 9, 6, 'smooth_stone_slab[type=bottom]')
    # Subtle window sill brackets at y=4, z=6 under outer bays
    for x in (6, 7, 13, 14):
        b.put(x, 4, 6, 'smooth_stone_slab[type=top]')
    return b.result()


def _rowhouse_shop_conversion() -> dict[str, Any]:
    b = VoxelBuilder()
    # Strictly inside x=5..13, z=8..13, y=3..5; <= 55 edits; preserves stair at x=14 & Built 2012 placard at (5,5,8)
    b.box(6, 3, 11, 8, 3, 11, 'smooth_quartz')
    b.head(6, 4, 11, 'coffee_maker')
    b.head(8, 4, 11, 'pos_terminal')
    b.put(7, 4, 11, 'lantern')
    b.put(11, 3, 9, 'spruce_stairs[facing=south,half=bottom]')
    b.put(11, 3, 10, 'oak_slab[type=top]')
    b.put(11, 3, 11, 'spruce_stairs[facing=north,half=bottom]')
    b.put(11, 4, 10, 'lantern')
    # Mounted shop sign backed by protected south wall at z=14 (no new-build claim)
    b.sign(12, 4, 13, 'north', ['Rowhouse Brew', 'Refitted Cafe'])
    return b.result()


def _inspector_repair() -> dict[str, Any]:
    b = VoxelBuilder()
    # Minimal 4-cell surgical repair
    b.put(5, 5, 6, 'air')
    b.put(12, 6, 9, 'air')
    b.put(8, 3, 6, 'air')
    b.sign(5, 5, 7, 'north', ['Cafe hours'])
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
