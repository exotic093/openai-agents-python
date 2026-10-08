# Gold Analysis Brain — XAUUSD Top-Down Method (Extracted)

Knowledge file for a gold-analysis and position-monitoring bot. It restates the method documented in the
owner's two gold skill files and adds no new strategy. Where the sources are silent, it says so.
Extracted 2026-10-08.

---

## 0. How to use this file

### Labels

| Label | Meaning | What the bot does |
|---|---|---|
| DOCUMENTED | Stated in a source file (source and line given) | Apply as written |
| INFERRED | Not stated, but follows from the sources (basis given) | Apply; call it an interpretation if asked |
| MISSING | Not defined anywhere in the sources | Report the gap; never fill it with an own rule |
| PROPOSED | A suggestion, not part of the method | Ignore unless the owner adopts it |

### Sources

Line numbers refer to these exact file versions. "GSE 37" means line 37 of the GSE file.

| Key | File | Updated | sha256 prefix | Content |
|---|---|---|---|---|
| GSE | `gold-scalp-engine/SKILL.md` | 2026-10-06 | `a2a914b8ea51` | Analysis doctrine; REACH engine rules |
| XER | `xau-engine-run/SKILL.md` | 2026-10-07 | `b80be1323c62` | TD-1007 engine method; operating runbook |

### Two position engines

Both files share one analysis doctrine but describe two different engines for building a position.

- **TD** — the TD-1007 method, computed by `tools/xau_td.py` (XER 10–21).
- **REACH** — computed by `tools/xau_reach.py`, helper v2.x (GSE 12–50).

**Which engine is canonical is MISSING.** GSE says every order plan comes from REACH (GSE 12–13). XER,
updated a day later, says TD decides trend, zones, prices, expiry and whether a position exists (XER 10).
The deployment must name one engine. Neither helper script was present in the inspected workspace.

### The governing rule — DOCUMENTED

Order plans come only from the configured engine's helper and are published exactly as printed. Without the
helper, the bot gives analysis only and never builds an entry, stop or target by hand, whatever the wording
of the request (GSE 12–15, 22–27, 79; XER 10, 64). This file explains the helpers' rules so the bot can
explain, sanity-check and monitor a plan. It does not authorise hand-built plans.

---

## 1. Purpose and intended thesis

**Purpose — DOCUMENTED.**
- Read XAUUSD top-down "like a desk, not like a retail indicator stack" (GSE 8).
- Deliver ONE position: the trend, the zone price should respect, a pending order in that zone, a stop
  beyond the structure guarding it, TP1/TP2 at the next real support/resistance, a validity window, and the
  next zone if price breaks through (XER 8). Otherwise an explicit NO PLAN.
- Planning only: never place, modify or cancel a broker order (XER 8). The user sizes and executes. Claim
  certainty about structure, never about outcome (GSE 68–69).

**Owner's intended thesis.** This is the design target; not every point is implemented in the sources.
Coverage per point is in `GOLD_ANALYSIS_SOURCES_AND_GAPS.md` §4.

1. Top-down: broader trend, intraday direction, trending / ranging / transitioning.
2. Reaction zones and how price behaves around them.
3. Lower timeframes for a realistic scalping entry.
4. Fundamentals, news and observed reactions for continuation, reversal and event risk.
5. Entry, stop and targets from market structure, not arbitrary prices or an attractive ratio.
6. The best available conditional or confirmed setup; never force a position.
7. Monitor an issued setup or verified position against its original thesis: normal fluctuation vs
   deterioration vs invalidation.
8. Replace only with a separately supported new setup; a failed long is not automatically a short; one
   open position at a time.

---

## 2. Required inputs

A missing, stale or unverified input is reported by name. It is never estimated, recalled from memory, or
taken from news.

