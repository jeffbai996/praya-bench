"""Deterministic acceptable reference examples for all 44 prayabench tasks.

These synthetic reference solutions validate task specifications and provide
offline visual baselines. They are NOT model benchmark results.
"""
from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from ._examples_art import art_example
from ._examples_buildings import BUILDING_AND_TERRA_BUILDERS
from ._examples_world import EXTRA_WORLD_BUILDERS, VEHICLE_BUILDERS
from .art import ART_TASKS, art_previews
from .evaluate import assess
from .render import svg
from .scene import validate_cells
from .tasks import SCALES, TASK_SPECS, TRACKS, fixture
from .voxel_tasks import FACINGS, VEHICLES

# Preferred camera index (0=SE, 1=SW, 2=NW, 3=NE) for front-facing preview cards.
_DEFAULT_PREVIEW_VIEW: dict[str, int] = {
    'transit-shelter': 2,
    'sloped-cafe': 2,
    'shop-renovation': 2,
    'small-house': 2,
    'utility-substation': 2,
    'corner-shophouse': 2,
    'party-wall-infill': 2,
    'rowhouse-terrace': 2,
    'medical-clinic': 2,
    'grocery-supermarket': 2,
    'elevated-rail-station': 2,
    'midrise-apartments': 2,
    'civic-office-tower': 2,
    'washroom-fitout': 2,
    'roof-hvac': 2,
    'junction-wayfinding': 2,
    'facade-depth-retrofit': 2,
    'rowhouse-shop-conversion': 2,
    'inspector-repair': 2,
}


def list_examples() -> tuple[str, ...]:
    """Return every task name in catalog order."""
    return tuple(TASK_SPECS)


def example(task: str, facing: str | None = None) -> dict[str, Any]:
    """Return a deterministic acceptable reference submission for ``task``."""
    if task not in TASK_SPECS:
        raise ValueError(f'unknown task: {task}')
    if facing is not None and (task not in VEHICLES or facing not in FACINGS):
        raise ValueError('facing is only supported on vehicle tasks')
    if task in ART_TASKS:
        return art_example(task)
    if task in VEHICLES:
        return VEHICLE_BUILDERS[task](facing or 'north')
    if task in BUILDING_AND_TERRA_BUILDERS:
        return BUILDING_AND_TERRA_BUILDERS[task]()
    return EXTRA_WORLD_BUILDERS[task]()


def atlas(
    out: str | Path,
    *,
    scale: str | None = None,
    category: str | None = None,
    track: str | None = None,
) -> Path:
    """Render an offline HTML reference atlas of acceptable examples."""
    if scale is not None and scale not in SCALES:
        raise ValueError(f'unknown scale: {scale}')
    if track is not None and track not in TRACKS:
        raise ValueError(f'unknown track: {track}')
    selected = [
        name for name, spec in TASK_SPECS.items()
        if (scale is None or spec['scale'] == scale)
        and (category is None or spec['category'] == category)
        and (track is None or spec.get('track', 'voxel') == track)
    ]
    if not selected:
        raise ValueError('no tasks matched filter')

    cards: list[str] = []
    for task_name in selected:
        spec = TASK_SPECS[task_name]
        f = fixture(task_name)
        ex = example(task_name)
        rep = assess(f, ex)
        comp = rep['completion']
        errors = sum(1 for i in rep['issues'] if i['severity'] == 'error')
        warns = sum(1 for i in rep['issues'] if i['severity'] == 'warn')
        t_track = spec.get('track', 'voxel')
        if t_track == 'voxel':
            grid = validate_cells({'cells': f['cells']}) | validate_cells(ex)
            view = _DEFAULT_PREVIEW_VIEW.get(task_name, 0)
            bounds = f['bounds']
            dims = f'{bounds[3]+1}×{bounds[4]+1}×{bounds[5]+1}'
            preview = '<div class="scene">' + svg(grid, view=view, bounds=bounds) + '</div>'
        else:
            dims = t_track
            thumbs = art_previews(f, ex)
            # Show primary rendered preview (front assembled head for head-skin, quantized map or banner)
            chosen = thumbs[1] if t_track == 'head-skin' and len(thumbs) > 1 else thumbs[0]
            preview = '<div class="scene art">' + chosen[1] + '</div>'

        status = f'{comp["met_count"]}/{comp["total_count"]} checks · {errors} err · {warns} warn'
        cards.append(
            '<article class="card">'
            f'<div class="meta"><span>{html.escape(spec["scale"])} · {html.escape(spec["category"])}</span>'
            f'<span>{html.escape(dims)}</span></div>'
            f'<h2>{html.escape(task_name)}</h2>'
            + preview
            + f'<div class="badge">{html.escape(status)}</div>'
            + f'<p class="brief">{html.escape(spec["brief"])}</p>'
            '</article>'
        )

    doc = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>prayabench reference atlas</title>'
        '<style>*{box-sizing:border-box}body{font:15px/1.45 system-ui,sans-serif;background:#eef2ee;color:#1f3128;margin:0}'
        'main{max-width:1440px;margin:auto;padding:32px 24px}h1{font-size:38px;letter-spacing:-1px;margin:0 0 8px}'
        '.note{color:#4d6257;margin:0 0 24px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}'
        '.card{background:#fff;border:1px solid #cad6cc;border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px}'
        '.meta{display:flex;justify-content:space-between;font:12px monospace;color:#52715d;text-transform:uppercase}'
        'h2{margin:0;font-size:19px}.scene{background:#eef2ef;border-radius:10px;overflow:hidden;aspect-ratio:6/5;display:flex;align-items:center;justify-content:center}'
        '.scene svg,.scene img{width:100%;height:100%;object-fit:contain;display:block}'
        '.badge{font:12px monospace;color:#1e5635;background:#e4f2e8;border-radius:999px;padding:4px 10px;align-self:flex-start}'
        '.brief{margin:0;font-size:13px;color:#45594f}</style>'
        f'<main><h1>prayabench reference atlas ({len(selected)} tasks)</h1>'
        '<p class="note">Deterministic reference examples, not model results. Offline flat-colour previews.</p>'
        '<section class="grid">' + '\n'.join(cards) + '</section></main></html>'
    )
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc)
    return out_path
