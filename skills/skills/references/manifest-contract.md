# Manus Skill Manifest Contract

Use this contract when deciding whether a package is loadable as a Manus skill.

| Check | Requirement | Blocking? |
|---|---|---|
| Package entrypoint | The package contains `SKILL.md` at its root. | Yes |
| Frontmatter | The file starts with YAML frontmatter delimited by `---`. | Yes |
| Required metadata | `name` and `description` are present, non-empty strings. | Yes |
| Name format | `name` uses lowercase letters, digits, and single hyphens; it is at most 64 characters and matches the package directory. | Yes |
| Description | `description` is at most 1,024 characters and contains no angle brackets. It states what the skill does and when to use it. | Yes |
| Supported metadata | Use only runtime-supported frontmatter keys. For the baseline validator, these are `name`, `description`, `license`, `allowed-tools`, and `metadata`. | Yes |
| Body | The Markdown body is non-empty, actionable, and under 500 lines. | Yes |
| Resources | Referenced scripts, references, and templates exist and are safe to invoke. | Yes when referenced |
| Quality | Inputs, outputs, boundaries, and a local acceptance check are clear. | No, but strongly recommended |

The platform validator is authoritative for the baseline manifest checks:

```bash
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py /absolute/path/to/skill
```

Repository audits should also check name-to-directory alignment, broken relative references, accidental secrets, duplicated layer instructions, and unreviewed executable resources. Keep operational guidance in `SKILL.md`; put large schemas and variant-specific material in `references/`.
