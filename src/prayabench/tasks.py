"""Synthetic multi-scale building and terraforming fixtures. No saved-world exports or account context."""
import hashlib
import json
from pathlib import Path
from typing import Any

from . import __version__
from .scene import ASSETS, PALETTE
from .art import ART_TASKS, art_fixture, art_palette, art_prompt
from .voxel_tasks import EXTRA_VOXEL, FACINGS, VEHICLES, configure_fixture, task_extra

SCALES = ('small', 'medium', 'large', 'terraforming', 'asset')
TRACKS = ('voxel', 'map-art', 'loom-banner', 'head-skin')

TASK_SPECS: dict[str, dict[str, Any]] = {
    # --- SMALL: street micro-infrastructure, parks, compact buildings ---
    'transit-shelter': {
        'scale': 'small',
        'category': 'civic-micro',
        'bounds': [0, 0, 0, 17, 13, 15],
        'source_limit': 14000,
        'terrain': 'Flat kerbside strip at y=2 behind north bus lane and pavement z=0..4.',
        'brief': (
            'Build a compact kerbside bus/tram transit shelter around x=3..14,z=5..10 facing the north road. '
            'Include a weather-protective canopy with clean structural supports, rear/windscreen glazing, '
            'passenger bench seating, a mounted route/timetable sign, lighting, a ticket_validator prop and '
            'a trash_bin prop on a level paved pad connected to the sidewalk, with low planting behind.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 45,
            'reachable_doors': 0,
            'reachable_interior_cells': 6,
            'assets': ['ticket_validator', 'trash_bin'],
            'signs': 1,
            'seating': 2,
            'lights': 2,
            'flora': 2,
        },
    },
    'pocket-park': {
        'scale': 'small',
        'category': 'landscape-civic',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Flat grass plot at y=2 behind north pavement z=3..4.',
        'brief': (
            'Build a small welcoming park at z>=5. Include a continuous path from the pavement into the park, '
            'two benches, two different believable trees including a conifer and a broadleaf tree, planted beds, '
            'a mailbox_orange on a slender post, and one informative sign mounted on a proper support. Preserve '
            'a clear walking route and avoid isolated floating fixtures.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 60,
            'reachable_doors': 0,
            'reachable_interior_cells': 12,
            'assets': ['mailbox_orange'],
            'signs': 1,
            'conifer_leaves': 8,
            'broadleaf_leaves': 8,
            'seating': 2,
            'flora': 4,
        },
    },
    'sloped-cafe': {
        'scale': 'small',
        'category': 'commercial-slope',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Lateral east-rising slope: ground(x, z) = 2 + x // 8.',
        'brief': (
            'Build an attractive one-storey coffee shop around x=2..14,z=7..17, facing north. '
            'Include a level floor, supported plinth, roof, facade depth, recessed glazing, a service counter '
            'with coffee_maker and pos_terminal props, two customer seats and a table. Connect its entrance to '
            'the sloped pavement. At x=16..22,z=7..18 add a connected pocket garden, tiered conifer, bench and '
            'mailbox_orange on a slender post.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 120,
            'reachable_doors': 1,
            'assets': ['coffee_maker', 'pos_terminal', 'mailbox_orange'],
            'signs': 1,
            'conifer_leaves': 8,
            'seating': 2,
        },
    },
    'shop-renovation': {
        'scale': 'small',
        'category': 'adaptive-reuse',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Flat plot at y=2 with a protected historic shop shell at x=3..15, z=7..17, y=2..8.',
        'brief': (
            'Fit out the supplied older shop shell: a service counter with coffee_maker and pos_terminal props, '
            'two customer seats/table, lights and mounted hours signage. Preserve all protected original shell '
            'cells including the historic Built 2012 placard. Do not describe this as new construction. Keep the '
            'door reachable. You may add interior blocks and front/side landscaping outside x=3..15,z=7..17 but '
            'must not replace protected shell cells.'
        ),
        'extra': (
            '\nThe exact existing shell and protected cells are listed in fixture.json; the shell occupies '
            'x=3..15,z=7..17,y=2..8. Door at [8,3,7], placard at [4,5,8].\n'
        ),
        'requirements': {
            'min_edited_cells': 35,
            'reachable_doors': 1,
            'assets': ['coffee_maker', 'pos_terminal'],
            'signs': 1,
            'seating': 2,
            'lights': 2,
            'forbid_new_build_claim': True,
        },
    },
    'small-house': {
        'scale': 'small',
        'category': 'residential-two-storey',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Flat grass plot at y=2 behind north pavement z=3..4.',
        'brief': (
            'Build a complete two-storey compact house around x=3..16,z=7..18. Include a living room, kitchen, '
            'bedroom with a paired two-cell bed, bathroom, connected interior stairs with headroom to a reachable '
            'upper floor, a roof, varied elevations, a reachable front entrance and a small planted front garden. '
            'Furnish rooms so a player can use the circulation space.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 180,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'beds': 1,
            'flora': 3,
        },
    },
    'utility-substation': {
        'scale': 'small',
        'category': 'utility-infrastructure',
        'bounds': [0, 0, 0, 21, 15, 19],
        'source_limit': 14000,
        'terrain': 'Flat municipal utility parcel at y=2 behind north street z=0..4.',
        'brief': (
            'Build a municipal electrical distribution substation at x=2..19,z=6..17. Include a masonry/concrete '
            'switchgear control room with a reachable service door, computer_monitor desk and exterior identification/hazard '
            'signage, an enclosed outdoor transformer yard with iron_bars or masonry screening, gated access, '
            'transformer/insulator assemblies, yard lighting, planted street frontage buffer and a fire_hydrant near the kerb.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 110,
            'reachable_doors': 1,
            'assets': ['computer_monitor', 'fire_hydrant'],
            'signs': 1,
            'lights': 2,
            'flora': 2,
        },
    },

    # --- MEDIUM: urban blocks, bridges, clinics, rowhouses, steep slopes ---
    'canal-crossing': {
        'scale': 'medium',
        'category': 'spanning-infrastructure',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Embankments at y=3 cut by a protected stone-lined water canal at z=7..10 (water surface y=2).',
        'brief': (
            'Span the protected east-west canal (z=7..10) with a continuous walkable footbridge from the north '
            'bank (z=5..6) to the south bank (z=11..21), keeping bridge structure at y>=4 over the water channel '
            'with continuous side railings/parapets. On the south bank around x=5..17,z=13..20, build a roofed '
            'waterside tea kiosk with a reachable entrance door, service counter with coffee_maker and pos_terminal '
            'props, waterside seating, lanterns and mounted signage.'
        ),
        'extra': (
            '\nProtected zones: north road/pavement z=0..4 (all y) and the canal channel z=7..10 for y=0..3 '
            '(stone bed/walls and water at y=1..2). Do not fill the canal; span above y>=4. Both banks sit at y=3.\n'
        ),
        'requirements': {
            'min_edited_cells': 130,
            'reachable_doors': 1,
            'south_bank_door_min_z': 12,
            'assets': ['coffee_maker', 'pos_terminal'],
            'signs': 1,
            'seating': 2,
            'lights': 2,
        },
    },
    'corner-shophouse': {
        'scale': 'medium',
        'category': 'urban-corner-mixed-use',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Dual-frontage flat corner lot at y=2; north street z=0..4 and west side lane x=0..3 are protected.',
        'brief': (
            'Build a two-storey mixed-use corner shophouse at x=4..17,z=5..17 addressing both the north main '
            'street and the west side lane. Ground floor: corner bakery/cafe with display glazing on both north '
            'and west street fronts, street entrance, counter with coffee_maker and pos_terminal props, and '
            'seating. Upper floor: reachable studio apartment with a paired two-cell bed, connected stairs with '
            'headroom, windows and roof. Add a rear/east court with mailbox_orange on a slender post.'
        ),
        'extra': (
            '\nProtected street rights-of-way: z=0..4 (north road and pavement) AND x=0..3 (west side lane and '
            'sidewalk) across all y. Build only at x>=4 and z>=5.\n'
        ),
        'requirements': {
            'min_edited_cells': 220,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'dual_frontage_glazing': True,
            'assets': ['coffee_maker', 'pos_terminal', 'mailbox_orange'],
            'signs': 1,
            'beds': 1,
        },
    },
    'party-wall-infill': {
        'scale': 'medium',
        'category': 'zero-lot-line-infill',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': 'Narrow urban slot x=5..16 flanked by protected neighbour party walls at x=0..4 and x=17..23 (z=5..17, y=2..10).',
        'brief': (
            'Infill the narrow urban gap x=5..16 between two protected neighbour party-wall buildings with a '
            'two-storey bookshop and upstairs reading loft. Do not modify either neighbour wall or place blind '
            'windows directly against opaque party walls; bring daylight from a recessed north street facade '
            'and a planted rear courtyard at z=17..21. Include ground-floor bookshelf stacks, checkout counter '
            'with pos_terminal, mounted shop signage, and stairs with headroom to a reachable upper reading room '
            'with seating and lights.'
        ),
        'extra': (
            '\nProtected structures: north street z=0..4 (all y), west neighbour building x=0..4,z=5..17,y=0..10, '
            'and east neighbour building x=17..23,z=5..17,y=0..10. Writable infill slot: x=5..16,z=5..21 (plus '
            'rear yard behind z>=18).\n'
        ),
        'requirements': {
            'min_edited_cells': 180,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'assets': ['pos_terminal'],
            'bookshelves': 4,
            'signs': 1,
            'seating': 2,
            'flora': 2,
            'lights': 2,
        },
    },
    'hillside-pavilion': {
        'scale': 'medium',
        'category': 'steep-terrain-terracing',
        'bounds': [0, 0, 0, 23, 17, 21],
        'source_limit': 14000,
        'terrain': '2D hillside rising south and east from y=2 at z<=5 up to y=8..9 at z>=16.',
        'brief': (
            'Build a stepped hillside route from the north pavement (z=3..4, y=2) up the steep slope to a roofed '
            'summit lookout/tea pavilion on the upper crest (z=15..20, y>=8). Retain cut/fill terrace edges with '
            'masonry walls rather than floating slabs, include a mid-slope rest landing with a bench and lanterns, '
            'mounted wayfinding/pavilion signage, conifers, and a reachable pavilion entrance door on the summit (y>=8).'
        ),
        'extra': (
            '\nTerrain varies in both x and z: call ground(x, z) to query exact surface elevation at each column '
            '(rises from y=2 at z<=5 to y=8 at x<15,z>=16 and y=9 at x>=15,z>=16).\n'
        ),
        'requirements': {
            'min_edited_cells': 140,
            'reachable_doors': 1,
            'summit_door_min_y': 8,
            'signs': 1,
            'seating': 1,
            'lights': 2,
            'conifer_leaves': 6,
        },
    },
    'rowhouse-terrace': {
        'scale': 'medium',
        'category': 'residential-rowhouse',
        'bounds': [0, 0, 0, 29, 21, 23],
        'source_limit': 18000,
        'terrain': 'Wide urban residential lot (30x22x24) at y=2 behind north street z=0..4.',
        'brief': (
            'Build a cohesive terrace of three attached two-storey urban rowhouses across x=2..27,z=6..18, '
            'separated by interior party walls. Give each of the three homes its own distinct reachable street '
            'stoop/front entrance door, subtle bay or material variation, interior stairs with headroom to '
            'upstairs bedrooms (at least three paired two-cell beds across the row), illuminated rooms, and '
            'small planted rear yards at z=19..22.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 420,
            'reachable_doors': 3,
            'upper_storey_min_y': 6,
            'beds': 3,
            'signs': 1,
            'lights': 6,
            'flora': 3,
        },
    },
    'medical-clinic': {
        'scale': 'medium',
        'category': 'civic-healthcare',
        'bounds': [0, 0, 0, 27, 19, 23],
        'source_limit': 16000,
        'terrain': 'Flat institutional corner-adjacent lot (28x20x24) at y=2 behind north street z=0..4.',
        'brief': (
            'Build a two-storey neighbourhood urgent-care clinic and pharmacy at x=2..25,z=6..19. Ground floor: '
            'step-free or gently ramped main entrance, reception desk with computer_monitor, waiting seating, '
            'dispensary counter with pos_terminal, wall-mounted or accessible defibrillator prop, and clear '
            'wayfinding signage. Upper floor: consultation rooms reached by wide interior stairs with headroom. '
            'Ensure every enclosed room is well lit.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 320,
            'reachable_doors': 1,
            'upper_storey_min_y': 6,
            'assets': ['computer_monitor', 'pos_terminal', 'defibrillator'],
            'signs': 1,
            'seating': 3,
            'lights': 6,
        },
    },

    # --- LARGE: large-format retail, rail transit, midrises, highrise towers ---
    'grocery-supermarket': {
        'scale': 'large',
        'category': 'commercial-large-format',
        'bounds': [0, 0, 0, 31, 19, 27],
        'source_limit': 20000,
        'terrain': 'Large corner commercial parcel (32x20x28) at y=2; north street z=0..4 and west service lane x=0..3 protected.',
        'brief': (
            'Build a complete neighbourhood grocery supermarket at x=5..29,z=6..24 with customer frontage on '
            'the north street and a service/loading entrance off the west lane. Include at least two checkout '
            'counters with pos_terminal props, parallel stocked retail gondola aisles, rear/side refrigerated '
            'display walls, thorough ceiling lighting across the deep floorplate so no interior aisle is dark, '
            'mounted fascia/hours signage, rooftop HVAC details and kerbside parking_meter on the frontage.'
        ),
        'extra': (
            '\nProtected street rights-of-way: north street z=0..4 and west service lane x=0..3 across all y. '
            'Build only at x>=4 and z>=5.\n'
        ),
        'requirements': {
            'min_edited_cells': 500,
            'reachable_doors': 2,
            'assets': ['pos_terminal', 'parking_meter'],
            'signs': 2,
            'lights': 10,
        },
    },
    'elevated-rail-station': {
        'scale': 'large',
        'category': 'transit-station',
        'bounds': [0, 0, 0, 33, 23, 25],
        'source_limit': 22000,
        'terrain': 'Urban site (34x24x26) at y=2 crossed by a protected elevated stone twin-track rail viaduct at z=15..18 (tracks at y=11).',
        'brief': (
            'Build a commuter elevated rail station integrating the protected stone viaduct (z=15..18, track deck '
            'y=10, rails y=11) without modifying any protected viaduct or track blocks. Build a street-level '
            'concourse/ticket hall at z=5..13 with reachable entrances, ticket_validator fare gates and departure '
            'signage, connected by covered stairs with full headroom up to elevated boarding platform(s) at y=11 '
            'alongside the tracks (z=11..14 and/or z=19..22), complete with platform canopies, yellow safety edge '
            'striping, benches and lighting.'
        ),
        'extra': (
            '\nProtected zones: north road/pavement z=0..4 (all y) and the elevated rail viaduct structure '
            '(deck x=0..33,z=15..18,y=10..12 including rails at z=16..17, plus stone piers at x in 2,11,22,31 '
            'for y=2..9). Build platforms flush alongside z=14 or z=19 at y=10..11.\n'
        ),
        'requirements': {
            'min_edited_cells': 480,
            'reachable_doors': 1,
            'reachable_floor_tiers': [11],
            'assets': ['ticket_validator'],
            'signs': 2,
            'seating': 2,
            'lights': 8,
        },
    },
    'midrise-apartments': {
        'scale': 'large',
        'category': 'residential-midrise',
        'bounds': [0, 0, 0, 29, 29, 25],
        'source_limit': 22000,
        'terrain': 'Urban block parcel (30x30x26) at y=2 behind protected north street z=0..4.',
        'brief': (
            'Build a five-storey mixed-use residential midrise (rising to at least y=23) at x=3..26,z=6..21. '
            'Include an active ground-floor cafe/shop (coffee_maker, pos_terminal) AND a separate street-reachable '
            'residential lobby entrance, a continuous interior stair core with headroom reaching every upper '
            'storey (tiers at y>=6, y>=12 and y>=18), recessed stained-glass windows, continuous guarded balconies, '
            'at least three furnished apartment beds across upper floors, illuminated corridors/rooms, and a '
            'finished rooftop terrace or mechanical bulkhead.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 750,
            'min_peak_height': 23,
            'reachable_doors': 2,
            'reachable_floor_tiers': [6, 12, 18],
            'assets': ['coffee_maker', 'pos_terminal'],
            'beds': 3,
            'signs': 1,
            'lights': 10,
        },
    },
    'civic-office-tower': {
        'scale': 'large',
        'category': 'highrise-tower',
        'bounds': [0, 0, 0, 29, 39, 27],
        'source_limit': 22000,
        'terrain': 'Downtown tower plot (30x40x28) at y=2 behind protected north avenue z=0..4.',
        'brief': (
            'Build an eight-storey civic and office tower rising to y>=32 at x=3..26,z=6..23. Express a distinct '
            'two-storey public podium/lobby with reception desk (computer_monitor) and signage, a stepped tower '
            'shaft above with real mullion/spandrel facade depth across all four elevations, a continuous stair '
            'core reaching upper office/sky-lobby floors (tiers at y>=6, y>=14 and y>=22), lit interior floorplates, '
            'a rooftop mechanical crown, and credible rooftop redstone_torch aircraft warning light(s) at y>=30.'
        ),
        'extra': '',
        'requirements': {
            'min_edited_cells': 950,
            'min_peak_height': 32,
            'reachable_doors': 1,
            'reachable_floor_tiers': [6, 14, 22],
            'aircraft_warning_light_min_y': 30,
            'assets': ['computer_monitor'],
            'signs': 1,
            'lights': 12,
        },
    },

    # --- TERRAFORMING & CHUNK-ERROR REPAIR ---
    'chunk-cliff-scar': {
        'scale': 'terraforming',
        'category': 'terraforming-chunk-error',
        'bounds': [0, 0, 0, 31, 21, 27],
        'source_limit': 16000,
        'repair_rect': [8, 6, 23, 21],
        'terrain': 'Intact rolling hillside (y=5..8) and east-west road severed by a sunken 16x16 chunk error at x=8..23,z=6..21 (dropped to y=1 with floating sheared treetop leaves).',
        'brief': (
            'Repair the corrupted 16x16 chunk at x=8..23,z=6..21. Clear the stranded floating tree-canopy leaves '
            'in mid-air, fill the sunken chunk solidly from stone/dirt up to grade (never leave a hollow 1-block '
            'grass shell over air!), blend terrain elevations smoothly across all four chunk seams to match the '
            'surrounding protected hillside (ground(7,z), ground(24,z), ground(x,5), ground(x,22)), reconnect the '
            'severed east-west gray_concrete road (z=8..10) and smooth_stone kerbs (z=7,11) continuously from x=7 '
            'to x=24, and restore natural grass, trees and meadow flora on the slopes.'
        ),
        'extra': (
            '\nProtected reference ring: all columns outside x=8..23,z=6..21 are immutable intact terrain; '
            'call ground(x, z) on neighbouring intact coordinates (x=7, x=24, z=5, z=22) to read exact target '
            'seam elevations. Clear floating corrupted leaves around y=12..14 inside x=8..23,z=6..21.\n'
        ),
        'requirements': {
            'min_edited_cells': 400,
            'reachable_doors': 0,
            'check_orphan_foliage': True,
            'no_subsurface_voids': True,
            'smooth_chunk_seam': 0.85,
            'reconnected_road': True,
            'surface_top_dressing': 0.85,
            'flora': 4,
        },
    },
    'chunk-river-seam': {
        'scale': 'terraforming',
        'category': 'terraforming-chunk-error',
        'bounds': [0, 0, 0, 31, 19, 25],
        'source_limit': 16000,
        'repair_rect': [8, 5, 23, 20],
        'terrain': 'Protected creek (z=10..13, water y=2..3) and meadow (y=4) blocked by a raised y=10 stone/dirt chunk-error monolith at x=8..23,z=5..20.',
        'brief': (
            'Repair the displaced raised 16x16 chunk monolith at x=8..23,z=5..20 that dams the east-west creek. '
            'Excavate the monolith down to natural grade, restore a continuous water channel (y=2..3 over gravel/sand '
            'bed) connecting the west creek mouth (x=7,z=10..13) to the east creek mouth (x=24,z=10..13), grade '
            'sandy/vegetated banks smoothly into all four chunk seams without hollow voids, and build a walkable '
            'footbridge with railings carrying a path from the north walkway (z=2..3) across the restored creek '
            'to the south meadow.'
        ),
        'extra': (
            '\nProtected surroundings: all columns outside x=8..23,z=5..20 are immutable intact river and meadow. '
            'West/east river water occupies z=10..13 at y=2..3 with sand banks at z=9 and z=14 (y=3) and grass '
            'meadow at y=4. Replace elevated monolith cells up to y=10 with air where excavated.\n'
        ),
        'requirements': {
            'min_edited_cells': 500,
            'reachable_doors': 0,
            'check_orphan_foliage': True,
            'no_subsurface_voids': True,
            'smooth_chunk_seam': 0.85,
            'continuous_waterway': True,
            'surface_top_dressing': 0.85,
            'reachable_interior_cells': 10,
        },
    },
    'coastal-seawall': {
        'scale': 'terraforming',
        'category': 'terraforming-waterfront',
        'bounds': [0, 0, 0, 27, 19, 25],
        'source_limit': 16000,
        'repair_rect': [0, 5, 27, 15],
        'terrain': 'Upland street at z=0..4 (y=7) dropping via an eroded jagged bluff (z=5..15) into a protected tidal bay at z=16..25 (water y=1..3).',
        'brief': (
            'Re-grade and stabilize the eroded coastal bluff at z=5..15 between the upper street (z=0..4, y=7) '
            'and the protected bay water (z=16..25, y=1..3). Clear any overhanging debris, build a continuous '
            'stone/masonry seawall and waterfront promenade along z=13..15 (around y=4..5) with railings and '
            'lanterns, connect the upper pavement to the lower quay via walkable terraced stairs, eliminate '
            'hollow subsurface voids and bare stone/dirt scars, and plant coastal conifers, benches and harbour signage.'
        ),
        'extra': (
            '\nProtected zones: north upland road/sidewalk z=0..4 (y=7, all y protected) and tidal bay water '
            'z=16..25 (y=0 sand, y=1..3 water, protected). Writable coastal bluff zone: x=0..27, z=5..15.\n'
        ),
        'requirements': {
            'min_edited_cells': 300,
            'reachable_doors': 0,
            'check_orphan_foliage': True,
            'no_subsurface_voids': True,
            'surface_top_dressing': 0.80,
            'reachable_promenade_z': [13, 15],
            'seating': 2,
            'lights': 3,
            'signs': 1,
            'conifer_leaves': 8,
        },
    },
    'quarry-reclamation': {
        'scale': 'terraforming',
        'category': 'terraforming-reclamation',
        'bounds': [0, 0, 0, 27, 21, 25],
        'source_limit': 16000,
        'repair_rect': [4, 5, 23, 22],
        'terrain': 'Protected perimeter rim and north street (y=5..7) surrounding an abandoned raw-stone quarry pit at x=4..23,z=5..22 dropping sheer to y=1.',
        'brief': (
            'Reclaim the gouged raw-stone quarry pit at x=4..23,z=5..22 into a naturalized sunken garden and '
            'stormwater pond park. Grade or terrace-retain the sheer pit walls with solid fill (no hollow grass '
            'crusts!), top-dress bare quarry stone with grass, moss and planted beds, form a clean pond basin '
            '(at least 12 water blocks), plant both conifer and broadleaf trees, and build a continuous walkable '
            'stepped path from the north street (z=3..4, y=5) down into the sunken park with benches and lanterns.'
        ),
        'extra': (
            '\nProtected zones: north street z=0..4 and outer grass rim (x=0..3, x=24..27, z=23..25). '
            'Writable quarry pit: x=4..23, z=5..22.\n'
        ),
        'requirements': {
            'min_edited_cells': 350,
            'reachable_doors': 0,
            'no_subsurface_voids': True,
            'surface_top_dressing': 0.80,
            'reachable_interior_cells': 16,
            'water_cells': 12,
            'conifer_leaves': 6,
            'broadleaf_leaves': 6,
            'seating': 2,
            'lights': 2,
            'flora': 4,
        },
    },
}

