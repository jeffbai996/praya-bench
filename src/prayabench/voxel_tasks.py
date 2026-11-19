"""Synthetic vehicle, civil engineering, fixture and retrofit challenges."""

FACINGS = ('north', 'east', 'south', 'west')

VEHICLES = {
    'box-truck': (4, 9, 4, 'Make a distinct two-row cab and a taller, enclosed cargo box. Suggested details include shulker panels, hopper tanks and layered snow on the wind deflector.'),
    'city-bus': (4, 13, 4, 'Put a two-block-high passenger door on the right (kerb) side, a destination board at the front and a glazed passenger cabin.'),
    'ambulance': (3, 7, 4, 'Include a rear access door and at least two mounted red emergency lights.'),
    'rail-coach': (5, 15, 4, 'Build a glazed coach with an end coupling on both ends and at least two wheelsets aligned over the rails.'),
    'harbour-ferry': (7, 15, 5, 'Make a waterline hull, a glazed wheelhouse at the bow half, and a mounted navigation light on each side.'),
}


def _spec(scale, category, bounds, brief, **requirements):
    return {
        'scale': scale, 'category': category, 'bounds': [0, 0, 0, *bounds],
        'source_limit': 16000, 'brief': brief, 'extra': '',
        'terrain': 'Synthetic site. Read the fixed geometry and restrictions in the brief.',
        'requirements': {'reachable_doors': 0, **requirements},
    }


EXTRA_VOXEL = {
    name: _spec('small' if length < 10 else 'medium', 'vehicle', (22, 12, 22),
                f'Build a {width}×{length} (width × length) {name.replace("-", " ")} '
                f'within {height} blocks of height. Keep the body connected. '
                'Place front glazing near the nose and use at least two kinds of partial-block details. '
                + brief + (' Ground vehicles need two separated wheelsets made from black concrete, black wool, or coal blocks.'
                           if name != 'harbour-ferry' else ''))
    for name, (width, length, height, brief) in VEHICLES.items()
}
EXTRA_VOXEL.update({
    'washroom-fitout': _spec('small', 'micro-fixture', (16, 12, 14),
        'Fit out an existing washroom. Use x=4..12,z=7..11,y=3..6 only. '
        'Provide a basin represented by a water cauldron at x=4..6, a mounted glass mirror '
        'against the west flank above and within one column of the basin, and a toilet '
        'represented by a stair seat and trapdoor lid in the separate east bay at x=10..12. '
        'Keep the central aisle x=8 at y=3..4 unobstructed and mount at least one lamp.'),
    'roof-hvac': _spec('small', 'micro-fixture', (16, 12, 14),
        'Add a rooftop HVAC assembly on the protected flat roof at y=6. Use x=4..12,z=7..11,y=7..10 only. '
        'Build a connected metal housing and a north-facing grille of iron bars or iron trapdoors '
        'at z=7. The assembly must bear on the roof. Keep the service lane x=8 at y=7..8 open.'),
    'diagonal-road': _spec('medium', 'civil-alignment', (24, 12, 23),
        'Connect two protected road stubs with a three-block-wide paved diagonal dogleg. '
        'Use gray or black concrete at y=2 and keep two blocks of headroom. '
        'For each z=4..19, pave center x=6+min(8,max(0,z-7)) and one block to either side. '
        'Keep extra paving within one block of the required footprint.'),
    'curved-tunnel': _spec('medium', 'civil-alignment', (24, 12, 23),
        'Join the protected north and south tunnel portals with a curved bore through the hill. '
        'For z=4..19, the centerline is x=6+min(8,max(0,z-7)). '
        'Lay stone-brick pavement at y=2, x=center±1 and clear those columns at y=3..5. '
        'Keep a full roof at y=6 above all three travel columns and retain the surrounding hill.'),
    'junction-wayfinding': _spec('medium', 'civil-sightline', (20, 12, 22),
        'Mount a north-facing oak_sign or oak_wall_sign reading Ferry and Right (on any two lines) '
        'in the sign position x=11,y=5,z=14. For a standing sign use rotation=8 and component traffic-sign. '
        'Keep it visible along the straight approach from x=11,y=5,z=5. '
        'Build a coherent roadside support with a solid base while preserving the protected travel lane.'),
    'specimen-conifer': _spec('medium', 'specimen-tree', (21, 20, 21),
        'Build one specimen spruce rooted at (10,3,10). Use spruce logs and persistent spruce leaves only '
        'above grade. Grow a continuous rooted trunk, a wide lower tier and a pointed taper. '
        'Keep foliage connected to the trunk, with no detached leaves.'),
    'specimen-broadleaf': _spec('medium', 'specimen-tree', (21, 20, 21),
        'Build one specimen oak rooted at (10,3,10). Use oak logs and persistent oak leaves only above grade. '
        'Grow a grounded forked trunk and a spreading crown, at least seven blocks across. '
        'Keep foliage connected to the trunk, with no detached leaves.'),
    'facade-depth-retrofit': _spec('medium', 'surgical-retrofit', (20, 15, 17),
        'Retrofitting brief: add facade depth to the flat protected building. Work only in x=4..16,z=5..6,y=3..9. '
        'Build two grounded side piers at x=4 and x=16 at z=6 from y=3..7 and a projection spanning '
        'x=5..15 at y=8,z=5. Keep the original entrance path x=10 at y=3..4 clear. '
        'At least 12 existing front-window cells must remain visible from the street. '
        'Reuse the original building, with at most 80 meaningful edits.'),
    'rowhouse-shop-conversion': _spec('medium', 'surgical-retrofit', (20, 15, 17),
        'Fit out the ground floor of an occupied rowhouse as a small shop. Only edit x=5..15,z=8..13,y=3..5 '
        'outside the marked protected east stair lane (x>=14). Keep the original entrance and stair lane working. '
        'Provide coffee_maker and pos_terminal props on counters, one mounted business sign and one lamp. '
        'Use at most 55 meaningful edits. Preserve the original 2012 placard.',
        reachable_doors=1, assets=['coffee_maker','pos_terminal'], signs=1, lights=1, forbid_new_build_claim=True),
    'inspector-repair': _spec('small', 'surgical-retrofit', (16, 12, 15),
        'Apply the inspector’s three corrections to the supplied café. Remove the obsolete floating '
        'sign at (5,5,6) and the unsupported rod at (12,6,9). Move the sign text to (5,5,7), '
        'north-facing against the existing wall, and clear the doorway approach blocker at (8,3,6). '
        'Only those four positions are writable.'),
})


