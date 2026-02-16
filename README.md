# Magnificent 7 Financial Dashboard

**By Alton / Cloud Partners**

Real-time financial dashboard tracking the Magnificent 7 tech companies: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA.

## Architecture

```
FMP API → Python Script → CSV files (in repo) → Google Sheets → Tableau Public
                        → Google Sheets (optional direct push)
```

## Data Sources

All data from [Financial Modeling Prep](https://financialmodelingprep.com/) stable API:

| Dataset | Endpoint | Coverage | Free Tier |
|---------|----------|----------|-----------|
| Income Statements | `/stable/income-statement` | 5 years quarterly | ❌ Paid only |
| Balance Sheets | `/stable/balance-sheet-statement` | 5 years quarterly | ❌ Paid only |
| Financial Ratios | `/stable/ratios` | 5 years quarterly | ❌ Paid only |
| Stock Prices | `/stable/historical-price-eod/light` | Since 2021 | ✅ |
| Company Profiles | `/stable/profile` | Current | ✅ |

> **Note:** Income statements, balance sheets, and ratios require a paid FMP plan (~$19/mo Starter). The script handles this gracefully — it fetches what's available and skips the rest.

## Setup

### Local Development

```bash
pip install -r requirements.txt
export FMP_API_KEY=your_key_here
python data/fetch_financials.py
```

CSV files will be written to `data/csv/`.

### Google Sheets Integration (Optional)

1. Create a Google Cloud project
2. Enable the Google Sheets API & Google Drive API
3. Create a service account and download the JSON key
4. Create a Google Sheet and share it with the service account email
5. Set environment variables:
   - `GOOGLE_SHEETS_CREDS` — full JSON contents of the service account key
   - `GOOGLE_SHEET_ID` — the spreadsheet ID from the URL

### GitHub Actions

The workflow runs daily at 6 AM UTC. Set these repository secrets:

- `FMP_API_KEY` — Financial Modeling Prep API key
- `GOOGLE_SHEETS_CREDS` — (optional) service account JSON
- `GOOGLE_SHEET_ID` — (optional) target spreadsheet ID

### Connecting Tableau Public

**Option A — Google Sheets:** Import CSVs into Google Sheets, publish the sheet, connect Tableau Public to it.

**Option B — Direct CSV:** Use the raw GitHub URLs for the CSV files as a web data source.

## Project Structure

```
magnificent7-dashboard/
├── data/
│   ├── fetch_financials.py    # Main data pipeline
│   └── csv/                   # Generated CSV files
├── .github/workflows/
│   └── update-data.yml        # Daily automation
├── requirements.txt
└── README.md
```
