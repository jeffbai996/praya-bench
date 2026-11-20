import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from prayabench.evaluate import assess
from prayabench.tasks import TASK_SPECS, fixture
from prayabench.voxel_tasks import FACINGS, VEHICLES


class ReferenceExamplesTests(unittest.TestCase):
    def test_examples_cover_all_44_tasks_and_pass_zero_errors(self):
        from prayabench.examples import example, list_examples

        self.assertEqual(len(list_examples()), 44)
        self.assertEqual(set(list_examples()), set(TASK_SPECS))

        for task in TASK_SPECS:
            facings = FACINGS if task in VEHICLES else (None,)
            for facing in facings:
                f = fixture(task, facing)
                ex = example(task, facing)
                rep = assess(f, ex)
                errors = [i for i in rep['issues'] if i['severity'] == 'error']
                dark = [i for i in rep['issues'] if i['code'] == 'dark_interior']
                unmet = [c for c in rep['completion']['checks'] if not c['met']]
                self.assertEqual(errors, [], f'{task} ({facing}) errors: {errors}')
                self.assertEqual(dark, [], f'{task} ({facing}) dark_interior: {dark}')
                self.assertTrue(
                    rep['completion']['complete'],
                    f'{task} ({facing}) incomplete: {unmet}',
                )

    def test_example_facing_validation(self):
        from prayabench.examples import example

        with self.assertRaises(ValueError):
            example('unknown-task')
        with self.assertRaises(ValueError):
            example('sloped-cafe', facing='east')
        with self.assertRaises(ValueError):
            example('city-bus', facing='up')

    def test_cli_example_and_atlas(self):
        with tempfile.TemporaryDirectory() as d:
            out_json = Path(d) / 'bus-east.json'
            res = subprocess.run(
                [sys.executable, '-m', 'prayabench.cli', 'example', 'city-bus', '--facing', 'east', '--out', str(out_json)],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn(str(out_json), res.stdout)
            loaded = json.loads(out_json.read_text())
            rep = assess(fixture('city-bus', 'east'), loaded)
            self.assertTrue(rep['completion']['complete'])
            self.assertEqual(rep['issues'], [])

            out_html = Path(d) / 'atlas.html'
            subprocess.run(
                [sys.executable, '-m', 'prayabench.cli', 'atlas', str(out_html), '--track', 'map-art'],
                capture_output=True,
                text=True,
                check=True,
            )
            html_text = out_html.read_text()
            self.assertIn('Deterministic reference examples', html_text)
            self.assertIn('map-fascia-wordmark', html_text)
            self.assertIn('map-departure-board', html_text)
            self.assertIn('map-motorway-guide', html_text)