def road_center(z):
    return 6 + min(8, max(0, z - 7))


def rotate_xz(x, z, facing):
    """Rotate from north-facing canonical coordinates on the 23×23 fixture."""
    for _ in range(FACINGS.index(facing)):
        x, z = 22 - z, x
    return x, z


def vehicle_rect(task):
    width, length, _, _ = VEHICLES[task]
    return (11 - width // 2, 11 - length // 2, width, length)


def configure_fixture(task, facing, cells, protected, put):
    """Overlay specialized substrates and protections onto the standard fixture."""
    if task in VEHICLES:
        cells.clear()
        protected.clear()
        for x in range(23):
            for z in range(23):
                tx, tz = rotate_xz(x, z, facing)
                put(tx, 0, tz, 'stone')
                put(tx, 1, tz, 'water' if task == 'harbour-ferry' else 'stone')
                if task == 'harbour-ferry':
                    put(tx, 2, tz, 'water')
                elif task == 'rail-coach':
                    put(tx, 2, tz, 'gravel')
                    if x in (10, 12):
                        axis = 'north_south' if facing in ('north', 'south') else 'east_west'
                        put(tx, 3, tz, f'rail[shape={axis}]')
                else:
                    put(tx, 2, tz, 'smooth_stone' if x >= 14 else 'gray_concrete')
        protected.update(cells)
        if task == 'harbour-ferry':
            x0, z0, width, length = vehicle_rect(task)
            for x in range(x0, x0+width):
                for z in range(z0, z0+length):
                    tx, tz = rotate_xz(x, z, facing)
                    protected.discard((tx, 2, tz))
        return

    if task in ('diagonal-road', 'curved-tunnel'):
        cells.clear()
        protected.clear()
        for z in range(24):
            for x in range(25):
                stub = z < 4 or z >= 20
                lane = abs(x - road_center(z)) <= 1
                top = 8 if task == 'curved-tunnel' else 2
                for y in range(top + 1):
                    if task == 'curved-tunnel' and stub and lane and 3 <= y <= 5:
                        continue
                    surface = ('stone_bricks' if task == 'curved-tunnel' else 'gray_concrete') if stub and lane else 'grass_block'
                    put(x, y, z, surface if y == 2 and (stub or task == 'diagonal-road') else 'stone')
                protected.add((x, 0, z))
                if stub or task == 'curved-tunnel' and abs(x-road_center(z)) > 2:
                    protected.update((x, y, z) for y in range(13))
                elif task == 'curved-tunnel':
                    protected.update((x, y, z) for y in range(7,13))
        return

    if task == 'junction-wayfinding':
        for z in range(5, 23):
            for x in range(5, 10):
                put(x, 2, z, 'gray_concrete')
                protected.update((x, y, z) for y in range(13))
        return

    if task.startswith('specimen-'):
        protected.update(cells)
        return

    if task in ('washroom-fitout', 'roof-hvac'):
        for x in range(3, 14):
            for z in range(6, 13):
                put(x, 2, z, 'smooth_stone')
                if task == 'roof-hvac':
                    put(x, 6, z, 'iron_block')
                if x in (3, 13) or z in (6, 12):
                    for y in range(3, 7):
                        if (x, z) != (8, 6) or y > 4:
                            put(x, y, z, 'white_concrete')
        protected.update(cells)
        return

    if task in ('facade-depth-retrofit', 'rowhouse-shop-conversion', 'inspector-repair'):
        small = task == 'inspector-repair'
        x0, x1, front, rear, entry = (4, 12, 8, 12, 8) if small else (4, 16, 7, 14, 10)
        roof = 12 if task == 'rowhouse-shop-conversion' else 8
        for x in range(x0, x1 + 1):
            for z in range(front, rear + 1):
                for y in range(3, roof+1):
                    if x in (x0, x1) or z in (front, rear) or y == roof:
                        windows = z == front and y in (5, 6) and x not in (x0, x1, entry)
                        put(x, y, z, 'gray_stained_glass' if windows and not small else 'white_concrete')
        if task == 'rowhouse-shop-conversion':
            put(5, 5, 8, 'oak_wall_sign[facing=east]', ['Built', '2012'])
            for i in range(4):
                put(14, 3+i, 9+i, 'oak_stairs[facing=south]')
            for x in range(5, 16):
                for z in range(8, 14):
                    if (x, z) not in ((14, 11), (14, 12)):
                        put(x, 7, z, 'oak_planks')
        for y, half in ((3, 'lower'), (4, 'upper')):
            put(entry, y, front, f'oak_door[facing=north,half={half}]')
        protected.update(cells)
        if small:
            put(5, 5, 6, 'oak_wall_sign[facing=north]', ['Cafe hours'])
            put(12, 6, 9, 'end_rod[facing=up]')
            put(8, 3, 6, 'stone_bricks')


def task_extra(task, facing):
    if task not in VEHICLES:
        return ''
    x0,z0,width,length = vehicle_rect(task)
    corners = [rotate_xz(x,z,facing) for x in (x0,x0+width-1) for z in (z0,z0+length-1)]
    min_y = 2 if task == 'harbour-ferry' else 4 if task == 'rail-coach' else 3
    return (
        f'\nFrozen orientation: {facing}; build takes a sixth argument facing. '
        f'Footprint corners in scene coordinates: {corners}. Lowest occupied y={min_y}. '
        'For ferry only, the hull may replace water at y=2 inside its footprint. '
        'Right/left are relative to the direction of travel. Use blank wall signs as trim if desired.\n'
    )