| Input | Used for | Check | Label |
|---|---|---|---|
| Live XAUUSD bid, ask, timestamp, feed name | Spread, distances, the plan quote | Quote sanity (below) | DOCUMENTED (GSE 33–34, 232; XER 76–95) |
| Completed candles: D1 (rolls 17:00 New York), H4, H1; M15 and M5 for REACH | Regime gate, structure, levels | Completed bars only (GSE 32); enough history for 480 H1 ATR values and 50 D1 closes | DOCUMENTED (GSE 28–32, 37–45); history length INFERRED from the formulas |
| Helper output for the configured engine: `status`, `plan`, `manage` | Direction, prices, ACTIVE state | Helper present; TD helper sha256 starts `15bf0d11` (XER 25); data through the last finished hour (GSE 34) | DOCUMENTED (GSE 75–78; XER 25, 49, 67) |
| Tier-1 US event calendar, New York wall-clock times | Blackouts, plan validity | Covers the plan window; built from two sources; keep events both agree on; keep single-source Tier-1 items marked "(one source)" | DOCUMENTED (GSE 81, 199–203; XER 70) |
| Market state: open, daily break, reopen, holiday | Hard blocks | Closed or holiday → no plan | DOCUMENTED (GSE 191–192, 203; XER 67) |
| Current time, time-zone aware | Sessions, cutoffs | Compute every boundary from exchange-local time with DST-aware conversion, never hardcoded (GSE 177); report times in GST, Dubai UTC+4 (GSE 175) | DOCUMENTED |
| State of any working plan or open position | One-at-a-time rule, monitoring | Engine journal `journal/xau_plans.jsonl` | DOCUMENTED (GSE 49–50, 257) |
| *Optional:* news drivers (one search) | Context and the AGAINST line only | Never a source of prices or direction | DOCUMENTED (GSE 33; XER 71) |
| *Optional:* XAGUSD, GC futures, DXY, XAUEUR/XAUGBP, US10Y real yield/TIP, XPTUSD/HG copper | SMT and macro context | Same swing window; verified swing times and prices | DOCUMENTED (GSE 126–140) |
| *Optional:* CME GC front-month volume and delta; tick-volume RVOL | Volume context | Spot tick volume is not real volume; without GC volume, label volume conclusions "proxy" | DOCUMENTED (GSE 61–63, 163–169) |

**Quote sanity — DOCUMENTED in the TD runbook (XER 95).** The quote is usable only if all three hold:

1. |bid − helper's last bid| < 60
2. 0 < ask − bid ≤ 3
3. |(bid + ask) / 2 − last candle close| ≤ max(1.5, 2 × spread)

A null quote is reloaded once. A second sanity failure gives `NO TRADE — quote and candles disagree`.
Incomplete chart minutes after one retry give `NO TRADE — chart minutes incomplete` (XER 114).

---

## 3. The method in five stages

Run the stages in order: "never reorder" (GSE 85–87). Only the Stage 1 blocks and the Stage 2 regime and
direction rules can stop a plan. Everything else is context.

### Stage 1 — Verify inputs and apply hard blocks

If any block holds, the answer is NO PLAN (NO TRADE in the TD runbook) with the reason. Analysis may still
be given, labelled ANALYSIS ONLY (GSE 79).

| Block | Rule | Label |
|---|---|---|
| No helper | Helper missing or failing → no order plan; say "no order plan without the helper" | DOCUMENTED (GSE 22–27, 59; XER 64) |
| Tier-1 event | 15 min before to 15 min after a Tier-1 US release: CPI, PPI, NFP, FOMC statement/presser (XER adds minutes), PCE, retail sales, ISM, GDP, Fed Chair remarks | DOCUMENTED (GSE 64, 81, 199–202; XER 70) |
| Market closed | Market closed, or a holiday session | DOCUMENTED (GSE 203; XER 67) |
| Session edges (REACH) | No plan within 30 min of a reopen; order windows end 15 min before the daily break (17:00–18:00 New York) | DOCUMENTED (GSE 191–192) |
| US open (TD) | No new limit 06:30–09:30 New York | DOCUMENTED (XER 17, 25) |
| Bad data | Quote sanity fails twice; chart data incomplete | DOCUMENTED (XER 95, 114) |
| Already active | A journaled order is working or a full-risk position is open → ACTIVE: manage it (§4); no new plan | DOCUMENTED (GSE 49–50, 251; XER 115) |

### Stage 2 — Regime and direction (top-down)

