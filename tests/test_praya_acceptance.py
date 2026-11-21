import unittest

from prayabench.evaluate import assess
from prayabench.heads import ASSETS, BANNED_HEADS, HEAD_CATALOG, head_faces, resolve_head_name
from prayabench.render import svg
from prayabench.scene import validate_cells
from prayabench.tasks import fixture


class AcceptanceTests(unittest.TestCase):
    def codes(self, cells, task='sloped-cafe'):
        return {i['code'] for i in assess(fixture(task), {'cells': cells})['issues']}

    def test_head_catalog_standalone_and_has_8x8_faces(self):
        self.assertGreaterEqual(len(ASSETS), 60)
        for name in ASSETS:
            pal, faces = head_faces(name)
            self.assertTrue(pal)
            for face_key in ('front', 'left', 'right', 'top', 'back'):
                self.assertEqual(len(faces[face_key]), 8)
                self.assertTrue(all(len(row) == 8 for row in faces[face_key]))
        self.assertEqual(resolve_head_name('cash_register'), 'pos_terminal')
        self.assertEqual(resolve_head_name('monitor'), 'computer_monitor')

    def test_standing_sign_banned_exit_head_and_bookshelf_filler_caught(self):
        cells = [
            [8, 3, 8, 'oak_sign[rotation=8]', ['Menu', '-----', 'Coffee', ''], 'shop-sign'],
            [9, 3, 9, 'bookshelf'],
            [10, 3, 10, 'smooth_quartz'],
            [10, 4, 10, 'player_head[rotation=0]', None, 'prop', 'exit_sign'],
            [8, 3, 12, 'oak_door[facing=north,half=lower]'],
            [8, 4, 12, 'oak_door[facing=north,half=upper]'],
        ]
        rep = assess(fixture('sloped-cafe'), {'cells': cells})
        err_codes = {i['code'] for i in rep['issues'] if i['severity'] == 'error'}
        self.assertIn('standing_sign', err_codes)
        self.assertIn('bookshelf_filler', err_codes)
        self.assertIn('banned_exit_head', err_codes)

    def test_exterior_code_and_low_or_exterior_dedication_placard_rejected(self):
        cells = [
            [8, 3, 8, 'white_concrete'],
            [8, 4, 8, 'white_concrete'],
            [8, 4, 7, 'oak_wall_sign[facing=north]', ['Max Occupancy', '24 Persons', 'By Order of', 'Fire Marshal'], 'facade'],
            [9, 3, 8, 'white_concrete'],
            [9, 3, 7, 'oak_wall_sign[facing=north]', ['Built', '-----', 'Nov. 12,', '2026'], 'facade'],
        ]
        err_codes = {i['code'] for i in assess(fixture('small-house'), {'cells': cells})['issues'] if i['severity'] == 'error'}
        self.assertIn('exterior_code_sign', err_codes)
        self.assertIn('exterior_dedication_placard', err_codes)

    def test_floating_slab_pane_and_unplanted_base_caught(self):
        cells = [
            [8, 6, 10, 'smooth_stone_slab[type=bottom]'],
            [10, 6, 10, 'gray_stained_glass_pane'],
            [12, 4, 10, 'stone_bricks'],
        ]
        err_codes = {i['code'] for i in assess(fixture('small-house'), {'cells': cells})['issues'] if i['severity'] == 'error'}
        self.assertIn('floating_slab', err_codes)
        self.assertIn('floating_pane', err_codes)
        self.assertIn('unplanted_base', err_codes)

    def test_blank_planar_box_fails_elevation_recessed_entry_and_roof_equipment(self):
        cells = []
        for x in range(6, 18):
            for z in range(7, 17):
                cells.append([x, 2, z, 'smooth_stone'])
                cells.append([x, 7, z, 'smooth_stone'])
                if x in (6, 17) or z in (7, 16):
                    for y in range(3, 7):
                        cells.append([x, y, z, 'white_concrete'])
        # Featureless roof box
        for x in range(9, 14):
            for z in range(10, 13):
                cells.append([x, 8, z, 'iron_block'])
                cells.append([x, 9, z, 'iron_block'])
        cells.append([10, 3, 7, 'oak_door[facing=north,half=lower]'])
        cells.append([10, 4, 7, 'oak_door[facing=north,half=upper]'])
        rep = assess(fixture('medical-clinic'), {'cells': cells})
        err_codes = {i['code'] for i in rep['issues'] if i['severity'] == 'error'}
        self.assertIn('blank_elevation', err_codes)
        self.assertIn('planar_facade', err_codes)
        self.assertIn('flush_exterior_door', err_codes)
        self.assertIn('roof_equipment_form', err_codes)
        by_req = {c['requirement']: c['met'] for c in rep['completion']['checks']}
        self.assertFalse(by_req['address_plaque'])
        self.assertFalse(by_req['dedication_placard'])
        self.assertFalse(by_req['custom_head_density'])

    def test_renderer_draws_head_pixels_item_frame_and_sign_text(self):
        grid = validate_cells({
            'cells': [
                [8, 3, 10, 'bricks'],
                [8, 4, 10, 'bricks'],
                [8, 5, 10, 'bricks'],
                [8, 4, 9, 'oak_wall_sign[facing=north]', ['| 176 |', '---', 'Harbour Ave', '']],
                [8, 5, 9, 'air', None, 'placard', None, {'facing': 'north', 'item': 'stone_axe'}],
                [10, 3, 9, 'smooth_quartz'],
                [10, 4, 9, 'player_head[rotation=8]', None, 'prop', 'coffee_maker'],
            ]
        })
        out = svg(grid, view=2)
        self.assertIn('| 176 |', out)
        self.assertIn('Harbour Ave', out)
        # Head palette color (#d9534f shaded by ~0.74 -> #a03d3a) rather than flat tan (#918770)
        self.assertNotIn('#918770', out)
        self.assertIn('<g transform="matrix(', out)


if __name__ == '__main__':
    unittest.main()
