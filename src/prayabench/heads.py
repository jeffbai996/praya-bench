"""Standalone MIT semantic custom-head catalogue and multi-face 8x8 pixel-art definitions.

Provides a semantic prop vocabulary across 15 categories without bundling
any Mojang skin URLs, scraped third-party textures, or runtime imports from any external project.
"""
from __future__ import annotations

from typing import Any

# Post-mounted street furniture heads: must stand on iron_bars, a chain or a glass pane.
POST_MOUNTED_ASSETS: frozenset[str] = frozenset({
    'mailbox_orange',
    'mailbox_blue',
    'parking_meter',
})

# Explicitly banned exit-sign heads per the acceptance rules (only emergency_exit_light_caged is accepted).
BANNED_HEADS: frozenset[str] = frozenset({
    'exit_sign',
    'emergency_exit',
    'emergency_exit_sign',
})

# Shorthand aliases accepted from Builder / generator conventions -> canonical asset ID.
HEAD_ALIASES: dict[str, str] = {
    'cash_register': 'pos_terminal',
    'pos': 'pos_terminal',
    'register': 'pos_terminal',
    'monitor': 'computer_monitor',
    'pc_monitor': 'computer_monitor',
    'computer': 'desktop_pc',
    'cctv_camera': 'security_camera',
    'cctv': 'security_camera',
    'camera': 'security_camera',
    'coffee_machine': 'coffee_maker',
    'espresso': 'espresso_machine',
    'sbux_cup_1': 'cup_coffee',
    'sbux_cup_2': 'latte_cup',
    'coffee_cup': 'cup_coffee',
    'cheesecake_strawberry': 'cheesecake',
    'cake_slice': 'cheesecake',
    'pastry': 'croissant',
    'bread': 'bread_loaf',
    'mailbox': 'mailbox_orange',
    'post_box': 'mailbox_orange',
    'aed': 'defibrillator',
    'defib': 'defibrillator',
    'rx_bottle': 'medicine_pillbottle',
    'medicine_pillbottle_2': 'medicine_pillbottle',
    'tv_green_heart_monitor': 'heart_monitor',
    'sydney_transport_opal_card_reader': 'ticket_validator',
    'opal_reader': 'ticket_validator',
    'fare_reader': 'card_reader',
    'clock_tram_stop': 'tram_clock',
    'clock_white': 'wall_clock',
    'office_phone': 'telephone',
    'office_printer': 'printer',
    'plant': 'plant_pot',
    'potted_plant': 'plant_pot',
    'flower_pot': 'plant_pot',
    'books': 'book_stack',
    'hand_dryer': 'hand_dryer_white',
}


