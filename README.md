# SDD Harness

面向编程 agent 的规格驱动开发技能。当前版本：**0.16.6**。

受管项目的验收默认要求一个 MCP 服务、三个方法和两个必需 Hook；独立执行器通过现有 CLI 执行登记的验收并写入正式证据。生成代理不能用伪造回执或 JUnit 替代受保护的真实结果。缺少必需组件、有效证据或完整结束自检时，不放行。

- [MCP 接入](references/mcp.md)：`task_status`、`candidate_status` 和受限的 `request_gate`。默认 stdio，也支持独立执行器显式持有的 HTTP；不增加中转服务。
- [必需 Hook](references/hooks.md)复用现有处理器，检查任务与候选准入。其他扩展仍按项目需要接入。
- [候选与交付](references/delivery.md)绑定登记命令、原始报告、运行 ID 和构件摘要。重复请求读取原结果；结果未明时先查询原请求。
- [任务协调](references/coordination.md)保留实际归属和未决操作；[恢复规则](references/recovery.md)保护 worktree 成果。旧项目走受控迁移和历史回放。
- CLI 只读诊断保留稳定原因码和下一步，不替代验收或写证权限。异常、强制终止、陈旧或缺失的证据不能凭退出 0 获准通过。
- [项目检索](references/retrieval.md)默认准备 Zvec-Grep；不可用时记录原因，按任务需要回读原文。

## 安装与项目接入

仓库根目录可直接作为技能目录。Codex 用户可在自行备份旧安装后克隆固定版本：

```powershell
git clone --branch sdd-harness/v0.16.6 https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

Python 3.10+、Git 2.29+ 为脚本基础条件。受管验收的 MCP 服务需要 MCP SDK 2.3.0；Windows 受限生成器还需要 `pywin32`。复制或下载技能不会自动安装依赖、配置项目或启用 Hook。按[安装说明](references/install.md)在项目环境中完成接入，再在新会话调用 `$sdd-harness`。

既有安装应先备份至技能发现目录之外。项目升级前须处理活动操作和资源，并更新参与同一 registry 的 helper。不要通过改注册表指针或 Git 仓库归属覆盖来绕过迁移检查。

## 分发范围与历史

本仓库是独立分发输出，当前便携目录及必要说明与固定版本标签绑定；完整规格、测试、原始复测证据和新版 ZIP 留在源工作区。见[变更记录](CHANGELOG.md)。

既有 `dist/`、`release/` 和 `history/` 保留原字节，仅作为相应旧版本的历史材料。例如 [0.16.5 验证摘要](release/0.16.5-validation.md)和 [0.16.5 ZIP](dist/sdd-harness-0.16.5.zip)不能代替 0.16.6 的验证或安装包。
