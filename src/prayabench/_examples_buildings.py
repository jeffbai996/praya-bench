"""Deterministic acceptable reference examples for the 16 buildings and 4 terraforming tasks."""
from __future__ import annotations

from typing import Any

from . import demo
from ._examples_common import PROVENANCE, VoxelBuilder
from .tasks import ground_at


def _transit_shelter() -> dict[str, Any]:
    b = VoxelBuilder()
    # Level paved pad connected to sidewalk z=4
    b.box(3, 2, 5, 14, 2, 10, 'smooth_stone')
    # Low stone-brick base curb and structural columns
    b.box(3, 3, 10, 14, 3, 10, 'stone_bricks')
    for x in (3, 7, 11, 14):
        b.box(x, 3, 10, x, 5, 10, 'gray_concrete')
    b.box(3, 3, 7, 3, 5, 9, 'gray_concrete')
    # Windscreen glazing along back & west end
    for x in (4, 5, 6, 8, 9, 10, 12, 13):
        b.box(x, 4, 10, x, 5, 10, 'gray_stained_glass_pane')
    for z in (8, 9):
        b.box(3, 4, z, 3, 5, z, 'gray_stained_glass_pane')
    # Cantilevered canopy roof
    b.box(3, 6, 6, 14, 6, 10, 'gray_concrete')
    b.box(2, 6, 5, 15, 6, 5, 'deepslate_tile_slab[type=top]')
    b.box(2, 6, 11, 15, 6, 11, 'deepslate_tile_slab[type=top]')
    b.box(3, 7, 6, 14, 7, 10, 'smooth_stone_slab[type=bottom]')
    # Passenger bench seating (facing north road)
    for x in range(5, 10):
        b.put(x, 3, 9, 'spruce_stairs[facing=north,half=bottom]')
    # Route/timetable sign on solid column + ticket_validator + trash_bin
    b.sign(3, 4, 6, 'north', ['Route 14', 'North Pier', 'Every 6m'])
    b.put(12, 3, 8, 'polished_andesite')
    b.head(12, 4, 8, 'ticket_validator')
    b.head(14, 3, 8, 'trash_bin')
    # Canopy lighting
    for x in (5, 9, 13):
        b.put(x, 5, 7, 'lantern[hanging=true]')
    # Low planted landscape bed behind shelter
    for x in range(4, 14):
        b.put(x, 2, 11, 'grass_block')
        b.put(x, 2, 12, 'grass_block')
    for x, fl in ((4, 'poppy'), (6, 'cornflower'), (8, 'fern'), (10, 'oxeye_daisy'), (12, 'dandelion')):
        b.put(x, 3, 12, fl)
    return b.result()


def _pocket_park() -> dict[str, Any]:
    b = VoxelBuilder()
    # Continuous curved stone walkway from sidewalk z=4 into park
    for z in range(5, 18):
        cx = 11 if z < 9 else (12 if z < 14 else 11)
        for x in range(cx - 1, cx + 2):
            b.put(x, 2, z, 'smooth_stone')
    for x in range(7, 17):
        for z in (11, 12):
            b.put(x, 2, z, 'smooth_stone')
    # Central stone planter feature
    b.box(10, 2, 11, 13, 2, 12, 'stone_bricks')
    b.box(11, 3, 11, 12, 3, 12, 'moss_block')
    b.put(11, 4, 11, 'flowering_azalea')
    b.put(12, 4, 12, 'cornflower')
    # Two park benches along the plaza
    for x in (7, 8):
        b.put(x, 3, 10, 'spruce_stairs[facing=south,half=bottom]')
    for x in (15, 16):
        b.put(x, 3, 13, 'spruce_stairs[facing=north,half=bottom]')
    # Low stone plinth with mounted park sign + lantern piers
    b.box(8, 3, 6, 8, 4, 6, 'stone_bricks')
    b.put(8, 5, 6, 'lantern')
    b.sign(8, 4, 5, 'north', ['Pocket Park', 'Open Daily'])
    b.put(15, 3, 6, 'stone_brick_wall')
    b.put(15, 4, 6, 'lantern')
    b.put(11, 3, 17, 'stone_brick_wall')
    b.put(11, 4, 17, 'lantern')
    # Mailbox on slender iron bar near street
    b.put(14, 3, 5, 'iron_bars')
    b.head(14, 4, 5, 'mailbox_orange')
    # Believable conifer and broadleaf trees
    b.conifer(5, 3, 16, height=9)
    b.broadleaf(18, 3, 15, height=7)
    # Planted beds & flora
    for x, z, fl in (
        (5, 7, 'poppy'), (6, 8, 'dandelion'), (7, 7, 'cornflower'),
        (17, 7, 'oxeye_daisy'), (18, 8, 'poppy'), (19, 7, 'red_tulip'),
        (6, 13, 'fern'), (17, 11, 'azalea'),
    ):
        b.put(x, 3, z, fl)
    return b.result()


def _sloped_cafe() -> dict[str, Any]:
    data = demo.example(True)
    # Ensure interior stays warmly lit under the pitched roof
    cells = {tuple(c[:3]): c for c in data['cells']}
    for x in (6, 10):
        cells[x, 8, 12] = [x, 8, 12, 'lantern[hanging=true]', None, 'reference', None]
    return {'cells': list(cells.values()), 'provenance': PROVENANCE}


def _shop_renovation() -> dict[str, Any]:
    b = VoxelBuilder()
    # Fit out interior x=4..14, z=8..16, y=3..7 without touching protected shell or Built 2012 placard at (4,5,8)
    # Service counter along south-west interior
    b.box(5, 3, 13, 9, 3, 14, 'smooth_quartz')
    b.box(5, 3, 15, 5, 3, 15, 'spruce_planks')
    b.head(6, 4, 13, 'coffee_maker')
    b.head(8, 4, 13, 'pos_terminal')
    # Display shelf along south wall
    for x in range(11, 14):
        b.put(x, 3, 16, 'spruce_planks')
        b.put(x, 4, 16, 'bookshelf')
    # Two customer seating booths along east side
    for z in (10, 14):
        b.put(13, 3, z - 1, 'spruce_stairs[facing=south,half=bottom]')
        b.put(13, 3, z, 'oak_slab[type=top]')
        b.put(13, 3, z + 1, 'spruce_stairs[facing=north,half=bottom]')
    # Pendant lighting hanging from protected stone_bricks ceiling at y=8
    for x in (6, 9, 12):
        for z in (10, 14):
            b.put(x, 7, z, 'lantern[hanging=true]')
    # Exterior hours sign mounted on front shell wall (outside x=3..15, z=7..17, backed by protected white_concrete at z=7)
    b.sign(10, 5, 6, 'north', ['Corner Cafe', 'Interior Refit', '08:00-18:00'])
    # Front paved apron & planters outside protected shell
    b.box(6, 2, 5, 11, 2, 6, 'smooth_stone')
    b.put(5, 3, 6, 'poppy')
    b.put(12, 3, 6, 'dandelion')
    b.put(13, 3, 6, 'cornflower')
    return b.result()


