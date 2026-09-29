This closed-source script provides a structured framework for identifying and filtering Opening Range Breakouts (ORB) across specific session windows. Rather than relying solely on price crossing a time-based threshold, this tool combines volatility, momentum, and trend-following metrics into a unified, non-repainting logic engine to evaluate the statistical probability of a breakout's continuation.

Core Breakout Logic:
The script establishes an initial High and Low boundary based on user-defined session times (e.g., the New York Open). It evaluates breakouts by requiring strict closing conditions (wick vs. body close) and utilizes a tick-based buffer zone to confirm the breach. To combat immediate fake-outs, it incorporates a "Validity Window," requiring secondary structural confirmations before a breakout is deemed active.

To filter out low-probability environments, the script integrates several standard technical indicators, combining them to assess three distinct market conditions simultaneously:

Volatility & Sizing Constraints (ATR): Breakouts are frequently invalid if the initial opening range is either too narrow (lacking volume) or too wide (exhausted). The script uses the Average True Range (ATR) to measure the raw point size of the Opening Range. If the range falls outside the predefined Min/Max ATR threshold, the setup is blocked.

Trend & Volume Alignment (EMA, VWAP, Volume SMA): To ensure a breakout has directional backing, the script requires price to be aligned with a local EMA, a Higher Timeframe (HTF) trend EMA, and the Daily VWAP. Additionally, it compares the breakout candle's volume against a 20-period Volume SMA to ensure institutional injection accompanies the structural break.

Exhaustion & Proximity Blocks (RSI, PDH/PDL): Breakouts that occur at extreme extensions often reverse. The script uses a 14-period RSI as an exhaustion block (e.g., blocking long breakouts if the RSI is already >70). It also maps the Previous Day High (PDH) and Previous Day Low (PDL), applying an ATR-based proximity buffer to block trades that break out directly into established daily liquidity levels.

Risk Management Routing:
Upon a validated breakout, the script automatically plots theoretical entry, stop-loss, and take-profit levels. Stop-losses can be routed dynamically based on recent pivot extremes, breakout candle lows, or ATR multipliers. Take-profits are mathematically projected using either fixed Risk-to-Reward (RR) ratios or dynamic ATR multiples, complete with a breakeven trailing function.