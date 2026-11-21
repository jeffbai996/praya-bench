"""Bounded declarative formats for Minecraft-style graphics. No external assets."""
import base64
import html
import json
import re
import struct
import zlib

from . import __version__

# Selected map base colours and the four map shade multipliers. A fixed subset
# keeps the task portable across versions without bundling game assets.
MAP_BASES = (
    (127, 178, 56), (247, 233, 163), (199, 199, 199), (255, 0, 0), (164, 168, 184),
    (167, 167, 167), (0, 124, 0), (255, 255, 255), (151, 109, 77),
    (112, 112, 112), (64, 64, 255), (143, 119, 72), (255, 252, 245), (216, 127, 51),
    (178, 76, 216), (102, 153, 216), (229, 229, 51), (127, 204, 25), (242, 127, 165),
    (76, 76, 76), (153, 153, 153), (76, 127, 153), (127, 63, 178), (51, 76, 178),
    (102, 76, 51), (102, 127, 51), (153, 51, 51), (25, 25, 25), (250, 238, 77),
    (92, 219, 213), (74, 128, 255), (0, 217, 58), (129, 86, 49), (112, 2, 0),
    (209, 177, 161), (159, 82, 36), (149, 87, 108), (112, 108, 138), (186, 133, 36),
    (103, 117, 53), (160, 77, 78), (57, 41, 35), (135, 107, 98), (87, 92, 92),
    (122, 73, 88), (76, 62, 92), (76, 50, 35), (76, 82, 42), (142, 60, 46),
    (37, 22, 16),
)
MAP_PALETTE = sorted({tuple(c * shade // 255 for c in rgb)
                      for rgb in MAP_BASES for shade in (180, 220, 255, 135)})
DYES = dict(zip(
    ('white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
     'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black'),
    ('f9fffe', 'f9801d', 'c74ebd', '3ab3da', 'fed83d', '80c71f', 'f38baa', '474f52',
     '9d9d97', '169c9c', '8932b8', '3c44aa', '835432', '5e7c16', 'b02e26', '1d1d21'),
))
PATTERNS = (
    'stripe_center', 'stripe_middle', 'stripe_left', 'stripe_right', 'stripe_top',
    'stripe_bottom', 'cross', 'straight_cross', 'circle', 'rhombus', 'border',
    'half_vertical', 'half_horizontal', 'triangle_top', 'triangle_bottom',
)

# Standard Java 64x64 head atlas rectangles, named from the avatar's front.
INNER = {'front': (8, 8), 'right': (0, 8), 'left': (16, 8), 'back': (24, 8),
         'top': (8, 0), 'bottom': (16, 0)}
OUTER = {face: (x+32, y) for face, (x, y) in INNER.items()}


def _spec(track, category, brief, **settings):
    return {'track': track, 'scale': 'asset', 'category': category, 'brief': brief,
            'terrain': 'Synthetic asset brief.', **settings}


ART_TASKS = {
    'map-fascia-wordmark': _spec('map-art', 'fascia',
        'Design a two-tile transparent storefront wordmark reading NORTH PIER. Use high-contrast lettering. '
        'Keep all edges clear and treat the tile boundary as part of one continuous design.',
        width=256, height=128, transparent=True,
        probes=[[[25, 44, 117, 84], 'left word'], [[139, 44, 232, 84], 'right word']]),
    'map-departure-board': _spec('map-art', 'civic-display',
        'Make an opaque 128×128 dark transit departure board. Show a DEPARTURES header, two rows with '
        'distinct destinations and times, and an amber status accent. Keep tiny text readable after map quantization.',
        width=128, height=128, transparent=False, field='dark', accent='amber',
        probes=[[[12, 10, 116, 35], 'header'], [[12, 44, 116, 65], 'first departure'],
                [[12, 74, 116, 96], 'second departure']]),
    'map-motorway-guide': _spec('map-art', 'road-sign',
        'Make a three-tile opaque motorway guide panel. Use a dark green field, legible pale destination '
        'text for AIRPORT and HARBOUR, and a distinct arrow for each lane. Pay attention to the two tile seams.',
        width=384, height=128, transparent=False, field='green',
        probes=[[[16, 14, 177, 65], 'left destination'], [[207, 14, 367, 65], 'right destination'],
                [[16, 77, 177, 114], 'left arrow'], [[207, 77, 367, 114], 'right arrow']]),
    'banner-harbour-burgee': _spec('loom-banner', 'emblem',
        'Reconstruct the harbour burgee target using a survival loom recipe.', base='blue',
        target_layers=[['stripe_middle', 'white'], ['rhombus', 'yellow']]),
    'banner-civic-shield': _spec('loom-banner', 'emblem',
        'Reconstruct the civic shield target using a survival loom recipe.', base='green',
        target_layers=[['border', 'white'], ['straight_cross', 'yellow'], ['circle', 'red']]),
    'banner-rail-roundel': _spec('loom-banner', 'emblem',
        'Reconstruct the rail roundel target using a survival loom recipe.', base='black',
        target_layers=[['circle', 'red'], ['stripe_middle', 'white'], ['stripe_left', 'blue']]),
    'head-parking-meter': _spec('head-skin', 'street-asset',
        'Paint a parking meter head with a distinct screen and payment slot on the front and a raised display bezel.',
        overlay_faces=['front']),
    'head-hvac-vent': _spec('head-skin', 'building-asset',
        'Paint an HVAC vent head with a slatted front, a plainer back, and grille relief on the front and top.',
        overlay_faces=['front', 'top']),
    'head-mailbox': _spec('head-skin', 'street-asset',
        'Paint a postal dropbox head with a high-contrast front slot and a raised lid. Make the postal front distinct from the back.',
        overlay_faces=['front', 'top']),
}


def _matches(pattern, x, y):
    nx, ny = (x+.5)/16, (y+.5)/32
    masks = {
        'stripe_center': 5 <= x < 11, 'stripe_middle': 11 <= y < 21,
        'stripe_left': x < 5, 'stripe_right': x >= 11, 'stripe_top': y < 10,
        'stripe_bottom': y >= 22, 'straight_cross': 6 <= x < 10 or 13 <= y < 19,
        'cross': min(abs(nx-ny), abs(nx+ny-1)) < .10,
        'circle': (nx-.5)**2+(ny-.5)**2 <= .11,
        'rhombus': abs(nx-.5)+abs(ny-.5) <= .42,
        'border': x < 2 or x >= 14 or y < 4 or y >= 28,
        'half_vertical': x < 8, 'half_horizontal': y < 16,
        'triangle_top': ny < .46 and abs(nx-.5) <= .50-ny,
        'triangle_bottom': ny >= .54 and abs(nx-.5) <= ny-.50,
    }
    return masks[pattern]


def banner_pixels(base, layers):
    pixels = [base]*512
    for pattern, dye in layers:
        for i in range(512):
            if _matches(pattern, i%16, i//16):
                pixels[i] = dye
    return pixels


def art_fixture(task):
    spec = {k: v for k, v in ART_TASKS[task].items() if k != 'target_layers'}
    spec['task'] = task
    if spec['track'] == 'loom-banner':
        pixels = banner_pixels(spec.pop('base'), ART_TASKS[task]['target_layers'])
        keys = {dye: '0123456789abcdef'[i] for i, dye in enumerate(DYES)}
        spec['target'] = [''.join(keys[p] for p in pixels[i:i+16]) for i in range(0, 512, 16)]
    if spec['track'] == 'head-skin':
        spec['width'], spec['height'] = 64, 64
        spec['inner_uv'], spec['outer_uv'] = INNER, OUTER
    return spec


def art_prompt(fixture):
    track = fixture['track']
    prompt = f"Task {fixture['task']}. {fixture['brief']}\nReturn one JSON object.\n"
    if track == 'loom-banner':
        return prompt + (
            'Format: {"base":"blue","layers":[["stripe_middle","white"]]}. '
            'Apply up to 6 ordered layers from the supported survival loom subset. '
            'The target is a 16×32 abstract preview using the following dye key.\n'
            f"{json.dumps(dict(zip('0123456789abcdef', DYES)))}\n"
            f"Supported patterns: {', '.join(PATTERNS)}.\n" + '\n'.join(fixture['target']) + '\n'
        )
    prompt += (
        'Format: {"colors":{"a":"#RRGGBB","b":"#RRGGBBAA"},"rects":[[x,y,width,height,"a"]],'
        '"rows":{"0":"..aaa"}}. Rectangles are painted in order, then optional sparse row strings overwrite pixels '
        'from x=0 (including "." for transparent). Unpainted pixels are transparent. Use at most 4096 rectangles '
        'and 64 colour symbols. Origin is upper left.\n'
        f"Canvas: {fixture['width']}×{fixture['height']}.\n"
    )
    if track == 'head-skin':
        return prompt + (
            f'Inner 8×8 faces: {json.dumps(INNER)}. Outer 8×8 faces: {json.dumps(OUTER)}. '
            'Fully paint all six inner faces with opaque pixels. Use transparent pixels '
            'outside the head islands and leave some transparent pixels in the outer layer. '
            f"Required relief faces: {', '.join(fixture['overlay_faces'])}.\n"
        )
    return prompt + (
        'Map art is quantized to a fixed Minecraft map-palette subset. Alpha is binary at 128. '
        + ('Leave the canvas edge transparent. ' if fixture['transparent'] else 'Use an opaque field. ')
        + f"Include visible detail within these half-open rectangles: {json.dumps(fixture['probes'])}.\n"
    )


def art_palette(track):
    if track == 'map-art':
        return '\n'.join('#%02x%02x%02x' % rgb for rgb in MAP_PALETTE) + '\n'
    if track == 'loom-banner':
        return '\n'.join(f'{k} #{v}' for k, v in DYES.items()) + '\n\n' + '\n'.join(PATTERNS) + '\n'
    return '#RRGGBB or #RRGGBBAA (sRGB)\n'


def rasterize(data, width, height):
    colors, rects, rows = data.get('colors', {}), data.get('rects', []), data.get('rows', {})
    if not isinstance(colors, dict) or len(colors) > 64 or not isinstance(rects, list) or len(rects) > 4096:
        raise ValueError('invalid colors or rectangle budget')
    if not isinstance(rows, dict) or len(rows) > height:
        raise ValueError('invalid sparse rows')
    transparent = (0, 0, 0, 0)
    lut = {'.': transparent}
    for key, value in colors.items():
        if not re.fullmatch(r'[A-Za-z0-9!$%&*+,:;=?@^_-]', key) or not isinstance(value, str) or not re.fullmatch(r'#[a-fA-F0-9]{6}(?:[a-fA-F0-9]{2})?', value):
            raise ValueError('colors need single ASCII symbols and #RRGGBB or #RRGGBBAA')
        rgb = tuple(bytes.fromhex(value[1:]))
        lut[key] = rgb if len(rgb) == 4 else (*rgb, 255)
    pixels = [transparent]*(width*height)
    painted = 0
    for rectangle in rects:
        if not isinstance(rectangle, list) or len(rectangle) != 5:
            raise ValueError('rectangle needs x,y,width,height,symbol')
        x, y, w, h, key = rectangle
        if (any(type(n) is not int for n in (x,y,w,h)) or not isinstance(key, str) or key not in lut
                or min(x,y) < 0 or min(w,h) < 1 or x+w > width or y+h > height):
            raise ValueError('invalid or out-of-bounds rectangle')
        painted += w*h
        if painted > width*height*16:
            raise ValueError('paint budget exceeded')
        for yy in range(y, y+h):
            start = yy*width+x
            pixels[start:start+w] = [lut[key]]*w
    for key, row in rows.items():
        if not re.fullmatch(r'0|[1-9][0-9]{0,2}', key) or int(key) >= height or not isinstance(row, str) or len(row) > width:
            raise ValueError('invalid row coordinate or width')
        if any(c not in lut for c in row):
            raise ValueError('row uses unknown color symbol')
        start = int(key)*width
        pixels[start:start+len(row)] = [lut[c] for c in row]
    return pixels


def quantize(pixels):
    lookup = {}
    for rgb in {p[:3] for p in pixels if p[3] >= 128}:
        lookup[rgb] = min(MAP_PALETTE, key=lambda c: sum((a-b)**2 for a,b in zip(rgb,c)))
    return [(*lookup[p[:3]], 255) if p[3] >= 128 else (0,0,0,0) for p in pixels]


def _regions(width, rect):
    x0, y0, x1, y1 = rect
    return [y*width+x for y in range(y0, y1) for x in range(x0, x1)]


def _face(pixels, uv):
    x, y = uv
    return [pixels[i] for i in _regions(64, (x,y,x+8,y+8))]


def assess_art(fixture, data):
    if not isinstance(data, dict):
        raise ValueError('expected a JSON object')
    track = fixture['track']
    checks, issues, metrics = [], [], {}

    def check(requirement, expected, observed, met):
        checks.append(dict(requirement=requirement, expected=expected, observed=observed, met=bool(met)))

    if track == 'loom-banner':
        if set(data) != {'base', 'layers'} or not isinstance(data['base'], str) or data['base'] not in DYES or not isinstance(data['layers'], list):
            raise ValueError('banner needs base dye and an ordered layers array')
        layers = data['layers']
        if len(layers) > 64:
            raise ValueError('excessive banner layer count')
        for layer in layers:
            if (not isinstance(layer, list) or len(layer) != 2 or any(not isinstance(v, str) for v in layer)
                    or layer[0] not in PATTERNS or layer[1] not in DYES):
                raise ValueError('unsupported banner pattern or dye')
        if len(layers) > 6:
            issues.append(dict(code='loom_layer_limit', severity='error', detail='Survival loom permits at most six layers.'))
        pixels = banner_pixels(data['base'], layers)
        key = dict(zip('0123456789abcdef', DYES))
        target = [key[c] for row in fixture['target'] for c in row]
        accuracy = sum(a == b for a,b in zip(pixels,target))/512
        classes = sorted(set(target))
        iou = {}
        for dye in classes:
            intersection = sum(a == b == dye for a,b in zip(pixels, target))
            union = sum(a == dye or b == dye for a,b in zip(pixels, target))
            iou[dye] = round(intersection/union, 4)
        metrics.update(pixel_accuracy=round(accuracy,4), per_dye_iou=iou, layer_count=len(layers))
        check('survival_recipe', 'at most 6 layers', len(layers), len(layers) <= 6)
        check('target_pixel_match', 1, round(accuracy,4), accuracy == 1)
    else:
        if set(data) - {'colors','rects','rows'}:
            raise ValueError('pixel art accepts colors, rects and rows')
        w, h = fixture['width'], fixture['height']
        pixels = rasterize(data, w, h)
        if track == 'map-art':
            rendered = quantize(pixels)
            opaque = [p for p in rendered if p[3]]
            fraction = len(opaque)/(w*h)
            metrics.update(opaque_fraction=round(fraction,4), quantized_colors=len(set(opaque)),
                           tiles=[w//128,h//128])
            threshold = .03 if fixture['transparent'] else .97
            upper = .85 if fixture['transparent'] else 1
            check('alpha_coverage', [threshold,upper], round(fraction,4), threshold <= fraction <= upper)
            span = _luminance_span(opaque)
            check('map_palette_contrast', 'luminance span ≥ 60', span, span >= 60)
            if fixture.get('field') == 'dark':
                dark = sum(_luminance(p) <= 65 for p in opaque)/(w*h)
                check('dark_display_field','≥ 60% of pixels',round(dark,3),dark >= .60)
            elif fixture.get('field') == 'green':
                green = sum(g >= 1.2*r and g >= 1.15*b and _luminance((r,g,b,a)) <= 125
                            for r,g,b,a in opaque)/(w*h)
                check('green_guide_field','≥ 60% of pixels',round(green,3),green >= .60)
            if fixture.get('accent') == 'amber':
                amber = sum(r>=135 and .38*r<=g<=.90*r and b<.65*g for r,g,b,a in opaque)
                check('amber_status_accent','≥ 16 pixels',amber,amber >= 16)
            if fixture['transparent']:
                border = sum(bool(rendered[y*w+x][3]) for y in range(h) for x in range(w) if x in (0,w-1) or y in (0,h-1))
                check('transparent_edge', 0, border, border == 0)
                if fixture['task'] == 'map-fascia-wordmark':
                    # Verify smooth rounded corners on any backing plate (bounding corners of opaque pixels remain transparent)
                    oxs = [x for y in range(h) for x in range(w) if rendered[y*w+x][3]]
                    oys = [y for y in range(h) for x in range(w) if rendered[y*w+x][3]]
                    if oxs and oys:
                        x0, x1, y0, y1 = min(oxs), max(oxs), min(oys), max(oys)
                        corner_hits = sum(
                            bool(rendered[cy*w+cx][3])
                            for cx in (x0, x0+1, x1-1, x1)
                            for cy in (y0, y0+1, y1-1, y1)
                        )
                        check('rounded_corners', 0, corner_hits, corner_hits == 0)
            for rect, label in fixture['probes']:
                region = [rendered[i] for i in _regions(w, rect) if rendered[i][3]]
                occupied = len(region) / ((rect[2]-rect[0])*(rect[3]-rect[1]))
                span = _luminance_span(region)
                coverage = round(occupied, 3)
                minimum = .05 if fixture['transparent'] else .92
                check(label, {'coverage_min':minimum,'luminance_span_min':55 if not fixture['transparent'] else 0},
                      {'coverage':coverage,'luminance_span':span}, occupied >= minimum and (fixture['transparent'] or span >= 55))
            metrics['seam_color_change'] = [round(sum(rendered[y*w+x-1] != rendered[y*w+x] for y in range(h))/h,4)
                                            for x in range(128,w,128)]
        else:
            inner = {face: _face(pixels, xy) for face,xy in INNER.items()}
            outer = {face: _face(pixels, xy) for face,xy in OUTER.items()}
            for face, samples in inner.items():
                solid = sum(p[3] == 255 for p in samples)
                check(f'opaque_{face}', 64, solid, solid == 64)
            front = _luminance_span(inner['front'])
            check('front_contrast', '≥ 45 luminance', front, front >= 45)
            different = sum(a != b for a,b in zip(inner['front'],inner['back']))
            check('front_back_distinction', '≥ 8 different pixels', different, different >= 8)
            overlays = {face:sum(p[3] > 0 for p in samples) for face,samples in outer.items()}
            for face in fixture['overlay_faces']:
                check(f'{face}_relief', '1–48 visible pixels', overlays[face], 1 <= overlays[face] <= 48)
            check('transparent_overlay', '<384 visible pixels', sum(overlays.values()), sum(overlays.values()) < 384)
            allowed = {i for x,y in (*INNER.values(), *OUTER.values()) for i in _regions(64, (x,y,x+8,y+8))}
            stray = sum(bool(p[3]) and i not in allowed for i,p in enumerate(pixels))
            if stray:
                issues.append(dict(code='pixels_outside_head_uv', severity='error', detail=f'{stray} painted pixels are outside the head UV islands.'))
            metrics['outer_visible_pixels'] = overlays

    met = sum(c['met'] for c in checks)
    return {
        'schema_version': 4, 'evaluator_version': __version__, 'task':fixture['task'], 'track':track,
        'scale':'asset','issues':issues,'counts':{i['code']:1 for i in issues},
        'completion': {'checks':checks,'met_count':met,'total_count':len(checks),'complete':met==len(checks)},
        'metrics':metrics, 'review_status':'Human visual review required',
        'limitations': [
            {
                'map-art':'Checks measure contrast and placement detail. Review lettering, arrows and seams visually.',
                'loom-banner':'IoU uses deterministic approximations of a survival loom pattern subset.',
                'head-skin':'Checks measure UV coverage, contrast and relief. Review recognition and seams visually.',
            }[track],
        ],
    }


def _luminance_span(pixels):
    values = [_luminance(pixel) for pixel in pixels if pixel[3]]
    return max(values)-min(values) if values else 0


def _luminance(pixel):
    r,g,b,_ = pixel
    return round(.213*r+.715*g+.072*b)


def _png_uri(pixels, width, height):
    def chunk(kind, payload):
        return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload))
    body = b''.join(b'\0'+bytes(c for p in pixels[i:i+width] for c in p)
                    for i in range(0,width*height,width))
    png = (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))
           +chunk(b'IDAT',zlib.compress(body))+chunk(b'IEND',b''))
    return 'data:image/png;base64,' + base64.b64encode(png).decode('ascii')


