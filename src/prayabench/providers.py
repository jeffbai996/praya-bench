"""Optional native-client adapters. User explicitly selects and invokes a model."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from .tasks import verify_run,sha

def final_result(raw):
    obj=json.loads(raw)
    if isinstance(obj,list):obj=next((v for v in reversed(obj) if isinstance(v,dict) and v.get('type')=='result'),{})
    if not isinstance(obj,dict):raise ValueError('unrecognized client result')
    text=obj.get('result',obj.get('response',obj.get('text')))
    if not isinstance(text,str) or not text.strip():raise ValueError('no final text in client result')
    if obj.get('is_error'):raise ValueError('client reported failure')
    return text,{k:obj[k] for k in ('usage','modelUsage','duration_ms','duration_seconds','num_turns') if k in obj}

def generate(run,provider,model,out,effort='medium',timeout=390):
    verify_run(run);run=Path(run);out=Path(out)
    if out.exists():raise ValueError('output directory already exists')
    out.mkdir(parents=True)
    prompt=(run/'prompt.txt').read_text()+'\nSUPPORTED PALETTE:\n'+(run/'palette.txt').read_text()
    if provider=='codex':
        cmd=['codex','exec','--ignore-user-config','--skip-git-repo-check','--ephemeral',
            '--sandbox','read-only','--model',model,'-c','model_reasoning_effort='+json.dumps(effort),
            '--output-last-message',str((out/'answer.py').resolve()),'-']
    elif provider=='claude':
        cmd=['claude','-p','--model',model,'--effort',effort,'--output-format','json','--tools','',
            '--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--setting-sources','','--no-session-persistence']
    elif provider=='agy':
        cmd=['agy','-p',prompt,'--model',model,'--effort',effort,'--output-format','json','--print-timeout',str(timeout)+'s','--disable-slash-commands']
    else:raise ValueError('unsupported provider')
    record={'provider':provider,'requested_model':model,'effort':effort,'timeout_seconds':timeout,
        'prompt_sha256':sha(run/'prompt.txt'),'palette_sha256':sha(run/'palette.txt'),
        'caveat':'Native client/system context differs. Same effort names are not equal compute.'}
    env=os.environ.copy();env.pop('CLAUDECODE',None);start=time.monotonic()
    proc=subprocess.Popen(cmd,cwd=out,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    try:
        stdout,stderr=proc.communicate(None if provider=='agy' else prompt,timeout=timeout)
        record['exit_code']=proc.returncode
        if proc.returncode:raise RuntimeError('Native client failed; check its authentication and model availability. Exit '+str(proc.returncode))
        if provider!='codex':
            answer,usage=final_result(stdout);record.update(usage);(out/'answer.py').write_text(answer)
        if not (out/'answer.py').exists():raise RuntimeError('Client returned no answer file')
        record['status']='returned'
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGTERM)
        try:proc.wait(timeout=3)
        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        record['status']='timeout';raise RuntimeError('Native client exceeded time limit') from None
    except Exception:
        record['status']='failed';raise
    finally:
        record['elapsed_seconds']=round(time.monotonic()-start,3)
        (out/'run.json').write_text(json.dumps(record,indent=2))
    return out/'answer.py'
