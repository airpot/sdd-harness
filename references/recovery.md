# Preservation, Recovery, and Removal

## Prefer native archives

If the host provides recoverable worktree archives, check the tool's capabilities and managed ownership.
Check whether the native archive preserves necessary content held only in the Git index.
Check protected resources, active chats, and necessary results.
If the authorized cleanup conditions hold, use the native tool.
Check both preservation and removal results.
Write internal recovery records according to [the writing policy](writing.md).

If Codex provides `list_artifacts` and `archive_worktree`, use the returned attachment identity.
Do not infer attachment identity from a path.
If the archive omits necessary ignored files or external results, preserve those results separately first.
If the archive omits necessary content held only in the Git index, preserve that content separately first.
Then verify all separately saved results before using the native archive tool.
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

`inspect` reads Git state with optional Git locks disabled. A timestamp-only file change does not refresh the source index.
It does not prove idle state or grant write permission.

`snapshot` saves these items:

- A Git bundle of current HEAD history and the Git object format.
- Current tracked files and ordinary untracked files.
- A list of tracked file deletions.
- Ignored files or directories that you select with `--include`.

The Git index records staged content that can differ from HEAD and current working files.
The bundled snapshot does not preserve content that exists only in the Git index.
If necessary content exists only in the Git index, preserve that content separately through a reliable method.
Before removal, verify the saved content itself.

Save the archive outside the worktree. Do not overwrite an existing file.
The script rejects shallow repositories before archive creation. It does not fetch missing history.
It also rejects effective nonempty legacy graft information before it creates the archive or its parent directory.
Git resolves the graft path from actual metadata and source environment settings, including linked worktrees and `GIT_GRAFT_FILE`.
Empty graft information does not prevent preservation of otherwise supported history.
Keep the source. Obtain complete history through separately authorized Git work, or use a verified native preservation tool.
Then repeat preservation and restoration checks.
The script records hashes and source state. It checks for observable changes during copying.
These checks do not replace stopped writers.

Select necessary ignored results individually.
Preserve external results separately. Record accessible locations.
The script does not synchronize remote storage or collect all ignored directories or credentials.

`verify` checks the complete archive member set and content hashes.
`restore` writes to a new directory only. It restores HEAD and current file state.
Before creating the output, restore copies the process environment and clears the repository-local variables reported by `git rev-parse --local-env-vars`.
It uses that same environment for every restore Git command. It does not change the caller's environment or unrelated settings.
This includes repository, worktree, index, object-store, and repository-local configuration overrides.
Git documents this procedure for commands that target another repository in its [hook guidance](https://git-scm.com/docs/githooks).
Restore checks the output's actual Git directory, common directory, worktree root, HEAD, and own index before it reports success.
Every Git command that targets the restore output uses a temporary empty hook directory and an empty `core.fsmonitor` value.
Initialization also uses an empty template directory.
These command-local settings prevent inherited templates, hooks, and fsmonitor callbacks from changing restored state.
The empty fsmonitor value also disables callbacks on supported Git 2.29 versions.
These settings do not change user Git configuration.
After the index check, restore checks actual metadata and HEAD again.
The success result reports this final observed HEAD.
After all Git operations, restore checks every actual regular working file against the manifest inventory and content hashes.
This check includes selected ignored results and excludes only the root Git metadata directory.
A deleted tracked regular file can be replaced by a directory when saved current descendants require that directory.
Other deleted snapshot paths must remain absent. A recreated regular file or an undeclared directory prevents success.
Unexpected files and changed content prevent a successful verification result.
An unborn repository remains unborn and receives an empty index in the output.
It does not restore native chats, exact staging state, other branches, original paths, processes, credentials, or external databases.
After recovery, check the environment and evidence again.
Old ownership records do not grant permission.

Worktree restoration does not reverse a deployed configuration or data migration.
Use the project's authorized operational recovery process.

The script checks `lstat` attributes before path traversal and rejects symlinks and Windows reparse points without `Path.is_junction`.
It also rejects gitlinks, submodules, and unsupported paths.
For these projects, use native tools with the necessary preservation capabilities.
Matching hashes prove content consistency. They do not prove source trust.
These checks do not provide a sandbox against concurrent filesystem replacement or malicious source content.

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
