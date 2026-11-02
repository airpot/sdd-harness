# SDD Harness

面向编程 agent 的规格驱动开发（SDD）技能包。当前版本：**0.15.1**。
默认独立开发，按需使用协作、subagent 与执行约束。仓库根目录即技能目录，可直接安装。

## 能力

0.15.1 修正完整依赖链复核、归档后证据可用性、成功候选退役、只读绑定共存和诊断读取副作用，并限制恢复后的迟到回调。沿用现有 SQLite 与项目记录，不新增服务。

- **规格到验收**：结合 OpenSpec 与 Spec Kit 的长处，沿用项目已有规格、任务与工具；按需加入 TDD、DDD 和 AI 执行方法。
- **任务领取与锁**：关联 worktree 共用本机执行记录，分别记录任务、session 和子任务；原子领取、范围约束、依赖复核和显式交接，过期不自动夺取。
- **RC 到发布**：固定候选、构件摘要、配置与 gate 清单；RC 在全部必跑 gate 期间保持占用，生产发布到验证保持互斥；保留重复请求及不确定结果的恢复证据。
- **分层测试与回归增长**：单元与组件测试前置，RC 以真实系统及端到端验收为主。按需求和缺陷增加适用的正例、负例、边界与历史回归，核查断言后纳入必跑清单。
- **上下文与子 agent**：保留交接记录，由主 agent 接回、核验子任务结果；worktree 在归属明确、写入停止、成果已保存后可恢复归档。
- **检索与经验回路**：默认准备 Zvec-Grep，覆盖规格、参考资料、经验教训和相关项目文档；保留原文依据及覆盖缺口。后端不可用时记录原因，并按任务需要使用直接阅读与 `rg`。
- **按需原生 hook**：支持显式配置 Codex、ZCode 的相关检查。普通安装不修改全局配置。内部执行指令使用 STE-guided English，README 使用中文。

入口：[SKILL.md](SKILL.md)。专项规则见[任务协调](references/coordination.md)、[交付](references/delivery.md)、[测试](references/testing.md)、[子 agent](references/subagents.md)与[原生 hook](references/hooks.md)。

## 安装

```powershell
git clone https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

若目录已存在，先将旧安装移到技能发现目录之外保存。随后在 Codex 调用 `$sdd-harness`；新版本在下一轮对话可用，必要时刷新发现或新开对话。

也可下载[安装包](dist/sdd-harness-0.15.1.zip)与 [SHA-256 文件](dist/sdd-harness-0.15.1.sha256)，解压后执行：

```text
python sdd-harness/scripts/install.py --into "~/.agents/skills"
```

脚本只安装 29 个技能文件，拒绝覆盖不同内容。克隆仓库则同时保留历史文件和发布记录。ZCode、DeepSeek Harness 等路径详见[安装说明](references/install.md)。

执行脚本需要 Python 3.10+；工作区命令需要 Git 2.29+。SQLite 使用 Python 标准库，无须数据库服务。默认检索后端另需 Node.js 22+、Zvec-Grep 与首次模型下载，不打入 skill 包。仅阅读指令和模板无需 Python。

## 使用

> Use sdd-harness for this project. Read the accepted specifications, task ownership, and handoff before the next action.

按实际交付物选用[Skill、MCP、Agent、业务系统及数据分析提示](references/project-profiles.md)。小修改沿用简短记录，无须额外组队或新增基础设施。

## 验证与边界

0.15.1 在 2026-10-31 完成的本地全仓检查共 537 项：534 通过、3 项条件跳过，无失败或错误；最后两轮对相同冻结范围的完整独立审查均无待修问题。独立上下文完成本地归档后依赖接续、旧候选退役和后继 RC/gate 演练，由主 agent 另行核验实际记录与构件。详见[本版验证摘要](release/0.15.1-validation.md)、[发布清单](release/0.15.1-manifest.json)及[变更记录](CHANGELOG.md)。这些是此前执行并绑定文件哈希的验证结果，本次分发不将其记作重新执行。

旧版已存在的 shared=passed、local=running 不一致检查记录须由项目受控迁移；新检查防止再次形成该中断窗口。

安装不自动启用 hook、配置项目 CI 或授予发布权限。实际容器、生产流水线、原生 hook 执行仍须接入项目验证；不同机器、独立 clone 或不同 registry 不自动互斥。新脚本未完成原生 POSIX、精确最低版本及完整 STE 逐词资格验证。0.9.3 的历史验证不替代新增能力的验证。

本仓库为独立分发输出，开发与完整评测留在统一源码工作区。既有历史文件、旧包与标签保留，历史材料不作为当前执行入口。
