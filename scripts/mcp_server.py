#!/usr/bin/env python3
"""Serve SDD Harness queries and approved gates over stdio or owned HTTP."""

import argparse
import asyncio
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from threading import Lock, Thread

import coordination
import delivery
import gate_route


TOOLS = ("task_status", "candidate_status", "request_gate")
GATE_FIELDS = set(gate_route.FIELDS)
EVIDENCE_ERRORS = (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError)


def load_policy(root, name):
    path = delivery.local_file(root, name)
    raw = path.read_bytes()
    if len(raw) > 1048576:
        raise ValueError("The gate policy exceeds the input limit.")
    policy = delivery.strict_json(raw)
    if not isinstance(policy, dict) or not policy:
        raise ValueError("The gate policy must identify approved candidates.")
    for candidate, item in policy.items():
        delivery.identifier(candidate)
        if (not isinstance(item, dict) or set(item) != {"registration_id", "manifest_sha256", "checks"}
                or not isinstance(item["registration_id"], str)
                or not re.fullmatch(r"[a-f0-9]{32}", item["registration_id"])
                or not isinstance(item["manifest_sha256"], str)
                or not re.fullmatch(r"sha256:[a-f0-9]{64}", item["manifest_sha256"])
                or not isinstance(item["checks"], list) or not item["checks"]):
            raise ValueError(f"Invalid gate policy entry: {candidate}")
        checks = [delivery.identifier(check) for check in item["checks"]]
        if len(checks) != len(set(checks)):
            raise ValueError(f"Repeated checks in the gate policy: {candidate}")
    return path, policy, delivery.digest(raw)


OWNER_BEARER = "SDD_HARNESS_MCP_BEARER"


def authorized_http_app(application, token):
    expected = b"Bearer " + token.encode("ascii")
    async def authenticated(scope, receive, send):
        if scope["type"] == "http":
            values = [value for key, value in scope.get("headers", []) if key.lower() == b"authorization"]
            if len(values) != 1 or not hmac.compare_digest(values[0], expected):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"www-authenticate", b"Bearer"), (b"content-type", b"application/json")]})
                await send({"type": "http.response.body", "body": b'{"error":"unauthorized"}'})
                return
        await application(scope, receive, send)
    return authenticated


def owner_pipe():
    # A blocked reader must not hold the standard buffered stdin lock during
    # an abnormal interpreter exit. Its private raw descriptor is not stdin.
    descriptor = os.dup(sys.stdin.fileno())
    try:
        return os.fdopen(descriptor, 'rb', buffering=0)
    except BaseException:
        os.close(descriptor)
        raise


