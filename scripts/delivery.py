#!/usr/bin/env python3
"""Run project commands for fixed candidates. Keep results and uncertain operations.

The project runner writes SDD_GATE_RESULT. This file states which artifacts the
runner observed. A receipt is project evidence, not independent provenance.
Project credentials and permissions must control actual release authority.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time
import uuid

from coordination import reserve, store, unreserve


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def strict_json(data):
    def object_value(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('A JSON object contains a repeated key')
            value[key] = item
        return value

    def invalid_constant(value):
        raise ValueError('A JSON number must be finite')

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('A JSON number must be finite')
        return number

    return json.loads(data, object_pairs_hook=object_value, parse_constant=invalid_constant,
                      parse_float=finite_float)


def immutable(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', value):
        raise ValueError('Use a short identifier with letters, digits, periods, underscores, or hyphens')
    return value


def local_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('Use a project-relative file path')
    path = root / name
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('The input is not a file inside the project')
    for part in (path, *path.parents):
        if part == root:
            break
        info = part.lstat()
        if part.is_symlink() or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('The input path contains a link or reparse point')
    return resolved


def command_valid(command):
    if not isinstance(command, dict) or not isinstance(command.get('argv'), list) or not command['argv']:
        raise ValueError('An argv list is necessary for the command')
    if any(not isinstance(arg, str) or not arg or '\x00' in arg for arg in command['argv']):
        raise ValueError('Each command argument must be a nonempty string')
    timeout = command.get('timeout')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('A positive finite timeout is necessary for the command')


def fingerprints(root, manifest):
    observed = {name: digest(local_file(root, name).read_bytes()) for name in manifest['basis']}
    if observed != manifest['basis']:
        raise ValueError('An applicable basis file changed')
    result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', 'HEAD'],
                            capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise ValueError('Current Git commit evidence is necessary for candidate delivery')
    if result.stdout.strip() != manifest['commit']:
        raise ValueError('The checkout commit differs from the candidate commit')
    return observed


def validate_manifest(root, manifest):
    if not isinstance(manifest, dict) or manifest.get('format') != 1:
        raise ValueError('The manifest format is not supported')
    identifier(manifest.get('candidate'))
    if not isinstance(manifest.get('commit'), str) or not re.fullmatch(r'[a-f0-9]{40}|[a-f0-9]{64}', manifest['commit']):
        raise ValueError('Use the full identifier of the fixed commit')
    for field in ('basis', 'artifacts'):
        values = manifest.get(field)
        if not isinstance(values, dict) or not values:
            raise ValueError('Basis files and artifacts are necessary in the manifest')
        if any(not isinstance(name, str) or not name or not isinstance(value, str) or
               not re.fullmatch(r'sha256:[a-f0-9]{64}', value) for name, value in values.items()):
            raise ValueError('Use named SHA256 digests')
    for field in ('target', 'target_revision'):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise ValueError('The target and its expected revision are necessary')
    for field in ('rc_resources', 'production_resources'):
        values = manifest.get(field)
        if not isinstance(values, list) or not values or any(not isinstance(key, str) or not key.strip() for key in values):
            raise ValueError('Explicit resource keys are necessary for each stage')
        if len(set(values)) != len(values):
            raise ValueError('Resource keys must be unique')
    if set(manifest['rc_resources']) & set(manifest['production_resources']):
        raise ValueError('RC and production resources must have different keys')
    commands = manifest.get('commands', {})
    if not isinstance(commands, dict) or set(commands) != {'rc', 'publish', 'verify'}:
        raise ValueError('The rc, publish, and verify commands are necessary in the manifest')
    for command in commands.values():
        command_valid(command)
    gates = manifest.get('gates')
    if not isinstance(gates, dict) or not gates:
        raise ValueError('Mandatory gates are necessary in the manifest')
    for name, gate in gates.items():
        identifier(name)
        command_valid(gate)
        tests = gate.get('tests')
        if not isinstance(tests, list) or not tests or any(not isinstance(test, str) or not test.strip() for test in tests):
            raise ValueError('Mandatory test identifiers are necessary for each gate')
        if len(set(tests)) != len(tests):
            raise ValueError('Test identifiers must be unique in a gate')
    if manifest.get('authority') not in manifest['basis']:
        raise ValueError('The authority file must be a frozen basis input')
    fingerprints(root, manifest)


def candidate(state, name, root):
    item = state['candidates'].get(name)
    if item is None:
        raise ValueError('The candidate is not registered')
    if item['checkout'] != str(root):
        raise ValueError('Use the checkout that registered the candidate')
    if item.get('invalid'):
        raise ValueError('The candidate has failed evidence. Register a new candidate')
    return item


def holder(item, kind):
    return 'delivery:' + kind + ':' + item['manifest']['candidate']


def complete(item):
    return item.get('rc') and set(item.get('gates', {})) == set(item['manifest']['gates'])


def authority(root, manifest, supplied):
    if supplied != manifest['authority']:
        raise ValueError('Supply the project authority file that you froze')
    record = strict_json(local_file(root, supplied).read_bytes())
    expected = dict(authorized=True, candidate=manifest['candidate'], target=manifest['target'],
                    target_revision=manifest['target_revision'])
    if not isinstance(record, dict) or record.get('authorized') is not True or any(record.get(key) != value for key, value in expected.items()):
        raise ValueError('The project authority record does not authorize this release')


def selection_valid(state, item, generation):
    manifest = item['manifest']
    selected = state['selections'].get(manifest['target'])
    if not selected or selected['candidate'] != manifest['candidate'] or selected['generation'] != generation:
        raise ValueError('The release selection changed')
    if selected['target_revision'] != manifest['target_revision']:
        raise ValueError('The expected target revision changed')


def receipt_valid(receipt, manifest, stage, gate):
    if not isinstance(receipt, dict) or receipt.get('candidate') != manifest['candidate']:
        raise ValueError('The receipt identifies a different candidate')
    if receipt.get('artifacts') != manifest['artifacts']:
        raise ValueError('The observed artifact digests differ from the fixed artifacts')
    if stage in ('publish', 'verify'):
        if receipt.get('target') != manifest['target'] or receipt.get('target_revision') != manifest['candidate']:
            raise ValueError('The receipt must identify the observed target and released candidate revision')
        if stage == 'publish' and receipt.get('previous_target_revision') != manifest['target_revision']:
            raise ValueError('The receiver must report the target revision from before publication')
    if stage == 'gate':
        tests = receipt.get('tests')
        expected = set(manifest['gates'][gate]['tests'])
        if not isinstance(tests, dict) or set(tests) != expected or any(value != 'passed' for value in tests.values()):
            raise ValueError('Every mandatory test must be present and passed. For extra tests, a manifest revision is necessary')


def register(args, root):
    raw = args.manifest.read_bytes()
    manifest = strict_json(raw)
    validate_manifest(root, manifest)
    with store(root) as (state, directory):
        name = manifest['candidate']
        old = state['candidates'].get(name)
        if old:
            if old['manifest_sha256'] == digest(raw) and old['checkout'] == str(root):
                return copy.deepcopy(old)
            raise ValueError('The candidate identifier has a frozen manifest')
        path = directory / 'delivery/manifests' / (uuid.uuid4().hex + '.json')
        immutable(path, raw)
        item = dict(manifest=manifest, manifest_sha256=digest(raw), manifest_path=str(path),
                    checkout=str(root), gates={}, rc=None, publish=None, verify=None, invalid=False)
        state['candidates'][name] = item
        return copy.deepcopy(item)


def select(args, root):
    with store(root) as (state, _):
        item = candidate(state, args.candidate, root)
        manifest = item['manifest']
        fingerprints(root, manifest)
        if not complete(item):
            raise ValueError('RC deployment and every mandatory gate must pass')
        if any(op['stage'] in ('publish', 'verify') and op['target'] == manifest['target'] and
               op['status'] in ('running', 'uncertain', 'passed') and
               not state['candidates'][op['candidate']].get('verify') and
               not state['candidates'][op['candidate']].get('invalid')
               for op in state['operations'].values()):
            raise ValueError('The production outcome has no resolution')
        previous = state['selections'].get(manifest['target'], {})
        if previous.get('generation', 0) != args.expected:
            raise ValueError('The expected selection generation is stale')
        selected = dict(candidate=args.candidate, generation=args.expected + 1,
                        target_revision=manifest['target_revision'])
        state['selections'][manifest['target']] = selected
        return copy.deepcopy(selected)


def admission(state, item, args, root):
    manifest = item['manifest']
    if args.stage != 'gate' and args.gate is not None:
        raise ValueError('The gate argument applies only to the gate stage')
    if args.stage == 'rc':
        if item['rc']:
            raise ValueError('This candidate has an RC deployment')
        reserve(state, manifest['rc_resources'], holder(item, 'rc'))
    elif args.stage == 'gate':
        if not item['rc'] or args.gate not in manifest['gates']:
            raise ValueError('Use a mandatory gate after the RC deployment')
        if args.gate in item['gates']:
            raise ValueError('This gate passed')
        if any(state['resources'].get(key) != holder(item, 'rc') for key in manifest['rc_resources']):
            raise ValueError('The candidate does not hold the RC resources')
    else:
        if not complete(item):
            raise ValueError('Every mandatory gate must pass before production use')
        selection_valid(state, item, args.selection)
        authority(root, manifest, args.authority)
        if args.stage == 'publish':
            if item['publish']:
                raise ValueError('This candidate has a publication')
            reserve(state, manifest['production_resources'] + ['delivery:target:' + manifest['target']], holder(item, 'production'))
        else:
            if not item['publish'] or item['verify']:
                raise ValueError('One completed publication is necessary before verification')
            if any(state['resources'].get(key) != holder(item, 'production') for key in
                   manifest['production_resources'] + ['delivery:target:' + manifest['target']]):
                raise ValueError('The candidate does not hold the production resources')


def accepted(state, item, operation):
    stage = operation['stage']
    if stage == 'gate':
        item['gates'][operation['gate']] = operation['request']
        if complete(item):
            unreserve(state, holder(item, 'rc'))
    else:
        item[stage] = operation['request']
        if stage == 'verify':
            unreserve(state, holder(item, 'production'))


def run(args, root):
    identifier(args.request)
    identity = dict(candidate=args.candidate, stage=args.stage, gate=args.gate,
                    selection=args.selection, authority=args.authority, checkout=str(root))
    with store(root) as (state, directory):
        previous = state['operations'].get(args.request)
        if previous:
            if previous['identity'] != identity:
                raise ValueError('The request identifier belongs to a different operation')
            return copy.deepcopy(previous)
        item = candidate(state, args.candidate, root)
        manifest = copy.deepcopy(item['manifest'])
        before = fingerprints(root, manifest)
        reserve(state, ['delivery:candidate:' + args.candidate], 'delivery:operation:' + args.request)
        admission(state, item, args, root)
        run_directory = directory / 'delivery/runs' / uuid.uuid4().hex
        run_directory.mkdir(parents=True)
        operation = dict(request=args.request, candidate=args.candidate, stage=args.stage, gate=args.gate,
                         target=manifest['target'], identity=identity, status='running', before=before,
                         manifest_sha256=item['manifest_sha256'], directory=str(run_directory),
                         started=time.time(), after=None, returncode=None, receipt=None)
        immutable(run_directory / 'input.json', encode(dict(operation=operation, manifest=manifest)))
        state['operations'][args.request] = operation
    command = manifest['gates'][args.gate] if args.stage == 'gate' else manifest['commands'][args.stage]
    env = dict(os.environ, SDD_CANDIDATE=args.candidate, SDD_STAGE=args.stage, SDD_REQUEST=args.request,
               SDD_GATE=args.gate or '', SDD_GATE_RESULT=str(run_directory / 'receipt.json'),
               SDD_GATE_TESTS=json.dumps(command.get('tests', [])), SDD_MANIFEST=str(run_directory / 'input.json'),
               SDD_TARGET=manifest['target'], SDD_TARGET_REVISION=manifest['target_revision'],
               SDD_ARTIFACTS=json.dumps(manifest['artifacts']))
    error = None
    returncode = None
    receipt = None
    try:
        with (run_directory / 'stdout.log').open('xb') as stdout, (run_directory / 'stderr.log').open('xb') as stderr:
            result = subprocess.run(command['argv'], cwd=root, env=env, stdout=stdout, stderr=stderr,
                                    timeout=command['timeout'], shell=False)
            returncode = result.returncode
        if returncode != 0:
            raise ValueError('The project command returned a failure')
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        error = str(exc)
    try:
        raw_receipt = (run_directory / 'receipt.json').read_bytes()
        immutable(run_directory / 'receipt-observed.json', raw_receipt)
        if not error:
            observed_receipt = strict_json(raw_receipt)
            receipt_valid(observed_receipt, manifest, args.stage, args.gate)
            receipt = observed_receipt
    except (OSError, ValueError) as exc:
        error = (error + '; ' if error else '') + str(exc)
    try:
        after = fingerprints(root, manifest)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        after = None
        error = (error + '; ' if error else '') + str(exc)
    with store(root) as (state, _):
        item = state['candidates'][args.candidate]
        operation = state['operations'][args.request]
        if operation['status'] != 'running':
            immutable(run_directory / ('late-observation-' + uuid.uuid4().hex + '.json'),
                      encode(dict(after=after, returncode=returncode, receipt=receipt, error=error,
                                  observed=time.time())))
            return copy.deepcopy(operation)
        if args.stage in ('publish', 'verify') and not error:
            try:
                selection_valid(state, item, args.selection)
                authority(root, manifest, args.authority)
            except (OSError, ValueError) as exc:
                error = str(exc)
        # A child process can start other writers. After a timeout or failed mutation,
        # project observations are necessary before this entry can release resources.
        status = 'passed' if not error else ('failed' if args.stage == 'gate' and returncode is not None else 'uncertain')
        operation.update(status=status, after=after, returncode=returncode, receipt=receipt,
                         error=error, completed=time.time())
        if status == 'passed':
            accepted(state, item, operation)
            unreserve(state, 'delivery:operation:' + args.request)
        elif status == 'failed':
            item['invalid'] = True
            unreserve(state, 'delivery:operation:' + args.request)
        immutable(run_directory / 'operation.json', encode(operation))
        return copy.deepcopy(operation)


def reconcile(args, root):
    raw = args.evidence.read_bytes()
    evidence = strict_json(raw)
    if not isinstance(evidence, dict) or evidence.get('writer_stopped') is not True or evidence.get('outcome') not in ('passed', 'failed'):
        raise ValueError('Supply actual writer-stop observations and an explicit outcome')
    with store(root) as (state, _):
        operation = state['operations'].get(args.request)
        if not operation or operation['status'] not in ('running', 'uncertain', 'failed'):
            raise ValueError('This operation has no state for reconciliation')
        item = state['candidates'][operation['candidate']]
        if item['checkout'] != str(root):
            raise ValueError('Use the checkout that registered the candidate')
        original = copy.deepcopy(operation)
        manifest = item['manifest']
        if evidence['outcome'] == 'passed':
            if operation['status'] == 'failed' or item['invalid']:
                raise ValueError('After a failed gate, use a new candidate')
            after = fingerprints(root, manifest)
            receipt = evidence.get('receipt')
            receipt_valid(receipt, manifest, operation['stage'], operation['gate'])
            if operation['stage'] in ('publish', 'verify'):
                selection_valid(state, item, operation['identity']['selection'])
                authority(root, manifest, operation['identity']['authority'])
            operation['receipt'] = receipt
            operation['after'] = after
            accepted(state, item, operation)
        else:
            item['invalid'] = True
            unreserve(state, holder(item, 'rc'))
            unreserve(state, holder(item, 'production'))
        observed = time.time()
        record = dict(evidence_sha256=digest(raw), evidence_path=str(args.evidence.resolve()), observed=observed)
        directory = Path(operation['directory'])
        immutable(directory / ('pre-reconcile-' + uuid.uuid4().hex + '.json'), encode(original))
        immutable(directory / ('reconcile-' + uuid.uuid4().hex + '.json'), raw)
        operation['reconciliation'] = record
        operation['status'] = evidence['outcome']
        # This time records the recovery resolution, not an unknown process end.
        operation['resolved_at'] = observed
        operation['completed'] = observed
        operation['completion_source'] = 'reconciliation'
        unreserve(state, 'delivery:operation:' + args.request)
        immutable(directory / ('resolution-' + uuid.uuid4().hex + '.json'), encode(operation))
        return copy.deepcopy(operation)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    actions = parser.add_subparsers(dest='action', required=True)
    registration = actions.add_parser('register')
    registration.add_argument('--manifest', type=Path, required=True)
    execution = actions.add_parser('run')
    execution.add_argument('--candidate', required=True)
    execution.add_argument('--stage', choices=['rc', 'gate', 'publish', 'verify'], required=True)
    execution.add_argument('--gate')
    execution.add_argument('--request', required=True)
    execution.add_argument('--selection', type=int)
    execution.add_argument('--authority')
    selection = actions.add_parser('select')
    selection.add_argument('--candidate', required=True)
    selection.add_argument('--expected', type=int, required=True)
    recovery = actions.add_parser('reconcile')
    recovery.add_argument('--request', required=True)
    recovery.add_argument('--evidence', type=Path, required=True)
    actions.add_parser('inspect')
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if args.action == 'inspect':
            with store(root) as (state, directory):
                result = dict(state=copy.deepcopy(state), directory=str(directory))
        else:
            result = globals()[args.action](args, root)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0 if result.get('status', 'passed') == 'passed' or args.action != 'run' else 2
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(json.dumps(dict(error=str(exc))), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