def _small_house() -> dict[str, Any]:
    b = VoxelBuilder()
    # Ground floor plinth & walls x=4..15, z=7..17, y=2..9
    b.box(4, 2, 7, 15, 2, 17, 'spruce_planks')
    # Exterior perimeter walls ground (y=3..5) and upper (y=7..9), floor slab at y=6
    b.box(4, 3, 7, 15, 9, 17, 'white_concrete')
    b.box(5, 3, 8, 14, 5, 16, 'air')
    b.box(5, 6, 8, 14, 6, 16, 'oak_planks')
    b.box(5, 7, 8, 14, 9, 16, 'air')
    # Ground stone trim plinth along exterior base
    for x in range(4, 16):
        b.put(x, 3, 7, 'stone_bricks')
        b.put(x, 3, 17, 'stone_bricks')
    for z in range(7, 18):
        b.put(4, 3, z, 'stone_bricks')
        b.put(15, 3, z, 'stone_bricks')
    # Front entrance door (x=7, z=7) + walkway to pavement z=4
    b.door(7, 3, 7, 'north', 'spruce')
    b.box(6, 2, 5, 8, 2, 6, 'smooth_stone')
    # Windows (keeping full-block door jambs)
    for x in (10, 11, 13):
        b.box(x, 4, 7, x, 5, 7, 'gray_stained_glass')
        b.box(x, 8, 7, x, 9, 7, 'gray_stained_glass')
    for x in (6, 7):
        b.box(x, 8, 7, x, 9, 7, 'gray_stained_glass')
    for z in (10, 11, 14, 15):
        b.box(4, 4, z, 4, 5, z, 'gray_stained_glass')
        b.box(15, 4, z, 15, 5, z, 'gray_stained_glass')
        b.box(4, 8, z, 4, 9, z, 'gray_stained_glass')
        b.box(15, 8, z, 15, 9, z, 'gray_stained_glass')
    for x in (6, 7, 11, 12):
        b.box(x, 4, 17, x, 5, 17, 'gray_stained_glass')
        b.box(x, 8, 17, x, 9, 17, 'gray_stained_glass')
    # Interior stairs along east wall (x=14, z=10..13) rising y=3 -> y=6 (feet y=7) with open stairwell
    for i, z in enumerate((10, 11, 12, 13)):
        b.put(14, 3 + i, z, 'oak_stairs[facing=south,half=bottom]')
    b.box(14, 6, 10, 14, 6, 12, 'air')
    # Ground floor kitchen & living furnishings
    b.box(5, 3, 14, 7, 3, 16, 'smooth_quartz')
    b.put(5, 3, 15, 'furnace[facing=east]')
    b.put(6, 3, 16, 'water_cauldron')
    b.put(10, 3, 14, 'spruce_stairs[facing=north,half=bottom]')
    b.put(11, 3, 14, 'spruce_stairs[facing=north,half=bottom]')
    b.put(10, 3, 12, 'oak_slab[type=top]')
    # Upper floor bedroom with paired bed + bathroom corner
    b.bed(6, 7, 14, 'south', 'red')
    b.put(8, 7, 15, 'spruce_planks')
    b.put(8, 8, 15, 'lantern')
    b.put(11, 7, 15, 'water_cauldron')
    # Lighting on both floors
    for x in (7, 12):
        b.put(x, 5, 11, 'lantern[hanging=true]')
        b.put(x, 9, 11, 'lantern[hanging=true]')
    # Gable roof with overhang & gables
    b.box(4, 10, 7, 15, 10, 17, 'spruce_planks')
    for dx in range(0, 8):
        y = 10 + dx
        lx, rx = 3 + dx, 16 - dx
        for z in range(6, 19):
            b.put(lx, y, z, 'deepslate_tile_stairs[facing=east,half=bottom]')
            b.put(rx, y, z, 'deepslate_tile_stairs[facing=west,half=bottom]')
        if dx >= 1:
            for x in range(lx + 1, rx):
                for z in (7, 17):
                    b.put(x, y, z, 'spruce_planks')
    # Front garden flora
    for x, fl in ((4, 'poppy'), (5, 'dandelion'), (10, 'cornflower'), (12, 'oxeye_daisy'), (14, 'red_tulip')):
        b.put(x, 3, 6, fl)
    return b.result()


def _utility_substation() -> dict[str, Any]:
    b = VoxelBuilder()
    # Paved concrete utility yard pad
    b.box(2, 2, 6, 19, 2, 17, 'smooth_stone')
    b.box(5, 2, 5, 6, 2, 5, 'smooth_stone')
    # Switchgear control house on west side (x=2..9, z=6..14, y=3..7)
    b.box(2, 3, 6, 9, 7, 14, 'bricks')
    b.box(3, 3, 7, 8, 6, 13, 'air')
    b.box(2, 7, 6, 9, 7, 14, 'stone_bricks')
    b.box(2, 8, 6, 9, 8, 14, 'smooth_stone_slab[type=bottom]')
    b.door(5, 3, 6, 'north', 'oak')
    b.box(7, 4, 6, 8, 5, 6, 'gray_stained_glass')
    # Control desk with computer_monitor + switchgear cabinets + interior lights
    b.box(3, 3, 11, 5, 3, 12, 'polished_andesite')
    b.head(4, 4, 11, 'computer_monitor')
    b.box(7, 3, 10, 8, 5, 13, 'iron_block')
    b.put(4, 6, 9, 'lantern[hanging=true]')
    b.put(7, 6, 9, 'lantern[hanging=true]')
    b.sign(3, 5, 5, 'north', ['Substation 4', 'High Voltage', 'Authorized'])
    # Enclosed transformer yard (x=10..19, z=6..17) with iron_bars & masonry piers
    for x in range(10, 20):
        for z in (6, 17):
            b.put(x, 3, z, 'stone_bricks' if x in (10, 14, 19) else 'iron_bars')
            b.put(x, 4, z, 'stone_bricks' if x in (10, 14, 19) else 'iron_bars')
            b.put(x, 5, z, 'stone_brick_slab[type=bottom]' if x in (10, 14, 19) else 'iron_bars')
    for z in range(7, 17):
        b.put(19, 3, z, 'stone_bricks' if z in (11, 12) else 'iron_bars')
        b.put(19, 4, z, 'stone_bricks' if z in (11, 12) else 'iron_bars')
        b.put(19, 5, z, 'stone_brick_slab[type=bottom]' if z in (11, 12) else 'iron_bars')
    for z in range(15, 18):
        b.put(2, 3, z, 'stone_bricks')
        b.put(2, 4, z, 'iron_bars')
    # Two outdoor transformers with cooling fins and lightning-rod bushings
    for tz in (9, 14):
        b.box(12, 3, tz - 1, 16, 4, tz + 1, 'polished_andesite')
        b.box(13, 5, tz, 15, 5, tz, 'copper_block')
        for tx in (13, 15):
            b.put(tx, 6, tz, 'lightning_rod')
    # Overhead busbar + yard lighting
    b.box(13, 7, 9, 13, 7, 14, 'iron_bars')
    b.box(15, 7, 9, 15, 7, 14, 'iron_bars')
    b.put(10, 5, 6, 'lantern')
    b.put(19, 5, 6, 'lantern')
    b.put(19, 5, 17, 'lantern')
    # Kerbside fire_hydrant & frontage planting
    b.put(12, 2, 5, 'smooth_stone')
    b.head(12, 3, 5, 'fire_hydrant')
    for x, fl in ((15, 'azalea'), (16, 'fern'), (17, 'dandelion'), (18, 'poppy')):
        b.put(x, 3, 5, fl)
    return b.result()


