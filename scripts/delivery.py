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
import stat
import subprocess
import sys
import time
import uuid

from coordination import inspect_state, regular_path, reserve, store, unreserve
import gate_reports


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
    if not path.is_relative_to(root):
        raise ValueError('The input is not a file inside the project')
    current = root
    for component in path.relative_to(root).parts:
        current = current / component
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('The input path contains a link or reparse point')
    try:
        resolved = path.resolve(strict=True)
    except RuntimeError as exc:
        raise ValueError('The input path has no resolution') from exc
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('The input is not a file inside the project')
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
    if not isinstance(manifest, dict) or type(manifest.get('format')) is not int or manifest['format'] not in (1, 2):
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
        if manifest['format'] == 2:
            gate_reports.validate_cases(gate)
            if any(case['file'] not in manifest['basis'] for case in gate['junit'].values()):
                raise ValueError('Every mandatory JUnit test file must be a frozen basis input')
        elif 'junit' in gate:
            raise ValueError('JUnit evidence requires a format 2 candidate')
    if manifest.get('authority') not in manifest['basis']:
        raise ValueError('The authority file must be a frozen basis input')
    fingerprints(root, manifest)


def candidate(state, name, root):
    item = state['candidates'].get(name)
    if item is None:
        raise ValueError('The candidate is not registered')
    if item['checkout'] != str(root):
        raise ValueError('Use the checkout that registered the candidate')
    if item.get('retirement'):
        raise ValueError('The candidate is retired. Register a new candidate')
    if item.get('invalid'):
        raise ValueError('The candidate has failed evidence. Register a new candidate')
    return item


def holder(item, kind):
    return 'delivery:' + kind + ':' + item['manifest']['candidate']


def complete(item):
    return item.get('rc') and set(item.get('gates', {})) == set(item['manifest']['gates'])


def require_gate_reports(state, item):
    if item['manifest']['format'] != 2:
        return
    for name, request in item['gates'].items():
        op = state['operations'][request]
        report_hashes = op.get('gate_reports', {})
        if (op['status'] != 'passed' or op.get('stage') != 'gate' or op.get('gate') != name or
                op.get('candidate') != item['manifest']['candidate'] or
                op.get('manifest_sha256') != item['manifest_sha256'] or
                set(report_hashes) != set(gate_reports.shards(item['manifest']['gates'][name]))):
            raise ValueError('This strict gate has no applicable report evidence')
        directory = regular_path(op['directory'])
        for shard, expected in report_hashes.items():
            path = local_file(directory, 'reports-observed/' + shard + '.xml')
            if digest(gate_reports.read_report(path)) != expected:
                raise ValueError('A retained JUnit report changed')


def observe_gate_reports(directory, gate, retained='reports-observed'):
    directory = regular_path(directory)
    reports = {}
    errors = []
    for shard in gate_reports.shards(gate):
        name = shard + '.xml'
        try:
            report = gate_reports.read_report(local_file(directory, 'reports/' + name))
            kept = regular_path(directory / retained / name)
            immutable(kept, report)
            reports[shard] = digest(report)
            gate_reports.check_report(report, directory.name, shard, gate['junit'])
        except (OSError, ValueError) as exc:
            errors.append(f'{shard}: {exc}')
    return reports, errors


def registration_id(item):
    return Path(item['manifest_path']).stem


def legacy_verification(state, item, stage):
    published = state['operations'].get(item['publish'])
    return stage == 'verify' and published and 'registration_id' not in published['identity']


