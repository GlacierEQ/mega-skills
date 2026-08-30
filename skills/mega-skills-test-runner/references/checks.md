# Local Validation Reference

Run from a trusted checkout root that contains `registry/`, `scripts/validate_hierarchy.py`, and `tests/`.

| Result | Interpretation | Next action |
|---|---|---|
| Validator fails | A canonical package, entrypoint, ID, dependency, Combo contract, or Mega route rule is malformed or unresolved. | Read the named error; fix the contract and registry together. |
| Regression suite fails | A tested behavior differs from the intended graph. | Determine whether the implementation or test needs change; do not weaken an assertion without an explicit behavior decision. |
| Diff hygiene fails | The pending diff has whitespace errors. | Correct the reported line before release. |
| Repository-state output | The tested working state and branch were recorded. | Include it with release evidence; it is not a pass/fail assertion. |

The standard command is:

```bash
python /path/to/mega-skills-test-runner/scripts/run_checks.py --repo /path/to/mega-skills
```

For a machine-readable artifact:

```bash
python /path/to/mega-skills-test-runner/scripts/run_checks.py \
  --repo /path/to/mega-skills \
  --report /tmp/mega-skills-validation.json
```

Use `--fail-fast` during local diagnosis. Use `--skip-diff-check` only when the directory is intentionally not a Git working tree or whitespace checks are handled elsewhere; preserve that exception in the validation evidence.
