# Magnificent 7 Financial Dashboard

**Project Type:** Tableau Demo Portfolio for Consulting Business
**Status:** Planning Complete — Ready to Build
**Created:** 2026-02-12

## Purpose

Notla runs a Tableau consulting side business. Clients often ask for demos but all prior work is confidential. This project creates a public demo portfolio using publicly available financial data from the Magnificent 7 tech companies.

## The Magnificent 7

| Company | Ticker | Story Angle |
|---------|--------|-------------|
| Apple | AAPL | Services growth, cash machine |
| Microsoft | MSFT | Cloud + AI integration |
| Alphabet | GOOGL | Ad revenue vs AI investment |
| Amazon | AMZN | AWS margins vs retail |
| Nvidia | NVDA | AI chip dominance |
| Meta | META | Efficiency turnaround |
| Tesla | TSLA | Margin compression, volume vs profit |

## Tech Stack

- **Visualization:** Tableau Public (free, easy to share)
- **Data Source:** Financial Modeling Prep API (free tier: 250 calls/day)
- **Data Bridge:** Google Sheets (Tableau Public can connect + auto-refresh)
- **Automation:** GitHub Actions (free, runs Python script on schedule)
- **Update Frequency:** Daily (catches new data within 24-48 hours of earnings)

## Architecture

```
Financial Modeling Prep API
           │
           ▼
   Python Script (GitHub Actions - daily cron)
           │
           ▼
     Google Sheets
           │
           ▼
    Tableau Public (auto-refresh every 24h)
           │
           ▼
   Embedded on Portfolio Website
```

## Dashboard Structure

### Navigation Flow

```
┌─────────────────────────────────────────────┐
│              HOME / LANDING                  │
│                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│   │ Company │  │ Compare │  │ Health  │    │
│   │  Dive   │  │ Leaders │  │  Score  │    │
│   └────┬────┘  └────┬────┘  └────┬────┘    │
└────────┼────────────┼────────────┼──────────┘
         ▼            ▼            ▼
      Detail       Detail       Detail
```

### Page 1: Home / Landing Dashboard

**Purpose:** First impression, navigation hub, "wow factor"

**Elements:**
- Clean header with branding
- Tagline: "Magnificent 7 Financial Analytics — Tableau Consulting by [Name]"
- 7 clickable tiles (one per company) OR 3-4 section tiles
- Mini KPI bar (total market cap tracked, etc.)
- Subtle hover effects to show interactivity

**Vibe:** Apple-clean, not cluttered. Shows design sense.

### Page 2: Company Deep-Dive (Template)

**Purpose:** Detailed financial analysis for ONE company at a time

**Elements:**
- Company selector dropdown (switch between all 7)
- Header: Company logo, name, sector, current stock price
- Row 1: Revenue trend (line chart, 5 years quarterly) + YoY growth %
- Row 2: Profitability — Gross margin, operating margin, net margin
- Row 3: Key metrics cards — P/E ratio, EPS, debt-to-equity, current ratio
- Row 4: Mini balance sheet — assets vs liabilities
- Navigation: "Back to Home" button

**Why this impresses:** Single template, parameter-driven = efficient design

### Page 3: Competitive Comparison

**Purpose:** Side-by-side analysis — "who's winning"

**Elements:**
- Company multi-select (pick 2-7 companies)
- Metric selector (Revenue, Net Income, Margin %, Growth Rate)
- Overlay line chart showing selected companies
- Rank table: sortable, latest quarter stats
- Insight callout: "Nvidia leads in growth at +X% YoY"
- Navigation: Back to Home

**Why this impresses:** Flexible, user-driven analytics

### Page 4: Financial Health Scorecard

**Purpose:** Executive summary — quick health check across all 7

**Elements:**
- KPI tiles for each company (7 tiles in grid)
  - Company name/logo
  - Health score (composite)
  - RAG indicator (green/yellow/red)
  - Sparkline of stock trend
- Click tile → detail panel with ratios
- Navigation: Back to Home

**Why this impresses:** Synthesizes complex data into exec-friendly format

### Page 5: About / Contact (Optional)

**Purpose:** Convert viewers into leads

**Elements:**
- Brief bio
- Services offered
- Contact info/CTA
- "Like what you see? Let's talk."

## Data Structure (Google Sheets)

| Sheet | Contents |
|-------|----------|
| `income_statement` | Revenue, gross profit, operating income, net income (quarterly, all 7 companies) |
| `balance_sheet` | Assets, liabilities, equity, cash, debt (quarterly) |
| `ratios` | P/E, EPS, margins, debt-to-equity, current ratio |
| `stock_prices` | Daily/weekly close price |
| `company_info` | Name, ticker, sector, logo URL, description |

## Timeline Estimate

| Phase | Hours |
|-------|-------|
| Data Pipeline (API → Sheets) | 3-4 |
| Dashboard Development | 6-8 |
| Polish & Storytelling | 2-3 |
| Publishing & Website | 2-3 |
| **Total** | **13-18 hours** |

## Files To Create

- `data/fetch_financials.py` — Python script to pull API data
- `.github/workflows/update-data.yml` — GitHub Action schedule
- `README.md` — Setup instructions
- Google Sheet (created manually, linked here once done)
- Tableau Public workbook (link here once published)

## Next Steps

1. [ ] Sign up for Financial Modeling Prep API key (free)
2. [ ] Create Google Sheet with proper structure
3. [ ] Build Python script to fetch data
4. [ ] Set up GitHub repo + Actions for scheduling
5. [ ] Test data pipeline end-to-end
6. [ ] Build dashboards in Tableau Public
7. [ ] Embed on portfolio site

## Notes

- All 7 companies are tech — if clients ask about other industries, offer custom dashboards
- "Magnificent 7" is a recognized finance term — good marketing hook
- Tableau Public auto-refreshes from Google Sheets every 24 hours
- Financial Modeling Prep free tier (250 calls/day) is plenty for 7 companies × 4 endpoints = 28 calls