def authority(root, manifest, supplied, *, legacy=False):
    if supplied != manifest['authority']:
        raise ValueError('Supply the project authority file that you froze')
    record = strict_json(local_file(root, supplied).read_bytes())
    expected = dict(authorized=True, candidate=manifest['candidate'], target=manifest['target'],
                    target_revision=manifest['target_revision'])
    if not legacy:
        expected['artifacts'] = manifest['artifacts']
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
    with store(root, initialize=True) as (state, directory):
        if manifest['format'] == 2 and state['format'] == 1:
            if (state['resources'] or any(c['status'] != 'closed' for c in state['claims'].values()) or
                    any(r['status'] in ('running', 'unknown') for r in state['claim_runs'].values()) or
                    any(op['status'] in ('running', 'uncertain') for op in state['operations'].values())):
                raise ValueError('Resolve active claims, operations, and resource holders before a registry upgrade')
            state['format'] = 2
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
        require_gate_reports(state, item)
        if unresolved_production(state, manifest['target']):
            raise ValueError('The production outcome has no resolution')
        previous = state['selections'].get(manifest['target'], {})
        if previous.get('generation', 0) != args.expected:
            raise ValueError('The expected selection generation is stale')
        selected = dict(candidate=args.candidate, generation=args.expected + 1,
                        target_revision=manifest['target_revision'])
        state['selections'][manifest['target']] = selected
        return copy.deepcopy(selected)


def unresolved_production(state, target):
    return [op for op in state['operations'].values()
            if op['stage'] in ('publish', 'verify') and op['target'] == target and
            op['status'] in ('running', 'uncertain', 'passed') and
            not any(state['candidates'][op['candidate']].get(key) for key in ('verify', 'invalid', 'retirement'))]


