# Preservation, Recovery, and Removal

## Prefer native archives

If the host provides recoverable worktree archives, check the tool's capabilities and managed ownership.
Check protected resources, active chats, and necessary results.
If the authorized cleanup conditions hold, use the native tool.
Check both preservation and removal results.
Write internal recovery records according to [the writing policy](writing.md).

If Codex provides `list_artifacts` and `archive_worktree`, use the returned attachment identity.
Do not infer attachment identity from a path.
If the archive omits necessary ignored files or external results, preserve those results separately first.
Then verify those results before using the native archive tool.
For other harnesses, use only tools that actually exist.

## Use the bundled script

The script needs Python 3.10 or later and Git 2.29 or later.
It has no third-party Python dependencies.
Replace `<skill-dir>` with the actual installation path.

```text
python <skill-dir>/scripts/workspace.py inspect --repo <worktree>
python <skill-dir>/scripts/workspace.py snapshot --repo <worktree> --output <outside-worktree>/task.zip --include <necessary-ignored-path>
python <skill-dir>/scripts/workspace.py verify --archive <outside-worktree>/task.zip
python <skill-dir>/scripts/workspace.py restore --archive <outside-worktree>/task.zip --output <new-directory>
```

`inspect` reads Git state. It does not prove idle state or grant write permission.

`snapshot` saves these items:

- A Git bundle of current HEAD history and the Git object format.
- Current tracked files and ordinary untracked files.
- A list of tracked file deletions.
- Ignored files or directories that you select with `--include`.

Save the archive outside the worktree. Do not overwrite an existing file.
The script rejects shallow repositories before archive creation. It does not fetch missing history.
Keep the source. Obtain complete history through separately authorized Git work, or use a verified native preservation tool.
Then repeat preservation and restoration checks.
The script records hashes and source state. It checks for observable changes during copying.
These checks do not replace stopped writers.

Select necessary ignored results individually.
Preserve external results separately. Record accessible locations.
The script does not synchronize remote storage or collect all ignored directories or credentials.

`verify` checks the complete archive member set and content hashes.
`restore` writes to a new directory only. It restores HEAD and current file state.
It does not restore native chats, exact staging state, other branches, original paths, processes, credentials, or external databases.
After recovery, check the environment and evidence again.
Old ownership records do not grant permission.

Worktree restoration does not reverse a deployed configuration or data migration.
Use the project's authorized operational recovery process.

The script rejects symlinks, gitlinks, submodules, and unsupported paths.
For these projects, use native tools with the necessary preservation capabilities.
Matching hashes prove content consistency. They do not prove source trust.

## Remove a worktree

The bundled script does not remove source directories.
Before removal, satisfy all these conditions:

1. Identify ownership and the normalized absolute path.
   Confirm that the path belongs to authorized, managed temporary resources.
   Do not remove the primary worktree or a permanent environment.
2. Confirm that all relevant chats, writers, and background executions stopped.
   A timeout or the absence of known processes does not prove stopped state.
3. Preserve necessary results reliably at accessible locations.
   For the first important recovery, restore results into a separate directory.
   Then check the restored results.
   For later recoveries, follow the project's recovery validation policy.
4. Protect the resource against new use between preservation checks and removal.
   If results change after preservation, save the changed results again.
   Then verify the saved results.
5. Use native removal or the host's supported Git worktree removal process.
   Check the directory and registration state.
   Do not substitute forced recursive deletion for worktree lifecycle management.

If preservation succeeds but removal fails, keep the archive record and continue the same operation.
Do not overwrite the only backup.
After a failed removal, check writers, protection, preservation, and actual registration before retrying.
Continue the supported operation while its conditions hold. Keep the verified archive.

If use resumes or protection is lost, stop removal.
Preserve newer necessary results after stopped use and protection are established again.

If the final record update fails, check actual state before repairing the record.
If ownership is unknown, use continues, or necessary results are not saved, keep the resource.
Report the reason for keeping the resource.

If its necessary results are reliably preserved, an idle worktree can be removed before integration.
Worktree removal does not create chat archives or prove a successful release.