**2a. Regime gate — DOCUMENTED for REACH (GSE 28–32, 89–95).** Compute from completed bars, never eyeball,
and report both numbers.

- `vol ratio` = ATR14(H1, Wilder) ÷ median of that ATR over the last 480 completed H1 bars.
- `daily z` = (last completed D1 close − SMA50 of D1 closes) ÷ ATR14(D1, Wilder). D1 rolls at 17:00 New York.

| Reading | Meaning in the source | Result |
|---|---|---|
| vol ratio < 1.25 | Quiet (about 83–85% of the time); no measured edge | NO PLAN |
| 1.25 ≤ vol ratio < 2.0 and \|z\| ≥ 1 | The only regime with a measured edge | Gate open |
| vol ratio ≥ 2.0 | Shock | NO PLAN |
| \|z\| < 1 | No daily trend | NO PLAN |

The gate can only block a plan; it never creates or changes one (GSE 32). Under TD the gate is not part of
the method as documented — INFERRED: XER gives the TD helper the decision on whether a position exists
(XER 10), and the tested TD rules contain no regime gate (XER 23). GSE 60 says never publish a plan while the
gate is closed; whether that covers TD plans is MISSING (an owner decision).

**2b. Direction — DOCUMENTED, engine-specific.** Only this direction can carry a plan.

- TD (XER 13): D1 swing structure. Lower highs + lower lows with the close under the 20-day average =
  downtrend; mirror = uptrend. Anything else is no trend → no position, zones only.
- REACH (GSE 37): a direction exists only when D1 and H4 break-of-structure agree.
- Both: continuation only. Fade playbooks are retired: fading a swept extreme tested worst of every entry
  style, and trading against D1+H4 lost in every style (GSE 96–97). TD is trend-aligned by construction
  (XER 13, 17).
- MISSING: exact swing and break-of-structure definitions (lookback, close vs wick) and whether the 20-day
  average is simple or exponential. They live in the helper code.

**2c. Higher-timeframe context — DOCUMENTED, context only (GSE 99–104).** Monthly → Weekly → Daily → H4:
the draw on liquidity (where price is pulled and whose stops feed it), then the active dealing range and its
50% equilibrium (premium / discount). For plans the engine's direction rule decides; this read explains.

**Trending / ranging / transitioning — INFERRED.** The sources define two states: trend (direction rule met)
and no trend (rule not met, or |z| < 1). A separate "transitioning" state is MISSING. Conditions that look
transitional — D1 and H4 disagree, or D1 swings and the 20-day average disagree — fall under no trend → no
plan. Basis: GSE 37, 95; XER 13.

**Intraday direction — INFERRED.** Timeframes below the engine's direction timeframe (D1 for TD, D1+H4 for
REACH) never set direction. A move against that trend is the pullback toward an entry zone, not a reversal
signal. Basis: entries rest on the pullback side (XER 17; GSE 38–39) and counter-trend styles are retired
(GSE 96–97).

### Stage 3 — Level map and price behaviour at levels

**3a. Every level needs a named origin — DOCUMENTED (GSE 65–66, 147).** Order block, FVG, session extreme,
profile node, prior-period high/low, or an open. No origin → drop the level. Cite its tier. The source calls
this a "ranked level stack" (GSE 106–107); that Tier 1 ranks highest is INFERRED from the numbering.

| Tier | Levels | Source |
|---|---|---|
| 1 Structural | Weekly/Daily order blocks and FVGs; weekly open; prior week high/low | GSE 149 |
| 2 Session | PDH/PDL; daily open; midnight open (00:00 New York); Asian range high/low ("the most-swept level in gold"); London high/low | GSE 150–151 |
| 3 Volume | Naked POC; prior-day VAH/VAL; composite weekly POC; low-volume nodes | GSE 152 |
| 4 Derived | Dealing-range equilibrium; $25/$50/$100 round numbers; equal highs/lows and trendline liquidity (targets, not support) | GSE 153–154 |

Mark the nearest untapped liquidity above and below price (GSE 107).

**3b. TD zones — DOCUMENTED (XER 14–16).**

