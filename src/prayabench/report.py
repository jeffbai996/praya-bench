"""Self-contained, offline comparison pages with optional blind review."""
import html
import json
from pathlib import Path
import random
from .scene import load_json,validate_cells
from .tasks import verify_run
from .evaluate import assess
from .render import svg

def report(run,builds,out,blind=True,seed=42):
    fixture=verify_run(run);base=validate_cells({'cells':fixture['cells']})
    entries=[]
    for path in builds:
        p=Path(path);data=load_json(p);edits=validate_cells(data)
        entries.append((p.stem,edits,assess(fixture,data)))
    if not entries or len(entries)>12:raise ValueError('compare 1–12 builds')
    if blind:random.Random(seed).shuffle(entries)
    parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>prayabench — build comparison</title>
<style>*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;background:#f1f4f0;color:#24372e;margin:0}main{max-width:1120px;margin:auto;padding:40px 24px}h1{font-size:clamp(36px,6vw,60px);letter-spacing:-2px;margin:0}h2{margin:0}header{margin-bottom:30px}.tag{font:12px monospace;text-transform:uppercase;letter-spacing:2px;color:#52735b}.muted{color:#586b61}article{background:white;border:1px solid #cbd8cd;border-radius:16px;margin:24px 0;padding:22px;box-shadow:0 5px 16px #28422d08}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:14px 0}button{font:inherit;background:#edf3ed;border:1px solid #becfbe;border-radius:8px;padding:7px 13px;color:inherit;cursor:pointer}button[aria-pressed=true]{background:#294f39;color:white}button:focus-visible,summary:focus-visible{outline:3px solid #c48335;outline-offset:3px}.scene{background:#eef2ef;border-radius:10px;overflow:hidden}.scene svg{width:100%;max-height:650px;display:block}summary{cursor:pointer;padding:10px 0;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:380px;overflow:auto;font:13px/1.5 monospace;background:#f2f5f1;padding:14px;border-radius:8px}.metrics{display:flex;gap:20px;flex-wrap:wrap;padding:12px 0}.metric b{font-size:22px;display:block}.metric span{font-size:12px;color:#586b61}footer{margin:36px 0}.hidden{display:none}textarea{width:100%;min-height:80px;font:inherit;border:1px solid #becfbe;border-radius:8px;padding:10px}a{color:#285b3c}</style>
<main><header><div class="tag">Spatial reasoning · construction · design</div><h1>prayabench</h1><p>A visual benchmark for AI building in Minecraft.</p>
<p class="muted">Inspect the builds before revealing their labels. Rotate the view, lift the roof, then compare construction findings and sign/prop records. These flat-colour previews approximate geometry; they are not Minecraft screenshots.</p></header>''']
    parts.append('<p>Task: <strong>'+html.escape(fixture['task'])+'</strong>. '+('Anonymous order; labels revealed on demand.' if blind else 'Labels visible.')+'</p>')
    for i,(label,edits,checks) in enumerate(entries):
        title='Candidate '+chr(65+i) if blind else label
        parts.append(f'<article data-view="0" data-cut="18"><h2>{html.escape(title)}</h2><div class="toolbar" role="group" aria-label="Camera views">')
        for v,word in enumerate(('SE','SW','NW','NE')):parts.append(f'<button class="angle" data-angle="{v}" aria-pressed="{str(v==0).lower()}">{word}</button>')
        parts.append('<button class="cut" aria-pressed="false">Lift roof</button></div>')
        grid=base|edits
        for v in range(4):
            for cut in (18,9):
                cls='scene' if v==0 and cut==18 else 'scene hidden'
                parts.append(f'<div class="{cls}" data-angle="{v}" data-height="{cut}">'+svg(grid,v,cut)+'</div>')
        errors=sum(x['severity']=='error' for x in checks['issues']);warn=sum(x['severity']=='warn' for x in checks['issues'])
        parts.append(f'<div class="metrics"><div class="metric"><b>{len(edits)}</b><span>edited cells</span></div><div class="metric"><b>{errors}</b><span>error findings</span></div><div class="metric"><b>{warn}</b><span>review warnings</span></div></div>')
        parts.append('<p class="muted">A clean check list does not establish good architecture or complete task fulfillment. No combined quality score is assigned.</p>')
        for heading,value in [('Located findings',checks['issues']),('Sign and prop records',{'signs':checks['signs'],'props':checks['props']}),('Reveal label',label)]:
            parts.append('<details><summary>'+heading+'</summary><pre>'+html.escape(json.dumps(value,indent=2,ensure_ascii=False))+'</pre></details>')
        parts.append(f'<label for="notes-{i}">Your review notes</label><textarea id="notes-{i}" placeholder="Proportions, circulation, supports, terrain fit, corrections needed…"></textarea><p class="muted">Notes stay on this page until you download them; they are not sent anywhere.</p></article>')
    parts.append('''<button id="export">Download review notes</button><footer class="muted">Experimental benchmark. Approximate walkability allows one-block jumps; it is not an accessibility certification. The supported palette is not a complete Minecraft registry. Blind labels are a convenience, not a secrecy mechanism. See the reproducible fixture and submitted JSON for evidence.</footer></main>
<script>document.querySelectorAll('article').forEach(a=>{const show=()=>{a.querySelectorAll('.scene').forEach(s=>s.classList.toggle('hidden',s.dataset.angle!==a.dataset.view||s.dataset.height!==a.dataset.cut));a.querySelectorAll('.angle').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.angle===a.dataset.view)));};a.querySelectorAll('.angle').forEach(b=>b.addEventListener('click',()=>{a.dataset.view=b.dataset.angle;show();}));a.querySelector('.cut').addEventListener('click',e=>{a.dataset.cut=a.dataset.cut==='18'?'9':'18';e.target.setAttribute('aria-pressed',String(a.dataset.cut==='9'));show();});});document.getElementById('export').addEventListener('click',()=>{const notes=Array.from(document.querySelectorAll('article')).map(a=>({candidate:a.querySelector('h2').textContent,notes:a.querySelector('textarea').value}));const url=URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='prayabench-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});</script></html>''')
    Path(out).write_text('\n'.join(parts))
    return Path(out)