def _canal_crossing() -> dict[str, Any]:
    b = VoxelBuilder()
    # Walkable stone footbridge spanning protected canal z=7..10 at y=4 (banks at y=3)
    b.box(10, 3, 5, 13, 3, 6, 'smooth_stone')
    for x in (11, 12):
        b.put(x, 4, 6, 'stone_brick_stairs[facing=south,half=bottom]')
        b.put(x, 4, 11, 'stone_brick_stairs[facing=north,half=bottom]')
    b.box(10, 4, 7, 13, 4, 10, 'stone_bricks')
    for x in (10, 13):
        b.put(x, 4, 6, 'stone_bricks')
        b.put(x, 4, 11, 'stone_bricks')
        for z in range(6, 12):
            b.put(x, 5, z, 'stone_brick_wall')
        b.put(x, 6, 7, 'lantern')
        b.put(x, 6, 10, 'lantern')
    # South bank plaza & approach path
    b.box(9, 3, 12, 14, 3, 13, 'smooth_stone')
    # Waterside tea kiosk x=6..16, z=13..20, floor y=3, ceiling y=7
    b.box(6, 3, 13, 16, 3, 20, 'spruce_planks')
    b.box(6, 4, 13, 16, 7, 20, 'white_concrete')
    b.box(7, 4, 14, 15, 6, 19, 'air')
    b.box(6, 7, 13, 16, 7, 20, 'spruce_planks')
    # Pitched hipped/gabled roof
    for i in range(4):
        b.box(5 + i, 8 + i, 12 + i, 17 - i, 8 + i, 21 - i, 'deepslate_tile_slab[type=bottom]')
    # Reachable south-bank door at z=13 (>= 12) + canal-view glazing
    b.door(11, 4, 13, 'north', 'spruce')
    for x in (8, 9, 13, 14):
        b.box(x, 5, 13, x, 6, 13, 'gray_stained_glass')
    for z in (15, 16, 18):
        b.box(6, 5, z, 6, 6, z, 'gray_stained_glass')
        b.box(16, 5, z, 16, 6, z, 'gray_stained_glass')
    # Counter with coffee_maker + pos_terminal, lights, seating & signage
    b.box(7, 4, 18, 11, 4, 19, 'smooth_quartz')
    b.head(8, 5, 18, 'coffee_maker')
    b.head(10, 5, 18, 'pos_terminal')
    b.put(14, 4, 16, 'spruce_stairs[facing=west,half=bottom]')
    b.put(14, 4, 18, 'spruce_stairs[facing=west,half=bottom]')
    b.put(13, 4, 17, 'oak_slab[type=top]')
    # Outdoor canal-side bench
    b.put(7, 4, 12, 'spruce_stairs[facing=north,half=bottom]')
    b.put(8, 4, 12, 'spruce_stairs[facing=north,half=bottom]')
    b.put(9, 6, 16, 'lantern[hanging=true]')
    b.put(13, 6, 16, 'lantern[hanging=true]')
    b.sign(13, 5, 12, 'north', ['Canal Tea', 'Kiosk', '09:00-19:00'])
    return b.result()


def _corner_shophouse() -> dict[str, Any]:
    b = VoxelBuilder()
    # Two-storey corner shophouse at x=4..17, z=5..17 (protected z<5 and x<4)
    b.box(4, 2, 5, 17, 2, 17, 'smooth_stone')
    b.box(4, 3, 5, 17, 10, 17, 'white_concrete')
    b.box(5, 3, 6, 16, 5, 16, 'air')
    b.box(5, 6, 6, 16, 6, 16, 'spruce_planks')
    b.box(5, 7, 6, 16, 9, 16, 'air')
    # Warm brick upper facade band for architectural articulation
    for y in (7, 8, 9):
        for x in range(4, 18):
            b.put(x, y, 5, 'bricks')
            b.put(x, y, 17, 'bricks')
        for z in range(5, 18):
            b.put(4, y, z, 'bricks')
            b.put(17, y, z, 'bricks')
    # Parapet & roof trim
    b.box(4, 10, 5, 17, 10, 17, 'stone_bricks')
    for x in range(4, 18):
        b.put(x, 11, 5, 'smooth_stone_slab[type=bottom]')
        b.put(x, 11, 17, 'smooth_stone_slab[type=bottom]')
    for z in range(5, 18):
        b.put(4, 11, z, 'smooth_stone_slab[type=bottom]')
        b.put(17, 11, z, 'smooth_stone_slab[type=bottom]')
    # Dual-frontage corner glazing on BOTH north (z=5) and west (x=4) streets!
    b.door(8, 3, 5, 'north', 'spruce')
    for x in (5, 6, 10, 11, 13, 14):
        b.box(x, 4, 5, x, 5, 5, 'gray_stained_glass')
    for z in (7, 8, 10, 11, 13, 14):
        b.box(4, 4, z, 4, 5, z, 'gray_stained_glass')
    # Upper-storey windows
    for x in (6, 7, 11, 12, 15):
        b.box(x, 8, 5, x, 9, 5, 'gray_stained_glass')
    for z in (7, 8, 12, 13):
        b.box(4, 8, z, 4, 9, z, 'gray_stained_glass')
        b.box(17, 8, z, 17, 9, z, 'gray_stained_glass')
    # Interior stairs along east wall (x=16, z=9..12) up to y=6 (feet y=7) with stairwell cutout
    for i, z in enumerate((9, 10, 11, 12)):
        b.put(16, 3 + i, z, 'oak_stairs[facing=south,half=bottom]')
    b.box(16, 6, 9, 16, 6, 11, 'air')
    # Ground bakery/cafe counter + props + seating
    b.box(10, 3, 14, 14, 3, 15, 'smooth_quartz')
    b.head(11, 4, 14, 'coffee_maker')
    b.head(13, 4, 14, 'pos_terminal')
    b.put(6, 3, 11, 'spruce_stairs[facing=south,half=bottom]')
    b.put(6, 3, 12, 'oak_slab[type=top]')
    b.put(6, 3, 13, 'spruce_stairs[facing=north,half=bottom]')
    # Upper studio apartment with paired bed + lighting
    b.bed(6, 7, 14, 'south', 'blue')
    b.put(11, 7, 15, 'bookshelf')
    b.put(12, 7, 15, 'bookshelf')
    for x in (8, 13):
        b.put(x, 5, 10, 'lantern[hanging=true]')
        b.put(x, 9, 10, 'lantern[hanging=true]')
    # Mounted storefront sign (inside x>=4, z>=5 -> mount at z=5? Wait: z=4 is protected! Mount on east courtyard side or recessed porch!
    # Check: if facade is at z=6, sign can be at z=5! Let's check: or mount interior/east exterior sign at x=18, y=5, z=7 backed by x=17!
    b.sign(18, 5, 7, 'east', ['Corner Bake', '& Coffee', '07:30-17:00'])
    # East courtyard with mailbox_orange on slender iron_bars
    b.box(18, 2, 6, 21, 2, 16, 'smooth_stone')
    b.put(19, 3, 7, 'iron_bars')
    b.head(19, 4, 7, 'mailbox_orange')
    b.put(20, 2, 12, 'grass_block')
    b.put(20, 3, 12, 'poppy')
    b.put(20, 2, 14, 'grass_block')
    b.put(20, 3, 14, 'dandelion')
    return b.result()