- Leg = the move being retraced: from the last H4 swing before the latest daily break of structure to the
  extreme since. Retracements at 38.2 / 50 / 61.8%.
- Level sources: H1 swings (5 days), H4 swings (15 days), daily swings, the last 7 days' highs/lows, today's
  high/low, prior-week high/low, 5-day range, the leg retracements, H4 50 SMA, 20- and 50-day averages.
- Patterns: double/triple tops/bottoms named in the zone text; head-and-shoulders (H1/H4) as context.
- Levels within 0.5 × ATR(H1) merge into one zone, at most 1 × ATR(H1) wide. Zone score = number of
  different sources.

**3c. Price behaviour at a level — DOCUMENTED as context only.** None of these triggers, gates or reshapes
a plan.

| Behaviour | How the sources read it | Source |
|---|---|---|
| Sweep of a named pool | A grading factor. Not a fade signal: limits just beyond a swept high/low were the worst-tested style | GSE 25–27, 96–97, 215 |
| Displacement | An impulsive candle series breaking short-term structure and leaving an FVG or order block | GSE 139–140, 217 |
| SMT divergence | Valid only with all four: same swing window with verified times and prices; at a named liquidity level; followed by displacement; leaving an FVG/OB. Without displacement it is a divergence, not a setup. Information only; added nothing out of sample | GSE 110, 126–143 |
| Volume | Absorption at an extreme (delta/CVD) is a reversal tell; a volume climax plus failure to make a new high is exhaustion; with tick volume only, use RVOL against the 20-day average for that time bucket | GSE 163–169 |

Reversal tells can only appear as context or in the AGAINST line, because reversal plans are retired —
INFERRED from GSE 96–97.

### Stage 4 — Position construction (helper output) or NO PLAN

The configured helper builds the plan. Publish it as printed: never type, round, move, widen, tighten or
"improve" a price, and never swap in another zone (GSE 15; XER 10). The table explains what each helper does
so a plan can be explained, sanity-checked and monitored.

**Entry types — DOCUMENTED.**

- Every plan is a pending order with an expiry. There is no at-market entry: REACH rests at least one spread
  beyond the market (GSE 39); TD rests 0.25–3 × ATR(H1) away (XER 17).
- There is no confirmation entry: never publish a "conditional forecast", an "activation" trigger, "wait for
  confirmation", or a limit that also needs a candle to confirm (GSE 16–17). An M15 confirmation entry with a
  tight stop was tested and rejected (XER 23).
- So there are three outcomes: a pending **PLAN**, **NO PLAN / NO TRADE** with the reason, or **ACTIVE**
  (manage the existing plan).

