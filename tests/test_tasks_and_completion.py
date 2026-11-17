import json
from pathlib import Path
import tempfile
import unittest

from prayabench.demo import example
from prayabench.evaluate import assess, summarize_reports
from prayabench.tasks import TASKS, TASK_SPECS, fixture, ground_at, init_run, verify_run


class TasksAndCompletionTests(unittest.TestCase):
    def test_all_eight_tasks_initialize_and_pass_baseline_integrity(self):
        expected = {
            'sloped-cafe',
            'small-house',
            'pocket-park',
            'shop-renovation',
            'canal-crossing',
            'corner-shophouse',
            'party-wall-infill',
            'hillside-pavilion',
        }
        self.assertTrue(expected.issubset(set(TASKS)))
        self.assertTrue(expected.issubset(set(TASK_SPECS)))
        with tempfile.TemporaryDirectory() as d:
            for task_name in expected:
                run_dir = init_run(Path(d) / task_name, task_name)
                loaded = verify_run(run_dir)
                self.assertEqual(loaded['task'], task_name)
                self.assertTrue(len(loaded['cells']) > 0)
                self.assertTrue(len(loaded['protected']) > 0)

    def test_ground_elevation_supports_both_1d_and_2d_calls(self):
        self.assertEqual(ground_at('sloped-cafe', 0), 2)
        self.assertEqual(ground_at('sloped-cafe', 16), 4)
        self.assertEqual(ground_at('sloped-cafe', 16, 12), 4)
        self.assertEqual(ground_at('small-house', 10), 2)
        self.assertLess(ground_at('hillside-pavilion', 10, 4), ground_at('hillside-pavilion', 10, 18))
        self.assertLess(ground_at('hillside-pavilion', 8, 16), ground_at('hillside-pavilion', 18, 16))

    def test_canal_crossing_requires_spanning_bridge_for_south_bank_door(self):
        base_fix = fixture('canal-crossing')
        kiosk_only = [
            [10, 4, 14, 'oak_door[facing=north,half=lower]'],
            [10, 5, 14, 'oak_door[facing=north,half=upper]'],
        ]
        rep_unbridged = assess(base_fix, {'cells': kiosk_only})
        codes_unbridged = {i['code'] for i in rep_unbridged['issues']}
        self.assertIn('unreachable_door', codes_unbridged)

        bridge = [
            [10, 4, 6, 'stone_brick_stairs[facing=south,half=bottom]'],
            *[[10, 4, z, 'stone_brick_slab[type=top]'] for z in range(7, 11)],
            [10, 4, 11, 'stone_brick_stairs[facing=north,half=bottom]'],
        ]
        rep_bridged = assess(base_fix, {'cells': kiosk_only + bridge})
        codes_bridged = {i['code'] for i in rep_bridged['issues']}
        self.assertNotIn('unreachable_door', codes_bridged)

        canal_fill = assess(base_fix, {'cells': [[10, 2, 8, 'stone_bricks']]})
        self.assertIn('protected_change', {i['code'] for i in canal_fill['issues']})

    def test_corner_shophouse_protects_both_streets_and_checks_dual_frontage_and_upper_floor(self):
        base_fix = fixture('corner-shophouse')
        street_violation = assess(base_fix, {'cells': [[2, 2, 10, 'stone_bricks'], [10, 2, 2, 'stone_bricks']]})
        violated_positions = [tuple(i['at']) for i in street_violation['issues'] if i['code'] == 'protected_change']
        self.assertIn((2, 2, 10), violated_positions)
        self.assertIn((10, 2, 2), violated_positions)

        incomplete = assess(base_fix, {'cells': [
            [8, 3, 5, 'oak_door[facing=north,half=lower]'],
            [8, 4, 5, 'oak_door[facing=north,half=upper]'],
        ]})
        self.assertFalse(incomplete['completion']['complete'])
        by_req = {c['requirement']: c['met'] for c in incomplete['completion']['checks']}
        self.assertFalse(by_req['dual_frontage_glazing'])
        self.assertFalse(by_req['reachable_upper_storey'])
        self.assertFalse(by_req['paired_beds'])

    def test_party_wall_infill_protects_neighbour_walls_and_warns_on_blind_party_wall_glazing(self):
        base_fix = fixture('party-wall-infill')
        damaged = assess(base_fix, {'cells': [[4, 5, 10, 'air'], [17, 5, 10, 'air']]})
        self.assertEqual(
            sum(1 for i in damaged['issues'] if i['code'] == 'protected_change'),
            2,
        )
        blind_window = assess(base_fix, {'cells': [
            [5, 5, 10, 'gray_stained_glass_pane'],
            [8, 3, 6, 'oak_door[facing=north,half=lower]'],
            [8, 4, 6, 'oak_door[facing=north,half=upper]'],
        ]})
        self.assertIn('blind_party_wall_glazing', {i['code'] for i in blind_window['issues']})

        street_window = assess(base_fix, {'cells': [
            [9, 5, 6, 'gray_stained_glass_pane'],
            [8, 3, 6, 'oak_door[facing=north,half=lower]'],
            [8, 4, 6, 'oak_door[facing=north,half=upper]'],
        ]})
        self.assertNotIn('blind_party_wall_glazing', {i['code'] for i in street_window['issues']})

    def test_hillside_pavilion_requires_stepped_route_to_summit_door(self):
        base_fix = fixture('hillside-pavilion')
        summit_y = ground_at('hillside-pavilion', 10, 17) + 1
        door_only = [
            [10, summit_y, 17, 'spruce_door[facing=north,half=lower]'],
            [10, summit_y + 1, 17, 'spruce_door[facing=north,half=upper]'],
        ]
        # Carve a sheer 3-block cliff across z=9 so 1-block jump cannot climb without stairs
        cliff = [[x, y, 9, 'air'] for x in range(24) for y in range(2, 10)]
        unstepped = assess(base_fix, {'cells': cliff + door_only})
        self.assertIn('unreachable_door', {i['code'] for i in unstepped['issues']})

        stairs = []
        for idx, z in enumerate(range(5, 17)):
            prev_top = ground_at('hillside-pavilion', 10, z - 1)
            cur_top = ground_at('hillside-pavilion', 10, z)
            target_top = min(summit_y - 1, 2 + (idx + 1) // 2)
            for y in range(2, target_top + 1):
                stairs.append([10, y, z, 'stone_bricks'])
            for y in range(target_top + 1, 14):
                stairs.append([10, y, z, 'air'])
        for y in range(2, summit_y):
            stairs.append([10, y, 17, 'stone_bricks'])
        stepped = assess(base_fix, {'cells': cliff + stairs + door_only})
        self.assertNotIn('unreachable_door', {i['code'] for i in stepped['issues']})
        by_req = {c['requirement']: c['met'] for c in stepped['completion']['checks']}
        self.assertTrue(by_req['reachable_summit_entrance'])

    def test_empty_and_minimal_submissions_fail_task_completion_while_demos_pass(self):
        park_empty = assess(fixture('pocket-park'), {'cells': []})
        self.assertFalse(park_empty['completion']['complete'])

        lone_door = assess(fixture('sloped-cafe'), {'cells': [
            [8, 4, 5, 'oak_door[facing=north,half=lower]'],
            [8, 5, 5, 'oak_door[facing=north,half=upper]'],
        ]})
        self.assertFalse(lone_door['completion']['complete'])

        for gabled in (True, False):
            demo_rep = assess(fixture('sloped-cafe'), example(gabled))
            self.assertEqual([i for i in demo_rep['issues'] if i['severity'] == 'error'], [])
            self.assertTrue(demo_rep['completion']['complete'], demo_rep['completion'])

    def test_renovation_flags_contradictory_new_build_placard(self):
        bad = assess(fixture('shop-renovation'), {'cells': [
            [10, 5, 8, 'oak_wall_sign[facing=south]', ['BUILT 2026', 'New Build', '', '']],
        ]})
        self.assertIn('contradictory_renovation_date', {i['code'] for i in bad['issues']})

        good = assess(fixture('shop-renovation'), {'cells': [
            [10, 5, 8, 'oak_wall_sign[facing=south]', ['Renovated', '2026', 'Espresso Bar', '']],
        ]})
        self.assertNotIn('contradictory_renovation_date', {i['code'] for i in good['issues']})

    def test_summary_aggregates_validity_and_completion_without_combined_score(self):
        r1 = assess(fixture('sloped-cafe'), example(True))
        r2 = assess(fixture('pocket-park'), {'cells': []})
        summary = summarize_reports([('gable', r1), ('empty', r2)])
        self.assertEqual(len(summary['entries']), 2)
        for row in summary['entries']:
            self.assertNotIn('score', row)
            self.assertNotIn('total_score', row)
        self.assertTrue(summary['entries'][0]['complete'])
        self.assertFalse(summary['entries'][1]['complete'])


if __name__ == '__main__':
    unittest.main()
