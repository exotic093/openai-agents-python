# Gold Analysis — Sources and Gaps

Companion to `GOLD_ANALYSIS_BRAIN.md`. It records what was inspected, where each part of the brain came from,
what is inferred or missing, how the existing method differs from the intended thesis, and a consistency
check against source-backed examples. Extracted 2026-10-08. The original strategy files were read only and
not modified.

---

## 1. Sources inspected

### 1.1 Gold-analysis sources found and used

Both files were read in full. Line numbers below and in the brain refer to these versions.

| Key | Path | Size | sha256 | Updated |
|---|---|---|---|---|
| GSE | `/root/.claude/skills/synced/784c1bfa-c3ee-4726-ab10-706ff347c7ed_58cf719a-3f88-44b3-9ae0-e6594ca026c5/gold-scalp-engine/SKILL.md` | 290 lines, 17,084 bytes | `a2a914b8ea51dfc957d78aab433d1917509de614977b164c5a95ab7f1dfac56b` | 2026-10-06T11:02Z |
| XER | `/root/.claude/skills/synced/784c1bfa-c3ee-4726-ab10-706ff347c7ed_58cf719a-3f88-44b3-9ae0-e6594ca026c5/xau-engine-run/SKILL.md` | 198 lines, 19,876 bytes | `b80be1323c62e4cce3e2b611c84f6e2cee93a44448d2dfa04bb408a196cf930b` | 2026-10-07T10:58Z |

The update times and skill ids come from the skills manifest in the same folder (`manifest.json`; GSE =
`skill_01Xf2P1RiToxgvsnwoARsQzc`, XER = `skill_01BdBusF3yCbG3MHZto1ECiZ`).

**GSE section map**

| Lines | Section | Used in the brain |
|---|---|---|
| 10–53 | READ FIRST: helper-only plans, prohibitions, regime gate, what the REACH helper does | §0 governing rule; Stage 2a; Stage 4 (REACH); §5 |
| 57–69 | §0 Non-negotiables | §6 essentials |
| 73–81 | §1 Input contract | §2 inputs; Stage 1 |
| 85–120 | §2 Analysis sequence (8 steps) | Stage order; Stages 2–3 |
| 124–143 | §3 SMT divergence | Stage 3c |
| 147–157 | §4 Level hierarchy | Stage 3a |
| 161–169 | §5 Volume | §2 inputs; Stage 3c |
| 173–203 | §6 Sessions, timing, blackouts | Stage 1; Stage 5 |
| 207–222 | §7 Grading rubric | Stage 5 |
| 226–251 | §8 Output format | Stage 5 outputs; §4 |
| 255–262 | §9 Feedback loop | §7 |
| 266–274 | §10 Reference files (absent) | §7 limitations |
| 278–290 | §11 Evidence | §7 evidence |

**XER section map**

| Lines | Section | Used in the brain |
|---|---|---|
| 8–10 | Goal; RULE ZERO | §1 purpose; §0 governing rule |
| 12–21 | THE METHOD (9 steps) | Stages 2b, 3b, 4 (TD); §5 |
| 23 | EVIDENCE | Stage 4 setup choice; §7 evidence; consistency check |
| 25–28 | SETTINGS | Stage 1 (US open); §8 |
| 32–64 | G0 SETUP | Helper and journal requirements; §8 |
| 66–67 | G1 STATUS | Market-closed block |
| 69–71 | B1 EVENTS; NEWS | Stage 1; Stage 5 |
| 73–95 | B2–B3 tabs, quote, candles | Quote sanity (§2) |
| 97–117 | B4 PLAN: statuses; ACTIVE → manage | Stage 4; §4 |
| 119–180 | B5–B7 draw, verify, journal, sync | §8 only |
| 182–183 | WATCH | §4 cadence; §8 |
| 185–198 | NEVER; FINAL ANSWER | §6; Stage 5 outputs; §7 |

### 1.2 Searched; no gold-analysis content

- **This repository (`openai-agents-python`).** Every gold/XAU/scalp match is the "Golden Gate Bridge" example
  (`README.md:185`, `docs/sessions.md:24`, `docs/running_agents.md:79`, `examples/basic/remote_image.py:5`,
  `examples/basic/session_example.py:29`, `tests/test_session.py:71`, and the `docs/ja/` copies). Git history
  on all branches contains no gold-related paths.
- **Other synced skills and plugin bundles under `/root/.claude/`.** Matches are colour names, "golden ratio"
  and "gold standard".