TASK_SPECS.update(EXTRA_VOXEL)
TASK_SPECS.update(ART_TASKS)
TASKS: dict[str, str] = {k: v['brief'] for k, v in TASK_SPECS.items()}


def contract_text(bounds: list[int], source_limit: int) -> str:
    xmax, ymax, zmax = bounds[3], bounds[4], bounds[5]
    asset_list = ', '.join(ASSETS)
    return f'''You are completing a one-pass offline Minecraft-style voxel construction benchmark.
Return ONLY Python source defining build(put, box, head, sign, ground).
No imports, tools, file access, external calls, Markdown or top-level calls.
Use loops/functions and range,min,max,abs,int,float,bool,len,sum,any,all,
enumerate,zip,reversed,list,dict,set,tuple,round,sorted,str.
Maximum source length: {source_limit} characters.

Coordinates: x=0..{xmax},y=0..{ymax},z=0..{zmax}. North=-z.
ground(x, z=5) returns the initial fixture surface block y at (x, z); ground(x)
also works on 1D/flat plots, while 2D and terraforming tasks require ground(x, z).
Protected street, rail, neighbour and reference-terrain cells listed in fixture.json
are immutable.
Player height is two blocks. Supply paired lower/upper halves for doors with
matching facing, and paired foot/head cells for beds.
Use supported block names from palette.txt. Standard Minecraft state syntax.

put(x,y,z,state,component=''): one block.
box(x0,y0,z0,x1,y1,z1,state,component=''): inclusive cuboid.
head(x,y,z,asset,state='player_head[rotation=0]',component=''): semantic prop;
assets: {asset_list}. No external skin textures.
sign(x,y,z,state,lines,component=''): at most four short text lines.
Later writes replace earlier writes. Air explicitly removes a writable cell.

Construction & terraforming rules: all fixtures have plausible supports. Place wall
signs/heads on connected solid walls, never panes or isolated floating filler blocks.
Ceiling hanging signs attach overhead; wall hanging signs attach to side supports.
Props sit flush on counters/tables/floors; mailbox_orange and parking_meter use
slender bars/chains/panes/fences, not solid-block plinths. Gravity blocks (sand,
gravel) need non-passable support underneath. Plant flora on soil, grass or moss.
Door jambs in glazed walls are full blocks. Light enclosed rooms thoroughly so
interior spaces are not dark. On highrise towers (y>=30), mount rooftop aircraft
warning redstone torches credibly; omit them on low-rise buildings. On terraforming
and chunk-error tasks, clear floating debris, fill terrain solidly from below
without hollow air cavities under turf, match adjacent seam elevations smoothly,
and top-dress raw stone/dirt scars. Preserve historic construction dates during
renovations and never claim an older shell is newly built.
'''


