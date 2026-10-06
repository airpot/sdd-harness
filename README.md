# SDD Harness

一个可跨对话、worktree 和编码 agent 使用的规格驱动开发（SDD）技能包。

当前版本：**0.5.1**。

**默认独立开发，按需启用协作。**小任务沿用现有项目记录，保持简短；日常独立开发无需拆分前后端任务，也无需新增角色配置、接口格式、mock 服务或团队 CI。

本技能结合 OpenSpec 的已接受规格与增量变更，以及 Spec Kit 的需求澄清与一致性检查。优先使用项目已有的规格与工具，两者均非必需依赖。

## 适用场景

- 从任务交接记录继续开发，在不同对话、检出目录或 harness 之间接续独立任务。
- 协作开发时，将组件任务关联到同一份已接受的接口契约及完整业务目标。
- 区分 mock 测试结果、真实接口提供方与调用方的验证结果，以及完整流程的验收证据。
- 审查共享变更，复用项目已有命令、运行资源与集成职责。
- 按确切代码与规格版本核验验收证据，追踪原始需求、实现与验证结果的对应关系。
- 审查测试断言是否符合已接受的需求，保留有效反例与回归证据。
- 依据相关现有代码与组件规划变更，针对当前集成目标验证实际合并后的候选版本。
- 在发布执行时核验候选版本是否仍符合发布条件。
- 按受影响行为与风险，选择系统、性能、安全、迁移与恢复检查。
- 明示必需验证的缺口，将已接受行为同步到项目的权威规格。
- 通过项目现有发布入口交付，并在获授权移除 worktree 前保存可恢复成果。
- 按英语与 ASD-STE100 写作规则编写内部开发文档。

## 安装到 Codex

仓库根目录即技能目录，包含 `SKILL.md`、`scripts/`、`references/` 和 `assets/`。可直接克隆到 Codex 能发现的技能目录中。

Windows PowerShell 示例：

```powershell
git clone https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

随后在 Codex 中调用 `$sdd-harness`。若尚未识别，可刷新技能发现或新开对话。若目标目录已存在，须先保留旧安装，再进行替换。

直接克隆会同时保留仓库中的开发记录。若只需安装 13 个技能文件，可使用安装脚本：

```text
git clone https://github.com/airpot/sdd-harness.git
cd sdd-harness
python scripts/install.py --into "~/.agents/skills"
```

ZCode 可将安装父目录设为 `~/.zcode/skills`。DeepSeek Harness 可使用项目的 `.dsh/skills`，或其实际配置的用户技能目录。技能发现、更新与其他路径详见[安装说明](references/install.md)。

安装脚本拒绝覆盖不同内容。更新前，应将旧安装保存到技能发现目录之外。

## 从安装包安装

下载 [sdd-harness-0.5.1.zip](dist/sdd-harness-0.5.1.zip) 及其 [SHA-256 校验文件](dist/sdd-harness-0.5.1.sha256)，解压到本地目录，然后在该目录执行：

```text
python sdd-harness/scripts/install.py --into "~/.agents/skills"
```

没有 Python 时，可将完整的 `sdd-harness` 目录复制到目标技能目录；须保留完整资源，不能只复制 `SKILL.md`。

## 继续项目开发

可向 agent 提供以下指令：

> Use sdd-harness to continue from the task handoff. Check results, ownership, and evidence before the next action.

工作流程与资源入口见[技能执行指令](SKILL.md)。项目记录应保存到目标项目中，并与技能安装目录分开。优先复用现有记录，再按需新增文件。

## 内部文档写作规范

新增或修改的内部开发文档默认使用英语。规格、计划、决策、验证与交接记录均应遵循[写作规范](references/writing.md)，采用短句、主动语态、明确条件与一致术语。

用户明确指定的语言与项目强制格式优先。代码标识符、命令、路径、引文及原始证据保持原样；与用户交流时，默认使用用户的语言。本 README 按用户要求使用中文，技能执行指令仍使用英语。

技能包采用 **STE-guided English（遵循 STE 指导的英语）**，尚未完成 ASD-STE100 词典与完整标准的合规审计。

## 工作区工具

脚本需要 Python 3.10 或更高版本；工作区命令还需要 Git 2.29 或更高版本。无第三方 Python 依赖。

```text
python scripts/workspace.py --help
```

| 命令 | 功能 |
| --- | --- |
| `inspect` | 读取 Git 状态；不能据此判定工作区无人使用或已获得写入权限。 |
| `snapshot` | 在 worktree 之外保存 HEAD 历史、当前普通文件及明确选取的被忽略成果。 |
| `verify` | 核验归档内容与哈希。 |
| `restore` | 将保存的成果恢复到新目录。 |

这些命令不会删除源 worktree。移除条件及支持的恢复范围见[恢复说明](references/recovery.md)。

协作开发者可在同一仓库中使用已分配任务、普通分支与独立检出目录。流程不强制要求跨机器执行权声明、心跳租约或协调服务。

书面任务范围不能强制执行原生权限；是否存在有效限制，须核验实际项目与宿主控制。安装脚本不会配置项目 CI 或发布凭据。

## 验证与打包

运行测试：

```text
python -m unittest discover -s tests -q
```

在尚未使用的输出路径生成安装包：

```text
python tools/package_skill.py --source . --output dist/sdd-harness-local.zip
```

打包工具会检查相对链接与 ZIP 完整性，拒绝覆盖已有输出，并返回安装包的 SHA-256 哈希。

测试覆盖工作区成果保存与恢复、安装及打包；不能据此认定所有产品、机器与操作系统的运行兼容性均已得到验证。

已接受的需求见[行为规格](specs/sdd-harness.md)，版本间的执行决策比较见[指令评测](evals/README.md)。评分标准与完整评测结果不提供给执行者作为输入。

当前指令评测集包含 28 个场景、84 项标准，覆盖独立开发与可选协作。隔离的宿主评测以多轮独立执行检查实际文件、哈希、行为与操作尝试；模拟器只用于仓库评测，不包含在技能安装包中。

- [0.5.0 工作流程验证记录](evals/results/0.5.0-validation.md)：结果、审查修正及证据适用范围。
- [0.5.1 分发验证记录](evals/results/0.5.1-validation.md)：根目录布局、安装文件筛选与安装包验证。
