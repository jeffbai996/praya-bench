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

if __name__=='__main__':unittest.main()
