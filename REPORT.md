<!-- Copyright 2026 Nasif Hossain | endoscorpion@gmail.com | All rights reserved. -->
# Win Logic Report — Cycle 39 (2026-10-20)
_Updated: 2026-10-20 — ECN pts (5-digit; $0.10/pt at 0.1 lot). Cost deducted. Past results ≠ advice._

---

## Leg 1 (#G11)

| Period | n | WR% | PF | Avg WP/t (pts) | PF@3×cost | Max DD |
|---|---|---|---|---|---|---|
| IS 2024-26 | 34 | 71% | 2.84 | +81 | 2.31 | $60 |
| OOS 2020-23 | 36 | 75% | 5.19 | +177 | 4.46 | $45 |
| ALL 2020-26 | 70 | ~73% | ~3.8 | ~+131 | — | $60 |

Per-year PF (IS): 2024: 4.02 / 2025: 1.13 / 2026: 15.45  
Per-year PF (OOS): 2020: 3.27 / 2021: 13.33 / 2022: 18.90 / 2023: 1.74  
WP/w ≈ +0.5 pts · WP/m ≈ +2.3 pts · WP/yr est. ~+$27 (0.1 lot)  
**Status: ✅ CLEAN — 6/6 years positive**

---

## Leg 2

| Period | n | WR% | PF | Avg WP/t (pts) | PF@3×cost | Max DD |
|---|---|---|---|---|---|---|
| IS 2024-26 | 57 | 56% | 2.53 | +44 | 1.78 | $36 |
| OOS 2020-23 | 67 | 61% | 1.77 | +67 | 1.54 | $110 |
| ALL 2020-26 | 124 | ~59% | ~2.1 | +57 | — | $110 |

Per-year PF (IS): 2024: 2.06 / 2025: 3.73 / 2026: 1.57  
Per-year PF (OOS): 2020: 2.18 / 2021: 1.41 / 2022: 2.17 / 2023: 1.21  
**Status: ⚠️ Weakest leg — OOS PF 1.77 marginal; PF@3×cost 1.54. In #StackC at reduced size.**

---

## Leg 3 (#T82)

| Period | n | WR% | PF | Avg WP/t (pts) | PF@3×cost | Max DD |
|---|---|---|---|---|---|---|
| IS 2024-26 | 28 | 57% | 3.56 | +55 | 2.36 | $31 |
| OOS 2020-23 | 35 | 60% | 2.21 | +100 | 1.95 | $107 |
| ALL 2020-26 | 63 | ~59% | ~2.7 | +80 | — | $107 |

Per-year PF (IS): 2024: 21.93 / 2025: 4.44 / 2026: 1.00  
Per-year PF (OOS): 2020: 0.84 / 2021: 0.62 / 2022: 2.93 / 2023: 4.81  
**Status: ⚠️ IS n=28 (<30). 2026 PF=1.00. OOS 2020–21 PF <1.0 — inconsistent across periods.**

---

## Leg 4a (#n016)

| Period | n | WR% | PF | Avg WP/t (pts) | PF@3×cost | Max DD |
|---|---|---|---|---|---|---|
| IS 2024-26 | 45 | 67% | 2.67 | +90 | 2.25 | $59 |
| OOS 2020-23 | 44 | 70% | 3.07 | +126 | 2.67 | $68 |
| ALL 2020-26 | 89 | ~68% | ~2.9 | +108 | — | $68 |

Per-year PF (IS): 2024: 1.49 / 2025: 2.93 / 2026: 4.92  
Per-year PF (OOS): 2020: 2.11 / 2021: 3.31 / 2022: 9.59 / 2023: 1.61  
**Status: ✅ CLEAN — 6/6 years positive.**

---

## Leg 4b (#n021 — #StackC variant)

Stats inferred from stack differentials (no standalone run file found; MT4 confirm queued).  
IS PF ~3.11 / OOS PF ~4.12 (estimate). Replaces Leg 4a in #StackC.  
**Status: ⚠️ Needs standalone MT4 confirmation (nomem6_021 queued, relay empty).**

---

## #StackA (Legs 1+2+3+4a, full size)

| Period | n | WR% | PF | Net $ | PF@3×cost | Max DD |
|---|---|---|---|---|---|---|
| IS 2024-26 | 164 | 62% | 2.76 | +$1,090 | 2.14 | $100 |
| OOS 2020-23 | 182 | 66% | 2.54 | +$1,989 | 2.22 | $122 |
| ALL 2020-26 | 346 | 64% | 2.61 | +$3,079 | 2.19 | $122 |