- **`/mnt/user-data/{uploads,outputs,working}` and `/mnt/attach`.** Empty. `/mnt/skills` has no gold skills.

### 1.3 Not available in this session

No live charts, broker account, helper output, journal, past conversations or backtest data were available,
and none were used. Every rule in the brain comes from GSE or XER.

### 1.4 Referenced by the sources but absent

| Missing item | Referenced at | Role | Impact |
|---|---|---|---|
| `tools/xau_td.py` (sha256 `15bf0d11a2b30c21f2f7d70a87a05fee15b68a93d28730608bc278a45c066bbc`) | XER 10, 25, 49, 64, 99, 115 | Computes every TD plan and the manage actions | No TD plans possible under the method |
| `tools/xau_reach.py` (helper v2.x) | GSE 12, 22, 75–78, 119, 251, 257 | Computes REACH status, plans, manage, grade | No REACH plans possible under the method |
| `journal/xau_plans.jsonl` | GSE 257; XER 51–54, 166 | Record of issued plans and outcomes | No issued plans to check against; ACTIVE state unknown |
| `journal/events.json`, `journal/td_drawn_ids.json` | XER 55–58, 69–70, 102 | Event-calendar cache; drawing ids | Calendar must be rebuilt (format at XER 70) |
| `references/gold-market-anatomy.md`, `smt-and-structure.md`, `volume-and-levels.md`, `setup-playbooks.md`, `risk-and-execution.md` | GSE 270–274 | Macro stack, BOS/CHoCH, PD arrays, full SMT method, level construction, playbooks, sizing | Structure definitions unavailable; analysis depth limited |
| JS-G regime-gate snippet "from the xau-engine-run skill" | GSE 31 | Reads the regime gate from the OANDA H1 chart | The current XER has only JS-A, JS-B, JS-T and JS-V; compute the gate from bars instead |
| "SETUP v3" | GSE 23 | Helper setup procedure | The current XER has "G0 SETUP" instead |
| Backtest and MCMC studies ("17-year study", "Oct 2026 audit", 5-year M1 replay) | GSE 26–27, 89–97, 278–290; XER 23 | Evidence behind the rules | The figures cannot be verified |

---

## 2. Where each part of the brain came from

| Brain section | Sources | Label |
|---|---|---|
| §0 Two engines; governing rule | GSE 12–27, 79; XER 10, 64 | DOCUMENTED; canonical engine MISSING |
| §1 Purpose | GSE 8, 68–69; XER 8 | DOCUMENTED |
| §1 Thesis | The owner's task brief | Intended design, not a source |
| §2 Inputs and checks | GSE 28–34, 61–63, 75–81, 126–140, 163–177, 191–203, 257; XER 25, 49, 67, 70–71, 76–95, 114 | DOCUMENTED; history length INFERRED |
| Stage 1 Hard blocks | GSE 22–27, 49–50, 59, 64, 81, 191–192, 199–203, 251; XER 17, 25, 64, 67, 70, 95, 114–115 | DOCUMENTED |
| Stage 2a Regime gate | GSE 28–32, 60, 89–97 | DOCUMENTED for REACH; TD scope INFERRED / MISSING |
| Stage 2b Direction | GSE 37, 96–97; XER 13, 17 | DOCUMENTED; swing/BOS definitions MISSING |
| Stage 2c HTF context | GSE 99–104 | DOCUMENTED |
| Trending / ranging / transitioning; intraday direction | GSE 37–39, 95–97; XER 13, 17 | INFERRED; "transitioning" MISSING |
| Stage 3a Level tiers | GSE 65–66, 106–107, 147–157 | DOCUMENTED; tier ranking INFERRED |
| Stage 3b TD zones | XER 14–16 | DOCUMENTED |
| Stage 3c Behaviour at levels | GSE 25–27, 96–97, 110, 126–143, 163–169, 215, 217 | DOCUMENTED, context only; reversal-tell handling INFERRED |
| Stage 4 Entry types | GSE 16–17, 39; XER 17, 23 | DOCUMENTED |
| Stage 4 Engine table | TD: XER 13–21, 70. REACH: GSE 28–50, 64, 191–192, 201 | DOCUMENTED; "earliest of" validity and long-side TD targets INFERRED; buffers, window length, P(touch) model, TD post-fill time exit MISSING |
| Stage 4 Structure vs ratios; setup choice | GSE 18–21, 38–40; XER 17–19, 23 | INFERRED summary; DOCUMENTED rules |
| Stage 5 Weighing evidence | GSE 20–21, 32, 52–53, 110, 116, 143, 209–210, 239; XER 10, 71, 192 | DOCUMENTED |
| Stage 5 Fundamentals and news | GSE 33, 133, 288–289; XER 70–71 | DOCUMENTED; news-driven reversal or management MISSING |
| Stage 5 Sessions, rubric, outputs | GSE 22–23, 67, 175–197, 207–251; XER 17, 23, 25, 64, 67, 95, 114–115, 190–192 | DOCUMENTED |
| §4 Monitoring | GSE 15, 41–48, 52–53, 67, 75, 191–192, 251, 257–259, 286; XER 8, 10, 18–20, 23, 71, 115, 183 | Mostly DOCUMENTED; original thesis, normal fluctuation, state-name mapping and engine-vs-broker INFERRED; deterioration MISSING |
| §5 Replacement | GSE 12–13, 49–50, 85–87, 96–97; XER 8, 13, 21, 115 | DOCUMENTED; fresh run and fallback-to-plan INFERRED; runner rule MISSING |
| §6 Essentials vs optional | GSE 15, 22–33, 52–53, 59–69, 81, 96–116, 175–177, 199–210; XER 8–17, 71, 186, 198 | DOCUMENTED |
| §7 Limitations and evidence | GSE 31, 255–262, 270–290; XER 23, 196 | DOCUMENTED claims, unverified |
| §8 Separate responsibilities | GSE 255–262; XER 8, 25, 32–198 (operating sections) | DOCUMENTED |

