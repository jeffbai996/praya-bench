"""Auto-framing isometric SVG renderer with pixel-art custom heads, item frames and legible sign text."""
import html
from typing import Any, Sequence

from .heads import head_faces
from .scene import RAIL_BLOCKS, full_block, state_parts

# Camera visible cardinal faces per view index (0=SE, 1=SW, 2=NW, 3=NE).
_VISIBLE_SIDES = (
    frozenset({'east', 'south'}),
    frozenset({'south', 'west'}),
    frozenset({'west', 'north'}),
    frozenset({'north', 'east'}),
)
_ROT_TO_FACING = ('south', 'west', 'north', 'east')


def colour(b: str) -> tuple[int, int, int]:
    colors = {
        'white': (225, 225, 218), 'light_gray': (169, 174, 171), 'gray': (66, 72, 76), 'black': (33, 37, 41),
        'red': (166, 64, 53), 'orange': (206, 125, 53), 'yellow': (222, 188, 66), 'green': (74, 120, 68),
        'lime': (128, 165, 72), 'blue': (58, 91, 145), 'light_blue': (129, 172, 192), 'cyan': (70, 139, 142),
        'purple': (130, 93, 150), 'magenta': (172, 105, 150), 'pink': (208, 153, 167), 'brown': (112, 81, 59),
    }
    if b == 'air':
        return (140, 181, 195)
    if b == 'water':
        return (74, 134, 178)
    if b in ('flowering_azalea', 'flowering_azalea_leaves'):
        return (124, 132, 92)
    if 'leaves' in b or b in ('grass_block', 'moss_block', 'moss_carpet', 'azalea', 'fern', 'large_fern', 'bush', 'sweet_berry_bush', 'short_grass', 'tall_grass', 'lily_pad', 'vine'):
        return (72, 116, 62)
    if any(t in b for t in ('poppy', 'dandelion', 'flower', 'cornflower', 'bluet', 'peony', 'rose_bush', 'oxeye_daisy', 'lily_of_the_valley', 'allium', 'orchid', 'tulip', 'lilac', 'sunflower')):
        return (192, 148, 115)
    if b == 'tinted_glass':
        return (78, 76, 86)
    if 'glass' in b:
        for color in sorted(colors, key=len, reverse=True):
            if b.startswith(color + '_'):
                rc, gc, bc = colors[color]
                return ((rc + 125) // 2, (gc + 159) // 2, (bc + 169) // 2)
        return (125, 159, 169)
    if b == 'powered_rail':
        return (206, 164, 62)
    if b in RAIL_BLOCKS:
        return (138, 130, 118)
    if b == 'daylight_detector':
        return (62, 88, 128)
    if 'prismarine' in b:
        return (94, 154, 145)
    if 'oxidized' in b and 'copper' in b:
        return (83, 153, 132)
    if 'weathered' in b and 'copper' in b:
        return (108, 148, 116)
    if 'copper' in b or b == 'lightning_rod':
        return (184, 108, 82)
    if b == 'coal_ore':
        return (72, 75, 78)
    if b == 'iron_ore':
        return (156, 138, 124)
    if 'bamboo' in b:
        return (196, 178, 88)
    if 'cherry' in b:
        return (203, 145, 148)
    if 'mangrove' in b:
        return (119, 58, 52)
    if 'acacia' in b:
        return (173, 98, 57)
    if 'jungle' in b:
        return (163, 119, 84)
    if 'dark_oak' in b:
        return (78, 55, 35)
    if 'spruce' in b:
        return (114, 84, 52)
    if 'birch' in b:
        return (212, 196, 150)
    if any(t in b for t in ('oak', 'barrel', 'bookshelf', 'lectern', 'chest', 'crafting_table', 'composter', 'loom', 'cartography_table')):
        return (166, 130, 82)
    if 'mud' in b:
        return (138, 114, 98)
    if b == 'clay':
        return (160, 166, 179)
    if 'granite' in b:
        return (154, 109, 93)
    if 'mossy_' in b:
        return (112, 126, 104)
    if 'red_sand' in b:
        return (186, 103, 56)
    if 'sand' in b:
        return (216, 203, 155)
    if 'diorite' in b:
        return (205, 205, 202)
    if 'andesite' in b or b == 'gravel' or 'tuff' in b:
        return (132, 136, 136)
    if 'deepslate' in b or 'blackstone' in b or 'basalt' in b:
        return (57, 63, 67)
    if 'quartz' in b or b in ('calcite', 'bone_block'):
        return (226, 223, 209)
    if b in ('bricks', 'brick_wall') or b.startswith('brick_'):
        return (158, 102, 84)
    if b in ('iron_block', 'iron_door', 'iron_trapdoor', 'iron_bars', 'cauldron', 'water_cauldron', 'hopper', 'anvil', 'tripwire_hook'):
        return (188, 193, 196)
    if b in ('sea_lantern', 'verdant_froglight', 'pearlescent_froglight'):
        return (195, 224, 218)
    if any(t in b for t in ('lantern', 'torch', 'end_rod', 'glowstone', 'redstone_lamp', 'shroomlight', 'ochre_froglight', 'campfire')):
        return (238, 209, 130)
    if b in ('dirt', 'rooted_dirt', 'podzol', 'coarse_dirt'):
        return (120, 89, 61)
    if b in ('smoker', 'furnace', 'blast_furnace', 'stonecutter', 'grindstone'):
        return (112, 112, 114)
    for color in sorted(colors, key=len, reverse=True):
        if b.startswith(color + '_'):
            return colors[color]
    if b == 'terracotta':
        return (155, 103, 79)
    if 'head' in b:
        return (145, 135, 112)
    return (143, 147, 145)


def shape(b: str, p: dict[str, str]) -> list[tuple[float, float, float, float, float, float]]:
    if b == 'snow':
        layers = p.get('layers', '1')
        height = min(8, max(1, int(layers))) / 8 if layers.isdigit() else .125
        return [(0, 0, 0, 1, height, 1)]
    if b == 'daylight_detector':
        return [(0, 0, 0, 1, .38, 1)]
    if b == 'hopper':
        return [(.08, .45, .08, .92, 1, .92), (.3, .14, .3, .7, .45, .7), (.4, 0, .4, .6, .14, .6)]
    if b.endswith('shulker_box'):
        return [(.02, .02, .02, .98, .48, .98), (.02, .5, .02, .98, .98, .98)]
    if b == 'water':
        return [(0, 0, 0, 1, .88, 1)]
    if b in RAIL_BLOCKS:
        return [(.1, 0, .1, .9, .08, .9)]
    if b.endswith('_slab'):
        t = p.get('type', 'bottom')
        return [(0, .5 if t == 'top' else 0, 0, 1, 1 if t != 'bottom' else .5, 1)]
    if b.endswith('_stairs'):
        up = p.get('half') == 'top'
        parts = [(0, .5 if up else 0, 0, 1, 1 if up else .5, 1)]
        f = p.get('facing', 'north')
        x0, x1 = (.5, 1) if f == 'east' else (0, .5) if f == 'west' else (0, 1)
        z0, z1 = (0, .5) if f == 'north' else (.5, 1) if f == 'south' else (0, 1)
        return parts + [(x0, 0 if up else .5, z0, x1, .5 if up else 1, z1)]
    if b.endswith('_wall_hanging_sign'):
        f = p.get('facing', 'north')
        if f in ('north', 'south'):
            return [(.0, .86, .45, 1.0, .96, .55), (.14, .10, .44, .86, .74, .56)]
        return [(.45, .86, .0, .55, .96, 1.0), (.44, .10, .14, .56, .74, .86)]
    if b.endswith('_hanging_sign'):
        rot = p.get('rotation', '0')
        ew = rot in ('4', '12')
        if ew:
            return [(.46, .74, .26, .54, 1.0, .32), (.46, .74, .68, .54, 1.0, .74), (.44, .10, .14, .56, .74, .86)]
        return [(.26, .74, .46, .32, 1.0, .54), (.68, .74, .46, .74, 1.0, .54), (.14, .10, .44, .86, .74, .56)]
    if 'wall_sign' in b or b.endswith('_wall_banner'):
        t = .08 if b.endswith('_wall_banner') else .10
        f = p.get('facing', 'north')
        x0, x1 = (0, t) if f == 'east' else (1 - t, 1) if f == 'west' else (.08, .92)
        z0, z1 = (1 - t, 1) if f == 'north' else (0, t) if f == 'south' else (.08, .92)
        return [(x0, 0 if b.endswith('_wall_banner') else .24, z0, x1, .95 if b.endswith('_wall_banner') else .78, z1)]
    if b.endswith('_sign'):
        rot = p.get('rotation', '0')
        ew = rot in ('4', '12')
        board = (.44, .42, .10, .56, .92, .90) if ew else (.10, .42, .44, .90, .92, .56)
        return [(.45, 0, .45, .55, .42, .55), board]
    if b.endswith('_banner'):
        rotation = p.get('rotation', '0')
        return [(.45, 0, .45, .55, .9, .55),
                (.48, .16, .08, .52, .85, .92) if rotation in ('4', '12')
                else (.08, .16, .48, .92, .85, .52)]
    if b == 'player_wall_head':
        f = p.get('facing', 'north')
        x0, x1 = (0, .5) if f == 'east' else (.5, 1) if f == 'west' else (.25, .75)
        z0, z1 = (.5, 1) if f == 'north' else (0, .5) if f == 'south' else (.25, .75)
        return [(x0, .25, z0, x1, .75, z1)]
    if b == 'player_head':
        return [(.25, 0, .25, .75, .5, .75)]
    if b == 'tripwire_hook':
        f = p.get('facing', 'north')
        x0, x1 = (0, .28) if f == 'east' else (.72, 1) if f == 'west' else (.38, .62)
        z0, z1 = (.72, 1) if f == 'north' else (0, .28) if f == 'south' else (.38, .62)
        return [(x0, .22, z0, x1, .62, z1)]
    if b.endswith('_button'):
        f = p.get('facing', 'north')
        if p.get('face') == 'wall':
            x0, x1 = (0, .14) if f == 'east' else (.86, 1) if f == 'west' else (.36, .64)
            z0, z1 = (.86, 1) if f == 'north' else (0, .14) if f == 'south' else (.36, .64)
            return [(x0, .38, z0, x1, .62, z1)]
        return [(.36, 0, .36, .64, .12, .64)]
    if b in ('lantern', 'soul_lantern'):
        return [(.32, .35, .32, .68, .82, .68)] if p.get('hanging') == 'true' else [(.32, 0, .32, .68, .48, .68)]
    if b.endswith('_bed'):
        return [(0, 0, 0, 1, .56, 1)]
    if b.endswith('_door') or b.endswith('_trapdoor'):
        f = p.get('facing', 'north')
        if b.endswith('_trapdoor') and p.get('open') != 'true':
            return [(0, .85 if p.get('half') == 'top' else 0, 0, 1, 1 if p.get('half') == 'top' else .15, 1)]
        if f == 'north':
            return [(0, 0, .82, 1, 1, 1)]
        if f == 'south':
            return [(0, 0, 0, 1, 1, .18)]
        if f == 'east':
            return [(0, 0, 0, .18, 1, 1)]
        return [(.82, 0, 0, 1, 1, 1)]
    if b.endswith(('_pane', '_bars', '_fence', '_wall')):
        pieces = [(.43, 0, .43, .57, 1, .57)]
        for f, ext in [('north', (.43, 0, 0, .57, 1, .5)), ('south', (.43, 0, .5, .57, 1, 1)), ('east', (.5, 0, .43, 1, 1, .57)), ('west', (0, 0, .43, .5, 1, .57))]:
            if p.get(f) in ('true', 'low', 'tall'):
                pieces.append(ext)
        return pieces
    if b in ('iron_chain', 'chain', 'lightning_rod', 'end_rod', 'torch', 'redstone_torch', 'wall_torch', 'redstone_wall_torch'):
        if b == 'end_rod' and p.get('facing') in ('north', 'south'):
            return [(.42, .42, 0, .58, .58, 1)]
        if b == 'end_rod' and p.get('facing') in ('east', 'west'):
            return [(0, .42, .42, 1, .58, .58)]
        return [(.45, 0, .45, .55, 1, .55)]
    if b.endswith(('_carpet', '_pressure_plate')) or b in ('moss_carpet', 'lily_pad'):
        return [(0, 0, 0, 1, .07, 1)]
    if b.startswith('potted_') or b in ('flower_pot', 'fern', 'short_grass', 'tall_grass', 'large_fern', 'poppy', 'dandelion', 'cornflower', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley', 'allium', 'blue_orchid', 'red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip', 'peony', 'rose_bush', 'lilac', 'sunflower', 'azalea', 'flowering_azalea', 'bush', 'sweet_berry_bush', 'candle', 'cake') or b.endswith('_candle'):
        return [(.2, 0, .2, .8, .6, .8)]
    return [(0, 0, 0, 1, 1, 1)]


def _hex_shade(hex_col: str, factor: float) -> str:
    r = int(hex_col[1:3], 16)
    g = int(hex_col[3:5], 16)
    b = int(hex_col[5:7], 16)
    return f'#{min(255, int(r * factor)):02x}{min(255, int(g * factor)):02x}{min(255, int(b * factor)):02x}'


def _merge_8x8_rects(rows: tuple[str, ...]) -> list[tuple[int, int, int, int, str]]:
    """Merge identical symbols in an 8x8 grid into maximal rectangles (u0, v0, u1, v1, sym)."""
    used = [[False] * 8 for _ in range(8)]
    out: list[tuple[int, int, int, int, str]] = []
    for r in range(8):
        for c in range(8):
            if used[r][c]:
                continue
            sym = rows[r][c]
            c1 = c + 1
            while c1 < 8 and not used[r][c1] and rows[r][c1] == sym:
                c1 += 1
            r1 = r + 1
            while r1 < 8 and all(not used[r1][cc] and rows[r1][cc] == sym for cc in range(c, c1)):
                r1 += 1
            for rr in range(r, r1):
                for cc in range(c, c1):
                    used[rr][cc] = True
            out.append((c, r, c1, r1, sym))
    return out


def _head_local_face(world_face: str, front_dir: str) -> str:
    if world_face == 'top':
        return 'top'
    order = ('north', 'east', 'south', 'west')
    fi = order.index(front_dir)
    wi = order.index(world_face)
    rel = (wi - fi) % 4
    return ('front', 'left', 'back', 'right')[rel]


def _head_face_quad(
    x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
    world_face: str, u0: float, v0: float, u1: float, v1: float,
) -> list[tuple[float, float, float]]:
    """Map normalized (u in 0..1 left-to-right, v in 0..1 top-to-bottom) onto one cube face."""
    def lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    if world_face == 'north':
        # Viewer looks +z: left is x1, right is x0; top is y1, bottom is y0
        xa, xb = lerp(x1, x0, u0), lerp(x1, x0, u1)
        ya, yb = lerp(y1, y0, v0), lerp(y1, y0, v1)
        return [(xa, ya, z0), (xb, ya, z0), (xb, yb, z0), (xa, yb, z0)]
    if world_face == 'south':
        xa, xb = lerp(x0, x1, u0), lerp(x0, x1, u1)
        ya, yb = lerp(y1, y0, v0), lerp(y1, y0, v1)
        return [(xa, ya, z1), (xb, ya, z1), (xb, yb, z1), (xa, yb, z1)]
    if world_face == 'east':
        za, zb = lerp(z1, z0, u0), lerp(z1, z0, u1)
        ya, yb = lerp(y1, y0, v0), lerp(y1, y0, v1)
        return [(x1, ya, za), (x1, ya, zb), (x1, yb, zb), (x1, yb, za)]
    if world_face == 'west':
        za, zb = lerp(z0, z1, u0), lerp(z0, z1, u1)
        ya, yb = lerp(y1, y0, v0), lerp(y1, y0, v1)
        return [(x0, ya, za), (x0, ya, zb), (x0, yb, zb), (x0, yb, za)]
    # top
    xa, xb = lerp(x0, x1, u0), lerp(x0, x1, u1)
    za, zb = lerp(z0, z1, v0), lerp(z0, z1, v1)
    return [(xa, y1, za), (xb, y1, za), (xb, y1, zb), (xa, y1, zb)]


def _sign_face_corners(
    x: int, y: int, z: int, b: str, p: dict[str, str], vis_sides: frozenset[str],
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], float] | None:
    """Return ``(TL, TR, BL, face_factor)`` for a camera-visible sign text plane, or None."""
    if b.endswith(('_hanging_sign', '_wall_hanging_sign')):
        if b.endswith('_wall_hanging_sign'):
            f = p.get('facing', 'north')
            candidates = (f, {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}.get(f, 'south'))
        else:
            rot = p.get('rotation', '0')
            ew = rot in ('4', '12')
            candidates = ('east', 'west') if ew else ('north', 'south')
        face = next((c for c in candidates if c in vis_sides), None)
        if face is None:
            return None
        y_top, y_bot = y + .72, y + .12
        if face == 'north':
            return ((x + .84, y_top, z + .435), (x + .16, y_top, z + .435), (x + .84, y_bot, z + .435), .72)
        if face == 'south':
            return ((x + .16, y_top, z + .565), (x + .84, y_top, z + .565), (x + .16, y_bot, z + .565), .72)
        if face == 'east':
            return ((x + .565, y_top, z + .84), (x + .565, y_top, z + .16), (x + .565, y_bot, z + .84), .84)
        return ((x + .435, y_top, z + .16), (x + .435, y_top, z + .84), (x + .435, y_bot, z + .16), .84)

    if 'wall_sign' in b:
        face = p.get('facing', 'north')
        if face not in vis_sides:
            return None
        y_top, y_bot = y + .76, y + .26
        if face == 'north':
            return ((x + .90, y_top, z + .895), (x + .10, y_top, z + .895), (x + .90, y_bot, z + .895), .72)
        if face == 'south':
            return ((x + .10, y_top, z + .105), (x + .90, y_top, z + .105), (x + .10, y_bot, z + .105), .72)
        if face == 'east':
            return ((x + .105, y_top, z + .90), (x + .105, y_top, z + .10), (x + .105, y_bot, z + .90), .84)
        return ((x + .895, y_top, z + .10), (x + .895, y_top, z + .90), (x + .895, y_bot, z + .10), .84)

    # Standing *_sign
    rot_s = p.get('rotation', '0')
    rot_i = int(rot_s) if rot_s.isdigit() else 0
    face = _ROT_TO_FACING[((rot_i + 2) // 4) % 4]
    if face not in vis_sides:
        return None
    y_top, y_bot = y + .90, y + .44
    if face == 'north':
        return ((x + .88, y_top, z + .435), (x + .12, y_top, z + .435), (x + .88, y_bot, z + .435), .72)
    if face == 'south':
        return ((x + .12, y_top, z + .565), (x + .88, y_top, z + .565), (x + .12, y_bot, z + .565), .72)
    if face == 'east':
        return ((x + .565, y_top, z + .88), (x + .565, y_top, z + .12), (x + .565, y_bot, z + .88), .84)
    return ((x + .435, y_top, z + .12), (x + .435, y_top, z + .88), (x + .435, y_bot, z + .12), .84)


def svg(
    grid: dict[tuple[int, int, int], list[Any]],
    view: int = 0,
    cut: int | None = None,
    bounds: Sequence[int] | None = None,
) -> str:
    width, height = 960, 800
    pad = 36.0
    if bounds is not None:
        w, h, d = int(bounds[3]) + 1, int(bounds[4]) + 1, int(bounds[5]) + 1
    else:
        w = max([24] + [x + 1 for (x, _, _) in grid])
        h = max([18] + [y + 1 for (_, y, _) in grid])
        d = max([22] + [z + 1 for (_, _, z) in grid])

    cut_limit = h if cut is None else cut
    v_idx = view % 4
    vis_sides = _VISIBLE_SIDES[v_idx]
    span_a, span_b = (w, d) if v_idx in (0, 2) else (d, w)
    u_span = float(span_a + span_b)
    u_mid = (span_a - span_b) * 0.5
    vv_span = float(h) + u_span * 0.5
    vv_mid = (u_span * 0.5 - float(h)) * 0.5
    scale = min((width - 2 * pad) / max(1.0, u_span), (height - 2 * pad) / max(1.0, vv_span))

    def rotate(x: float, z: float) -> tuple[float, float]:
        return ((x, z), (z, w - x), (w - x, d - z), (d - z, x))[v_idx]

    def point(x: float, y: float, z: float) -> tuple[float, float]:
        a, b_coord = rotate(x, z)
        u = a - b_coord
        vv = (a + b_coord) * 0.5 - y
        px = max(0.0, min(float(width), width * 0.5 + (u - u_mid) * scale))
        py = max(0.0, min(float(height), height * 0.5 + (vv - vv_mid) * scale))
        return (px, py)

    def quad_depth(pts: Sequence[tuple[float, float, float]]) -> float:
        return sum(sum(rotate(v[0], v[2])) + v[1] * .08 for v in pts) / len(pts)

    def poly(pts: Sequence[tuple[float, float, float]], fill_hex: str, stroke_w: float = 0.35) -> str:
        coords = ' '.join(f'{px:.1f},{py:.1f}' for px, py in (point(*v) for v in pts))
        return f'<polygon points="{coords}" fill="{fill_hex}" stroke="{fill_hex}" stroke-width="{stroke_w}"/>'

    faces: list[tuple[float, str]] = []
    for (x, y, z), cell in grid.items():
        if not (0 <= x < w and 0 <= y < cut_limit and 0 <= z < d):
            continue
        b, p = state_parts(cell[3])
        lines = cell[4] if len(cell) > 4 else None
        asset = cell[6] if len(cell) > 6 else None
        frame = cell[7] if len(cell) > 7 else None

        # Render visible item_frame (even when block state at (x,y,z) is 'air')
        if isinstance(frame, dict) and not frame.get('invisible', False):
            ff = frame.get('facing', 'north')
            if ff in vis_sides:
                factor = .72 if ff in ('north', 'south') else .84
                if ff == 'north':
                    bx0, by0, bz0, bx1, by1, bz1 = x + .16, y + .16, z + .92, x + .84, y + .84, z + 1.0
                elif ff == 'south':
                    bx0, by0, bz0, bx1, by1, bz1 = x + .16, y + .16, z + .0, x + .84, y + .84, z + .08
                elif ff == 'east':
                    bx0, by0, bz0, bx1, by1, bz1 = x + .0, y + .16, z + .16, x + .08, y + .84, z + .84
                else:
                    bx0, by0, bz0, bx1, by1, bz1 = x + .92, y + .16, z + .16, x + 1.0, y + .84, z + .84
                outer_q = _head_face_quad(bx0, by0, bz0, bx1, by1, bz1, ff, 0.0, 0.0, 1.0, 1.0)
                inner_q = _head_face_quad(bx0, by0, bz0, bx1, by1, bz1, ff, 0.14, 0.14, 0.86, 0.86)
                d_fr = quad_depth(outer_q)
                faces.append((d_fr + 0.01, poly(outer_q, _hex_shade('#b5824c', factor))))
                faces.append((d_fr + 0.015, poly(inner_q, _hex_shade('#5b3821', factor))))
                item_name = str(frame.get('item', ''))
                # Draw miniature builder tool silhouette inside the frame
                shaft_q = _head_face_quad(bx0, by0, bz0, bx1, by1, bz1, ff, 0.42, 0.30, 0.56, 0.80)
                head_col = '#9aa3ab' if 'stone' in item_name or 'iron' in item_name else '#b88748'
                blade_q = _head_face_quad(bx0, by0, bz0, bx1, by1, bz1, ff, 0.24, 0.20, 0.72, 0.42)
                faces.append((d_fr + 0.02, poly(shaft_q, _hex_shade('#8c6239', factor), 0.2)))
                faces.append((d_fr + 0.022, poly(blade_q, _hex_shade(head_col, factor), 0.2)))

        if b == 'air':
            continue

        # Render custom player_head / player_wall_head with 8x8 multi-face pixel art
        if b in ('player_head', 'player_wall_head'):
            box_bounds = shape(b, p)[0]
            hx0, hy0, hz0, hx1, hy1, hz1 = (
                x + box_bounds[0], y + box_bounds[1], z + box_bounds[2],
                x + box_bounds[3], y + box_bounds[4], z + box_bounds[5],
            )
            if b == 'player_wall_head':
                front_dir = p.get('facing', 'north')
                if front_dir not in ('north', 'south', 'east', 'west'):
                    front_dir = 'north'
            else:
                rot_s = p.get('rotation', '0')
                rot_i = int(rot_s) if rot_s.isdigit() else 0
                front_dir = _ROT_TO_FACING[((rot_i + 2) // 4) % 4]
            pal, h_faces = head_faces(asset)
            for w_face in ('top', *sorted(vis_sides)):
                factor = 1.0 if w_face == 'top' else (.74 if w_face in ('north', 'south') else .86)
                local_f = _head_local_face(w_face, front_dir)
                rows_8 = h_faces[local_f]
                base_q = _head_face_quad(hx0, hy0, hz0, hx1, hy1, hz1, w_face, 0.0, 0.0, 1.0, 1.0)
                f_depth = quad_depth(base_q)
                for u0, v0, u1, v1, sym in _merge_8x8_rects(rows_8):
                    sub_q = _head_face_quad(hx0, hy0, hz0, hx1, hy1, hz1, w_face, u0 / 8.0, v0 / 8.0, u1 / 8.0, v1 / 8.0)
                    col_hex = _hex_shade(pal.get(sym, '#8c8270'), factor)
                    faces.append((f_depth + 0.002, poly(sub_q, col_hex, 0.22)))
            continue

        if b.endswith(('_pane', '_bars', '_fence', '_wall')):
            p = dict(p)
            for f, (dx, dz) in {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}.items():
                adjacent = grid.get((x + dx, y, z + dz), [0, 0, 0, 'air'])[3]
                if f not in p and (full_block(adjacent) or state_parts(adjacent)[0] == b):
                    p[f] = 'true'
        rgb = colour(b)
        parts = shape(b, p)
        for part_idx, (a0, h0, c0, a1, h1, c1) in enumerate(parts):
            # Render hanging sign chains / crossbar in dark iron
            part_rgb = (62, 68, 74) if (b.endswith(('_hanging_sign', '_wall_hanging_sign')) and part_idx < len(parts) - 1) else rgb
            vertices = [
                (x + a0, y + h0, z + c0), (x + a1, y + h0, z + c0), (x + a1, y + h0, z + c1), (x + a0, y + h0, z + c1),
                (x + a0, y + h1, z + c0), (x + a1, y + h1, z + c0), (x + a1, y + h1, z + c1), (x + a0, y + h1, z + c1),
            ]
            for inds, factor, offset in [
                ((0, 1, 5, 4), .72, (0, 0, -1)),
                ((1, 2, 6, 5), .84, (1, 0, 0)),
                ((2, 3, 7, 6), .72, (0, 0, 1)),
                ((3, 0, 4, 7), .84, (-1, 0, 0)),
                ((4, 5, 6, 7), 1.0, (0, 1, 0)),
            ]:
                nx, ny, nz = x + offset[0], y + offset[1], z + offset[2]
                neighbor = grid.get((nx, ny, nz), [0, 0, 0, 'air'])[3]
                if full_block(cell[3]) and ny < cut_limit and full_block(neighbor):
                    continue
                if b == 'water' and ny < cut_limit and offset != (0, 1, 0) and (state_parts(neighbor)[0] == 'water' or full_block(neighbor)):
                    continue
                pts = [vertices[i] for i in inds]
                depth = quad_depth(pts)
                fill = '#' + ''.join(f'{int(c * factor):02x}' for c in part_rgb)
                faces.append((depth, poly(pts, fill, 0.4)))

        # Project legible sign text onto visible sign faces
        if lines and b.endswith(('_sign', '_hanging_sign', '_wall_hanging_sign')) and any(s.strip() for s in lines):
            corners = _sign_face_corners(x, y, z, b, p, vis_sides)
            if corners is not None:
                tl_w, tr_w, bl_w, _ = corners
                br_w = (tr_w[0] + bl_w[0] - tl_w[0], bl_w[1], tr_w[2] + bl_w[2] - tl_w[2])
                s_depth = quad_depth((tl_w, tr_w, br_w, bl_w))
                tl_p, tr_p, bl_p = point(*tl_w), point(*tr_w), point(*bl_w)
                cw, ch = 96.0, 48.0
                ma = (tr_p[0] - tl_p[0]) / cw
                mb = (tr_p[1] - tl_p[1]) / cw
                mc = (bl_p[0] - tl_p[0]) / ch
                md = (bl_p[1] - tl_p[1]) / ch
                ink = '#f7f3e8' if ('dark_oak' in b or 'mangrove' in b) else '#17130f'
                padded = [str(s) for s in lines[:4]]
                while len(padded) < 4:
                    padded.append('')
                text_nodes = []
                for row_i, raw_line in enumerate(padded):
                    clean_line = raw_line.strip()
                    if not clean_line:
                        continue
                    ty = 11.0 + row_i * 11.0
                    esc = html.escape(clean_line[:22])
                    text_nodes.append(
                        f'<text x="48" y="{ty:.1f}" text-anchor="middle" '
                        f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
                        f'font-size="9.2" font-weight="700" fill="{ink}">{esc}</text>'
                    )
                if text_nodes:
                    grp = (
                        f'<g transform="matrix({ma:.4f} {mb:.4f} {mc:.4f} {md:.4f} {tl_p[0]:.2f} {tl_p[1]:.2f})">'
                        + ''.join(text_nodes)
                        + '</g>'
                    )
                    faces.append((s_depth + 0.025, grp))

    title = html.escape('Isometric voxel scene with custom heads, item frames and sign text')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
        f'<rect width="100%" height="100%" fill="#eef2ef"/>'
        + ''.join(s for _, s in sorted(faces, key=lambda q: q[0]))
        + '</svg>'
    )
