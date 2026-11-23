"""Record and consume admission for managed acceptance requests."""

from contextlib import contextmanager
import hashlib
import math
from pathlib import Path
import secrets
import sqlite3
import subprocess
import time
import uuid

import coordination


MANAGED_FORMAT = 3
NATIVE_TOOL = 'mcp__sdd_harness__request_gate'
FIELDS = ('candidate_id', 'check_name', 'request_id')
REQUIRED_EVENTS = ('SessionStart', 'PreToolUse')
MAX_AGE = 120
REQUIRED = 'Managed acceptance requires MCP and Hook admission for this request'
REGISTRY_ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError,
                   sqlite3.Error, subprocess.SubprocessError)

NEXT_ACTION = {
    'gate_invalid_arguments': 'correct_gate_identifiers',
    'gate_not_approved': 'review_candidate_and_check',
    'gate_registry_unavailable': 'inspect_original_request',
    'gate_policy_changed': 'review_policy_and_restart_server',
    'gate_manifest_changed': 'register_new_candidate',
    'gate_evidence_stale': 'register_new_candidate',
    'gate_observation_missing_or_stale': 'restore_managed_gate_route',
    'gate_session_start_missing': 'reopen_trusted_session',
    'gate_session_binding_required': 'bind_current_session',
    'gate_admission_busy': 'inspect_original_request',
    'gate_request_conflict': 'use_original_request_for_original_check',
    'gate_request_not_recorded': 'inspect_original_request',
    'gate_admission_denied': 'review_gate_prerequisites',
    'gate_outcome_unknown': 'inspect_original_request',
    'gate_passed': 'inspect_selection_prerequisites',
    'gate_failed': 'review_gate_failure',
    'gate_replayed': 'read_existing_gate_result',
    'gate_history_only': 'read_existing_gate_result',
}


def guidance(code, reason=None):
    result = dict(reason_code=code, next_action=NEXT_ACTION[code])
    if reason is not None:
        result['reason'] = reason
    return result


class Denial(ValueError):
    def __init__(self, code, reason):
        super().__init__(reason)
        self.code = code

    def hook_reason(self):
        return f'[{self.code}; {NEXT_ACTION[self.code]}] {self}'


def registry_unavailable(problem):
    return Denial('gate_registry_unavailable',
                  f'Review the trusted registry, then inspect the original request without retrying: {problem}')


def gate_routes(state):
    routes = state.get('gate_routes', {})
    if not isinstance(routes, dict):
        raise registry_unavailable('The registry gate routes must be an object')
    for request, route in routes.items():
        if not isinstance(route, dict):
            raise registry_unavailable('The registry contains a malformed gate route')
        expiry, identity, ticket = route.get('expires'), route.get('identity'), route.get('ticket_sha256')
        if (type(expiry) not in (int, float) or (isinstance(expiry, float) and not math.isfinite(expiry))
                or not isinstance(identity, list) or len(identity) != len(FIELDS)
                or not all(isinstance(value, str) for value in identity) or identity[2] != request
                or not all(isinstance(route.get(key), str) for key in (
                    'checkout', 'manifest_sha256', 'manifest_path', 'session', 'claim', 'executor', 'task', 'observation'))
                or (ticket is not None and (not isinstance(ticket, str) or len(ticket) != 64 or not ticket.isascii()))):
            raise registry_unavailable('The registry contains a malformed gate route')
    return routes


def read_registry(root):
    try:
        state, directory = coordination.inspect_state(root)
        if not all(isinstance(state.get(key), dict) for key in ('candidates', 'operations')):
            raise ValueError('The registry gate records are malformed')
        gate_routes(state)
        return state, directory
    except Denial:
        raise
    except REGISTRY_ERRORS as problem:
        raise registry_unavailable(problem) from problem


@contextmanager
def route_store(root, **options):
    in_body = False
    try:
        with coordination.store(root, **options) as result:
            in_body = True
            yield result
            in_body = False
    except REGISTRY_ERRORS as problem:
        if in_body or isinstance(problem, Denial):
            raise
        raise registry_unavailable(problem) from problem


def ticket_digest(ticket):
    return hashlib.sha256(ticket.encode('ascii')).hexdigest()


def observe_start(root, session):
    if not session:
        raise Denial('gate_session_binding_required', 'A native session identifier is necessary')
    with route_store(root) as (state, _):
        state.setdefault('gate_sessions', {})[session] = str(root)


def observed_claim(state, root, route):
    if state.get('gate_sessions', {}).get(route['session']) != str(root):
        raise Denial('gate_session_start_missing', 'Load the required SessionStart Hook in a fresh Codex session')
    try:
        claim = coordination.get_claim(state, route['claim'], route['executor'], root)
    except ValueError as problem:
        raise Denial('gate_session_binding_required', str(problem)) from problem
    if claim['task'] != route['task']:
        raise Denial('gate_session_binding_required', 'The native task binding changed')


def route_matches(item, root, identity, route):
    return (item is not None and item['manifest']['format'] == MANAGED_FORMAT
            and item['checkout'] == str(root) == route['checkout']
            and item['manifest_sha256'] == route['manifest_sha256']
            and item['manifest_path'] == route['manifest_path']
            and identity == route['identity']
            and identity[1] in item['manifest']['gates'])


def candidate_matches(item, root, identity, route):
    return route_matches(item, root, identity, route) and not (item.get('retirement') or item.get('publish'))