def _party_wall_infill() -> dict[str, Any]:
    b = VoxelBuilder()
    # Narrow two-storey bookshop filling x=5..16, z=6..17 between protected neighbours x=0..4 and x=17..23
    # Zero glazing on x=5 or x=16 where z=5..17!
    b.box(5, 2, 5, 16, 2, 17, 'spruce_planks')
    b.box(5, 2, 5, 16, 2, 5, 'smooth_stone')
    b.box(5, 3, 6, 16, 10, 17, 'light_gray_terracotta')
    b.box(6, 3, 7, 15, 5, 16, 'air')
    b.box(6, 6, 7, 15, 6, 16, 'oak_planks')
    b.box(6, 7, 7, 15, 9, 16, 'air')
    # Recessed north street frontage (z=6) & glazed rear courtyard wall (z=17)
    b.door(10, 3, 6, 'north', 'dark_oak')
    for x in (6, 7, 8, 12, 13, 14):
        b.box(x, 4, 6, x, 5, 6, 'gray_stained_glass')
        b.box(x, 8, 6, x, 9, 6, 'gray_stained_glass')
        b.box(x, 4, 17, x, 5, 17, 'gray_stained_glass')
        b.box(x, 8, 17, x, 9, 17, 'gray_stained_glass')
    # Projecting upper bay cornice at z=5 (inside x=5..16) + fascia sign
    b.box(5, 6, 5, 16, 6, 5, 'stone_brick_slab[type=top]')
    b.box(5, 10, 5, 16, 10, 5, 'deepslate_tile_slab[type=top]')
    b.sign(10, 5, 5, 'north', ['Infill Books', '& Reading'])
    # Ground floor bookshelves (>= 4) + checkout counter with pos_terminal
    for z in range(9, 15):
        b.box(6, 3, z, 6, 5, z, 'bookshelf')
    b.box(12, 3, 13, 14, 3, 14, 'smooth_quartz')
    b.head(13, 4, 13, 'pos_terminal')
    # Interior stair along east wall (x=15, z=9..12) to upper reading loft (feet y=7)
    for i, z in enumerate((9, 10, 11, 12)):
        b.put(15, 3 + i, z, 'oak_stairs[facing=south,half=bottom]')
    b.box(15, 6, 9, 15, 6, 11, 'air')
    # Upper reading room seating & bookshelves
    for z in (9, 13):
        b.put(8, 7, z, 'spruce_stairs[facing=east,half=bottom]')
        b.put(9, 7, z, 'oak_slab[type=top]')
        b.put(10, 7, z, 'spruce_stairs[facing=west,half=bottom]')
    for z in (10, 11, 12):
        b.box(6, 7, z, 6, 8, z, 'bookshelf')
    # Skylight roof + lighting on both floors
    b.box(5, 10, 6, 16, 10, 17, 'deepslate_tiles')
    b.box(8, 10, 10, 13, 10, 13, 'gray_stained_glass')
    for x in (8, 13):
        b.put(x, 5, 11, 'lantern[hanging=true]')
        b.put(x, 9, 11, 'lantern[hanging=true]')
    # Planted rear courtyard at z=18..20
    for x, z, fl in ((7, 19, 'poppy'), (9, 19, 'fern'), (12, 19, 'cornflower'), (14, 19, 'dandelion')):
        b.put(x, 3, z, fl)
    return b.result()


def _hillside_pavilion() -> dict[str, Any]:
    b = VoxelBuilder()
    # Continuous masonry-retained stepped walkway from north sidewalk (z=4, y=2) up to summit (z=15, y=8)
    for z in range(5, 16):
        target_y = min(8, 2 + (z - 4) // 2 + (1 if z >= 15 else 0))
        for x in range(8, 11):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, target_y), target_y + 1):
                b.put(x, y, z, 'stone_bricks')
            for y in range(target_y + 1, max(g, target_y) + 4):
                b.put(x, y, z, 'air')
        # Retaining side curbs & occasional lanterns
        for sx in (7, 11):
            g = ground_at('hillside-pavilion', sx, z)
            for y in range(min(g, target_y), target_y + 1):
                b.put(sx, y, z, 'stone_bricks')
            b.put(sx, target_y + 1, z, 'stone_brick_wall')
            if z in (7, 11, 14):
                b.put(sx, target_y + 2, z, 'lantern')
    # Mid-slope rest terrace landing at x=12..15, z=9..11, y=5
    for x in range(12, 16):
        for z in range(9, 12):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, 5), 6):
                b.put(x, y, z, 'stone_bricks' if y < 5 else 'smooth_stone')
            for y in range(6, 10):
                b.put(x, y, z, 'air')
    b.put(13, 6, 11, 'spruce_stairs[facing=north,half=bottom]')
    b.put(14, 6, 11, 'spruce_stairs[facing=north,half=bottom]')
    # Summit masonry terrace & roofed lookout tea pavilion at x=5..14, z=15..20, floor y=8
    for x in range(5, 15):
        for z in range(15, 21):
            g = ground_at('hillside-pavilion', x, z)
            for y in range(min(g, 8), 9):
                b.put(x, y, z, 'stone_bricks' if y < 8 else 'spruce_planks')
            for y in range(9, 16):
                b.put(x, y, z, 'air')
    # Pavilion walls y=9..12, roof y=13..15, reachable summit door at y=9 (>= 8)
    b.box(5, 9, 15, 14, 12, 20, 'white_concrete')
    b.box(6, 9, 16, 13, 11, 19, 'air')
    b.door(9, 9, 15, 'north', 'spruce')
    for x in (6, 7, 11, 12):
        b.box(x, 10, 15, x, 11, 15, 'gray_stained_glass')
        b.box(x, 10, 20, x, 11, 20, 'gray_stained_glass')
    for z in (17, 18):
        b.box(5, 10, z, 5, 11, z, 'gray_stained_glass')
        b.box(14, 10, z, 14, 11, z, 'gray_stained_glass')
    b.box(4, 13, 14, 15, 13, 21, 'deepslate_tile_slab[type=bottom]')
    b.box(6, 14, 16, 13, 14, 19, 'deepslate_tiles')
    b.box(7, 15, 17, 12, 15, 18, 'deepslate_tile_slab[type=bottom]')
    b.put(8, 11, 18, 'lantern[hanging=true]')
    b.put(11, 11, 18, 'lantern[hanging=true]')
    b.put(7, 9, 19, 'spruce_stairs[facing=north,half=bottom]')
    b.put(12, 9, 19, 'spruce_stairs[facing=north,half=bottom]')
    b.sign(7, 11, 14, 'north', ['Summit Tea', 'Pavilion'])
    # Slope conifers
    b.conifer(3, ground_at('hillside-pavilion', 3, 11) + 1, 11, height=7)
    b.conifer(19, ground_at('hillside-pavilion', 19, 14) + 1, 14, height=7)
    return b.result()