---

## 3. Documented versus inferred components

Everything in the brain not listed here is DOCUMENTED, with its line references.

**INFERRED, with basis**

1. History length (480 H1 ATR values, 50 D1 closes) — follows from the regime-gate formulas (GSE 28–30).
2. The regime gate is not part of TD as documented — XER 10 gives the TD helper the existence decision, and the
   tested TD rules contain no regime gate (XER 23).
3. Trending / ranging mapping; no "transitioning" state — the sources only distinguish trend and no trend
   (GSE 37, 95; XER 13).
4. Intraday moves are pullbacks, not reversal signals — entries rest on the pullback side (XER 17; GSE 38–39);
   counter-trend styles are retired (GSE 96–97).
5. Tier 1 ranks highest in the "ranked level stack" — from the tier numbering (GSE 106–107, 147–154).
6. Reversal tells (absorption, exhaustion) can only be context or AGAINST — reversal plans are retired
   (GSE 96–97).
7. TD validity is the earliest of 20 h, the Tier-1 cutoff and Friday 16:45 New York — XER 20, with "the helper
   cuts the validity" (XER 70).
8. TD long-side targets mirror the short-side wording — XER 13, 17.
9. "Prices from structure; ratios only qualify a level" — a summary of XER 17–19 and GSE 18–19, 38–46.
10. The original thesis is the issued plan's fixed items — GSE 15, 47, 67; XER 10.
11. Normal fluctuation means no documented trigger was hit — GSE 47 ("only if"); XER 23 outcome distribution.
12. Context that turns against an open trade is report-only — GSE 15, 52–53; XER 10, 71.
13. Engine ACTIVE and fill states come from the journal and price data, not a broker — GSE 75, 257–259; XER 8.
14. A new plan needs a complete fresh run; the fallback zone becomes a plan only through a later run —
    GSE 12–13, 85–87; XER 21.
15. Matching helper state names (`closed`, `MISSED_MOVE`, `INVALIDATED`, `NOT_FILLED`) to the cancel rules —
    names at XER 115, rules at XER 20 and GSE 47.
16. Applying the regime gate to TD would likely block most TD runs — the gate is open only 21–30% of the time
    even from 7 PM to midnight Dubai (GSE 196–197), the window of the TD run times (XER 25).

**MISSING — not defined anywhere in the sources**

Canonical engine; whether the regime gate covers TD; a "transitioning" state; swing, BOS/CHoCH, FVG and
order-block detection rules; whether the 20-day average is simple or exponential; stop and front-run buffer
sizes; TD's "room for the targets"; the anchor of TD's 0.25–3 × ATR distance; TD's handling of a structural
stop outside 0.8–2.5 × ATR; TD's time exit after a fill; REACH's P(touch) model and order-window length;
exact triggers of the helper states; "deterioration"; any news-driven reversal or management rule; whether a
post-TP1 runner blocks a new plan; the layout of the TD helper's table; any broker reconciliation.

