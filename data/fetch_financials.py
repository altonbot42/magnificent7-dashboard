"""
Magnificent 7 Financial Data Pipeline
- FMP API: stock prices (daily) and company profiles (free tier)
- yfinance: quarterly financial statements + calculated ratios (free)

Author: Alton / Cloud Partners
"""

import os
import csv
import json
import time
import logging
import requests
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("FMP_API_KEY", "HVp7rw4zU1qyxdtbUoXJjCrbY0WxT3fT")
BASE_URL = "https://financialmodelingprep.com/stable"
LEGACY_URL = "https://financialmodelingprep.com/api/v3"
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
OUTPUT_DIR = Path(__file__).parent / "csv"
RATE_LIMIT_DELAY = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FMP helpers (stock prices + company profiles only)
# ---------------------------------------------------------------------------

def fetch(endpoint, params=None, use_legacy=False):
    params = params or {}
    params["apikey"] = API_KEY
    base = LEGACY_URL if use_legacy else BASE_URL
    url = f"{base}/{endpoint}"
    log.info(f"GET {url}")
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code == 402 and not use_legacy:
        log.info("  → 402, trying legacy v3...")
        return fetch(endpoint, {k: v for k, v in params.items() if k != "apikey"}, use_legacy=True)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "value" in data:
        return data["value"]
    if isinstance(data, list):
        return data
    return [data] if data else []


def fetch_for_all(endpoint, extra_params=None):
    all_rows = []
    for symbol in SYMBOLS:
        time.sleep(RATE_LIMIT_DELAY)
        try:
            params = {"symbol": symbol, **(extra_params or {})}
            rows = fetch(endpoint, params)
            for r in rows:
                r.setdefault("symbol", symbol)
            all_rows.extend(rows)
            log.info(f"  {symbol}: {len(rows)} rows")
        except Exception as e:
            log.error(f"  {symbol}: FAILED — {e}")
    return all_rows


def fetch_stock_prices():
    return fetch_for_all("historical-price-eod/light", {"from": "2021-01-01"})


def fetch_company_profiles():
    return fetch_for_all("profile")

# ---------------------------------------------------------------------------
# yfinance: financial statements
# ---------------------------------------------------------------------------

def _df_to_rows(df, symbol):
    """Convert a yfinance financial DataFrame (columns=dates, rows=items) to list of dicts."""
    if df is None or df.empty:
        return []
    rows = []
    for col_date in df.columns:
        row = {"symbol": symbol, "date": col_date.strftime("%Y-%m-%d")}
        for item in df.index:
            # Clean column name: replace spaces/special chars
            clean = str(item).replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
            val = df.loc[item, col_date]
            row[clean] = None if pd.isna(val) else val
        rows.append(row)
    return rows


def fetch_yfinance_financials():
    """Fetch quarterly income statements, balance sheets, cash flow from yfinance."""
    all_income = []
    all_balance = []
    all_cashflow = []

    for symbol in SYMBOLS:
        log.info(f"  yfinance: {symbol}")
        try:
            tk = yf.Ticker(symbol)
            all_income.extend(_df_to_rows(tk.quarterly_income_stmt, symbol))
            all_balance.extend(_df_to_rows(tk.quarterly_balance_sheet, symbol))
            all_cashflow.extend(_df_to_rows(tk.quarterly_cashflow, symbol))
        except Exception as e:
            log.error(f"  {symbol}: yfinance FAILED — {e}")

    return all_income, all_balance, all_cashflow


def build_income_csv(raw_income):
    """Normalize income statement rows to consistent columns."""
    rows = []
    for r in raw_income:
        rows.append({
            "symbol": r.get("symbol"),
            "date": r.get("date"),
            "revenue": r.get("Total_Revenue"),
            "cost_of_revenue": r.get("Cost_Of_Revenue"),
            "gross_profit": r.get("Gross_Profit"),
            "operating_income": r.get("Operating_Income"),
            "net_income": r.get("Net_Income"),
            "ebitda": r.get("EBITDA"),
            "basic_eps": r.get("Basic_EPS"),
            "diluted_eps": r.get("Diluted_EPS"),
            "operating_expense": r.get("Operating_Expense"),
            "research_and_development": r.get("Research_And_Development"),
            "interest_expense": r.get("Interest_Expense"),
            "tax_provision": r.get("Tax_Provision"),
        })
    return rows


def build_balance_csv(raw_balance):
    """Normalize balance sheet rows."""
    rows = []
    for r in raw_balance:
        rows.append({
            "symbol": r.get("symbol"),
            "date": r.get("date"),
            "total_assets": r.get("Total_Assets"),
            "total_liabilities": r.get("Total_Liabilities_Net_Minority_Interest"),
            "stockholders_equity": r.get("Stockholders_Equity") or r.get("Total_Equity_Gross_Minority_Interest"),
            "cash_and_equivalents": r.get("Cash_And_Cash_Equivalents"),
            "total_debt": r.get("Total_Debt"),
            "net_debt": r.get("Net_Debt"),
            "current_assets": r.get("Current_Assets"),
            "current_liabilities": r.get("Current_Liabilities"),
            "long_term_debt": r.get("Long_Term_Debt"),
            "retained_earnings": r.get("Retained_Earnings"),
            "common_stock_shares_outstanding": r.get("Ordinary_Shares_Number") or r.get("Share_Issued"),
        })
    return rows


