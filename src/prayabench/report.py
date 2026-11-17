"""Self-contained, offline comparison pages with multi-scale cutaways and optional blind review."""
import html
import json
from pathlib import Path
import random
from typing import Sequence

from .evaluate import assess
from .render import svg
from .scene import load_json, validate_cells
from .tasks import TASK_SPECS, verify_run


def report(
    run: str | Path,
    builds: Sequence[str | Path],
    out: str | Path,
    blind: bool = True,
    seed: int = 42,
) -> Path:
    fixture = verify_run(run)
    base = validate_cells({'cells': fixture['cells']})
    entries = []
    for path in builds:
        p = Path(path)
        data = load_json(p)
        edits = validate_cells(data)
        entries.append((p.stem, edits, assess(fixture, data)))
    if not entries or len(entries) > 12:
        raise ValueError('compare 1–12 builds')
    if blind:
        random.Random(seed).shuffle(entries)

    task_name = fixture['task']
    spec = TASK_SPECS.get(task_name, {})
    brief = spec.get('brief', '')
    bounds = fixture.get('bounds') or spec.get('bounds', [0, 0, 0, 23, 17, 21])
    h = int(bounds[4]) + 1
    mid_cut = max(8, round(h * 0.56))
    low_cut = min(mid_cut - 2, max(5, round(h * 0.28)))
    cuts = [(h, 'Full view'), (mid_cut, f'Upper cut (y<{mid_cut})'), (low_cut, f'Ground cut (y<{low_cut})')]

    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>prayabench build comparison</title>
