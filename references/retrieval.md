# Project Retrieval

## Prepare the default backend

Zvec-Grep is the default backend for project retrieval.
For first project use, prepare the backend. Obey the user's applicable setup authorization.
After root, model, or document scope changes, examine the setup again.
If a project instruction selects a different backend, obey the instruction.
Keep the selected backend, version, model, root, and setup result in the task record that the project uses.

Do not include backend dependencies, models, or indexes in the portable skill package.
Use a verified command or a tool directory that the source index excludes.
For npm package `@zvec/zvec-grep` version `0.2.2`, the minimum `Node.js` version is 22.
If setup is necessary and authorized, use these example commands:

```text
npm install --prefix "<tool-directory>" @zvec/zvec-grep@0.2.2
node "<tool-directory>/node_modules/@zvec/zvec-grep/dist/cli/index.js" --version
```

Replace `<tool-directory>` with the selected absolute path.
In these examples, `zg` means the verified command.
If the host has no verified `zg` command, replace `zg` with `node "<absolute-entry.js>"`.
Use the absolute path to `dist/cli/index.js` from the version command. Keep `node` in the command.
Before commands for other releases, examine their help.
Do not use `zg install` automatically.
The command changes agent configuration and approval settings. It can start a daemon.

Use a local model as the default.
For mixed-language documents, first examine `local/multilingual-e5-small` with representative questions.
For English code, `local/potion-code-16m-v2` is an alternative.
Before model acceptance, examine source evidence for questions in the languages that the project uses.
An initial download is necessary for model files. Local models keep project content on the machine.
If a remote provider is necessary, first make sure that authorization permits content transfer.

Before the first index write, select the [document scope and exclusions](#examine-document-coverage).
From the selected project root, use these example commands:

```text
zg index . --embedding local/multilingual-e5-small --mode direct --debug
zg query "where archive entries are checked" --mode direct --refresh wait --limit 5 --preview short
zg status --mode direct
```

Version `0.2.2` uses the working directory for queries, without `--root`.
Its `direct` mode has refresh `OFF` as the default. Use `--refresh wait` for freshness.
Before writes or service operations, use the [effect controls](#examine-source-and-effects).

If runtime, download, model quality, authorization, or backend failure prevents setup, record the reason and next action.
Use direct reads and `rg` for work that these tools can support.
Keep setup and coverage gaps in the task record. A fallback does not show index readiness.
Do not stop independent development only because the backend is unavailable.

## Examine document coverage

Find applicable documents in the locations that the project uses.
Use the project inventory, task links, and file discovery.
Git ignore rules and search filters can hide necessary documents.
Do not make a new structure for project directories or a document template mandatory.

| Category | Scope when present |
| --- | --- |
| Project rules | README, AGENTS, development constraints, and project policies |
| Specifications | Accepted requirements, acceptance conditions, and related change specifications |
| Design and contracts | Architecture, decisions, interfaces, and data models |
| References | Business references, technical references, and local copies of external sources |
| Lessons and problems | Verified lessons, incident reviews, known limitations, and technical debt |
| Current work | Task records, handoffs, and related source and tests |

For each category, keep the selected paths or the reason that the category is not applicable.
For large projects, select the task scope. Include linked constraints across its boundaries.
Keep document status, authority, version, and source identity with the coverage record.
Search rank does not give drafts, references, or history authority to change accepted requirements.
If sources conflict, use [specification review](spec-review.md).

After an index refresh, examine admission of each selected file.
Use file records from the backend or path-filtered queries with identifiable source text.
Compare the returned content with the file at the selected root.
Use different entries for missing files, extraction failures, truncation, and unresolved admission.
Total file counts and an index command with a success result do not prove document coverage.
A query hit shows only the returned content. It does not prove extraction of all file content.
If the backend cannot show admission, keep the coverage gap.
Then, read the file directly.

For necessary ignored or hidden documents, examine filters for their paths and ignore settings.
Keep exclusions for secrets, dependencies, build output, caches, and raw logs.
Before an ignore override, examine the files that the override includes.
Exclude evaluator-only answers and grading criteria from execution inputs and their index.
Project requirements and acceptance conditions stay in scope.

Zvec-Grep admits Markdown and other supported text formats.
It skips PDF and Office files.
For necessary unsupported files, make a text copy with source locations and a source hash.
Compare the copy with the source file. Keep their identities and conversion limits.
If conversion is unavailable or omits necessary content, record the gap.
If direct inspection is possible, use it.
If necessary files have unresolved coverage, do not give a report of full coverage.

## Select the query tool

Read the task specifications, constraints, and acceptance conditions directly.
Search results help you find source. They do not replace these records.

If names, paths, or text are sufficient for `rg`, use `rg`.
If symbol tools help the task, use them for definitions and references.
If source locations or wording are unknown, use hybrid retrieval.
Hybrid retrieval uses lexical ranking and semantic retrieval.
Lexical ranking gives a result sequence from text features. Semantic retrieval finds related meanings.
Default backend preparation does not make a semantic call necessary for each question.

Set a token or output budget.
Start with short results. Then read necessary source sections.
Increase the scope only for remaining uncertainty.
Record output truncation and zero hits as evidence limits.
These limits are not sufficient evidence that there is no related source.

## Examine source and effects

Before important claims, read source files at the selected project root again.
Read necessary context. Keep the root and content identity with evidence.
Dirty files contain changes that the HEAD commit does not record.
When identity is necessary for dirty files, keep a content hash or snapshot.
HEAD does not identify their content.

Use a different index for each checkout or worktree root.
An index is a database of source locations and content representations.
An index seed is an initial copy, not evidence that the index agrees with source files.
After branch or source changes, do an index refresh before queries.
For an embedding model change, examine compatibility. If its vector space changes, do an index rebuild.
If freshness is unknown, record this gap. Read source directly.

Initialization, index writes, and watchers are effects, also for `search` tools.
A watcher is a background process that finds file changes.
Before these effects, use [ownership controls](collaboration.md) and [recovery controls](recovery.md).
For unknown outcomes, use [effect recovery](workflow.md#resolve-uncertain-effects).
If ownership or applicable authorization is not clear, do not stop a shared service.

For lesson discovery, verification, use, and maintenance, use the [lesson loop](workflow.md#use-lessons-across-tasks).
At task closure, keep useful supported lessons and necessary unverified follow-up in the project's existing records.
After document changes, use this procedure:

1. If the backend is available, refresh the index.
   Then, examine admission of the changed files again.
2. If the backend is unavailable, update the recorded gap.
   Use direct reads for work that they can support.

Before lesson reuse, examine its source evidence and applicability to the current task.

MCP is optional. Its default tool is `zvec_grep_search`.
Before MCP queries, examine the host's tool schema and client.
In that schema, use the project's absolute root path and freshness value `wait_for_fresh`.
For CLI and MCP results, use the same source and effect controls.
