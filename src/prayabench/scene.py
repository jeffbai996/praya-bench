"""Declared block palette and bounded JSON scene format; no code execution."""
import json
from pathlib import Path
import re
from typing import Any

MAX_BYTES = 12_000_000
MAX_CELLS = 90_000
ASSETS = (
    'coffee_maker', 'pos_terminal', 'mailbox_orange',
    'ticket_validator', 'computer_monitor', 'fire_hydrant',
    'parking_meter', 'trash_bin', 'defibrillator',
)
POST_MOUNTED_ASSETS = frozenset({'mailbox_orange', 'parking_meter'})
WOODS = ('oak', 'spruce', 'birch', 'dark_oak', 'acacia', 'jungle', 'cherry', 'mangrove')
COLORS = (
    'white', 'light_gray', 'gray', 'black', 'red', 'orange', 'yellow', 'green',
    'lime', 'blue', 'light_blue', 'cyan', 'purple', 'magenta', 'pink', 'brown',
)
FLORA_SOIL = frozenset({'grass_block', 'dirt', 'coarse_dirt', 'podzol', 'moss_block', 'rooted_dirt', 'mud'})
TALL_FLORA = frozenset({'tall_grass', 'large_fern', 'peony', 'rose_bush', 'lilac', 'sunflower'})
GROUND_FLORA = TALL_FLORA | frozenset({
    'azalea', 'flowering_azalea', 'bush', 'sweet_berry_bush', 'fern', 'short_grass',
    'poppy', 'dandelion', 'cornflower', 'azure_bluet', 'oxeye_daisy',
    'lily_of_the_valley', 'allium', 'blue_orchid',
    'red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip',
})
GRAVITY_BLOCKS = frozenset({'sand', 'red_sand', 'gravel'})
RAIL_BLOCKS = frozenset({'rail', 'powered_rail', 'detector_rail', 'activator_rail'})

PALETTE = set(
    'air stone cobblestone mossy_cobblestone coal_ore iron_ore copper_ore '
    'dirt rooted_dirt clay mud packed_mud grass_block podzol coarse_dirt gravel sand red_sand '
    'calcite terracotta bricks mud_bricks brick_wall stone_bricks mossy_stone_bricks '
    'chiseled_stone_bricks cracked_stone_bricks smooth_stone smooth_quartz quartz_block '
    'quartz_bricks quartz_pillar prismarine prismarine_bricks dark_prismarine '
    'granite polished_granite polished_diorite polished_andesite andesite diorite '
    'tuff polished_tuff tuff_bricks polished_deepslate deepslate_tiles deepslate_bricks '
    'polished_blackstone polished_basalt copper_block cut_copper weathered_copper '
    'weathered_cut_copper oxidized_copper oxidized_cut_copper copper_bulb '
    'weathered_copper_bulb oxidized_copper_bulb waxed_copper_bulb waxed_oxidized_copper_bulb '
    'iron_block iron_bars iron_chain chain lightning_rod glass tinted_glass glass_pane '
    'sea_lantern shroomlight ochre_froglight verdant_froglight pearlescent_froglight '
    'lantern soul_lantern torch wall_torch end_rod redstone_torch redstone_wall_torch '
    'redstone_lamp glowstone barrel bookshelf lectern furnace blast_furnace smoker '
    'crafting_table cartography_table smithing_table loom stonecutter grindstone anvil '
    'bell note_block jukebox chest composter cauldron water_cauldron hopper ladder '
    'scaffolding campfire soul_campfire daylight_detector hay_block bone_block '
    'rail powered_rail detector_rail activator_rail '
    'heavy_weighted_pressure_plate light_weighted_pressure_plate polished_blackstone_pressure_plate '
    'water lily_pad vine glow_lichen '
    'flower_pot potted_fern potted_azalea_bush potted_flowering_azalea_bush '
    'potted_poppy potted_dandelion potted_allium potted_azure_bluet potted_cornflower '
    'potted_lily_of_the_valley potted_oxeye_daisy potted_oak_sapling potted_spruce_sapling '
    'potted_birch_sapling potted_bamboo potted_cactus potted_dead_bush '
    'potted_red_tulip potted_orange_tulip potted_white_tulip potted_pink_tulip '
    'azalea flowering_azalea bush sweet_berry_bush fern large_fern short_grass tall_grass '
    'poppy dandelion cornflower azure_bluet oxeye_daisy lily_of_the_valley allium '
    'blue_orchid red_tulip orange_tulip white_tulip pink_tulip peony rose_bush lilac sunflower '
    'moss_block moss_carpet player_head player_wall_head iron_door iron_trapdoor '
    'oak_leaves spruce_leaves birch_leaves jungle_leaves acacia_leaves dark_oak_leaves '
    'cherry_leaves mangrove_leaves azalea_leaves flowering_azalea_leaves '
    'candle cake lever stone_button polished_blackstone_button stone_pressure_plate'.split()
)
for wood in WOODS:
    for suffix in (
        'planks', 'log', 'wood', 'stairs', 'slab', 'fence', 'fence_gate', 'trapdoor',
        'door', 'sign', 'wall_sign', 'hanging_sign', 'wall_hanging_sign', 'button',
        'pressure_plate',
    ):
        PALETTE.add(f'{wood}_{suffix}')
    PALETTE.update((f'stripped_{wood}_log', f'stripped_{wood}_wood'))
