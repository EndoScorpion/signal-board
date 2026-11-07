# ProQuant Trade — MQL/Signal Ecosystem Audit
## Build 048 Linkage Map | 6 Nov 2026

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                   SIGNAL ECOSYSTEM                          │
├─────────────────┬──────────────────┬──────────────┬─────────┤
│   MQL REPO      │  Signal REPO     │signal-status │s-board  │
│ (Win Logic v2)  │ (Backtest+Anal)  │  (Library)   │(Public) │
└─────────────────┴──────────────────┴──────────────┴─────────┘
      ↑                    ↑                ↑           ↑
   HTML                 Python           Status      Messages
   Sandbox             Scripts           Docs        JSON/HTML
```

---

## 1. MQL REPOSITORY (Win Logic v2 Trading Sandbox)

### 1.1 Primary Artifact
**File**: `Signal_Live_Companion_v0.01d_build048_*.html` (~1.9 MB)
- **Role**: Single-file HTML trading sandbox
- **Engine**: Win Logic v2 (branch generator + cost model + drawdown + alerts)
- **Data**: ~1.2 MB embedded hourly bars (line with `var BARS_S=`)
- **Output**: Winners exported as `.txt` or `.js`
- **Memory**: IndexedDB (50K winners cap) + localStorage fallback

### 1.2 Build Lineage (042→048)
| Build | Date     | Feature                          | Winners | Change    |
|-------|----------|----------------------------------|---------|-----------|
| 042   | Oct 9    | WinLogicV2 + costs              | 16,748  | baseline  |
| 043   | Oct 9    | MQL families (EMA/MACD/BB/etc)  | 20,260  | +22%      |
| 044   | Oct 9    | MQL2: KC/ENV/MOM/AO/ICH/STD   | 20,260  | tiered    |
| 045   | Oct 9    | External 2h/4h series           | 20,260  | TF expand |
| 046   | Oct 9    | Per-TF seeds + IndexedDB        | 20,260  | mem opt   |
| 047   | Oct 11   | v1 port (tier 3, CNV)          | 28,368  | +40%      |
| 048   | Oct 11   | 8pt commission baseline        | 27,656  | cost adj  |

**Cost Model** (build 048):
- Commission: 8 points flat per round trip (0.01/0.001/0.0001 by price level)
- Fee, spread, swap, tax: per asset class (stock/crypto/perp/bloxwap)
- Dividend capture: stock % only

### 1.3 Code Structure

#### Templates & Sources
```
w2_module_source.html          → Source of Win Logic v2 JS engine
Signal_WinLogicV2_module_CODE_BACKUP_v0.01d_build048_*.txt  
  └─ Full JS module extraction (57.6 KB)
```

#### Exported Assets
```
signal_alerts_LIVE_v0.01d_build048_*.js (29 KB)
  ├─ Winner rules as JS functions
  ├─ Indicator code (EMA, MACD, Stoch, etc.)
  ├─ Entry/exit logic
  └─ Regime gates (ADX, vol, time)

Signal_WinLogic_v2_winners_LIVE_v0.01d_build048_*.txt (5.7 MB)
  ├─ Each line: name|entry|exit|regime|cost|drawdown|stats
  ├─ 27,656 winners at 8pt commission
  └─ Names encode: family, parameters, tier (B0=legacy, B1=043, B2=044, B3=047)
```

#### MQL EAs (100+ variants)
**Root Family**: `Strong2010b_claude_*`
```
Strong2010b_claude.mq4           → Minimal template (10 KB)
Strong2010b_claude_g4a.mq4       → Full G4A variant (130 KB) [LIVE]

b-series (b1→b44): Bracket/ladder/regime switches
  ├─ SafeChunkEA_MT4_b25/b26: Chunk-safe wrapper
  ├─ MR_RegimeSwitch_b50-b53: Market regime variants
  ├─ ChopBracket_h1a-h1d: Chop-bracket for H1
  └─ Strong2010b_claude_b20legs_g1a/g1b: Multi-leg versions

