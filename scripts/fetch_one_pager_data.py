#!/usr/bin/env python3
"""
One Pager 通用数据拉取脚本

用法：在项目根目录或本脚本所在目录运行，传入股票代码即可，无需每次写新脚本。
  python scripts/fetch_one_pager_data.py 600519.SH
  python scripts/fetch_one_pager_data.py 000001.SZ
  python .cursor/skills/finance-one-pager/scripts/fetch_one_pager_data.py 600519.SH

从 Tushare 拉取：基本信息、近一年日线、财务指标、利润表，并输出结构化数据摘要，
供直接用于填写 One Pager 模板（0.基本信息 / 1.业务 / 2.财务摘要 / 3.亮点 / 4.风险）。
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pandas as pd
import tushare as ts


def _format_date(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return "—"
    if isinstance(s, float):
        if abs(s) >= 1e8:
            return f"{s/1e8:.2f}亿"
        if abs(s) >= 1e4:
            return f"{s/1e4:.2f}万"
        if abs(s) < 10 and s != 0 and "margin" in str(s).lower() or "roe" in str(s).lower():
            return f"{s:.2f}%"
        return f"{s:.2f}"
    return str(s)


def fetch_one_pager_data(ts_code: str):
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        print("ERROR: 未配置 TUSHARE_TOKEN，请在 .env 或环境中设置", file=sys.stderr)
        sys.exit(1)
    ts_code = ts_code.strip().upper()
    if not ts_code.endswith((".SH", ".SZ")):
        if len(ts_code) == 6:
            ts_code = ts_code + ".SH" if ts_code.startswith(("6", "5")) else ts_code + ".SZ"
    pro = ts.pro_api(token)
    end = datetime.now().strftime("%Y%m%d")
    start_daily = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    start_fina = "20200101"

    out = []
    out.append("=" * 60)
    out.append(f"ONE PAGER 数据摘要 | {ts_code} | 数据来源: Tushare")
    out.append("=" * 60)

    # 1. 基本信息
    basic = pro.stock_basic(ts_code=ts_code, fields="ts_code,name,area,industry,market,list_date")
    if basic.empty:
        out.append("\n[基本信息] 未查到该代码，请核对 ts_code（如 600519.SH、000001.SZ）")
        name = area = industry = list_date = "—"
    else:
        row = basic.iloc[0]
        name, area, industry, list_date = row["name"], row["area"], row["industry"], row["list_date"]
        out.append("\n--- 0. 基本信息 ---")
        out.append(f"  名称: {name} | 地区: {area} | 行业: {industry} | 上市日: {list_date}")

    # 2. 日线（近一年）
    daily = pro.daily(ts_code=ts_code, start_date=start_daily, end_date=end)
    if daily.empty:
        out.append("\n--- 日线 --- 无数据")
        latest_close = price_min = price_max = latest_date = None
    else:
        daily = daily.sort_values("trade_date", ascending=False)
        latest_close = float(daily.iloc[0]["close"])
        latest_date = daily.iloc[0]["trade_date"]
        price_min = float(daily["close"].min())
        price_max = float(daily["close"].max())
        out.append(f"\n--- 日线（近一年） ---")
        out.append(f"  最新收盘: {latest_close:.2f}（{latest_date}）| 区间: {price_min:.2f} ~ {price_max:.2f}")

    # 3. 财务指标
    fina = pro.fina_indicator(ts_code=ts_code, start_date=start_fina, end_date=end)
    if fina.empty:
        out.append("\n--- 财务指标 --- 无数据")
    else:
        fina = fina.sort_values("end_date", ascending=False)
        out.append("\n--- 财务指标（最近几期）---")
        for _, r in fina.head(6).iterrows():
            ed = r.get("end_date", "")
            roe = r.get("roe")
            roa = r.get("roa")
            gross = r.get("grossprofit_margin")
            net = r.get("netprofit_margin")
            debt = r.get("debt_to_assets")
            op_yoy = r.get("op_yoy")
            parts = [f"  {ed}"]
            if roe is not None and not pd.isna(roe): parts.append(f"ROE={roe:.2f}%")
            if roa is not None and not pd.isna(roa): parts.append(f"ROA={roa:.2f}%")
            if gross is not None and not pd.isna(gross): parts.append(f"毛利率={gross:.2f}%")
            if net is not None and not pd.isna(net): parts.append(f"净利率={net:.2f}%")
            if debt is not None and not pd.isna(debt): parts.append(f"资产负债率={debt:.2f}%")
            if op_yoy is not None and not pd.isna(op_yoy): parts.append(f"营收同比={op_yoy:.2f}%")
            out.append(" | ".join(parts))

    # 4. 利润表
    income = pro.income(ts_code=ts_code, start_date=start_fina, end_date=end, fields="end_date,revenue,n_income,total_profit")
    if income.empty:
        out.append("\n--- 利润表 --- 无数据")
    else:
        income = income.sort_values("end_date", ascending=False)
        out.append("\n--- 利润表（最近几期）---")
        for _, r in income.head(6).iterrows():
            ed = r.get("end_date", "")
            rev = r.get("revenue")
            ni = r.get("n_income")
            tp = r.get("total_profit")
            rev_s = _format_date(rev) if rev is not None and not pd.isna(rev) else "—"
            ni_s = _format_date(ni) if ni is not None and not pd.isna(ni) else "—"
            out.append(f"  {ed}  营收={rev_s}  净利润={ni_s}")

    out.append("\n" + "=" * 60)
    out.append("以上为 One Pager 所需的结构化数据，可直接用于填写 SKILL.md 中的模板。")
    out.append("业务/亮点/风险的定性描述需结合公司情况自行补充。")
    out.append("=" * 60)
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_one_pager_data.py <股票代码>", file=sys.stderr)
        print("示例: python fetch_one_pager_data.py 600519.SH", file=sys.stderr)
        sys.exit(1)
    ts_code = sys.argv[1]
    print(fetch_one_pager_data(ts_code))


if __name__ == "__main__":
    main()
