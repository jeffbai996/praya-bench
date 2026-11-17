from pathlib import Path
import re
import tempfile
import unittest

from prayabench.evaluate import assess
from prayabench.render import svg
from prayabench.scene import PALETTE, state_parts, validate_cells
from prayabench.tasks import SCALES, TASKS, TASK_SPECS, fixture, ground_at, init_run, init_suite, verify_run


class MultiscaleAndTerraformingTests(unittest.TestCase):
    def test_all_twenty_tasks_span_four_scales_and_initialize_cleanly(self):
        expected_by_scale = {
            'small': {
                'transit-shelter', 'pocket-park', 'sloped-cafe',
                'shop-renovation', 'small-house', 'utility-substation',
            },
            'medium': {
                'canal-crossing', 'corner-shophouse', 'party-wall-infill',
                'hillside-pavilion', 'rowhouse-terrace', 'medical-clinic',
            },
            'large': {
                'grocery-supermarket', 'elevated-rail-station',
                'midrise-apartments', 'civic-office-tower',
            },
            'terraforming': {
                'chunk-cliff-scar', 'chunk-river-seam',
                'coastal-seawall', 'quarry-reclamation',
            },
        }
        all_expected = set().union(*expected_by_scale.values())
        self.assertEqual(len(all_expected), 20)
        self.assertEqual(set(TASKS), all_expected)
        self.assertEqual(set(SCALES), {'small', 'medium', 'large', 'terraforming'})
        for scale_name, names in expected_by_scale.items():
            actual = {k for k, v in TASK_SPECS.items() if v['scale'] == scale_name}
            self.assertEqual(actual, names)

        with tempfile.TemporaryDirectory() as d:
            for task_name in sorted(all_expected):
                run_dir = init_run(Path(d) / task_name, task_name)
                loaded = verify_run(run_dir)
                bx0, by0, bz0, bx1, by1, bz1 = loaded['bounds']
                self.assertEqual((bx0, by0, bz0), (0, 0, 0))
                self.assertEqual(len(loaded['ground']), bx1 + 1)
                self.assertEqual(len(loaded['ground'][0]), bz1 + 1)
                for c in loaded['cells']:
                    x, y, z, st = c[:4]
                    self.assertTrue(0 <= x <= bx1 and 0 <= y <= by1 and 0 <= z <= bz1, (task_name, c[:4]))
                    self.assertIn(state_parts(st)[0], PALETTE)

    def test_variable_bounds_and_task_source_budgets_enforced(self):
        shelter_fix = fixture('transit-shelter')
        rep_compact = assess(shelter_fix, {'cells': [[19, 3, 8, 'stone_bricks']]})
        self.assertIn('out_of_bounds', {i['code'] for i in rep_compact['issues']})

        tower_fix = fixture('civic-office-tower')
        rep_tower = assess(tower_fix, {
            'cells': [[28, 35, 24, 'white_concrete']],
            'source_characters': 18000,
        })
        codes_tower = {i['code'] for i in rep_tower['issues']}
        self.assertNotIn('out_of_bounds', codes_tower)
        self.assertNotIn('source_budget_exceeded', codes_tower)

        cafe_over = assess(fixture('sloped-cafe'), {'cells': [], 'source_characters': 18000})
        self.assertIn('source_budget_exceeded', {i['code'] for i in cafe_over['issues']})

    def test_floating_backing_block_and_gravity_sand_defects_caught(self):
        cells = [
            [8, 9, 10, 'white_concrete'],
            [8, 9, 9, 'oak_wall_sign[facing=north]', ['Hover', 'Sign', '', '']],
            [12, 7, 10, 'sand'],
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=north,half=upper]'],
        ]
        rep = assess(fixture('small-house'), {'cells': cells})
        codes = {i['code'] for i in rep['issues']}
        self.assertIn('floating_backing_block', codes)
        self.assertIn('floating_gravity_block', codes)

    def test_dark_enclosed_interior_warns_until_lit(self):
        cells = []
        for x in range(5, 16):
            for z in range(7, 18):
                cells.append([x, 2, z, 'stone_bricks'])
                cells.append([x, 7, z, 'stone_bricks'])
                if x in (5, 15) or z in (7, 17):
                    for y in range(3, 7):
                        cells.append([x, y, z, 'stone_bricks'])
        cells.append([10, 3, 7, 'iron_door[facing=north,half=lower]'])
        cells.append([10, 4, 7, 'iron_door[facing=north,half=upper]'])
        for z in (5, 6):
            cells.append([10, 2, z, 'smooth_stone'])

        dark_rep = assess(fixture('small-house'), {'cells': cells})
        self.assertIn('dark_interior', {i['code'] for i in dark_rep['issues']})

        lit_cells = list(cells) + [
            [8, 6, 10, 'sea_lantern'],
            [12, 6, 10, 'sea_lantern'],
            [8, 6, 14, 'sea_lantern'],
            [12, 6, 14, 'sea_lantern'],
        ]
        lit_rep = assess(fixture('small-house'), {'cells': lit_cells})
        self.assertNotIn('dark_interior', {i['code'] for i in lit_rep['issues']})

    def test_chunk_cliff_scar_detects_artifacts_hollow_crust_seams_and_road(self):
        base_fix = fixture('chunk-cliff-scar')
        unmodified = assess(base_fix, {'cells': []})
        unmod_codes = {i['code'] for i in unmodified['issues']}
        self.assertIn('orphan_foliage', unmod_codes)
        by_req0 = {c['requirement']: c['met'] for c in unmodified['completion']['checks']}
        self.assertFalse(by_req0['cleared_corrupted_artifacts'])
        self.assertFalse(by_req0['smooth_chunk_seam'])
        self.assertFalse(by_req0['reconnected_road'])

        # Attempt a hollow 1-block grass crust floating at y=6 over the sunken pit
        crust = [[x, 6, z, 'grass_block'] for x in range(8, 24) for z in range(6, 22)]
        crust_rep = assess(base_fix, {'cells': crust})
        self.assertIn('subsurface_void', {i['code'] for i in crust_rep['issues']})

        # Proper solid repair: clear sky artifacts, fill solidly to match target grade, reconnect road
        repaired = []
        for x in range(8, 24):
            for z in range(6, 22):
                for y in range(1, 18):
                    repaired.append([x, y, z, 'air'])
                # Interpolate smoothly between surrounding terrain heights
                target_y = 5 + (z - 6) // 6
                for y in range(1, target_y + 1):
                    if y == target_y:
                        mat = 'gray_concrete' if 8 <= z <= 10 else ('smooth_stone' if z in (7, 11) else 'grass_block')
                    elif y == target_y - 1:
                        mat = 'dirt'
                    else:
                        mat = 'stone'
                    repaired.append([x, y, z, mat])
        rep_ok = assess(base_fix, {'cells': repaired})
        ok_codes = {i['code'] for i in rep_ok['issues']}
        self.assertNotIn('orphan_foliage', ok_codes)
        self.assertNotIn('subsurface_void', ok_codes)
        by_req_ok = {c['requirement']: c['met'] for c in rep_ok['completion']['checks']}
        self.assertTrue(by_req_ok['cleared_corrupted_artifacts'])
        self.assertTrue(by_req_ok['solid_subsurface_fill'])
        self.assertTrue(by_req_ok['smooth_chunk_seam'], rep_ok['completion']['checks'])
        self.assertTrue(by_req_ok['reconnected_road'], rep_ok['completion']['checks'])

    def test_chunk_river_seam_requires_excavating_monolith_and_restoring_waterway(self):
        base_fix = fixture('chunk-river-seam')
        unmodified = assess(base_fix, {'cells': []})
        by_req0 = {c['requirement']: c['met'] for c in unmodified['completion']['checks']}
        self.assertFalse(by_req0['continuous_waterway'])
        self.assertFalse(by_req0['smooth_chunk_seam'])

        excavated = []
        for x in range(8, 24):
            for z in range(5, 21):
                for y in range(1, 16):
                    excavated.append([x, y, z, 'air'])
                if 10 <= z <= 13:
                    excavated.append([x, 1, z, 'gravel'])
                    excavated.append([x, 2, z, 'water'])
                    excavated.append([x, 3, z, 'water'])
                elif z in (9, 14):
                    for y in range(1, 4):
                        excavated.append([x, y, z, 'sand' if y == 3 else 'stone'])
                else:
                    for y in range(1, 5):
                        excavated.append([x, y, z, 'grass_block' if y == 4 else ('dirt' if y == 3 else 'stone')])
        rep_ok = assess(base_fix, {'cells': excavated})
        by_req_ok = {c['requirement']: c['met'] for c in rep_ok['completion']['checks']}
        self.assertTrue(by_req_ok['continuous_waterway'], rep_ok['completion']['checks'])
        self.assertTrue(by_req_ok['smooth_chunk_seam'], rep_ok['completion']['checks'])

    def test_elevated_rail_station_protects_viaduct_and_checks_platform_reachability(self):
        base_fix = fixture('elevated-rail-station')
        track_cell = next(c for c in base_fix['cells'] if state_parts(c[3])[0] in ('rail', 'powered_rail'))
        damaged = assess(base_fix, {'cells': [[track_cell[0], track_cell[1], track_cell[2], 'air']]})
        self.assertIn('protected_change', {i['code'] for i in damaged['issues']})

        ground_only = assess(base_fix, {'cells': [
            [10, 3, 6, 'iron_door[facing=north,half=lower]'],
            [10, 4, 6, 'iron_door[facing=north,half=upper]'],
        ]})
        by_req = {c['requirement']: c['met'] for c in ground_only['completion']['checks']}
        self.assertFalse(by_req['reachable_tier:y>=11'])

    def test_civic_office_tower_checks_height_tiers_and_aircraft_beacon(self):
        base_fix = fixture('civic-office-tower')
        stub = assess(base_fix, {'cells': [
            [10, 3, 6, 'iron_door[facing=north,half=lower]'],
            [10, 4, 6, 'iron_door[facing=north,half=upper]'],
        ]})
        by_req = {c['requirement']: c['met'] for c in stub['completion']['checks']}
        self.assertFalse(by_req['min_peak_height'])
        self.assertFalse(by_req['aircraft_warning_light'])
        self.assertFalse(by_req['reachable_tier:y>=22'])

    def test_rowhouse_terrace_requires_three_entrances_and_three_beds(self):
        base_fix = fixture('rowhouse-terrace')
        one_unit = assess(base_fix, {'cells': [
            [6, 3, 6, 'oak_door[facing=north,half=lower]'],
            [6, 4, 6, 'oak_door[facing=north,half=upper]'],
        ]})
        by_req = {c['requirement']: c['met'] for c in one_unit['completion']['checks']}
        self.assertFalse(by_req['reachable_doors'])
        self.assertFalse(by_req['paired_beds'])

    def test_auto_framing_svg_renderer_keeps_tall_towers_inside_viewport(self):
        tower_fix = fixture('civic-office-tower')
        grid = validate_cells({'cells': tower_fix['cells'] + [
            [15, 36, 14, 'white_concrete', None, 'spire', None],
            [15, 37, 14, 'iron_bars', None, 'spire', None],
            [15, 38, 14, 'redstone_torch', None, 'beacon', None],
        ]})
        rendered = svg(grid, view=0, cut=40, bounds=tower_fix['bounds'])
        nums = [float(v) for pair in re.findall(r'points="([^"]+)"', rendered) for tok in pair.split() for v in tok.split(',')]
        xs = nums[0::2]
        ys = nums[1::2]
        self.assertGreaterEqual(min(xs), 0.0)
        self.assertLessEqual(max(xs), 960.0)
        self.assertGreaterEqual(min(ys), 0.0)
        self.assertLessEqual(max(ys), 800.0)

    def test_init_suite_initializes_filtered_scale(self):
        with tempfile.TemporaryDirectory() as d:
            created = init_suite(Path(d) / 'terra-suite', scale='terraforming')
            self.assertEqual(len(created), 4)
            suite_meta = (Path(d) / 'terra-suite' / 'suite.json').read_text()
            self.assertIn('chunk-cliff-scar', suite_meta)
            self.assertIn('chunk-river-seam', suite_meta)


if __name__ == '__main__':
    unittest.main()
