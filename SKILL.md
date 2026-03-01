---
name: finance-one-pager
description: 基于 Tushare 数据生成上市公司结构化 One Pager（业务、财务摘要、亮点、风险）。支持 A 股/港股/美股，数据从 Tushare Pro 获取，输出为固定四段式中文一页纸。
---

# Finance One Pager

本 skill 融合 **Tushare 金融数据** 与 **投资备忘录 / One Pager 模板**：用 Tushare Pro API 拉取行情与财报数据，按约定结构生成上市公司的**结构化 One Pager**（0. 基本信息 / 1. 业务 / 2. 财务摘要 / 3. 亮点 / 4. 风险）。

## 适用场景与触发词

- 用户给出**上市公司名称或代码**，要求生成**一页纸公司概览**（业务、财务摘要、亮点、风险）。
- 典型表述：「写一份 XX 的 One Pager」「生成 XX 公司结构化概览」「用 Tushare 数据做 XX 的财务与亮点/风险分析」。
- 触发词：上市公司 One Pager、公司一页纸、业务 财务摘要 亮点 风险、equity research、investment memo。

## 在 Cursor 中使用

- **执行方式**：在**项目根目录**运行 Python，调用 Tushare 拉取数据后按本 skill 的 One Pager 模板填写并输出。
- **Token**：环境变量 `TUSHARE_TOKEN` 或项目/本 skill 目录下 `.env` 中 `TUSHARE_TOKEN=你的token`。本 skill 目录：`.cursor/skills/finance-one-pager/`。
- **依赖**：`pip install -r .cursor/skills/finance-one-pager/requirements.txt`（含 tushare、pandas、python-dotenv）。
- **接口索引**：本 skill 内 [reference/README.md](reference/README.md)，具体接口见 `reference/接口文档/`。

---

## 一、Tushare 数据获取（用于 One Pager）

### 1. Token 与依赖

- 未配置时引导用户：https://tushare.pro 注册并获取 Token，写入 `.env` 或环境变量 `TUSHARE_TOKEN`。
- 验证：`python -c "import tushare, pandas; print('OK')"`；缺则 `pip install tushare pandas python-dotenv`。

### 2. 常用接口速查（One Pager 常用）

| 用途 | 接口方法 | 说明 |
|------|----------|------|
| 股票/公司基本信息 | `pro.stock_basic(ts_code=...)` | 名称、地区、行业、上市日等 |
| 日线行情 | `pro.daily(ts_code, start_date, end_date)` | 收盘价、涨跌幅、成交量/额 |
| 财务指标 | `pro.fina_indicator(ts_code, start_date, end_date)` | ROE、ROA、毛利率、净利率、资产负债率、同比等 |
| 利润表 | `pro.income(ts_code, start_date, end_date)` | 营收、净利润、营业利润等 |
| 资产负债表 | `pro.balancesheet(...)` | 资产、负债、权益（可选） |
| 现金流量表 | `pro.cashflow(...)` | 经营/投资/筹资现金流（可选） |

- 日期格式：`YYYYMMDD`；股票代码：`000001.SZ`、`600519.SH`、港股/美股见 Tushare 文档。
- 完整 220+ 接口：见 [reference/README.md](reference/README.md) 与 `reference/接口文档/`。

### 3. 通用数据脚本（推荐：不用每次写新脚本）

在仓库或项目根目录执行，**只需传入股票代码**即可拉取 One Pager 所需数据并输出结构化摘要：

```bash
python scripts/fetch_one_pager_data.py 600519.SH
python scripts/fetch_one_pager_data.py 000001.SZ
```

若克隆到 Cursor 项目 `.cursor/skills/finance-one-pager/` 下，则可用：

```bash
python .cursor/skills/finance-one-pager/scripts/fetch_one_pager_data.py 600519.SH
```

脚本会拉取：基本信息、近一年日线、财务指标、利润表，并打印成「数据摘要」，直接用于填写 One Pager 模板；业务/亮点/风险的定性描述再根据公司与行业补充即可。

### 4. 数据获取流程（与 One Pager 配合）

1. 解析用户输入：公司名、证券代码、市场（A/港/美）。
2. 根据代码调用 Tushare：`stock_basic` → `daily`（近期）→ `fina_indicator`、`income`（最近 3–5 年或若干报告期）。
3. 从返回中提取：营收、增速、利润率、ROE/ROA、现金流与杠杆等，映射到 One Pager 的「财务摘要」「亮点」「风险」。
4. 若无权限或缺失：用定性描述并标注「数据基于历史公开信息/非实时财报」。
5. 按下面「上市公司 One Pager 模板」生成最终一页纸。

---

## 二、上市公司 One Pager 模板（固定结构）

用户要求对**上市公司**做**结构化一页纸**时，必须采用以下结构，**数据优先从 Tushare 拉取**，缺失时用定性描述并注明。

```
ONE-PAGER: [公司名称]（[代码]，[交易所]）

0. 基本信息 / BASIC INFO
   - 上市地、代码、行业、市值区间、总部
   - 一句话业务概览

1. 业务（Business Overview）
   - 核心业务板块与产品/服务
   - 收入结构（定性或定量）
   - 客户与场景、行业地位与竞争格局

2. 财务摘要（Financial Snapshot）
   - 最近期营收与增速（来自 Tushare income / fina_indicator）
   - 盈利能力：毛利率、净利率、ROE/ROA 等（来自 fina_indicator）
   - 现金流与杠杆概况
   - 2–3 个关键财务趋势；数据若为近似或历史，需标注

3. 亮点（Investment Highlights）
   - 3–6 条，每条：短标题 + 1–2 句证据（尽量引用 Tushare 指标）
   - 偏卖方研究风格，不给出买入/卖出评级

4. 风险（Key Risks）
   - 3–6 条，每条：风险内容、对业绩/估值的影响、可标概率/影响程度（如中概率/高影响）
   - 覆盖：宏观/行业、公司执行、财务/杠杆、监管/治理等

文末声明：以上仅供分析讨论，不构成投资建议；数据来源与时效请以披露为准。
```

### 写作与数据约定

- 输出语言：**中文**；关键财务术语可中英并列（如「自由现金流 FCF」）。
- 风格：简洁、偏卖方/机构研究，信息密度高；**不给出目标价或买卖建议**。
- 数据：优先标注「数据来源：Tushare」，并注明报告期或数据时点；若为定性或历史，明确写出「基于历史公开信息/非实时财报」。

### 市场与代码

- A 股：`600519.SH`、`000001.SZ` 等
- 港股：`00700.HK`、`09988.HK` 等
- 美股：`AAPL`、`NVDA` 等（Tushare 若支持则用对应接口，否则可仅做定性+行情补充）

---

## 三、One Pager 工作流（推荐步骤）

1. **解析输入**：公司名、代码、市场；缺代码时尝试推断或向用户确认。
2. **调用 Tushare**：`stock_basic` → `daily`（近 1 年）→ `fina_indicator`、`income`（如 20220101–当前），提取关键字段。
3. **填充模板**：把提取的数值与趋势填入 0～4 段；无法取数的部分用定性描述并注明。
4. **生成终稿**：按上述模板输出完整 One Pager，并附数据来源与免责声明。

---

## 四、脚本与参考

- **One Pager 数据（推荐）**：`scripts/fetch_one_pager_data.py <股票代码>` — 无需每次写脚本，直接拉数据并输出摘要。
- **通用 API 封装**：`scripts/api_client.py`（Tushare 类封装，支持从 `.env` 读 Token）。
- **接口文档**：本仓库下 [reference/README.md](reference/README.md)。
- **Tushare 官网**：https://tushare.pro/document/2
