#!/usr/bin/env python3
"""Keep task execution ownership in a shared local registry."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import time
import uuid


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regular_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('The path contains a link or reparse point')
    return path


def project_path(root, value):
    path = regular_path(root / value)
    if not path.is_relative_to(root):
        raise ValueError('The task path is outside the checkout')
    relative = path.relative_to(root)
    if relative.parts and relative.parts[0] in ('.git', '.sdd-harness'):
        raise ValueError('Control metadata is not a task scope')
    return path


def checkout_origin(root):
    root = regular_path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('The checkout origin must be a directory')
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                capture_output=True, encoding='utf-8', timeout=3)
    except FileNotFoundError:
        result = None
    if result is not None and result.returncode == 0:
        origin = regular_path(Path(result.stdout.rstrip('\r\n'))).resolve(strict=True)
        if not root.is_relative_to(origin):
            raise ValueError('The project root is outside the checkout origin')
        return origin
    if any((part / '.git').exists() for part in (root, *root.parents)):
        raise ValueError('The Git checkout origin cannot be verified')
    return root


def registry(root):
    configuration = regular_path(root / '.sdd-harness/coordination.json')
    if configuration.exists():
        value = json.loads(configuration.read_text(encoding='utf-8'))
        target = Path(value['registry'])
        if not target.is_absolute():
            raise ValueError('The shared registry path must be absolute')
        return regular_path(target)
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--git-common-dir'],
                                capture_output=True, encoding='utf-8', timeout=3)
    except FileNotFoundError:
        if (root / '.git').exists():
            raise ValueError('Git is necessary to resolve the shared repository registry')
        return regular_path(root / '.sdd-harness/coordination')
    if result.returncode == 0:
        common = Path(result.stdout.rstrip('\r\n'))
        if not common.is_absolute():
            common = root / common
        return regular_path(common.resolve() / 'sdd-harness-coordination')
    if (root / '.git').exists():
        raise ValueError('The repository registry has no resolution. Examine Git metadata')
    return regular_path(root / '.sdd-harness/coordination')


def enabled(root):
    return (registry(root) / 'state.sqlite').exists()


def empty_state():
    return dict(format=1, generation=0, claims={}, tasks={}, resources={}, candidates={},
                selections={}, operations={}, claim_runs={})


def inspect_state(root):
    directory = registry(root)
    database = regular_path(directory / 'state.sqlite')
    if not database.exists():
        return empty_state(), directory
    # WAL reads can create sidecars even with mode=ro. The helper uses rollback journals.
    with database.open('rb') as stream:
        header = stream.read(20)
    if header.startswith(b'SQLite format 3\x00') and 2 in header[18:20]:
        raise ValueError('Read-only inspection does not support a registry in WAL mode')
    for suffix in ('-journal', '-wal', '-shm'):
        regular_path(Path(str(database) + suffix))
    connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True, timeout=2)
    try:
        row = connection.execute('SELECT body FROM registry WHERE id=1').fetchone()
        state = json.loads(row[0]) if row else empty_state()
        if state.get('format') not in (1, 2):
            raise ValueError('The registry format is not supported')
        return state, directory
    finally:
        connection.close()


@contextmanager
def store(root):
    directory = registry(root)
    directory.mkdir(parents=True, exist_ok=True)
    database = regular_path(directory / 'state.sqlite')
    for suffix in ('-journal', '-wal', '-shm'):
        regular_path(Path(str(database) + suffix))
    connection = sqlite3.connect(database, timeout=2, isolation_level=None)
    try:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS registry (id INTEGER PRIMARY KEY, body TEXT NOT NULL)')
        row = connection.execute('SELECT body FROM registry WHERE id=1').fetchone()
        state = json.loads(row[0]) if row else empty_state()
        if state.get('format') not in (1, 2):
            raise ValueError('The registry format is not supported')
        yield state, directory
        body = json.dumps(state)
        if not row or body != row[0]:
            connection.execute('INSERT OR REPLACE INTO registry VALUES (1, ?)', (body,))
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def reserve(state, keys, holder):
    keys = sorted(set(keys))
    if any(not isinstance(key, str) or not key.strip() or len(key) > 200 for key in keys):
        raise ValueError('A resource key must be a short nonempty string')
    if any(state['resources'].get(key, holder) != holder for key in keys):
        raise ValueError('A shared resource has a different owner')
    state['resources'].update({key: holder for key in keys})


def unreserve(state, holder):
    for key in list(state['resources']):
        if state['resources'][key] == holder:
            del state['resources'][key]


def executor_identity(value):
    if len(value) > 300 or len(value.split(':')) < 3 or any(not p.strip() for p in value.split(':')):
        raise ValueError('Use host:instance:session and an optional worker for the executor')
    return value


def interval(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError('The lease interval must be finite and nonnegative')
    return time.time() + value if value else None


def get_claim(state, token, executor=None, root=None, live=True):
    item = state['claims'].get(token)
    if not item or state['tasks'].get(item['task_id']) != token or item['status'] == 'closed':
        raise ValueError('The claim is absent, closed, or superseded')
    if executor is not None and item['executor'] != executor:
        raise ValueError('The executor does not own this claim')
    if root is not None and Path(item['checkout']) != root:
        raise ValueError('The claim belongs to a different checkout')
    if live:
        if item['expires'] is not None and item['expires'] <= time.time():
            raise ValueError('The claim is suspect. Examine writers before recovery')
        current_basis(state, item)
        if item['parent']:
            get_claim(state, item['parent'], live=True)
    return item


def evidence_path(item, kind):
    source = item['task'] if kind == 'task' else item['result']['path']
    origin = item.get('checkout_origin')
    if origin is None:
        if regular_path(Path(item['checkout'])).exists():
            return regular_path(Path(source))
        raise ValueError('The removed project has no verified checkout origin')
    if regular_path(Path(origin)).exists():
        return regular_path(Path(source))
    accepted = item['status'] == 'closed' and item['disposition'] == 'accepted'
    kept = item.get('preserved') if accepted else None
    if kind == 'task' and not kept:
        kept = item.get('basis_preserved')
    if not kept or kept.get('format') != 1 or kept.get('token') != item['token']:
        raise ValueError('The removed checkout has no kept evidence for this basis')
    expected = item['revision'] if kind == 'task' else item['result']['sha256']
    entry = kept[kind]
    if entry['source'] != source or entry['sha256'] != expected:
        raise ValueError('The kept evidence has a different source or hash')
    return regular_path(Path(entry['path']))


def current_basis(state, item, visiting=None):
    visiting = set() if visiting is None else set(visiting)
    if item['task_id'] in visiting:
        raise ValueError('The task basis has a cycle')
    visiting.add(item['task_id'])
    if digest(evidence_path(item, 'task')) != item['revision']:
        raise ValueError('The accepted task revision changed')
    for dependency, basis in item.get('dependency_basis', {}).items():
        previous = state['claims'].get(state['tasks'].get(dependency))
        if (not previous or previous['token'] != basis['token'] or previous['status'] != 'closed'
                or previous['disposition'] != 'accepted'):
            raise ValueError('A dependency assignment changed')
        if previous['revision'] != basis['revision'] or not previous['result']:
            raise ValueError('A dependency revision changed')
        current_basis(state, previous, visiting)
        if (previous['result']['sha256'] != basis['result_sha256']
                or digest(evidence_path(previous, 'result')) != basis['result_sha256']):
            raise ValueError('A dependency result changed')
    if item['parent']:
        current_basis(state, state['claims'][item['parent']], visiting)


def preserve_evidence(state, directory, item):
    current_basis(state, item)
    seen = set()

    def keep(node, with_result):
        key = (node['token'], with_result)
        if key in seen:
            return
        seen.add(key)
        if regular_path(Path(node['checkout'])).exists():
            origin = str(checkout_origin(Path(node['checkout'])))
            if node.get('checkout_origin', origin) != origin:
                raise ValueError('The verified checkout origin changed')
            node['checkout_origin'] = origin
        elif not node.get('checkout_origin'):
            raise ValueError('Preserve the checkout origin before cleanup')
        field, folder = ('preserved', 'accepted') if with_result else ('basis_preserved', 'basis')
        kept = dict(format=1, token=node['token'])
        target = regular_path(directory / folder / node['token'])
        target.mkdir(parents=True, exist_ok=True)
        for kind in ('task', 'result') if with_result else ('task',):
            source = node['task'] if kind == 'task' else node['result']['path']
            expected = node['revision'] if kind == 'task' else node['result']['sha256']
            data = evidence_path(node, kind).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('The required evidence changed before preservation')
            path = regular_path(target / (kind + '.bin'))
            try:
                with path.open('xb') as output:
                    output.write(data)
            except FileExistsError:
                if digest(path) != expected:
                    raise ValueError('The kept evidence changed')
            kept[kind] = dict(source=source, path=str(path), sha256=expected)
        if field in node and node[field] != kept:
            raise ValueError('The kept evidence record changed')
        node[field] = kept
        for dependency in node.get('dependency_basis', {}):
            keep(state['claims'][state['tasks'][dependency]], True)
        if node['parent']:
            keep(state['claims'][node['parent']], False)

    keep(item, True)
    current_basis(state, item)
    if digest(evidence_path(item, 'result')) != item['result']['sha256']:
        raise ValueError('The accepted result changed before preservation')
    return copy.deepcopy(item)


def preserve(args, root):
    with store(root) as (state, directory):
        item = state['claims'].get(args.claim)
        if (not item or state['tasks'].get(item['task_id']) != args.claim
                or item['status'] != 'closed' or item['disposition'] != 'accepted'
                or item['executor'] != args.executor or Path(item['checkout']) != root
                or not item['result']):
            raise ValueError('Preserve only this owner\'s current accepted result')
        return preserve_evidence(state, directory, item)


def parents(state, token):
    found = set()
    while token:
        if token in found:
            raise ValueError('The claim ancestry has a cycle')
        found.add(token)
        token = state['claims'][token]['parent']
    return found


def active_children(state, token):
    return [item for item in state['claims'].values()
            if item['status'] != 'closed' and token in parents(state, item['parent'])]


def stopped(state, item, confirmed):
    if not confirmed:
        raise ValueError('Confirm stopped writers from actual host observations')
    if active_children(state, item['token']):
        raise ValueError('Keep ownership until child execution has resolution')
    if any(run['claim'] == item['token'] and run['status'] in ('running', 'unknown')
           for run in state['claim_runs'].values()):
        raise ValueError('Keep ownership until active or uncertain commands have resolution')


def claim(args, root):
    executor_identity(args.executor)
    if not args.task_id.strip() or len(args.task_id) > 200:
        raise ValueError('A short task identifier is necessary')
    task = project_path(root, args.task)
    if not task.is_file() or digest(task) != args.expect_revision:
        raise ValueError('The expected task revision does not match its current bytes')
    scopes = sorted(set(str(project_path(root, value).relative_to(root)) for value in args.scope))
    origin = str(checkout_origin(root))
    expires = interval(args.lease_seconds)
    declaration = dict(task_id=args.task_id, task=str(task), revision=args.expect_revision,
        executor=args.executor, checkout=str(root), scope=scopes, parent=args.parent,
        resources=sorted(set(args.resource)), read_only=args.read_only, depends_on=sorted(set(args.depends_on)))
    with store(root) as (state, _):
        previous = state['claims'].get(state['tasks'].get(args.task_id))
        if previous and previous['status'] != 'closed':
            if all(previous[key] == value for key, value in declaration.items()):
                return copy.deepcopy(get_claim(state, previous['token'], args.executor, root))
            raise ValueError('The task has an execution owner')
        if previous and previous['disposition'] == 'accepted' and previous['revision'] == args.expect_revision:
            raise ValueError('This task revision has an accepted result')
        ancestor_ids = set()
        if args.parent:
            parent = get_claim(state, args.parent, root=root)
            if parent['read_only'] and not args.read_only:
                raise ValueError('A child cannot increase write authority')
            if not all(any(Path(scope).is_relative_to(Path(p)) for p in parent['scope']) for scope in scopes):
                raise ValueError('The child scope is outside the parent scope')
            ancestor_ids = parents(state, args.parent)
            if any(run['claim'] in ancestor_ids and run['status'] in ('running', 'unknown')
                   for run in state['claim_runs'].values()):
                raise ValueError('Complete ancestor commands before child allocation')
        dependency_basis = {}
        for dependency in args.depends_on:
            item = state['claims'].get(state['tasks'].get(dependency))
            if not item or item['status'] != 'closed' or item['disposition'] != 'accepted':
                raise ValueError('A dependency has no accepted current result')
            current_basis(state, item, {args.task_id})
            if not item['result'] or digest(evidence_path(item, 'result')) != item['result']['sha256']:
                raise ValueError('A dependency result changed or is absent')
            dependency_basis[dependency] = dict(token=item['token'], revision=item['revision'], result_sha256=item['result']['sha256'])
        for token, other in state['claims'].items():
            if other['status'] == 'closed' or token in ancestor_ids:
                continue
            if args.read_only or other['read_only']:
                continue
            if any((root / a).is_relative_to(Path(other['checkout']) / b)
                   or (Path(other['checkout']) / b).is_relative_to(root / a)
                   for a in scopes for b in other['scope']):
                raise ValueError('The checkout scope has a different writer')
        token = uuid.uuid4().hex
        if digest(task) != args.expect_revision:
            raise ValueError('The task revision changed during allocation')
        reserve(state, args.resource, token)
        state['generation'] += 1
        item = dict(declaration, token=token, generation=state['generation'], status='running',
                    checkout_origin=origin,
                    disposition=None, result=None, dependency_basis=dependency_basis,
                    created=time.time(), observed=time.time(), expires=expires)
        state['claims'][token] = item
        state['tasks'][args.task_id] = token
        return copy.deepcopy(item)


def update(args, root):
    with store(root) as (state, directory):
        item = get_claim(state, args.claim, args.executor, root,
                         live=args.action in ('renew', 'finish'))
        if args.action == 'renew':
            item['expires'] = interval(args.lease_seconds)
            item['observed'] = time.time()
        elif args.action == 'finish':
            if item['status'] != 'running' or any(r['claim'] == args.claim and r['status'] in ('running', 'unknown')
                                                 for r in state['claim_runs'].values()):
                raise ValueError('Keep execution state until active commands have resolution')
            path = project_path(root, args.result)
            if not path.is_file():
                raise ValueError('The returned result file is absent')
            item['result'] = dict(path=str(path), sha256=digest(path))
            item['status'] = 'returned'
        elif args.action in ('close', 'transfer'):
            stopped(state, item, args.writers_stopped)
            if args.action == 'close':
                if args.disposition != 'abandoned':
                    if item['status'] != 'returned' or not item['result']:
                        raise ValueError('A result must return before acceptance or rejection')
                    if digest(Path(item['result']['path'])) != item['result']['sha256']:
                        raise ValueError('The returned result changed')
                    if args.disposition == 'accepted':
                        current_basis(state, item)
                        preserve_evidence(state, directory, item)
                item['status'], item['disposition'] = 'closed', args.disposition
                unreserve(state, item['token'])
            else:
                executor_identity(args.to)
                if digest(Path(item['task'])) != args.expect_revision:
                    raise ValueError('The expected transfer revision changed')
                # Scope and task revision changes require a separate new claim.
                if args.expect_revision != item['revision']:
                    raise ValueError('Close the old claim before a changed task assignment')
                old_token = item['token']
                item['status'], item['disposition'] = 'closed', 'transferred'
                state['generation'] += 1
                new = copy.deepcopy(item)
                new.pop('preserved', None)
                new.pop('basis_preserved', None)
                new.update(token=uuid.uuid4().hex, generation=state['generation'], executor=args.to,
                           status='running', disposition=None, result=None, created=time.time(),
                           observed=time.time(), expires=None)
                for key in item['resources']:
                    if state['resources'].get(key) == old_token:
                        state['resources'][key] = new['token']
                state['claims'][new['token']] = new
                state['tasks'][new['task_id']] = new['token']
                return copy.deepcopy(new)
        return copy.deepcopy(item)


def run(args, root):
    if not args.command or args.command[0] != '--' or len(args.command) < 2:
        raise ValueError('Put -- before the command')
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ValueError('Use a finite positive timeout')
    run_id = uuid.uuid4().hex
    with store(root) as (state, directory):
        item = get_claim(state, args.claim, args.executor, root)
        if item['status'] != 'running' or item['read_only']:
            raise ValueError('Only an active write assignment can execute a command')
        if any(not child['read_only'] for child in active_children(state, item['token'])):
            raise ValueError('Complete delegated writes before an unbounded parent command')
        if any(r['claim'] == args.claim and r['status'] in ('running', 'unknown')
               for r in state['claim_runs'].values()):
            raise ValueError('This assignment has an active or uncertain command')
        added = [key for key in args.resource if key not in item['resources']]
        reserve(state, args.resource, args.claim)
        logdir = regular_path(directory / 'claim-runs' / run_id)
        logdir.mkdir(parents=True)
        record = dict(id=run_id, claim=args.claim, generation=item['generation'], command=args.command[1:],
                      status='running', started=time.time(), added_resources=added, logs=str(logdir))
        state['claim_runs'][run_id] = record
    code = 1
    try:
        with (logdir / 'stdout.log').open('wb') as output, (logdir / 'stderr.log').open('wb') as error:
            process = subprocess.run(args.command[1:], cwd=root, stdout=output, stderr=error, timeout=args.timeout)
        code = process.returncode
        outcome = 'passed' if code == 0 else 'failed'
    except subprocess.TimeoutExpired:
        outcome = 'unknown'
    except OSError as problem:
        (logdir / 'launch-error.txt').write_text(str(problem), encoding='utf-8')
        outcome = 'failed'
    with store(root) as (state, _):
        record = state['claim_runs'][run_id]
        if record['status'] != 'running':
            observation = dict(status=outcome, exit_code=code, ended=time.time())
            path = regular_path(logdir / ('late-observation-' + uuid.uuid4().hex + '.json'))
            with path.open('x', encoding='utf-8') as output:
                json.dump(observation, output)
            record.setdefault('late_observations', []).append(dict(path=str(path), sha256=digest(path)))
            return copy.deepcopy(record), 1
        record.update(status=outcome, exit_code=code, ended=time.time())
        if outcome != 'unknown':
            for key in record['added_resources']:
                if state['resources'].get(key) == args.claim:
                    del state['resources'][key]
        return copy.deepcopy(record), 0 if outcome == 'passed' else 1


def inspect_task(state, root, task_id, executor):
    token = state['tasks'].get(task_id)
    summary = dict(format=1, task_id=task_id, observed_checkout=str(root), status='missing',
                   next_action='locate_task')
    if token is None:
        return summary
    item = state['claims'][token]
    expired = item['status'] != 'closed' and item['expires'] is not None and item['expires'] <= time.time()
    runs = [dict(run_id=run_id, status=run['status'], kind=run.get('kind', 'command'), logs=run.get('logs'))
            for run_id, run in state['claim_runs'].items()
            if run['claim'] == token and run['status'] in ('running', 'unknown')]
    summary.update(checkout=item['checkout'], executor=item['executor'], generation=item['generation'],
                   status='suspect' if expired else item['status'], disposition=item['disposition'], task=item['task'],
                   revision=item['revision'], result=item['result'], unresolved_runs=runs,
                   resources={key: owner for key, owner in state['resources'].items()
                              if owner == token})
    if item['status'] == 'closed':
        summary.update(next_action='read_closed_record', preserved=item.get('preserved'))
    elif Path(item['checkout']) != root:
        summary['next_action'] = 'locate_claim_checkout'
    elif runs or expired:
        summary['next_action'] = 'inspect_writers_and_effects'
    elif executor != item['executor']:
        summary['next_action'] = 'confirm_owner_and_writers'
    else:
        try:
            get_claim(state, token, executor, root)
            if item['status'] == 'returned':
                result = project_path(root, item['result']['path'])
                if not result.is_file() or digest(result) != item['result']['sha256']:
                    raise ValueError('The returned result is absent or changed')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            summary.update(next_action='examine_task_basis', reason=str(exc))
        else:
            summary['next_action'] = ('review_returned_result' if item['status'] == 'returned'
                                      else 'read_task_and_check_writers')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('claim', 'renew', 'finish', 'close', 'transfer', 'run', 'resolve-run', 'preserve', 'inspect'):
        command = commands.add_parser(name)
        command.add_argument('--repo', type=Path, required=True)
        if name != 'inspect':
            command.add_argument('--executor', required=True)
        if name not in ('claim', 'inspect'):
            command.add_argument('--claim', required=True)
        if name == 'claim':
            command.add_argument('--task-id', required=True)
            command.add_argument('--task', required=True)
            command.add_argument('--expect-revision', required=True)
            command.add_argument('--scope', action='append', required=True)
            command.add_argument('--resource', action='append', default=[])
            command.add_argument('--depends-on', action='append', default=[])
            command.add_argument('--parent')
            command.add_argument('--read-only', action='store_true')
        if name == 'inspect':
            command.add_argument('--task-id')
            command.add_argument('--executor')
        if name in ('claim', 'renew'):
            command.add_argument('--lease-seconds', type=float, default=0)
        if name in ('finish', 'resolve-run'):
            command.add_argument('--result', required=True)
        if name in ('close', 'transfer', 'resolve-run'):
            command.add_argument('--writers-stopped', action='store_true')
        if name == 'close':
            command.add_argument('--disposition', choices=['accepted', 'rejected', 'abandoned'], required=True)
        if name == 'transfer':
            command.add_argument('--to', required=True)
            command.add_argument('--expect-revision', required=True)
        if name == 'run':
            command.add_argument('--resource', action='append', default=[])
            command.add_argument('--timeout', type=float, default=600)
            command.add_argument('command', nargs=argparse.REMAINDER)
        if name == 'resolve-run':
            command.add_argument('--run-id', required=True)
    args = parser.parse_args()
    try:
        root = regular_path(args.repo).resolve(strict=True)
        if not root.is_dir():
            raise ValueError('The checkout must be a directory')
        code = 0
        if args.action == 'claim':
            result = claim(args, root)
        elif args.action == 'run':
            result, code = run(args, root)
        elif args.action == 'preserve':
            result = preserve(args, root)
        elif args.action == 'inspect':
            result, _ = inspect_state(root)
            if args.task_id is not None:
                result = inspect_task(result, root, args.task_id, args.executor)
            elif args.executor is not None:
                raise ValueError('Give a task ID when you supply an executor to inspect')
            else:
                for item in result['claims'].values():
                    if item['status'] != 'closed' and item['expires'] is not None and item['expires'] <= time.time():
                        item['status'] = 'suspect'
        elif args.action == 'resolve-run':
            with store(root) as (state, _):
                item = get_claim(state, args.claim, args.executor, root, live=False)
                record = state['claim_runs'][args.run_id]
                if not args.writers_stopped or record['claim'] != item['token'] or record['status'] not in ('running', 'unknown'):
                    raise ValueError('Resolve only this owner\'s uncertain command after writer inspection')
                path = project_path(root, args.result)
                record.update(status='resolved', resolution=dict(path=str(path), sha256=digest(path)))
                for key in record['added_resources']:
                    if state['resources'].get(key) == args.claim:
                        del state['resources'][key]
                result = copy.deepcopy(record)
        else:
            result = update(args, root)
        print(json.dumps(result, ensure_ascii=True))
        return code
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as problem:
        print(json.dumps({'error': str(problem), 'control': 'Examine ownership before mutation.'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
