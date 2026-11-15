# Contributing

Useful contributions include new synthetic tasks, located false-positive cases,
tests for missed construction defects, renderer improvements and provider adapters.
Keep the core usable offline and without a paid account.

For an evaluator change, include a small fixture demonstrating the problem and
a regression test. Preserve raw findings when manually adjudicating a result.
Do not turn aesthetic preferences into hard physics errors or introduce an
opaque aggregate score without a separately reviewed methodology.

For a result contribution, include model/client IDs, settings, frozen inputs,
unchanged final answers, compiled JSON, elapsed time and the evaluator version.
Redact credentials, local account paths and private context. Do not include
hidden reasoning traces or claim provider billing was verified when it was not.
The deterministic demo is not a model result and must never be ranked as one.

Only contribute code, fixtures and artwork you have the right to redistribute
under MIT. Do not upload Minecraft assets, proprietary skins or private worlds.
Adding an adapter must not embed credentials or make model calls in tests/CI.

Run the standard unittest suite. Changes to compilation or isolation also need
the opt-in Docker integration tests. Avoid host-side fallbacks for generated code.
