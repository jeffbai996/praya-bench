import json
from pathlib import Path
import tempfile
import unittest

from prayabench.scene import validate_cells,full_block,flush_top
from prayabench.tasks import fixture,init_run,verify_run
from prayabench.evaluate import assess
from prayabench.providers import final_result
from prayabench.report import report
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
        self.assertIn('mailbox_plinth',self.codes([h,[18,5,7,'stone']]))
        self.assertNotIn('mailbox_plinth',self.codes([h,[18,5,7,'iron_bars']]))

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

if __name__=='__main__':unittest.main()
