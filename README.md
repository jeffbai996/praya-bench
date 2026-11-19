# prayabench

**A visual benchmark for AI building, terraforming, vehicles and art in Minecraft.**

Give models the same plot and brief—from a kerbside bus shelter to an eight-storey
office tower or a sheared `16×16` chunk error. Inspect what they build, check
whether doors, upper storeys and platforms are reachable, verify supports and
subsurface grading, then reveal who built what.

![Synthetic reference scene, not a model result](docs/demo.svg)

prayabench is an experimental, MIT-licensed toolkit for comparing generated voxel
builds, repairs and artwork. It keeps validity, brief completion,
visual preference and runtime separate. There is no magic combined score and no
authoritative leaderboard.

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

Open `runs/demo/index.html`. Rotate the scenes, inspect dynamic upper and ground
cutaways, review automated findings and brief checks, and download your review
notes. The two demo scenes are deterministic package examples, **not model results**.
The HTML works offline and sends nothing anywhere.

## Benchmark suite

```sh
prayabench tasks
prayabench tasks --scale large
prayabench tasks --scale terraforming --json
prayabench tasks --track map-art
prayabench init runs/chunk --task chunk-cliff-scar
prayabench init-suite runs/terra --scale terraforming
```

`init` freezes `prompt.txt`, `palette.txt` and a synthetic `fixture.json` with
per-task geometry and constraints, pinned by SHA-256 hashes in `manifest.json`.

### `small` — Street furniture, parks & compact buildings
- **`transit-shelter`** (`18×14×16`, `civic-micro`): kerbside bus/tram canopy, windscreen glazing, route sign, bench, `ticket_validator` and `trash_bin`.
- **`pocket-park`** (`24×18×22`, `landscape-civic`): continuous park path, conifer and broadleaf trees, benches, planted beds and `mailbox_orange`.
- **`sloped-cafe`** (`24×18×22`, `commercial-slope`): one-storey café and pocket garden on an east-rising lateral slope.
- **`shop-renovation`** (`24×18×22`, `adaptive-reuse`): interior café fit-out inside a protected older shell with a historic `Built 2012` placard.
- **`small-house`** (`24×18×22`, `residential-two-storey`): two-storey compact house with interior stairs, headroom and paired bed.
- **`utility-substation`** (`22×16×20`, `utility-infrastructure`): enclosed electrical substation yard, switchgear room, hazard signage, `computer_monitor` and `fire_hydrant`.

### `medium` — Urban infill, bridges, clinics & rowhouses
- **`canal-crossing`** (`24×18×22`, `spanning-infrastructure`): walkable footbridge spanning a protected stone-lined water canal to reach a south-bank tea kiosk.
- **`corner-shophouse`** (`24×18×22`, `urban-corner-mixed-use`): two-storey corner bakery and upstairs studio addressing two protected streets.
- **`party-wall-infill`** (`24×18×22`, `zero-lot-line-infill`): narrow two-storey bookshop and reading loft between two protected neighbour party walls.
- **`hillside-pavilion`** (`24×18×22`, `steep-terrain-terracing`): stepped retaining route climbing a steep 2D slope (`ground(x, z)`) to a summit pavilion.
- **`rowhouse-terrace`** (`30×22×24`, `residential-rowhouse`): three attached two-storey urban rowhouses with separate street stoops/doors, party walls and bedrooms.
- **`medical-clinic`** (`28×20×24`, `civic-healthcare`): two-storey urgent-care clinic and pharmacy with check-in, dispensary, `defibrillator` and upstairs exam rooms.

### `large` — Supermarkets, transit stations, midrises & towers
- **`grocery-supermarket`** (`32×20×28`, `commercial-large-format`): deep-floorplate supermarket with dual street/loading access, checkout lanes, gondolas, thorough interior lighting and `parking_meter`.
- **`elevated-rail-station`** (`34×24×26`, `transit-station`): street concourse, `ticket_validator` gates and covered stairs climbing to `y=11` platforms beside a protected twin-track stone rail viaduct.
- **`midrise-apartments`** (`30×30×26`, `residential-midrise`): five-storey mixed-use midrise with ground retail, separate residential lobby, multi-tier stair core (`y>=6, 12, 18`), balconies and furnished flats.
- **`civic-office-tower`** (`30×40×28`, `highrise-tower`): eight-storey podium-and-shaft tower (`y>=32`) with mullion depth, multi-tier stair core (`y>=6, 14, 22`) and rooftop `redstone_torch` aircraft warning lights.