def _rowhouse_terrace() -> dict[str, Any]:
    b = VoxelBuilder()
    # Three attached 2-storey rowhouses across x=2..27, z=6..18
    units = [
        (2, 10, 'bricks', 'red', 'spruce'),
        (10, 18, 'white_concrete', 'blue', 'oak'),
        (18, 27, 'light_gray_terracotta', 'green', 'dark_oak'),
    ]
    for idx, (x0, x1, wall_mat, bed_col, wood) in enumerate(units):
        # Foundation & 2-storey envelope
        b.box(x0, 2, 6, x1, 2, 18, 'spruce_planks')
        b.box(x0, 3, 6, x1, 10, 18, wall_mat)
        b.box(x0 + 1, 3, 7, x1 - 1, 5, 17, 'air')
        b.box(x0 + 1, 6, 7, x1 - 1, 6, 17, 'oak_planks')
        b.box(x0 + 1, 7, 7, x1 - 1, 9, 17, 'air')
        # Parapet cornice with subtle height variation
        cornice_y = 11 if idx == 1 else 10
        b.box(x0, 10, 6, x1, cornice_y, 18, 'stone_bricks')
        b.box(x0 + 1, 10, 7, x1 - 1, cornice_y, 17, 'deepslate_tiles')
        # Front stoop & reachable street door
        dx = x0 + 3
        b.box(dx - 1, 2, 5, dx + 1, 2, 5, 'smooth_stone')
        b.door(dx, 3, 6, 'north', wood)
        # Front & rear windows
        for wx in (x0 + 5, x0 + 6):
            b.box(wx, 4, 6, wx, 5, 6, 'gray_stained_glass')
            b.box(wx, 8, 6, wx, 9, 6, 'gray_stained_glass')
        b.box(dx, 8, 6, dx, 9, 6, 'gray_stained_glass')
        for wx in (x0 + 2, x0 + 3, x0 + 5, x0 + 6):
            b.box(wx, 4, 18, wx, 5, 18, 'gray_stained_glass')
            b.box(wx, 8, 18, wx, 9, 18, 'gray_stained_glass')
        # Interior stair along inner party wall (x1-1, z=9..12) to upper floor (feet y=7)
        sx = x1 - 1
        for i, z in enumerate((9, 10, 11, 12)):
            b.put(sx, 3 + i, z, f'{wood}_stairs[facing=south,half=bottom]')
        b.box(sx, 6, 9, sx, 6, 11, 'air')
        # Upstairs paired bed + downstairs seating + thorough lighting
        b.bed(x0 + 2, 7, 15, 'south', bed_col)
        b.put(x0 + 2, 3, 14, 'spruce_stairs[facing=north,half=bottom]')
        b.put(x0 + 3, 3, 14, 'oak_slab[type=top]')
        b.put(x0 + 4, 5, 11, 'lantern[hanging=true]')
        b.put(x0 + 4, 9, 11, 'lantern[hanging=true]')
        # Rear yard planting
        b.put(x0 + 3, 3, 20, ('poppy', 'cornflower', 'dandelion')[idx])
        b.put(x0 + 5, 3, 21, 'fern')
    b.sign(13, 5, 5, 'north', ['Maple Row', 'Nos. 1 - 3'])
    return b.result()


def _medical_clinic() -> dict[str, Any]:
    b = VoxelBuilder()
    # Two-storey institutional clinic x=2..25, z=6..19 (floor y=2, upper y=6, roof y=10)
    b.box(2, 2, 6, 25, 2, 19, 'smooth_quartz')
    b.box(11, 2, 5, 16, 2, 5, 'smooth_stone')
    b.box(2, 3, 6, 25, 10, 19, 'white_concrete')
    b.box(3, 3, 7, 24, 5, 18, 'air')
    b.box(3, 6, 7, 24, 6, 18, 'smooth_stone')
    b.box(3, 7, 7, 24, 9, 18, 'air')
    # Cyan terracotta institutional spandrel trim
    for x in range(2, 26):
        b.put(x, 6, 6, 'cyan_terracotta')
        b.put(x, 10, 6, 'cyan_terracotta')
    # Step-free double-width main entrance & display glazing
    b.door(13, 3, 6, 'north', 'oak', 'left')
    b.door(14, 3, 6, 'north', 'oak', 'right')
    for x in (4, 5, 6, 8, 9, 10, 17, 18, 19, 21, 22, 23):
        b.box(x, 4, 6, x, 5, 6, 'light_blue_stained_glass')
        b.box(x, 8, 6, x, 9, 6, 'light_blue_stained_glass')
        b.box(x, 4, 19, x, 5, 19, 'light_blue_stained_glass')
        b.box(x, 8, 19, x, 9, 19, 'light_blue_stained_glass')
    # Reception desk (computer_monitor), pharmacy counter (pos_terminal), defibrillator
    b.box(11, 3, 11, 16, 3, 12, 'smooth_quartz')
    b.head(13, 4, 11, 'computer_monitor')
    b.box(4, 3, 15, 8, 3, 16, 'smooth_quartz')
    b.head(6, 4, 15, 'pos_terminal')
    b.put(18, 3, 11, 'polished_andesite')
    b.head(18, 4, 11, 'defibrillator')
    # Waiting seating (>= 3)
    for x in (4, 5, 6, 7):
        b.put(x, 3, 9, 'spruce_stairs[facing=south,half=bottom]')
    # Wide 2-wide interior stairs (x=22..23, z=10..13) up to upper consultation rooms (feet y=7)
    for i, z in enumerate((10, 11, 12, 13)):
        for sx in (22, 23):
            b.put(sx, 3 + i, z, 'smooth_quartz_stairs[facing=south,half=bottom]')
    b.box(22, 6, 10, 23, 6, 12, 'air')
    # Upper consultation partitions & desks
    b.box(10, 7, 7, 10, 9, 14, 'white_concrete')
    b.box(17, 7, 7, 17, 9, 14, 'white_concrete')
    for x in (5, 13, 19):
        b.put(x, 7, 10, 'smooth_quartz')
        b.put(x, 7, 12, 'spruce_stairs[facing=north,half=bottom]')
    # Bright ceiling sea_lanterns across both floors (>= 6)
    for x in (6, 13, 20):
        for z in (9, 16):
            b.put(x, 6, z, 'sea_lantern')
            b.put(x, 10, z, 'sea_lantern')
    # Parapet & rooftop mechanical unit
    b.box(2, 11, 6, 25, 11, 6, 'smooth_stone_slab[type=bottom]')
    b.box(2, 11, 19, 25, 11, 19, 'smooth_stone_slab[type=bottom]')
    b.box(10, 11, 11, 16, 12, 14, 'light_gray_concrete')
    b.sign(13, 6, 5, 'north', ['Civic Clinic', '& Pharmacy', 'Urgent Care'])
    return b.result()


