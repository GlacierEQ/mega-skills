#!/usr/bin/env python3
"""Bounded offline Skill authoring: structured spec -> validated skill + evaluation corpus.

No model calls, tool permissions, provider installation, or behavioral evaluation are implied.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRECHECK_SPEC = importlib.util.spec_from_file_location('skill_preflight', HERE / 'validate_package.py')
preflight = importlib.util.module_from_spec(PRECHECK_SPEC)
PRECHECK_SPEC.loader.exec_module(preflight)
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
FAMILIES = {'positive', 'negative', 'ambiguous', 'adversarial', 'contradictory', 'recovery'}


def require_text(obj, field, limit=2000):
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip() or len(value) > limit or '\x00' in value:
        raise ValueError(f'INVALID_TEXT:{field}')
    return value.strip()


def require_list(obj, field):
    items = obj.get(field)
    if not isinstance(items, list) or not items or len(items) > 50:
        raise ValueError(f'INVALID_LIST:{field}')
    return [require_text({'value': item}, 'value') for item in items]


def check_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError('SPEC_MUST_BE_OBJECT')
    allowed = {'name', 'description', 'purpose', 'triggers', 'avoid_when', 'steps', 'verification', 'evals', 'references'}
    if set(spec) - allowed:
        raise ValueError('UNRECOGNIZED_SPEC_FIELD:' + ','.join(sorted(set(spec) - allowed)))
    name = require_text(spec, 'name', 64)
    if not NAME.fullmatch(name):
        raise ValueError('INVALID_SKILL_NAME')
    description = require_text(spec, 'description', 1024)
    purpose = require_text(spec, 'purpose')
    triggers, avoid = require_list(spec, 'triggers'), require_list(spec, 'avoid_when')
    verification = require_list(spec, 'verification')
    steps = spec.get('steps')
    if not isinstance(steps, list) or not steps or len(steps) > 30:
        raise ValueError('INVALID_STEPS')
    for index, step in enumerate(steps):
        if not isinstance(step, dict) or set(step) != {'action', 'evidence', 'failure'}:
            raise ValueError(f'INVALID_STEP:{index}')
        for field in ('action', 'evidence', 'failure'):
            require_text(step, field)
    evals = spec.get('evals')
    if not isinstance(evals, list) or len(evals) < len(FAMILIES):
        raise ValueError('EVAL_FAMILY_BREADTH_MISSING')
    families = set()
    for index, case in enumerate(evals):
        if not isinstance(case, dict) or set(case) != {'family', 'prompt', 'expected_behavior'}:
            raise ValueError(f'INVALID_EVAL:{index}')
        family = require_text(case, 'family')
        if family not in FAMILIES or family in families:
            raise ValueError('EVAL_FAMILY_DUPLICATED_OR_UNKNOWN')
        families.add(family)
        require_text(case, 'prompt')
        require_text(case, 'expected_behavior')
    if families != FAMILIES:
        raise ValueError('EVAL_FAMILY_BREADTH_MISSING')
    references = spec.get('references', {})
    if not isinstance(references, dict) or len(references) > 40:
        raise ValueError('INVALID_REFERENCES')
    for filename, content in references.items():
        if not isinstance(filename, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*\.md', filename):
            raise ValueError('UNSAFE_REFERENCE_FILENAME')
        if not isinstance(content, str) or not content.strip() or len(content) > 50000:
            raise ValueError('INVALID_REFERENCE_CONTENT')
    return {'name': name, 'description': description, 'purpose': purpose,
            'triggers': triggers, 'avoid_when': avoid, 'steps': steps,
            'verification': verification, 'evals': evals, 'references': references}


def render(s):
    lines = ['---', 'name: ' + s['name'], 'description: ' + json.dumps(s['description'], ensure_ascii=False),
             '---', '', '# ' + s['name'].replace('-', ' ').title(), '', s['purpose'], '',
             '## Activation', '', '**Use when**']
    lines += ['- ' + item for item in s['triggers']]
    lines += ['', '**Do not use when**'] + ['- ' + item for item in s['avoid_when']]
    lines += ['', '## Procedure', '']
    for i, step in enumerate(s['steps'], 1):
        lines += [f'### {i}. {step["action"]}', '', '- Evidence: ' + step['evidence'],
                  '- If blocked: ' + step['failure'], '']
    lines += ['## Verification and handoff', ''] + ['- ' + item for item in s['verification']]
    lines += ['', 'Capture sources, decisions, observed outputs, unresolved risks and the exact continuation cursor.',
              'Do not claim execution, acceptance, installation, or external provider success without provider readback.', '',
              '## Behavioral evaluation', '',
              'Review the six independent evaluation families in `evals/scenarios.json` with an actual host.',
              'These are test specifications, not passing behavioral results.']
    if s['references']:
        lines += ['', '## References', ''] + [f'- [Reference {i}](references/{f})' for i, f in enumerate(sorted(s['references']), 1)]
    return '\n'.join(lines) + '\n'


def _files(root):
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('SYMLINK_EXISTING_SKILL')
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def author(spec, output_dir):
    s = check_spec(spec)
    output = Path(output_dir).absolute()
    # Reject symlink parent traversal rather than resolving it into an unrelated tree.
    for ancestor in (output, *output.parents):
        if ancestor.is_symlink():
            raise ValueError('SYMLINK_OUTPUT_ROOT')
    output.mkdir(parents=True, exist_ok=True)
    target = output / s['name']
    if target.is_symlink():
        raise ValueError('SYMLINK_EXISTING_SKILL')
    with tempfile.TemporaryDirectory(prefix='.skill-creator-', dir=output) as tempdir:
        source = Path(tempdir) / s['name']
        source.mkdir()
        (source / 'SKILL.md').write_text(render(s), encoding='utf-8')
        eval_dir = source / 'evals'
        eval_dir.mkdir()
        (eval_dir / 'scenarios.json').write_text(json.dumps({'schema_version': 1, 'skill_name': s['name'], 'behavioral_evaluation': 'NOT_RUN', 'cases': s['evals']}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        if s['references']:
            refs = source / 'references'
            refs.mkdir()
            for filename, content in s['references'].items():
                (refs / filename).write_text(content.rstrip() + '\n', encoding='utf-8')
        check = preflight.inspect_skill(source)
        if check['status'] != 'PASS_STATIC_ONLY':
            raise ValueError('PACKAGE_STATIC_VALIDATION_FAILED:' + ','.join(check['errors']))
        if target.exists():
            if not target.is_dir():
                raise ValueError('TARGET_EXISTS_DIFFERENT')
            if _files(target) != _files(source):
                raise ValueError('TARGET_EXISTS_DIFFERENT')
            status = 'ALREADY_PRESENT_IDENTICAL'
        else:
            source.rename(target)
            status = 'SKILL_AUTHORED_STATICALLY_VALIDATED'
    return {'skill': s['name'], 'path': str(target), 'status': status,
            'source_sha256': check['package_sha256'], 'authoring_execution': 'LOCAL_EXECUTED',
            'behavioral_evaluation': 'NOT_RUN', 'provider_execution': 'NOT_RUN',
            'installation': 'NOT_RUN', 'eval_families': sorted(FAMILIES)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if not args.execute:
        print(json.dumps({'skill': 'skill-creator', 'status': 'adapter_ready', 'capability_executed': False,
                          'reason': 'Supply --execute --spec FILE.json --output DIRECTORY to author a validated skill.'}))
        return 0
    if not args.spec or not args.output:
        print(json.dumps({'status': 'INPUT_REQUIRED', 'provider_execution': 'NOT_RUN',
                          'error': 'Both --spec and --output are required for --execute.'}))
        return 2
    try:
        if args.spec.stat().st_size > 1_000_000:
            raise ValueError('SPEC_TOO_LARGE')
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
        result = author(spec, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'FAIL', 'capability_executed': False,
                          'provider_execution': 'NOT_RUN', 'error': str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())