---

## 4. Existing method versus the intended thesis

| # | Thesis | Existing method | Fit |
|---|---|---|---|
| 1 | Top-down trend, intraday direction, trending / ranging / transitioning | Monthly → H4 context (GSE 99–101). Direction from D1 (TD) or D1+H4 (REACH). REACH adds a measured volatility and daily-trend gate. Intraday never sets direction. No "transitioning" state | Partial: "transitioning" is missing; the regime is volatility + daily z, not a market-phase label |
| 2 | Reaction zones and behaviour around them | Tiered levels with named origins; TD confluence zones. Sweeps, displacement, SMT and volume are context only; behaviour never triggers or gates an entry | Partial: zones match; behaviour is never decisive |
| 3 | Lower-timeframe scalping entry | REACH: M15/H1/H4 levels and an M15 continuation stop; TP1 from M5/M15 pools. TD: entry at the middle of H1/H4/D1-derived zones; an M15 confirmation entry was tested and rejected | Partial (REACH); differs (TD) |
| 4 | Fundamentals and news for continuation, reversal, event risk | Event risk is a hard blackout. News gives 2–3 drivers for context and AGAINST and never changes a price. Reversal plans are retired | Differs: news never decides direction, reversal or management |
| 5 | Entry, stop, targets from structure, not ratios | Yes, within ATR bounds; REACH has no minimum R:R gate. TD's TP2 falls back to 3R when no structural target ≥ 2R exists | Matches, with one ratio fallback |
| 6 | Best conditional or confirmed setup; never force | The only conditional form is a pending LIMIT/STOP with expiry and fixed cancel rules. Confirmation entries, activation triggers and conditional forecasts are forbidden (GSE 16–17). NO PLAN is a normal answer | Partial: no "confirmed setup" mode; "conditional forecast" is forbidden |
| 7 | Monitor against the original thesis; fluctuation vs deterioration vs invalidation | `manage --id` reported verbatim; fixed invalidation, cancel, TP1 and time rules. No deterioration state; no discretionary changes. Tracks the engine journal, not a broker | Partial: invalidation defined; deterioration missing; no broker verification |
| 8 | Replace only with a separate setup; failed long ≠ short; one at a time | One plan at a time; continuation only; the next same-direction zone is drawn as a fallback; a new plan only from a new run. The "full-risk" wording may let a post-TP1 runner coexist with a new plan | Mostly matches; runner ambiguity |
| — | Autonomous bot | The sources describe a human-in-the-loop planning runbook: the owner places orders, and checks are scheduled runs | Differs: autonomy is limited to analysis and plan relay |

**Conflicts between the two sources**

- **Canonical helper:** REACH (GSE 12–13) vs TD (XER 10). GSE 31 still points to a JS-G snippet in XER that the
  current XER does not contain.
- **Run timing:** GSE 194–195 rates 4:15 PM Dubai among the best REACH run times; XER 23 and 25 refuse the
  16:15 Dubai run for TD, where such plans lost −0.13 to −0.18R per fill.
- **Filters:** GSE 289 reports that confluence scores and minimum-reward gates added nothing out of sample,
  while TD requires 3+ confluences and TP1 ≥ 1.2R / TP2 ≥ 2R. Different engines and studies; the sources do
  not reconcile them.
- **Entry style:** GSE's audit reports engine-style trend-aligned limits at −0.025R and breakout stop entries
  with both gates as best (GSE 280–283); TD's limits are reported positive (XER 23). Different rule sets; not
  reconciled.

---

## 5. Consequential gaps

Only gaps that prevent faithful implementation.

| # | Gap | Why it blocks | What would close it |
|---|---|---|---|
| G1 | Helper code absent (`xau_td.py`, `xau_reach.py`) | The method forbids hand-built plans, so without a helper only ANALYSIS ONLY is possible | Supply the helper(s); TD sha256 `15bf0d11…` |
| G2 | Canonical engine undefined; regime-gate scope unclear | The engines differ in direction rule, entry, stop, targets, expiry and cancel rules. Applying GSE's gate to TD would likely block most TD runs — INFERRED: the gate is open only 21–30% of the time even in the 7 PM–midnight Dubai window where TD runs (GSE 196–197; XER 25) | The owner names the engine and rules on the gate for TD |
| G3 | Construction parameters exist only in code | Swing/BOS/FVG detection, buffers, "room for the targets", P(touch), window length and out-of-band stops all change the plan; a re-implementation would produce different plans | The helper code, or a written spec plus a parity test |
| G4 | Monitoring definitions | "Deterioration" is undefined; helper states are only partly named; TD's post-fill time exit is undefined; engine fills are simulated, not broker-confirmed | Owner decisions plus read-only broker state |
| G5 | Post-TP1 runner vs the one-position rule | GSE 49's "full-risk" wording may allow a second position after TP1, against thesis 8 | An owner decision |
| G6 | Structure references absent | BOS/CHoCH and PD-array definitions sit in the missing `references/*.md`, so direction and level reads cannot be pinned down | Restore the reference files |