def ground_at(task: str, x: int, z: int = 5) -> int:
    if task not in TASK_SPECS:
        raise ValueError(f'unknown task: {task}')
    bx1, _, bz1 = TASK_SPECS[task]['bounds'][3], TASK_SPECS[task]['bounds'][4], TASK_SPECS[task]['bounds'][5]
    xc = max(0, min(bx1, int(x)))
    zc = max(0, min(bz1, int(z)))
    if task == 'sloped-cafe':
        return 2 + xc // 8
    if task == 'canal-crossing':
        return 2 if 7 <= zc <= 10 else 3
    if task == 'hillside-pavilion':
        if zc <= 5:
            return 2
        return 2 + min(6, (zc - 4) // 2) + (1 if xc >= 15 else 0)
    if task == 'chunk-cliff-scar':
        if 8 <= xc <= 23 and 6 <= zc <= 21:
            return 1
        return 5 if zc <= 5 else 5 + (zc - 6) // 6
    if task == 'chunk-river-seam':
        if 8 <= xc <= 23 and 5 <= zc <= 20:
            return 10
        if 10 <= zc <= 13 or zc in (9, 14):
            return 3
        return 4
    if task == 'coastal-seawall':
        if zc <= 4:
            return 7
        if zc >= 16:
            return 3
        # Jagged eroded coastal bluff dropping irregularly from y=7 to y=2
        raw = 7 - (zc - 4) // 2 - ((xc + zc) % 2 if 7 <= zc <= 13 else 0)
        return max(2, min(7, raw))
    if task == 'quarry-reclamation':
        if 4 <= xc <= 23 and 5 <= zc <= 22:
            if xc in (4, 23) or zc in (5, 22):
                return 3
            return 1
        return 5 if zc <= 8 else 6
    return 2


def ground_grid(task: str) -> list[list[int]]:
    bounds = TASK_SPECS[task]['bounds']
    w, d = bounds[3] + 1, bounds[5] + 1
    return [[ground_at(task, x, z) for z in range(d)] for x in range(w)]


def _rect_seam_pairs(rx0: int, rz0: int, rx1: int, rz1: int, w: int, d: int) -> list[list[list[int]]]:
    pairs: list[list[list[int]]] = []
    if rx0 > 0:
        for z in range(rz0, rz1 + 1):
            pairs.append([[rx0, z], [rx0 - 1, z]])
    if rx1 < w - 1:
        for z in range(rz0, rz1 + 1):
            pairs.append([[rx1, z], [rx1 + 1, z]])
    if rz0 > 0:
        for x in range(rx0, rx1 + 1):
            pairs.append([[x, rz0], [x, rz0 - 1]])
    if rz1 < d - 1:
        for x in range(rx0, rx1 + 1):
            pairs.append([[x, rz1], [x, rz1 + 1]])
    return pairs


def fixture(task: str, facing: str | None = None) -> dict[str, Any]:
    if task not in TASK_SPECS:
        raise ValueError('unknown task')
    if facing is not None and (task not in VEHICLES or facing not in FACINGS):
        raise ValueError('facing is only supported on vehicle tasks')
    facing = facing or 'north'
    if task in ART_TASKS:
        return art_fixture(task)
    spec = TASK_SPECS[task]
    bounds = list(spec['bounds'])
    w, h, d = bounds[3] + 1, bounds[4] + 1, bounds[5] + 1
    cells: dict[tuple[int, int, int], list[Any]] = {}
    protected: set[tuple[int, int, int]] = set()

    def put(x: int, y: int, z: int, s: str, lines: list[str] | None = None) -> None:
        cells[x, y, z] = [x, y, z, s, lines, 'fixture', None]

    has_west_lane = task in ('corner-shophouse', 'grocery-supermarket')

    # --- Specialized terraforming / chunk-error terrain generation ---
    if task == 'chunk-cliff-scar':
        for x in range(w):
            for z in range(d):
                in_scar = 8 <= x <= 23 and 6 <= z <= 21
                top = ground_at(task, x, z)
                for y in range(top + 1):
                    if in_scar:
                        mat = 'coal_ore' if (y == 1 and (x + z) % 11 == 0) else ('iron_ore' if (y == 1 and (x * z) % 17 == 1) else 'stone')
                    elif y == top:
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
                    put(x, y, z, mat)
                if not in_scar:
                    for y in range(h):
                        protected.add((x, y, z))
                else:
                    protected.add((x, 0, z))
        # Stranded floating chunk-error tree crown inside writable scar (no trunk)
        for x in range(13, 16):
            for z in range(14, 17):
                put(x, 12, z, 'oak_leaves[persistent=true]')
                if x == 14 or z == 15:
                    put(x, 13, z, 'oak_leaves[persistent=true]')

    elif task == 'chunk-river-seam':
        for x in range(w):
            for z in range(d):
                in_scar = 8 <= x <= 23 and 5 <= z <= 20
                if in_scar:
                    top = 10
                    for y in range(top + 1):
                        mat = 'coarse_dirt' if y == 10 and (x + z) % 3 == 0 else ('dirt' if y >= 9 else 'stone')
                        put(x, y, z, mat)
                    protected.add((x, 0, z))
                else:
                    if 10 <= z <= 13:
                        put(x, 0, z, 'stone')
                        put(x, 1, z, 'gravel')
                        put(x, 2, z, 'water')
                        put(x, 3, z, 'water')
                    elif z in (9, 14):
                        for y in range(4):
                            put(x, y, z, 'sand' if y == 3 else 'stone')
                    else:
                        for y in range(5):
                            if y == 4:
                                mat = 'gray_concrete' if z < 2 else ('smooth_stone' if z < 4 else 'grass_block')
                            elif y == 3:
                                mat = 'dirt'
                            else:
                                mat = 'stone'
                            put(x, y, z, mat)
                    for y in range(h):
                        protected.add((x, y, z))
        for x in (11, 12):
            for z in (8, 9):
                put(x, 14, z, 'spruce_leaves[persistent=true]')

    elif task == 'coastal-seawall':
        for x in range(w):
            for z in range(d):
                if z >= 16:
                    put(x, 0, z, 'sand')
                    for y in range(1, 4):
                        put(x, y, z, 'water')
                    for y in range(h):
                        protected.add((x, y, z))
                else:
                    top = ground_at(task, x, z)
                    for y in range(top + 1):
                        if z <= 4:
                            mat = ('gray_concrete' if z < 3 else 'smooth_stone') if y == top else ('dirt' if y == top - 1 else 'stone')
                        else:
                            mat = 'coarse_dirt' if (y == top and (x + z) % 2 == 0) else ('dirt' if y >= top - 1 else 'stone')
                        put(x, y, z, mat)
                    if z <= 4:
                        for y in range(h):
                            protected.add((x, y, z))
                    else:
                        protected.add((x, 0, z))
        for x in (9, 10):
            put(x, 11, 9, 'spruce_leaves[persistent=true]')

    elif task == 'quarry-reclamation':
        for x in range(w):
            for z in range(d):
                in_pit = 4 <= x <= 23 and 5 <= z <= 22
                top = ground_at(task, x, z)
                for y in range(top + 1):
                    if in_pit:
                        mat = 'andesite' if (x + z) % 5 == 0 else ('coal_ore' if (y == 1 and (x * z) % 13 == 0) else 'stone')
                    elif y == top:
                        mat = 'gray_concrete' if z < 3 else ('smooth_stone' if z < 5 else 'grass_block')
                    elif y == top - 1:
                        mat = 'dirt'
                    else:
                        mat = 'stone'
                    put(x, y, z, mat)
                if not in_pit:
                    for y in range(h):
                        protected.add((x, y, z))
                else:
                    protected.add((x, 0, z))

    else:
        # Standard architectural / urban / canal / hillside site generation
        for x in range(w):
            for z in range(d):
                top = ground_at(task, x, z)
                if task == 'canal-crossing' and 7 <= z <= 10:
                    put(x, 0, z, 'stone_bricks')
                    put(x, 1, z, 'water')
                    put(x, 2, z, 'water')
                    for y in range(4):
                        protected.add((x, y, z))
                else:
                    for y in range(top + 1):
                        if y == top:
                            if z < 3 or (has_west_lane and x < 2):
                                surf = 'gray_concrete'
                            elif z < 5 or (has_west_lane and x < 4):
                                surf = 'smooth_stone'
                            elif task == 'canal-crossing' and z in (6, 11):
                                surf = 'stone_bricks'
                            else:
                                surf = 'grass_block'
                        elif y < top - 1:
                            surf = 'stone'
                        else:
                            surf = 'stone_bricks' if (task == 'canal-crossing' and z in (6, 11)) else 'dirt'
                        put(x, y, z, surf)
                if z < 5 or (has_west_lane and x < 4):
                    for y in range(h):
                        protected.add((x, y, z))

    if task == 'shop-renovation':
        for x in range(3, 16):
            for z in range(7, 18):
                put(x, 2, z, 'stone_bricks')
                put(x, 8, z, 'stone_bricks')
                if x in (3, 15) or z in (7, 17):
                    for y in range(3, 8):
                        put(x, y, z, 'white_concrete')
        for y in (3, 4):
            put(8, y, 7, f'oak_door[facing=north,half={"lower" if y == 3 else "upper"}]')
        put(4, 5, 8, 'oak_wall_sign[facing=south]', ['Built', '-----', '2012', ''])
        for pos in list(cells):
            if 3 <= pos[0] <= 15 and 7 <= pos[2] <= 17:
                protected.add(pos)
        for z in (5, 6):
            put(8, 2, z, 'smooth_stone')

    elif task == 'party-wall-infill':
        for x in range(0, 5):
            for z in range(5, 18):
                for y in range(2, 10):
                    if x in (0, 4) or z in (5, 17) or y in (2, 9):
                        put(x, y, z, 'bricks' if y < 9 else 'stone_bricks')
                if x == 4 or z in (5, 17):
                    put(x, 10, z, 'stone_brick_slab[type=bottom]')
                for y in range(0, 11):
                    protected.add((x, y, z))
        for x in range(17, 24):
            for z in range(5, 18):
                for y in range(2, 10):
                    if x in (17, 23) or z in (5, 17) or y in (2, 9):
                        put(x, y, z, 'stone_bricks' if y < 9 else 'smooth_stone')
                if x == 17 or z in (5, 17):
                    put(x, 10, z, 'smooth_stone_slab[type=bottom]')
                for y in range(0, 11):
                    protected.add((x, y, z))

    elif task == 'elevated-rail-station':
        for x in range(w):
            for z in range(15, 19):
                put(x, 10, z, 'stone_bricks')
                protected.add((x, 10, z))
                protected.add((x, 11, z))
                protected.add((x, 12, z))
            for z_track in (16, 17):
                rail_type = 'powered_rail[shape=east_west,powered=true]' if x % 8 == 0 else 'rail[shape=east_west]'
                put(x, 11, z_track, rail_type)
        for pier_x in (2, 11, 22, 31):
            for z in range(15, 19):
                for y in range(2, 10):
                    put(pier_x, y, z, 'stone_bricks')
                    protected.add((pier_x, y, z))

    configure_fixture(task, facing, cells, protected, put)
    if task in EXTRA_VOXEL:
        ground = [[-1]*d for _ in range(w)]
        # Surface elevation uses the actual frozen scene, including rail or roof.
        for (x,y,z), cell in cells.items():
            ground[x][z] = max(y, ground[x][z])
    else:
        ground = ground_grid(task)

    if task == 'chunk-cliff-scar':
        street_seeds = [[x, z] for x in range(w) for z in range(d) if (x <= 7 or x >= 24) and 7 <= z <= 11]
    elif task == 'chunk-river-seam':
        street_seeds = [[x, z] for x in range(w) for z in range(4)]
    elif task == 'quarry-reclamation':
        street_seeds = [[x, z] for x in range(w) for z in range(5)]
    else:
        street_seeds = [
            [x, z]
            for x in range(w)
            for z in range(d)
            if z <= 4 or (has_west_lane and x <= 3)
        ]

    out: dict[str, Any] = {
        'task': task,
        'scale': spec['scale'],
        'category': spec['category'],
        'bounds': bounds,
        'source_limit': spec['source_limit'],
        'ground': ground,
        'street_seeds': street_seeds,
        'requirements': spec['requirements'],
        'cells': list(cells.values()),
        'protected': [list(p) for p in sorted(protected)],
    }
    out['track'] = 'voxel'
    if task in VEHICLES:
        out['facing'] = facing
    if 'repair_rect' in spec:
        rx0, rz0, rx1, rz1 = spec['repair_rect']
        out['repair_rect'] = [rx0, rz0, rx1, rz1]
        out['seam_pairs'] = _rect_seam_pairs(rx0, rz0, rx1, rz1, w, d)
    if task == 'chunk-cliff-scar':
        out['road_endpoints'] = {
            'start': [[7, 8], [7, 9], [7, 10]],
            'end': [[24, 8], [24, 9], [24, 10]],
        }
    if task == 'chunk-river-seam':
        out['water_endpoints'] = {
            'start': [[7, 10], [7, 11], [7, 12], [7, 13]],
            'end': [[24, 10], [24, 11], [24, 12], [24, 13]],
        }
    return out


def sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def init_run(path: str | Path, task: str, facing: str | None = None) -> Path:
    if task not in TASK_SPECS:
        raise ValueError('unknown task')
    f = fixture(task, facing)
    out_path = Path(path)
    out_path.mkdir(parents=True, exist_ok=False)
    spec = TASK_SPECS[task]
    track = f['track']
    (out_path / 'fixture.json').write_text(json.dumps(f, indent=2))
    metadata = {}
    if track == 'voxel':
        bounds = spec['bounds']
        source_limit = spec['source_limit']
        prompt = contract_text(bounds, source_limit) + f'\nTASK: {task} ({spec["scale"]} · {spec["category"]})\n' + spec['brief'] + spec['extra']
        if task in EXTRA_VOXEL:
            prompt += '\nThis challenge uses its own site geometry and restrictions described above.\n'
        if task in VEHICLES:
            prompt = prompt.replace('build(put, box, head, sign, ground)', 'build(put, box, head, sign, ground, facing)')
            prompt += task_extra(task, f['facing'])
            metadata['facing'] = f['facing']
        palette = '\n'.join(sorted(PALETTE)) + '\n'
        metadata.update(bounds=bounds, source_limit=source_limit,
                        scene_cell_limit=min(90000, max(30000, (bounds[3]+1)*(bounds[4]+1)*(bounds[5]+1)*2)))
    else:
        prompt = art_prompt(f)
        palette = art_palette(track)
    (out_path / 'prompt.txt').write_text(prompt)
    (out_path / 'palette.txt').write_text(palette)
    hashes = {n: sha(out_path / n) for n in ('fixture.json', 'prompt.txt', 'palette.txt')}
    (out_path / 'manifest.json').write_text(json.dumps({
        'schema_version': 4,
        'package_version': __version__,
        'task': task,
        'scale': spec['scale'],
        'category': spec['category'],
        'track': track,
        'hashes': hashes,
        **metadata,
    }, indent=2))
    return out_path


def init_suite(
    directory: str | Path, scale: str | None = None, category: str | None = None,
    track: str | None = None, all_facings: bool = False,
) -> list[Path]:
    if scale is not None and scale not in SCALES:
        raise ValueError(f'unknown scale: {scale}')
    selected = [
        name for name, spec in TASK_SPECS.items()
        if (scale is None or spec['scale'] == scale)
        and (category is None or spec['category'] == category)
        and (track is None or spec.get('track', 'voxel') == track)
    ]
    if not selected:
        raise ValueError('no tasks matched filter')
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    created = []
    for task_name in selected:
        if all_facings and task_name in VEHICLES:
            created.extend(init_run(root / f'{task_name}-{face}', task_name, face) for face in FACINGS)
        else:
            created.append(init_run(root / task_name, task_name))
    (root / 'suite.json').write_text(json.dumps({
        'schema_version': 1,
        'package_version': __version__,
        'scale_filter': scale,
        'category_filter': category,
        'track_filter': track,
        'all_facings': all_facings,
        'tasks': selected,
        'runs': [p.name for p in created],
    }, indent=2))
    return created


def verify_run(path: str | Path) -> dict[str, Any]:
    from .scene import load_json
    run_path = Path(path)
    m = load_json(run_path / 'manifest.json')
    if set(m['hashes']) != {'fixture.json', 'prompt.txt', 'palette.txt'}:
        raise ValueError('unexpected manifest inputs')
    for n, h in m['hashes'].items():
        if sha(run_path / n) != h:
            raise ValueError('frozen input changed: ' + n)
    return load_json(run_path / 'fixture.json')