for suffix in (
    'planks', 'mosaic', 'stairs', 'mosaic_stairs', 'slab', 'mosaic_slab', 'fence',
    'fence_gate', 'trapdoor', 'door', 'sign', 'wall_sign', 'hanging_sign',
    'wall_hanging_sign', 'button', 'pressure_plate',
):
    PALETTE.add(f'bamboo_{suffix}')
PALETTE.update(('bamboo_block', 'stripped_bamboo_block'))
for color in COLORS:
    for suffix in ('concrete', 'terracotta', 'wool', 'carpet', 'stained_glass', 'stained_glass_pane', 'bed', 'candle'):
        PALETTE.add(f'{color}_{suffix}')
for stone in (
    'stone', 'cobblestone', 'mossy_cobblestone', 'stone_brick', 'mossy_stone_brick',
    'smooth_stone', 'quartz', 'smooth_quartz', 'brick', 'mud_brick',
    'granite', 'polished_granite', 'diorite', 'polished_diorite',
    'andesite', 'polished_andesite', 'tuff', 'polished_tuff', 'tuff_brick',
    'prismarine', 'prismarine_brick', 'dark_prismarine',
    'polished_deepslate', 'deepslate_tile', 'deepslate_brick',
    'polished_blackstone', 'sandstone', 'smooth_sandstone', 'red_sandstone', 'smooth_red_sandstone',
    'cut_copper', 'weathered_cut_copper', 'oxidized_cut_copper',
):
    PALETTE.add(f'{stone}_slab')
    if stone != 'smooth_stone':
        PALETTE.add(f'{stone}_stairs')
    if stone in (
        'cobblestone', 'mossy_cobblestone', 'stone_brick', 'mossy_stone_brick',
        'brick', 'mud_brick', 'granite', 'diorite', 'andesite', 'tuff', 'polished_tuff',
        'tuff_brick', 'prismarine', 'polished_deepslate', 'deepslate_tile', 'deepslate_brick',
        'polished_blackstone', 'sandstone', 'red_sandstone',
    ):
        PALETTE.add(f'{stone}_wall')
for copper in (
    'copper_block', 'cut_copper', 'cut_copper_slab', 'cut_copper_stairs',
    'weathered_copper', 'weathered_cut_copper', 'weathered_cut_copper_slab', 'weathered_cut_copper_stairs',
    'oxidized_copper', 'oxidized_cut_copper', 'oxidized_cut_copper_slab', 'oxidized_cut_copper_stairs',
):
    PALETTE.add(f'waxed_{copper}')
# Deliberately a supported rendering vocabulary, not a full game block registry.
VEC = {
    'north': (0, 0, -1), 'south': (0, 0, 1),
    'east': (1, 0, 0), 'west': (-1, 0, 0),
    'up': (0, 1, 0), 'down': (0, -1, 0),
}