---

## 6. Consistency check against source-backed examples

This checks whether the extracted rules explain the documented decisions. It is not evidence of profitability.
No journal was available, so no issued plan or outcome could be checked beyond the items below.

**Example 1 — TD-1007: 4181.5 / 4201.5 / 4149 / 4115 (XER 23).**
The source lists the four prices without labels. Read in the order of the PLACE line (entry · SL · TP1 · TP2,
XER 111), they form a short: stop above entry, targets below (INFERRED).

| Check | Result |
|---|---|
| Risk | 4201.5 − 4181.5 = 20.0 |
| TP1 ≥ 1.2R (XER 19) | (4181.5 − 4149) / 20 = 1.625R — consistent |
| TP2 ≥ 2R, else 3R (XER 19) | (4181.5 − 4115) / 20 = 3.325R — consistent. A pure 3R fallback would be 4121.5, so TP2 came from structure, the rule's first branch |
| Stop beyond structure, incl. $50 numbers, + buffer (XER 18) | 4201.5 = 4200 + 1.5, just beyond a $50 round number — consistent (the guarding structure is not named in the source) |
| Risk 0.8–2.5 × ATR(H1) (XER 18) | Holds only if ATR(H1) was between 8.0 and 25.0 — not verifiable (no candle data) |
| Short needs a D1 downtrend (XER 13); entry at the middle of the nearest 3+ confluence zone (XER 17) | Not verifiable (no candle data). The source states the nearest-zone rule reproduces TD-1007 |
| Against REACH rules | TP1 ≥ 0.5R and TP2 ≥ 1.5R hold; the stop floor needs ATR(H1) ≤ 20 and spread ≤ 1.00, and the regime gate is unknown — not verifiable |

Verdict: TD-1007's arithmetic fits the documented TD stop and target rules. The trend, zone and ATR conditions
cannot be checked from the available material.

**Example 2 — the refused 16:15 Dubai run (XER 17, 23, 25).** Converted with time-zone-aware arithmetic
(Python `zoneinfo`, Asia/Dubai → America/New_York):

| Dubai run | New York, summer (EDT) | New York, winter (EST) | Inside 06:30–09:30 New York? |
|---|---|---|---|
| 16:15 | 08:15 | 07:15 | Yes → no new limit |
| 19:15 | 11:15 | 10:15 | No |
| 22:15 | 14:15 | 13:15 | No |

Verdict: the documented US-open rule fully explains why TD runs only at 19:15 and 22:15 Dubai, in both DST
regimes.

**Example 3 — the hand-built plan of October 2026 (GSE 22–27).** A plan typed by hand, with a limit just beyond
a swept high or low. The extracted method rejects it on three independent documented grounds: it did not come
from the helper (essential 2); it fades a swept extreme, a retired style (GSE 96–97); its prices did not come
from the engine's structural selection (Stage 4). Consistent. The source gives no prices for this plan.

**Example 4 — documented rejections.** Retired or rejected in the sources: the 1.8R minimum R:R gate and
grade-based gating (GSE 18–21); a 4-hour reversal filter, an M15 confirmation entry with a tight stop, a looser
trend rule and 1-hour EMAs (XER 23); SMT, yield, DXY, hour and Friday filters (GSE 284–289). None appears as a
gate or trigger in the brain. Consistent.

---

## 7. Proposed improvements (outside the extraction)

PROPOSED — not part of the method; adopt only by owner decision.

1. Supply the helper(s) and the journal; declare `ENGINE = TD` or `ENGINE = REACH` in the bot configuration;
   decide whether the regime gate applies to TD (G1, G2). Engine and gate scope are now decided for the bot
   (§9).