def art_previews(fixture, data):
    """Return labelled SVGs for use by the offline comparison report."""
    track = fixture['track']
    if track == 'loom-banner':
        key = dict(zip('0123456789abcdef', DYES))
        target = [key[c] for row in fixture['target'] for c in row]
        return [(label, _raster_preview([(*bytes.fromhex(DYES[d]),255) for d in dyes],16,32,label))
                for label,dyes in [('Target',target),('Recipe',banner_pixels(data['base'],data['layers']))]]
    w, h = fixture['width'], fixture['height']
    pixels = rasterize(data,w,h)
    if track == 'map-art':
        return [('Submitted', _raster_preview(pixels,w,h,'Submitted colours')),
                ('Map palette', _raster_preview(quantize(pixels),w,h,'Map palette',seams=True))]
    return [('UV atlas', _raster_preview(pixels,w,h,'Head UV atlas')),
            ('Front', _cube_preview(pixels,('front','left','top'))),
            ('Back', _cube_preview(pixels,('back','right','top')))]


def _raster_preview(pixels, w, h, label, seams=False):
    uri = _png_uri(pixels,w,h)
    guides = ''.join(f'<path d="M{x} 0V{h}" stroke="#ffffff" stroke-width="0.8" stroke-dasharray="4 2"/>'
                     for x in range(128,w,128)) if seams else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(label)}" '
            f'viewBox="0 0 {w} {h}"><image width="{w}" height="{h}" href="{uri}" '
            f'style="image-rendering:pixelated"/>{guides}</svg>')


def _cube_preview(pixels, faces):
    # Affine map of each 8×8 UV face onto an isometric parallelogram.
    transforms = ('5 2.5 0 5 10 30','5 -2.5 0 5 50 50','5 2.5 -5 2.5 50 10')
    layers = []
    for face, transform in zip(faces,transforms):
        for uv in (INNER,OUTER):
            uri = _png_uri(_face(pixels,uv[face]),8,8)
            layers.append(f'<image width="8" height="8" transform="matrix({transform})" href="{uri}" style="image-rendering:pixelated"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Assembled head UV preview" viewBox="0 0 100 100">'+''.join(layers)+'</svg>'