def _box_head(
    cat: str,
    palette: dict[str, str],
    front: tuple[str, ...],
    side: tuple[str, ...] | None = None,
    top: tuple[str, ...] | None = None,
    back: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    s = side or tuple('b' + 'm' * 6 + 'b' if 0 < r < 7 else 'b' * 8 for r in range(8))
    t = top or tuple('b' + 't' * 6 + 'b' if 0 < r < 7 else 'b' * 8 for r in range(8))
    bk = back or s
    return {
        'category': cat,
        'palette': palette,
        'faces': {'front': front, 'left': s, 'right': s, 'top': t, 'back': bk},
    }


def _appliance(cat: str, body: str, trim: str, top_c: str, accent1: str, accent2: str, front_rows: tuple[str, ...]) -> dict[str, Any]:
    pal = {'b': trim, 'm': body, 't': top_c, 'a': accent1, 'c': accent2, 'k': '#1b2026', 'w': '#f4f6f7'}
    return _box_head(cat, pal, front_rows)


def _crate(cat: str, wood_dark: str, wood_mid: str, item_main: str, item_hi: str) -> dict[str, Any]:
    pal = {'b': wood_dark, 'm': wood_mid, 't': item_main, 'a': item_hi, 'c': '#3d6b35'}
    front = (
        'taaaaaat',
        'atttttta',
        'bbbbbbbb',
        'bmmmmmmb',
        'bbbbbbbb',
        'bmmmmmmb',
        'bbbbbbbb',
        'bmmmmmmb',
    )
    top = (
        'bbbbbbbb',
        'btatattb',
        'batatttb',
        'bttatacb',
        'batttatb',
        'bttacatb',
        'btattttb',
        'bbbbbbbb',
    )
    return _box_head(cat, pal, front, side=front, top=top, back=front)


HEAD_CATALOG: dict[str, dict[str, Any]] = {
    # --- Commercial & POS ---
    'pos_terminal': _appliance(
        'commercial', '#333b42', '#1f252b', '#465059', '#49d49d', '#e5c158',
        ('bbbbbbbb', 'bkkkkkkb', 'bkaaaakb', 'bkaaaakb', 'bmmmmmmb', 'bmccccmb', 'bmwwwwmb', 'bbbbbbbb'),
    ),
    'card_reader': _appliance(
        'commercial', '#2b3238', '#191e22', '#3d464e', '#46c8e8', '#52d681',
        ('bbbbbbbb', 'bmmmmmmb', 'bkkaakkb', 'bkkaakkb', 'bmmmmmmb', 'bmccccmb', 'bmkwkmkb', 'bbbbbbbb'),
    ),
    'atm_screen': _appliance(
        'commercial', '#3a4c5e', '#22303d', '#4f6478', '#5cc8ff', '#f0b429',
        ('bbbbbbbb', 'bwaaaawb', 'bkaaaakb', 'bkaaaakb', 'bmmmmmmb', 'bmkkkkmb', 'bmccccmb', 'bbbbbbbb'),
    ),
    'shopping_basket': _appliance(
        'commercial', '#c9382b', '#8f2219', '#24292e', '#f2d16b', '#f4f6f7',
        ('bttttttb', 'bbbbbbbb', 'bmwmwmwb', 'bmmmmmmb', 'bmwmwmwb', 'bmmmmmmb', 'bmwmwmwb', 'bbbbbbbb'),
    ),
    'barcode_scanner': _appliance(
        'commercial', '#2e343b', '#1b1f24', '#414952', '#e04848', '#9aa5b1',
        ('bbbbbbbb', 'bkkkkkkb', 'bkaaaakb', 'bkkkkkkb', 'bbmmmmbb', 'bbmccmbb', 'bbmmmmbb', 'bbbbbbbb'),
    ),

    # --- Drinks & Cafe ---
    'coffee_maker': _appliance(
        'appliances', '#3b4046', '#212529', '#b8c2cc', '#d9534f', '#f5f7f8',
        ('bttttttb', 'bmmammcb', 'bkkkkkkb', 'bkcccckb', 'bkcwwckb', 'bkcwwckb', 'bttttttb', 'bbbbbbbb'),
    ),
    'espresso_machine': _appliance(
        'appliances', '#c7d0d8', '#68737d', '#dfe5ea', '#c94a38', '#2a3036',
        ('bttttttb', 'bmammamb', 'bccccccb', 'bmckkcmb', 'bmwwwwmb', 'bmwwwwmb', 'bttttttb', 'bbbbbbbb'),
    ),
    'coffee_grinder': _appliance(
        'appliances', '#2e3338', '#1b1e22', '#6b4a2b', '#c48f5a', '#d8dee4',
        ('bttttttb', 'btaaaatb', 'bttttttb', 'bmmmmmmb', 'bmccccmb', 'bmkwwkmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'cup_coffee': _appliance(
        'drinks', '#f2efe9', '#c9c2b8', '#6f4728', '#2d6a4f', '#ffffff',
        ('cccccccc', 'bttttttb', 'bmmmmmmb', 'bmaaaamb', 'bmaaaamb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'latte_cup': _appliance(
        'drinks', '#e8dfd1', '#b8ab99', '#c89b6e', '#f7f3eb', '#8c5a32',
        ('bbbbbbbb', 'btatatab', 'bmmmmmmb', 'bmccccmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'boba_cup': _appliance(
        'drinks', '#e6be8a', '#b58952', '#f5ece0', '#2b2118', '#d96b43',
        ('bbbccbbb', 'tttttttt', 'bmmmmmmb', 'bmmmmmmb', 'bmamamab', 'bamamamb', 'bkakakab', 'bbbbbbbb'),
    ),
    'teapot': _appliance(
        'drinks', '#4f6d5a', '#314739', '#678a74', '#d8cfc0', '#243329',
        ('bbbttbbb', 'bttttttb', 'bmmmmmmb', 'bmaaaamb', 'bmmmmmmb', 'bmccccmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'tea_tin': _appliance(
        'drinks', '#2f5d50', '#1d3d34', '#d4af37', '#f4ecd8', '#a33b2e',
        ('tttttttt', 'bbbbbbbb', 'bmmmmmmb', 'bmaaaamb', 'bmacacmb', 'bmaaaamb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'water_cooler': _appliance(
        'appliances', '#e6eaee', '#9aa5b1', '#7cc6fe', '#3b82f6', '#ef4444',
        ('bttttttb', 'btaaaatb', 'bttttttb', 'bmmmmmmb', 'bmckkcmb', 'bmkkkkmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),

    # --- Food & Bakery ---
    'bread_loaf': _appliance(
        'food', '#c98a4b', '#8f5b28', '#dda15e', '#f3d5a5', '#6f4518',
        ('bttttttb', 'taaaaaat', 'tmmmmmmt', 'bmaaaamb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'croissant': _appliance(
        'food', '#d99441', '#9c6321', '#eab364', '#f6d89e', '#6e4212',
        ('bbbbbbbb', 'bttttttb', 'taaaaaat', 'tmmmmmmt', 'bmaaaamb', 'bbmmmmbb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'cheesecake': _appliance(
        'food', '#f6e7c1', '#c79f62', '#d94343', '#fff8e7', '#8c5e2a',
        ('bttttttb', 'taaaaaat', 'aaaaaaaa', 'mmmmmmmm', 'mmmmmmmm', 'cccccccc', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'pastry_box': _appliance(
        'food', '#f4ede2', '#cdbba3', '#f8f4ec', '#c85a32', '#7a9e7e',
        ('tttttttt', 'tttttttt', 'bmaaaamb', 'baaaaaab', 'bmmmmmmb', 'bmccccmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'ramen_bowl': _appliance(
        'food', '#c83e37', '#7a1f1b', '#e8b960', '#f7f4ea', '#5c9ead',
        ('taaaaaat', 'atttttta', 'bbbbbbbb', 'bmmmmmmb', 'bmccccmb', 'bmmmmmmb', 'bbmmmmbb', 'bbbbbbbb'),
    ),
    'bento_box': _appliance(
        'food', '#262626', '#141414', '#e07a5f', '#f4f1de', '#81b29a',
        ('bbbbbbbb', 'btaaaacb', 'btaaaacb', 'bbbbbbbb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'sushi_platter': _appliance(
        'food', '#2c302e', '#171a18', '#f26a4b', '#ffffff', '#4d7c4a',
        ('bbbbbbbb', 'btatatcb', 'baaaaaab', 'bccccccb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),

    # --- Groceries & Market ---
    'apple_basket': _crate('groceries', '#7c532f', '#a47143', '#cc3333', '#e85d4a'),
    'orange_crate': _crate('groceries', '#7c532f', '#a47143', '#e67e22', '#f39c12'),
    'produce_crate': _crate('groceries', '#6e4b2a', '#96683e', '#4d9b45', '#82c95b'),
    'cabbage_head': _appliance(
        'groceries', '#5fa34d', '#3e7331', '#7ec468', '#bce3a8', '#2d5722',
        ('bttttttb', 'taaaaaat', 'tmmmammt', 'bmammamb', 'bmmmammt', 'bmmmmmmb', 'bbmmmmbb', 'bbbbbbbb'),
    ),
    'watermelon': _appliance(
        'groceries', '#2f6e36', '#1d4a22', '#3f8a47', '#65b36b', '#16381a',
        ('btctctcb', 'mamasama'.replace('s', 'm'), 'cmcmcmcm', 'mamasama'.replace('s', 'm'),
         'cmcmcmcm', 'mamasama'.replace('s', 'm'), 'cmcmcmcm', 'btctctcb'),
    ),
    'cheese_wheel': _appliance(
        'groceries', '#e6b43b', '#b8881e', '#f2c957', '#f9df8a', '#8f6712',
        ('bttttttb', 'taaaaaat', 'mmmmmmmm', 'mmammmam', 'mmmmammm', 'mmmmmmmm', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'milk_carton': _appliance(
        'groceries', '#f2f6fa', '#c5d1dc', '#3b82c4', '#5aa4e6', '#ffffff',
        ('bbttttbb', 'bttttttb', 'bmmmmmmb', 'baaaaaab', 'baaaaaab', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'cereal_box': _appliance(
        'groceries', '#e09f3e', '#9e6618', '#d6453d', '#fff3b0', '#335c67',
        ('tttttttt', 'bmmmmmmb', 'btaaaatb', 'bmaaaamb', 'bmccccmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'rice_sack': _appliance(
        'groceries', '#d8cbb5', '#a6967c', '#e6dcc8', '#b83b2b', '#4d6b45',
        ('bbttttbb', 'bttttttb', 'bmmmmmmb', 'bmaaaamb', 'bmccccmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'spice_jars': _appliance(
        'groceries', '#d9e4ec', '#8b99a4', '#8f4724', '#c95b2b', '#d4a72c',
        ('bbttttbb', 'bbbbbbbb', 'bmacmcmb', 'bmacmcmb', 'bmacmcmb', 'bmacmcmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'jar_pickles': _appliance(
        'groceries', '#6c9a4b', '#476b2f', '#c9d1d8', '#9ec46e', '#2d471d',
        ('bbttttbb', 'bttttttb', 'bmaaaamb', 'bmcmcmmb', 'bmacmcmb', 'bmcmcmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'salmon_fillet': _crate('groceries', '#cfd8df', '#9fb0bd', '#e87458', '#f9c2b2'),
    'crab_ice': _crate('groceries', '#cfd8df', '#9fb0bd', '#c94332', '#e8f4fa'),

    # --- Appliances & HVAC ---
    'ac_unit': _appliance(
        'appliances', '#dce1e5', '#8c969e', '#e9edf0', '#2b3137', '#58636d',
        ('bbbbbbbb', 'bkkkkrmb'.replace('r', 'm'), 'bkkkkmmb', 'bkakkmmb', 'bkkkkccb', 'bkkkkmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'wall_vent': _appliance(
        'appliances', '#adb6bd', '#6c757d', '#ced4da', '#212529', '#dee2e6',
        ('bbbbbbbb', 'bkkkkkkb', 'bccccccb', 'bkkkkkkb', 'bccccccb', 'bkkkkkkb', 'bccccccb', 'bbbbbbbb'),
    ),
    'microwave': _appliance(
        'appliances', '#dde2e6', '#7d8790', '#eef1f4', '#22282e', '#f0ad4e',
        ('bbbbbbbb', 'bmmmmmmb', 'bkkaakwb', 'bkkaakwb', 'bkkkkkwb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'toaster': _appliance(
        'appliances', '#c8d0d8', '#6e7780', '#2b3036', '#d97736', '#495057',
        ('bbkkkkbb', 'bmmmmmmb', 'bmmmmckb', 'bmmmmakb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'rice_cooker': _appliance(
        'appliances', '#f1f3f5', '#9aa3ab', '#dee2e6', '#e05347', '#343a40',
        ('bbttttbb', 'bttttttb', 'bmmmmmmb', 'bmckkcmb', 'bmcaacmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'mini_fridge': _appliance(
        'appliances', '#e9ecef', '#868e96', '#f8f9fa', '#495057', '#adb5bd',
        ('bbbbbbbb', 'bmmmmamb', 'bmmmmamb', 'bccccccb', 'bmmmmamb', 'bmmmmamb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'kettle': _appliance(
        'appliances', '#cfd6dc', '#646d75', '#212529', '#38bdf8', '#495057',
        ('bbttttbb', 'bmmmmmmb', 'bmmaammk', 'bmmaammk', 'bmmaammb', 'bmmmmmmb', 'bttttttb', 'bbbbbbbb'),
    ),

    # --- Electronics & Office ---
    'computer_monitor': _appliance(
        'electronics', '#2b3036', '#171a1e', '#383e46', '#4da8da', '#d8eef9',
        ('bbbbbbbb', 'baaaaaab', 'baccccab', 'baaaaaab', 'baaaaaab', 'bbbbbbbb', 'bbbmmbbb', 'bbmmmmbb'),
    ),
    'laptop': _appliance(
        'electronics', '#8d97a1', '#4a525a', '#adb6bf', '#3b82f6', '#1f2429',
        ('bbbbbbbb', 'bkaaaakb', 'bkaaaakb', 'bkaaaakb', 'bbbbbbbb', 'mmmmmmmm', 'mccccccm', 'bbbbbbbb'),
    ),
    'desktop_pc': _appliance(
        'electronics', '#2b3035', '#16191d', '#3a4047', '#22c55e', '#64748b',
        ('bbbbbbbb', 'bmccccmb', 'bmkkkkmb', 'bmmmammm'[:8], 'bmkkkkmb', 'bmkkkkmb', 'bmccccmb', 'bbbbbbbb'),
    ),
    'printer': _appliance(
        'electronics', '#dee3e8', '#7f8993', '#ffffff', '#2b3035', '#38bdf8',
        ('bbttttbb', 'bmmmmmmb', 'bmkkkkmb', 'bmcaacmb', 'bmmmmmmb', 'bbttttbb', 'bbttttbb', 'bbbbbbbb'),
    ),
    'telephone': _appliance(
        'electronics', '#2d3339', '#191d21', '#3e464e', '#94a3b8', '#e2e8f0',
        ('bbbbbbbb', 'bkkmmmmb', 'bkkmccmb', 'bkkmccmb', 'bkkmmmmb', 'bkkmaamb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'server_unit': _appliance(
        'electronics', '#22272c', '#121518', '#30373e', '#22c55e', '#38bdf8',
        ('bbbbbbbb', 'bkakckkb', 'bmmmmmmb', 'bkckakkb', 'bmmmmmmb', 'bkakakkb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'radio_transceiver': _appliance(
        'electronics', '#37414a', '#1e2429', '#4b5661', '#f59e0b', '#10b981',
        ('bbbbbbbb', 'bkaaaakb', 'bkcccckb', 'bmmmmmmb', 'bmkwkwmb', 'bmkkkkmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'router': _appliance(
        'electronics', '#262b30', '#15181b', '#343b42', '#34d399', '#60a5fa',
        ('bbbbbbbb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb', 'bkakckab', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'wall_clock': _appliance(
        'electronics', '#f8f9fa', '#343a40', '#495057', '#212529', '#d9480f',
        ('bbttttbb', 'bmmmmmmb', 'bmmammbb'[:8], 'bmmammmb', 'bmmaacmb', 'bmmmmmmb', 'bmmmmmmb', 'bbttttbb'),
    ),
    'speaker': _appliance(
        'electronics', '#2a2e33', '#16181b', '#3a3f46', '#6c757d', '#adb5bd',
        ('bbbbbbbb', 'bmkkkkmb', 'bkaccakb', 'bkcwwckb', 'bkaccakb', 'bmkkkkmb', 'bmkkkkmb', 'bbbbbbbb'),
    ),

    # --- Medical & Pharmacy ---
    'defibrillator': _appliance(
        'medical', '#2ca568', '#1b6e44', '#38b877', '#ffffff', '#e03e3e',
        ('bbbbbbbb', 'bmmaammb', 'bmaaaamb', 'bmacacmb', 'bmaaaamb', 'bmmaammb', 'bmccccmb', 'bbbbbbbb'),
    ),
    'first_aid_kit': _appliance(
        'medical', '#f4f6f8', '#b8c2cc', '#ffffff', '#d93838', '#9aa5b1',
        ('bbbbbbbb', 'bmmmmmmb', 'bmmaammb', 'bmaaaamb', 'bmaaaamb', 'bmmaammb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'heart_monitor': _appliance(
        'medical', '#263038', '#161c21', '#384652', '#34d399', '#f43f5e',
        ('bbbbbbbb', 'bkkkkkkb', 'bkakkkkb', 'bkaaaakb', 'bkkkckkb', 'bmmmmmmb', 'bmwwwwmb', 'bbbbbbbb'),
    ),
    'microscope': _appliance(
        'medical', '#dce2e8', '#5c6670', '#252b31', '#38bdf8', '#94a3b8',
        ('bbbttbbb', 'bbbttbbb', 'bbmmmmbb', 'bbmaambb', 'bbkkkkbb', 'bbbmmbbb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'medicine_pillbottle': _appliance(
        'medical', '#e07a2b', '#9e4f14', '#ffffff', '#f8fafc', '#2563eb',
        ('tttttttt', 'tttttttt', 'bmmmmmmb', 'baaaaaab', 'baccccab', 'baaaaaab', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'rx_mortar': _appliance(
        'medical', '#eceff2', '#9aa4ae', '#d4d9df', '#8c6239', '#ffffff',
        ('bbbbaccb', 'bbbaccbb', 'bttttttb', 'bmmmmmmb', 'bmaaaamb', 'bmmmmmmb', 'bbmmmmbb', 'bbbbbbbb'),
    ),

    # --- Safety & Code ---
    'emergency_exit_light_caged': _appliance(
        'safety', '#228b57', '#7b8794', '#9aa5b1', '#e6fffa', '#166534',
        ('bbbbbbbb', 'bmabamab', 'baaaaaab', 'bmabamab', 'baaaaaab', 'bmabamab', 'bccccccb', 'bbbbbbbb'),
    ),
    'fire_extinguisher': _appliance(
        'safety', '#c92a2a', '#7f1d1d', '#2b3035', '#f8f9fa', '#eab308',
        ('bbttttbb', 'bbtcckbb', 'bbmmmmbb', 'bmaaaamb', 'bmacccmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'fire_alarm_pull': _appliance(
        'safety', '#d63333', '#8c1d1d', '#e04848', '#ffffff', '#1f2429',
        ('bbbbbbbb', 'bmaaaamb', 'bmmmmmmb', 'bmwwwwmb', 'bmkkkkmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'security_camera': _appliance(
        'safety', '#e2e6ea', '#6c757d', '#eef1f4', '#181c20', '#ef4444',
        ('tttttttt', 'bmmmmmmb', 'bmkkkkmb', 'bmkcakmb', 'bmkkkkmb', 'bmmmmmmb', 'bbbbbbbb', 'bbbbbbbb'),
    ),
    'smoke_detector': _appliance(
        'safety', '#f1f3f5', '#adb5bd', '#ffffff', '#ef4444', '#868e96',
        ('bbmmmmbb', 'bmmmmmmb', 'bmccccmb', 'bmcmmcmb', 'bmcmacmb', 'bmccccmb', 'bmmmmmmb', 'bbmmmmbb'),
    ),
    'electrical_panel': _appliance(
        'safety', '#6c757d', '#495057', '#868e96', '#eab308', '#212529',
        ('bbbbbbbb', 'bmmmmmmb', 'bmmaammb', 'bmkkkkmb', 'bmkkkkmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'hard_hat': _appliance(
        'safety', '#eab308', '#a16207', '#facc15', '#fef08a', '#1f2937',
        ('bbttttbb', 'btaaaatb', 'bmmmmmmb', 'bmmmmmmb', 'mmmmmmmm', 'bbbbbbbb', 'kkkkkkkk', 'kkkkkkkk'),
    ),

    # --- Transit & Street ---
    'ticket_validator': _appliance(
        'transit', '#255c8a', '#163a59', '#f59e0b', '#38bdf8', '#22c55e',
        ('tttttttt', 'bmmmmmmb', 'bkaaaakb', 'bkaaaakb', 'bmmmmmmb', 'bmccccmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'mailbox_orange': _appliance(
        'street', '#e07224', '#a84c12', '#f29346', '#1b1f23', '#f7f5ee',
        ('tttttttt', 'baaaaaak'[:8], 'baaaaaab', 'bmmmmmmb', 'bmccccmb', 'bmcmmcmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'mailbox_blue': _appliance(
        'street', '#24589e', '#163869', '#3872bd', '#181c22', '#f4f6f8',
        ('tttttttt', 'baaaaaab', 'baaaaaab', 'bmmmmmmb', 'bmccccmb', 'bmcmmcmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'parking_meter': _appliance(
        'street', '#6e777d', '#1f282e', '#2d4b6e', '#4ee08e', '#d64545',
        ('bbbbbbbb', 'bkkkkkkb', 'bkaaaakb', 'bkaaaakb', 'bmmmmmmb', 'bmccwakb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'fire_hydrant': _appliance(
        'street', '#c9302c', '#7f1d1d', '#e04b47', '#d1d5db', '#9ca3af',
        ('bbttttbb', 'bmmmmmmb', 'ammmmmma', 'ammmammm'[:8], 'bmmmmmmb', 'bccccccb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'trash_bin': _appliance(
        'street', '#3d4852', '#22292f', '#1b2025', '#9aa5b1', '#606f7b',
        ('bttttttb', 'bkkkkkkb', 'bbbbbbbb', 'bmcmcmmb', 'bmcmcmmb', 'bmcmcmmb', 'bmcmcmmb', 'bbbbbbbb'),
    ),
    'recycling_bin': _appliance(
        'street', '#1d6fa5', '#124669', '#153a54', '#ffffff', '#63b3ed',
        ('bttttttb', 'bkkkkkkb', 'bbbbbbbb', 'bmmammbb'[:8], 'bmamammb', 'bmaaaamb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'bollard_light': _appliance(
        'street', '#2f363d', '#1b1f23', '#3d464f', '#fde68a', '#fef3c7',
        ('bbbbbbbb', 'baaaaaab', 'bccccccb', 'baaaaaab', 'bmmmmmmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
    'tram_clock': _appliance(
        'transit', '#1f2933', '#10161c', '#323f4b', '#f8fafc', '#f59e0b',
        ('bbbbbbbb', 'baaaaaab', 'baacaaab', 'baacccab', 'baaaaaab', 'baaaaaab', 'bbbbbbbb', 'bbbbbbbb'),
    ),

    # --- Bathroom ---
    'soap_dispenser': _appliance(
        'bathroom', '#eceff2', '#9aa4ae', '#cfd6de', '#60a5fa', '#475569',
        ('bbbttbbb', 'bmmmmmmb', 'bmmmmmmb', 'bmaaaamb', 'bmaaaamb', 'bmmmmmmb', 'bbbccbbb', 'bbbbbbbb'),
    ),
    'hand_dryer_white': _appliance(
        'bathroom', '#f4f6f8', '#9aa5b1', '#ffffff', '#38bdf8', '#334155',
        ('tttttttt', 'bmmmmmmb', 'bmmmmmmb', 'bmccccmb', 'bmcaacmb', 'bmmmmmmb', 'bkkkkkkb', 'bbbbbbbb'),
    ),
    'paper_towel_dispenser': _appliance(
        'bathroom', '#dce2e8', '#7d8894', '#eef2f6', '#ffffff', '#334155',
        ('bbbbbbbb', 'bmmmmmmb', 'bmmmmmmb', 'bmccccmb', 'bmmmmmmb', 'baaaaaab', 'baaaaaab', 'bbbbbbbb'),
    ),
    'toilet_paper_roll': _appliance(
        'bathroom', '#f8fafc', '#cbd5e1', '#e2e8f0', '#64748b', '#ffffff',
        ('bbbbbbbb', 'bccccccb', 'bcmmmmcb', 'bcmaamcb', 'bcmmmmcb', 'bccccccb', 'bccccccb', 'bbbbbbbb'),
    ),

    # --- Furniture, Books & Plants ---
    'globe': _appliance(
        'furniture', '#2b7bbb', '#8c6239', '#3b95db', '#57a752', '#d4af37',
        ('bbttttbb', 'btaaaatb', 'btmmaatb', 'baammttb', 'btaammtb', 'bbttttbb', 'bbbccbbb', 'bbbbbbbb'),
    ),
    'book_stack': _appliance(
        'furniture', '#8c2d2d', '#3d5a80', '#e09f3e', '#f4f1de', '#2f5d50',
        ('tttttttt', 'taaaaaat', 'bbbbbbbb', 'baaaaaab', 'cccccccc', 'caaaaaac', 'mmmmmmmm', 'maaaaaam'),
    ),
    'desk_lamp': _appliance(
        'furniture', '#d4a72c', '#7c5d12', '#e6be4c', '#fef3c7', '#2b3035',
        ('bbttttbb', 'bmmmmmmb', 'baaaaaab', 'baaaaaab', 'bbbkkbbb', 'bbbkkbbb', 'bbmmmmbb', 'bbbbbbbb'),
    ),
    'plant_pot': _appliance(
        'plants', '#b35c38', '#7c3d23', '#3f7d3a', '#5ca854', '#4a3525',
        ('baatattb', 'atttttta', 'btaaaatb', 'bccccccb', 'bmmmmmmb', 'bmmmmmmb', 'bbmmmmbb', 'bbbbbbbb'),
    ),
    'bonsai_pot': _appliance(
        'plants', '#468c41', '#2c5e28', '#5fa858', '#6b4423', '#36454f',
        ('btaaaatb', 'atttttta', 'bttttttb', 'bbbccbbb', 'bbbccbbb', 'kkkkkkkk', 'kkkkkkkk', 'bbbbbbbb'),
    ),
    'toolbox': _appliance(
        'furniture', '#c9342b', '#7f1d1d', '#dc453b', '#cbd5e1', '#1f2429',
        ('bbkkkkbb', 'tttttttt', 'bmmmmmmb', 'baaaaaab', 'bmmkkmmb', 'bmmmmmmb', 'bmmmmmmb', 'bbbbbbbb'),
    ),
}

ASSETS: tuple[str, ...] = tuple(HEAD_CATALOG.keys())


def resolve_head_name(raw: str | None) -> str | None:
    """Resolve canonical head name or shorthand alias; return None if unknown."""
    if raw is None or not isinstance(raw, str):
        return None
    clean = raw.strip().lower().replace('-', '_').replace(' ', '_')
    if clean in HEAD_ALIASES:
        clean = HEAD_ALIASES[clean]
    if clean in HEAD_CATALOG or clean in BANNED_HEADS:
        return clean
    return None


def head_faces(asset: str | None) -> tuple[dict[str, str], dict[str, tuple[str, ...]]]:
    """Return ``(palette, faces)`` 8x8 pixel-art definition for ``asset``."""
    canon = resolve_head_name(asset) if asset else None
    entry = HEAD_CATALOG.get(canon or '')
    if entry is None:
        fallback_pal = {'b': '#6e6556', 'm': '#918770', 't': '#a89d84'}
        grid = tuple('b' + 'm' * 6 + 'b' if 0 < r < 7 else 'b' * 8 for r in range(8))
        return fallback_pal, {'front': grid, 'left': grid, 'right': grid, 'top': grid, 'back': grid}
    return entry['palette'], entry['faces']
