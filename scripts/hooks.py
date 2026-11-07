#!/usr/bin/env python3
"""Use optional project hooks. Keep native permissions and release controls."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import uuid

import coordination

STATE = Path('.sdd-harness/hooks')
WRITES = {'write', 'edit', 'write_file', 'edit_file', 'apply_patch'}
EVENTS = ['SessionStart', 'PreToolUse', 'PostToolUse', 'PreCompact', 'Stop',
          'SubagentStart', 'SubagentStop', 'SessionEnd', 'Interrupt']
LIMITS = ['Tool hooks do not include all arbitrary shell writes or host tools.',
          'Local bindings do not prove that unobserved writers stopped.',
          'Check success means process success, not semantic acceptance.',
          'Registration is not evidence of native trust or activation.',
          'Independent controls are necessary for release credentials and irreversible effects.']


def linked(path):
    try:
        info = path.lstat()
        return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)
    except FileNotFoundError:
        return False


def local(root, value):
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = Path(os.path.abspath(path))
    if not path.is_relative_to(root):
        raise ValueError('The path is outside the enabled project')
    for part in [path, *path.parents]:
        if part == root:
            break
        if linked(part):
            raise ValueError('The path contains a link or reparse point')
    return path


def relative(root, value):
    path = local(root, value)
    if path == root / '.git' or (root / '.git') in path.parents:
        raise ValueError('Git metadata is not a task path')
    if path == root / STATE or (root / STATE) in path.parents:
        raise ValueError('Hook state is not a task path')
    return path.relative_to(root).as_posix()


def contains(parent, child):
    return Path(child).is_relative_to(Path(parent))


def atomic(path, data):
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(data, stream, ensure_ascii=True, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def transaction(root):
    directory = local(root, STATE)
    directory.mkdir(parents=True, exist_ok=True)
    local(root, STATE / 'state.json')
    lock = directory / 'state.lock'
    descriptor = None
    for _ in range(100):
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            time.sleep(0.02)
    if descriptor is None:
        raise ValueError('Hook state is busy. Examine the writer before recovery')
    try:
        path = directory / 'state.json'
        state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'bindings': {}}
        if not isinstance(state, dict) or not isinstance(state.get('bindings'), dict):
            raise ValueError('Hook state has an invalid structure')
        yield state, directory
        atomic(path, state)
    finally:
        os.close(descriptor)
        lock.unlink()


def binding(state, session):
    item = state['bindings'].get(session)
    if not item:
        raise ValueError('No active task binding exists for this session')
    return item


def fingerprint(root, paths):
    result = {}
    for value in paths:
        base = local(root, value)
        candidates = [base] if not base.is_dir() else sorted(base.rglob('*'))
        if not base.exists():
            result[value] = None
        for path in candidates:
            if '.git' in path.parts or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path == root / STATE or (root / STATE) in path.parents:
                continue
            local(root, path)
            if path.is_file():
                if len(result) >= 5000:
                    raise ValueError('Select a smaller evidence input scope')
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    for block in iter(lambda: stream.read(65536), b''):
                        digest.update(block)
                result[path.relative_to(root).as_posix()] = digest.hexdigest()
    return result


def bind(args, root):
    if not args.session.strip():
        raise ValueError('A native session identifier is necessary')
    task = relative(root, args.task)
    if not local(root, task).is_file():
        raise ValueError('The task record does not exist')
    scope = sorted(set(relative(root, p) for p in args.scope))
    basis = sorted(set([task, *(relative(root, p) for p in args.basis)]))
    if any(not local(root, p).exists() for p in basis):
        raise ValueError('An evidence input does not exist')
    declaration = {'task': task, 'scope': scope, 'basis': basis,
                   'required_checks': sorted(set(args.required_check))}
    if args.claim or args.executor:
        if not args.claim or not args.executor or args.executor.split(':')[2:3] != [args.session]:
            raise ValueError('The claim executor must identify this native session')
        declaration.update(claim=args.claim, executor=args.executor)
    claim_guard(root, declaration)
    with transaction(root) as (state, _):
        previous = state['bindings'].get(args.session)
        if previous:
            if any(previous[k] != v for k, v in declaration.items()):
                raise ValueError('Keep the active binding. Examine writers before a new binding')
            return {'status': 'already-bound'}
        for other in state['bindings'].values():
            if any(contains(a, b) or contains(b, a) for a in scope for b in other['scope']):
                if not compatible_claim_bindings(root, declaration, other):
                    raise ValueError('The task scope conflicts with another active session')
        state['bindings'][args.session] = dict(declaration, identity=uuid.uuid4().hex,
            status='progress', checks={}, workers={}, continuations=0, events=[])
    return {'status': 'bound', 'session': args.session}


def compatible_claim_bindings(root, new, old):
    if not new.get('claim') or not old.get('claim'):
        return False
    with coordination.store(root) as (state, _):
        current = coordination.get_claim(state, new['claim'], new['executor'], root)
        try:
            previous = coordination.get_claim(state, old['claim'], old['executor'], root, live=False)
        except ValueError:
            return True
        return (current['read_only'] or previous['read_only'] or
                previous['token'] in coordination.parents(state, current['parent']) or
                current['token'] in coordination.parents(state, previous['parent']))


def claim_guard(root, item, targets=None, start=None, completed=False):
    token = item.get('claim')
    if not token:
        if coordination.enabled(root):
            raise ValueError('Bind this session with the current claim for its task')
        return
    with coordination.store(root) as (state, directory):
        claim = coordination.get_claim(state, token, item['executor'], root)
        if (root / item['task']) != Path(claim['task']):
            raise ValueError('The hook task differs from the shared assignment')
        if not all(any(contains(scope, owned) for scope in claim['scope']) for owned in item['scope']):
            raise ValueError('The hook scope is outside the shared assignment')
        if completed:
            if coordination.active_children(state, token):
                raise ValueError('The child execution or result disposition has no resolution')
            if any(run['claim'] == token and run['status'] in ('running', 'unknown')
                   for run in state['claim_runs'].values()):
                raise ValueError('A shared command is active or its outcome is unknown')
        if targets is not None:
            if claim['read_only'] or claim['status'] != 'running':
                raise ValueError('This assignment has no current write authority')
            for other_token, other in state['claims'].items():
                if other_token == token or other['status'] == 'closed' or other['read_only'] or other['checkout'] != str(root):
                    continue
                if other_token in coordination.parents(state, claim['parent']):
                    continue
                if any(contains(scope, target) or contains(target, scope)
                       for scope in other['scope'] for target in targets):
                    raise ValueError('The write scope belongs to a different active assignment')
        if start:
            if claim['read_only'] or claim['status'] != 'running':
                raise ValueError('This assignment cannot execute a write-capable check')
            if coordination.active_children(state, token):
                raise ValueError('Complete child execution before this shared check')
            if any(run['claim'] == token and run['status'] in ('running', 'unknown')
                   for run in state['claim_runs'].values()):
                raise ValueError('The claim has an active or uncertain command')
            state['claim_runs'][start] = dict(id=start, claim=token, generation=claim['generation'],
                status='running', kind='hook-check', started=time.time(), added_resources=[])
            return directory


def end_claim_check(root, item, run_id, outcome, shared_registry):
    if not item.get('claim'):
        return
    with coordination.store(root, bound_registry=shared_registry) as (state, _):
        run = state['claim_runs'].get(run_id)
        if not run or run['claim'] != item['claim'] or run.get('kind') != 'hook-check':
            raise ValueError('The admitted hook check has no matching record')
        observation = dict(outcome=outcome, ended=time.time())
        if run['status'] != 'running':
            run.setdefault('late_observations', []).append(observation)
            return
        run.update(status='unknown' if outcome == 'timeout' else outcome, ended=observation['ended'])


def sync_recovered_checks(root, item, directory, shared_registry=None):
    if not item.get('claim'):
        return
    with coordination.store(root, bound_registry=shared_registry) as (state, _):
        for proof in item['checks'].values():
            run_id = proof.get('run_id')
            shared = state['claim_runs'].get(run_id)
            if proof.get('outcome') == 'recovered' or not shared or shared['claim'] != item['claim']:
                continue
            if shared['status'] == 'resolved':
                previous = copy.deepcopy(proof)
                proof.update(outcome='recovered', stable=False, previous=previous,
                             resolution=shared.get('resolution'))
                atomic(directory / 'checks' / (run_id + '.recovered.json'), proof)


def check(args, root):
    command = args.command
    if not command or command[0] != '--' or len(command) < 2:
        raise ValueError('Put -- before the check command')
    token = uuid.uuid4().hex
    with transaction(root) as (state, directory):
        item = binding(state, args.session)
        sync_recovered_checks(root, item, directory)
        if item['checks'].get(args.name, {}).get('outcome') == 'running':
            raise ValueError('A check with this name is still active')
        current = copy.deepcopy(item)
        before = fingerprint(root, current['basis'])
        logs = local(root, directory / 'checks')
        logs.mkdir(exist_ok=True)
        output, error = logs / (token + '.stdout'), logs / (token + '.stderr')
        shared_registry = claim_guard(root, item, start=token)
        item['checks'][args.name] = {'outcome': 'running', 'run_id': token, 'stable': False,
            'before': before, 'after': {}, 'stdout': str(output), 'stderr': str(error)}
    code, outcome = None, 'unknown'
    try:
        with output.open('xb') as out, error.open('xb') as err:
            process = subprocess.run(command[1:], cwd=root, stdout=out, stderr=err, timeout=args.timeout)
            code = process.returncode
            outcome = 'passed' if code == 0 else 'failed'
    except subprocess.TimeoutExpired:
        outcome = 'timeout'
    except OSError as problem:
        error.write_text(str(problem), encoding='utf-8')
        outcome = 'setup-error'
    after = fingerprint(root, current['basis'])
    record_path = logs / (token + '.json')
    record = {'outcome': outcome, 'run_id': token, 'returncode': code, 'before': before, 'after': after,
              'argv': command[1:], 'binding': current['identity'], 'record': str(record_path),
              'stable': before == after, 'stdout': str(output), 'stderr': str(error),
              'stdout_preview': output.read_bytes()[:2048].decode('utf-8', 'replace'),
              'stderr_preview': error.read_bytes()[:2048].decode('utf-8', 'replace')}
    atomic(record_path, record)
    with transaction(root) as (state, directory):
        item = binding(state, args.session)
        if item['identity'] != current['identity'] or item['checks'].get(args.name, {}).get('run_id') != token:
            raise ValueError('The binding changed during the check. Keep its logs without acceptance')
        sync_recovered_checks(root, item, directory, shared_registry)
        if item['checks'][args.name]['outcome'] != 'recovered':
            item['checks'][args.name] = record
    # Keep the shared run recoverable until local process evidence is durable.
    # Stop still checks shared activity before it can accept this local proof.
    end_claim_check(root, current, token, outcome, shared_registry)
    with transaction(root) as (state, directory):
        item = binding(state, args.session)
        if item['identity'] != current['identity'] or item['checks'].get(args.name, {}).get('run_id') != token:
            raise ValueError('The binding changed during the check. Keep its logs without acceptance')
        sync_recovered_checks(root, item, directory, shared_registry)
        proof = item['checks'][args.name]
        if proof['outcome'] == 'recovered':
            proof.setdefault('late_observations', []).append(dict(record=str(record_path), outcome=outcome,
                                                                 observed=time.time()))
            record = copy.deepcopy(proof)
            outcome = 'recovered'
            code = code if code else 1
    return {'status': outcome, 'check': record}, code if code is not None else 1


def checkpoint(root, item, directory):
    name = item['identity'] + '.checkpoint.json'
    path = local(root, directory / name)
    data = {key: item[key] for key in ('task', 'scope', 'basis', 'status', 'workers')}
    data['checks'] = {key: {'outcome': value['outcome'], 'stable': value['stable'],
                           'stdout': value['stdout'], 'stderr': value['stderr']}
                      for key, value in item['checks'].items()}
    atomic(path, data)
    return str(path)


def deny(reason):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                   'permissionDecisionReason': reason}}


def destructive(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|')
        lexer.whitespace_split = True
        segments, part = [], []
        for token in lexer:
            if token in (';', '&', '&&', '|', '||'):
                segments.append(part)
                part = []
            else:
                part.append(token.lower())
        segments.append(part)
    except ValueError:
        return False
    for words in segments:
        if not words:
            continue
        program = Path(words[0]).name.removesuffix('.exe')
        tail = words[1:]
        if program == 'git':
            if ('reset' in tail and '--hard' in tail or 'clean' in tail or
                'worktree' in tail and 'remove' in tail or
                'push' in tail and any(x in ('--force', '--force-with-lease', '-f', '--tags') for x in tail)):
                return True
        if program in ('rm', 'remove-item') and any(
                w in ('-recurse', '-r', '-rf', '-fr', '--recursive') for w in tail):
            return True
        if program in ('npm', 'pnpm') and 'publish' in tail or program == 'gh' and tail[:2] == ['release', 'create']:
            return True
    return False


def paths_for(event):
    tool = event.get('tool_name', '').lower()
    data = event.get('tool_input', {})
    if not isinstance(data, dict):
        raise ValueError('Tool arguments must be an object')
    if tool == 'apply_patch':
        patch = data.get('patch', data.get('command', ''))
        if not isinstance(patch, str):
            raise ValueError('Patch arguments must contain text')
        return re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', patch, re.M)
    if tool in WRITES:
        return [data.get('file_path', data.get('path', ''))]
    return None


def handle(args, root):
    raw = sys.stdin.buffer.read(1048577)
    if len(raw) > 1048576:
        raise ValueError('The hook input exceeds the input limit')
    event = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(event, dict):
        raise ValueError('The hook input must be an object')
    session, kind = event.get('session_id', ''), event.get('hook_event_name', '')
    if not isinstance(session, str) or not isinstance(kind, str):
        raise ValueError('Hook identifiers must be strings')
    cwd = Path(event.get('cwd', str(root))).resolve()
    if not cwd.is_relative_to(root):
        targets = paths_for(event) if kind == 'PreToolUse' else None
        data = event.get('tool_input', {})
        operation_cwd = Path(data.get('workdir', str(cwd))) if isinstance(data, dict) else cwd
        if not operation_cwd.is_absolute():
            operation_cwd = cwd / operation_cwd
        enters = targets and any(isinstance(value, str) and (operation_cwd / value).resolve().is_relative_to(root)
                                 for value in targets)
        if not enters:
            return {}
    unbound_context = {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext':
                       'Native session: ' + session + '. Project: ' + str(root) +
                       '. No task binding exists for this session. Read the accepted task and bind an independent scope.'}}
    managed = coordination.enabled(root)
    if not (root / STATE / 'state.json').exists():
        if managed and kind == 'PreToolUse' and event.get('tool_name', '').lower() in WRITES:
            return deny('Bind this session with the current claim for its task before writes')
        return unbound_context if kind == 'SessionStart' else {}
    with transaction(root) as (state, directory):
        item = state['bindings'].get(session)
        if state['bindings'] and kind == 'PreToolUse':
            data = event.get('tool_input', {})
            if isinstance(data, dict) and event.get('tool_name', '').lower() in ('bash', 'exec_command', 'shell_command', 'run_shell_command'):
                command = data.get('command', data.get('cmd', ''))
                if isinstance(command, str) and destructive(command):
                    return deny('Use the project release or recovery entry with its required controls')
        if not item:
            if (state['bindings'] or managed) and kind == 'PreToolUse' and event.get('tool_name', '').lower() in WRITES:
                return deny('Bind this session to an independent scope before writes')
            return unbound_context if kind == 'SessionStart' else {}
        if kind == 'PreToolUse':
            tool_input = event.get('tool_input', {})
            if not isinstance(tool_input, dict):
                return deny('Tool arguments must be an object')
            if event.get('tool_name', '').lower() in ('bash', 'exec_command', 'shell_command', 'run_shell_command'):
                command = tool_input.get('command', tool_input.get('cmd', ''))
                if isinstance(command, str) and destructive(command):
                    return deny('Use the project release or recovery entry with its required controls')
            try:
                claim_guard(root, item)
                if item.get('executor') and item['executor'].split(':')[0] != args.host:
                    return deny('The hook host does not match the shared executor identity')
                paths = paths_for(event)
                if paths is not None:
                    if not paths or not all(isinstance(p, str) and p for p in paths):
                        return deny('The write target is not available for inspection')
                    operation_cwd = Path(tool_input.get('workdir', str(cwd))).resolve()
                    for value in paths:
                        target = relative(root, operation_cwd / value)
                        if not any(contains(scope, target) for scope in item['scope']):
                            return deny('The write target is outside this task scope')
                        claim_guard(root, item, targets=[target])
            except (OSError, ValueError, sqlite3.Error) as problem:
                return deny(str(problem))
        elif kind in ('SubagentStart', 'SubagentStop'):
            worker = event.get('agent_id')
            if isinstance(worker, str) and worker:
                previous = item['workers'].get(worker)
                if kind == 'SubagentStart':
                    item['workers'][worker] = 'running'
                elif previous not in ('accepted', 'rejected'):
                    item['workers'][worker] = 'returned'
        elif kind == 'Stop' and item['status'] == 'completed':
            sync_recovered_checks(root, item, directory)
            errors = []
            try:
                claim_guard(root, item, completed=True)
            except (OSError, ValueError, sqlite3.Error) as problem:
                errors.append(str(problem))
            current = fingerprint(root, item['basis'])
            for name in item['required_checks']:
                proof = item['checks'].get(name)
                if not proof or proof['outcome'] != 'passed' or not proof['stable'] or proof['after'] != current:
                    errors.append('Check evidence is missing, failed, or stale: ' + name)
            if any(proof.get('outcome') == 'running' for proof in item['checks'].values()):
                errors.append('A check is still active')
            if any(value in ('running', 'returned') for value in item['workers'].values()):
                errors.append('A worker has status running or returned. Complete main-agent disposition after return')
            if errors:
                reason = '. '.join(errors)
                if item['continuations'] < 2:
                    item['continuations'] += 1
                    return {'decision': 'block', 'reason': reason}
                item['status'] = 'blocked'
                return {'systemMessage': reason + '. Acceptance stays blocked. No more automatic continuation.'}
            item['continuations'] = 0
        item['events'] = (item['events'] + [{'event': kind, 'tool': str(event.get('tool_name', ''))[:128]}])[-12:]
        path = checkpoint(root, item, directory)
        if kind == 'SessionStart':
            return {'hookSpecificOutput': {'hookEventName': kind, 'additionalContext':
                    'Task state: ' + path + '. Task record: ' + str(root / item['task']) +
                    '. Examine source state and evidence applicability before completion.'}}
    return {}


def configurations(root, host):
    script = str(Path(__file__).resolve()).replace('\\', '/')
    arguments = [sys.executable.replace('\\', '/'), script, 'handle', '--repo', str(root).replace('\\', '/'), '--host', host]
    selected = EVENTS if host == 'codex' else ['SessionStart', 'PreToolUse', 'PostToolUse', 'Stop']
    groups = {}
    for event in selected:
        if host == 'zcode':
            handler = {'type': 'process', 'command': arguments[0], 'args': arguments[1:], 'timeoutMs': 5000}
        else:
            if os.name == 'nt':
                invocation = '& ' + ' '.join("'" + value.replace("'", "''") + "'" for value in arguments)
                encoded = base64.b64encode(invocation.encode('utf-16le')).decode('ascii')
                command = 'powershell.exe -NoProfile -NonInteractive -EncodedCommand ' + encoded
            else:
                command = shlex.join(arguments)
            handler = {'type': 'command', 'command': command,
                       'timeout': 3 if event in ('SessionEnd', 'Interrupt') else 5,
                       'statusMessage': 'SDD hook: ' + script}
        groups[event] = [{'hooks': [handler]}]
    return groups


def configure(args, root):
    destination = Path(args.output or args.merge).absolute()
    if linked(destination) or not destination.parent.is_dir():
        raise ValueError('The configuration target must have a regular parent directory')
    for parent in destination.parents:
        if linked(parent):
            raise ValueError('The configuration parent contains a link')
    original = destination.read_bytes() if args.merge else None
    if args.output and destination.exists():
        raise ValueError('Use an unused configuration output path')
    document = json.loads(original.decode('utf-8-sig')) if original is not None else {}
    hooks = document.setdefault('hooks', {})
    events = hooks
    if args.host == 'zcode':
        hooks['enabled'] = True
        events = hooks.setdefault('events', {})
    for event, groups in configurations(root, args.host).items():
        existing = events.setdefault(event, [])
        if not isinstance(existing, list):
            raise ValueError('The existing hook event is not an array')
        for group in groups:
            if group not in existing:
                existing.append(group)
    updated = (json.dumps(document, ensure_ascii=True, indent=2) + '\n').encode('utf-8')
    backup = None
    if original is not None:
        if original == updated:
            return {'status': 'already-configured'}
        backup = destination.with_name(destination.name + '.' + uuid.uuid4().hex + '.bak')
        with backup.open('xb') as stream:
            stream.write(original)
        atomic(destination, document)
    else:
        with destination.open('xb') as stream:
            stream.write(updated)
    return {'status': 'configured', 'backup': str(backup) if backup else None,
            'activation': 'Unverified. Examine native trust and do a test in a fresh session.', 'limits': LIMITS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('bind', 'check', 'status', 'worker', 'release', 'handle', 'configure', 'inspect'):
        command = commands.add_parser(name)
        command.add_argument('--repo', type=Path, required=True)
        if name in ('bind', 'check', 'status', 'worker', 'release'):
            command.add_argument('--session', required=True)
        if name == 'bind':
            command.add_argument('--task', required=True)
            command.add_argument('--scope', action='append', required=True)
            command.add_argument('--basis', action='append', required=True)
            command.add_argument('--required-check', action='append', default=[])
            command.add_argument('--claim')
            command.add_argument('--executor')
        if name == 'check':
            command.add_argument('--name', required=True)
            command.add_argument('--timeout', type=float, default=600)
            command.add_argument('command', nargs=argparse.REMAINDER)
        if name in ('status', 'worker'):
            values = ['progress', 'completed', 'partial', 'blocked', 'paused'] if name == 'status' else ['running', 'returned', 'accepted', 'rejected']
            command.add_argument('--value', choices=values, required=True)
        if name == 'worker':
            command.add_argument('--id', required=True)
        if name in ('configure', 'handle'):
            command.add_argument('--host', choices=['codex', 'zcode'], required=True)
        if name == 'configure':
            target = command.add_mutually_exclusive_group(required=True)
            target.add_argument('--output')
            target.add_argument('--merge')
    args = parser.parse_args()
    code = 0
    try:
        root = args.repo.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('The project root must be a directory')
        if args.action == 'bind':
            result = bind(args, root)
        elif args.action == 'check':
            result, code = check(args, root)
        elif args.action == 'handle':
            result = handle(args, root)
        elif args.action == 'configure':
            result = configure(args, root)
        else:
            with transaction(root) as (state, directory):
                if args.action == 'inspect':
                    result = dict(state, limits=LIMITS)
                else:
                    item = binding(state, args.session)
                    sync_recovered_checks(root, item, directory)
                    if args.action == 'status':
                        item['status'] = args.value
                    elif args.action == 'worker':
                        if args.value in ('accepted', 'rejected') and item['workers'].get(args.id) != 'returned':
                            raise ValueError('A worker must return before disposition')
                        item['workers'][args.id] = args.value
                    elif args.action == 'release':
                        if any(proof.get('outcome') == 'running' for proof in item['checks'].values()):
                            raise ValueError('Keep the binding until active checks stop')
                        if any(v in ('running', 'returned') for v in item['workers'].values()):
                            raise ValueError('Keep the binding until worker execution and disposition have resolution')
                        del state['bindings'][args.session]
                    result = {'status': args.action, 'checkpoint': checkpoint(root, item, directory)}
        print(json.dumps(result, ensure_ascii=True))
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error, subprocess.SubprocessError) as problem:
        print(json.dumps({'error': str(problem), 'control': 'Degraded. Do not claim enforcement.'}), file=sys.stderr)
        return 1
    return code


if __name__ == '__main__':
    raise SystemExit(main())
