---
title: QuantFlowLabs ORB
created: 2026-09-29
tags: [orb, tradingview, quantflowlabs]
---

# QuantFlowLabs scripts

Back to [[ORB]] · Related: [[Community ORB Scripts]]

The profile <https://www.tradingview.com/u/quantflowlabs/> has **4 published scripts, all closed source**. The pine-facade API answers "User is not allowed to see source code", so only their descriptions can be studied. The full text is in `research/quantflowlabs/*_description.md`.

| Script | Type | Market / TF | Published |
|---|---|---|---|
| QuantFlowLabs ORB Suite | strategy | MNQ 15m | 2026-08-16 |
| ORB Ultimate Pro | indicator | NAS100 5m | 2026-05-05 |
| SMC Sniper Pro | indicator | NAS100 1m | 2026-05-05 (not ORB) |
| IFVG Elite Pro | indicator | XAUUSD 1m | 2026-05-05 (not ORB) |

## ORB Suite: rules stated in the description
- The opening range is **09:30–09:45 ET** on 15-minute MNQ bars. Entry needs a **confirmed candle close outside the range**, with orders processed on the bar close.
- There are 4 profiles (balanced, wide target, near target with a wider stop, and scalping, the default). The stops and targets come from "price-structure and volatility rules", which aren't disclosed.
- **Controlled second trade:** at most one more trade from the same range. It arms only after a later candle **closes back inside the range**, and it can be limited by the first trade's exit type and direction.
- Sizing is by dollar risk (default $1,000 per trade). The strategy exits at 16:00 ET. Costs are $0.75 per contract per side plus 1 tick of slippage, with 10% margin.

## ORB Ultimate Pro: filters stated in the description
- Close vs wick confirmation, a tick buffer, and a "validity window" that requires a second structural confirmation.
- A **min/max opening-range size in ATR**.
- Trend alignment: a local **EMA**, a **higher-timeframe EMA** and the **daily VWAP**, plus breakout **volume above its 20-bar SMA**.
- **RSI(14) exhaustion block** (for example, no longs above 70) and a **PDH/PDL proximity block** with an ATR buffer.
- Stops at a pivot, the breakout candle or an ATR multiple. Targets at a fixed R:R or an ATR multiple, with a breakeven trail.

## How their ideas scored on 10 years of NQ (see [[Community ORB Scripts]])
- **15-min range with close confirmation** (the Suite's core) had Sharpe 0.14 on train with a 2R target. Their undisclosed profiles may do better, but the base idea is weak on NQ.
- **VWAP alignment:** helps our 5-min winner (holdout Sharpe 1.12 → 1.25). ✅ Adopted in ORB v1.
- **RSI exhaustion block:** hurts (validation 1.50 → 1.04). ❌
- **HTF trend (20-day):** hurts on validation (0.92). ❌
- **PDH/PDL proximity block:** helps on train, hurts on validation. Mixed, so not adopted.
- **Range-size min/max vs ATR:** tested in the first grid; no robust gain.
- **Second trade:** not tested yet.
