"""Deterministic synthetic reference examples; these are NOT model benchmark results."""
import json
from pathlib import Path

from ._examples_common import VoxelBuilder
from .evaluate import evaluate
from .report import report
from .tasks import ground_at, init_run


def example(gabled: bool = True) -> dict:
    """Rainier Coffee House (118 Cascade St) on lateral east-rising slope."""
    b = VoxelBuilder('demo')
    # Grade floor slab at y=3 across x=3..14, z=7..17, carrying foundations down to ground(x,z)
    for x in range(3, 15):
        for z in range(7, 18):
            g = ground_at('sloped-cafe', x, z)
            for y in range(min(g, 3), 4):
                on_edge = x in (3, 14) or z in (7, 17)
                b.put(x, y, z, 'stone_bricks' if (y < 3 or on_edge) else 'spruce_planks', component='floor')
            for y in range(4, 9):
                b.put(x, y, z, 'air', component='interior')

    # Perimeter walls (y=4..7): stone_bricks base/quoins, warm bricks/quartz infill, spandrel at y=7
    wall_mat = 'white_concrete' if gabled else 'bricks'
    for y in range(4, 8):
        for x in range(3, 15):
            for z in (7, 17):
                corner = x in (3, 14)
                mat = 'smooth_quartz' if y == 7 else ('stone_bricks' if corner else wall_mat)
                b.put(x, y, z, mat, component='wall')
        for z in range(8, 17):
            for x in (3, 14):
                b.put(x, y, z, 'smooth_quartz' if y == 7 else wall_mat, component='wall')

    # Paved street forecourt & single-step grade transition at z=5..6 (sidewalk z=4 is y=2 at x<8 and y=3 at x>=8)
    for x in range(3, 15):
        g5 = ground_at('sloped-cafe', x, 5)
        g6 = ground_at('sloped-cafe', x, 6)
        if x >= 7:
            for y in range(min(g5, 3), 4):
                b.put(x, y, 5, 'stone_brick_stairs[facing=south,half=bottom]' if (x == 7 and y == 3) else 'polished_andesite', component='apron')
            for y in range(min(g6, 3), 4):
                b.put(x, y, 6, 'polished_andesite', component='apron')
            b.put(x, 4, 5, 'air')
            b.put(x, 4, 6, 'air')
        else:
            # West sidewalk patio terrace at y=2
            b.put(x, 2, 5, 'polished_andesite', component='apron')
            b.put(x, 2, 6, 'polished_andesite', component='apron')

    # 1-block recessed north entrance portal at x=7..9, y=4..6, z=7 (door at x=8, z=8, flush with y=3 apron!)
    b.recessed_north_portal(7, 9, 4, 7, door_xs=8, door_wood='dark_oak', pier_mat='smooth_quartz', height=3, uplight=True)

    # Smoked shopfront windows + projecting cafe awning on north, plus dressed windows on west, east & south
    for x in (4, 5, 6, 11, 12, 13):
        b.box(x, 5, 7, x, 6, 7, 'gray_stained_glass', component='window')
        b.put(x, 7, 6, 'deepslate_tile_slab[type=top]', component='canopy')
    b.put(4, 3, 6, 'spruce_stairs[facing=north,half=bottom]', component='bench')
    b.put(5, 3, 6, 'oak_slab[type=top]', component='furniture')
    b.head(5, 4, 6, 'cup_coffee', facing='north')
    b.put(12, 4, 6, 'azalea_leaves[persistent=true]', component='relief')
    b.put(13, 4, 6, 'flowering_azalea_leaves[persistent=true]', component='relief')

    # West, East, and South dressed windows (ensuring every elevation has openings + non-planar sills/shutters)
    b.dressed_window('west', 3, 10, 13, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    for z in range(10, 14):
        b.put(14, 5, z, 'gray_stained_glass', component='window')
        b.put(14, 6, z, 'gray_stained_glass', component='window')
        g_e = ground_at('sloped-cafe', 15, z)
        if g_e < 4:
            b.put(15, 4, z, 'smooth_quartz_stairs[facing=west,half=top]', component='relief')
    for z in (9, 14):
        if ground_at('sloped-cafe', 15, z) < 5:
            b.put(15, 5, z, 'spruce_trapdoor[facing=east,half=bottom,open=true]', component='relief')
            b.put(15, 6, z, 'spruce_trapdoor[facing=east,half=bottom,open=true]', component='relief')
    b.dressed_window('south', 17, 5, 7, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 17, 10, 12, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')

    # Roof: pitched gable with eaves & low brick chimney OR flat modern roof with 2x2 fan + solar
    b.box(3, 8, 7, 14, 8, 17, 'spruce_planks' if gabled else 'smooth_stone', component='roof')
    if gabled:
        for i in range(7):
            y = 8 + i
            lx, rx = 2 + i, 15 - i
            for z in range(6, 19):
                if lx < rx:
                    b.put(lx, y, z, 'deepslate_tile_stairs[facing=east,half=bottom]', component='roof')
                    b.put(rx, y, z, 'deepslate_tile_stairs[facing=west,half=bottom]', component='roof')
            if i >= 1:
                for x in range(lx + 1, rx):
                    for z in (7, 17):
                        mat = 'gray_stained_glass_pane' if (i == 2 and x in (8, 9)) else 'spruce_planks'
                        b.put(x, y, z, mat, component='wall')
        # Low chimney (2 blocks clear of roof slope)
        for cy in range(9, 13):
            b.put(12, cy, 15, 'bricks', component='chimney')
        b.put(12, 13, 15, 'stone_brick_wall', component='chimney')
    else:
        for x in range(3, 15):
            b.put(x, 9, 7, 'stone_brick_slab[type=bottom]', component='roof')
            b.put(x, 9, 17, 'stone_brick_slab[type=bottom]', component='roof')
        for z in range(7, 18):
            b.put(3, 9, z, 'stone_brick_slab[type=bottom]', component='roof')
            b.put(14, 9, z, 'stone_brick_slab[type=bottom]', component='roof')
        b.fan_unit_2x2(5, 9, 13)
        for sx in range(9, 13):
            for sz in (13, 14):
                b.put(sx, 9, sz, 'daylight_detector[inverted=true]', component='roof')
        b.head(8, 9, 10, 'ac_unit', facing='north', component='roof')

    # Interior espresso bar, pastry display, booths, lighting & Built placard + stone_axe item_frame
    b.box(4, 4, 14, 8, 4, 15, 'smooth_quartz', component='furniture')
    b.head(4, 5, 14, 'espresso_machine', facing='north')
    b.head(5, 5, 14, 'coffee_maker', facing='north')
    b.head(6, 5, 14, 'croissant', facing='north')
    b.head(7, 5, 14, 'cheesecake', facing='north')
    b.head(8, 5, 14, 'pos_terminal', facing='north')
    b.head(8, 5, 15, 'card_reader', facing='west')
    for bz in (10, 14):
        b.put(12, 4, bz - 1, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
        b.put(12, 4, bz, 'oak_slab[type=top]', component='furniture')
        b.put(12, 4, bz + 1, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.head(12, 5, 10, 'latte_cup', facing='west')
    for lx in (6, 11):
        for lz in (10, 14):
            b.put(lx, 7, lz, 'lantern[hanging=true]', component='lights')

    # Signage: exterior address plaque, fascia sign, hours board, and interior Built placard + stone_axe frame
    b.address_plaque(10, 5, 6, 'north', 118, 'Cascade St', '卡스케이드街'[:0] + '瀑布街')
    b.sign(5, 7, 6, 'north', ['Rainier Coffee', '雷尼爾咖啡', '--------------', 'Roastery & Bar'], wood='spruce', component='facade')
    b.framed_sign(10, 6, 6, 'north', 'Daily 07-19h', 'Esp & Pastry', wood='birch', component='facade')
    b.dedication_placard(4, 5, 11, 'east', 'Nov. 12,', '2026', tool='stone_axe')

    # East pocket garden (x=16..22, z=6..18) graded on natural y=4 terrace
    for z in range(5, 16):
        gy = ground_at('sloped-cafe', 18, z)
        b.put(18, gy, z, 'stone_bricks', component='path')
    for x in (19, 20):
        gy = ground_at('sloped-cafe', x, 11)
        b.put(x, gy + 1, 11, 'spruce_stairs[facing=north,half=bottom]', component='bench')
    gy_m = ground_at('sloped-cafe', 17, 6)
    b.put(17, gy_m + 1, 6, 'iron_bars', component='street')
    b.head(17, gy_m + 2, 6, 'mailbox_orange', facing='north')
    b.put(17, gy_m, 8, 'polished_andesite', component='path')
    b.head(17, gy_m + 1, 8, 'trash_bin', facing='east')
    b.conifer(20, ground_at('sloped-cafe', 20, 15) + 1, 15, height=9)
    for x, z, fl in ((16, 7, 'poppy'), (16, 9, 'cornflower'), (21, 8, 'oxeye_daisy'), (22, 10, 'dandelion'), (17, 14, 'fern')):
        b.put(x, ground_at('sloped-cafe', x, z) + 1, z, fl, component='garden')

    out = b.result()
    out['provenance'] = 'Deterministic package demo; not a model run.'
    return out


def demo(out):
    out = Path(out)
    init_run(out, 'sloped-cafe')
    files = []
    for name, gable in [('reference-gable', True), ('reference-flat', False)]:
        p = out / (name + '.json')
        p.write_text(json.dumps(example(gable), indent=2))
        files.append(p)
        evaluate(out, p, out / (name + '.checks.json'))
    report(out, files, out / 'index.html', blind=False)
    return out / 'index.html'