def build_ratios_csv(income_rows, balance_rows, stock_prices):
    """Calculate financial ratios from income + balance sheet data."""
    # Build a price lookup: symbol -> latest close (simple approach)
    price_map = {}
    for p in stock_prices:
        sym = p.get("symbol")
        if sym and sym not in price_map:
            price_map[sym] = p.get("price") or p.get("close") or p.get("adjClose")

    # Index balance sheet by (symbol, date)
    bs_map = {}
    for b in balance_rows:
        bs_map[(b["symbol"], b["date"])] = b

    rows = []
    for inc in income_rows:
        sym, dt = inc["symbol"], inc["date"]
        bs = bs_map.get((sym, dt), {})
        revenue = inc.get("revenue")
        gross = inc.get("gross_profit")
        op_inc = inc.get("operating_income")
        net_inc = inc.get("net_income")
        equity = bs.get("stockholders_equity")
        assets = bs.get("total_assets")
        debt = bs.get("total_debt")
        cur_assets = bs.get("current_assets")
        cur_liab = bs.get("current_liabilities")
        eps = inc.get("diluted_eps")
        price = price_map.get(sym)
        shares = bs.get("common_stock_shares_outstanding")

        def safe_div(a, b):
            if a is not None and b is not None and b != 0:
                return round(a / b, 4)
            return None

        rows.append({
            "symbol": sym,
            "date": dt,
            "gross_margin": safe_div(gross, revenue),
            "operating_margin": safe_div(op_inc, revenue),
            "net_margin": safe_div(net_inc, revenue),
            "pe_ratio": safe_div(price, eps) if eps and eps > 0 else None,
            "eps_diluted": eps,
            "debt_to_equity": safe_div(debt, equity),
            "current_ratio": safe_div(cur_assets, cur_liab),
            "roe": safe_div(net_inc, equity),
            "roa": safe_div(net_inc, assets),
            "revenue": revenue,
            "net_income": net_inc,
            "total_debt": debt,
            "stockholders_equity": equity,
            "price": price,
        })
    return rows

# ---------------------------------------------------------------------------
# CSV writing
# ---------------------------------------------------------------------------

def write_csv(name, rows):
    if not rows:
        log.warning(f"No data for {name}, skipping.")
        return None
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.csv"
    headers = list(dict.fromkeys(k for row in rows for k in row.keys()))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"Wrote {len(rows)} rows → {path}")
    return path

# ---------------------------------------------------------------------------
# Google Sheets (optional)
# ---------------------------------------------------------------------------

def update_google_sheets(datasets):
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not creds_json or not sheet_id:
        log.info("Google Sheets credentials not set — skipping.")
        return
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        log.warning("gspread not installed — skipping Sheets.")
        return
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)
    for sheet_name, rows in datasets.items():
        if not rows:
            continue
        headers = list(dict.fromkeys(k for row in rows for k in row.keys()))
        values = [headers] + [[row.get(h, "") for h in headers] for row in rows]
        try:
            ws = spreadsheet.worksheet(sheet_name)
            ws.clear()
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=sheet_name, rows=len(values), cols=len(headers))
        ws.update(range_name="A1", values=values)
        log.info(f"Sheets: updated '{sheet_name}' with {len(rows)} rows")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 60)
    log.info("Magnificent 7 Financial Data Pipeline")
    log.info(f"Run time: {datetime.now().isoformat()}")
    log.info("=" * 60)

    datasets = {}

    # --- FMP: stock prices & company profiles (free tier) ---
    log.info("\n📈 Fetching stock prices (FMP)...")
    datasets["stock_prices"] = fetch_stock_prices()

    log.info("\n🏢 Fetching company profiles (FMP)...")
    datasets["company_info"] = fetch_company_profiles()

    # --- yfinance: financial statements ---
    log.info("\n📊 Fetching financial statements (yfinance)...")
    raw_income, raw_balance, raw_cashflow = fetch_yfinance_financials()

    income_rows = build_income_csv(raw_income)
    balance_rows = build_balance_csv(raw_balance)
    ratios_rows = build_ratios_csv(income_rows, balance_rows, datasets["stock_prices"])

    datasets["income_statement"] = income_rows
    datasets["balance_sheet"] = balance_rows
    datasets["ratios"] = ratios_rows

    # --- Write CSVs ---
    log.info("\n💾 Writing CSV files...")
    for name, rows in datasets.items():
        write_csv(name, rows)

    # --- Optional: Google Sheets ---
    log.info("\n☁️  Updating Google Sheets...")
    update_google_sheets(datasets)

    # --- Summary ---
    log.info("\n✅ Pipeline complete!")
    for name, rows in datasets.items():
        log.info(f"  {name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