def admission(state, item, args, root):
    manifest = item['manifest']
    if args.stage != 'gate' and args.gate is not None:
        raise ValueError('The gate argument applies only to the gate stage')
    if args.stage in ('publish', 'verify'):
        if args.registration_id != registration_id(item):
            raise ValueError('Supply the registration ID for this candidate')
    elif args.registration_id is not None:
        raise ValueError('The registration ID argument applies only to production stages')
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
        require_gate_reports(state, item)
        selection_valid(state, item, args.selection)
        authority(root, manifest, args.authority, legacy=legacy_verification(state, item, args.stage))
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
    if args.registration_id is not None:
        identity['registration_id'] = args.registration_id
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
        strict_gate = manifest['format'] == 2 and args.stage == 'gate'
        if strict_gate:
            (run_directory / 'reports').mkdir()
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
    for key in ('SDD_GATE_RUN_ID', 'SDD_GATE_REPORT_DIR'):
        env.pop(key, None)
    if strict_gate:
        env.update(SDD_GATE_RUN_ID=run_directory.name, SDD_GATE_REPORT_DIR=str(run_directory / 'reports'))
    error = None
    returncode = None
    receipt = None
    reports = None
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
    if strict_gate:
        try:
            reports, report_errors = observe_gate_reports(run_directory, command)
            if report_errors:
                error = '; '.join(([error] if error else []) + report_errors)
        except (OSError, ValueError) as exc:
            error = (error + '; ' if error else '') + str(exc)
    try:
        after = fingerprints(root, manifest)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        after = None
        error = (error + '; ' if error else '') + str(exc)
    with store(root, bound_registry=directory) as (state, _):
        operation = state['operations'].get(args.request)
        if (not operation or operation['identity'] != identity
                or operation['directory'] != str(run_directory)):
            raise ValueError('The admitted delivery operation has no matching record')
        item = state['candidates'][args.candidate]
        if operation['status'] != 'running':
            immutable(run_directory / ('late-observation-' + uuid.uuid4().hex + '.json'),
                      encode(dict(after=after, returncode=returncode, receipt=receipt, error=error,
                                  gate_reports=reports, observed=time.time())))
            return copy.deepcopy(operation)
        if args.stage in ('publish', 'verify') and not error:
            try:
                selection_valid(state, item, args.selection)
                authority(root, manifest, args.authority, legacy=legacy_verification(state, item, args.stage))
            except (OSError, ValueError) as exc:
                error = str(exc)
        # A child process can start other writers. After a timeout or failed mutation,
        # project observations are necessary before this entry can release resources.
        status = 'passed' if not error else ('failed' if args.stage == 'gate' and returncode is not None else 'uncertain')
        operation.update(status=status, after=after, returncode=returncode, receipt=receipt,
                         error=error, completed=time.time())
        if strict_gate:
            operation['gate_reports'] = reports
            gates = {**item['gates'], args.gate: args.request}
            if status == 'passed' and set(gates) == set(manifest['gates']):
                try:
                    require_gate_reports(state, {**item, 'gates': gates})
                except (OSError, ValueError) as exc:
                    status = 'failed'
                    operation.update(status=status, error='Cannot verify retained gate evidence: ' + str(exc))
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
    evidence_sha = digest(raw)
    with store(root) as (state, _):
        operation = state['operations'].get(args.request)
        if not operation:
            raise ValueError('This operation has no state for reconciliation')
        item = state['candidates'][operation['candidate']]
        if item['checkout'] != str(root):
            raise ValueError('Use the checkout that registered the candidate')
        previous = operation.get('reconciliation')
        if previous:
            if previous['evidence_sha256'] != evidence_sha:
                raise ValueError('The operation has different reconciliation evidence')
            return copy.deepcopy(operation)
        if not isinstance(evidence, dict) or evidence.get('operation_id') != Path(operation['directory']).name:
            raise ValueError('Use the operation ID for this admitted execution in the reconciliation evidence')
        if operation['status'] not in ('running', 'uncertain', 'failed'):
            raise ValueError('This operation has no state for reconciliation')
        if item.get('retirement'):
            raise ValueError('The candidate is retired. Keep its recorded operations')
        if (evidence.get('writer_stopped') is not True
                or evidence.get('outcome') not in ('passed', 'failed')
                or not isinstance(evidence.get('observations'), str) or not evidence['observations'].strip()):
            raise ValueError('Supply writer_stopped=true, an explicit outcome, and nonempty observations')
        original = copy.deepcopy(operation)
        manifest = item['manifest']
        if evidence['outcome'] == 'passed':
            if operation['status'] == 'failed' or item['invalid']:
                raise ValueError('After a failed gate, use a new candidate')
            if manifest['format'] == 2 and operation['stage'] == 'gate':
                raise ValueError('An interrupted strict gate cannot reconcile as passed')
            after = fingerprints(root, manifest)
            receipt = evidence.get('receipt')
            receipt_valid(receipt, manifest, operation['stage'], operation['gate'])
            if operation['stage'] in ('publish', 'verify'):
                selection_valid(state, item, operation['identity']['selection'])
                legacy = ('registration_id' not in operation['identity']
                          or legacy_verification(state, item, operation['stage']))
                authority(root, manifest, operation['identity']['authority'], legacy=legacy)
            operation['receipt'] = receipt
            operation['after'] = after
            accepted(state, item, operation)
        else:
            if manifest['format'] == 2 and operation['stage'] == 'gate':
                retained = 'recovery-reports-' + uuid.uuid4().hex
                directory = Path(operation['directory'])
                try:
                    reports, errors = observe_gate_reports(directory, manifest['gates'][operation['gate']], retained)
                except (OSError, ValueError) as exc:
                    reports, errors = {}, [str(exc)]
                operation.setdefault('recovery_gate_reports', []).append(dict(
                    directory=str(directory / retained), reports=reports, errors=errors))
            item['invalid'] = True
            unreserve(state, holder(item, 'rc'))
            unreserve(state, holder(item, 'production'))
        observed = time.time()
        record = dict(evidence_sha256=evidence_sha, evidence_path=str(args.evidence.resolve()), observed=observed)
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