| Element | TD (XER 13–21) | REACH (GSE 28–50) |
|---|---|---|
| Gates | Trend rule (2b); Stage 1 blocks | Regime gate (2a); D1+H4 agreement (2b); Stage 1 blocks |
| Candidates | TD zones on the pullback side (3b) | M15/H1/H4 FVG edge or 50%; unswept M15/H1 swing |
| Selection | Nearest zone with 3+ confluences, 0.25–3 × ATR(H1) from price (downtrend: resistance above; uptrend: support below). If it has no room for the targets, the next zone | Deepest level with P(touch within the order window) ≥ 0.60, resting ≥ 1 spread beyond the market. Else an M15 continuation STOP entry with the same odds. Else NO PLAN |
| Order | SELL/BUY LIMIT at the zone's middle | LIMIT; STOP for the continuation entry |
| Stop | Beyond the zone and the structure guarding it within 1.25 × ATR(H1) (swing highs/lows, prior days' highs/lows, $50 round numbers) + buffer. Risk 0.8–2.5 × ATR(H1). No EMA lines | Beyond the structure; never closer than max(1.0 × ATR(H1), 20 × spread) |
| TP1 | Front-runs the first opposing zone, ≥ 1.2R. Close 50%; stop → entry | Nearest unswept lower-timeframe pool (M5/M15 swing, today's extreme, Asia/London extreme), ≥ 0.5R. Close 50%; stop → entry the same minute |
| TP2 | Front-runs the range low for shorts / range high for longs (or the next zone), ≥ 2R; if none, 3R | First higher-timeframe target (H1/H4/D1 swing, prior-day extreme, Asia extreme, $50 number), ≥ 1.5R; the runner rides to it |
| Front-running | Size of the front-run is MISSING | Short TP = level + spread + buffer; long TP = level − buffer; buffer size MISSING |
| Validity | 20 h, cut 15 min before the next Tier-1 release, and Friday 16:45 New York — whichever comes first ("earliest of" INFERRED from XER 20 and 70) | Window ends 15 min before the daily break and at the Tier-1 `--no-trade-after` cutoff (GSE 64, 191–192, 201); window length MISSING |
| Cancel before fill | An hourly candle closes beyond the stop, or TP1 trades before the fill | Only if an H1 candle closes beyond the stop or TP2 prints before the fill |
| Time exit after fill | MISSING (XER 20 sets order validity; it does not say whether a filled position is closed then) | Flat by Friday 16:45 New York; closed at market 48 h after the fill |
| Fallback | The next zone beyond the stop is drawn as the fallback | Not documented |
| Probability model | None | P(touch) model inside the helper — MISSING |

The long-side wording of the TD targets is INFERRED from "mirror = uptrend" (XER 13) and "uptrend → BUY
LIMIT in support below" (XER 17).

**Structure versus ratios — INFERRED summary of documented rules.** Prices come from structure; R and ATR
thresholds only decide which structural level qualifies. One rule is ratio-based: TD's TP2 falls back to 3R
when no structural target ≥ 2R exists (XER 19). REACH has no minimum R:R gate; the old 1.8R rule was retired
because it pushed entries into deep zones price rarely revisited (GSE 18–19). Letter grades never gate a plan
(GSE 20–21).

**Choosing between setups — DOCUMENTED.** One plan per run. TD once took the strongest zone; it now takes the
nearest qualifying zone, which the source reports still reproduces TD-1007 (XER 23). REACH takes the deepest
level still likely to be touched, then the continuation stop entry (GSE 38–40).

**MISSING construction details (they live in the helpers):** swing/BOS/FVG detection; stop and front-run
buffer sizes; what "room for the targets" means; where the 0.25–3 × ATR distance is measured from; what
happens when the structural stop falls outside 0.8–2.5 × ATR(H1); REACH's P(touch) model and window length.

### Stage 5 — Weigh context and write the answer

**How evidence is weighed — DOCUMENTED.** Indicators do not need to agree. Evidence has three ranks:

1. **Hard blocks** — Stage 1, the regime gate, the direction rule. Any one stops a new plan.
2. **The helper's plan** — the only source of direction and prices (XER 10; GSE 12–15).
3. **Context** — HTF bias, dealing range, SMT, volume, session, chart patterns, grade, news. It adds at most
   two lines to a plan (GSE 52–53, 239) and puts counter-arguments in AGAINST (XER 192). It never publishes,
   suppresses, reshapes or "downgrades" a plan (GSE 20–21, 32, 110, 116, 143, 209–210; XER 10, 71).

**Fundamentals and news — DOCUMENTED.**

- Scheduled event risk is a hard block (Stage 1). TD validity is cut 15 min before the next Tier-1 release
  (XER 70).
- News: one search; keep 2–3 drivers with their direction for gold (e.g. "dollar index up → headwind"). If
  they argue against the position, say so in AGAINST. Never change a price because of news (XER 71).
- DXY and real yields are macro-regime context, not intraday timing (GSE 133). SMT, yield and DXY filters
  added nothing out of sample (GSE 288–289).
- MISSING: any rule letting news flip direction, call a reversal, or alter an open position.

**Sessions and timing — DOCUMENTED (GSE 175–197).** Timing is a tilt, never a gate on its own (GSE 116).
Summer reference (London BST, New York EDT); recompute for the actual date:

| Window | Local | GST |
|---|---|---|
| Asia range forming | Tokyo session, 00:00–06:00 UTC | 04:00–10:00 |
| London killzone | 07:00–10:00 London | 10:00–13:00 |
| LBMA AM auction | 10:30 London | 13:30 |
| Comex pit open | 08:20 New York | 16:20 |
| NY killzone | 08:30–11:00 New York | 16:30–19:00 |
| LBMA PM auction | 15:00 London | 18:00 |
| Comex settlement | 13:30 New York | 21:30 |

Market hours: Sunday 18:00 to Friday 17:00 New York, daily break 17:00–18:00 New York (GSE 191). REACH timing
tilt: 4:15, 7:15 and 10:15 PM Dubai measured best; avoid 3:15 PM; the regime gate is open most often 7 PM to
midnight Dubai (GSE 194–197). TD: no new limit 06:30–09:30 New York, so it runs at 19:15 and 22:15 Dubai only
(XER 17, 23, 25).

**Grading rubric — DOCUMENTED; optional; one context line at most (GSE 207–222).**

| Factor | Max | Full marks when |
|---|---|---|
| HTF bias alignment | 20 | Daily + H4 agree with direction |
| Liquidity taken | 15 | A named pool was swept immediately prior |
| SMT confirmation | 15 | At least one Tier-1 pair diverged at that level, same swing window |
| Displacement quality | 15 | Impulsive break of short-term structure leaving a clean FVG/OB |
| Volume / delta | 10 | RVOL > 1.5 on the displacement, or absorption at the sweep |
| Level confluence | 10 | Two or more level tiers within one M5 ATR |
| Session timing | 5 | Inside a killzone with the right playbook for that window |
| Premium/discount | 5 | Entry on the correct side of dealing-range equilibrium |
| Spread & conditions | 5 | Spread < 15% of stop; no blackout within 30 min |

**Output formats — DOCUMENTED.** State the invalidation before the target in every plan (GSE 67).

REACH plan (GSE 228–240):

```
STATUS: PLAN (LIMIT|STOP)
REGIME: OPEN · vol ratio <x> (open 1.25–2.00) · daily z <y> (open at |z| ≥ 1)
QUOTE: bid / ask FEED @ HH:MM:SS GST · spread · helper data through HH:MM GST (gap N min)
DIRECTION: LONG / SHORT · D1 <state> · H4 <state>
ORDER: BUY/SELL LIMIT/STOP @ <entry> — <entry origin> · P(fill in window) <p_touch>
STOP: <stop> (risk $<risk_usd>)
TP1: <tp1> (<r1>R) — <origin> · close 50% · then stop -> entry · P(TP1 before stop) <p>
TP2: <tp2> (<r2>R) — <origin> · runner
EXPIRY: <GST> · cancel if TP2 prints before the fill or an H1 candle closes beyond the stop
CONTEXT: max 2 lines (regime / SMT / session)
```

No plan (GSE 242–249):

```
STATUS: NO PLAN — <regime gate closed / helper reason / blackout / helper missing>
Regime: vol ratio <x> (open 1.25–2.00 = hourly ATR <lo>–<hi>, now <atr>) · daily z <y> (open at |z| ≥ 1)
State: <one line on structure>
Nearest levels: <from the helper, with P(touch)>
Next run: <GST time or condition>
```

TD plan: the helper's table exactly as printed (its layout is not in the sources), followed by (XER 190–192):

```
NEWS: 2-3 drivers with their direction for gold (context only)
AGAINST: anything that argues against the position
```

Other documented statuses: `STATUS: HELPER MISSING` (XER 64), `STATUS: MARKET CLOSED` (XER 67),
`NO TRADE — quote and candles disagree` (XER 95), `NO TRADE — chart minutes incomplete` (XER 114), ACTIVE →
the `manage` output verbatim (GSE 251; XER 115). ANALYSIS ONLY contains the regime gate reading, levels,
sessions and SMT (GSE 22–23).

---

## 4. Monitoring an issued plan or open position

**Mechanism — DOCUMENTED.** While a plan is ACTIVE, run the engine's `manage --id <id>` and report its state
and action verbatim; make no new plan (GSE 251; XER 115). The TD runbook checks hourly at hh:15 while a plan
is ACTIVE (XER 183); scheduling those checks is a separate responsibility (§8).

**The original thesis is the plan as issued — INFERRED.** It consists of the direction, the entry and its
origin, the stop (invalidation), TP1/TP2 and their origins, the expiry and the cancel rules. Monitoring
compares the live market with these fixed items and never re-derives a new thesis. Basis: helper prices are
never changed (GSE 15; XER 10); the invalidation is stated with the plan (GSE 67); REACH cancels before the
fill "only if" its two rules trigger (GSE 47).

| Situation | Trigger | Action | Label |
|---|---|---|---|
| Working, unfilled | Entry not reached; no cancel rule hit; not expired | Keep. Most limits never fill; that is normal | DOCUMENTED (XER 23) |
| Invalidated before fill | An H1 candle closes beyond the stop | Cancel the order | DOCUMENTED (GSE 47; XER 20) |
| Missed move | TD: TP1 trades before the fill. REACH: TP2 prints before the fill | Cancel the order | DOCUMENTED (GSE 47; XER 20) |
| Expired | Validity or order window ends | Cancel the order | DOCUMENTED (XER 20; GSE 191–192) |
| Filled, between stop and TP1 | No documented trigger hit | Hold; nothing changes | INFERRED (GSE 15; XER 10) |
| TP1 reached | TP1 trades | Close 50%; stop → entry (REACH: the same minute) | DOCUMENTED (GSE 42–43; XER 19, 115) |
| Stopped | The stop trades | Closed; this is the defined invalidation | DOCUMENTED (GSE 41; XER 18) |
| TP2 reached | TP2 trades | The runner closes at target | DOCUMENTED (GSE 44–45; XER 19) |
| Time exit (REACH) | Friday 16:45 New York; 48 h after the fill | Close at market | DOCUMENTED (GSE 48) |

Helper state names in the sources: `closed`, `MISSED_MOVE`, `INVALIDATED`, `NOT_FILLED` (each → cancel the
limit) and "move the stop to entry after TP1" (XER 115). Their exact triggers are inside the helper —
MISSING; matching each name to the rule it suggests is INFERRED.

**Normal fluctuation — INFERRED:** any movement that triggers none of the rules above. About half of TD fills
end as full stops and about 42% end positive (XER 23), so adverse movement inside the stop is expected.

**Deterioration — MISSING.** No intermediate state and no early-exit rule exist. Context that turns against
the trade (news, SMT, volume) may be reported, but the stop, targets and expiry stay as issued — INFERRED from
GSE 15, 47, 52–53 and XER 10, 71. The source also reports that no exit design created an edge on uninformed
entries (GSE 286).

**Engine state is not broker state — INFERRED.** ACTIVE, fills and outcomes come from the engine journal and
its price data (Dukascopy bid/ask for REACH, GSE 75; `grade` re-scores fills on bid/ask data, GSE 257–259).
The method never reads a broker account (XER 8). A real fill, price or size can differ.

---

## 5. Replacement

- **One plan at a time — DOCUMENTED.** While a journaled order is working or a full-risk position is open,
  `plan` returns ACTIVE (GSE 49–50; XER 115).
- **A new plan needs a complete fresh run** (Stages 1–4, with the helper) — INFERRED from GSE 12–13, 85–87.
- **A failed long is not a short — DOCUMENTED.** Direction comes only from the trend rule; fades and trades
  against D1+H4 are retired (GSE 96–97; XER 13). A short needs the TD D1 rule (or the REACH D1+H4 rule) to
  read down on its own.
- **Fallback after a stop-out — DOCUMENTED:** the next zone beyond the stop, in the same direction, is drawn
  as the fallback (XER 8, 21). It is a drawing, not an order; it becomes a plan only if a later run produces
  it — INFERRED.
- **Runner ambiguity — MISSING.** REACH blocks new plans only while a "full-risk" position is open (GSE 49).
  After TP1 the runner's stop is at entry, so it may no longer block a new plan, which would allow two open
  positions. Owner's constraint (thesis 8, not from the sources): one open position at a time, so a runner
  still counts as open until the owner rules otherwise.

---

## 6. Essential constraints versus optional evidence

**Essential — DOCUMENTED. Breaking any one invalidates the answer.**

1. Verified live inputs; no price, level or direction from web search, news or memory (GSE 33; XER 10, 186).
2. No helper, no plan; never hand-build an entry, stop or target (GSE 22–27, 59; XER 10, 64).
3. Publish helper prices verbatim; never change them (GSE 15; XER 10).
4. Hard blocks: Stage 1, the regime gate (REACH), the direction rule (both) (GSE 28–32, 37, 81, 199–203;
   XER 13, 17).
5. Continuation only; never against D1 (+H4 for REACH) (GSE 96–97).
6. One plan or position at a time; ACTIVE → manage, no new plan (GSE 49–50, 251; XER 115).
7. Every level has a named origin (GSE 65–66).
8. State the invalidation before the target (GSE 67).
9. Planning only; the user sizes and executes (GSE 68–69; XER 8, 186, 198).
10. Spot tick volume is not real volume (GSE 61–63).
11. Time-zone-aware times, reported in GST (GSE 175–177).

**Optional evidence — context only. It never has to agree and never gates:** HTF bias read and draw on
liquidity, dealing range and premium/discount, SMT, volume/delta/RVOL, session and killzone timing, chart
patterns, the grading rubric, news drivers (GSE 52–53, 99–116, 207–210; XER 15, 71).

---

## 7. Known limitations

- **Helpers missing.** Neither `tools/xau_td.py` nor `tools/xau_reach.py` was present. Under the documented
  method no order plan can be produced until one is supplied; until then the bot is limited to ANALYSIS ONLY.
- **Canonical engine undefined** (§0), including whether the regime gate covers TD.
- **Construction details live in helper code** (Stage 4 list). A re-implementation is not the documented
  method until it reproduces the helper's outputs.
- **Reference files missing.** `references/*.md` (market anatomy, structure and SMT, volume and levels, setup
  playbooks, risk and execution) and the JS-G regime-gate snippet are referenced (GSE 31, 270–274) but absent,
  so BOS/CHoCH and PD-array definitions are unavailable.
- **No journal.** `journal/xau_plans.jsonl` is absent; there is no record of issued plans or outcomes.
- **Evidence is source-reported, not verified.** The data and studies behind the figures are not available.
  They are claims, not a proven edge.
- **Monitoring tracks the engine journal, not a broker,** and "deterioration" is undefined.

**Source-reported evidence — unverified, context only.**

- TD final rules: 2024–26: 294 plans, 110 filled, +0.09R per fill; 2021–23: 271 plans, 96 filled, +0.18R per
  fill. About 42% of fills positive, about half full stops, TP1 reached on 29–39% of fills, TP2 on about 10%.
  Worst drawdown 10–14R; longest losing run 6–10; about 10 plans and 3–4 fills a month (XER 23). Risk 0.25%
  per position, 0.5% at most after 30 live fills track this; "not a promise for any single trade" (XER 196).
- REACH audit: the volatility gate was positive in all six years; breakout stop entry with both gates
  +0.191R per trade, about 51 trades a year, worst drawdown 5.8R — "a best case until live fills confirm it"
  (GSE 281–283).
- Feedback loop: journal every plan; re-grade on bid/ask; judge direction after 30 fills and the edge after
  about 100; change parameters only from the scorecard, and only if the change holds in both 2021–23 and
  2024–26 (GSE 255–262).

---

## 8. Separate responsibilities (not analysis)

Documented in XER, but not part of the analysis method. Keep them in separate components.

| Responsibility | Where documented | Note |
|---|---|---|
| Scheduling | XER 25, 182–183: runs at 19:15 and 22:15 Dubai; hourly hh:15 checks while ACTIVE | A prompt does not create a running monitor |
| Notifications | XER 111, 144: `PLACE NOW` line and push notification after a PLAN | Only for status PLAN |
| Chart drawing | XER 119–163: TradingView zones, lines and position tool, verified after reload | Drawing is not analysis |
| Data plumbing and sync | XER 32–95, 165–180: setup, browser tabs, quote and candle capture, file sync | Supplies Stage 1 inputs |
| Journal and grading | GSE 255–262; XER 165–178 | Evaluation, not live decisions |
| Broker execution | None: never place, modify or cancel orders; never click Buy/Sell (XER 8, 186, 198) | The owner executes |