def _grocery_supermarket() -> dict[str, Any]:
    b = VoxelBuilder()
    # Large supermarket x=5..29, z=6..24 (protected z<5 and x<4)
    b.box(5, 2, 6, 29, 2, 24, 'light_gray_concrete')
    b.box(13, 2, 5, 19, 2, 5, 'smooth_stone')
    b.box(4, 2, 17, 4, 2, 20, 'smooth_stone')
    # Outer shell y=3..8, parapet y=9
    b.box(5, 3, 6, 29, 8, 24, 'white_concrete')
    b.box(6, 3, 7, 28, 7, 23, 'air')
    b.box(5, 8, 6, 29, 8, 24, 'light_gray_concrete')
    for x in range(5, 30):
        b.put(x, 7, 6, 'green_terracotta')
        b.put(x, 9, 6, 'stone_bricks')
        b.put(x, 9, 24, 'stone_bricks')
    for z in range(6, 25):
        b.put(5, 9, z, 'stone_bricks')
        b.put(29, 9, z, 'stone_bricks')
    # Customer entrance on north (z=6) + loading/service door on west (x=5)
    b.door(15, 3, 6, 'north', 'oak', 'left')
    b.door(16, 3, 6, 'north', 'oak', 'right')
    b.door(5, 3, 18, 'west', 'spruce')
    # North display glazing
    for x in (7, 8, 9, 10, 11, 12, 19, 20, 21, 22, 23, 24, 25, 26, 27):
        b.box(x, 4, 6, x, 6, 6, 'gray_stained_glass')
    # Two checkout lanes with pos_terminal
    for cx in (11, 19):
        b.box(cx, 3, 9, cx + 2, 3, 10, 'smooth_quartz')
        b.head(cx + 1, 4, 9, 'pos_terminal')
    # Parallel stocked retail gondola aisles
    for gx in (9, 14, 20, 25):
        b.box(gx, 3, 13, gx + 1, 4, 19, 'bookshelf')
        b.box(gx, 5, 13, gx + 1, 5, 19, 'smooth_stone_slab[type=bottom]')
    # Rear refrigerated cold wall
    b.box(8, 3, 23, 26, 5, 23, 'light_blue_stained_glass')
    for x in range(9, 26, 4):
        b.put(x, 6, 23, 'sea_lantern')
    # Grid of bright ceiling sea_lanterns across deep floorplate (zero dark_interior!)
    for x in (8, 13, 18, 23, 27):
        for z in (9, 14, 19, 22):
            b.put(x, 8, z, 'sea_lantern')
    # Rooftop HVAC units
    b.box(10, 9, 12, 14, 10, 15, 'polished_andesite')
    b.box(20, 9, 14, 24, 10, 17, 'polished_andesite')
    # Fascia signs (>= 2) + kerbside parking_meter on iron_bars
    b.sign(15, 7, 5, 'north', ['Fresh Market', 'Groceries'])
    b.sign(19, 7, 5, 'north', ['Open Daily', '07:00 - 22:00'])
    b.put(9, 3, 5, 'iron_bars')
    b.head(9, 4, 5, 'parking_meter')
    return b.result()


def _elevated_rail_station() -> dict[str, Any]:
    b = VoxelBuilder()
    # Protected viaduct: x=0..33, z=15..18, y=10..12 + piers x in (2,11,22,31), z=15..18, y=2..9
    # Street-level concourse/ticket hall at x=6..27, z=6..13 (floor y=2, ceiling y=6)
    b.box(6, 2, 6, 27, 2, 13, 'smooth_stone')
    b.box(14, 2, 5, 19, 2, 5, 'smooth_stone')
    b.box(6, 3, 6, 27, 6, 13, 'light_gray_concrete')
    b.box(7, 3, 7, 26, 5, 12, 'air')
    b.door(16, 3, 6, 'north', 'oak', 'left')
    b.door(17, 3, 6, 'north', 'oak', 'right')
    for x in (8, 9, 10, 12, 13, 20, 21, 23, 24, 25):
        b.box(x, 4, 6, x, 5, 6, 'gray_stained_glass')
    # Fare gate island with ticket_validator props
    for fx in (12, 16, 20):
        b.put(fx, 3, 9, 'polished_andesite')
        b.head(fx, 4, 9, 'ticket_validator')
    # Elevated boarding platform flush alongside north track edge (x=4..29, z=11..14, y=10 -> feet y=11)
    b.box(4, 10, 11, 29, 10, 14, 'stone_bricks')
    for x in range(4, 30):
        b.put(x, 10, 14, 'yellow_concrete')
    # Platform support columns outside protected viaduct
    for px in (5, 11, 17, 23, 28):
        b.box(px, 3, 14, px, 9, 14, 'stone_bricks')
        b.box(px, 11, 11, px, 14, 11, 'gray_concrete')
    # Covered staircase rising smoothly from concourse (y=3, x=24, z=10) west to platform (y=10, x=17, z=12)
    # Step up along x=24..17 inside z=11..12: 8 steps y=3..10 (feet reach y=11 at x=16!)
    for i in range(8):
        sx = 24 - i
        sy = 3 + i
        for sz in (11, 12):
            b.put(sx, sy, sz, 'stone_brick_stairs[facing=west,half=bottom]')
            for cy in range(sy + 1, min(14, sy + 4)):
                b.put(sx, cy, sz, 'air')
        # Solid support under stair
        if sy > 3:
            b.box(sx, 3, 11, sx, sy - 1, 12, 'stone_bricks')
    # Clear platform landing cutout at x=17..23 on y=10 where stairs rise
    b.box(18, 10, 11, 24, 10, 12, 'air')
    for i in range(8):
        sx = 24 - i
        sy = 3 + i
        for sz in (11, 12):
            b.put(sx, sy, sz, 'stone_brick_stairs[facing=west,half=bottom]')
    # Platform canopy at y=15 + rear glass windscreen at z=11
    b.box(4, 15, 11, 29, 15, 14, 'gray_concrete')
    b.box(4, 16, 11, 29, 16, 14, 'smooth_stone_slab[type=bottom]')
    for x in range(6, 28):
        if x not in (11, 17, 23):
            b.box(x, 12, 11, x, 13, 11, 'gray_stained_glass_pane')
    # Platform benches (>= 2), departure signage (>= 2), thorough lighting (>= 8)
    for x in (8, 9, 13, 14):
        b.put(x, 11, 12, 'spruce_stairs[facing=south,half=bottom]')
    for x in (8, 13, 18, 23):
        b.put(x, 6, 9, 'sea_lantern')
        b.put(x, 14, 12, 'lantern[hanging=true]')
        b.put(x, 14, 13, 'lantern[hanging=true]')
    b.sign(14, 5, 5, 'north', ['Central Rail', 'Platform 1'])
    b.sign(11, 13, 12, 'south', ['Eastbound', 'Platform 1', 'Every 5 min'])
    return b.result()