g-series (g2→g10): Generation/tier variants
  ├─ g2a-g2e: Gen 2 five-variant set
  ├─ g4a: Gen 4A (primary live)
  ├─ g5a-g5e: Gen 5 variants
  └─ g9c-g10e: Gen 9-10 latest

Scalp variants: ScalpEA_v001b → v009_H1 (9 versions, ~1 KB each)
```

#### Support Tools
```
/tools/
├─ w2_node.js              → Node harness (reproduces page engine exactly)
├─ run_page.js             → Runs page in headless Chromium, reads winners
├─ compare_runs.js         → Cross-build lineage verification
├─ make_hl_seed.js         → Hyperliquid bar seed injection
├─ make_ext_seed.js        → External bars (Webull) ingest from tool-results
├─ fetch_av.js             → Alpha Vantage key handler
├─ fetch_free_sources.py   → Yahoo/Stooq/AV fallback fetcher
└─ record_run.js           → Run snapshot recorder
```

#### Data Storage
```
/data/
├─ history/<coin>_<tf>_<stamp>.json    → [t_ms,o,h,l,c] arrays
├─ history_<stamp>.csv                  → Page History format
├─ slc_win2_hl.json                      → Hyperliquid seed (localStorage key)
├─ slc_win2_ext.json                     → External series {SYM|TF:{cls,src,b}}
└─ baseline_8pt_commission_*.md          → Run reports
```

#### Directories
```
/Experts/              → 100+ MQL EA variants (backtest library)
/patches/              → Incremental patches (not used in builds)
/backups/              → Build snapshots
/fx/                   → FX-specific strategy research
/coordination/         → Agent messaging (signal-board integration)
/handoff/              → Knowledge transfer docs
```

---

## 2. SIGNAL REPOSITORY (Backtesting & Research)

### 2.1 Core Mission
- Pull daily history for every symbol
- Re-test all win rules NET OF COSTS
- Feed survivors back into MQL HTML app
- Track results: win%, avg net %/trade, n, per-period (2015-19, 2020-22, 2023-26)

### 2.2 Data Flow
```
MQL winners (txt) 
    ↓ [convert rules]
Signal backtest scripts
    ↓ [fetch history, apply costs]
Results CSVs
    ↓ [filter survivors]
Signal/app_addons/
    ├─ addon29.html       → Cost model (JSON)
    ├─ addon36.html       → RULES snapshot
    ├─ addon37.html       → RULES snapshot
    └─ gen_kit.py + build.py
    ↓ [regenerate]
New MQL HTML base
    ↓ [embed in MQL repo]
