"""Docker-only execution: no host mounts, credentials, network or fallback exec."""
import json
from pathlib import Path
import subprocess
import uuid
from .scene import validate_cells
from .tasks import verify_run

DEFAULT_IMAGE='python:3.12-slim'

def compile_build(run,source,out,image=DEFAULT_IMAGE,timeout=12):
    fixture=verify_run(run);path=Path(source)
    if path.stat().st_size>60000:raise ValueError('source file too large')
    code=path.read_text()
    if len(code)>14000:raise ValueError('source exceeds 14000 characters')
    # Resolve a locally available image to an immutable ID. Never pull silently.
    inspect=subprocess.run(['docker','image','inspect',image,'--format','{"id":{{json .Id}},"digests":{{json .RepoDigests}}}'],capture_output=True,text=True,timeout=10)
    if inspect.returncode:raise RuntimeError('Sandbox image unavailable. Run: docker pull '+image)
    image_meta=json.loads(inspect.stdout);image_id=image_meta['id']
    if not image_id.startswith('sha256:'):raise RuntimeError('Could not pin sandbox image')
    container='prayabench-'+uuid.uuid4().hex
    worker=Path(__file__).with_name('worker.py').read_text()
    cmd=['docker','run','--rm','--name',container,'--network','none','--read-only',
         '--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534',
         '--memory','128m','--memory-swap','128m','--cpus','1','--pids-limit','16',
         '--ulimit','cpu=5:5','--ulimit','fsize=0:0','-i',image_id,'python','-I','-B','-c',worker]
    try:
        proc=subprocess.run(cmd,input=json.dumps({'source':code,'task':fixture['task']}),capture_output=True,text=True,timeout=timeout)
        if len(proc.stdout)>4_000_000:raise RuntimeError('Sandbox output too large')
        try:result=json.loads(proc.stdout)
        except json.JSONDecodeError:raise RuntimeError('Sandbox failed: '+proc.stderr[-300:]) from None
        if proc.returncode or 'error' in result:raise RuntimeError('Sandbox rejected submission: '+str(result.get('error','process exit '+str(proc.returncode))))
        validate_cells(result)
        Path(out).write_text(json.dumps(result,indent=2,ensure_ascii=False))
        Path(str(out)+'.sandbox.json').write_text(json.dumps({'image_id':image_id,'registry_digests':image_meta.get('digests') or [],'network':'none',
            'readonly':True,'memory_bytes':134217728,'cpu_seconds':5,'wall_timeout_seconds':timeout},indent=2))
        return result
    except subprocess.TimeoutExpired:raise RuntimeError('Sandbox wall-clock limit reached') from None
    finally:
        subprocess.run(['docker','rm','-f',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
