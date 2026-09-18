# Output Execution Runs

This report records how output-eval variants were produced and whether timing or token evidence is observed or estimated.

- Cases: `5`
- Variant runs: `10`
- Command executed: `10`
- Model executed: `0`
- Recorded fixtures: `0`
- Timing observed: `10`
- Token observed: `0`
- Token estimated: `10`
- Delta: `95.0`
- Gate pass: `True`

No model-executed runs are recorded yet.

Use `python3 scripts/yao.py output-exec --provider-runner openai` or `--runner-command` with a reviewed provider-backed runner to replace recorded fixtures with real model output evidence.

Command runner evidence is present. This proves the eval harness executed an external command, but it is not provider-backed model evidence unless the runner reports model metadata.

## Runs

| Case | Variant | Mode | Model | Duration ms | Tokens | Score | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| low-information-intake | baseline | command | local-output-eval-runner | 16.06 | 14 | 25.0 | pass |
| low-information-intake | with_skill | command | local-output-eval-runner | 15.6 | 36 | 100.0 | pass |
| layout-only-boundary | baseline | command | local-output-eval-runner | 16.27 | 11 | 0.0 | pass |
| layout-only-boundary | with_skill | command | local-output-eval-runner | 16.01 | 38 | 100.0 | pass |
| jd-keyword-gap | baseline | command | local-output-eval-runner | 18.51 | 22 | 0.0 | pass |
| jd-keyword-gap | with_skill | command | local-output-eval-runner | 17.82 | 43 | 100.0 | pass |
| multi-role-variants | baseline | command | local-output-eval-runner | 17.65 | 15 | 0.0 | pass |
| multi-role-variants | with_skill | command | local-output-eval-runner | 17.52 | 39 | 100.0 | pass |
| causal-claim-review | baseline | command | local-output-eval-runner | 16.18 | 16 | 0.0 | pass |
| causal-claim-review | with_skill | command | local-output-eval-runner | 16.69 | 45 | 100.0 | pass |

## Next Fixes

- Keep recorded fixtures as reproducible baselines, but do not describe them as model-executed evidence.
- Use `scripts/provider_output_eval_runner.py` for provider-backed holdout cases when release confidence depends on real generation behavior.
- Compare timing, token cost, and assertion deltas before promoting a skill to governed reuse.
