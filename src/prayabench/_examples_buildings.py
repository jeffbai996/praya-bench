"""Deterministic acceptable reference examples for the 16 buildings and 4 terraforming tasks."""
from __future__ import annotations

from typing import Any

from . import demo
from ._examples_common import PROVENANCE, VoxelBuilder
from .tasks import ground_at


def _transit_shelter() -> dict[str, Any]:
    b = VoxelBuilder('shelter')
    # Level paved pad connected to sidewalk z=4, with yellow tactile boarding strip at z=5
    b.box(3, 2, 5, 14, 2, 10, 'polished_andesite')
    for x in range(4, 14):
        b.put(x, 2, 5, 'yellow_concrete')
    # Grounded stone-brick base curb & dark steel portal columns (no floating panes!)
    b.box(3, 3, 10, 14, 3, 10, 'stone_bricks')
    b.box(3, 3, 7, 3, 3, 9, 'stone_bricks')
    for x in (3, 7, 11, 14):
        b.box(x, 3, 10, x, 5, 10, 'polished_deepslate')
    b.box(3, 3, 7, 3, 5, 7, 'polished_deepslate')
    b.box(14, 3, 7, 14, 5, 7, 'polished_deepslate')
    for x in (4, 5, 6, 8, 9, 10, 12, 13):
        b.box(x, 4, 10, x, 5, 10, 'gray_stained_glass_pane')
    for z in (8, 9):
        b.box(3, 4, z, 3, 5, z, 'gray_stained_glass_pane')
    # Cantilevered canopy roof with timber soffit & slab fascia
    b.box(3, 6, 6, 14, 6, 10, 'polished_deepslate')
    b.box(4, 6, 7, 13, 6, 9, 'stripped_spruce_wood[axis=x]')
    b.box(2, 6, 5, 15, 6, 5, 'smooth_quartz_slab[type=top]')
    b.box(2, 6, 11, 15, 6, 11, 'smooth_quartz_slab[type=top]')
    b.box(3, 7, 6, 14, 7, 10, 'smooth_stone_slab[type=bottom]')
    # Passenger bench, route/timetable signs, fare validator, bins & transit clock
    b.bench(5, 9, 9, 9, 3, 'north', 'spruce')
    b.sign(3, 4, 6, 'north', ['14 North Pier', '北碼頭', '-------------', 'Every 6 min'], wood='oak')
    b.framed_sign(11, 4, 9, 'north', 'Fare Zone 1', 'Tap Compass', wood='birch')
    b.put(12, 3, 7, 'smooth_quartz')
    b.head(12, 4, 7, 'ticket_validator', facing='north')
    b.head(13, 3, 8, 'trash_bin', facing='north')
    b.head(13, 3, 9, 'recycling_bin', facing='north')
    b.head(7, 5, 9, 'tram_clock', facing='north', wall=True)
    for x in (5, 9, 13):
        b.put(x, 5, 7, 'lantern[hanging=true]', component='lights')
    # Low rain-garden planting bed behind shelter
    for x in range(4, 14):
        b.put(x, 2, 11, 'grass_block')
        b.put(x, 2, 12, 'moss_block' if x % 2 == 0 else 'grass_block')
    for x, fl in ((4, 'azalea'), (6, 'cornflower'), (8, 'fern'), (10, 'flowering_azalea'), (12, 'oxeye_daisy')):
        b.put(x, 3, 12, fl)
    return b.result()


def _pocket_park() -> dict[str, Any]:
    b = VoxelBuilder('park')
    # Continuous winding stone walkway from sidewalk z=4 into central plaza
    for z in range(5, 18):
        cx = 11 if z < 9 else (12 if z < 14 else 11)
        for x in range(cx - 1, cx + 2):
            b.put(x, 2, z, 'polished_andesite' if x == cx else 'stone_bricks', component='path')
    for x in range(7, 17):
        for z in (10, 11, 12, 13):
            b.put(x, 2, z, 'polished_andesite', component='path')
    # Central raised stone-brick & moss planter feature
    b.box(10, 2, 11, 13, 2, 12, 'stone_bricks')
    b.box(11, 3, 11, 12, 3, 12, 'moss_block')
    b.put(11, 4, 11, 'flowering_azalea')
    b.put(12, 4, 12, 'cornflower')
    # Two park benches facing plaza
    b.bench(7, 9, 9, 9, 3, 'south', 'spruce')
    b.bench(14, 14, 16, 14, 3, 'north', 'spruce')
    # Canonical BCParks post plaque + stone lamp piers
    b.bcparks_post_sign(8, 3, 6, 'north', 'Cedar Creek')
    for lx, lz in ((9, 6), (15, 6), (7, 14), (16, 10)):
        b.put(lx, 3, lz, 'stone_brick_wall', component='lights')
        b.put(lx, 4, lz, 'lantern', component='lights')
    # Post-mounted mailbox + park waste/recycling heads
    b.put(14, 3, 5, 'iron_bars')
    b.head(14, 4, 5, 'mailbox_orange', facing='north')
    b.put(16, 2, 6, 'polished_andesite')
    b.head(16, 3, 6, 'trash_bin', facing='west')
    b.put(16, 2, 7, 'polished_andesite')
    b.head(16, 3, 7, 'recycling_bin', facing='west')
    # Organic PNW conifer and forked broadleaf
    b.conifer(5, 3, 16, height=10, seed=3)
    b.broadleaf(18, 3, 15, height=8, seed=5)
    for x, z, fl in (
        (5, 7, 'poppy'), (6, 8, 'dandelion'), (7, 7, 'cornflower'),
        (17, 7, 'oxeye_daisy'), (18, 8, 'poppy'), (19, 7, 'red_tulip'),
        (6, 12, 'fern'), (18, 11, 'azalea'),
    ):
        b.put(x, 3, z, fl)
    return b.result()


def _sloped_cafe() -> dict[str, Any]:
    out = demo.example(True)
    out['provenance'] = PROVENANCE
    return out