Cycle repeats
```

### 2.3 Python Backtesting Suite

#### Fetchers
```
fetch_history.py
  ├─ Primary: Webull MCP (symbols ≤3, timespan D, 1000 bars)
  ├─ Fallback 1: Shibui Finance (call schema + patterns first, LIMIT ≤200)
  ├─ Fallback 2: yfinance (pip install yfinance)
  ├─ Fallback 3: Stooq CSV (https://stooq.com/q/d/l/?s=spy.us&i=d)
  ├─ Fallback 4: Yahoo chart API (query1.finance.yahoo.com)
  └─ Output: data/history/*.csv (source,symbol,date,o,h,l,c,vol)

fetch_free_sources.py  [MQL/tools/]
  ├─ Stooq & Yahoo (live, no key needed)
  └─ Merge to MQL/data/

tools/add_bars.py
  └─ Append bars to existing data
```

#### Backtesting Engine
```
backtest_costs.py
  ├─ Input: rules, data/, cost_model.json, hold periods
  ├─ Train: 70% of bars | Hold-out: 30% (real number reported)
  ├─ Costs: spread, slippage, regulatory fee, commission, swap, tax
  ├─ Output: results/rules_net.csv (rule | win% | avg net %/trade | n | dd)
  └─ Filter: Keep only rules (win% > 0 NET OF COSTS in ≥2 of 3 periods)
```

#### FX Scalping Research
```
fx_scalp_sim.py         → Single-rule simulator
fx_scalp_sweep.py       → Parameter sweep (9.6 KB)
hs_pattern.py           → Head-shoulders pattern miner
miner_crypto_h1.py      → Crypto H1 dip-rebound finder
```

#### Paper Trading / Simulation
```
paper_bot.py            → Simulated execution (test entry/exit signals)
paper_daily.py          → Daily symbol loop, track equity

test_star_stoch.py      → Stochastic variant tests
test_mq5_family.py      → MQ5 family compatibility

hst_to_csv.py           → MetaTrader HST to CSV converter
do_all_safe.bat         → Batch runner (3 symbols, 120ms pause, 75% mem stop)
adb_tablet_setup.bat    → ADB tablet deployment
```

### 2.4 Config & Cost Model

```
cost_model.json
{
  "stock": { "commission": 0.05%, "spread": 0.01, "fee": 0.001, ... },
  "crypto": { "commission": 0.10%, "spread": 0.10, ... },
  "perp": { "commission": 0.05%, "swap": daily, ... },
  "bloxwap": { "fee": 0.05%, ... }
}
```

```
universe.txt           → Stock symbols (SPY, QQQ, ULTY, ...)
crypto_universe.txt    → Crypto pairs (BTC, ETH, ...)
```

### 2.5 Addon Architecture
```
app_addons/
├─ addon29.html       → window.slcCost (cost_model mirror)
├─ addon36.html       → RULES array (v0.01d_build039)
├─ addon37.html       → RULES array (legacy snapshot)
├─ gen_kit.py         → Generate addon HTML from templates
└─ build.py           → Compile addons into final HTML

/analysis/             → Research notes & breakdowns
/backup/ + /backups/   → Historical snapshots
/results/              → Backtest output CSVs
/data/                 → History CSVs
```

### 2.6 Docs
```
CLAUDE.md              → Hard rules (costs, safe chunks, periods, backups)
KNOWLEDGE_BASE.md      → Domain knowledge (data sources, indicators, findings)
HUB_STATE.md           → Current project state & blockers
WORK_SUMMARY.md        → Completed work log
```

---

## 3. signal-status REPOSITORY (Status Library)

### 3.1 Purpose
Lightweight status board + library for health checks & reporting.

### 3.2 Files
```
signal_board.html      → Dashboard (24.5 KB)
  ├─ Real-time status display
  ├─ Win/loss tracking
  └─ Drawdown visualization

STATUS.md              → Current system state (uptime, last run, alerts)
REPORT.md              → Daily/weekly summary
TEST.md                → Test results & validation
DC_METHODS.md          → Desktop Commander method reference
GLOSSARY.md            → Term definitions (MQL, agent, regime, etc.)
```

### 3.3 Integration
- Reads from signal-board/board.json (public messages)
- Mirrors cost_model.json from Signal repo
- Pulls recent winners from MQL/Signal_WinLogic_v2_winners_LIVE_*.txt

---

## 4. signal-board REPOSITORY (Public Communication Hub)

### 4.1 Purpose
- Vague-only public message board (no strategy details)
- Agent-to-agent relay (Cloud Coordinator ↔ LocalThug ↔ GOON)
- Network message routing

### 4.2 Architecture

#### Message Board
```
board.json
{
  "ts": "ISO 8601 timestamp",
  "from": "CloudCoordinator | LocalThug | GOON | PhoneGOON",
  "type": "STATUS | REQUEST | ALERT",
  "msg": "vague codes only: WR/WP/WV/PF/n/DD/#StackC/#G11"
}
```

**Vague-Only Rules** (NO strategy names, legs, entry/exit, params):
- Use codes: `#StackC`, `#G11`, `WR%`, `PF`, `n`, `pts`
- Full details: private repos only
- Example: `"WR 58% +0.33% n=859 PF=1.2"` (vague, safe)
- ✗ Bad: `"EMA5/EMA20 cross, 1.5% stop, crypto H1"` (exposed)

#### HTML Pages
```
index.html    (19 KB)  → Main board UI
inbox.html    (30 KB)  → Message inbox & routing
```

#### Python Listeners & Notifiers
```
listener_security.py   → Validate message format (type, from, msg)
  ├─ Check: msg length, vague-only words
  ├─ Reject: strategy names, parameters, leg logic
  └─ Log: rejection reason

notify.py              → Post message to board.json
  ├─ Append: {ts, from, type, msg}
  ├─ Persist: board.json
  └─ Relay: alert to connected agents
```

#### Docs
```
README.md              → Board usage guide
BULLETIN.md            → Announcements
GLOSSARY.md            → Vague codes reference
TEST.md                → Board test suite
```

---

## 5. DATA FLOW & DEPENDENCIES

### 5.1 MQL → Signal Handoff
```
MQL/build048/
  ├─ Signal_WinLogicV2_module_CODE_BACKUP_build048.txt
  ├─ Signal_WinLogic_v2_winners_LIVE_build048.txt
  └─ signal_alerts_LIVE_build048.js
    ↓ [parsed by]
Signal/CLAUDE.md (PLAN.md)
  ├─ Extract winner rules
  ├─ Group by asset class
  └─ Assign to backtest jobs
    ↓ [executed by]
Signal/backtest_costs.py
  ├─ Fetch history (Webull → Shibui → yfinance → ...)
  ├─ Apply cost_model.json
  ├─ Calculate net win% per period
  └─ Output: results/rules_net.csv
    ↓ [survivors feed back to]
MQL for next cycle
```

### 5.2 Signal → signal-board Relay
```
Signal/WORK_SUMMARY.md
  ├─ Results: win%, avg net %/trade, n, periods
  └─ Vague summary
    ↓ [encoded as]
signal-board/board.json
  {"from": "Signal", "type": "STATUS", "msg": "WR 58% PF=1.2 n=859"}
    ↓ [monitored by]
signal-status/signal_board.html
  └─ Displays: latest message + color (🟢 WR>50%, 🔴 WR<30%)
```

### 5.3 Shared Assets
```
MQL/Tools/fetch_free_sources.py  ≡  Signal/fetch_history.py
  └─ Same source: Yahoo, Stooq, Alpha Vantage

cost_model.json
  ├─ Source: Signal/cost_model.json (truth)
  ├─ Mirrored: MQL builds (embedded)
  └─ Copied: signal-status/signal_board.html
```

---

## 6. EXTERNAL DATA SOURCES

### 6.1 API Keys & Credentials
```
ALPHAVANTAGE_KEY="X29IM00UJZGP1GLS"  [owner-supplied, free tier 25/day, 5/min]
  Location: .env (git-ignored) OR env var
  Fallback: Alpha Vantage tool (tools/fetch_av.js)

Webull MCP     → get_stock_bars(≤3 symbols, D, ≤1200 bars)
Shibui Finance → get_database_schema + get_query_patterns + db query
```

### 6.2 Free Public Sources
```
Stooq CSV              → https://stooq.com/q/d/l/?s=spy.us&i=d (daily/weekly/monthly)
Yahoo Finance Chart    → query1.finance.yahoo.com/v8/finance/chart/<sym>?interval=1h&range=60d
Hyperliquid (keyless)  → POST https://api.hyperliquid.xyz/info {type:"candleSnapshot", req:{coin,interval,startTime,endTime}}
```

### 6.3 Network Policy (Hosted Sandbox)
- ✗ Blocked: api.hyperliquid.xyz, api.binance.us, alphavantage.co, stooq.com, finance.yahoo.com (proxy 403)
- ✓ Workaround: Fetch on user's PC → commit data/ → run tools/

---

## 7. SHARED CODE FAMILIES

### 7.1 Strong2010b Dynasty
```
Original: strong_feb_2011_272_98.16_PatRec_11_Jul_21_commented.mq4 (30 KB)
  └─ Template: Pattern recognition + bracket logic

Signal/Strong2010b_claude.mq4 (10 KB)
  └─ Lightweight entry-exit wrapper

MQL/Experts/Strong2010b_claude_*
  ├─ b-series: Bracket/ladder regime switches
  ├─ g-series: Generation variants (g2→g10)
  ├─ Scalp variants: v001b→v009_H1
  └─ 100+ total combinations (BT library)
```

### 7.2 Indicator Ecosystem
**Built-in (Win Logic v2)**:
- EMA, MACD, BB, SAR, ADX, CCI, Stoch, RSI, AO, ICH, Keltner, Envelope, MOM, Williams%R

**Per-build (BASE, BASE2, BASE3 seeds)**:
- Tier 0 (legacy): 12 winners
- Tier 1 (043): 8 new seeds
- Tier 2 (044): 6 new seeds
- Tier 3 (047): v1 port (CNV, loss-learned)

---

## 8. BUILD AUTOMATION

### 8.1 MQL HTML Builds
```
w2_module_source.html
  ├─ Read: baseline HTML template
  ├─ Inject: 1.2 MB BARS_S (hourly history)
  ├─ Inject: seed rules (BASE, BASE2, BASE3)
  ├─ Run: Win Logic v2 engine (generate winners)
  └─ Output: Signal_Live_Companion_v0.01d_build048_*.html
```

### 8.2 Signal Addon Build
```
Signal/app_addons/
  ├─ gen_kit.py  → Generate addon HTML files
  ├─ build.py    → Compile addon files into final HTML
  └─ Output: Embed RULES[] into MQL HTML
```

### 8.3 CI/CD Hooks
```
MQL/patches/          → Pre-build validation
MQL/tools/
  ├─ node --check     → Syntax validation
  ├─ hype_bt.js       → Smoke test (Chromium headless)
  └─ compare_runs.js  → Lineage integrity check
```

---

## 9. MEMORY & STORAGE

### 9.1 MQL HTML
```
localStorage:
  └─ slc_win2        → Winners (trimmed copy, ~416 chars per winner)

IndexedDB:
  └─ slc_win2_db / store "kv" / key "slc_win2"
     └─ Full winners list (cap 50,000)

External data:
  ├─ slc_win2_hl     → Hyperliquid seed
  ├─ slc_win2_ext    → External series {SYM|TF:{cls,src,b}}
  └─ window.W2EXT    → Injected by node inject_ext.js
```

### 9.2 Storage Quota (Chromium)
- ~5M chars per origin (~416 chars/winner → ~12,000 winners baseline)
- Build 046+: 50K cap (auto-trim if browser refuses, status line reports trim)

---

## 10. KEY FINDINGS (Known Edges)

### 10.1 Crypto H1 Dip-Rebound (Gross)
- **Rule**: R1-R4 (first 4 rebounds after dip)
- **Hold**: 4 bars
- **Hard stop**: 1.5%
- **Result**: n=859, win%=58%, avg=+0.33% (at 0.04% cost, +0.25% at 0.12%)
- **Status**: Re-check with full cost model (build 048)

### 10.2 Dividend Capture
- **Gross**: Zero-sum pre-cost (price drop ≈ dividend)
- **Net**: Usually negative (costs + tax eat gain)
- **Exception**: Only pays if price recovers post-dividend

### 10.3 Daily Stocks/ETFs
- **Weak lead**: Below Bollinger & Stoch<10 in uptrend, 3d hold, blue chips
- **Status**: No consistent edge yet; needs regime refinement

---

## 11. COORDINATION & MESSAGING

### 11.1 Signal-Board Bootstrap
```
READ (no auth):
  WebFetch: https://raw.githubusercontent.com/EndoScorpion/signal-board/main/board.json

READ + WRITE (GitHub MCP):
  get_file_contents(owner=EndoScorpion, repo=signal-board, path=board.json)
  create_or_update_file(..., sha=..., branch=main)
```

### 11.2 Message Format
```json
{
  "ts": "2026-11-06T20:53:18Z",
  "from": "CloudCoordinator",
  "type": "STATUS",
  "msg": "WR 58% PF=1.2 n=859 DD=0.05 pts=8"
}
```

**Codes**:
- `WR`: Win rate (%)
- `PF`: Profit factor
- `n`: Sample size
- `DD`: Max drawdown (%)
- `pts`: Commission (points)
- `#StackC`: Stack-candlestick pattern
- `#G11`: Generation 11 variant

---

## 12. DEPLOYMENT PATHS

### 12.1 MQL to MT4
```
1. Generate/select EA from MQL/Experts/
2. Copy to: C:\Program Files\MetaTrader 4\experts\
3. Compile & attach to chart
4. Monitor: logs, equity, drawdown
```

### 12.2 Signal Analysis Cycle
```
1. User runs: python3 Signal/do_all_safe.bat
2. Fetch history (3 symbols, 120ms pause)
3. Backtest rules (cost model, net of costs)
4. Filter survivors (win% > 0, ≥2 periods)
5. Output: results/SURVIVORS.md
6. Manual: Update app_addons/ RULES
7. Rebuild: MQL HTML with new addon
8. Commit & test
```

### 12.3 Status Board Update
```
1. Signal agent: Compute results
2. Encode as vague message
3. Append to signal-board/board.json
4. signal-status reads board.json
5. signal_board.html refreshes display
6. Alert color: 🟢 (win%>50%) or 🔴 (win%<30%)
```

---

## 13. REPO SYNC CHECKLIST

### 13.1 Before Push to MQL
- [ ] Build number bumped (title, module banners, filenames)
- [ ] Timestamp updated (UTC, ET format)
- [ ] Code backup .txt added
- [ ] Winners .txt added (if generation happened)
- [ ] JS export updated
- [ ] node --check passed
- [ ] Chromium headless smoke test passed
- [ ] Compare-runs lineage verified

### 13.2 Before Push to Signal
- [ ] History CSVs complete (fetch_history.py succeeded)
- [ ] Backtest CSVs generated (backtest_costs.py clean exit)
- [ ] Survivors filtered (win% > 0, ≥2 periods)
- [ ] SURVIVORS.md updated
- [ ] cost_model.json unchanged (golden rule)
- [ ] Safe chunk limits honored (≤3 symbols, 120ms, 75% mem)

### 13.3 Before Push to signal-board
- [ ] Message format valid (vague-only, no strategy names)
- [ ] board.json syntax checked
- [ ] listener_security.py validation passed
- [ ] No sensitive data in message
- [ ] Previous message not duplicated

---

## 14. DEPENDENCY GRAPH

```
MQL/w2_module_source.html
  ├─ Reads: BARS_S (embedded history)
  ├─ Runs: Win Logic v2 engine
  ├─ Outputs: Winners → localStorage/IndexedDB
  └─ Exports: .txt + .js → Signal/

Signal/backtest_costs.py
  ├─ Inputs: Winners, fetch_history.py, cost_model.json
  ├─ Verifies: net % > 0 across periods
  └─ Outputs: results/SURVIVORS.md

Signal/app_addons/build.py
  ├─ Inputs: SURVIVORS.md
  ├─ Updates: addon36.html RULES
  └─ Generates: new MQL HTML base

MQL/ (new cycle)
  ├─ Embeds: addon RULES
  ├─ Generates: new winners
  └─ → Signal/ (feedback loop)

signal-board/board.json
  ├─ Inputs: Signal/WORK_SUMMARY.md (vague summary)
  └─ Monitored by: signal-status/signal_board.html

signal-status/signal_board.html
  ├─ Reads: board.json
  ├─ Displays: Real-time status
  └─ Color: Green/Red based on latest message
```

---

## 15. CRITICAL CONSTRAINTS

### Hard Rules (CLAUDE.md)
1. **Real data only** — no synthetic/simulated bars
2. **Never remove/re-render** existing visuals — append only
3. **ALL costs** — commission, fee, spread, swap, tax (per component + totals)
4. **Train 70% / Hold-out 30%** — report hold-out as real number
5. **Build bump on every change** — title, module banners, filenames
6. **Max 3 backups** per version
7. **Time-slice** Chrome runs ≤14 ms, gate on >60% heap
8. **Network blocks** — Hyperliquid, Binance, AV, Stooq in sandbox (fetch on PC)

### Workflow Constraints
1. Grep/awk for locating, never read whole files (BARS_S line alone is 1.2 MB)
2. Patch with Python read-replace (assert count==1)
3. node --check validation mandatory
4. Smoke test in headless Chromium (pageerror must be empty)
5. Deliver HTML + .txt backup
6. Budget token/credit usage

---

## 16. FILE LOCATION REFERENCE

### MQL Repo (main branch)
```
Root:
  - CLAUDE.md, PLAN.md, README.md
  - *.html (Signal_Live_Companion_v0.01d_build*)
  - *.txt (code backups, winners)
  - *.js (signal_alerts_LIVE)
  - *.mq4 (Strong2010b, root EA)
  - fetch_history.js, hype_bt.js, inject_*.js
  
Subdirs:
  - /Experts/        (100+ MQL EA variants)
  - /tools/          (w2_node.js, run_page.js, compare_runs.js, etc.)
  - /data/           (history JSON/CSV)
  - /fx/             (FX research)
  - /patches/        (incremental patches)
  - /backups/        (build snapshots)
  - /coordination/   (agent messages)
  - /handoff/        (knowledge transfer)
```

### Signal Repo (main branch)
```
Root:
  - CLAUDE.md, KNOWLEDGE_BASE.md, HUB_STATE.md, PLAN.md, WORK_SUMMARY.md
  - *.py (fetch_history, backtest_costs, fx_*, paper_*, hs_pattern, etc.)
  - *.mq4 (Strong2010b_claude variants)
  - *.html (signal_paper_lab)
  - cost_model.json, universe.txt, crypto_universe.txt
  - do_all_safe.bat, adb_tablet_setup.bat
  
Subdirs:
  - /app_addons/     (addon29/36/37.html, gen_kit.py, build.py)
  - /analysis/       (research notes)
  - /data/           (history CSVs)
  - /tools/          (add_bars.py, fetch_free_sources.py)
  - /results/        (backtest output, SURVIVORS.md)
  - /backup/, /backups/  (snapshots)
  - /fx/             (FX strategy research)
  - /coordination/   (agent messages)
  - /patches/        (incremental updates)
```

### signal-status Repo (main branch)
```
Root:
  - signal_board.html
  - STATUS.md, REPORT.md, TEST.md
  - DC_METHODS.md, GLOSSARY.md
  - README.md, NOTICE.txt
```

### signal-board Repo (main branch)
```
Root:
  - board.json (message history)
  - index.html, inbox.html
  - listener_security.py, notify.py
  - BULLETIN.md, GLOSSARY.md, TEST.md, REPORT.md, README.md
```

---

## END AUDIT

**Generated**: 2026-11-06 20:53:18 UTC
**Build**: MQL 048, Signal 039 baseline
**Scope**: MQL + Signal + signal-status + signal-board linking
**Status**: Ready for integration & CI/CD setup