Per-year PF (IS): 2024: 2.70 / 2025: 2.51 / 2026: 3.28  
Per-year PF (OOS): 2020: 2.25 / 2021: 2.20 / 2022: 3.47 / 2023: 1.79  
WP/w ≈ +12.7 pts · WP/m ≈ +54 pts · WP/yr ≈ +$440 (0.1 lot)  
**Status: ✅ CLEAN — 7/7 years positive.**

---

## #StackC — BEST (Legs 1+2+3+4b, Leg 2 reduced size, #NFP filter)

| Period | n | WR% | PF | Net $ | Max DD |
|---|---|---|---|---|---|
| IS 2024-26 | 152 | 62% | 2.97 | +$859 | $76 |
| OOS 2020-23 | 175 | 66% | 2.94 | +$1,785 | $92 |
| ALL 2020-26 | 327 | ~64% | ~2.96 | +$2,644 | $92 |

Per-year net $ (IS): +$326 / +$269 / +$265  
Per-year net $ (OOS): +$449 / +$300 / +$870 / +$166  
Bootstrap 2000×: PF p5 1.94 IS / 2.09 OOS · P(net<0)=0% · DD p95 $133 IS / $177 OOS  
**Status: ✅ BEST STACK — 7/7 years positive. Lower DD than #StackA.**

---

## #AsiLon-v1 (#v2.3 / #Fade)

| Period | n | WR% | PF | Source |
|---|---|---|---|---|
| IS 2024-26 | 32 | 78% | 6.29 | Single venue |

**Status: ⚠️ No independent OOS dataset tested. n=32 borderline. Not in any stack.**

---

## #AsiLon-v2 (#v2.4 candidate)

| Period | n | PF | Source |
|---|---|---|---|
| IS 2024-26 | 19 | 10.33 | Single venue |

**Status: ❌ REJECTED — n=19 (<30 minimum). Candidate only; needs more data.**

---

## Summary Table

| Branch | n(IS) | WR%(IS) | PF(IS) | n(OOS) | WR%(OOS) | PF(OOS) | n(ALL) | PF(ALL) | Max DD | W%/t | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Leg 1 (#G11) | 34 | 71% | 2.84 | 36 | 75% | 5.19 | 70 | ~3.8 | $60 | 73% | ✅ |
| Leg 2 | 57 | 56% | 2.53 | 67 | 61% | 1.77 | 124 | ~2.1 | $110 | 59% | ⚠️ |
| Leg 3 (#T82) | 28 | 57% | 3.56 | 35 | 60% | 2.21 | 63 | ~2.7 | $107 | 59% | ⚠️ |
| Leg 4a (#n016) | 45 | 67% | 2.67 | 44 | 70% | 3.07 | 89 | ~2.9 | $68 | 68% | ✅ |
| Leg 4b (#n021) | ~45 | ~67% | ~3.11 | ~44 | ~70% | ~4.12 | ~89 | ~3.5 | — | ~68% | ⚠️ pending |
| #StackA | 164 | 62% | 2.76 | 182 | 66% | 2.54 | 346 | 2.61 | $122 | 64% | ✅ |
| #StackC | 152 | 62% | 2.97 | 175 | 66% | 2.94 | 327 | ~2.96 | $92 | 64% | ✅ BEST |
| #AsiLon-v1 (#v2.3) | 32 | 78% | 6.29 | — | — | — | — | — | — | 78% | ⚠️ |
| #AsiLon-v2 (#v2.4) | 19 | — | 10.33 | — | — | — | — | — | — | — | ❌ |

---

## Flags

1. Leg 4b (#n021) — no standalone run file; stats inferred from stack differential; MT4 confirm queued (relay empty 22:00Z Oct 20)
2. #AsiLon-v2 — n=19, rejected
3. #AsiLon-v1 (#v2.3) — no independent OOS; venue-only data
4. Leg 3 (#T82) — IS n=28 (<30); OOS 2020-21 PF <1.0; inconsistent across periods
5. MT4 confirmations (nomem6_004–029) all pending; theory_results.json empty at 22:00Z Oct 20

_Source: SURVIVORS_nomem6_20261020.txt · IS = ECN live data 2024-26 · OOS = third-party H1 2020-23_
