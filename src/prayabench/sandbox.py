"""Docker-only execution: no host mounts, credentials, network or fallback exec."""
import json
from pathlib import Path
import re
import subprocess
from typing import Any
import uuid

from .scene import ASSETS, MAX_BYTES, MAX_CELLS, validate_cells
from .tasks import TASK_SPECS, ground_grid, verify_run

DEFAULT_IMAGE = 'python:3.12-slim'
DEFAULT_SOURCE_LIMIT = 14000
DIAGNOSTIC_SOURCE_LIMIT = 80000


def extract_python_source(raw: str) -> tuple[str, bool]:
    text = raw.strip()
    match = re.fullmatch(r'```(?:python|py)?\s*\n(.*?)\n```', text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + '\n', True
    return raw, False


def compile_build(
    run: str | Path,
    source: str | Path,
    out: str | Path,
    image: str = DEFAULT_IMAGE,
    timeout: int = 15,
    diagnostic_overbudget: bool = False,
) -> dict[str, Any]:
    fixture = verify_run(run)
    task = fixture['task']
    contract_limit = fixture.get('source_limit') or TASK_SPECS.get(task, {}).get('source_limit', DEFAULT_SOURCE_LIMIT)
    path = Path(source)
    if path.stat().st_size > 180_000:
        raise ValueError('source file too large')
    raw_code = path.read_text()
    code, stripped_fence = extract_python_source(raw_code)
    source_chars = len(code)
    cap = DIAGNOSTIC_SOURCE_LIMIT if diagnostic_overbudget else contract_limit
    if source_chars > cap:
        raise ValueError(f'source exceeds {cap} characters ({source_chars})')
    over_contract = source_chars > contract_limit

    inspect = subprocess.run(
        ['docker', 'image', 'inspect', image, '--format', '{"id":{{json .Id}},"digests":{{json .RepoDigests}}}'],
        capture_output=True, text=True, timeout=10,
    )
    if inspect.returncode:
        raise RuntimeError('Sandbox image unavailable. Run: docker pull ' + image)
    image_meta = json.loads(inspect.stdout)
    image_id = image_meta['id']
    if not image_id.startswith('sha256:'):
        raise RuntimeError('Could not pin sandbox image')

    container = 'prayabench-' + uuid.uuid4().hex
    worker = Path(__file__).with_name('worker.py').read_text()
    cmd = [
        'docker', 'run', '--rm', '--name', container, '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534',
        '--memory', '192m', '--memory-swap', '192m', '--cpus', '1', '--pids-limit', '16',
        '--ulimit', 'cpu=8:8', '--ulimit', 'fsize=0:0', '-i', image_id, 'python', '-I', '-B', '-c', worker,
    ]
    bounds = fixture.get('bounds') or TASK_SPECS.get(task, {}).get('bounds', [0, 0, 0, 23, 17, 21])
    payload = {
        'source': code,
        'task': task,
        'bounds': bounds,
        'ground': fixture.get('ground') or ground_grid(task),
        'assets': list(ASSETS),
        'source_limit': cap,
        'cell_limit': MAX_CELLS,
        'write_limit': MAX_CELLS * 2,
    }
    try:
        proc = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, timeout=timeout)
        if len(proc.stdout) > MAX_BYTES:
            raise RuntimeError('Sandbox output too large')
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise RuntimeError('Sandbox failed: ' + proc.stderr[-300:]) from None
        if proc.returncode or 'error' in result:
            raise RuntimeError('Sandbox rejected submission: ' + str(result.get('error', 'process exit ' + str(proc.returncode))))
        validate_cells(result)
        result['source_characters'] = source_chars
        result['stripped_markdown_fence'] = stripped_fence
        if over_contract:
            result['diagnostic_only'] = True
        Path(out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
        Path(str(out) + '.sandbox.json').write_text(json.dumps({
            'image_id': image_id,
            'registry_digests': image_meta.get('digests') or [],
            'network': 'none',
            'readonly': True,
            'memory_bytes': 201326592,
            'cpu_seconds': 8,
            'wall_timeout_seconds': timeout,
            'source_characters': source_chars,
            'contract_source_limit': contract_limit,
            'stripped_markdown_fence': stripped_fence,
            'diagnostic_only': over_contract,
        }, indent=2))
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError('Sandbox wall-clock limit reached') from None
    finally:
        subprocess.run(['docker', 'rm', '-f', container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