def _shop_renovation() -> dict[str, Any]:
    b = VoxelBuilder('renovation')
    # Fit out interior x=4..14, z=8..16, y=3..7 without touching protected shell x=3..15, z=7..17 or (4,5..6,8)
    # L-shaped quartz & oak bakery/espresso bar (zero bookshelf filler!)
    b.box(5, 3, 13, 10, 3, 14, 'smooth_quartz', component='furniture')
    b.box(5, 3, 11, 5, 3, 12, 'stripped_spruce_wood[axis=y]', component='furniture')
    b.head(5, 4, 13, 'espresso_machine', facing='north')
    b.head(6, 4, 13, 'coffee_maker', facing='north')
    b.head(7, 4, 13, 'croissant', facing='north')
    b.head(8, 4, 13, 'pastry_box', facing='north')
    b.head(9, 4, 13, 'pos_terminal', facing='north')
    b.head(10, 4, 13, 'card_reader', facing='north')
    b.head(5, 4, 11, 'cheesecake', facing='east')
    b.head(5, 4, 12, 'tea_tin', facing='east')
    # Back counter timber display credenza with chiseled_bookshelf & teapot
    b.box(6, 3, 16, 9, 3, 16, 'stripped_oak_wood[axis=x]', component='furniture')
    b.put(7, 4, 16, 'chiseled_bookshelf[facing=north]', component='furniture')
    b.head(8, 4, 16, 'teapot', facing='north')
    # Two customer booths along east wall (x=12..14)
    for bz in (10, 14):
        b.put(13, 3, bz - 1, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
        b.put(13, 3, bz, 'oak_slab[type=top]', component='furniture')
        b.put(13, 3, bz + 1, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.head(13, 4, 10, 'latte_cup', facing='west')
    # Interior Renovated placard at (14,5,9) + visible stone_axe item_frame at (14,6,9) against protected x=15 wall
    b.dedication_placard(14, 5, 9, 'west', 'Nov. 16,', '2026', label='Renovated', tool='stone_axe')
    b.head(8, 5, 8, 'emergency_exit_light_caged', facing='south', wall=True)
    # Slatted ceiling accents & warm pendant lanterns under protected y=8 roof
    for x in (6, 9, 12):
        for z in (10, 14):
            b.put(x, 7, z, 'lantern[hanging=true]', component='lights')
    for x in range(5, 14):
        b.put(x, 7, 12, 'end_rod[facing=east]' if 6 <= x <= 12 else 'oak_trapdoor[facing=north,half=top,open=false]', component='lights')
    # Exterior forecourt, canopy awning, address plaque & shop signage outside x=3..15, z=7..17
    b.box(4, 2, 5, 14, 2, 6, 'polished_andesite', component='apron')
    for x in range(5, 14):
        b.put(x, 6, 6, 'deepslate_tile_slab[type=top]', component='canopy')
    b.put(8, 5, 6, 'lantern[hanging=true]', component='lights')
    b.address_plaque(9, 4, 6, 'north', 42, 'Heritage Row', '古蹟巷')
    b.sign(7, 7, 6, 'north', ['Chia Te Bakery', '佳德鳳梨酥', '--------------', 'Pastry & Tea'], wood='spruce', component='facade')
    b.framed_sign(10, 5, 6, 'north', 'Open 08-19h', 'Baked Fresh', wood='birch', component='facade')
    b.bench(4, 6, 5, 6, 3, 'north', 'spruce')
    b.put(13, 3, 6, 'azalea_leaves[persistent=true]', component='garden')
    b.put(14, 3, 6, 'flowering_azalea_leaves[persistent=true]', component='garden')
    return b.result()


def _small_house() -> dict[str, Any]:
    b = VoxelBuilder('house')
    # Two-storey detached PNW villa x=4..16, z=7..17 (floor y=2, upper y=6, eaves y=10)
    b.box(4, 2, 7, 16, 2, 17, 'stone_bricks', component='floor')
    b.box(5, 2, 8, 15, 2, 16, 'spruce_planks', component='floor')
    b.box(4, 3, 7, 16, 9, 17, 'bricks', component='wall')
    b.box(5, 3, 8, 15, 5, 16, 'air', component='interior')
    b.box(4, 6, 7, 16, 6, 17, 'smooth_quartz', component='floor')
    b.box(5, 6, 8, 15, 6, 16, 'oak_planks', component='floor')
    b.box(5, 7, 8, 15, 9, 16, 'air', component='interior')
    for y in range(3, 10):
        for cx, cz in ((4, 7), (16, 7), (4, 17), (16, 17)):
            b.put(cx, y, cz, 'smooth_quartz', component='wall')

    # Paved front walkway + 1-block recessed porch portal at x=10..12, z=7 (door at x=11, z=8)
    b.box(10, 2, 5, 12, 2, 6, 'stone_bricks', component='path')
    b.recessed_north_portal(10, 12, 3, 7, door_xs=11, door_wood='spruce', pier_mat='smooth_quartz', height=3)
    b.box(10, 6, 6, 12, 6, 6, 'smooth_quartz_slab[type=bottom]', component='canopy')

    # Grounded two-storey front bay window on left (x=5..8, z=6, y=2..10)
    b.box(5, 2, 6, 8, 2, 6, 'stone_bricks', component='facade')
    for x in range(5, 9):
        post = x in (5, 8)
        for y in range(3, 10):
            if post:
                b.put(x, y, 6, 'stripped_spruce_wood[axis=y]', component='facade')
            elif y in (6, 3, 7):
                b.put(x, y, 6, 'smooth_quartz', component='facade')
            else:
                b.put(x, y, 6, 'gray_stained_glass_pane', component='window')
                b.put(x, y, 7, 'air', component='interior')
        b.put(x, 10, 6, 'smooth_quartz_slab[type=bottom]', component='facade')

    # Dressed windows with sills & shutters across all 4 elevations (north, west, east, south)
    b.dressed_window('north', 7, 13, 14, 4, 5)
    b.dressed_window('north', 7, 10, 14, 8, 9)
    b.dressed_window('west', 4, 10, 13, 4, 5)
    b.dressed_window('west', 4, 10, 13, 8, 9)
    b.dressed_window('east', 16, 13, 15, 4, 5, shutter_wood=None)
    b.dressed_window('east', 16, 13, 15, 8, 9, shutter_wood=None)
    b.dressed_window('south', 17, 6, 8, 4, 5)
    b.dressed_window('south', 17, 11, 13, 4, 5)
    b.dressed_window('south', 17, 6, 8, 8, 9)
    b.dressed_window('south', 17, 11, 13, 8, 9)

    # Headroom-safe interior stair along x=15, z=9..12 rising y=3..6 (air carved at y=6..8 above steps!)
    for i, z in enumerate((9, 10, 11, 12)):
        sy = 3 + i
        b.put(15, sy, z, 'oak_stairs[facing=south,half=bottom]', component='stairs')
        if sy > 3:
            b.box(15, 3, z, 15, sy - 1, z, 'bookshelf', component='furniture')
        for hy in (1, 2, 3):
            b.put(15, sy + hy, z, 'air', component='stairs')

    # Ground floor living room & kitchen with appliance custom heads
    b.box(6, 3, 9, 8, 3, 11, 'light_gray_carpet', component='furniture')
    b.put(6, 3, 12, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.put(8, 3, 12, 'scaffolding', component='furniture')
    b.head(8, 4, 12, 'plant_pot', facing='north')
    b.box(5, 3, 15, 9, 3, 16, 'smooth_quartz', component='furniture')
    b.put(5, 3, 16, 'smoker[facing=north]')
    b.put(6, 3, 16, 'water_cauldron[level=3]')
    b.put(6, 4, 16, 'tripwire_hook[facing=north]')
    b.head(7, 4, 16, 'coffee_maker', facing='north')
    b.head(8, 4, 16, 'toaster', facing='north')
    b.head(9, 4, 16, 'kettle', facing='north')

    # Upper floor bedroom (paired bed + desk) & domestic washroom
    b.bed(6, 7, 14, 'south', 'red')
    b.put(8, 7, 15, 'barrel[facing=up]')
    b.head(8, 8, 15, 'desk_lamp', facing='north')
    b.put(9, 7, 15, 'smooth_quartz', component='furniture')
    b.head(9, 8, 15, 'book_stack', facing='north')
    b.put(12, 7, 16, 'water_cauldron[level=3]')
    b.put(12, 8, 16, 'tripwire_hook[facing=north]')
    b.put(13, 7, 16, 'water_cauldron[level=1]')
    b.put(13, 8, 16, 'iron_trapdoor[facing=north,half=bottom,open=true]')
    b.put(13, 9, 16, 'stone_button[face=wall,facing=north]')

    # Signage & lighting
    b.address_plaque(12, 4, 6, 'north', 18, 'Maple Cres', '楓樹彎')
    b.framed_sign(9, 4, 6, 'north', 'Cedar Villa', 'No. 18', wood='spruce', component='facade')
    b.dedication_placard(9, 4, 8, 'south', 'Nov. 14,', '2026', tool='stone_axe')
    for x in (7, 12):
        for z in (10, 14):
            b.put(x, 5, z, 'lantern[hanging=true]', component='lights')
            b.put(x, 9, z, 'lantern[hanging=true]', component='lights')

    # Pitched gable roof with overhanging eaves & low 2-block-clear brick chimney
    b.box(4, 10, 7, 16, 10, 17, 'smooth_quartz', component='roof')
    for i in range(7):
        y = 10 + i
        lx, rx = 3 + i, 17 - i
        for z in range(6, 19):
            if lx < rx:
                b.put(lx, y, z, 'deepslate_tile_stairs[facing=east,half=bottom]', component='roof')
                b.put(rx, y, z, 'deepslate_tile_stairs[facing=west,half=bottom]', component='roof')
            elif lx == rx:
                b.put(lx, y, z, 'deepslate_tile_slab[type=bottom]', component='roof')
        if i >= 1:
            for x in range(lx + 1, rx):
                for z in (7, 17):
                    b.put(x, y, z, 'gray_stained_glass_pane' if (i == 2 and x == 10) else 'spruce_planks', component='wall')
    for cy in range(11, 16):
        b.put(14, cy, 15, 'bricks', component='chimney')
    b.put(14, 16, 15, 'stone_brick_wall', component='chimney')

    # Planted front garden
    for x, fl in ((4, 'azalea'), (5, 'poppy'), (6, 'cornflower'), (13, 'oxeye_daisy'), (14, 'dandelion'), (15, 'red_tulip')):
        b.put(x, 3, 5, fl, component='garden')
    return b.result()


def _utility_substation() -> dict[str, Any]:
    b = VoxelBuilder('substation')
    # CLP Power 132kV Urban GIS Substation (358 Pacific Ave) at x=2..19, z=6..17
    b.box(2, 2, 6, 19, 2, 17, 'polished_andesite', component='floor')
    b.box(4, 2, 5, 7, 2, 5, 'polished_andesite', component='apron')

    # Articulated GIS & SCADA Control Hall at x=2..10, z=6..15, y=3..7
    b.box(2, 3, 6, 10, 7, 15, 'light_gray_concrete', component='wall')
    b.box(3, 3, 7, 9, 6, 14, 'air', component='interior')
    for y in range(3, 8):
        for cx, cz in ((2, 6), (6, 6), (10, 6), (2, 10), (2, 15), (6, 15), (10, 15), (10, 10)):
            b.put(cx, y, cz, 'polished_deepslate', component='wall')
    b.box(2, 7, 6, 10, 7, 15, 'smooth_quartz', component='roof')
    for x in range(2, 11):
        b.put(x, 8, 6, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(x, 8, 15, 'stone_brick_slab[type=bottom]', component='roof')
    for z in range(6, 16):
        b.put(2, 8, z, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(10, 8, z, 'stone_brick_slab[type=bottom]', component='roof')

    # 1-block recessed north service door at x=4..6, z=6 (door at x=5, z=7)
    b.recessed_north_portal(4, 6, 3, 6, door_xs=5, door_wood='iron', pier_mat='polished_deepslate', jamb_mat='gray_stained_glass', height=3)
    # Acoustic louvers, clerestory glazing & proud sills/fins across all 4 elevations
    b.dressed_window('north', 6, 7, 9, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood='acacia')
    b.dressed_window('west', 2, 8, 9, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood='acacia')
    b.dressed_window('west', 2, 12, 13, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood='acacia')
    b.dressed_window('south', 15, 4, 5, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood='acacia')
    b.dressed_window('south', 15, 7, 9, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood='acacia')
    b.dressed_window('east', 10, 8, 9, 4, 5, glass='gray_stained_glass', sill_stair='smooth_quartz_stairs', shutter_wood=None)
    for z in (12, 13):
        b.put(10, 4, z, 'iron_bars', component='wall')
        b.put(10, 5, z, 'iron_bars', component='wall')
        b.put(11, 3, z, 'smooth_quartz_stairs[facing=west,half=top]', component='relief')

    # Rooftop 2x2 quartz+rail exhaust fan & AC condenser
    b.fan_unit_2x2(4, 8, 10)
    b.head(8, 8, 10, 'ac_unit', facing='north', component='roof')

    # SCADA control desk, GIS cabinets, lighting & Built placard + stone_axe frame
    b.box(3, 3, 12, 6, 3, 13, 'smooth_quartz', component='furniture')
    b.head(4, 4, 12, 'computer_monitor', facing='north')
    b.head(5, 4, 12, 'radio_transceiver', facing='north')
    b.box(8, 3, 11, 9, 5, 13, 'iron_block', component='furniture')
    b.head(7, 4, 12, 'electrical_panel', facing='west', wall=True)
    b.head(9, 4, 9, 'server_unit', facing='west')
    b.put(9, 3, 9, 'polished_andesite', component='furniture')
    b.dedication_placard(3, 5, 8, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    b.put(5, 6, 9, 'sea_lantern', component='lights')
    b.put(7, 6, 12, 'sea_lantern', component='lights')

    # Exterior CLP identity, address & HV warning signage
    b.address_plaque(6, 4, 5, 'north', 358, 'Pacific Ave', '太平洋大道')
    b.sign(8, 6, 5, 'north', ['| CLP Power |', '-------------', '132kV GIS Stn', '中華電力變電站'], wood='birch', component='facade')
    b.framed_sign(11, 4, 5, 'north', 'DANGER 132kV', 'Auth. Only', wood='oak', component='facade')

    # Enclosed outdoor HV transformer bay (x=11..19, z=6..17): grounded sill + iron_bars + top lintel (zero floating_pane!)
    for x in range(11, 20):
        for z in (6, 17):
            is_pier = x in (11, 15, 19)
            if z == 6 and x == 13:
                b.put(x, 3, z, 'spruce_fence_gate[facing=north,open=false]')
                b.put(x, 4, z, 'air')
                b.put(x, 5, z, 'polished_deepslate')
                continue
            b.put(x, 3, z, 'polished_deepslate' if is_pier else 'stone_bricks')
            b.put(x, 4, z, 'polished_deepslate' if is_pier else 'iron_bars')
            b.put(x, 5, z, 'polished_deepslate')
    for z in range(7, 17):
        is_pier = z in (11, 12)
        b.put(19, 3, z, 'polished_deepslate' if is_pier else 'stone_bricks')
        b.put(19, 4, z, 'polished_deepslate' if is_pier else 'iron_bars')
        b.put(19, 5, z, 'polished_deepslate')
    for z in (16, 17):
        b.box(2, 3, z, 10, 3, z, 'stone_bricks')

    # Two detailed HV transformers with radiator fins, copper conservators, porcelain bushings & overhead busbar
    for tz in (9, 14):
        b.box(13, 3, tz - 1, 16, 4, tz + 1, 'polished_andesite')
        for rx in (13, 16):
            b.put(rx, 3, tz - 2 if tz == 14 else tz + 2, 'iron_trapdoor[facing=north,half=bottom,open=true]')
        b.box(14, 5, tz, 15, 5, tz, 'copper_block')
        for bx in (13, 15, 16):
            b.put(bx, 5 if bx != 15 else 6, tz, 'lightning_rod')
    b.put(11, 6, 6, 'lantern', component='lights')
    b.put(19, 6, 6, 'lantern', component='lights')
    b.put(19, 6, 17, 'lantern', component='lights')
    # Kerbside fire_hydrant & planted street buffer
    b.put(12, 2, 5, 'polished_andesite', component='apron')
    b.head(12, 3, 5, 'fire_hydrant', facing='north')
    b.head(10, 6, 5, 'security_camera', facing='north', wall=True)
    for x, fl in ((14, 'azalea'), (15, 'fern'), (16, 'flowering_azalea'), (17, 'dandelion'), (18, 'poppy')):
        b.put(x, 3, 5, fl, component='garden')
    return b.result()


def _canal_crossing() -> dict[str, Any]:
    b = VoxelBuilder('canal')
    # Walkable stone-brick & quartz footbridge spanning protected canal z=7..10 at y=4 (banks sit at y=3)
    b.box(9, 3, 5, 14, 3, 6, 'polished_andesite', component='path')
    for x in (11, 12):
        b.put(x, 4, 6, 'stone_brick_stairs[facing=south,half=bottom]', component='bridge')
        b.put(x, 4, 11, 'stone_brick_stairs[facing=north,half=bottom]', component='bridge')
    b.box(10, 4, 7, 13, 4, 10, 'stone_bricks', component='bridge')
    for x in (10, 13):
        b.put(x, 4, 6, 'stone_bricks', component='bridge')
        b.put(x, 4, 11, 'stone_bricks', component='bridge')
        for z in range(6, 12):
            b.put(x, 5, z, 'stone_brick_wall', component='bridge')
        b.put(x, 6, 7, 'lantern', component='lights')
        b.put(x, 6, 10, 'lantern', component='lights')

    # South bank stone quay plaza (z=11..13) & outdoor canal-view seating
    b.box(7, 3, 12, 15, 3, 13, 'polished_andesite', component='apron')
    b.bench(7, 12, 8, 12, 4, 'north', 'spruce')
    b.head(15, 4, 12, 'trash_bin', facing='west')

    # Waterside Tea Kiosk (茗香茶室) at x=6..16, z=13..20, floor y=3, walls y=4..7
    b.box(6, 3, 13, 16, 3, 20, 'stone_bricks', component='floor')
    b.box(7, 3, 14, 15, 3, 19, 'spruce_planks', component='floor')
    b.box(6, 4, 13, 16, 7, 20, 'calcite', component='wall')
    b.box(7, 4, 14, 15, 6, 19, 'air', component='interior')
    for y in range(4, 8):
        for cx, cz in ((6, 13), (16, 13), (6, 20), (16, 20)):
            b.put(cx, y, cz, 'stripped_spruce_wood[axis=y]', component='wall')
    b.box(6, 7, 13, 16, 7, 20, 'stripped_spruce_wood[axis=x]', component='roof')

    # 1-block recessed canal-front entrance portal at x=10..12, y=4..6, z=13 (door at x=11, z=14 >= 12!)
    b.recessed_north_portal(10, 12, 4, 13, door_xs=11, door_wood='spruce', pier_mat='stripped_spruce_wood[axis=y]', height=3)

    # Dressed windows & wooden lattice shutters across all 4 elevations
    b.dressed_window('north', 13, 7, 9, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('north', 13, 13, 15, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('west', 6, 15, 18, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('east', 16, 15, 18, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 20, 8, 10, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 20, 12, 14, 5, 6, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')

    # Overhanging tiered hipped roof (anchored to y=7 roof plate — zero floating_slab!)
    b.box(5, 8, 12, 17, 8, 21, 'deepslate_tile_slab[type=bottom]', component='roof')
    b.box(6, 8, 13, 16, 8, 20, 'deepslate_tiles', component='roof')
    b.box(7, 9, 14, 15, 9, 19, 'deepslate_tiles', component='roof')
    b.box(8, 10, 15, 14, 10, 18, 'deepslate_tile_slab[type=bottom]', component='roof')

    # Tea bar, custom heads, indoor seating, lanterns & signage
    b.box(7, 4, 18, 11, 4, 19, 'smooth_quartz', component='furniture')
    b.head(7, 5, 18, 'coffee_maker', facing='north')
    b.head(8, 5, 18, 'teapot', facing='north')
    b.head(9, 5, 18, 'tea_tin', facing='north')
    b.head(10, 5, 18, 'cheesecake', facing='north')
    b.head(11, 5, 18, 'pos_terminal', facing='north')
    b.put(14, 4, 16, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
    b.put(14, 4, 17, 'oak_slab[type=top]', component='furniture')
    b.put(14, 4, 18, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.head(14, 5, 17, 'latte_cup', facing='west')
    b.put(9, 6, 16, 'lantern[hanging=true]', component='lights')
    b.put(13, 6, 16, 'lantern[hanging=true]', component='lights')

    b.address_plaque(10, 5, 12, 'north', 6, 'Canal Walk', '運河步道')
    b.sign(13, 6, 12, 'north', ['Canal Tea', '運河茗香茶室', '-------------', '09:00 - 20:00'], wood='spruce', component='facade')
    b.dedication_placard(7, 5, 15, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    return b.result()


def _corner_shophouse() -> dict[str, Any]:
    b = VoxelBuilder('shophouse')
    # Sun Wah Bakery (新華餅家, 202 Pacific Ave): body at x=5..17, z=6..17, using x=4 and z=5 as 1-block street setback!
    b.box(4, 2, 5, 17, 2, 17, 'polished_andesite', component='floor')
    b.box(6, 2, 7, 16, 2, 16, 'smooth_stone', component='floor')
    b.box(5, 3, 6, 17, 10, 17, 'bricks', component='wall')
    b.box(6, 3, 7, 16, 5, 16, 'air', component='interior')
    b.box(5, 6, 6, 17, 6, 17, 'smooth_quartz', component='floor')
    b.box(6, 6, 7, 16, 6, 16, 'spruce_planks', component='floor')
    b.box(6, 7, 7, 16, 9, 16, 'air', component='interior')
    for y in range(3, 6):
        for cx, cz in ((5, 6), (11, 6), (17, 6), (5, 11), (5, 17), (17, 17)):
            b.put(cx, y, cz, 'polished_deepslate', component='wall')

    # Dual-frontage ground bakery shopfront: 1-block recessed north portal (x=8..10, z=6) + smoked glazing on z=6 & x=5
    b.recessed_north_portal(8, 10, 3, 6, door_xs=9, door_wood='dark_oak', pier_mat='polished_deepslate', height=3, uplight=True)
    for x in (6, 7, 12, 13, 14, 15):
        b.box(x, 4, 6, x, 5, 6, 'gray_stained_glass', component='window')
        b.put(x, 6, 5, 'smooth_quartz_slab[type=top]', component='canopy')
    for z in (7, 8, 9, 10, 12, 13, 14, 15):
        b.box(5, 4, z, 5, 5, z, 'gray_stained_glass', component='window')
        b.put(4, 6, z, 'smooth_quartz_slab[type=top]', component='canopy')

    # Upper-floor fenestration & non-planar dressed sills/shutters on ALL 4 elevations
    b.dressed_window('north', 6, 6, 8, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('north', 6, 12, 15, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('west', 5, 7, 9, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('west', 5, 12, 15, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('east', 17, 7, 9, 4, 5, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('east', 17, 7, 9, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('east', 17, 13, 15, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 17, 7, 9, 4, 5, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 17, 7, 9, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 17, 12, 14, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')

    # Headroom-safe interior stair along east wall (x=16, z=9..12) to upper studio flat (feet y=7)
    for i, z in enumerate((9, 10, 11, 12)):
        sy = 3 + i
        b.put(16, sy, z, 'oak_stairs[facing=south,half=bottom]', component='stairs')
        if sy > 3:
            b.box(16, 3, z, 16, sy - 1, z, 'smooth_quartz', component='wall')
        for hy in (1, 2, 3):
            b.put(16, sy + hy, z, 'air', component='stairs')

    # Ground bakery/cafe counter & props (zero ground-floor bookshelf filler!)
    b.box(10, 3, 13, 14, 3, 14, 'smooth_quartz', component='furniture')
    b.head(10, 4, 13, 'espresso_machine', facing='north')
    b.head(11, 4, 13, 'coffee_maker', facing='north')
    b.head(12, 4, 13, 'bread_loaf', facing='north')
    b.head(13, 4, 13, 'croissant', facing='north')
    b.head(14, 4, 13, 'pos_terminal', facing='north')
    b.head(14, 4, 14, 'card_reader', facing='west')
    b.put(7, 3, 11, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
    b.put(7, 3, 12, 'oak_slab[type=top]', component='furniture')
    b.put(7, 3, 13, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.head(7, 4, 12, 'pastry_box', facing='east')

    # Upper studio apartment (y=7..9): paired bed, kitchen, bookshelves & lighting
    b.bed(7, 7, 14, 'south', 'blue')
    b.put(11, 7, 15, 'bookshelf', component='furniture')
    b.put(12, 7, 15, 'bookshelf', component='furniture')
    b.put(14, 7, 15, 'smooth_quartz', component='furniture')
    b.head(14, 8, 15, 'kettle', facing='north')
    for lx, lz in ((8, 9), (13, 9), (8, 14), (13, 14)):
        b.put(lx, 5, lz, 'lantern[hanging=true]', component='lights')
        b.put(lx, 9, lz, 'lantern[hanging=true]', component='lights')

    # Flat roof (y=10) with parapet, 2x2 quartz+rail exhaust fan, solar array & ac_unit
    b.box(5, 10, 6, 17, 10, 17, 'smooth_stone', component='roof')
    for x in range(5, 18):
        b.put(x, 11, 6, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(x, 11, 17, 'stone_brick_slab[type=bottom]', component='roof')
    for z in range(6, 18):
        b.put(5, 11, z, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(17, 11, z, 'stone_brick_slab[type=bottom]', component='roof')
    b.fan_unit_2x2(7, 11, 13)
    for sx in range(11, 15):
        for sz in (13, 14):
            b.put(sx, 11, sz, 'daylight_detector[inverted=true]', component='roof')
    b.head(9, 11, 9, 'ac_unit', facing='north', component='roof')

    # Signage: exterior address plaque, north fascia, west lane menu board & interior Built placard + stone_axe frame
    b.address_plaque(8, 4, 5, 'north', 202, 'Pacific Ave', '太平洋大道')
    b.sign(10, 5, 5, 'north', ['Sun Wah Bakery', '新華餅家', '--------------', 'Buns & Coffee'], wood='spruce', component='facade')
    b.framed_sign(4, 5, 11, 'west', 'Open 07-19h', 'Egg Tarts', wood='birch', component='facade')
    b.dedication_placard(16, 5, 8, 'west', 'Nov. 13,', '2026', tool='stone_axe')

    # East courtyard with post-mounted mailbox_orange, trash_bin & planted bed
    b.box(18, 2, 6, 21, 2, 16, 'polished_andesite', component='apron')
    b.put(19, 3, 7, 'iron_bars')
    b.head(19, 4, 7, 'mailbox_orange', facing='north')
    b.head(19, 3, 9, 'trash_bin', facing='east')
    for z, fl in ((12, 'azalea'), (13, 'poppy'), (14, 'cornflower'), (15, 'dandelion')):
        b.put(21, 2, z, 'grass_block')
        b.put(21, 3, z, fl, component='garden')
    return b.result()


def _party_wall_infill() -> dict[str, Any]:
    b = VoxelBuilder('infill')
    # Mercer Books (84 Mercer St): x=5..16, z=6..17 between protected party walls x=0..4 and x=17..23
    # Zero glazing on x=5 or x=16!
    b.box(5, 2, 5, 16, 2, 5, 'polished_andesite', component='apron')
    b.box(5, 2, 6, 16, 2, 17, 'spruce_planks', component='floor')
    b.box(5, 3, 6, 16, 10, 17, 'smooth_sandstone', component='wall')
    b.box(6, 3, 7, 15, 5, 16, 'air', component='interior')
    b.box(6, 6, 7, 15, 6, 16, 'oak_planks', component='floor')
    b.box(6, 7, 7, 15, 9, 16, 'air', component='interior')
    for y in range(3, 11):
        for px in (5, 16):
            b.put(px, y, 6, 'polished_deepslate', component='wall')
            b.put(px, y, 17, 'polished_deepslate', component='wall')

    # North street facade (z=6, setback z=5): 1-block recessed bookshop portal + projecting upper reading-room oriel bay!
    b.recessed_north_portal(9, 11, 3, 6, door_xs=10, door_wood='dark_oak', pier_mat='polished_deepslate', height=3, uplight=True)
    for x in (6, 7, 8, 12, 13, 14):
        b.box(x, 4, 6, x, 5, 6, 'gray_stained_glass', component='window')
    # Upper projecting oriel bay across x=7..14 at z=5 (supported on corbel stairs at y=5,z=5!)
    for x in range(7, 15):
        b.put(x, 5, 5, 'smooth_quartz_stairs[facing=south,half=top]', component='facade')
        b.put(x, 6, 5, 'smooth_quartz', component='facade')
        b.put(x, 10, 5, 'deepslate_tile_slab[type=bottom]', component='facade')
        post = x in (7, 14)
        for y in (7, 8, 9):
            b.put(x, y, 5, 'stripped_dark_oak_wood[axis=y]' if post else 'gray_stained_glass_pane',
                  component='facade' if post else 'window')
            if not post:
                b.put(x, y, 6, 'air', component='interior')

    # South courtyard facade (z=17, yard z=18..20): garden door + dressed windows & upper planted loggia
    b.door(10, 3, 17, 'south', 'dark_oak')
    b.put(10, 2, 18, 'stone_bricks', component='path')
    b.put(10, 5, 18, 'smooth_quartz_slab[type=top]', component='canopy')
    b.dressed_window('south', 17, 6, 8, 4, 5, sill_stair='smooth_quartz_stairs', shutter_wood='dark_oak')
    b.dressed_window('south', 17, 12, 14, 4, 5, sill_stair='smooth_quartz_stairs', shutter_wood='dark_oak')
    b.dressed_window('south', 17, 7, 13, 8, 9, sill_stair='smooth_quartz_stairs', shutter_wood='dark_oak')

    # Ground-floor oak bookshelf stacks (>= 4) + checkout desk with custom heads
    for z in range(9, 15):
        b.box(6, 3, z, 6, 5, z, 'bookshelf', component='furniture')
    b.box(12, 3, 13, 14, 3, 14, 'smooth_quartz', component='furniture')
    b.head(12, 4, 13, 'pos_terminal', facing='north')
    b.head(13, 4, 13, 'card_reader', facing='north')
    b.head(14, 4, 13, 'book_stack', facing='north')

    # Headroom-safe interior stair along east party wall (x=15, z=9..12) to upper reading room
    for i, z in enumerate((9, 10, 11, 12)):
        sy = 3 + i
        b.put(15, sy, z, 'oak_stairs[facing=south,half=bottom]', component='stairs')
        if sy > 3:
            b.box(15, 3, z, 15, sy - 1, z, 'bookshelf', component='furniture')
        for hy in (1, 2, 3):
            b.put(15, sy + hy, z, 'air', component='stairs')

    # Upper reading loft seating, tables, bookshelves & study heads
    for z in (9, 13):
        b.put(8, 7, z, 'spruce_stairs[facing=east,half=bottom]', component='furniture')
        b.put(9, 7, z, 'oak_slab[type=top]', component='furniture')
        b.put(10, 7, z, 'spruce_stairs[facing=west,half=bottom]', component='furniture')
    b.head(9, 8, 9, 'cup_coffee', facing='south')
    b.head(9, 8, 13, 'desk_lamp', facing='north')
    b.put(12, 7, 15, 'smooth_quartz', component='furniture')
    b.head(12, 8, 15, 'globe', facing='north')
    for z in (10, 11, 12):
        b.box(6, 7, z, 6, 8, z, 'chiseled_bookshelf[facing=east]', component='furniture')

    # Skylight roof, lighting & signage
    b.box(5, 10, 6, 16, 10, 17, 'deepslate_tiles', component='roof')
    b.box(8, 10, 10, 13, 10, 13, 'gray_stained_glass', component='roof')
    for x in (8, 13):
        for z in (9, 14):
            b.put(x, 5, z, 'lantern[hanging=true]', component='lights')
            b.put(x, 9, z, 'lantern[hanging=true]', component='lights')

    b.address_plaque(9, 4, 5, 'north', 84, 'Mercer St', '美瑟街')
    b.sign(11, 5, 5, 'north', ['Mercer Books', '美瑟書局', '------------', 'Rare & New'], wood='dark_oak', component='facade')
    b.framed_sign(13, 4, 5, 'north', 'Open 10-21h', 'Reading Loft', wood='birch', component='facade')
    b.dedication_placard(6, 5, 8, 'east', 'Nov. 14,', '2026', tool='stone_axe')

    # Planted rear courtyard garden at z=18..20
    b.bench(12, 19, 14, 19, 3, 'north', 'spruce')
    for x, z, fl in ((7, 19, 'azalea'), (8, 20, 'poppy'), (9, 19, 'fern'), (12, 20, 'cornflower'), (15, 19, 'dandelion')):
        b.put(x, 3, z, fl, component='garden')
    return b.result()


def _hillside_pavilion() -> dict[str, Any]:
    b = VoxelBuilder('pavilion')
    # Masonry-retained stepped mountain trail from north pavement (z=4, y=2) up to summit (z=15, y=8)
    for z in range(5, 16):
        target_y = min(8, 2 + (z - 3) // 2)
        for x in range(8, 11):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, target_y), target_y + 1):
                b.put(x, y, z, 'stone_bricks', component='steps')
            for y in range(target_y + 1, max(g, target_y) + 4):
                b.put(x, y, z, 'air', component='path')
        for sx in (7, 11):
            g = ground_at('hillside-pavilion', sx, z)
            for y in range(min(g, target_y), target_y + 1):
                b.put(sx, y, z, 'stone_bricks', component='foundation')
            b.put(sx, target_y + 1, z, 'stone_brick_wall', component='guard')
            if z in (7, 11, 14):
                b.put(sx, target_y + 2, z, 'lantern', component='lights')

    # Mid-slope rest landing at x=12..15, z=9..11, y=5
    for x in range(12, 16):
        for z in range(9, 12):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, 5), 6):
                b.put(x, y, z, 'stone_bricks' if y < 5 else 'polished_andesite', component='path')
            for y in range(6, 10):
                b.put(x, y, z, 'air')
    b.bench(13, 11, 14, 11, 6, 'north', 'spruce')
    b.box(15, 6, 9, 15, 7, 9, 'stone_bricks', component='park-sign')
    b.framed_sign(15, 7, 8, 'north', 'Summit Trail', 'Tea Lookout ^', wood='spruce', component='park-sign')

    # Summit masonry terrace & Cloudveil Tea Pavilion (雲嶺茶亭) at x=5..15, z=15..20, floor y=8
    for x in range(5, 16):
        for z in range(14, 21):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, 8), 9):
                surf = 'polished_andesite' if z == 14 else ('stone_bricks' if (x in (5, 15) or z in (15, 20)) else 'spruce_planks')
                b.put(x, y, z, 'stone_bricks' if y < 8 else surf, component='floor')
            for y in range(9, 16):
                b.put(x, y, z, 'air')

    b.box(5, 9, 15, 15, 12, 20, 'calcite', component='wall')
    b.box(6, 9, 16, 14, 11, 19, 'air', component='interior')
    for y in range(9, 13):
        for cx, cz in ((5, 15), (15, 15), (5, 20), (15, 20)):
            b.put(cx, y, cz, 'stripped_spruce_wood[axis=y]', component='wall')
    b.box(5, 12, 15, 15, 12, 20, 'stripped_spruce_wood[axis=x]', component='roof')

    # 1-block recessed summit entrance portal at x=8..10, y=9..11, z=15 (door at x=9, y=9, z=16 -> y>=8!)
    b.recessed_north_portal(8, 10, 9, 15, door_xs=9, door_wood='spruce', pier_mat='stripped_spruce_wood[axis=y]', height=3)

    # Panoramas & non-planar sills/eaves on all 4 elevations
    b.dressed_window('north', 15, 6, 7, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('north', 15, 12, 14, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('west', 5, 17, 18, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('east', 15, 17, 18, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 20, 7, 9, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')
    b.dressed_window('south', 20, 11, 13, 10, 11, sill_stair='smooth_quartz_stairs', shutter_wood='spruce')

    # Overhanging tiered hipped roof (y=13..15)
    b.box(4, 13, 14, 16, 13, 21, 'deepslate_tile_slab[type=bottom]', component='roof')
    b.box(5, 13, 15, 15, 13, 20, 'deepslate_tiles', component='roof')
    b.box(6, 14, 16, 14, 14, 19, 'deepslate_tiles', component='roof')
    b.box(7, 15, 17, 13, 15, 18, 'deepslate_tile_slab[type=bottom]', component='roof')

    # Tea counter, custom heads, seating, lanterns & signage
    b.box(6, 9, 18, 9, 9, 19, 'smooth_quartz', component='furniture')
    b.head(6, 10, 18, 'teapot', facing='north')
    b.head(7, 10, 18, 'tea_tin', facing='north')
    b.head(8, 10, 18, 'latte_cup', facing='north')
    b.head(9, 10, 18, 'bonsai_pot', facing='north')
    b.put(13, 9, 18, 'spruce_stairs[facing=west,half=bottom]', component='furniture')
    b.put(12, 9, 18, 'oak_slab[type=top]', component='furniture')
    b.put(8, 11, 17, 'lantern[hanging=true]', component='lights')
    b.put(12, 11, 17, 'lantern[hanging=true]', component='lights')

    b.address_plaque(8, 10, 14, 'north', 1, 'Summit Trl', '雲嶺徑')
    b.sign(11, 11, 14, 'north', ['Cloudveil Tea', '雲嶺茶亭', '-------------', 'Summit 110m'], wood='spruce', component='facade')
    b.dedication_placard(14, 10, 16, 'west', 'Nov. 14,', '2026', tool='stone_axe')

    # PNW slope conifers
    b.conifer(3, ground_at('hillside-pavilion', 3, 11) + 1, 11, height=9, seed=1)
    b.conifer(19, ground_at('hillside-pavilion', 19, 13) + 1, 13, height=9, seed=2)
    return b.result()


def _rowhouse_terrace() -> dict[str, Any]:
    b = VoxelBuilder('rowhouse')
    # Three attached 2-storey rowhouses across x=3..26, z=6..18 (leaving x=2 and x=27 for end-flank window relief!)
    units = [
        (3, 10, 'bricks', 'smooth_quartz', 'red', 'dark_oak', 10, 'toaster', 'plant_pot'),
        (10, 18, 'calcite', 'polished_deepslate', 'blue', 'spruce', 12, 'coffee_maker', 'book_stack'),
        (18, 26, 'smooth_sandstone', 'smooth_quartz', 'green', 'oak', 14, 'kettle', 'desk_lamp'),
    ]
    for idx, (x0, x1, wall_mat, pier_mat, bed_col, wood, num, app_head, study_head) in enumerate(units):
        b.box(x0, 2, 6, x1, 2, 18, 'stone_bricks', component='floor')
        b.box(x0 + 1, 2, 7, x1 - 1, 2, 17, 'spruce_planks', component='floor')
        b.box(x0, 3, 6, x1, 10, 18, wall_mat, component='wall')
        b.box(x0 + 1, 3, 7, x1 - 1, 5, 17, 'air', component='interior')
        b.box(x0, 6, 6, x1, 6, 18, pier_mat, component='floor')
        b.box(x0 + 1, 6, 7, x1 - 1, 6, 17, 'oak_planks', component='floor')
        b.box(x0 + 1, 7, 7, x1 - 1, 9, 17, 'air', component='interior')
        for y in range(3, 11):
            b.put(x0, y, 6, pier_mat, component='wall')
            b.put(x1, y, 6, pier_mat, component='wall')
            b.put(x0, y, 18, pier_mat, component='wall')
            b.put(x1, y, 18, pier_mat, component='wall')

        # Distinct parapet skyline & roof solar/AC details
        top_y = 11 if idx == 1 else 10
        b.box(x0, 10, 6, x1, top_y, 18, 'smooth_stone', component='roof')
        for x in range(x0, x1 + 1):
            b.put(x, top_y + 1, 6, 'stone_brick_slab[type=bottom]', component='roof')
            b.put(x, top_y + 1, 18, 'stone_brick_slab[type=bottom]', component='roof')
        for sx in range(x0 + 2, x1 - 2):
            b.put(sx, top_y + 1, 14, 'daylight_detector[inverted=true]', component='roof')

        # Paved stoop & 1-block recessed front porch portal
        dx = x0 + 2
        b.box(dx - 1, 2, 5, dx + 1, 2, 5, 'polished_andesite', component='apron')
        b.recessed_north_portal(dx - 1, dx + 1, 3, 6, door_xs=dx, door_wood=wood, pier_mat=pier_mat, height=3)
        b.address_plaque(dx + 1, 4, 5, 'north', num, 'Alder Row', '赤楊排屋')

        # Front & rear windows + upper bay/ledge variation
        b.dressed_window('north', 6, x0 + 4, x1 - 2, 4, 5, shutter_wood=None)
        if idx == 0:
            # Projecting upper oriel bay on Unit 1
            for ox in range(x0 + 3, x1 - 1):
                b.put(ox, 6, 5, 'smooth_quartz_stairs[facing=south,half=top]', component='facade')
                b.put(ox, 10, 5, 'smooth_quartz_slab[type=bottom]', component='facade')
                for oy in (7, 8, 9):
                    b.put(ox, oy, 5, pier_mat if ox in (x0 + 3, x1 - 2) else 'gray_stained_glass_pane', component='facade')
                    if ox not in (x0 + 3, x1 - 2):
                        b.put(ox, oy, 6, 'air', component='interior')
        else:
            b.dressed_window('north', 6, x0 + 2, x1 - 2, 8, 9, shutter_wood='spruce')
        b.dressed_window('south', 18, x0 + 2, x0 + 3, 4, 5, shutter_wood='spruce')
        b.dressed_window('south', 18, x0 + 5, x1 - 2, 4, 5, shutter_wood=None)
        b.dressed_window('south', 18, x0 + 2, x1 - 2, 8, 9, shutter_wood='spruce')

        # Headroom-safe interior stair along x1-1, z=9..12
        sx = x1 - 1
        for i, z in enumerate((9, 10, 11, 12)):
            sy = 3 + i
            b.put(sx, sy, z, f'{wood}_stairs[facing=south,half=bottom]', component='stairs')
            if sy > 3:
                b.box(sx, 3, z, sx, sy - 1, z, 'bookshelf', component='furniture')
            for hy in (1, 2, 3):
                b.put(sx, sy + hy, z, 'air', component='stairs')

        # Furnishings & custom heads per rowhouse
        b.box(x0 + 2, 3, 15, x0 + 4, 3, 16, 'smooth_quartz', component='furniture')
        b.head(x0 + 2, 4, 15, app_head, facing='north')
        b.put(x0 + 4, 3, 11, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
        b.bed(x0 + 2, 7, 15, 'south', bed_col)
        b.put(x0 + 4, 7, 16, 'barrel[facing=up]')
        b.head(x0 + 4, 8, 16, study_head, facing='north')
        b.put(x0 + 4, 5, 11, 'lantern[hanging=true]', component='lights')
        b.put(x0 + 4, 9, 11, 'lantern[hanging=true]', component='lights')
        b.put(x0 + 4, 5, 15, 'lantern[hanging=true]', component='lights')
        b.put(x0 + 4, 9, 15, 'lantern[hanging=true]', component='lights')
        if idx == 1:
            b.dedication_placard(x0 + 1, 5, 8, 'east', 'Nov. 14,', '2026', tool='stone_axe')
        else:
            b.framed_sign(x0 + 1, 5, 8, 'east', f'Unit {num}', 'Alder Row', wood='birch', component='interior')

        # Rear garden & front hedge
        for gx in range(x0 + 4, x1):
            b.put(gx, 3, 5, 'azalea_leaves[persistent=true]', component='garden')
        b.put(x0 + 3, 3, 20, ('poppy', 'cornflower', 'oxeye_daisy')[idx], component='garden')
        b.put(x0 + 5, 3, 21, 'fern', component='garden')
        for fx in range(x0, x1 + 1):
            b.put(fx, 3, 22, 'birch_fence', component='garden')

    # Articulate outer west (x=3) and east (x=26) end-gable flanks so zero side elevation is blank!
    b.dressed_window('west', 3, 9, 11, 4, 5)
    b.dressed_window('west', 3, 14, 15, 4, 5)
    b.dressed_window('west', 3, 9, 11, 8, 9)
    b.dressed_window('west', 3, 14, 15, 8, 9)
    b.dressed_window('east', 26, 9, 11, 4, 5)
    b.dressed_window('east', 26, 14, 15, 4, 5)
    b.dressed_window('east', 26, 14, 16, 8, 9)
    b.put(2, 2, 5, 'polished_andesite')
    b.put(2, 3, 5, 'iron_bars')
    b.head(2, 4, 5, 'mailbox_orange', facing='north')
    return b.result()


def _medical_clinic() -> dict[str, Any]:
    b = VoxelBuilder('clinic')
    # Alder Urgent Care & Pharmacy (410 Alder Ave) at x=3..24, z=6..19 (leaving x=2,25 for flank relief!)
    b.box(3, 2, 6, 24, 2, 19, 'smooth_quartz', component='floor')
    b.box(10, 2, 5, 17, 2, 5, 'polished_andesite', component='apron')
    b.box(3, 3, 6, 24, 10, 19, 'white_concrete', component='wall')
    b.box(4, 3, 7, 23, 5, 18, 'air', component='interior')
    b.box(3, 6, 6, 24, 6, 19, 'cyan_terracotta', component='wall')
    b.box(4, 6, 7, 23, 6, 18, 'smooth_stone', component='floor')
    b.box(4, 7, 7, 23, 9, 18, 'air', component='interior')
    b.box(3, 10, 6, 24, 10, 19, 'smooth_quartz', component='roof')
    for y in range(3, 11):
        for cx in (3, 9, 18, 24):
            b.put(cx, y, 6, 'polished_deepslate', component='wall')
            b.put(cx, y, 19, 'polished_deepslate', component='wall')
        for cz in (6, 12, 19):
            b.put(3, y, cz, 'polished_deepslate', component='wall')
            b.put(24, y, cz, 'polished_deepslate', component='wall')

    # Step-free 1-block recessed double entrance portal at x=12..15, z=6
    b.recessed_north_portal(11, 16, 3, 6, door_xs=(13, 14), door_wood='birch', pier_mat='smooth_quartz', height=3, uplight=True)
    for x in range(11, 17):
        b.put(x, 6, 5, 'smooth_quartz_slab[type=bottom]', component='canopy')

    # Dressed institutional glazing + brise-soleil sills across ALL 4 elevations (north, south, west, east)
    for span in ((5, 8), (19, 22)):
        b.dressed_window('north', 6, span[0], span[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('north', 6, span[0], span[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('south', 19, span[0], span[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('south', 19, span[0], span[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('north', 6, 11, 16, 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('south', 19, 11, 16, 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('south', 19, 11, 16, 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    for wspan in ((8, 10), (14, 17)):
        b.dressed_window('west', 3, wspan[0], wspan[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('west', 3, wspan[0], wspan[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('east', 24, 8, 9, 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('east', 24, 15, 17, 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('east', 24, 15, 17, 8, 9, glass='light_blue_stained_glass', shutter_wood=None)

    # Ground floor: triage reception, waiting seats, pharmacy counter, AED & safety heads (zero bookshelf filler!)
    b.box(11, 3, 11, 16, 3, 12, 'smooth_quartz', component='furniture')
    b.head(12, 4, 11, 'computer_monitor', facing='north')
    b.head(14, 4, 11, 'telephone', facing='north')
    b.head(15, 4, 11, 'card_reader', facing='north')
    for x in (5, 6, 7, 8):
        b.put(x, 3, 9, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
    b.put(9, 3, 9, 'smooth_quartz', component='furniture')
    b.head(9, 4, 9, 'water_cooler', facing='south')
    # Dispensary counter
    b.box(5, 3, 15, 9, 3, 16, 'smooth_quartz', component='furniture')
    b.head(6, 4, 15, 'pos_terminal', facing='north')
    b.head(7, 4, 15, 'medicine_pillbottle', facing='north')
    b.head(8, 4, 15, 'rx_mortar', facing='north')
    # Accessible wall-mounted defibrillator, first_aid_kit & interior emergency_exit_light_caged
    b.box(18, 3, 11, 18, 5, 11, 'smooth_quartz', component='wall')
    b.head(18, 4, 10, 'defibrillator', facing='north', wall=True)
    b.head(18, 4, 12, 'first_aid_kit', facing='south', wall=True)
    b.head(13, 5, 8, 'emergency_exit_light_caged', facing='south', wall=True)

    # Wide 2-wide interior stair (x=21..22, z=10..13) with full headroom
    for i, z in enumerate((10, 11, 12, 13)):
        sy = 3 + i
        for sx in (21, 22):
            b.put(sx, sy, z, 'smooth_quartz_stairs[facing=south,half=bottom]', component='stairs')
            if sy > 3:
                b.box(sx, 3, z, sx, sy - 1, z, 'smooth_quartz', component='wall')
            for hy in (1, 2, 3):
                b.put(sx, sy + hy, z, 'air', component='stairs')

    # Upper consultation rooms & diagnostic heads
    b.box(10, 7, 7, 10, 9, 13, 'white_concrete', component='wall')
    b.box(17, 7, 7, 17, 9, 13, 'white_concrete', component='wall')
    for rx, rhead in ((6, 'heart_monitor'), (13, 'microscope'), (19, 'computer_monitor')):
        b.put(rx, 7, 10, 'smooth_quartz', component='furniture')
        b.head(rx, 8, 10, rhead, facing='south')
        b.put(rx, 7, 12, 'spruce_stairs[facing=north,half=bottom]', component='furniture')

    # Ceiling sea_lantern grid across both floors
    for x in (6, 13, 20):
        for z in (9, 16):
            b.put(x, 6, z, 'sea_lantern', component='lights')
            b.put(x, 10, z, 'sea_lantern', component='lights')

    # Rooftop parapet + two 2x2 quartz+rail HVAC exhaust units + solar + ac_unit (no featureless grey box!)
    for x in range(3, 25):
        b.put(x, 11, 6, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(x, 11, 19, 'stone_brick_slab[type=bottom]', component='roof')
    b.fan_unit_2x2(9, 11, 11)
    b.fan_unit_2x2(13, 11, 11)
    for sx in range(9, 16):
        for sz in (15, 16):
            b.put(sx, 11, sz, 'daylight_detector[inverted=true]', component='roof')
    b.head(16, 11, 12, 'ac_unit', facing='east', component='roof')

    # Signage: exterior address, clinic fascia, pharmacy hours, interior Built placard + frame & Max Occupancy
    b.address_plaque(10, 4, 5, 'north', 410, 'Alder Ave', '赤楊大道')
    b.sign(13, 6, 5, 'north', ['Alder Health', '赤楊急症診所', '--------------', 'Urgent Care'], wood='birch', component='facade')
    b.framed_sign(17, 4, 5, 'north', 'Pharmacy Rx', 'Daily 08-22h', wood='oak', component='facade')
    b.dedication_placard(4, 5, 8, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    b.occupancy_plaque(4, 5, 12, 'east', 48)
    return b.result()


def _grocery_supermarket() -> dict[str, Any]:
    b = VoxelBuilder('supermarket')
    # Flagship supermarket (176 Harbour Ave) at x=6..29, z=6..24 (protected z<5, x<4)
    b.box(5, 2, 5, 29, 2, 24, 'polished_andesite', component='floor')
    b.box(4, 2, 16, 5, 2, 21, 'polished_andesite', component='apron')
    b.box(7, 2, 7, 28, 2, 23, 'smooth_stone', component='floor')
    # Deepslate plinth + crisp white_concrete & smooth_quartz portal shell (y=3..8)
    b.box(6, 3, 6, 29, 8, 24, 'white_concrete', component='wall')
    b.box(7, 3, 7, 28, 7, 23, 'air', component='interior')
    for x in range(6, 30):
        b.put(x, 3, 6, 'deepslate_tiles', component='wall')
        b.put(x, 3, 24, 'deepslate_tiles', component='wall')
        b.put(x, 8, 6, 'smooth_quartz', component='roof')
        b.put(x, 9, 6, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(x, 9, 24, 'stone_brick_slab[type=bottom]', component='roof')
    for z in range(6, 25):
        b.put(6, 3, z, 'deepslate_tiles', component='wall')
        b.put(29, 3, z, 'deepslate_tiles', component='wall')
        b.put(6, 9, z, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(29, 9, z, 'stone_brick_slab[type=bottom]', component='roof')
    b.box(6, 8, 6, 29, 8, 24, 'smooth_stone', component='roof')
    # Signature red/blue architectural brand band above north portal
    for x in range(12, 20):
        b.put(x, 7, 6, 'red_concrete' if x < 16 else 'blue_concrete', component='facade')
        b.put(x, 7, 5, 'smooth_quartz_slab[type=bottom]', component='canopy')

    # 1-block recessed customer double portal on north (x=13..18, z=6) + flush sea_lantern uplights!
    b.recessed_north_portal(13, 18, 3, 6, door_xs=(15, 16), door_wood='dark_oak', pier_mat='smooth_quartz', height=4, uplight=True)
    # 1-block recessed west service/loading entrance off west lane (z=17..20, x=6, door at x=7, z=18)
    b.recessed_west_portal(17, 20, 3, 6, door_z=18, door_wood='iron', pier_mat='polished_deepslate', jamb_mat='gray_stained_glass', height=3)

    # Smoked glazing, acacia_trapdoor louvers & vertical end_rod fins on ALL 4 elevations (zero blank flanks!)
    for span in ((8, 11), (20, 27)):
        b.dressed_window('north', 6, span[0], span[1], 4, 6, glass='gray_stained_glass', shutter_wood='acacia')
    for x in (7, 12, 19, 28):
        b.box(x, 4, 5, x, 6, 5, 'end_rod[facing=up]', component='lights')
        b.put(x, 3, 5, 'polished_deepslate_wall', component='facade')
    b.dressed_window('west', 6, 8, 14, 4, 6, glass='gray_stained_glass', shutter_wood='acacia')
    b.dressed_window('west', 6, 21, 22, 4, 6, glass='gray_stained_glass', shutter_wood=None)
    b.dressed_window('east', 29, 8, 13, 4, 6, glass='gray_stained_glass', shutter_wood='acacia')
    b.dressed_window('east', 29, 17, 22, 4, 6, glass='gray_stained_glass', shutter_wood='acacia')
    b.dressed_window('south', 24, 9, 15, 4, 6, glass='light_blue_stained_glass', shutter_wood='acacia')
    b.dressed_window('south', 24, 19, 26, 4, 6, glass='light_blue_stained_glass', shutter_wood='acacia')

    # Slatted commercial sub-ceiling with end_rods + roof sea_lantern bays (zero dark_interior!)
    for x in (9, 14, 19, 24, 27):
        for z in (9, 13, 17, 21):
            b.put(x, 8, z, 'sea_lantern', component='lights')
    for z in (10, 15, 20):
        for x in range(7, 29):
            b.put(x, 7, z, 'end_rod[facing=east]', component='lights')

    # 3 conveyor POS checkout lanes (black_concrete belt + smooth_quartz pod + pos_terminal + card_reader)
    for cx in (9, 14, 19):
        b.put(cx, 3, 9, 'smooth_quartz', component='pos')
        b.put(cx, 3, 10, 'black_concrete', component='pos')
        b.put(cx, 3, 11, 'black_concrete', component='pos')
        b.head(cx, 4, 9, 'pos_terminal', facing='north')
        b.head(cx, 4, 10, 'card_reader', facing='west')
    b.put(22, 3, 9, 'smooth_quartz', component='pos')
    b.head(22, 4, 9, 'shopping_basket', facing='north')

    # 4 parallel stocked retail gondolas & wooden produce islands (quartz_stairs + spruce_trapdoor — ZERO bookshelf!)
    aisle_stock = [
        (10, ['apple_basket', 'orange_crate', 'produce_crate', 'cabbage_head', 'watermelon']),
        (15, ['rice_sack', 'cereal_box', 'spice_jars', 'jar_pickles', 'tea_tin']),
        (20, ['bread_loaf', 'croissant', 'pastry_box', 'cheesecake', 'bento_box']),
        (25, ['ramen_bowl', 'sushi_platter', 'boba_cup', 'jar_pickles', 'rice_cooker']),
    ]
    for gx, heads_list in aisle_stock:
        for idx_z, gz in enumerate(range(14, 19)):
            b.put(gx, 3, gz, 'smooth_quartz', component='gondola')
            b.put(gx + 1, 3, gz, 'quartz_stairs[facing=east,half=bottom]', component='gondola')
            b.put(gx + 1, 4, gz, 'spruce_trapdoor[facing=east,half=bottom,open=false]', component='gondola')
            b.head(gx, 4, gz, heads_list[idx_z], facing='west')

    # Backlit dairy cold wall & live seafood ice counter along z=22..23
    for x in range(9, 20, 2):
        b.put(x, 3, 22, 'smooth_quartz', component='gondola')
        b.head(x, 4, 22, 'milk_carton' if x % 4 == 1 else 'cheese_wheel', facing='north')
    for x in range(22, 27):
        b.put(x, 3, 22, 'water_cauldron[level=3]' if x in (23, 25) else 'smooth_quartz', component='gondola')
    b.head(22, 4, 22, 'salmon_fillet', facing='north')
    b.head(24, 4, 22, 'crab_ice', facing='north')
    b.head(26, 4, 22, 'salmon_fillet', facing='north')

    # Rooftop mechanical package: two 2x2 smooth_quartz + 4-rail circular exhaust fans + solar + ac_unit
    b.fan_unit_2x2(10, 9, 12)
    b.fan_unit_2x2(21, 9, 15)
    for sx in range(14, 19):
        for sz in (13, 14):
            b.put(sx, 9, sz, 'daylight_detector[inverted=true]', component='roof')
    b.head(13, 9, 12, 'ac_unit', facing='north', component='roof')

    # Street furniture: kerbside parking_meter on iron_bars, shopping-cart corral & bin
    b.put(9, 3, 5, 'iron_bars')
    b.head(9, 4, 5, 'parking_meter', facing='north')
    b.head(21, 3, 5, 'trash_bin', facing='north')
    b.head(18, 6, 5, 'security_camera', facing='north', wall=True)
    b.head(15, 6, 8, 'emergency_exit_light_caged', facing='south', wall=True)

    # Full commercial signage set (exterior address, brand fascia, hours, departments, interior Built + Occupancy)
    b.address_plaque(13, 4, 5, 'north', 176, 'Harbour Ave', '海港大道')
    b.sign(15, 7, 5, 'north', ['HANA MARKET', '韓亞市場', '-------------', 'Fresh Grocer'], wood='birch', component='facade')
    b.framed_sign(18, 4, 5, 'north', 'Daily 08-22h', 'Delivery West', wood='oak', component='facade')
    b.framed_sign(11, 6, 23, 'north', 'Dairy & Cold', '乳製品冷藏區', wood='birch', component='interior')
    b.framed_sign(24, 6, 23, 'north', 'Live Seafood', '鮮活水產部', wood='birch', component='interior')
    b.dedication_placard(7, 5, 9, 'east', 'Nov. 10,', '2026', tool='stone_axe')
    b.occupancy_plaque(7, 5, 12, 'east', 120)
    return b.result()


def _elevated_rail_station() -> dict[str, Any]:
    b = VoxelBuilder('station')
    # Harbour Bridge MRT Station integrating protected viaduct z=15..18, y=10..12 + piers x in (2,11,22,31)
    b.box(6, 2, 5, 27, 2, 13, 'polished_andesite', component='floor')
    b.box(7, 2, 7, 26, 2, 12, 'smooth_stone', component='floor')
    b.box(6, 3, 6, 27, 6, 13, 'light_gray_concrete', component='wall')
    b.box(7, 3, 7, 26, 5, 12, 'air', component='interior')
    for y in range(3, 7):
        for cx in (6, 12, 21, 27):
            b.put(cx, y, 6, 'polished_deepslate', component='wall')
            b.put(cx, y, 13, 'polished_deepslate', component='wall')
    b.box(6, 6, 6, 27, 6, 13, 'smooth_quartz', component='roof')

    # 1-block recessed commuter concourse portal at x=14..19, z=6
    b.recessed_north_portal(14, 19, 3, 6, door_xs=(16, 17), door_wood='iron', pier_mat='smooth_quartz', jamb_mat='gray_stained_glass', height=3, uplight=True)
    for x in range(13, 21):
        b.put(x, 6, 5, 'deepslate_tile_slab[type=bottom]', component='canopy')

    # Articulated concourse glazing + sills on all 4 sides
    b.dressed_window('north', 6, 8, 11, 4, 5, shutter_wood=None)
    b.dressed_window('north', 6, 22, 25, 4, 5, shutter_wood=None)
    b.dressed_window('west', 6, 8, 11, 4, 5, shutter_wood='acacia')
    b.dressed_window('east', 27, 8, 11, 4, 5, shutter_wood='acacia')
    b.dressed_window('south', 13, 8, 10, 4, 5, shutter_wood=None)
    b.dressed_window('south', 13, 13, 16, 4, 5, shutter_wood=None)

    # Fare gate array (ticket_validator), ticket booth (computer_monitor), tram_clock, bins & exit light
    for fx in (11, 14, 17, 20):
        b.put(fx, 3, 9, 'smooth_quartz', component='furniture')
        b.head(fx, 4, 9, 'ticket_validator', facing='north')
    b.box(8, 3, 9, 9, 3, 10, 'smooth_quartz', component='furniture')
    b.head(8, 4, 9, 'computer_monitor', facing='east')
    b.head(16, 5, 12, 'tram_clock', facing='north', wall=True)
    b.head(25, 3, 8, 'trash_bin', facing='west')
    b.head(25, 3, 9, 'recycling_bin', facing='west')
    b.head(16, 5, 8, 'emergency_exit_light_caged', facing='south', wall=True)

    # Elevated boarding platform flush alongside north track edge (x=4..29, z=11..14, y=10 -> feet y=11)
    b.box(4, 10, 11, 29, 10, 14, 'stone_bricks', component='floor')
    for x in range(4, 30):
        b.put(x, 10, 14, 'yellow_concrete', component='floor')
    for px in (5, 11, 16, 25, 28):
        b.box(px, 3, 14, px, 9, 14, 'polished_deepslate', component='wall')
        b.box(px, 11, 11, px, 14, 11, 'polished_deepslate', component='wall')

    # Headroom-safe 2-wide covered staircase from concourse (x=24, y=3, z=12..13) west up to platform (x=17, y=10 -> lands at x=16, y=10!)
    b.box(17, 6, 12, 25, 10, 13, 'air', component='stairs')
    b.box(25, 3, 12, 25, 5, 13, 'air', component='stairs')
    for i in range(8):
        sx = 24 - i
        sy = 3 + i
        for sz in (12, 13):
            if sy > 3:
                b.box(sx, 3, sz, sx, sy - 1, sz, 'stone_bricks', component='stairs')
            b.put(sx, sy, sz, 'stone_brick_stairs[facing=west,half=bottom]', component='stairs')
            for cy in range(sy + 1, 15):
                b.put(sx, cy, sz, 'air', component='stairs')

    # Grounded platform rear windscreen at z=11 with architectural windows & sills so upper wall is articulated!
    b.box(4, 11, 11, 29, 11, 11, 'stone_bricks', component='wall')
    b.box(4, 14, 11, 29, 14, 11, 'polished_deepslate', component='roof')
    for x in range(6, 28):
        if x not in (11, 16, 25):
            b.box(x, 12, 11, x, 13, 11, 'gray_stained_glass_pane', component='window')
            b.put(x, 11, 10, 'smooth_quartz_stairs[facing=south,half=top]', component='relief')
    for z in (12, 13):
        for ex in (4, 29):
            b.box(ex, 11, z, ex, 14, z, 'polished_deepslate', component='wall')
            b.box(ex, 12, z, ex, 13, z, 'gray_stained_glass', component='window')
    b.box(4, 15, 11, 29, 15, 14, 'polished_deepslate', component='roof')
    b.box(4, 16, 11, 29, 16, 14, 'smooth_quartz_slab[type=bottom]', component='roof')

    # Platform benches, lighting & full station signage set
    b.bench(7, 12, 9, 12, 11, 'south', 'spruce')
    b.bench(12, 12, 14, 12, 11, 'south', 'spruce')
    for x in (8, 13, 18, 23):
        b.put(x, 6, 9, 'sea_lantern', component='lights')
        b.put(x, 14, 12, 'lantern[hanging=true]', component='lights')
        b.put(x, 14, 13, 'lantern[hanging=true]', component='lights')

    b.address_plaque(13, 4, 5, 'north', 300, 'Viaduct Way', '高架橋道')
    b.sign(16, 6, 5, 'north', ['| MRT 海港站 |', '-------------', 'Harbour Br.', 'Line 2 · 東西線'], wood='birch', component='facade')
    b.framed_sign(11, 13, 12, 'south', 'Platform 1 ->', 'Every 4 min', wood='oak', component='sign')
    b.dedication_placard(7, 5, 8, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    b.occupancy_plaque(7, 5, 11, 'east', 180)
    return b.result()


def _midrise_apartments() -> dict[str, Any]:
    b = VoxelBuilder('midrise')
    # Pacific & Redmond Flats (245 Pacific Ave): 5-storey mixed-use at x=4..25, z=6..20, roof y=23, bulkhead y=24..26
    floor_ys = [2, 6, 11, 15, 19]
    roof_y = 23
    b.box(4, 2, 6, 25, 2, 20, 'polished_andesite', component='floor')
    b.box(6, 2, 5, 11, 2, 5, 'polished_andesite', component='apron')
    b.box(17, 2, 5, 22, 2, 5, 'polished_andesite', component='apron')

    # Shell with limestone frame + warm brick spandrels
    b.box(4, 3, 6, 25, roof_y, 20, 'bricks', component='wall')
    for idx, fy in enumerate(floor_ys):
        top = roof_y if idx == len(floor_ys) - 1 else floor_ys[idx + 1]
        b.box(5, fy + 1, 7, 24, top - 1, 19, 'air', component='interior')
        if fy > 2:
            b.box(4, fy, 6, 25, fy, 20, 'smooth_quartz', component='floor')
            b.box(5, fy, 7, 24, fy, 19, 'oak_planks', component='floor')
    for y in range(3, roof_y + 1):
        for cx in (4, 10, 15, 20, 25):
            b.put(cx, y, 6, 'polished_deepslate' if y <= 6 else 'smooth_quartz', component='wall')
            b.put(cx, y, 20, 'polished_deepslate' if y <= 6 else 'smooth_quartz', component='wall')
        for cz in (6, 13, 20):
            b.put(4, y, cz, 'polished_deepslate' if y <= 6 else 'smooth_quartz', component='wall')
            b.put(25, y, cz, 'polished_deepslate' if y <= 6 else 'smooth_quartz', component='wall')

    # Ground floor split: west Kettle & Fern Cafe (x=5..14) + east Residential Lobby (x=15..24)
    b.box(15, 3, 7, 15, 5, 19, 'white_concrete', component='wall')
    b.recessed_north_portal(7, 9, 3, 6, door_xs=8, door_wood='spruce', pier_mat='polished_deepslate', height=3, uplight=True)
    b.recessed_north_portal(18, 20, 3, 6, door_xs=19, door_wood='dark_oak', pier_mat='polished_deepslate', height=3, uplight=True)

    # Ground cafe fit-out (zero ground-floor bookshelf!) + lobby props
    b.box(6, 3, 15, 11, 3, 16, 'smooth_quartz', component='furniture')
    b.head(6, 4, 15, 'espresso_machine', facing='north')
    b.head(7, 4, 15, 'coffee_maker', facing='north')
    b.head(8, 4, 15, 'croissant', facing='north')
    b.head(9, 4, 15, 'pos_terminal', facing='north')
    b.head(10, 4, 15, 'card_reader', facing='north')
    b.put(12, 3, 10, 'spruce_stairs[facing=south,half=bottom]', component='furniture')
    b.put(12, 3, 11, 'oak_slab[type=top]', component='furniture')
    b.put(12, 3, 12, 'spruce_stairs[facing=north,half=bottom]', component='furniture')
    b.head(12, 4, 11, 'latte_cup', facing='west')
    b.put(23, 2, 5, 'polished_andesite', component='apron')
    b.put(23, 3, 5, 'iron_bars')
    b.head(23, 4, 5, 'mailbox_orange', facing='north')
    b.head(19, 5, 8, 'emergency_exit_light_caged', facing='south', wall=True)
    b.head(16, 5, 8, 'security_camera', facing='east', wall=True)

    # Headroom-safe continuous switchback stair core in x=21..23, z=11..17 (y=2 -> 6 -> 11 -> 15 -> 19)
    b.box(21, 6, 11, 23, 22, 17, 'air', component='stairs')
    for idx in range(len(floor_ys) - 1):
        fy = floor_ys[idx]
        ny = floor_ys[idx + 1]
        steps = ny - fy
        go_south = (idx % 2 == 0)
        sx = 23 if go_south else 21
        # Landing slabs at both ends (z=10..11 and z=17..18)
        if fy > 2:
            for lx in range(21, 24):
                b.put(lx, fy, 11, 'smooth_quartz', component='stairs')
                b.put(lx, fy, 17, 'smooth_quartz', component='stairs')
        for s in range(steps):
            sz = (12 + s) if go_south else (16 - s)
            sy = fy + 1 + s
            facing = 'south' if go_south else 'north'
            b.put(sx, sy, sz, f'stone_brick_stairs[facing={facing},half=bottom]', component='stairs')
            for cy in range(sy + 1, min(roof_y, sy + 4)):
                b.put(sx, cy, sz, 'air', component='stairs')
        # Ensure top landing block at step exit
        end_z = (12 + steps) if go_south else (16 - steps)
        for lx in range(21, 24):
            b.put(lx, ny, end_z, 'smooth_quartz', component='stairs')

    # Fenestration, walkable guarded balconies & side/rear relief across ALL 4 elevations!
    for idx, fy in enumerate(floor_ys):
        yh0, yh1 = fy + 2, fy + 3
        if fy == 2:
            b.dressed_window('north', 6, 5, 6, 4, 5, shutter_wood='spruce')
            b.dressed_window('north', 6, 11, 14, 4, 5, shutter_wood='spruce')
            b.dressed_window('north', 6, 16, 17, 4, 5, shutter_wood=None)
            b.dressed_window('north', 6, 21, 24, 4, 5, shutter_wood='spruce')
        else:
            b.dressed_window('north', 6, 6, 8, yh0, yh1, shutter_wood='spruce')
            b.dressed_window('north', 6, 16, 18, yh0, yh1, shutter_wood='spruce')
            b.dressed_window('north', 6, 21, 23, yh0, yh1, shutter_wood=None)
            # Projecting guarded north balcony at x=11..14, z=5 + planted azalea box
            b.box(11, fy, 5, 14, fy, 5, 'smooth_quartz', component='balcony')
            for bx in range(11, 15):
                b.put(bx, fy + 1, 5, 'azalea_leaves[persistent=true]' if bx == 11 else 'gray_stained_glass_pane', component='balcony')
            b.door(12, fy + 1, 6, 'north', 'spruce')
            b.box(13, fy + 1, 6, 13, fy + 2, 6, 'gray_stained_glass', component='window')
        # South, West (x=4) and East (x=25) windows + projecting sills/balconies on every floor!
        b.dressed_window('south', 20, 6, 8, yh0, yh1, shutter_wood='spruce')
        b.dressed_window('south', 20, 12, 14, yh0, yh1, shutter_wood='spruce')
        b.dressed_window('south', 20, 17, 19, yh0, yh1, shutter_wood=None)
        b.dressed_window('west', 4, 8, 11, yh0, yh1, shutter_wood='spruce')
        b.dressed_window('west', 4, 15, 18, yh0, yh1, shutter_wood='spruce')
        b.dressed_window('east', 25, 8, 10, yh0, yh1, shutter_wood='spruce')
        if fy >= 6 and idx in (1, 2, 3):
            b.bed(7, fy + 1, 16, 'south', ('red', 'blue', 'yellow')[idx - 1])
            b.put(6, fy + 1, 18, 'smooth_quartz', component='furniture')
            b.head(6, fy + 2, 18, ('microwave', 'kettle', 'plant_pot')[idx - 1], facing='north')
        for lx in (8, 13, 18):
            for lz in (9, 17):
                b.put(lx, fy + 3, lz, 'sea_lantern', component='lights')
        b.put(22, fy + 3, 10, 'sea_lantern', component='lights')

    # Roof parapet + louvered stair bulkhead (y=24..26 >= 23) + 2x2 quartz+rail fan + solar + ac_unit
    b.box(4, roof_y, 6, 25, roof_y, 20, 'smooth_stone', component='roof')
    for x in range(4, 26):
        b.put(x, roof_y + 1, 6, 'stone_brick_slab[type=bottom]', component='roof')
        b.put(x, roof_y + 1, 20, 'stone_brick_slab[type=bottom]', component='roof')
    b.box(19, roof_y + 1, 11, 24, roof_y + 3, 17, 'smooth_quartz', component='roof')
    for z in (12, 13, 15):
        b.put(19, roof_y + 2, z, 'iron_trapdoor[facing=west,half=bottom,open=true]', component='roof')
    b.box(19, roof_y + 4, 11, 24, roof_y + 4, 17, 'deepslate_tile_slab[type=bottom]', component='roof')
    b.fan_unit_2x2(8, roof_y + 1, 12)
    for sx in range(12, 17):
        for sz in (12, 13):
            b.put(sx, roof_y + 1, sz, 'daylight_detector[inverted=true]', component='roof')
    b.head(11, roof_y + 1, 12, 'ac_unit', facing='north', component='roof')

    # Signage: exterior address, cafe fascia, residential plaque, interior Built + Max Occupancy
    b.address_plaque(17, 4, 5, 'north', 245, 'Pacific Ave', '太平洋大道')
    b.sign(8, 6, 5, 'north', ['Kettle & Fern', '壺蕨咖啡館', '-------------', 'Espresso Bar'], wood='spruce', component='facade')
    b.framed_sign(20, 4, 5, 'north', 'Redmond Flats', 'Residences', wood='birch', component='facade')
    b.dedication_placard(16, 5, 10, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    b.occupancy_plaque(16, 5, 13, 'east', 96)
    return b.result()


def _civic_office_tower() -> dict[str, Any]:
    b = VoxelBuilder('tower')
    # Pacific Finance Centre (100 Exchange Pl): podium x=4..25,z=6..22 (y=2..10), shaft x=7..22,z=8..20 (y=10..30), crown y=31..36
    b.box(4, 2, 6, 25, 2, 22, 'polished_andesite', component='floor')
    b.box(11, 2, 5, 18, 2, 5, 'polished_andesite', component='apron')
    b.box(4, 3, 6, 25, 10, 22, 'smooth_quartz', component='wall')
    b.box(5, 3, 7, 24, 5, 21, 'air', component='interior')
    b.box(5, 6, 7, 24, 6, 21, 'smooth_stone', component='floor')
    b.box(5, 7, 7, 24, 9, 21, 'air', component='interior')
    b.box(4, 10, 6, 25, 10, 22, 'polished_deepslate', component='roof')
    for y in range(3, 11):
        for cx in (4, 9, 12, 17, 20, 25):
            b.put(cx, y, 6, 'polished_deepslate', component='wall')
            b.put(cx, y, 22, 'polished_deepslate', component='wall')
        for cz in (6, 11, 17, 22):
            b.put(4, y, cz, 'polished_deepslate', component='wall')
            b.put(25, y, cz, 'polished_deepslate', component='wall')

    # Grand 1-block recessed north civic portal (x=12..17, z=6)
    b.recessed_north_portal(12, 17, 3, 6, door_xs=(14, 15), door_wood='dark_oak', pier_mat='polished_deepslate', height=3, uplight=True)
    for x in range(11, 19):
        b.put(x, 6, 5, 'smooth_quartz_slab[type=bottom]', component='canopy')

    # Articulate ALL 4 podium elevations with smoked/tinted curtain bays & projecting sills
    for pspan in ((6, 8), (10, 11), (18, 19), (21, 23)):
        b.dressed_window('north', 6, pspan[0], pspan[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('north', 6, pspan[0], pspan[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('south', 22, pspan[0], pspan[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('south', 22, pspan[0], pspan[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('north', 6, 13, 16, 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('south', 22, 13, 16, 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
    b.dressed_window('south', 22, 13, 16, 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
    for zspan in ((8, 10), (13, 15), (18, 20)):
        b.dressed_window('west', 4, zspan[0], zspan[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('west', 4, zspan[0], zspan[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('east', 25, zspan[0], zspan[1], 4, 5, glass='light_blue_stained_glass', shutter_wood=None)
        b.dressed_window('east', 25, zspan[0], zspan[1], 8, 9, glass='light_blue_stained_glass', shutter_wood=None)

    # Stepped 6-storey curtain-wall tower shaft (x=7..22, z=8..20, y=10..30) with mullion & spandrel fin relief on all 4 faces
    shaft_floors = [10, 14, 18, 22, 26]
    b.box(7, 11, 8, 22, 30, 20, 'polished_deepslate', component='wall')
    for fy in shaft_floors:
        b.box(8, fy + 1, 9, 21, fy + 3, 19, 'air', component='interior')
        b.box(8, fy, 9, 21, fy, 19, 'smooth_stone', component='floor')
        for x in range(8, 22):
            b.put(x, fy, 8, 'smooth_quartz', component='facade')
            b.put(x, fy, 20, 'smooth_quartz', component='facade')
            b.put(x, fy, 7, 'smooth_quartz_slab[type=top]', component='relief')
            b.put(x, fy, 21, 'smooth_quartz_slab[type=top]', component='relief')
            if x % 3 != 1:
                b.box(x, fy + 1, 8, x, fy + 3, 8, 'light_blue_stained_glass', component='window')
                b.box(x, fy + 1, 20, x, fy + 3, 20, 'light_blue_stained_glass', component='window')
        for z in range(9, 20):
            b.put(7, fy, z, 'smooth_quartz', component='facade')
            b.put(22, fy, z, 'smooth_quartz', component='facade')
            b.put(6, fy, z, 'smooth_quartz_slab[type=top]', component='relief')
            b.put(23, fy, z, 'smooth_quartz_slab[type=top]', component='relief')
            if z % 3 != 0:
                b.box(7, fy + 1, z, 7, fy + 3, z, 'light_blue_stained_glass', component='window')
                b.box(22, fy + 1, z, 22, fy + 3, z, 'light_blue_stained_glass', component='window')
    b.box(7, 30, 8, 22, 30, 20, 'smooth_quartz', component='roof')

    # Headroom-safe continuous switchback stair core (x=16..18, z=11..17, y=2..26 -> covers tiers 6, 14, 22!)
    all_floors = [2, 6, 10, 14, 18, 22, 26]
    b.box(16, 6, 11, 18, 29, 17, 'air', component='stairs')
    for idx in range(len(all_floors) - 1):
        fy = all_floors[idx]
        ny = all_floors[idx + 1]
        steps = ny - fy
        go_south = (idx % 2 == 0)
        sx = 18 if go_south else 16
        if fy > 2:
            for lx in range(16, 19):
                b.put(lx, fy, 11, 'smooth_quartz', component='stairs')
                b.put(lx, fy, 17, 'smooth_quartz', component='stairs')
        for s in range(steps):
            sz = (12 + s) if go_south else (15 - s)
            sy = fy + 1 + s
            facing = 'south' if go_south else 'north'
            b.put(sx, sy, sz, f'stone_brick_stairs[facing={facing},half=bottom]', component='stairs')
            for cy in range(sy + 1, min(30, sy + 4)):
                b.put(sx, cy, sz, 'air', component='stairs')
        end_z = (12 + steps) if go_south else (15 - steps)
        for lx in range(16, 19):
            b.put(lx, ny, end_z, 'smooth_quartz', component='stairs')

    # Lobby reception & furnished upper sky-lobby/office floors (12 custom heads, zero bookshelf filler!)
    b.box(11, 3, 10, 15, 3, 10, 'smooth_quartz', component='furniture')
    b.head(11, 4, 10, 'computer_monitor', facing='north')
    b.head(13, 4, 10, 'computer_monitor', facing='north')
    b.head(14, 4, 10, 'telephone', facing='north')
    b.head(15, 4, 10, 'card_reader', facing='north')
    b.put(9, 3, 10, 'smooth_quartz', component='furniture')
    b.head(9, 4, 10, 'card_reader', facing='north')
    b.put(20, 3, 10, 'scaffolding', component='furniture')
    b.head(20, 4, 10, 'plant_pot', facing='north')
    b.head(14, 5, 8, 'emergency_exit_light_caged', facing='south', wall=True)
    b.head(11, 5, 7, 'security_camera', facing='south', wall=True)
    for fy, ohead in ((6, 'laptop'), (14, 'printer'), (22, 'water_cooler'), (26, 'desk_lamp')):
        b.put(10, fy + 1, 11, 'smooth_quartz', component='furniture')
        b.head(10, fy + 2, 11, ohead, facing='south')

    # Lighting across podium & every shaft floor
    for fy in (2, 6):
        for lx in (8, 14, 21):
            for lz in (9, 19):
                b.put(lx, fy + 3, lz, 'sea_lantern', component='lights')
    for fy in shaft_floors:
        for lx in (10, 14, 19):
            for lz in (10, 18):
                b.put(lx, fy + 3, lz, 'sea_lantern', component='lights')

    # Articulated louvered mechanical crown (y=31..34) + 2x2 fan unit + ac_unit + aircraft warning lights at y=36 (>=30)
    b.box(10, 31, 11, 19, 34, 17, 'polished_deepslate', component='roof')
    for x in range(12, 18):
        b.put(x, 32, 11, 'iron_trapdoor[facing=north,half=bottom,open=true]', component='roof')
        b.put(x, 33, 11, 'iron_bars', component='roof')
        b.put(x, 32, 17, 'iron_trapdoor[facing=south,half=bottom,open=true]', component='roof')
    b.box(10, 35, 11, 19, 35, 17, 'smooth_quartz_slab[type=bottom]', component='roof')
    b.fan_unit_2x2(13, 35, 13)
    b.head(16, 35, 13, 'ac_unit', facing='east', component='roof')
    for cx, cz in ((10, 11), (19, 11), (10, 17), (19, 17)):
        b.put(cx, 35, cz, 'polished_deepslate', component='roof')
        b.put(cx, 36, cz, 'redstone_torch', component='lights')

    # Signage: exterior address, tower nameplate, directory hours, interior Built placard + frame & Max Occupancy
    b.address_plaque(11, 4, 5, 'north', 100, 'Exchange Pl', '交易廣場')
    b.sign(14, 6, 5, 'north', ['Pacific Centre', '太平洋金融中心', '--------------', 'Civic & Trade'], wood='birch', component='facade')
    b.framed_sign(18, 4, 5, 'north', 'Lobby Mon-Fri', '07:00 - 20:00', wood='oak', component='facade')
    b.dedication_placard(5, 5, 9, 'east', 'Nov. 14,', '2026', tool='stone_axe')
    b.occupancy_plaque(5, 5, 13, 'east', 240)
    return b.result()


def _chunk_cliff_scar() -> dict[str, Any]:
    b = VoxelBuilder('terraform')
    b.box(13, 12, 14, 15, 13, 16, 'air')
    for x in range(8, 24):
        for z in range(6, 22):
            top = 5 + (z - 6) // 6
            for y in range(1, top + 1):
                if y == top:
                    if 8 <= z <= 10:
                        mat = 'gray_concrete'
                    elif z in (7, 11):
                        mat = 'smooth_stone'
                    else:
                        mat = 'grass_block'
                elif y == top - 1:
                    mat = 'dirt'
                else:
                    mat = 'stone'
                b.put(x, y, z, mat)
    b.conifer(12, 5 + (15 - 6) // 6 + 1, 15, height=9, seed=4)
    b.broadleaf(19, 5 + (17 - 6) // 6 + 1, 17, height=7, seed=8)
    for x, z, fl in (
        (10, 13, 'poppy'), (14, 14, 'dandelion'), (16, 13, 'cornflower'),
        (21, 14, 'oxeye_daisy'), (11, 19, 'fern'), (15, 19, 'azalea'),
    ):
        top = 5 + (z - 6) // 6
        b.put(x, top + 1, z, fl)
    return b.result()


def _chunk_river_seam() -> dict[str, Any]:
    b = VoxelBuilder('terraform')
    b.box(8, 1, 5, 23, 14, 20, 'air')
    for x in range(8, 24):
        for z in range(5, 21):
            if 10 <= z <= 13:
                b.put(x, 1, z, 'gravel')
                b.put(x, 2, z, 'water')
                b.put(x, 3, z, 'water')
            elif z in (9, 14):
                b.put(x, 1, z, 'stone')
                b.put(x, 2, z, 'stone')
                b.put(x, 3, z, 'sand')
            else:
                b.put(x, 1, z, 'stone')
                b.put(x, 2, z, 'stone')
                b.put(x, 3, z, 'dirt')
                b.put(x, 4, z, 'grass_block')
    for z in range(5, 9):
        for x in (15, 16):
            b.put(x, 4, z, 'polished_andesite', component='path')
    for z in range(15, 21):
        for x in (15, 16):
            b.put(x, 4, z, 'polished_andesite', component='path')
    for x in (15, 16):
        b.put(x, 4, 9, 'stone_bricks', component='bridge')
        b.put(x, 4, 14, 'stone_bricks', component='bridge')
        b.put(x, 5, 9, 'spruce_stairs[facing=south,half=bottom]', component='bridge')
        b.put(x, 5, 14, 'spruce_stairs[facing=north,half=bottom]', component='bridge')
    b.box(14, 5, 10, 17, 5, 13, 'spruce_planks', component='bridge')
    for x in (14, 17):
        b.box(x, 4, 9, x, 5, 9, 'stone_bricks', component='bridge')
        b.box(x, 4, 14, x, 5, 14, 'stone_bricks', component='bridge')
        for z in range(9, 15):
            b.put(x, 6, z, 'stone_brick_wall', component='bridge')
        b.put(x, 7, 10, 'lantern', component='lights')
        b.put(x, 7, 13, 'lantern', component='lights')
    b.broadleaf(12, 5, 16, height=7, seed=9)
    b.conifer(19, 5, 16, height=8, seed=6)
    for x, z, fl in ((10, 7, 'poppy'), (12, 7, 'dandelion'), (19, 7, 'cornflower'), (19, 16, 'fern')):
        b.put(x, 5, z, fl)
    return b.result()


def _coastal_seawall() -> dict[str, Any]:
    b = VoxelBuilder('seawall')
    b.box(0, 1, 5, 27, 12, 15, 'air')
    for x in range(28):
        for z in range(5, 16):
            if z == 5:
                top, surf = 7, 'grass_block'
            elif z in (6, 7):
                top, surf = 6, 'grass_block'
            elif z in (8, 9, 10, 11):
                top, surf = 5, 'grass_block'
            elif z == 12:
                top, surf = 5, 'stone_bricks'
            else:
                top, surf = 4, 'polished_andesite' if z in (13, 14) else 'stone_bricks'
            for y in range(1, top + 1):
                if y == top:
                    mat = surf
                elif surf == 'grass_block' and y == top - 1:
                    mat = 'dirt'
                elif z >= 12:
                    mat = 'stone_bricks'
                else:
                    mat = 'stone'
                b.put(x, y, z, mat)
    for x in range(12, 16):
        b.put(x, 7, 5, 'polished_andesite', component='steps')
        b.put(x, 7, 6, 'air')
        b.put(x, 6, 6, 'stone_brick_stairs[facing=north,half=bottom]', component='steps')
        b.put(x, 6, 7, 'polished_andesite', component='steps')
        b.put(x, 6, 8, 'air')
        b.put(x, 5, 8, 'stone_brick_stairs[facing=north,half=bottom]', component='steps')
        for z in (9, 10, 11):
            b.put(x, 5, z, 'polished_andesite', component='steps')
        b.put(x, 5, 12, 'stone_brick_stairs[facing=north,half=bottom]', component='steps')
    for x in range(28):
        b.put(x, 5, 15, 'stone_bricks' if x % 6 == 2 else 'stone_brick_wall', component='guard')
        if x % 6 == 2:
            b.put(x, 6, 15, 'lantern', component='lights')
    b.bench(6, 13, 8, 13, 5, 'south', 'spruce')
    b.bench(19, 13, 21, 13, 5, 'south', 'spruce')
    b.conifer(4, 6, 9, height=9, seed=12)
    b.conifer(23, 6, 9, height=9, seed=13)
    b.bcparks_post_sign(10, 5, 13, 'north', 'Harbour Quay')
    for x, z, fl in ((7, 8, 'fern'), (9, 9, 'poppy'), (18, 9, 'dandelion'), (20, 8, 'cornflower')):
        b.put(x, 6, z, fl)
    return b.result()


def _quarry_reclamation() -> dict[str, Any]:
    b = VoxelBuilder('quarry')
    for x in range(4, 24):
        for z in range(5, 23):
            in_pond = 10 <= x <= 17 and 12 <= z <= 17 and not (x in (10, 17) and z in (12, 17))
            outer_rim = x in (4, 5, 22, 23) or z in (5, 21, 22)
            if in_pond:
                b.put(x, 1, z, 'stone')
                b.put(x, 2, z, 'gravel')
                b.put(x, 3, z, 'water')
            elif outer_rim:
                top = 5
                for y in range(1, top):
                    b.put(x, y, z, 'stone' if y < top - 1 else 'dirt')
                b.put(x, top, z, 'grass_block')
            else:
                near_pond = 9 <= x <= 18 and 11 <= z <= 18
                top = 3 if near_pond else 4
                for y in range(1, top):
                    b.put(x, y, z, 'stone' if y < top - 1 else 'dirt')
                b.put(x, top, z, 'moss_block' if near_pond else 'grass_block')
    for x in (13, 14):
        b.put(x, 5, 5, 'polished_andesite', component='steps')
        b.put(x, 5, 6, 'air')
        b.put(x, 4, 6, 'stone_brick_stairs[facing=north,half=bottom]', component='steps')
        for z in (7, 8, 9):
            b.put(x, 4, z, 'polished_andesite', component='steps')
        b.put(x, 4, 10, 'stone_brick_stairs[facing=north,half=bottom]', component='steps')
    for x in range(9, 19):
        b.put(x, 3, 11, 'polished_andesite', component='path')
        b.put(x, 3, 18, 'polished_andesite', component='path')
    for z in range(11, 19):
        b.put(9, 3, z, 'polished_andesite', component='path')
        b.put(18, 3, z, 'polished_andesite', component='path')
    b.conifer(7, 5, 9, height=9, seed=15)
    b.broadleaf(19, 5, 10, height=7, seed=16)
    b.bench(10, 10, 11, 10, 4, 'south', 'spruce')
    b.bench(16, 19, 17, 19, 4, 'north', 'spruce')
    b.bcparks_post_sign(11, 5, 6, 'north', 'Quarry Pond')
    for lx, lz in ((9, 11), (18, 11), (9, 18), (18, 18)):
        b.put(lx, 4, lz, 'stone_brick_wall', component='lights')
        b.put(lx, 5, lz, 'lantern', component='lights')
    for x, z, fl in (
        (7, 14, 'poppy'), (7, 16, 'cornflower'), (8, 15, 'fern'),
        (20, 15, 'dandelion'), (20, 17, 'oxeye_daisy'), (12, 20, 'azalea'),
    ):
        b.put(x, 5, z, fl)
    return b.result()


BUILDING_AND_TERRA_BUILDERS: dict[str, Any] = {
    'transit-shelter': _transit_shelter,
    'pocket-park': _pocket_park,
    'sloped-cafe': _sloped_cafe,
    'shop-renovation': _shop_renovation,
    'small-house': _small_house,
    'utility-substation': _utility_substation,
    'canal-crossing': _canal_crossing,
    'corner-shophouse': _corner_shophouse,
    'party-wall-infill': _party_wall_infill,
    'hillside-pavilion': _hillside_pavilion,
    'rowhouse-terrace': _rowhouse_terrace,
    'medical-clinic': _medical_clinic,
    'grocery-supermarket': _grocery_supermarket,
    'elevated-rail-station': _elevated_rail_station,
    'midrise-apartments': _midrise_apartments,
    'civic-office-tower': _civic_office_tower,
    'chunk-cliff-scar': _chunk_cliff_scar,
    'chunk-river-seam': _chunk_river_seam,
    'coastal-seawall': _coastal_seawall,
    'quarry-reclamation': _quarry_reclamation,
}
