"""Optional native-client adapters. User explicitly selects and invokes a model."""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any

from .tasks import sha, verify_run


def _sanitize_detail(stderr: str) -> str:
    lines = [ln.strip() for ln in (stderr or '').splitlines() if ln.strip()]
    if not lines:
        return ''
    tail = lines[-1][:200]
    return re.sub(r'(?:sk-[A-Za-z0-9_-]+|Bearer\s+\S+)', '[redacted]', tail)


def final_result(raw: str) -> tuple[str, dict[str, Any]]:
    obj = json.loads(raw)
    if isinstance(obj, list):
        obj = next((v for v in reversed(obj) if isinstance(v, dict) and v.get('type') == 'result'), {})
    if not isinstance(obj, dict):
        raise ValueError('unrecognized client result')
    text = obj.get('result', obj.get('response', obj.get('text')))
    if not isinstance(text, str) or not text.strip():
        raise ValueError('no final text in client result')
    if obj.get('is_error'):
        raise ValueError('client reported failure')
    return text, {k: obj[k] for k in ('usage', 'modelUsage', 'duration_ms', 'duration_seconds', 'num_turns') if k in obj}


def generate(
    run: str | Path,
    provider: str,
    model: str,
    out: str | Path,
    effort: str = 'medium',
    timeout: int = 390,
) -> Path:
    fixture = verify_run(run)
    run_path = Path(run)
    out_path = Path(out)
    if out_path.exists():
        raise ValueError('output directory already exists')
    out_path.mkdir(parents=True)
    prompt = (run_path / 'prompt.txt').read_text() + '\nSUPPORTED PALETTE:\n' + (run_path / 'palette.txt').read_text()
    track = fixture.get('track', 'voxel')
    answer_path = out_path / ('answer.py' if track == 'voxel' else 'answer.json')
    if provider == 'codex':
        cmd = [
            'codex', 'exec', '--ignore-user-config', '--skip-git-repo-check', '--ephemeral',
            '--sandbox', 'read-only', '--model', model, '-c', 'model_reasoning_effort=' + json.dumps(effort),
            '--output-last-message', str(answer_path.resolve()), '-',
        ]
    elif provider == 'claude':
        cmd = [
            'claude', '-p', '--model', model, '--effort', effort, '--output-format', 'json', '--tools', '',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '', '--no-session-persistence',
        ]
    elif provider == 'agy':
        cmd = [
            'agy', '-p', prompt, '--model', model, '--effort', effort, '--output-format', 'json',
            '--print-timeout', str(timeout) + 's', '--disable-slash-commands',
        ]
    else:
        raise ValueError('unsupported provider')

    record: dict[str, Any] = {
        'provider': provider,
        'requested_model': model,
        'track': track,
        'effort': effort,
        'timeout_seconds': timeout,
        'prompt_sha256': sha(run_path / 'prompt.txt'),
        'palette_sha256': sha(run_path / 'palette.txt'),
        'caveat': 'Native client/system context differs. Same effort names are not equal compute.',
    }
    env = os.environ.copy()
    env.pop('CLAUDECODE', None)
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd, cwd=out_path, env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(None if provider == 'agy' else prompt, timeout=timeout)
        record['exit_code'] = proc.returncode
        if proc.returncode:
            detail = _sanitize_detail(stderr)
            if detail:
                record['error_detail'] = detail
            msg = f'Native client failed (exit {proc.returncode})'
            if detail:
                msg += f': {detail}'
            raise RuntimeError(msg)
        if provider != 'codex':
            answer, usage = final_result(stdout)
            record.update(usage)
            answer_path.write_text(answer)
        if not answer_path.exists():
            raise RuntimeError('Client returned no answer file')
        record['status'] = 'returned'
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        record['status'] = 'timeout'
        raise RuntimeError('Native client exceeded time limit') from None
    except Exception:
        record['status'] = 'failed'
        raise
    finally:
        record['elapsed_seconds'] = round(time.monotonic() - start, 3)
        (out_path / 'run.json').write_text(json.dumps(record, indent=2))
    return answer_path
