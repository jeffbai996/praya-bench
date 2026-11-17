# Evaluation protocol

## Versioned multi-scale inputs

Every run records a task, scale (`small`, `medium`, `large`, `terraforming`),
category, coordinate `bounds`, `source_limit`, baseline fixture, supported palette
and prompt hash. Changing any of these requires a new run directory. The evaluator
version and source hash appear in check reports. Pin the package commit and compiler
image digest for reproducibility.

## Recommended experiment

1. Sample tasks across scales and problem types—compact street buildings, multi-unit
   or multi-storey circulation (`rowhouse-terrace`, `elevated-rail-station`,
   `midrise-apartments`, `civic-office-tower`), and terrain/chunk repair
   (`chunk-cliff-scar`, `chunk-river-seam`, `coastal-seawall`, `quarry-reclamation`)—
   and freeze model IDs and inference settings before running. Use `prayabench init-suite`
   to initialize a filtered or complete task set reproducibly.
2. Use fresh sessions and identical visible inputs and tools for each trial.
3. Run at least three repetitions. Report source-limit failures, timeouts and
   transport errors separately; a transport failure is not evidence of poor design.
4. Keep raw final answers and compiled JSON unchanged. The compiler records
   `stripped_markdown_fence` when extracting a fenced code block and `diagnostic_only`
   when `--diagnostic-overbudget` is used. Do not count repaired or overbudget
   runs as compliant first-pass wins.
5. Evaluate bounded geometry, interior lighting, subsurface fill and brief completion,
   then compare anonymized views across exterior rotations and adaptive floor cutaways.
6. If testing repair ability, supply the same correction prompt and repair budget.
   Keep first-pass and repaired results separate.

## Separate dimensions

**Validity:** located construction and terraforming defects—missing supports,
isolated floating backing blocks, gravity blocks over air, unreachable doors,
unlit enclosed rooms (`dark_interior`), orphan chunk-error foliage, subsurface
air cavities under turf (`subsurface_void`), protected-zone edits, budget overruns
and unsupported block names (`issues`).
**Completion:** task-specific checks verifying requested structures, multi-tier
vertical reachability, aircraft beacons, props, chunk-seam elevation continuity,
reconnected roads/waterways and scar top-dressing (`completion`).
**Design:** blind human preference across rotations and floor cutaways, with
written reasons.
**Efficiency:** observed runtime and provider-reported usage, with accounting caveats.

There is no weighted total score. Use `prayabench summary` to inspect validity
and completion side by side across models and scales.

## Native adapters and known limits

The CLI adapters invoke authenticated local clients (`codex`, `claude`, `agy`),
whose system context and transport overhead differ; equal effort labels do not
imply equal compute. Linter findings remain inspectable and can be adjudicated
as false positives with documented reasons. The SVG renderer auto-frames variable
bounds using flat colours and approximate block shapes; an in-game walkthrough
remains a separate evaluation step. Only synthetic MIT fixtures ship with this
repository.
