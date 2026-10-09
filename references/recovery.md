# Preservation, Recovery, and Removal

CAUTION: BEFORE YOU REMOVE A WORKTREE OR OVERWRITE A BACKUP, KEEP ALL NECESSARY DATA.
IF YOU REMOVE OR OVERWRITE THE ONLY COPY, YOU CAN BE WITHOUT THE DATA.

## Use native archives when available

If the host supplies worktree archives for recovery of results, examine the tool's capabilities and worktree ownership.
Find if the native archive keeps necessary content that is only in the Git index.
Examine resource restrictions, active chats, and necessary results.
If the resource agrees with permitted cleanup conditions, use the native tool.
Examine preservation and removal results.
Obey [the writing policy](writing.md) for recovery records for project development.

If Codex supplies `list_artifacts` and `archive_worktree`, use the attachment identity from their result.
A path is not sufficient evidence of attachment identity.
If the archive does not include necessary ignored files or external results, keep these results at a different location first.
If the archive does not include content from the Git index, keep necessary content at a different location first.
Before you use the native archive tool, make sure that all these results are kept correctly.
For other harnesses, use only tools that are available.

## Use the skill's script

Python 3.10 or a subsequent version and Git 2.29 or a subsequent version are necessary for the script.
It has no third-party Python dependencies.
Replace `<skill-dir>` with the skill directory path that you use.

```text
python <skill-dir>/scripts/workspace.py inspect --repo <worktree>
python <skill-dir>/scripts/workspace.py snapshot --repo <worktree> --output <outside-worktree>/task.zip --include <necessary-ignored-path>
python <skill-dir>/scripts/workspace.py verify --archive <outside-worktree>/task.zip
python <skill-dir>/scripts/workspace.py restore --archive <outside-worktree>/task.zip --output <new-directory>
```

When `inspect` reads Git state, it uses the `--no-optional-locks` option.
A change only to a file timestamp does not cause an index refresh in the source.
It is not sufficient evidence that execution stopped.
It does not give write permission.

`snapshot` keeps these items:

- A Git bundle of HEAD history at snapshot and the Git object format
- Tracked files and untracked regular files at snapshot
- A list of tracked file deletions
- Ignored files or directories that you select with `--include`.

The Git index records staged content that can be different from HEAD and working files at snapshot.
The skill's snapshot does not keep content that is only in the Git index.
If necessary content is only in the Git index, keep this content at a different location.
Make sure that the method keeps this content correctly.
Before removal, make sure that the kept content is correct.

Keep the archive in a directory that is not in the worktree.
Do not overwrite a file that is there.
Before archive creation, the script rejects shallow repositories.
It does not use Git fetch for missing history.

Before creation of the archive or its parent directory, it also examines legacy graft information.
If this information is not empty and Git uses it, the script rejects the source.
Git finds the graft path from metadata and source environment settings.
This path selection includes linked worktrees and `GIT_GRAFT_FILE`.

Empty graft information does not prevent preservation of history that the script can keep when no other condition prevents preservation.
Keep the source.
Get full history with Git work that has authorization.
Or use a native preservation tool that you examined.
Then, do preservation and restoration checks again.

The script records hashes and source state.
It examines source changes during the copy.
These checks do not remove the condition that writers are stopped.

Select each necessary ignored result.
Keep external results at a different location.
Record locations that you can access.
The script does not make remote storage agree with source storage.
It does not collect all ignored directories or credentials.

`verify` examines the full set of archive members and content hashes.
`restore` writes only to a new directory.
The `restore` command makes HEAD and file state from the snapshot in the output.
Before creation of the output, the `restore` command makes a copy of the process environment.
It removes the repository-local variables that `git rev-parse --local-env-vars` gives from that copy.
It uses this same environment for each restore Git command.

It does not change the caller's environment or settings not related to the restore operation.
It removes repository, worktree, index, object-store, and repository-local configuration overrides from that environment.
Git gives this procedure for commands that use a different repository in its [hook guidance](https://git-scm.com/docs/githooks).
Before restore gives a report of success, it examines metadata for that output directly.
This check includes its Git directory, common directory, worktree root, HEAD, and index.

Each Git command for the restore output uses an empty hook directory that is temporary.
Each command also uses an empty `core.fsmonitor` value.
Initialization also uses an empty template directory.
These command-local settings prevent inherited templates, hooks, and fsmonitor callbacks from changes to the output state.

The empty fsmonitor value also prevents callback activation for compatible Git 2.29 versions.
These settings do not change user Git configuration.
After the index check, restore examines metadata and HEAD directly again.

The success result gives HEAD from this last check.
After all Git operations, restore compares each regular working file directly with the manifest inventory and content hashes.
This check includes selected ignored results.
This check does not include the Git metadata directory at the root.

At snapshot, a tracked regular file can be missing.
Restore can make this directory at the deleted file path when descendants that are kept at snapshot make this directory necessary.
Other deleted snapshot paths must not be there.

A new regular file at one of these other deleted paths prevents success.
A directory not in the manifest also prevents success at these paths.
Files not in the manifest and changed content prevent a verification success result.

An unborn repository has no HEAD history in the output and receives an empty index.
The `restore` command does not give native chats, snapshot staging state, other branches, or initial paths.
It also does not give processes, credential state, or external databases.
After recovery, examine the environment and evidence again.
Previous ownership records do not give permission.

Worktree restoration does not change configuration in the deployment target or migrated data to their previous state.
Use the permitted recovery procedure for operational effects in the project.

Before path traversal, the script examines `lstat` attributes.
It rejects symlinks and Windows reparse points without `Path.is_junction`.
It also rejects gitlinks, submodules, and paths that are not permitted in the script's path rules.
For these projects, use native tools with the necessary preservation capabilities.
Hashes that agree show content consistency.

They are not sufficient evidence of source trust.
These checks do not supply a sandbox to prevent concurrent filesystem replacement or source content from an attacker.

## Remove a worktree

The skill's script does not remove source directories.
Before removal, make sure of all these conditions:

1. Find ownership and the normalized absolute path.
   Make sure that the path is a temporary resource with worktree lifecycle management and approval for removal.
   Do not remove the primary worktree or a permanent environment.
2. Make sure that all related chats, writers, and background executions stopped.
   A timeout or no known processes is not sufficient evidence that execution stopped.
3. Keep necessary results at locations that you can access.
   Make sure that their preservation is correct.
   For the first important recovery, make the results from content in the backup in a different directory.
   Then, examine these results.
   For subsequent recoveries, obey the recovery validation policy for the project.
4. Prevent new operation of the resource between preservation checks and removal.
   If results change after preservation, keep the changed results again.
   Then, make sure that these results are kept correctly.
5. Use native removal or the available removal procedure for the host's Git worktrees.
   Examine the directory and registration state.
   Do not use forced recursive deletion as worktree lifecycle management.

If preservation gives a success result but removal gives a failure result, keep the archive record.
Continue the same operation.
   Do not overwrite the only backup.
After removal failure, examine writers, protection, preservation, and registration directly before a retry.
While the operation agrees with its conditions, continue the available operation.
Keep the archive with a satisfactory verification result.

If execution starts again or controls do not prevent new operation, stop removal.
After execution stops and protection prevents new operation again, keep newer necessary results.

If the last record update has a failure result, examine the state directly before you repair the record.
If ownership is unknown, execution continues, or necessary results are not kept, keep the resource.
Give a report of the condition that prevents removal.

If preservation of necessary results is satisfactory and no execution is active, you can remove the worktree before integration.
Worktree removal does not make chat archives.
It is not sufficient evidence of release success.