def _midrise_apartments() -> dict[str, Any]:
    b = VoxelBuilder()
    # 5-storey mixed-use midrise at x=4..25, z=6..20, floors at y=2, 6, 11, 15, 19, roof y=23, bulkhead y=24..26
    floor_ys = [2, 6, 11, 15, 19]
    roof_y = 23
    b.box(4, 2, 6, 25, 2, 20, 'smooth_stone')
    b.box(7, 2, 5, 10, 2, 5, 'smooth_stone')
    b.box(18, 2, 5, 21, 2, 5, 'smooth_stone')
    # Exterior envelope + floorplates
    b.box(4, 3, 6, 25, roof_y, 20, 'light_gray_concrete')
    for fy in floor_ys:
        top = roof_y if fy == floor_ys[-1] else floor_ys[floor_ys.index(fy) + 1]
        b.box(5, fy + 1, 7, 24, top - 1, 19, 'air')
        if fy > 2:
            b.box(5, fy, 7, 24, fy, 19, 'oak_planks')
    # Brick residential facade above ground concrete retail podium
    for y in range(7, roof_y):
        for x in range(4, 26):
            b.put(x, y, 6, 'bricks')
            b.put(x, y, 20, 'bricks')
        for z in range(6, 21):
            b.put(4, y, z, 'bricks')
            b.put(25, y, z, 'bricks')
    # Ground floor partition between west cafe (x=5..14) and east residential lobby (x=15..24)
    b.box(15, 3, 6, 15, 5, 19, 'white_concrete')
    b.door(8, 3, 6, 'north', 'spruce')
    b.door(19, 3, 6, 'north', 'oak')
    # Ground cafe fit-out (coffee_maker, pos_terminal) + fascia sign
    b.box(6, 3, 15, 11, 3, 16, 'smooth_quartz')
    b.head(7, 4, 15, 'coffee_maker')
    b.head(10, 4, 15, 'pos_terminal')
    b.sign(8, 5, 5, 'north', ['Harbour', 'Flats & Cafe'])
    # Continuous switchback stair core in x=19..24, z=11..18 rising from y=3 to y=20 (covers tiers 6, 12, 18!)
    for i in range(len(floor_ys) - 1):
        fy = floor_ys[i]
        ny = floor_ys[i + 1]
        steps = ny - fy
        go_south = (i % 2 == 0)
        sx = 23 if go_south else 21
        for s in range(steps):
            sz = (12 + s) if go_south else (16 - s)
            sy = fy + 1 + s
            facing = 'south' if go_south else 'north'
            b.put(sx, sy, sz, f'stone_brick_stairs[facing={facing},half=bottom]')
            for cy in range(sy + 1, min(ny + 3, sy + 4)):
                b.put(sx, cy, sz, 'air')
        # Ensure stairwell cutout in upper slab above stair run
        for s in range(steps - 1):
            sz = (12 + s) if go_south else (16 - s)
            b.put(sx, ny, sz, 'air')
    # Recessed windows, balconies & upper apartment beds (>= 3)
    for idx, fy in enumerate(floor_ys):
        for x in (6, 7, 11, 12, 17, 21, 22):
            if fy == 2 and x in (8, 19):
                continue
            b.box(x, fy + 2, 6, x, fy + 3, 6, 'gray_stained_glass')
            b.box(x, fy + 2, 20, x, fy + 3, 20, 'gray_stained_glass')
        if fy >= 6:
            # Guarded north balconies
            b.box(10, fy, 5, 13, fy, 5, 'smooth_stone')
            for bx in range(10, 14):
                b.put(bx, fy + 1, 5, 'gray_stained_glass_pane')
            # Furnished apartment bed on levels 2, 3, 4
            if idx in (1, 2, 3):
                b.bed(7, fy + 1, 15, 'south', ('red', 'blue', 'yellow')[idx - 1])
        # Thorough floorplate lighting
        for lx in (8, 13, 18, 23):
            for lz in (10, 16):
                b.put(lx, fy + 3, lz, 'sea_lantern')
    # Roof parapet + mechanical bulkhead (peak y=26 >= 23)
    b.box(4, roof_y, 6, 25, roof_y, 20, 'stone_bricks')
    for x in range(4, 26):
        b.put(x, roof_y + 1, 6, 'smooth_stone_slab[type=bottom]')
        b.put(x, roof_y + 1, 20, 'smooth_stone_slab[type=bottom]')
    b.box(17, roof_y + 1, 11, 23, roof_y + 3, 17, 'gray_concrete')
    b.box(17, roof_y + 4, 11, 23, roof_y + 4, 17, 'smooth_stone_slab[type=bottom]')
    return b.result()


def _civic_office_tower() -> dict[str, Any]:
    b = VoxelBuilder()
    # 2-storey public podium x=4..25, z=6..22 (floors y=2, 6; podium roof y=10)
    # 6-storey stepped tower shaft x=7..22, z=8..20 (floors y=10, 14, 18, 22, 26; roof y=30; crown y=31..35)
    b.box(4, 2, 6, 25, 2, 22, 'polished_andesite')
    b.box(12, 2, 5, 17, 2, 5, 'smooth_stone')
    b.box(4, 3, 6, 25, 10, 22, 'light_gray_concrete')
    b.box(5, 3, 7, 24, 5, 21, 'air')
    b.box(5, 6, 7, 24, 6, 21, 'smooth_stone')
    b.box(5, 7, 7, 24, 9, 21, 'air')
    b.box(4, 10, 6, 25, 10, 22, 'stone_bricks')
    # Podium entrance, reception (computer_monitor) & civic signage
    b.door(14, 3, 6, 'north', 'oak', 'left')
    b.door(15, 3, 6, 'north', 'oak', 'right')
    for x in range(6, 24):
        if x not in (13, 14, 15, 16) and x % 3 != 0:
            b.box(x, 4, 6, x, 5, 6, 'light_blue_stained_glass')
            b.box(x, 8, 6, x, 9, 6, 'light_blue_stained_glass')
    b.box(12, 3, 11, 17, 3, 11, 'smooth_quartz')
    b.head(14, 4, 11, 'computer_monitor')
    b.sign(14, 6, 5, 'north', ['Civic Office', 'Tower'])
    # Tower shaft y=10..30 with mullion/spandrel articulation
    shaft_floors = [10, 14, 18, 22, 26]
    b.box(7, 11, 8, 22, 30, 20, 'gray_concrete')
    for fy in shaft_floors:
        b.box(8, fy + 1, 9, 21, fy + 3, 19, 'air')
        b.box(8, fy, 9, 21, fy, 19, 'smooth_stone')
        # Curtain-wall bays between dark mullions on all 4 elevations
        for x in range(8, 22):
            if x % 3 != 1:
                b.box(x, fy + 1, 8, x, fy + 3, 8, 'light_blue_stained_glass')
                b.box(x, fy + 1, 20, x, fy + 3, 20, 'light_blue_stained_glass')
        for z in range(9, 20):
            if z % 3 != 0:
                b.box(7, fy + 1, z, 7, fy + 3, z, 'light_blue_stained_glass')
                b.box(22, fy + 1, z, 22, fy + 3, z, 'light_blue_stained_glass')
        # Spandrel banding
        for x in range(7, 23):
            b.put(x, fy, 8, 'light_gray_concrete')
            b.put(x, fy, 20, 'light_gray_concrete')
    b.box(7, 30, 8, 22, 30, 20, 'stone_bricks')
    # Continuous switchback stair core from y=2 up to y=26 (covers tiers 6, 14, 22!)
    all_floors = [2, 6, 10, 14, 18, 22, 26]
    for i in range(len(all_floors) - 1):
        fy = all_floors[i]
        ny = all_floors[i + 1]
        steps = ny - fy
        go_south = (i % 2 == 0)
        sx = 18 if go_south else 16
        for s in range(steps):
            sz = (12 + s) if go_south else (15 - s)
            sy = fy + 1 + s
            facing = 'south' if go_south else 'north'
            b.put(sx, sy, sz, f'stone_brick_stairs[facing={facing},half=bottom]')
            for cy in range(sy + 1, min(ny + 3, sy + 4)):
                b.put(sx, cy, sz, 'air')
        for s in range(steps - 1):
            sz = (12 + s) if go_south else (15 - s)
            b.put(sx, ny, sz, 'air')
    # Lighting on podium + every tower floor (>= 12)
    for fy in (2, 6):
        for lx in (8, 14, 21):
            for lz in (10, 17):
                b.put(lx, fy + 3, lz, 'sea_lantern')
    for fy in shaft_floors:
        for lx in (10, 15, 19):
            for lz in (11, 17):
                b.put(lx, fy + 3, lz, 'sea_lantern')
    # Rooftop mechanical crown & aircraft warning beacons (peak y=35 >= 32, lights at y=35 >= 30)
    b.box(10, 31, 11, 19, 34, 17, 'gray_concrete')
    b.box(10, 35, 11, 19, 35, 17, 'smooth_stone_slab[type=bottom]')
    for cx, cz in ((10, 11), (19, 11), (10, 17), (19, 17)):
        b.put(cx, 35, cz, 'iron_bars')
        b.put(cx, 36, cz, 'redstone_torch')
    return b.result()