def matching_gate_item(state, root, candidate_id, check_name):
    item = state['candidates'].get(candidate_id)
    if (item and item['checkout'] == str(root) and item['manifest']['format'] == MANAGED_FORMAT
            and check_name in item['manifest']['gates']):
        return item


def operation_matches(operation, item, identity):
    candidate_id, check_name, request_id = identity
    return (operation['request'] == request_id and operation['candidate'] == candidate_id
            and operation['stage'] == 'gate' and operation['gate'] == check_name
            and operation['manifest_sha256'] == item['manifest_sha256']
            and operation.get('gate_route', {}).get('source') == 'mcp-and-hook')


def request_conflict():
    return Denial('gate_request_conflict', 'This request ID does not identify the specified managed gate.')


def armed_request(state, root, item, identity):
    route = gate_routes(state).get(identity[2])
    if not route or not route.get('ticket_sha256') or route['expires'] <= time.time():
        return None
    if not route_matches(item, root, list(identity), route):
        raise request_conflict()
    return Denial('gate_admission_busy', 'Admission may be in progress; inspect the original request before acting')


def original_guidance(state, root, item, identity):
    """Leave the original admission intact and return only recovery guidance."""
    operation = state['operations'].get(identity[2])
    if operation and not operation_matches(operation, item, identity):
        conflict = request_conflict()
        return dict(status='denied', **guidance(conflict.code, str(conflict)))
    if operation and operation['status'] not in ('passed', 'failed'):
        status = operation['status']
        return dict(status=status, recorded_status=status, operation_id=Path(operation['directory']).name,
                    **guidance('gate_outcome_unknown', 'Inspect the original request and its effects before acting.'))
    try:
        armed = armed_request(state, root, item, identity)
    except Denial as conflict:
        return dict(status='denied', **guidance(conflict.code, str(conflict)))
    if armed:
        return dict(status='unknown', **guidance(armed.code, str(armed)))


def call_identity(event):
    args = event.get('tool_input')
    if (not isinstance(args, dict) or set(args) != set(FIELDS)
            or not all(isinstance(args[key], str) and 0 < len(args[key]) <= 128 for key in FIELDS)):
        raise Denial('gate_invalid_arguments', 'Use only the candidate, check, and request identifiers')
    return [args[key] for key in FIELDS]


def block_unresolved(state, root, item, identity):
    known = original_guidance(state, root, item, identity) if item else None
    if known:
        raise Denial(known['reason_code'], known['reason'])


def observe_call(root, session, binding, event):
    identity = call_identity(event)
    with route_store(root) as (state, _):
        item = state['candidates'].get(identity[0])
        now = time.time()
        if item is None:
            raise Denial('gate_not_approved', REQUIRED)
        if not binding.get('claim'):
            raise Denial('gate_session_binding_required', REQUIRED)
        routes = gate_routes(state)
        for key in list(routes):
            if routes[key]['expires'] <= now:
                del routes[key]
        block_unresolved(state, root, item, identity)
        tool_use_id = event.get('tool_use_id')
        route = dict(identity=identity, checkout=str(root), session=session, observation=uuid.uuid4().hex,
                     tool_use_id=tool_use_id if isinstance(tool_use_id, str) else None,
                     claim=binding['claim'], executor=binding['executor'],
                     task=str(root / binding['task']), manifest_sha256=item['manifest_sha256'],
                     manifest_path=item['manifest_path'], expires=now + MAX_AGE)
        observed_claim(state, root, route)
        if not candidate_matches(item, root, identity, route):
            raise Denial('gate_not_approved', 'Use an active managed candidate and a registered check')
        state.setdefault('gate_routes', {})[identity[2]] = route


def require_observation(state, root, item, identity):
    route = gate_routes(state).get(identity[2])
    if (not route or state['format'] != MANAGED_FORMAT or route['expires'] <= time.time()
            or not candidate_matches(item, root, identity, route)):
        raise Denial('gate_observation_missing_or_stale', REQUIRED)
    observed_claim(state, root, route)
    return route


def arm(root, identity):
    with route_store(root) as (state, _):
        item = state['candidates'].get(identity[0])
        block_unresolved(state, root, item, identity)
        route = require_observation(state, root, item, identity)
        # Expiry is checked again by require_observation; an existing ticket must never be replaced.
        if route.get('ticket_sha256'):
            raise Denial('gate_admission_busy', 'Admission may be in progress; inspect the original request before acting')
        ticket = secrets.token_hex(32)
        route['ticket_sha256'] = ticket_digest(ticket)
        return ticket, route['observation']


def discard(root, request, ticket):
    with coordination.store(root) as (state, _):
        routes = gate_routes(state)
        if routes.get(request, {}).get('ticket_sha256') == ticket_digest(ticket):
            del routes[request]


def consume(state, root, item, identity, ticket):
    if not ticket or len(ticket) != 64 or not ticket.isascii():
        raise ValueError(REQUIRED)
    route = require_observation(state, root, item, identity)
    if not secrets.compare_digest(route.get('ticket_sha256', ''), ticket_digest(ticket)):
        raise ValueError(REQUIRED)
    del state['gate_routes'][identity[2]]
    return {**{key: route[key] for key in ('session', 'observation', 'tool_use_id')},
            'source': 'mcp-and-hook'}
