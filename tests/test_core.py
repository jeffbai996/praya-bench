import json
from pathlib import Path
import tempfile
import unittest

from prayabench.scene import validate_cells,full_block,flush_top
from prayabench.tasks import fixture,init_run,verify_run
from prayabench.evaluate import assess
from prayabench.providers import final_result
from prayabench.render import colour,svg
from prayabench.report import report
from prayabench.sandbox import extract_python_source
from prayabench.demo import example

class CoreTests(unittest.TestCase):
    def codes(self,cells,task='sloped-cafe'):
        return {i['code'] for i in assess(fixture(task),{'cells':cells})['issues']}

    def test_solid_and_partial_surfaces(self):
        self.assertTrue(full_block('white_concrete'))
        self.assertFalse(full_block('gray_stained_glass_pane'))
        self.assertFalse(flush_top('oak_slab[type=bottom]'))
        self.assertTrue(flush_top('oak_slab[type=top]'))

    def test_schema_rejects_bad_coordinates_and_props(self):
        for cell in [[True,1,1,'stone'],[1,1,1,'stone[bad]'],[1,1,1,'stone',None,'',{'texture':'remote'}]]:
            with self.assertRaises(ValueError):validate_cells({'cells':[cell]})

    def test_street_protection_and_bounds(self):
        c=self.codes([[0,2,0,'air'],[24,3,7,'stone']])
        self.assertIn('protected_change',c);self.assertIn('out_of_bounds',c)

    def test_real_wall_required_for_head(self):
        head=[5,5,10,'player_wall_head[facing=north]',None,'','coffee_maker']
        self.assertIn('unsupported_wall_fixture',self.codes([head,[5,5,11,'gray_stained_glass_pane']]))
        self.assertNotIn('unsupported_wall_fixture',self.codes([head,[5,5,11,'white_concrete']]))

    def test_mailbox_needs_slender_post(self):
        h=[18,6,7,'player_head',None,'','mailbox_orange']
        self.assertIn('head_on_plinth',self.codes([h,[18,5,7,'stone']]))
        self.assertNotIn('head_on_plinth',self.codes([h,[18,5,7,'iron_bars']]))

    def test_disconnected_door_is_not_seeded_by_indoor_paving(self):
        cells=[[x,10,z,'smooth_stone'] for x in range(6,10) for z in range(8,12)]
        cells += [[7,11,8,'oak_door[half=lower,facing=north]'],[7,12,8,'oak_door[half=upper,facing=north]']]
        self.assertIn('unreachable_door',self.codes(cells))

    def test_missing_door_not_vacuous_success(self):self.assertIn('missing_door',self.codes([]))

    def test_roof_stairs_not_treated_as_walking_flights(self):
        c=self.codes([[8,14,12,'deepslate_tile_stairs[facing=east]'],[9,15,12,'deepslate_tile_slab']])
        self.assertNotIn('stair_headroom',c);self.assertNotIn('stair_dead_end',c)

    def test_renovation_preserves_date(self):
        c=self.codes([[4,5,8,'oak_wall_sign[facing=south]',['Built','','2026','']]],'shop-renovation')
        self.assertIn('protected_change',c)

    def test_simplified_not_an_error(self):
        c=self.codes([[6,5,10,'oak_wall_sign[facing=north]',['营业时间']],[6,5,11,'stone']])
        self.assertNotIn('simplified_cjk',c)

    def test_unsupported_name_reported(self):self.assertIn('unsupported_block',self.codes([[6,4,10,'barrels']]))

    def test_demo_access_and_supports(self):
        for gabled in (True,False):
            c=assess(fixture('sloped-cafe'),example(gabled))
            self.assertEqual([i for i in c['issues'] if i['severity']=='error'],[])

    def test_manifest_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','small-house');verify_run(p)
            (p/'prompt.txt').write_text('changed')
            with self.assertRaises(ValueError):verify_run(p)

    def test_native_json_object_and_array(self):
        for obj in ({'result':'def build(): pass','usage':{}},[{'type':'system'},{'type':'result','result':'def build(): pass','usage':{}}]):
            self.assertEqual(final_result(json.dumps(obj))[0],'def build(): pass')
        with self.assertRaises(ValueError):final_result('[]')

    def test_report_escapes_sign_text(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','pocket-park');build=p/'evil.json'
            build.write_text(json.dumps({'cells':[[6,4,8,'oak_wall_sign[facing=north]',['</pre><script>alert(1)</script>']]]}))
            report(p,[build],p/'index.html')
            output=(p/'index.html').read_text()
            self.assertNotIn('<script>alert(1)</script>',output)
            self.assertIn('&lt;script&gt;',output)

    def test_fence_gate_and_hanging_sign_do_not_block_door_reachability(self):
        cells = [
            *[[x, 3, 6, 'oak_fence'] for x in range(6, 11) if x != 8],
            [8, 3, 6, 'oak_fence_gate[facing=north,open=false]'],
            [8, 5, 7, 'stone_bricks'],
            [8, 4, 7, 'oak_hanging_sign[rotation=0]', ['Open', '', '', '']],
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=north,half=upper]'],
        ]
        c = self.codes(cells, 'small-house')
        self.assertNotIn('unreachable_door', c)
        self.assertNotIn('standing_sign', c)
        self.assertNotIn('unsupported_hanging_sign', c)

    def test_ceiling_and_wall_hanging_signs_check_proper_attachment(self):
        floating_ceiling = [[8, 6, 8, 'oak_hanging_sign[rotation=0]', ['Menu', '', '', '']]]
        self.assertIn('unsupported_hanging_sign', self.codes(floating_ceiling))
        self.assertNotIn('standing_sign', self.codes(floating_ceiling))

        supported_wall_hang = [
            [7, 6, 8, 'stone_bricks'],
            [8, 6, 8, 'oak_wall_hanging_sign[facing=north]', ['Cafe', '', '', '']],
        ]
        self.assertNotIn('unsupported_hanging_sign', self.codes(supported_wall_hang))

        floating_wall_hang = [[8, 6, 8, 'oak_wall_hanging_sign[facing=north]', ['Cafe', '', '', '']]]
        self.assertIn('unsupported_hanging_sign', self.codes(floating_wall_hang))

    def test_door_requires_matching_facing_and_warns_on_glass_pane_jamb(self):
        mismatched = [
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=east,half=upper]'],
        ]
        self.assertIn('unpaired_door', self.codes(mismatched, 'small-house'))

        pane_jamb = [
            [7, 3, 8, 'gray_stained_glass_pane'],
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=north,half=upper]'],
        ]
        self.assertIn('pane_beside_door', self.codes(pane_jamb, 'small-house'))

    def test_bed_requires_matching_head_and_foot_halves(self):
        orphan = [[8, 3, 10, 'white_bed[facing=north,part=foot]']]
        self.assertIn('unpaired_bed', self.codes(orphan, 'small-house'))

        paired = [
            [8, 3, 10, 'white_bed[facing=north,part=foot]'],
            [8, 3, 9, 'white_bed[facing=north,part=head]'],
        ]
        self.assertNotIn('unpaired_bed', self.codes(paired, 'small-house'))

    def test_floating_lantern_trapdoor_carpet_and_invalid_flora_substrate_detected(self):
        defects = [
            [6, 6, 10, 'lantern[hanging=true]'],
            [8, 6, 10, 'spruce_trapdoor[facing=north,half=top]'],
            [10, 6, 10, 'white_carpet'],
            [12, 3, 10, 'white_concrete'],
            [12, 4, 10, 'poppy'],
        ]
        c = self.codes(defects, 'small-house')
        self.assertIn('floating_fixture', c)
        self.assertIn('floating_trapdoor', c)
        self.assertIn('invalid_planting', c)

        valid = [
            [6, 7, 10, 'iron_chain'],
            [6, 6, 10, 'lantern[hanging=true]'],
            [7, 6, 10, 'stone_bricks'],
            [8, 6, 10, 'spruce_trapdoor[facing=east,half=top]'],
            [10, 3, 10, 'white_carpet'],
            [12, 3, 10, 'poppy'],
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=north,half=upper]'],
        ]
        vc = self.codes(valid, 'small-house')
        self.assertNotIn('floating_fixture', vc)
        self.assertNotIn('floating_trapdoor', vc)
        self.assertNotIn('invalid_planting', vc)

    def test_extract_python_source_strips_markdown_fence_and_records_wrapper(self):
        code, stripped = extract_python_source("```python\ndef build(put, box, head, sign, ground):\n    pass\n```\n")
        self.assertTrue(stripped)
        self.assertTrue(code.startswith("def build"))
        raw, stripped_raw = extract_python_source("def build(put, box, head, sign, ground):\n    pass\n")
        self.assertFalse(stripped_raw)
        self.assertEqual(raw.strip(), code.strip())

    def test_overbudget_submission_flagged_when_evaluated(self):
        rep = assess(fixture('pocket-park'), {'cells': [], 'source_characters': 17942, 'diagnostic_only': True})
        self.assertIn('source_budget_exceeded', {i['code'] for i in rep['issues']})

    def test_renderer_assigns_distinct_colours_and_culls_internal_water_faces(self):
        self.assertNotEqual(colour('water'), colour('stone'))
        self.assertNotEqual(colour('cherry_planks'), colour('stone'))
        self.assertNotEqual(colour('sandstone_slab'), colour('stone'))
        one_water = svg({(5, 2, 8): [5, 2, 8, 'water', None, '', None]})
        two_water = svg({
            (5, 2, 8): [5, 2, 8, 'water', None, '', None],
            (6, 2, 8): [6, 2, 8, 'water', None, '', None],
        })
        self.assertLess(two_water.count('<polygon'), one_water.count('<polygon') * 2)

    def test_tall_double_plants_and_everyday_vanilla_materials_supported(self):
        cells = [
            [6, 3, 10, 'peony[half=lower]'],
            [6, 4, 10, 'peony[half=upper]'],
            [8, 3, 10, 'mossy_stone_bricks'],
            [9, 3, 10, 'mud_bricks'],
            [10, 3, 10, 'cobblestone_wall'],
            [11, 3, 10, 'tinted_glass'],
            [12, 3, 10, 'composter'],
            [13, 3, 10, 'water_cauldron'],
            [14, 3, 10, 'allium'],
            [8, 3, 8, 'oak_door[facing=north,half=lower]'],
            [8, 4, 8, 'oak_door[facing=north,half=upper]'],
        ]
        c = self.codes(cells, 'small-house')
        self.assertNotIn('invalid_planting', c)
        self.assertNotIn('unsupported_block', c)
        # Upper half of peony directly on stone is still invalid
        bad = [[6, 3, 10, 'stone'], [6, 4, 10, 'peony[half=upper]']]
        self.assertIn('invalid_planting', self.codes(bad, 'small-house'))

if __name__=='__main__':unittest.main()