### `terraforming` — Chunk-error repair, waterways, seawalls & reclamation
- **`chunk-cliff-scar`** (`32×22×28`, `terraforming-chunk-error`): repair a sunken `16×16` corrupted chunk (`y=1`), clear floating sheared treetop leaves, fill solidly without hollow subsurface air crusts, blend all four seams into surrounding hillside elevations, and reconnect a severed east–west road.
- **`chunk-river-seam`** (`32×20×26`, `terraforming-chunk-error`): excavate a displaced `y=10` `16×16` chunk monolith damming an east–west creek, restore continuous water flow and sandy banks across the seams, and span the creek with a footbridge.
- **`coastal-seawall`** (`28×20×26`, `terraforming-waterfront`): re-grade an eroded coastal bluff between an upland `y=7` street and a protected tidal bay into a masonry seawall and stepped waterfront promenade.
- **`quarry-reclamation`** (`28×22×26`, `terraforming-reclamation`): reclaim a gouged raw-stone quarry pit (`y=1`) into a solid-filled terraced sunken garden and pond connected by stairs from the street.

### Vehicles, civil works and retrofits

- **Vehicles** include a box truck, bus, ambulance, rail coach and ferry. Each has four
  frozen compass orientations. The checks cover the envelope, body connectivity and
  the relevant kerbside door, axles, couplings or navigation lights. Vehicles can
  use shulker boxes, banners, hoppers, layered snow and blank trim signs.
- **Civil works** include a diagonal road, curved tunnel and junction sign.
  Checks cover full road width, tunnel clearance, the protected hill and a
  specified sightline to the sign.
- **Field and retrofit cases** include two specimen trees, a washroom, rooftop HVAC,
  a facade retrofit, a shop conversion with preserved stairs and historic placard,
  and a four-cell inspector repair on a supplied faulty café.

```sh
prayabench init-suite runs/vehicles --category vehicle --all-facings
prayabench compile-rotations city-bus bus.py --out runs/bus-rotations
```

Vehicle build functions use `build(put, box, head, sign, ground, facing)`.
Reuse the same source on all four fixtures to test rotation. Rotate a north-facing
position on the 23×23 plot to face east with `(x, z) → (22 - z, x)`, and rotate
its directional block properties too. `compile-rotations` freezes, compiles and
evaluates each orientation and writes a `rotations.json` summary.

### Map art, loom banners and head skins

These nine cases accept declarative JSON. `generate` saves their raw response as
`answer.json`. Save the JSON object to a file and pass it directly to
`evaluate` and `compare`.

| Track | Cases | Checks and previews |
| --- | --- | --- |
| `map-art` | Storefront wordmark, transit departure board, motorway guide | Contrast after quantization to a fixed map-palette subset, alpha coverage, detail regions and tile seams |
| `loom-banner` | Harbour burgee, civic shield, rail roundel | Six-layer cap, supported loom patterns, exact pixel agreement and per-dye IoU on schematic masks |
| `head-skin` | Parking meter, HVAC vent, mailbox | Java 64×64 head UV islands, six opaque inner faces, outer-layer relief, front/back contrast and assembled head previews |

```sh
prayabench init runs/board --task map-departure-board
prayabench evaluate runs/board answers/board.json --out runs/board/checks.json
prayabench compare runs/board answers/board.json --out runs/board/comparison.html
```

The raster input is a palette of single-character symbols, ordered rectangles
`[x,y,width,height,symbol]`, and optional sparse rows. Use `#RRGGBB` or
`#RRGGBBAA` for colours. A loom submission is an ordered recipe
such as `{"base":"blue","layers":[["stripe_middle","white"]]}`. Each frozen
prompt supplies the coordinates, target or pattern vocabulary for its case.
Readability and asset recognition still need visual review.

### Compile Python submissions in Docker

```sh
docker pull python:3.12-slim
prayabench compile runs/chunk answer.py --out runs/chunk/model-a.json
prayabench evaluate runs/chunk runs/chunk/model-a.json --out runs/chunk/model-a.checks.json
```