def retire(args, root):
    raw = args.evidence.read_bytes()
    evidence = strict_json(raw)
    with store(root) as (state, directory):
        item = state['candidates'].get(args.candidate)
        if not item or item['checkout'] != str(root):
            raise ValueError('Use the checkout that registered the candidate')
        previous = item.get('retirement')
        if previous:
            if previous['evidence_sha256'] != digest(raw):
                raise ValueError('The candidate has different retirement evidence')
            return copy.deepcopy(previous)
        manifest = item['manifest']
        expected = dict(candidate=args.candidate, target=manifest['target'],
                        manifest_sha256=item['manifest_sha256'],
                        registration_id=registration_id(item))
        if not isinstance(evidence, dict) or evidence.get('format') != 1 or any(
                evidence.get(key) != value for key, value in expected.items()):
            raise ValueError('Retirement evidence must identify the fixed candidate, target, and registration')
        if evidence.get('writer_stopped') is not True or any(
                not isinstance(evidence.get(field), str) or not evidence[field].strip()
                for field in ('writer_observations', 'reason')):
            raise ValueError('Supply actual stopped-writer observations and a retirement reason')
        outcome = evidence.get('external_outcome')
        if not isinstance(outcome, dict) or outcome.get('status') not in (
                'unchanged', 'published', 'removed', 'restored') or any(
                not isinstance(outcome.get(field), str) or not outcome[field].strip()
                for field in ('target_revision', 'observations')):
            raise ValueError('Supply a known external outcome and actual target observations')
        if ((outcome['status'] == 'published' and outcome['target_revision'] != args.candidate) or
                (outcome['status'] == 'unchanged' and outcome['target_revision'] != manifest['target_revision'])):
            raise ValueError('The observed target revision differs from the stated external outcome')
        operations = [op for op in state['operations'].values() if op['candidate'] == args.candidate]
        if any(op['status'] not in ('passed', 'failed') for op in operations):
            raise ValueError('Resolve every running or uncertain operation before retirement')
        # Withdrawal uses current project authority. The frozen publication basis
        # can be obsolete. These assertions do not prove provenance or process exit.
        authority_path = local_file(root, evidence.get('authority'))
        raw_authority = authority_path.read_bytes()
        record = strict_json(raw_authority)
        if not isinstance(record, dict) or record.get('authorized') is not True or record.get('action') != 'retire' or any(
                record.get(key) != value for key, value in expected.items()):
            raise ValueError('Current project authority must authorize this candidate retirement')
        record_directory = directory / 'delivery/retirements' / uuid.uuid4().hex
        retirement = dict(**expected, evidence_sha256=digest(raw), evidence_path=str(args.evidence.resolve()),
                          authority_sha256=digest(raw_authority), authority_path=str(authority_path),
                          directory=str(record_directory), observed=time.time(),
                          external_outcome=copy.deepcopy(outcome), reason=evidence['reason'])
        immutable(record_directory / 'evidence.json', raw)
        immutable(record_directory / 'authority.json', raw_authority)
        immutable(record_directory / 'retirement.json', encode(retirement))
        item['retirement'] = retirement
        owned_slots = [(key, holder(item, 'rc')) for key in manifest['rc_resources']]
        owned_slots.extend((key, holder(item, 'production')) for key in
                           manifest['production_resources'] + ['delivery:target:' + manifest['target']])
        owned_slots.extend(('delivery:candidate:' + args.candidate, 'delivery:operation:' + op['request'])
                           for op in operations)
        for key, owner in owned_slots:
            if state['resources'].get(key) == owner:
                del state['resources'][key]
        return copy.deepcopy(retirement)


def operation_ref(op):
    result = {key: op.get(key) for key in ('request', 'candidate', 'stage', 'gate', 'status',
                                          'directory', 'gate_reports', 'recovery_gate_reports')}
    result['operation_id'] = Path(op['directory']).name
    return result


