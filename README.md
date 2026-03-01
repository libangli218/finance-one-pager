# finance-one-pager

基于 **Tushare Pro** 的上市公司结构化 One Pager 技能：用 Tushare 拉取行情与财报数据，按固定结构生成**一页纸公司概览**（业务、财务摘要、亮点、风险）。

适合在 **Cursor** 中作为 Skill 使用，或单独用脚本拉数据后按模板整理成 One Pager。

---

## 功能

- **数据来源**：Tushare Pro（股票列表、日线、财务指标、利润表等）
- **输出结构**：0. 基本信息 → 1. 业务 → 2. 财务摘要 → 3. 亮点 → 4. 风险（中文）
- **支持市场**：A 股、港股、美股（依 Tushare 接口权限）

---

## 快速开始

### 1. 获取 Tushare Token

1. 打开 [tushare.pro](https://tushare.pro) 注册
2. 在个人中心获取 API Token

### 2. 配置 Token

任选其一：

- 在仓库目录下复制 `.env.example` 为 `.env`，填入：`TUSHARE_TOKEN=你的token`
- 或设置环境变量：`TUSHARE_TOKEN=你的token`

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 在 Cursor 中作为 Skill 使用

将本仓库克隆到 Cursor 项目的 skills 目录下：

```bash
# 在你的项目根目录下
git clone https://github.com/你的用户名/finance-one-pager.git .cursor/skills/finance-one-pager
```

在项目根目录配置 `.env` 或环境变量 `TUSHARE_TOKEN`，然后即可在对话中让 AI 按本 skill 的模板生成上市公司 One Pager（需在 Cursor 中启用该 skill）。

### 5. 单独运行脚本拉数据

```bash
python scripts/api_client.py
```

或在自己的 Python 代码中调用 Tushare，参考 `SKILL.md` 中的接口与 One Pager 模板整理输出。

---

## 目录说明

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 技能说明、Tushare 接口速查、One Pager 模板与工作流 |
| `reference/` | Tushare 接口文档索引与 220+ 接口说明 |
| `scripts/api_client.py` | Tushare 封装示例（股票日线、财务指标、利润表等） |
| `src/one_pager_workflow.md` | One Pager 生成步骤简述 |
| `requirements.txt` | Python 依赖（tushare、pandas、python-dotenv） |
| `.env.example` | Token 配置示例（复制为 `.env` 并填入真实 Token） |

---

## 许可证

MIT