Generated Python is never executed by the host CLI. The compiler uses a
network-disabled, read-only container with no host mounts, no added privileges,
a non-root user, memory/process limits and CPU/wall-clock limits. It pins the
locally installed image ID in `.sandbox.json` and fails closed if Docker or the
image is unavailable. If a response wraps its code in a single Markdown fence,
the compiler extracts the Python block and records `stripped_markdown_fence: true`.

Submissions exceeding the task's `source_limit` (`14,000`–`22,000` characters by
scale) are rejected by default. Pass `--diagnostic-overbudget` to compile an
over-limit submission for visual inspection; the output is marked
`diagnostic_only: true` and flagged `source_budget_exceeded` during evaluation.

The AST checks are an additional format filter, **not a security sandbox**. The
container shares the host kernel. Keep Docker updated; this alpha is intended
for local experiments, not an unattended public code-execution service.

### Optional native-client adapters, comparison & summary

```sh
prayabench generate runs/chunk --provider codex --model YOUR_MODEL --effort medium --out runs/chunk/attempt-a
prayabench compile runs/chunk runs/chunk/attempt-a/answer.py --out runs/chunk/model-a.json
prayabench compare runs/chunk runs/chunk/model-a.json runs/chunk/model-b.json --out runs/chunk/comparison.html
prayabench summary runs/chunk/*.checks.json --out runs/chunk/summary.json
```

Adapters are included for `codex`, `claude` and `agy` without bundled credentials
or silent fallbacks. `compare` auto-frames scenes of any footprint or tower height,
shuffles blind labels by default (`--named` reveals them), and slices scenes across
adaptive floor cutaways. `summary` aggregates validity and completion side by side.

## What gets checked

**Construction & terrain validity (`issues`):**
- Dynamic per-task scene bounds, source-character budgets and protected street, viaduct, canal, neighbour and reference-terrain cells.
- Connected solid backing for wall signs, wall torches and wall-mounted props (rejecting isolated floating 1-block filler cubes); overhead or horizontal bar support for hanging signs.
- Flush support for tabletop/ground props, rails, pots, beds, carpets, standing lights and slender `mailbox_orange` / `parking_meter` posts; hinge/floor/ceiling support for trapdoors; non-passable support under `sand` / `gravel` gravity blocks.
- Soil/grass/moss substrates for planted ground flora, including two-block tall plants.
- Aligned paired door and bed halves, glass-pane door jamb warnings, blind glazing against opaque party walls, 3D sky + block-light interior darkness warnings (`dark_interior`), and street-to-door reachability.
- Terraforming defects: un-cleared floating chunk-error leaf artifacts (`orphan_foliage`), hollow 1-block turf crusts over air cavities (`subsurface_void`), and contradictory renovation dating.

**Brief completion (`completion`):**
- Task-specific structural and functional targets: minimum edited volume, peak tower height, multi-tier vertical floor reachability (elevated rail platforms, midrises, highrises), rooftop aircraft warning beacons, south-bank/summit/multi-rowhouse entrances, dual-street glazing, semantic props (`coffee_maker`, `pos_terminal`, `mailbox_orange`, `ticket_validator`, `computer_monitor`, `fire_hydrant`, `parking_meter`, `trash_bin`, `defibrillator`), paired beds, trees/flora, water features, chunk-seam elevation matching (`smooth_chunk_seam`), reconnected roads (`reconnected_road`), restored continuous waterways (`continuous_waterway`), and scar top-dressing (`surface_top_dressing`).

## What does not get proved

The evaluator is a deliberately small approximation, not the Minecraft engine,
a structural simulation, an accessibility audit or a complete block-state
registry. Walking checks permit one-block jumps. Passing completion checks proves
requested elements exist, not that rooms or landscapes look good. Human visual
review remains essential.

See [the protocol](docs/protocol.md) and [contributing guide](CONTRIBUTING.md).

## Development

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
docker pull python:3.12-slim
PRAYABENCH_DOCKER_TESTS=1 python -m unittest discover -s tests -p test_sandbox.py -v
```

## License and provenance

Code, synthetic fixtures and original flat-colour SVG artwork: [MIT](LICENSE).
No Minecraft textures, saved worlds, third-party head skins or private pilot
transcripts are bundled. Minecraft belongs to Mojang/Microsoft; this is an
independent project, not an official Minecraft product.