def inspect_candidate(state, root, name):
    summary = dict(format=1, candidate=name, observed_checkout=str(root), status='missing',
                   next_action='locate_candidate')
    item = state['candidates'].get(name)
    if item is None:
        return summary
    manifest = item['manifest']
    keys = set(manifest['rc_resources'] + manifest['production_resources'] +
               ['delivery:target:' + manifest['target'], 'delivery:candidate:' + name])
    resources = {key: owner for key, owner in state['resources'].items() if key in keys}
    operations = [op for op in state['operations'].values() if op['candidate'] == name]
    pending = [op for op in operations if op['status'] in ('running', 'uncertain')]
    other = [op for op in unresolved_production(state, manifest['target']) if op['candidate'] != name]
    selected = state['selections'].get(manifest['target'])
    missing = sorted(set(manifest['gates']) - set(item['gates']))
    summary.update(checkout=item['checkout'], target=manifest['target'], resources=resources,
                   selection=selected, operations=[operation_ref(op) for op in operations],
                   pending_gates=missing, manifest_sha256=item['manifest_sha256'], manifest_path=item['manifest_path'],
                   registration_id=registration_id(item),
                   retirement_directory=(item.get('retirement') or {}).get('directory'),
                   target_blockers=[operation_ref(op) for op in other],
                   status='retired' if item.get('retirement') else 'invalid' if item['invalid'] else
                   'verified' if item['verify'] else 'published' if item['publish'] else
                   'gated' if complete(item) else 'rc' if item['rc'] else 'registered')
    if item['checkout'] != str(root):
        summary['next_action'] = 'locate_candidate_checkout'
    elif pending:
        summary['next_action'] = 'inspect_writers_and_effects'
    elif item.get('retirement') or item['verify']:
        summary['next_action'] = 'read_completed_record'
    elif item['invalid']:
        summary['next_action'] = 'review_failed_candidate'
    else:
        try:
            fingerprints(root, manifest)
            require_gate_reports(state, item)
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            summary.update(next_action='examine_candidate_evidence', reason=str(exc))
            return summary
        rc = manifest['rc_resources']
        prod = manifest['production_resources'] + ['delivery:target:' + manifest['target']]
        if 'delivery:candidate:' + name in resources:
            summary['next_action'] = 'inspect_shared_resources'
        elif not item['rc']:
            summary['next_action'] = ('inspect_shared_resources' if any(key in resources for key in rc)
                                      else 'check_rc_prerequisites')
        elif missing:
            summary['next_action'] = ('inspect_shared_resources' if any(resources.get(key) != holder(item, 'rc') for key in rc)
                                      else 'review_pending_gates')
        elif other or any(resources.get(key, holder(item, 'production')) != holder(item, 'production') for key in prod):
            summary['next_action'] = 'inspect_target_and_writers'
        elif item['publish']:
            summary['next_action'] = ('inspect_shared_resources' if any(
                resources.get(key) != holder(item, 'production') for key in prod)
                else 'check_verification_prerequisites')
        elif not selected or selected['candidate'] != name:
            summary['next_action'] = 'check_selection_prerequisites'
        else:
            summary['next_action'] = 'check_publication_authority'
    return summary


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
    execution.add_argument('--registration-id')
    execution.add_argument('--authority')
    selection = actions.add_parser('select')
    selection.add_argument('--candidate', required=True)
    selection.add_argument('--expected', type=int, required=True)
    recovery = actions.add_parser('reconcile')
    recovery.add_argument('--request', required=True)
    recovery.add_argument('--evidence', type=Path, required=True)
    retirement = actions.add_parser('retire')
    retirement.add_argument('--candidate', required=True)
    retirement.add_argument('--evidence', type=Path, required=True)
    inspection = actions.add_parser('inspect')
    inspection.add_argument('--candidate')
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if args.action == 'inspect':
            state, directory = inspect_state(root)
            result = (inspect_candidate(state, root, args.candidate) if args.candidate is not None
                      else dict(state=state, directory=str(directory)))
        else:
            result = globals()[args.action](args, root)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0 if result.get('status', 'passed') == 'passed' or args.action != 'run' else 2
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(json.dumps(dict(error=str(exc))), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
