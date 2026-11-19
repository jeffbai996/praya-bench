import json
from pathlib import Path
import tempfile
import unittest

from prayabench.art import ART_TASKS, INNER, OUTER, rasterize
from prayabench.evaluate import assess, evaluate, summarize_reports
from prayabench.report import report
from prayabench.scene import PALETTE, state_parts
from prayabench.tasks import TRACKS, TASKS, fixture, init_run, init_suite, verify_run
from prayabench.voxel_tasks import EXTRA_VOXEL, FACINGS, road_center, rotate_xz, vehicle_rect


def checks(r):
    return {c['requirement']: c['met'] for c in r['completion']['checks']}


def bus(facing, wrong_side=False):
    x0,z0,width,length = vehicle_rect('city-bus')
    cells = {}

    def put(x,y,z,state,lines=None):
        bx,bz = rotate_xz(x0+x,z0+z,facing)
        cells[bx,y,bz] = [bx,y,bz,state,lines]

    for z in range(length):
        for x in range(width):
            put(x,4,z,'white_concrete')
            put(x,6,z,'white_concrete')
        for x in (0,width-1):
            put(x,5,z,'gray_stained_glass')
    for z in (2,10):
        for x in (0,width-1):
            put(x,3,z,'black_wool')
    for x in (1,2):
        put(x,5,0,'gray_stained_glass_pane')
    for x in range(width):
        put(x,4,1,'white_concrete')
    put(0,4,0,f'oak_wall_sign[facing={facing}]',['North Pier'])
    door_face = FACINGS[(FACINGS.index(facing)+(-1 if wrong_side else 1))%4]
    for y,half in ((5,'lower'),(6,'upper')):
        put(0 if wrong_side else width-1,y,4,f'oak_door[facing={door_face},half={half}]')
    return {'cells':list(cells.values())}


def head_example():
    rects = [[x,y,8,8,'b'] for x,y in INNER.values()]
    x,y = INNER['front']
    rects.append([x+2,y+2,4,3,'d'])
    for face in ('front','top'):
        x,y = OUTER[face]
        rects.append([x+1,y,6,1,'s'])
    return {'colors':{'b':'#94a5a8','d':'#172422','s':'#f9fff3'},'rects':rects}


