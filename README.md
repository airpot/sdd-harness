# SDD Harness

面向编程 agent 的规格驱动开发技能。当前版本：**0.16.1**。默认支持独立开发，按需接入协作、子 agent、共享资源锁和发布流程。

- 按规格、验收条件和适用证据推进开发；支持 OpenSpec、Spec Kit 与项目既有记录。
- 用[任务领取和只读接续](references/coordination.md)识别归属、锁、未决命令和证据。使用 worktree 时按[恢复规则](references/recovery.md)保护成果。
- [RC 与交付](references/delivery.md)绑定候选、构件和测试；可选严格模式核验原始 JUnit 报告。失败后保留原结果，[先登记不同候选再跑 RC 和 gate](references/delivery.md#use-a-new-registered-candidate-after-a-failed-gate)。
- [局部重审](references/workflow.md#repeat-only-the-failed-review)仅复用仍适用的执行证据；[经验状态](references/workflow.md#record-a-lesson-state)保留试用、已验证、防护和失效记录。
- [项目检索](references/retrieval.md)默认准备 Zvec-Grep；不可用时记录原因并按任务需要回读原文。[原生 hook](references/hooks.md)按项目授权另行启用。

## 安装

仓库根目录可直接作为技能目录。Codex 用户可克隆固定版本：

```powershell
git clone --branch sdd-harness/v0.16.1 https://github.com/airpot/sdd-harness.git "$HOME/.agents/skills/sdd-harness"
```

也可下载 [sdd-harness-0.16.1.zip](dist/sdd-harness-0.16.1.zip) 和 [SHA-256](dist/sdd-harness-0.16.1.sha256)，解压后执行：

```text
python sdd-harness/scripts/install.py --into "~/.agents/skills"
```

已有安装时，先备份至技能发现目录之外。随后在新对话调用 `$sdd-harness`。其他宿主路径见[安装说明](references/install.md)。脚本仅使用 Python 标准库；默认检索后端另需项目配置。严格模式首次升级原 registry 前，要结清活动工作与占用，并更新所有参与的 helper。

## 验证

见[本版验证摘要](release/0.16.1-validation.md)、[发布清单](release/0.16.1-manifest.json)和[变更记录](CHANGELOG.md)。本仓库为独立分发输出，完整开发和评测证据留在源工作区。