<style>*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;background:#f1f4f0;color:#24372e;margin:0}main{max-width:1120px;margin:auto;padding:40px 24px}h1{font-size:clamp(36px,6vw,60px);letter-spacing:-2px;margin:0}h2{margin:0}header{margin-bottom:30px}.tag{font:12px monospace;text-transform:uppercase;letter-spacing:2px;color:#52735b}.muted{color:#586b61}.brief{background:#e6ede7;border-radius:10px;padding:12px 16px;margin:14px 0}article{background:white;border:1px solid #cbd8cd;border-radius:16px;margin:24px 0;padding:22px;box-shadow:0 5px 16px #28422d08}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:14px 0}.sep{width:1px;height:22px;background:#cbd8cd;margin:0 4px}button{font:inherit;background:#edf3ed;border:1px solid #becfbe;border-radius:8px;padding:7px 13px;color:inherit;cursor:pointer}button[aria-pressed=true]{background:#294f39;color:white}button:focus-visible,summary:focus-visible{outline:3px solid #c48335;outline-offset:3px}.scene{background:#eef2ef;border-radius:10px;overflow:hidden}.scene svg{width:100%;max-height:650px;display:block}summary{cursor:pointer;padding:10px 0;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:380px;overflow:auto;font:13px/1.5 monospace;background:#f2f5f1;padding:14px;border-radius:8px}.metrics{display:flex;gap:20px;flex-wrap:wrap;padding:12px 0}.metric b{font-size:22px;display:block}.metric span{font-size:12px;color:#586b61}footer{margin:36px 0}.hidden{display:none}textarea{width:100%;min-height:80px;font:inherit;border:1px solid #becfbe;border-radius:8px;padding:10px}a{color:#285b3c}</style>
<main data-task="''' + html.escape(task_name) + '''" data-blind="''' + str(blind).lower() + '''"><header><div class="tag">Spatial reasoning · construction · terraforming · design</div><h1>prayabench</h1><p>A visual benchmark for AI building in Minecraft.</p>
<p class="muted">Inspect the builds before revealing their labels. Rotate the view, slice upper and ground levels, then compare construction findings, brief completion and sign/prop records. These flat-colour previews approximate geometry; they are not Minecraft screenshots.</p></header>''']

    dims = f'{bounds[3]+1}×{bounds[4]+1}×{bounds[5]+1}'
    scale_label = fixture.get('scale') or spec.get('scale', 'small')
    parts.append(
        '<p>Task: <strong>' + html.escape(task_name) + '</strong> '
        f'<span class="muted">({html.escape(scale_label)} · {dims})</span>. '
        + ('Anonymous order; labels revealed on demand.' if blind else 'Labels visible.') + '</p>'
    )
    if brief:
        parts.append('<div class="brief"><strong>Brief:</strong> ' + html.escape(brief) + '</div>')

    for i, (label, edits, checks) in enumerate(entries):
        title = 'Candidate ' + chr(65 + i) if blind else label
        parts.append(f'<article data-view="0" data-cut="{h}"><h2>{html.escape(title)}</h2><div class="toolbar" role="group" aria-label="Camera views">')
        for v, word in enumerate(('SE', 'SW', 'NW', 'NE')):
            parts.append(f'<button class="angle" data-angle="{v}" aria-pressed="{str(v == 0).lower()}">{word}</button>')
        parts.append('<span class="sep" aria-hidden="true"></span>')
        for cut_val, cut_label in cuts:
            parts.append(f'<button class="cut" data-cut-level="{cut_val}" aria-pressed="{str(cut_val == h).lower()}">{cut_label}</button>')
        parts.append('</div>')

        grid = base | edits
        for v in range(4):
            for cut_val, _ in cuts:
                cls = 'scene' if v == 0 and cut_val == h else 'scene hidden'
                parts.append(f'<div class="{cls}" data-angle="{v}" data-height="{cut_val}">' + svg(grid, v, cut_val, bounds=bounds) + '</div>')

        errors = sum(x['severity'] == 'error' for x in checks['issues'])
        warn = sum(x['severity'] == 'warn' for x in checks['issues'])
        comp = checks.get('completion') or {'met_count': 0, 'total_count': 0, 'checks': []}
        parts.append(
            f'<div class="metrics">'
            f'<div class="metric"><b>{len(edits)}</b><span>edited cells</span></div>'
            f'<div class="metric"><b>{comp["met_count"]}/{comp["total_count"]}</b><span>brief checks met</span></div>'
            f'<div class="metric"><b>{errors}</b><span>error findings</span></div>'
            f'<div class="metric"><b>{warn}</b><span>review warnings</span></div>'
            f'</div>'
        )
        parts.append('<p class="muted">Passing automated checks confirms presence and approximate support, not good architecture. No combined quality score is assigned.</p>')
        for heading, value in [
            ('Brief completion checks', comp),
            ('Located findings', checks['issues']),
            ('Sign and prop records', {'signs': checks['signs'], 'props': checks['props']}),
            ('Reveal label', label),
        ]:
            parts.append('<details><summary>' + heading + '</summary><pre>' + html.escape(json.dumps(value, indent=2, ensure_ascii=False)) + '</pre></details>')
        parts.append(f'<label for="notes-{i}">Your review notes</label><textarea id="notes-{i}" placeholder="Proportions, circulation, supports, terrain fit, corrections needed…"></textarea><p class="muted">Notes stay on this page until you download them; they are not sent anywhere.</p></article>')

    parts.append('''<button id="export">Download review notes</button><footer class="muted">Experimental benchmark. Approximate walkability allows one-block jumps; it is not an accessibility certification. The supported palette is not a complete Minecraft registry. Blind labels are a convenience, not a secrecy mechanism. See the reproducible fixture and submitted JSON for evidence.</footer></main>
<script>document.querySelectorAll('article').forEach(a=>{const show=()=>{a.querySelectorAll('.scene').forEach(s=>s.classList.toggle('hidden',s.dataset.angle!==a.dataset.view||s.dataset.height!==a.dataset.cut));a.querySelectorAll('.angle').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.angle===a.dataset.view)));a.querySelectorAll('.cut').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.cutLevel===a.dataset.cut)));};a.querySelectorAll('.angle').forEach(b=>b.addEventListener('click',()=>{a.dataset.view=b.dataset.angle;show();}));a.querySelectorAll('.cut').forEach(b=>b.addEventListener('click',()=>{a.dataset.cut=b.dataset.cutLevel;show();}));});document.getElementById('export').addEventListener('click',()=>{const root=document.querySelector('main');const notes=Array.from(document.querySelectorAll('article')).map(a=>({candidate:a.querySelector('h2').textContent,task:root.dataset.task,blind:root.dataset.blind==='true',notes:a.querySelector('textarea').value}));const url=URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='prayabench-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});</script></html>''')
    Path(out).write_text('\n'.join(parts))
    return Path(out)
