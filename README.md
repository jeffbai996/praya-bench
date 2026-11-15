# prayabench

**A visual benchmark for AI building in Minecraft.**

Give models the same plot and brief. Inspect what they build, check whether the
doors are reachable and the fixtures are supported, then reveal who built what.

![Synthetic reference scene, not a model result](docs/demo.svg)

prayabench is an experimental, MIT-licensed toolkit for comparing generated voxel
builds. It keeps construction validity, task completion, visual preference and
runtime separate. There is no magic combined score and no authoritative leaderboard.

## Try it without a model or Minecraft server

Python 3.11 or newer; no runtime Python dependencies.

```sh
git clone https://github.com/jeffbai996/praya-bench.git
cd praya-bench
python -m venv .venv
. .venv/bin/activate
python -m pip install .
prayabench demo runs/demo
```

Open `runs/demo/index.html`. Rotate the scenes, lift their roofs, inspect findings
and download your review notes. The two demo scenes are deterministic package
examples, **not model results**. The HTML works offline and sends nothing anywhere.

## A benchmark run

```sh
prayabench tasks
prayabench init runs/cafe --task sloped-cafe
```

This freezes `prompt.txt`, `palette.txt` and a synthetic `fixture.json`, with
SHA-256 hashes in `manifest.json`. Tasks include a sloped café, a compact house,
a pocket park and an existing-shop renovation with a protected historic placard.

Give a model the prompt and supported palette. Have it return the specified
Python `build` function, or supply declarative JSON directly. The same inputs,
model settings, budgets and allowed tools should be used across a comparison.

### Compile Python submissions in Docker

```sh
docker pull python:3.12-slim
prayabench compile runs/cafe answer.py --out runs/cafe/model-a.json
prayabench evaluate runs/cafe runs/cafe/model-a.json --out runs/cafe/model-a.checks.json
```

Generated Python is never executed by the host CLI. The compiler uses a
network-disabled, read-only container with no host mounts, no added privileges,
a non-root user, memory/process limits and CPU/wall-clock limits. It pins the
locally installed image ID in its metadata. It fails closed if Docker or the
image is unavailable; it does not silently execute Python on the host.

To reproduce the image exactly on another machine, pull the recorded registry
digest yourself and pass it with `--image`. Image IDs are local content identities;
tags such as `python:3.12-slim` can change.

The AST checks are an additional format filter, **not a security sandbox**. The
container shares the host kernel. Keep Docker updated; this alpha is intended
for local experiments, not an unattended public code-execution service.

### Or import JSON without executing code

```json
{"cells": [[5, 3, 8, "stone_bricks", null, "plinth", null]]}
```

Cells are `[x, y, z, block_state, sign_lines?, component?, prop_asset?]`.
Coordinates are integers; later writes replace earlier ones. Prop assets are
semantic placeholders (`coffee_maker`, `pos_terminal`, `mailbox_orange`), not
downloaded Minecraft skins. The field contract is in each run's prompt.

### Optional native-client adapters

If you already have an authenticated client installed:

```sh
prayabench generate runs/cafe --provider codex --model YOUR_MODEL --effort medium --out runs/cafe/attempt-a
prayabench compile runs/cafe runs/cafe/attempt-a/answer.py --out runs/cafe/model-a.json
```

Adapters are included for `codex`, `claude` and the optional `agy` client. There
are no bundled credentials, automatic sign-ins or silent provider fallbacks.
Other providers can use the prompt/JSON interface. Generation makes a model call
using your client's account and may consume paid usage. It does not compile or
place the returned code automatically. Native clients have different system
prompts and overhead; compare those runs as **model-plus-client** measurements.
They are instructed not to use tools; only the Claude adapter explicitly disables
its built-in tool list. No claim of identical hidden context is made.

```sh
prayabench compare runs/cafe runs/cafe/model-a.json runs/cafe/model-b.json --out runs/cafe/comparison.html
```

Labels are shuffled and hidden behind a reveal control by default. Use `--named`
to show them. Review notes are exported on demand; reloading loses unsaved notes.

## What gets checked

- Scene bounds and protected terrain/architecture.
- Full backing for wall signs and wall-mounted props.
- Flush support for tabletop props and slender mailbox posts.
- Paired door halves and approximate street-to-door reachability.
- Supported palette names, missing entrances and blank/standing signs.

Roof stairs are not automatically treated as pedestrian stair flights. Chinese
script choice is not a validity failure. Renovations must preserve the original
construction date rather than relabelling old buildings as newly built.

## What does not get proved

The evaluator is a deliberately small approximation, not the Minecraft engine,
a structural simulation, an accessibility audit or a complete block-state
registry. Walking checks permit one-block jumps. Furniture and room quality need
visual review. The renderer uses original flat colours and approximate geometry;
it does not display game textures or sign lettering. Inspect sign records for text.

One appealing scene does not establish a model ranking. Use multiple tasks and
repeats, report failed runs, keep the evaluator version fixed, and record any
manual adjudications separately. Do not quietly repair model output before scoring.

See [the protocol](docs/protocol.md) and [contributing guide](CONTRIBUTING.md).

## Development

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
docker pull python:3.12-slim
PRAYABENCH_DOCKER_TESTS=1 python -m unittest discover -s tests -p test_sandbox.py -v
```

CI tests the package and Docker compiler without calling any models.

## License and provenance

Code, synthetic fixtures and original flat-colour SVG artwork: [MIT](LICENSE).
No Minecraft textures, saved worlds, third-party head skins or private pilot
transcripts are bundled. Contributions must identify their provenance and
redistribution rights. Minecraft belongs to Mojang/Microsoft; this is an
independent project, not an official Minecraft product.

The name comes from the building project that motivated the experiments.
You do not need its world, lore or infrastructure to run prayabench.