def state_parts(state: str) -> tuple[str, dict[str, str]]:
    match = re.fullmatch(r'(?:minecraft:)?([a-z0-9_]+)(?:\[([a-z0-9_=,]+)\])?', state)
    if not match:
        raise ValueError('malformed block state')
    props: dict[str, str] = {}
    if match[2]:
        for entry in match[2].split(','):
            bits = entry.split('=')
            if len(bits) != 2 or bits[0] in props:
                raise ValueError('malformed or duplicate property')
            props[bits[0]] = bits[1]
    return match[1], props


def load_json(path: str | Path) -> Any:
    p = Path(path)
    if p.stat().st_size > MAX_BYTES:
        raise ValueError('input exceeds 12 MB')
    return json.loads(p.read_text())


def validate_cells(obj: dict[str, Any]) -> dict[tuple[int, int, int], list[Any]]:
    if not isinstance(obj, dict) or not isinstance(obj.get('cells'), list):
        raise ValueError('expected {"cells": [...]}')
    if len(obj['cells']) > MAX_CELLS:
        raise ValueError('too many cells')
    out: dict[tuple[int, int, int], list[Any]] = {}
    for c in obj['cells']:
        if not isinstance(c, list) or not 4 <= len(c) <= 7:
            raise ValueError('cell must have 4–7 fields')
        x, y, z, state = c[:4]
        if any(type(v) is not int or abs(v) > 1024 for v in (x, y, z)):
            raise ValueError('coordinates must be bounded integers')
        if not isinstance(state, str) or len(state) > 180:
            raise ValueError('invalid state')
        state_parts(state)
        lines = c[4] if len(c) > 4 else None
        if lines is not None and (
            not isinstance(lines, list)
            or len(lines) > 4
            or any(not isinstance(s, str) or len(s) > 100 for s in lines)
        ):
            raise ValueError('sign needs at most four short strings')
        component = c[5] if len(c) > 5 else ''
        if not isinstance(component, str) or len(component) > 100:
            raise ValueError('invalid component label')
        asset = c[6] if len(c) > 6 else None
        if asset is not None and asset not in ASSETS:
            raise ValueError('unsupported prop asset')
        out[x, y, z] = [x, y, z, state, lines, component, asset]
    return out


def name(state: str) -> str:
    return state_parts(state)[0]


def passable(state: str) -> bool:
    b, _ = state_parts(state)
    return (
        b == 'air'
        or b in RAIL_BLOCKS
        or b.endswith((
            '_door', '_fence_gate', '_sign', '_hanging_sign', '_wall_hanging_sign',
            '_carpet', '_button', '_pressure_plate',
        ))
        or b in {
            'short_grass', 'tall_grass', 'fern', 'large_fern', 'poppy', 'dandelion',
            'cornflower', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley',
            'allium', 'blue_orchid', 'red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip',
            'torch', 'wall_torch', 'redstone_torch', 'redstone_wall_torch',
            'lever', 'ladder', 'vine', 'glow_lichen',
        }
    )


def full_block(state: str) -> bool:
    b, p = state_parts(state)
    if b not in PALETTE or passable(state):
        return False
    if b.endswith('_slab'):
        return p.get('type', 'bottom') == 'double'
    if b.endswith(('_stairs', '_pane', '_bars', '_fence', '_fence_gate', '_wall', '_trapdoor', '_head', '_bed', '_leaves', '_candle')):
        return False
    if b.startswith('potted_') or b in GROUND_FLORA or b in {
        'water', 'lily_pad', 'chain', 'iron_chain', 'lightning_rod',
        'lantern', 'soul_lantern', 'end_rod', 'flower_pot', 'candle', 'cake',
        'composter', 'cauldron', 'water_cauldron', 'hopper', 'lectern',
        'grindstone', 'stonecutter', 'anvil', 'bell', 'scaffolding',
        'campfire', 'soul_campfire', 'daylight_detector', 'lever',
    }:
        return False
    return True


def flush_top(state: str) -> bool:
    b, p = state_parts(state)
    return (
        full_block(state)
        or b == 'scaffolding'
        or (b.endswith('_slab') and p.get('type') in ('top', 'double'))
        or (b.endswith('_stairs') and p.get('half') == 'top')
    )