def owned_http(app, port):
    """The independent executor owns stdin; EOF closes this same MCP service."""
    import uvicorn
    # Gate subprocesses must not inherit the transport credential.
    token = os.environ.pop(OWNER_BEARER, "")
    if not re.fullmatch(r"[a-f0-9]{64}", token):
        raise ValueError("Owned HTTP requires an ephemeral 64-hex bearer from its executor.")
    application = authorized_http_app(app.streamable_http_app(json_response=True, stateless_http=True), token)

    async def run():
        server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=port,
                                              log_level="warning", lifespan="on", timeout_graceful_shutdown=75))
        loop = asyncio.get_running_loop()
        ended = loop.create_future()
        def watch_owner():
            try:
                with owner_pipe() as pipe:
                    value = pipe.read(1)
                error = ValueError("The owner pipe accepts EOF only.") if value != b"" else None
            except BaseException as problem:
                error = RuntimeError("The owner pipe failed before EOF.")
                error.__cause__ = problem
            def signal():
                if server.started:
                    server.should_exit = True
                if not ended.done():
                    if error is None:
                        ended.set_result(None)
                    else:
                        ended.set_exception(error)
            try:
                loop.call_soon_threadsafe(signal)
            except RuntimeError:
                pass  # A failed server can finish before its owner closes the pipe.
        Thread(target=watch_owner, daemon=True).start()
        async def serve_until_owner_eof():
            try:
                await server.serve()
            except BaseException as problem:
                raise RuntimeError("The HTTP service failed instead of returning normally.") from problem
            if (server.lifespan.startup_failed or server.lifespan.shutdown_failed
                    or server.lifespan.error_occurred):
                raise RuntimeError("The HTTP application lifespan failed.")
            # Capture the order in this task before a late owner notification
            # can make an unsolicited server return appear to be normal drain.
            if not ended.done():
                raise RuntimeError("The HTTP service stopped before owner EOF.")
        serving = asyncio.create_task(serve_until_owner_eof())
        while not server.started and not serving.done():
            await asyncio.sleep(0.01)
        if server.started:
            address = server.servers[0].sockets[0].getsockname()
            print(json.dumps({"transport": "owned-http", "pid": os.getpid(),
                              "url": f"http://127.0.0.1:{address[1]}/mcp"}), flush=True)
            if ended.done():
                server.should_exit = True
        await asyncio.wait((serving, ended), return_when=asyncio.FIRST_COMPLETED)
        if not ended.done():
            await serving
            raise RuntimeError("The HTTP service stopped before owner EOF.")
        try:
            await ended
        finally:
            await serving
    asyncio.run(run())


def configure(root, policy, gate_python, transport="stdio", port=0):
    if transport == "owned-http" and not 1 <= port <= 65535:
        raise ValueError("Use the observed nonzero port from the executor-owned service readiness record.")
    argv = ["-B", Path(__file__).resolve().as_posix(), "serve", "--repo", root.as_posix(),
            "--policy", policy.as_posix(), "--gate-python", gate_python.as_posix()]
    print("[mcp_servers.sdd_harness]")
    if transport == "owned-http":
        print("url = " + json.dumps(f"http://127.0.0.1:{port}/mcp"))
        print("bearer_token_env_var = " + json.dumps(OWNER_BEARER))
    else:
        print("command = " + json.dumps(Path(sys.executable).as_posix(), ensure_ascii=False))
        print("args = " + json.dumps(argv, ensure_ascii=False))
    print("enabled_tools = " + json.dumps(TOOLS))
    print("required = true")
    print("startup_timeout_sec = 20\ntool_timeout_sec = 90")
    inherited = sorted(key for key in os.environ if key.startswith("GIT_"))
    if os.name == "nt":
        inherited = ["SystemRoot", "APPDATA", "LOCALAPPDATA", "USERPROFILE", "PATH", *inherited]
    if inherited and transport == "stdio":
        print("env_vars = " + json.dumps(inherited))


