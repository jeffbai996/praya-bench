import json
import os
from pathlib import Path
import tempfile
import unittest

from prayabench.sandbox import compile_build
from prayabench.tasks import init_run

@unittest.skipUnless(os.environ.get('PRAYABENCH_DOCKER_TESTS')=='1','opt-in Docker integration tests')
class SandboxTests(unittest.TestCase):
    def test_valid_compilation_and_pinned_image(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','pocket-park');src=p/'answer.py';out=p/'build.json'
            src.write_text("def build(put,box,head,sign,ground):\n put(5,3,8,'stone')\n")
            result=compile_build(p,src,out)
            self.assertEqual(result['cells'][0][:4],[5,3,8,'stone'])
            meta=json.loads(Path(str(out)+'.sandbox.json').read_text())
            self.assertEqual(meta['network'],'none');self.assertTrue(meta['image_id'].startswith('sha256:'))

    def test_import_and_file_access_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','pocket-park');src=p/'answer.py'
            for code in ("def build(*args):\n import os\n", "def build(*args):\n open('/etc/passwd').read()\n"):
                src.write_text(code)
                with self.assertRaises(RuntimeError):compile_build(p,src,p/'build.json')
                self.assertFalse((p/'build.json').exists())

    def test_large_work_is_stopped(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','pocket-park');src=p/'answer.py'
            src.write_text("def build(*args):\n for n in range(100000000000):\n  x=n*n\n")
            with self.assertRaises(RuntimeError):compile_build(p,src,p/'build.json',timeout=9)

    def test_sandbox_supports_2d_ground_markdown_fences_and_safe_math_helpers(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','hillside-pavilion');src=p/'answer.py';out=p/'build.json'
            src.write_text("```python\ndef build(put,box,head,sign,ground):\n y=ground(10,16)+sum([0,1])\n put(10,y,16,'stone_bricks')\n```\n")
            result=compile_build(p,src,out)
            self.assertEqual(len(result['cells']),1)
            self.assertGreater(result['cells'][0][1],4)
            meta=json.loads(Path(str(out)+'.sandbox.json').read_text())
            self.assertTrue(meta['stripped_markdown_fence'])

    def test_diagnostic_overbudget_compilation_marks_submission(self):
        with tempfile.TemporaryDirectory() as d:
            p=init_run(Path(d)/'run','pocket-park');src=p/'answer.py';out=p/'build.json'
            padding='#'+'x'*14500+'\n'
            src.write_text("def build(put,box,head,sign,ground):\n"+padding+" put(6,3,8,'stone')\n")
            with self.assertRaises(ValueError):compile_build(p,src,out)
            result=compile_build(p,src,out,diagnostic_overbudget=True)
            self.assertTrue(result['diagnostic_only'])
            self.assertGreater(result['source_characters'],14000)

if __name__=='__main__':unittest.main()