2. Before trusting any re-implementation, require exact parity: reproduce TD-1007 and every journaled plan
   from the same historical inputs, and treat any mismatch as a defect (G3).
3. Add a read-only broker-state reader so the bot can label positions BROKER-VERIFIED and reconcile engine
   fills with real fills (G4).
4. Decide whether a post-TP1 runner blocks a new plan. Decided: the runner counts as open (G5, §9).
5. If you want a "deterioration" state, define it as report-only so it cannot change the tested stop, targets
   or expiry — or leave it undefined (G4).
6. Restore `references/*.md`; let the helper compute the regime gate (GSE 78 plans this for v2.4); update the
   stale JS-G and "SETUP v3" references in GSE (G6). These edit your original files and are left to you.

**Analysis changes to test on the bid/ask replay.** Keep a change only if it holds in both 2021–23 and
2024–26 (GSE 261–262).

7. A volatility gate on TD: split TD's results by vol ratio. The gate was the most robust gain in the REACH
   audit (GSE 92–93, 281); the bot already grades setups by it (§9).
8. Entry type, pullback limit versus breakout stop: limit fills are adversely selected (GSE 287), and
   breakout stop entries with both gates tested best (GSE 282–283).
9. H4 agreement for TD's direction: trading against D1+H4 lost in every style (GSE 97); TD only tested a
   looser trend rule (XER 23).
10. A liquidity check beyond the stop: the Asian range high/low is the most-swept level, and equal
    highs/lows are targets (GSE 150–154). Untested in the sources.
11. Trend extension: split results by daily z level and by the share of the daily ATR already used.
    Untested in the sources.
12. Execution costs: measure live spread, commission and stop-order slippage against the Dukascopy prices;
    every extra $0.10 per round trip costs about 0.008R (GSE 290).

---

## 8. Readiness

| Use | Status | Why |
|---|---|---|
| Descriptive analysis | Ready | The regime-gate formula, level tiers, sessions, blackouts, SMT and volume rules, and output formats are fully documented, and `gold_analysis/regime_gate.py` computes the gate. Structure reads stay qualitative until G6 closes |
| Conditional trade planning | Ready under the v2 owner decisions (§9) | The bot builds positions itself, overriding the helper-only rule. Under the documented method alone it would be blocked (G1, G2). Its plans have not been checked for parity with the original helpers (G3) |
| Monitoring | Ready under v2 | Documented invalidation, cancel, TP1 and time rules, plus the owner's report-only WEAKENING state and read-only eToro positions where the tool allows |

---

## 9. Owner decisions applied in the bot prompt (2026-10-08, v2)

These are decisions for this deployment, not extracted method. `GOLD_BOT_INTEGRATION.txt` (v2) applies
them and takes precedence over `GOLD_ANALYSIS_BRAIN.md` where they differ.

| Decision | Changes or fills | Basis |
|---|---|---|
| The bot builds positions itself; an engine helper is optional | Overrides "no helper, no plan" (GSE 22–27, 59; XER 10) | Owner instruction |
| REACH-style construction: D1+H4 direction, REACH stop floor and targets (TP1 ≥ 0.5R, TP2 ≥ 1.5R), cancel if TP2 prints first, TD zones for pullback entries | G2 (engine) | GSE 37–48; XER 14–17 |
| Entry type follows M15 structure: pullback limit while M15 runs against the bias, breakout stop while it runs with it | Proposal 8 | GSE 282–283, 287; untested as a switching rule |
| The regime gate grades setups: A when open; B is published but arms only when the gate opens (configurable); never in shock | Replaces the v1 rule that the gate blocks every plan | No measured edge outside the gate (GSE 91–95) |
| Swing = a candle beyond the two candles on each side; break of structure = a close beyond the latest swing | Fills the missing swing and BOS definitions (G3, G6) | A standard definition, not from the sources |
| The stop is never parked just past an unswept pool | Proposal 10 | Untested |
| WEAKENING is a report-only state between on-track and invalidated | Fills "deterioration" (G4) | Exits could not create an edge (GSE 286), so prices stay as planned |
| Prices are published in eToro terms; levels from another feed are shifted by the measured offset | — | The execution feed differs from the analysis feed |
| A post-TP1 runner counts as an open position | G5 | Thesis 8 |
| Runs every hour at hh:15 GST while the market is open; continuity comes from the routine | — | XER 183; GSE 259 |
| The regime gate is computed exactly (`regime_gate.py` or the same formulas), never estimated | — | GSE 28–32, 90 |
