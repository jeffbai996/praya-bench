"""Deterministic acceptable reference examples for the 9 art & asset tasks."""
from __future__ import annotations

from typing import Any

from .art import ART_TASKS, INNER, OUTER

# Crisp 5x7 uppercase bitmap font for map-art typography.
_FONT5X7: dict[str, tuple[str, ...]] = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01111', '10000', '10000', '10000', '10000', '10000', '01111'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01111', '10000', '10000', '10111', '10001', '10001', '01111'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('11111', '00100', '00100', '00100', '00100', '00100', '11111'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    '0': ('01110', '10011', '10101', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00110', '01000', '10000', '11111'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('01110', '10000', '11110', '10001', '10001', '10001', '01110'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    ':': ('00000', '00100', '00100', '00000', '00100', '00100', '00000'),
    '-': ('00000', '00000', '00000', '11111', '00000', '00000', '00000'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
}


def _draw_text(
    rects: list[list[Any]],
    text: str,
    x0: int,
    y0: int,
    scale_x: int,
    scale_y: int,
    sym: str,
    gap: int | None = None,
) -> int:
    """Append compact horizontal-run rects for uppercase text; return total pixel width."""
    spacing = scale_x if gap is None else gap
    cx = x0
    for ch in text.upper():
        glyph = _FONT5X7.get(ch, _FONT5X7[' '])
        for row_idx, bits in enumerate(glyph):
            col = 0
            while col < len(bits):
                if bits[col] == '1':
                    start = col
                    while col < len(bits) and bits[col] == '1':
                        col += 1
                    rects.append([cx + start * scale_x, y0 + row_idx * scale_y, (col - start) * scale_x, scale_y, sym])
                else:
                    col += 1
        cx += (3 * scale_x if ch == ' ' else 5 * scale_x) + spacing
    return max(0, cx - x0 - spacing)


def _draw_up_arrow(rects: list[list[Any]], cx: int, y_top: int, h: int, sym: str) -> None:
    """Draw a clean upward highway lane arrow centered at cx."""
    head_h = h // 2
    for dy in range(head_h):
        half_w = 2 + (dy * 14) // max(1, head_h - 1)
        rects.append([cx - half_w, y_top + dy, half_w * 2, 1, sym])
    shaft_w = 10
    rects.append([cx - shaft_w // 2, y_top + head_h, shaft_w, h - head_h, sym])


def _map_fascia_wordmark() -> dict[str, Any]:
    # 256x128 transparent-edge storefront fascia reading "NORTH PIER"
    rects: list[list[Any]] = [
        # Outer dark navy signboard with chamfered corners (leaves edges transparent)
        [16, 18, 224, 92, 'b'],
        [10, 24, 236, 80, 'b'],
        # Subtle warm brass inner border
        [18, 24, 220, 3, 'g'],
        [18, 101, 220, 3, 'g'],
        [18, 24, 3, 80, 'g'],
        [235, 24, 3, 80, 'g'],
        # Accent maritime divider below wordmark
        [28, 89, 200, 3, 'g'],
        [124, 36, 8, 44, 'a'],
    ]
    # "NORTH" across left tile probe [25,44,117,84], "PIER" across right tile probe [139,44,232,84]
    _draw_text(rects, 'NORTH', 26, 46, 3, 5, 'w', gap=3)
    _draw_text(rects, 'PIER', 148, 46, 3, 5, 'w', gap=4)
    return {
        'colors': {
            'b': '#1c2a3a',
            'w': '#ffffff',
            'g': '#d8af38',
            'a': '#3a668a',
        },
        'rects': rects,
    }


def _map_departure_board() -> dict[str, Any]:
    # 128x128 dark OLED transit board with amber indicators and 2 departure rows
    rects: list[list[Any]] = [
        [0, 0, 128, 128, 'b'],
        # Frame header band
        [6, 6, 116, 26, 'p'],
        [6, 32, 116, 2, 'a'],
        # Row 1 & Row 2 subtle dark panels
        [6, 38, 116, 24, 'p'],
        [6, 68, 116, 24, 'p'],
        # Live status amber badges & footer indicator bar
        [10, 14, 6, 10, 'a'],
        [10, 44, 6, 12, 'a'],
        [10, 74, 6, 12, 'a'],
        [10, 104, 26, 10, 'a'],
        [42, 104, 76, 10, 'p'],
    ]
    _draw_text(rects, 'DEPARTURES', 21, 13, 1, 2, 'w', gap=4)
    _draw_text(rects, '01 PIER 2M', 21, 44, 1, 2, 'w', gap=4)
    _draw_text(rects, '02 PORT 6M', 21, 74, 1, 2, 'w', gap=4)
    _draw_text(rects, 'ON TIME', 48, 106, 1, 1, 'w', gap=3)
    return {
        'colors': {
            'b': '#191919',
            'p': '#283138',
            'w': '#ffffff',
            'a': '#d87f33',
        },
        'rects': rects,
    }


def _map_motorway_guide() -> dict[str, Any]:
    # 384x128 dark green motorway overhead gantry guide: AIRPORT | HARBOUR + 2 lane arrows
    rects: list[list[Any]] = [
        [0, 0, 384, 128, 'g'],
        # Crisp white motorway border
        [6, 6, 372, 4, 'w'],
        [6, 118, 372, 4, 'w'],
        [6, 6, 4, 116, 'w'],
        [374, 6, 4, 116, 'w'],
        # Central lane separator
        [190, 14, 4, 100, 'w'],
        # Horizontal header rule
        [14, 64, 170, 3, 'w'],
        [200, 64, 170, 3, 'w'],
    ]
    _draw_text(rects, 'AIRPORT', 24, 20, 4, 5, 'w', gap=3)
    _draw_text(rects, 'HARBOUR', 210, 20, 4, 5, 'w', gap=3)
    _draw_up_arrow(rects, 98, 74, 38, 'w')
    _draw_up_arrow(rects, 286, 74, 38, 'w')
    return {
        'colors': {
            'g': '#1c4d2e',
            'w': '#ffffff',
        },
        'rects': rects,
    }


def _head_parking_meter() -> dict[str, Any]:
    # 64x64 UV: gunmetal housing, LCD display, coin slot, solar top, outer visor hood
    rects: list[list[Any]] = [[x, y, 8, 8, 'm'] for x, y in INNER.values()]
    # Shading & structural seams on sides/back/top/bottom
    for side in ('left', 'right'):
        sx, sy = INNER[side]
        rects.append([sx, sy, 8, 1, 'd'])
        rects.append([sx + 2, sy + 2, 4, 4, 'l'])
    bx, by = INNER['back']
    rects.append([bx + 1, by + 1, 6, 6, 'd'])
    rects.append([bx + 2, by + 2, 4, 4, 'm'])
    tx, ty = INNER['top']
    rects.append([tx + 1, ty + 1, 6, 6, 'd'])
    rects.append([tx + 2, ty + 2, 4, 4, 's'])
    # Front face: dark bezel, bright green LCD, coin slot, red/green buttons
    fx, fy = INNER['front']
    rects.extend([
        [fx + 1, fy + 1, 6, 4, 'd'],
        [fx + 2, fy + 2, 4, 2, 'c'],
        [fx + 2, fy + 6, 2, 1, 'r'],
        [fx + 5, fy + 6, 1, 1, 'c'],
        [fx + 5, fy + 5, 1, 1, 'w'],
    ])
    # Outer relief: protective visor rim on front + top hood (<= 48 px)
    ofx, ofy = OUTER['front']
    rects.extend([
        [ofx + 1, ofy, 6, 1, 'l'],
        [ofx, ofy + 1, 1, 4, 'd'],
        [ofx + 7, ofy + 1, 1, 4, 'd'],
    ])
    otx, oty = OUTER['top']
    rects.append([otx + 1, oty + 6, 6, 2, 'l'])
    return {
        'colors': {
            'm': '#6e777d',
            'l': '#98a3aa',
            'd': '#1f282e',
            's': '#2d4b6e',
            'c': '#4ee08e',
            'r': '#d64545',
            'w': '#f4f7f8',
        },
        'rects': rects,
    }


def _head_hvac_vent() -> dict[str, Any]:
    # 64x64 UV: galvanized steel casing, horizontal dark intake louvres, outer flange & ribs
    rects: list[list[Any]] = [[x, y, 8, 8, 'm'] for x, y in INNER.values()]
    for side in ('left', 'right', 'top', 'bottom'):
        sx, sy = INNER[side]
        rects.append([sx + 1, sy + 1, 6, 6, 'l'])
    bx, by = INNER['back']
    rects.extend([
        [bx + 1, by + 1, 6, 6, 'm'],
        [bx + 2, by + 2, 1, 1, 'd'],
        [bx + 5, by + 2, 1, 1, 'd'],
        [bx + 2, by + 5, 1, 1, 'd'],
        [bx + 5, by + 5, 1, 1, 'd'],
    ])
    fx, fy = INNER['front']
    rects.extend([
        [fx + 1, fy + 1, 6, 6, 'd'],
        [fx + 1, fy + 2, 6, 1, 'l'],
        [fx + 1, fy + 4, 6, 1, 'l'],
        [fx + 1, fy + 6, 6, 1, 'l'],
    ])
    # Outer relief: perimeter flange and louvre blade edges on front + top hood rim
    ofx, ofy = OUTER['front']
    rects.extend([
        [ofx, ofy, 8, 1, 'h'],
        [ofx, ofy + 7, 8, 1, 'h'],
        [ofx + 1, ofy + 2, 6, 1, 'm'],
        [ofx + 1, ofy + 4, 6, 1, 'm'],
    ])
    otx, oty = OUTER['top']
    rects.extend([
        [otx + 1, oty + 1, 6, 1, 'h'],
        [otx + 1, oty + 6, 6, 1, 'h'],
    ])
    return {
        'colors': {
            'm': '#8b959b',
            'l': '#adb7bd',
            'h': '#cfd6da',
            'd': '#1a2024',
        },
        'rects': rects,
    }


def _head_mailbox() -> dict[str, Any]:
    # 64x64 UV: signal-orange street postbox, dark mail slot, white timetable plaque, rain hood
    rects: list[list[Any]] = [[x, y, 8, 8, 'o'] for x, y in INNER.values()]
    tx, ty = INNER['top']
    rects.append([tx + 1, ty + 1, 6, 6, 'h'])
    bx, by = INNER['back']
    rects.append([bx + 2, by + 2, 4, 4, 'd'])
    for side in ('left', 'right'):
        sx, sy = INNER[side]
        rects.append([sx, sy, 8, 1, 'd'])
        rects.append([sx, sy + 7, 8, 1, 'd'])
    fx, fy = INNER['front']
    rects.extend([
        [fx + 1, fy + 1, 6, 2, 'k'],
        [fx + 2, fy + 4, 4, 3, 'w'],
        [fx + 3, fy + 5, 2, 1, 'k'],
    ])
    # Outer relief: rain hood lip above slot + top cap trim (22 px)
    ofx, ofy = OUTER['front']
    rects.extend([
        [ofx + 1, ofy, 6, 1, 'h'],
        [ofx + 1, ofy + 1, 6, 1, 'd'],
    ])
    otx, oty = OUTER['top']
    rects.append([otx + 1, oty + 6, 6, 2, 'h'])
    return {
        'colors': {
            'o': '#e07224',
            'h': '#f29346',
            'd': '#a84c12',
            'k': '#1b1f23',
            'w': '#f7f5ee',
        },
        'rects': rects,
    }


def art_example(task: str) -> dict[str, Any]:
    spec = ART_TASKS[task]
    if spec['track'] == 'loom-banner':
        return {'base': spec['base'], 'layers': [list(layer) for layer in spec['target_layers']]}
    builders = {
        'map-fascia-wordmark': _map_fascia_wordmark,
        'map-departure-board': _map_departure_board,
        'map-motorway-guide': _map_motorway_guide,
        'head-parking-meter': _head_parking_meter,
        'head-hvac-vent': _head_hvac_vent,
        'head-mailbox': _head_mailbox,
    }
    return builders[task]()