def serve(root, policy_path, policy, policy_hash, gate_python, transport="stdio", port=0):
    from mcp.server.mcpserver import MCPServer
    from mcp.types import CallToolResult, TextContent, ToolAnnotations

    async def exact_gate_arguments(ctx, call_next):
        params = ctx.params
        if ctx.method == "tools/call" and isinstance(params, dict) and params.get("name") == "request_gate":
            args = params.get("arguments")
            try:
                if not isinstance(args, dict) or set(args) != GATE_FIELDS:
                    raise ValueError("Use exactly candidate_id, check_name, and request_id.")
                for value in args.values():
                    delivery.identifier(value)
            except ValueError as exc:
                return CallToolResult(content=[TextContent(type="text", text=str(exc))], is_error=True,
                                      structured_content=gate_route.guidance("gate_invalid_arguments", str(exc)))
        return await call_next(ctx)

    app = MCPServer("sdd-harness", log_level="WARNING", middleware=[exact_gate_arguments])
    read_only = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                                idempotent_hint=True, open_world_hint=False)
    request = ToolAnnotations(read_only_hint=False, destructive_hint=False,
                               idempotent_hint=True, open_world_hint=False)
    lock = Lock()

    @app.tool(annotations=read_only)
    def task_status(task_id: str) -> dict:
        """Read a recorded task and its next action."""
        if not task_id.strip() or len(task_id) > 200 or "\x00" in task_id:
            raise ValueError("Use a short task identifier.")
        state, _ = coordination.inspect_state(root)
        row = coordination.inspect_task(state, root, task_id, None)
        return {key: row[key] for key in ("task_id", "status", "task", "revision", "next_action", "reason")
                if key in row}

    @app.tool(annotations=read_only)
    def candidate_status(candidate_id: str) -> dict:
        """Read a candidate, its checks, and its recorded evidence state."""
        state, _ = coordination.inspect_state(root)
        row = delivery.inspect_candidate(state, root, delivery.identifier(candidate_id))
        keys = ("candidate", "status", "historical_status", "next_action", "reason", "pending_gates",
                "registration_id", "manifest_sha256", "selection")
        result = {key: row[key] for key in keys if key in row}
        result["operations"] = [
            {key: item[key] for key in ("operation_id", "stage", "gate", "status", "gate_reports") if key in item}
            for item in row.get("operations", [])
        ]
        return result

    def approved_item(state, candidate, entry):
        policy_reason = "The trusted gate policy changed or is unavailable. Restart the server after review."
        try:
            current_hash = delivery.digest(policy_path.read_bytes())
        except OSError as exc:
            raise gate_route.Denial("gate_policy_changed", policy_reason) from exc
        if current_hash != policy_hash:
            raise gate_route.Denial("gate_policy_changed", policy_reason)
        item = state["candidates"].get(candidate)
        if (item is None or item["checkout"] != str(root) or item["manifest"]["format"] != gate_route.MANAGED_FORMAT
                or item["manifest_sha256"] != entry["manifest_sha256"]
                or delivery.registration_id(item) != entry["registration_id"]
                or item.get("retirement") or item.get("publish")):
            raise gate_route.Denial("gate_not_approved", "Use an approved, active managed format 3 candidate in this checkout.")
        delivery.check_retained_manifest(item)
        return item

    @app.tool(annotations=request)
    def request_gate(candidate_id: str, check_name: str, request_id: str) -> dict:
        """Run or retrieve one approved check. Inspect unresolved requests by their original ID before acting."""
        candidate, check, request_id = map(delivery.identifier, (candidate_id, check_name, request_id))
        identity = (candidate, check, request_id)
        reply = {"candidate_id": candidate, "check_name": check, "request_id": request_id}

        def explain(status, code, reason):
            return {**reply, "status": status, **gate_route.guidance(code, reason)}

        def original_guidance(state):
            item = gate_route.matching_gate_item(state, root, candidate, check)
            if item:
                return gate_route.original_guidance(state, root, item, identity)

        def before_failure(status, code, reason):
            # Another service may have admitted the original request since our first read.
            try:
                current, _ = gate_route.read_registry(root)
            except gate_route.Denial as exc:
                return explain("unknown", exc.code, str(exc))
            known = original_guidance(current)
            return {**reply, **known} if known is not None else explain(status, code, reason)

        def handoff_unknown(problem):
            try:
                gate_route.read_registry(root)
            except gate_route.Denial as exc:
                return explain("unknown", exc.code, f"{exc}. Child response: {problem}")
            return explain("unknown", "gate_outcome_unknown",
                           f"Admission or execution could not be determined. Inspect the original request "
                           f"and its effects before acting: {problem}")

        entry = policy.get(candidate)
        with lock:
            try:
                before, _ = gate_route.read_registry(root)
            except gate_route.Denial as exc:
                return explain("unknown", exc.code, str(exc))
            known = original_guidance(before)
            if known is not None:
                return {**reply, **known}
            if entry is None or check not in entry["checks"]:
                return before_failure("denied", "gate_not_approved", "Candidate or check is not approved.")
            try:
                item = approved_item(before, candidate, entry)
                if check not in item["manifest"]["gates"]:
                    raise ValueError("The check is not in the approved manifest.")
            except EVIDENCE_ERRORS as exc:
                return before_failure("denied", getattr(exc, "code", "gate_admission_denied"), str(exc))
            try:
                delivery.check_gate_evidence(before, root, item)
            except EVIDENCE_ERRORS as exc:
                return before_failure("stale", "gate_evidence_stale", str(exc))
            try:
                ticket, observation = gate_route.arm(root, list(identity))
            except gate_route.Denial as exc:
                if exc.code in ("gate_registry_unavailable", "gate_admission_busy", "gate_outcome_unknown"):
                    return explain("unknown", exc.code, str(exc))
                return before_failure("denied", exc.code, str(exc))
            except EVIDENCE_ERRORS as exc:
                return handoff_unknown(str(exc))
            try:
                result = subprocess.run(
                    [str(gate_python), "-B", str(Path(delivery.__file__).resolve()), "--root", str(root),
                     "run", "--stage", "gate", "--candidate", candidate, "--gate", check, "--request", request_id,
                     "--gate-ticket-stdin"],
                    input=(ticket + "\n").encode("ascii"), cwd=root, capture_output=True, timeout=70,
                )
                op = json.loads(result.stdout or result.stderr)
                if not isinstance(op, dict):
                    raise ValueError("No recognizable gate result")
                if "directory" not in op:
                    if op.get("reason_code") == "gate_registry_unavailable":
                        return explain("unknown", "gate_registry_unavailable", op["error"])
                    return handoff_unknown(op.get("error", "The child returned no operation record."))
                if not gate_route.operation_matches(op, item, identity):
                    raise ValueError("The child response does not match the original gate request.")
                replayed = op["gate_route"]["observation"] != observation
                outcome = {**reply, **delivery.gate_outcome(op, replayed), "replayed": replayed,
                           "operation_id": Path(op["directory"]).name, "report_hashes": op.get("gate_reports", {})}
            except EVIDENCE_ERRORS as exc:
                return handoff_unknown(str(exc))
            finally:
                try:
                    gate_route.discard(root, request_id, ticket)
                except EVIDENCE_ERRORS:
                    pass  # An unused ticket expires if the registry is unavailable.
            if op["status"] not in ("passed", "failed"):
                return outcome
            try:
                after, _ = gate_route.read_registry(root)
                delivery.check_gate_evidence(after, root, approved_item(after, candidate, entry))
            except gate_route.Denial as exc:
                status = "unknown" if exc.code == "gate_registry_unavailable" else "stale"
                return explain(status, exc.code, str(exc))
            except EVIDENCE_ERRORS as exc:
                return explain("stale", "gate_evidence_stale", str(exc))
            return outcome

    if transport == "owned-http":
        owned_http(app, port)
    else:
        app.run("stdio")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("configure", "serve"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--gate-python", type=Path, default=Path(sys.executable))
    parser.add_argument("--transport", choices=("stdio", "owned-http"), default="stdio")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    try:
        if not 0 <= args.port <= 65535:
            raise ValueError("Use a loopback port between 0 and 65535.")
        root = coordination.regular_path(args.repo).resolve(strict=True)
        policy = args.policy
        if policy.is_absolute():
            if not policy.is_relative_to(root):
                raise ValueError("Keep the trusted policy inside the project.")
            policy = policy.relative_to(root)
        path, approved, policy_hash = load_policy(root, policy.as_posix())
        gate_python = args.gate_python.absolute()
        if not gate_python.is_file():
            raise ValueError("Use an existing verifier Python executable.")
        if args.action == "configure":
            configure(root, path, gate_python, args.transport, args.port)
        else:
            serve(root, path, approved, policy_hash, gate_python, args.transport, args.port)
    except ImportError:
        parser.exit(2, "Serving MCP requires the Python MCP SDK 2.3.0.\n")
    except EVIDENCE_ERRORS as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
