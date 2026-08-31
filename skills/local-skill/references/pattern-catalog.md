# Pattern Catalog (local-skill)

Initial seed. Run `local-skill pattern_catalog` (or `inspect` then `pattern_catalog`) to refresh from the live tree.

## Dominant conventions observed in mega-skills

- Directory name: hyphenated lowercase (`my-skill-name`)
- Required: `SKILL.md` (YAML front-matter with `name` + `description`), `skill.py` (executable dispatcher)
- Strongly preferred: `scripts/`, `resources/`, `tests/`, `__init__.py`, `requirements.txt`
- Optional: `templates/`, `references/`
- skill.py pattern: thin CLI dispatcher that `exec`s scripts/<command>.py
- Scripts are executable and contain a `main()` + `if __name__ == "__main__"`
- Tests: `tests/test_<name>.py` with structural assertions
- Resources: YAML config + JSON schema is the most common pair
