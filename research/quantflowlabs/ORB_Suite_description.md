QuantFlowLabs ORB Suite is a Pine Script v6 intraday opening-range strategy designed for CME Micro E-mini Nasdaq-100 futures (MNQ) on standard 15-minute candles.

## What the strategy does

The strategy records the opening range from 09:30 to 09:45 in the America/New_York timezone. After the range is complete, it evaluates confirmed candle closes outside the range. A qualifying breakout must satisfy the timing and market-condition rules of the selected profile before an order is generated.

The script coordinates the complete trade lifecycle in one stateful process: opening-range construction, breakout eligibility, position sizing, entry confirmation, protective levels, session limits, optional second-trade eligibility, alerts, and end-of-day closure. Provisional planning levels are kept separate from confirmed strategy orders so an intrabar preview is not presented as a completed signal.

## Profiles and customization

Four named profiles provide different trade-management styles: balanced risk and target distance, a wider-target approach, a nearer-target approach with more room for price movement, and compact scalping management. These profiles are intended for MNQ on the 15-minute timeframe. Their internal settings are isolated from the manual Custom controls.

Custom mode exposes the session, entry, exit, timing, filter, and display controls for users who want to define their own configuration. Changing Custom inputs does not alter a named profile.

The optional Controlled Second Trade feature allows no more than one additional trade from the same opening range. It can be restricted by the first trade's exit type and by breakout direction. Before the additional trade can arm, a later confirmed candle must close back inside the opening range. The next qualifying breakout must then occur before the mandatory end-of-day cutoff.

## Position sizing and trade management

The strategy supports fixed-quantity sizing and dollar-risk sizing. Dollar-risk sizing uses the planned stop distance and the symbol point value, rounds quantity to the executable quantity step, and applies a user-defined safety cap. Because futures contracts trade in whole units and fills can differ from chart prices, realized cash risk can differ from the requested amount.

Stops and targets are created from the selected profile's price-structure and volatility rules. Confirmed entry, stop, and target levels can be displayed on the chart. The risk panel reports the planned quantity and estimated cash risk. Faded preview levels on the live candle are planning information only; users should wait for a confirmed candle-close state before treating a setup as active.

The supplied profiles flatten open positions at the adjustable end-of-day cutoff, which defaults to 16:00 America/New_York. Users should leave an appropriate buffer before any broker or evaluation-account liquidation deadline.

## Default chart and strategy properties

- Market: CME MNQ continuous contract
- Chart type: Standard candles
- Timeframe: 15 minutes
- Opening range: 09:30-09:45 America/New_York
- Default profile: Scalping
- Controlled Second Trade: Off
- Position sizing: Dollar Risk
- Requested cash risk: USD 1,000 per trade before costs and quantity rounding
- Initial capital: USD 100,000
- Commission: USD 0.75 per contract per fill
- Slippage: 1 tick
- Simulated long and short margin requirement: 10%
- Order processing: On confirmed candle close
- End-of-day cutoff: 16:00 America/New_York

Use the same market, timeframe, chart type, and Properties values when reviewing the published Strategy Report. Actual commissions, exchange fees, margin requirements, fills, and slippage depend on the broker, data feed, and account.

## Alerts and displays

The script provides confirmed long and short alert conditions and can produce dynamic messages containing the planned entry, stop, and target. The opening-range dashboard, risk calculator, trade-level plots, and preview display can be enabled or disabled independently without changing the named profile logic.

## Limitations

Historical strategy orders are simulated from chart data and the stated Properties assumptions; they are not live executions. Continuous futures contracts can contain rollover adjustments. Higher-timeframe conditions may continue changing until their source candle closes. Intrabar previews can disappear before candle close and do not represent confirmed orders. Dollar-risk sizing is approximate because of contract granularity, price gaps, and slippage.

This strategy is a research and decision-support tool. It does not predict future market behaviour, guarantee a particular outcome, or replace independent risk assessment.
