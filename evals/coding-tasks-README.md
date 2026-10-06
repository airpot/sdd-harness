# Editable coding evaluations (repository only)

This stdlib tool creates tiny Python project fixtures for evaluating
implementation behavior. It is not installed with the skill and requires no
dependency installation. Use it for actual coding trials:
retain the original failure, give an executor the task, then score its actual
implementation. A completion claim in `REPORT.md` never earns behavior credit.
Reports identify the exact grader, candidate, accepted inputs, and observed runtime.

| Scenario | Task | Independent evidence |
| --- | --- | --- |
| `pagination-repair` | Filter before paginating; retain order and row identity; validate pagination inputs. | Mixed active rows, consecutive pages, invalid types/ranges, empty and out-of-range pages. |
| `existing-feature` | Add a capped integer discount by reusing the existing cents helper; retain its baseline contract. | Capping, flooring, large amounts, invalid rules, baseline behavior and a substituted helper proving reuse. |
| `handoff-removal` | Remove guest/admin bypass and replace the public authorization helper with token authentication. | Old helper absence, valid-token preservation and invalid-token rejection despite a stale approval claim. |

The fixture contains accepted `SPEC.md`, `TASK.md`, `src/service.py`, deliberately
incomplete public unittest tests and, for removal, a stale `HANDOFF.md`. Original
inputs have fixed SHA-256 hashes bound by `.sdd-coding-task.json`. The grader
compares marker hashes with its fixed originals; editing the marker cannot
rebase the accepted inputs. Source code is intentionally editable. Optional
`REPORT.md` is allowed, while unexpected files fail the scope check. The
specification, task, public tests and handoff must remain intact.

Run from the repository root in PowerShell. Choose an **unused** destination
strictly inside the system temporary directory:

```powershell
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('sdd-coding-' + [guid]::NewGuid().ToString('N'))
python evals/coding_tasks.py create --case pagination-repair --output $fixture
python evals/coding_tasks.py score --root $fixture
```

The original `score` returns exit code **1**: that is the expected failing
baseline. Keep the printed report path and its JSON before any executor edits.
Give the executor the fixture directory and ask it to complete `TASK.md` using
the skill version under evaluation. Do not supply the external grader cases or
an answer implementation. Inside the fixture it can run the ordinary public
tests (this command is also in `TASK.md`):

```powershell
Push-Location $fixture
python -B -c "import sys,unittest; sys.path.insert(0,'src'); unittest.main(module=None,argv=['unittest','discover','-s','tests'])"
Pop-Location
python evals/coding_tasks.py score --root $fixture
```

Each score creates a new `reports/score-<unique-id>.json` with exclusive creation;
it never overwrites a baseline. It reports accepted-input integrity, expected
code scope, public test execution and independent behavioral checks. Reports
record the candidate SHA-256, Python/runtime metadata and hashes observed before
execution and after each subprocess. Accepted inputs and scope are checked again
after each subprocess; any observed change remains a failure even if a later
check restores it. A changed or missing candidate fails identity verification.
These observations do not prevent arbitrary changes between snapshots. Every
check must pass. Exit codes: **0** successful creation or passing score; **1**
failed score; **2** invalid fixture, input path or operation. Repeat with fresh
directories for `existing-feature` and `handoff-removal`, and use separate
fixtures for trials with and without a skill. Do not repair a failing baseline
before capturing it, or reuse a prior executor's candidate as a fresh baseline.

```powershell
python -m unittest discover -s tests -p test_coding_tasks.py -v
```

This is **not native host control or a security sandbox**. Scoring refuses
unmarked paths, outside-temp paths, symlinks and Windows junctions; it does not
delete any sources. Candidate code runs in a Python `-I -B` subprocess with a
timeout. `-I` limits Python environment/import behavior; it does not restrict
filesystem, network or process access. Do not score malicious code. Scope is a
task instruction and an observed file check, not enforced permissions. The
grader lives outside the editable fixture, but cannot be hidden from an
executor with full host access. These cases establish local observed behavior,
not production correctness, native owner coordination or secure isolation.
