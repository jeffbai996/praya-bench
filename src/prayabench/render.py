"""Auto-framing flat-colour isometric SVG renderer. No Minecraft artwork or texture downloads."""
import html
from typing import Any, Sequence

from .scene import RAIL_BLOCKS, full_block, state_parts


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
    if 'leaves' in b or b in ('grass_block', 'moss_block', 'moss_carpet', 'azalea', 'flowering_azalea', 'fern', 'large_fern', 'bush', 'sweet_berry_bush', 'short_grass', 'tall_grass', 'lily_pad', 'vine'):
        return (72, 116, 62)
    if any(t in b for t in ('poppy', 'dandelion', 'flower', 'cornflower', 'bluet', 'peony', 'rose_bush', 'oxeye_daisy', 'lily_of_the_valley', 'allium', 'orchid', 'tulip', 'lilac', 'sunflower')):
        return (192, 148, 115)
    if b == 'tinted_glass':
        return (78, 76, 86)
    if 'glass' in b:
        return (125, 159, 169)
    if b == 'powered_rail':
        return (206, 164, 62)
    if b in RAIL_BLOCKS:
        return (138, 130, 118)
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
    if 'spruce' in b or 'dark_oak' in b:
        return (109, 80, 50)
    if any(t in b for t in ('oak', 'birch', 'barrel', 'bookshelf', 'lectern', 'chest', 'crafting_table', 'composter', 'loom', 'cartography_table')):
        return (159, 123, 77)
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
    if b in ('iron_block', 'iron_door', 'iron_trapdoor', 'iron_bars', 'cauldron', 'water_cauldron', 'hopper', 'anvil'):
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
    if b == 'water':
        return [(0, 0, 0, 1, .88, 1)]
    if b in RAIL_BLOCKS:
        return [(0, 0, 0, 1, .08, 1)]
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
    if b.endswith(('_hanging_sign', '_wall_hanging_sign')):
        f = p.get('facing', 'north')
        return [(.15, .12, .44, .85, .72, .56)] if f in ('north', 'south') else [(.44, .12, .15, .56, .72, .85)]
    if 'wall_sign' in b or b == 'player_wall_head':
        t = .12 if 'sign' in b else .5
        f = p.get('facing', 'north')
        x0, x1 = (0, t) if f == 'east' else (1 - t, 1) if f == 'west' else (.15, .85)
        z0, z1 = (1 - t, 1) if f == 'north' else (0, t) if f == 'south' else (.15, .85)
        return [(x0, .3, z0, x1, .8, z1)]
    if b == 'player_head':
        return [(.25, 0, .25, .75, .5, .75)]
    if b in ('lantern', 'soul_lantern'):
        return [(.32, .35, .32, .68, .82, .68)] if p.get('hanging') == 'true' else [(.32, 0, .32, .68, .48, .68)]
    if b.endswith('_bed'):
        return [(0, 0, 0, 1, .56, 1)]
    if b.endswith('_door') or b.endswith('_trapdoor'):
        f = p.get('facing', 'north')
        if b.endswith('_trapdoor') and p.get('open') != 'true':
            return [(0, .85 if p.get('half') == 'top' else 0, 0, 1, 1 if p.get('half') == 'top' else .15, 1)]
        return [(0, 0, 0, 1, 1, .15)] if f in ('north', 'south') else [(0, 0, 0, .15, 1, 1)]
    if b.endswith(('_pane', '_bars', '_fence', '_wall')):
        pieces = [(.43, 0, .43, .57, 1, .57)]
        for f, ext in [('north', (.43, 0, 0, .57, 1, .5)), ('south', (.43, 0, .5, .57, 1, 1)), ('east', (.5, 0, .43, 1, 1, .57)), ('west', (0, 0, .43, .5, 1, .57))]:
            if p.get(f) in ('true', 'low', 'tall'):
                pieces.append(ext)
        return pieces
    if b in ('iron_chain', 'chain', 'lightning_rod', 'end_rod', 'torch', 'redstone_torch', 'wall_torch', 'redstone_wall_torch'):
        return [(.45, 0, .45, .55, 1, .55)]
    if b.endswith(('_carpet', '_pressure_plate')) or b in ('moss_carpet', 'lily_pad'):
        return [(0, 0, 0, 1, .07, 1)]
    if b.startswith('potted_') or b in ('flower_pot', 'fern', 'short_grass', 'tall_grass', 'large_fern', 'poppy', 'dandelion', 'cornflower', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley', 'allium', 'blue_orchid', 'red_tulip', 'orange_tulip', 'white_tulip', 'pink_tulip', 'peony', 'rose_bush', 'lilac', 'sunflower', 'azalea', 'flowering_azalea', 'bush', 'sweet_berry_bush', 'candle', 'cake') or b.endswith('_candle'):
        return [(.2, 0, .2, .8, .6, .8)]
    return [(0, 0, 0, 1, 1, 1)]


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
    span_a, span_b = (w, d) if v_idx in (0, 2) else (d, w)
    u_span = float(span_a + span_b)
    u_mid = (span_a - span_b) * 0.5
    vv_span = float(h) + u_span * 0.5
    vv_mid = (u_span * 0.5 - float(h)) * 0.5
    scale = min((width - 2 * pad) / max(1.0, u_span), (height - 2 * pad) / max(1.0, vv_span))

    def rotate(x: float, z: float) -> tuple[float, float]:
        return ((x, z), (z, w - x), (w - x, d - z), (d - z, x))[v_idx]

    def point(x: float, y: float, z: float) -> tuple[float, float]:
        a, b = rotate(x, z)
        u = a - b
        vv = (a + b) * 0.5 - y
        return (width * 0.5 + (u - u_mid) * scale, height * 0.5 + (vv - vv_mid) * scale)

    faces: list[tuple[float, str]] = []
    for (x, y, z), cell in grid.items():
        if not (0 <= x < w and 0 <= y < cut_limit and 0 <= z < d):
            continue
        b, p = state_parts(cell[3])
        if b == 'air':
            continue
        if b.endswith(('_pane', '_bars', '_fence', '_wall')):
            p = dict(p)
            for f, (dx, dz) in {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}.items():
                adjacent = grid.get((x + dx, y, z + dz), [0, 0, 0, 'air'])[3]
                if f not in p and (full_block(adjacent) or state_parts(adjacent)[0] == b):
                    p[f] = 'true'
        rgb = colour(b)
        for a0, h0, c0, a1, h1, c1 in shape(b, p):
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
                depth = sum(sum(rotate(v[0], v[2])) + v[1] * .08 for v in pts) / 4
                fill = '#' + ''.join(f'{int(c * factor):02x}' for c in rgb)
                coords = ' '.join(f'{px:.1f},{py:.1f}' for px, py in (point(*v) for v in pts))
                faces.append((depth, f'<polygon points="{coords}" fill="{fill}" stroke="{fill}" stroke-width="0.4"/>'))
    title = html.escape('Isometric voxel scene; approximate geometry and placeholder props')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
        f'<rect width="100%" height="100%" fill="#eef2ef"/>'
        + ''.join(s for _, s in sorted(faces, key=lambda q: q[0]))
        + '</svg>'
    )
