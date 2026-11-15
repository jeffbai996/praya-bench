# Evaluation protocol

## Versioned inputs

Every run records a task, baseline fixture, supported palette and prompt hash.
Changing any of these requires a new run directory. The evaluator version and
source hash appear in check reports. Pin the package commit and compiler image
digest for reproducibility. Runtime inputs, not a model's self-reported success,
determine whether a response compiled and what cells it produced.

## Recommended experiment

1. Select several tasks, model IDs and explicit inference settings before running.
2. Use fresh sessions and identical visible inputs and tools for each trial.
3. Run at least three repetitions. Report source-limit failures, timeouts and
   transport errors separately; a transport failure is not evidence of poor design.
4. Keep raw final answers and compiled JSON unchanged. Report any extraction
   wrappers removed or repairs performed; do not include repaired runs as first-pass wins.
5. Evaluate bounded geometry and compare anonymized views. Have humans assess
   proportions, circulation, structure, terrain integration and task fulfillment.
6. If testing repair ability, supply the same correction prompt and repair budget.
   Keep first-pass and repaired results separate.

## Separate dimensions

**Validity:** identified construction defects and unsupported block names.
**Completion:** whether the requested building, rooms and objects actually exist.
**Design:** blind human preference with written reasons.
**Efficiency:** observed runtime and provider-reported usage, with accounting caveats.

There is no weighted total score in v0.1. A beautiful inaccessible building does
not become valid through averaging; a plain valid box does not automatically win
the design review. Passing existence checks does not prove a room is useful.

## Native adapters

The CLI adapters are a convenience for existing authenticated clients. Their
system context, transport overhead and inference settings differ. Equal labels
such as Medium do not imply equal compute. Report exact model identifiers and
client versions; verify availability rather than silently substituting models.
The code-source character limit is an output contract, not a provider token cap.
Reported API-equivalent costs are not verified subscription charges.

## Review and known limits

Linter findings remain inspectable and can be adjudicated as false positives.
Preserve the raw report and add the reason for any exclusion. Do not adapt a
hidden scoring rule to favor an observed output. Improvements prompted by a run
should be versioned and applied to every candidate, with the original reports kept.

The renderer does not reproduce game lighting, texture detail, door collision,
sign lettering or exact partial-block collision. Street reachability is an
approximation permitting one-block jumps. A real in-game walkthrough remains a
separate evaluation step. Only synthetic fixtures ship with this repository.