def _chunk_cliff_scar() -> dict[str, Any]:
    b = VoxelBuilder()
    # Clear stranded floating chunk-error tree crown at x=13..15, z=14..16, y=12..13
    b.box(13, 12, 14, 15, 13, 16, 'air')
    # Solidly fill sunken 16x16 chunk x=8..23, z=6..21 matching surrounding hillside elevations
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
    # Restore natural trees and meadow flora on south hillside
    b.conifer(12, 5 + (15 - 6) // 6 + 1, 15, height=8)
    b.broadleaf(19, 5 + (17 - 6) // 6 + 1, 17, height=7)
    for x, z, fl in (
        (10, 13, 'poppy'), (14, 14, 'dandelion'), (16, 13, 'cornflower'),
        (21, 14, 'oxeye_daisy'), (11, 19, 'fern'), (15, 19, 'poppy'),
    ):
        top = 5 + (z - 6) // 6
        b.put(x, top + 1, z, fl)
    return b.result()


def _chunk_river_seam() -> dict[str, Any]:
    b = VoxelBuilder()
    # Excavate raised y=10 monolith + clear floating spruce leaves at y=14 inside x=8..23, z=5..20
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
    # Continuous walkable path & timber/stone footbridge connecting north walkway to south meadow
    for z in range(5, 9):
        for x in (15, 16):
            b.put(x, 4, z, 'smooth_stone')
    for z in range(15, 21):
        for x in (15, 16):
            b.put(x, 4, z, 'smooth_stone')
    # Bridge abutments, stairs and deck at y=5 over creek z=10..13
    for x in (15, 16):
        b.put(x, 4, 9, 'stone_bricks')
        b.put(x, 4, 14, 'stone_bricks')
        b.put(x, 5, 9, 'spruce_stairs[facing=south,half=bottom]')
        b.put(x, 5, 14, 'spruce_stairs[facing=north,half=bottom]')
    b.box(14, 5, 10, 17, 5, 13, 'spruce_planks')
    for x in (14, 17):
        b.box(x, 4, 9, x, 5, 9, 'stone_bricks')
        b.box(x, 4, 14, x, 5, 14, 'stone_bricks')
        for z in range(9, 15):
            b.put(x, 6, z, 'stone_brick_wall')
        b.put(x, 7, 10, 'lantern')
        b.put(x, 7, 13, 'lantern')
    # Meadow trees & bank flora
    b.broadleaf(11, 5, 17, height=7)
    b.conifer(20, 5, 17, height=7)
    for x, z, fl in ((10, 7, 'poppy'), (12, 7, 'dandelion'), (19, 7, 'cornflower'), (19, 16, 'fern')):
        b.put(x, 5, z, fl)
    return b.result()


def _coastal_seawall() -> dict[str, Any]:
    b = VoxelBuilder()
    # Clear floating leaves (9..10, 11, 9) and re-grade bluff x=0..27, z=5..15 cleanly
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
                top, surf = 4, 'smooth_stone' if z in (13, 14) else 'stone_bricks'
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
    # Grand stepped promenade stair at x=12..15 from upland z=5 (y=7) down to quay z=13 (y=4)
    for x in range(12, 16):
        b.put(x, 7, 5, 'smooth_stone')
        b.put(x, 7, 6, 'air')
        b.put(x, 6, 6, 'stone_brick_stairs[facing=north,half=bottom]')
        b.put(x, 6, 7, 'smooth_stone')
        b.put(x, 6, 8, 'air')
        b.put(x, 5, 8, 'stone_brick_stairs[facing=north,half=bottom]')
        for z in (9, 10, 11):
            b.put(x, 5, z, 'smooth_stone')
        b.put(x, 5, 12, 'stone_brick_stairs[facing=north,half=bottom]')
    # Waterfront railing & lanterns along seawall edge z=15
    for x in range(28):
        b.put(x, 5, 15, 'stone_bricks' if x % 6 == 2 else 'stone_brick_wall')
        if x % 6 == 2:
            b.put(x, 6, 15, 'lantern')
    # Harbour benches (>= 2), coastal conifers (>= 8 leaves) & mounted sign
    for x in (6, 7, 20, 21):
        b.put(x, 5, 13, 'spruce_stairs[facing=south,half=bottom]')
    b.conifer(4, 6, 9, height=8)
    b.conifer(23, 6, 9, height=8)
    b.box(10, 5, 12, 10, 6, 12, 'stone_bricks')
    b.sign(10, 6, 13, 'south', ['Harbour Quay', 'Promenade'])
    for x, z, fl in ((7, 8, 'fern'), (9, 9, 'poppy'), (18, 9, 'dandelion'), (20, 8, 'cornflower')):
        b.put(x, 6, z, fl)
    return b.result()


def _quarry_reclamation() -> dict[str, Any]:
    b = VoxelBuilder()
    # Solidly fill and terrace quarry pit x=4..23, z=5..22 into sunken garden & pond (water y=3)
    for x in range(4, 24):
        for z in range(5, 23):
            in_pond = 10 <= x <= 17 and 12 <= z <= 17 and not (x in (10, 17) and z in (12, 17))
            outer_rim = x in (4, 5, 22, 23) or z in (5, 21, 22)
            if in_pond:
                b.put(x, 1, z, 'stone')
                b.put(x, 2, z, 'gravel')
                b.put(x, 3, z, 'water')
            elif outer_rim:
                top = 5 if z <= 8 else 5
                for y in range(1, top):
                    b.put(x, y, z, 'stone' if y < top - 1 else 'dirt')
                b.put(x, top, z, 'grass_block')
            else:
                # Terraced sunken garden floor at y=4 (inner pond bank at y=3)
                near_pond = 9 <= x <= 18 and 11 <= z <= 18
                top = 3 if near_pond else 4
                for y in range(1, top):
                    b.put(x, y, z, 'stone' if y < top - 1 else 'dirt')
                b.put(x, top, z, 'moss_block' if near_pond else 'grass_block')
    # Stepped walkway from north street (z=4, y=5) down to pond terrace (y=4 -> y=3) & loop
    for x in (13, 14):
        b.put(x, 5, 5, 'smooth_stone')
        b.put(x, 5, 6, 'air')
        b.put(x, 4, 6, 'stone_brick_stairs[facing=north,half=bottom]')
        for z in (7, 8, 9):
            b.put(x, 4, z, 'smooth_stone')
        b.put(x, 4, 10, 'stone_brick_stairs[facing=north,half=bottom]')
    # Lakeside smooth_stone loop around pond at y=3..4
    for x in range(9, 19):
        b.put(x, 3, 11, 'smooth_stone')
        b.put(x, 3, 18, 'smooth_stone')
    for z in range(11, 19):
        b.put(9, 3, z, 'smooth_stone')
        b.put(18, 3, z, 'smooth_stone')
    # Conifer + broadleaf trees, seating (>= 2), lanterns (>= 2), flora (>= 4)
    b.conifer(6, 5, 9, height=8)
    b.broadleaf(20, 5, 10, height=7)
    b.put(10, 4, 10, 'spruce_stairs[facing=south,half=bottom]')
    b.put(11, 4, 10, 'spruce_stairs[facing=south,half=bottom]')
    b.put(16, 4, 19, 'spruce_stairs[facing=north,half=bottom]')
    b.put(17, 4, 19, 'spruce_stairs[facing=north,half=bottom]')
    for lx, lz in ((9, 11), (18, 11), (9, 18), (18, 18)):
        b.put(lx, 4, lz, 'stone_brick_wall')
        b.put(lx, 5, lz, 'lantern')
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