class ExpansionTests(unittest.TestCase):
    def test_catalog_and_track_fixtures(self):
        self.assertEqual(len(TASKS),44)
        self.assertEqual(len(EXTRA_VOXEL),15)
        self.assertEqual(len(ART_TASKS),9)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'suite'
            self.assertEqual(len(init_suite(root)),44)
            self.assertEqual({verify_run(p)['track'] for p in root.iterdir() if p.is_dir()},set(TRACKS))
            for task in EXTRA_VOXEL:
                f = verify_run(root/task)
                self.assertTrue(all(state_parts(c[3])[0] in PALETTE for c in f['cells']))
                self.assertFalse(assess(f,{'cells':[]})['completion']['complete'], task)

    def test_rotation_checks_actual_kerb_side_and_direction(self):
        for face in FACINGS:
            f = fixture('city-bus',face)
            good = assess(f,bus(face))
            self.assertEqual(good['issues'],[],face)
            self.assertTrue(good['completion']['complete'],good['completion'])
            bad = assess(f,bus(face,wrong_side=True))
            self.assertFalse(checks(bad)['kerbside_door'],face)
        with tempfile.TemporaryDirectory() as d:
            paths = init_suite(Path(d)/'vehicles',category='vehicle',all_facings=True)
            self.assertEqual(len(paths),20)
            self.assertEqual({verify_run(p)['facing'] for p in paths},set(FACINGS))

    def test_tunnel_needs_full_clearance_and_alignment(self):
        f = fixture('curved-tunnel')
        cells = [[x,y,z,'stone_bricks' if y==2 else 'air']
                 for z in range(4,20) for x in range(road_center(z)-1,road_center(z)+2) for y in range(2,6)]
        self.assertTrue(assess(f,{'cells':cells})['completion']['complete'])
        cells += [[road_center(10),4,10,'stone'],[road_center(12),6,12,'air']]
        report_checks = checks(assess(f,{'cells':cells}))
        self.assertFalse(report_checks['unobstructed_cross_section'])
        self.assertFalse(report_checks['intact_bore_roof'])

    def test_wayfinding_rejects_hidden_or_backwards_sign(self):
        f = fixture('junction-wayfinding')
        edits = [[11,y,15,'stone_bricks'] for y in range(3,6)]
        edits.append([11,5,14,'oak_wall_sign[facing=north]',['Ferry','Right']])
        self.assertTrue(assess(f,{'cells':edits})['completion']['complete'])
        edits += [[11,5,7,'stone'],[11,5,14,'oak_wall_sign[facing=south]',['Ferry','Right']]]
        report_checks = checks(assess(f,{'cells':edits}))
        self.assertFalse(report_checks['clear_approach_sightline'])
        self.assertFalse(report_checks['north_facing_wayfinding'])

    def test_inspector_repair_keeps_scope_and_original_sign_text(self):
        f = fixture('inspector-repair')
        cells = [[5,5,6,'air'],[12,6,9,'air'],[8,3,6,'air'],
                 [5,5,7,'oak_wall_sign[facing=north]',['Cafe hours']]]
        self.assertTrue(assess(f,{'cells':cells})['completion']['complete'])
        result = assess(f,{'cells':cells+[[8,3,8,'white_concrete']]})
        self.assertFalse(checks(result)['minimal_repair'])
        self.assertIn('protected_change',result['counts'])

    def test_existing_rowhouse_stair_survives_conversion(self):
        cells = [[6,3,12,'smooth_quartz'],[7,3,12,'smooth_quartz'],
                 [6,4,12,'player_head',None,'','coffee_maker'],
                 [7,4,12,'player_head',None,'','pos_terminal'],
                 [6,3,10,'lantern'],[13,4,13,'oak_wall_sign[facing=north]',['Coffee']]]
        r = assess(fixture('rowhouse-shop-conversion'),{'cells':cells})
        self.assertTrue(checks(r)['upper_stair_access'])
        self.assertTrue(checks(r)['bounded_conversion'])

    def test_banner_layer_limit_and_exact_pixel_reconstruction(self):
        for task,spec in ART_TASKS.items():
            if spec['track'] != 'loom-banner':
                continue
            f = fixture(task)
            self.assertNotIn('target_layers',f)
            result = assess(f,{'base':spec['base'],'layers':spec['target_layers']})
            self.assertEqual(result['metrics']['pixel_accuracy'],1)
            too_many = {'base':spec['base'],'layers':[spec['target_layers'][0]]*7}
            self.assertIn('loom_layer_limit',assess(f,too_many)['counts'])

    def test_map_quantization_precedes_contrast(self):
        f = fixture('map-departure-board')
        painted = [[0,0,128,128,'b'],[13,14,80,4,'f'],[13,47,80,4,'f'],[13,77,80,4,'f']]
        good = {'colors':{'b':'#263233','f':'#fffcf5','a':'#d18724'},'rects':painted+[[14,104,12,4,'a']]}
        self.assertTrue(assess(f,good)['completion']['complete'])
        bad = {'colors':{'b':'#263233','f':'#263234'},'rects':painted}
        self.assertFalse(checks(assess(f,bad))['map_palette_contrast'])
        with self.assertRaises(ValueError):
            rasterize({'colors':{'a':'#ffffff'},'rects':[[127,0,2,1,'a']]},128,128)

    def test_head_uv_checks_and_report_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            run = init_run(Path(d)/'meter','head-parking-meter')
            submission = run/'answer.json'
            submission.write_text(json.dumps(head_example()))
            rep = evaluate(run,submission,run/'checks.json')
            self.assertTrue(rep['completion']['complete'])
            self.assertEqual(rep['issues'],[])
            self.assertEqual(summarize_reports([('one',rep)])['entries'][0]['track'],'head-skin')
            output = report(run,[submission],run/'compare.html').read_text()
            self.assertIn('Candidate A',output)
            self.assertIn('UV atlas',output)
            self.assertIn('Assembled head UV preview',output)
            self.assertIn('data:image/png;base64,',output)
            bad = head_example()
            bad['rects'].append([63,63,1,1,'b'])
            self.assertIn('pixels_outside_head_uv',assess(verify_run(run),bad)['counts'])
