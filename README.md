# SDD Harness

当前版本：**0.8.2**。以 SDD 为主线，默认独立开发，按需启用协作与辅助方法。

本仓库为可直接安装的独立发布输出。开发、测试与评测留在统一源码工作区；来源提交、文件哈希与历史资料映射见[发布清单](release/0.8.2-manifest.json)。

0.8.1 修正独立 agent 的效果比较入口，并明确归档前须另存暂存区独有的必要成果。运行脚本与 16 文件包结构保持原样。

0.8.2 修复恢复终态核验：恢复命令临时禁用 fsmonitor 回调，核验 index 后重查实际 Git 元数据与 HEAD，再返回所见 HEAD。两项真实仓库回归及 Git 2.29.2 实测通过。16 文件结构、安装器与权限边界保持原样。

## 辅助方法

- **TDD**：适用的行为变更先选一个有意义的失败测试，再作小改动、检查保留行为；文档和低影响格式修改可直接核验。
- **BDD/ATDD**：以规则、例子和待解问题澄清验收；预期结果须来自已接受规则或独立依据。
- **旧系统修复**：区分观察到的旧行为与应保留的需求，避免用新实现输出证明自己正确。
- **DDD**：按业务语境界定术语、规则责任与边界转换；依实际状态与一致性需要选择模型，简单脚本保持简单。
- **接口与完整流程**：区分 mock、真实调用方与提供方的兼容检查，以及持久化、权限等完整流程证据。
- **AIDD**：按不确定性、依赖、风险与实际能力选执行方式，分类处理失败，接回子 agent 成果；记录必要版本与配置，避免凭据进入上下文。
- **测试完整性**：审查断言、跳过、mock、测试发现与运行命令，不能只凭退出码或测试数量验收。
- **效果评估**：依据实际验收、返工、冲突、人工审查、耗时与总成本比较，不承诺普遍提速。

入口见[技能指令](SKILL.md)。按需读取[测试方法](references/testing.md)、[领域建模](references/domain.md)、[subagent 闭环](references/subagents.md)及[恢复规则](references/recovery.md)。OpenSpec 与 Spec Kit 均为可选工具。

## 安装

```powershell
git clone https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

若目标已存在，先将旧安装保存在技能发现目录之外。随后在 Codex 调用 `$sdd-harness`；必要时刷新发现或新开对话。

若只需 16 个技能文件：

```text
git clone https://github.com/airpot/sdd-harness.git
cd sdd-harness
python scripts/install.py --into "~/.agents/skills"
```

亦可下载[安装包](dist/sdd-harness-0.8.2.zip)与 [SHA-256 校验文件](dist/sdd-harness-0.8.2.sha256)，解压后运行 `python sdd-harness/scripts/install.py --into "~/.agents/skills"`。没有 Python 时复制完整目录，不可只复制入口。

ZCode、DeepSeek Harness 与实际宿主能力的检查见[安装说明](references/install.md)。跨宿主复制成功不等于原生能力已验证。

## 使用与证据

小任务沿用现有记录；复杂变更、协作、发布与清理才加载相关流程。换对话时保存交接，发布前核验权限与候选版本；worktree 满足归属、停止写入及成果保存条件后，可按授权归档移除。

内部开发指令采用英语与 [STE 写作规则](references/writing.md)，README 使用中文。短句与格式检查不构成完整 ASD-STE100 词典合规认证。

本版核验了打包、解压、安装、重复安装及拒绝覆盖本地修改。既有八案与 0.8.1 两案决策观察用于检查指令边界，不能证明真实项目普遍提效。历史开发资料位于 `history/source-0.7.3/`，其原始路径为历史记录，不是本版执行入口。
