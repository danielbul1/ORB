# ORB

Research and trading of intraday rule sets on Nasdaq-100 futures (NQ/MNQ), starting from the opening range.

## Language

**Session**:
The New York regular trading hours of one day, 09:30–16:00 ET. A trade is always flat by the end of its Session.
_Avoid_: day (ambiguous with the 23-hour futures day), RTH day

**Opening Range (OR)**:
The high and low of the first N minutes of a Session.
_Avoid_: ORB (that names the strategy family, not the range)

**Rule Set**:
A complete, parameter-fixed description of when to enter, where the stop and target are, and when to be flat. It is backtestable without human judgment.
_Avoid_: algo, setup, model

**Filter**:
A condition known before entry that removes some of a Rule Set's trades (for example gap direction or VWAP side).

**R**:
The distance from entry to the initial stop. Trade results are measured in multiples of R, after costs.

**Edge**:
A Rule Set's positive expectancy after costs that survives the Holdout. An in-sample improvement is not an Edge.

**Train / Validate / Holdout**:
Time splits of history. Parameters are chosen on Train, confirmed on Validate, and the Holdout is looked at once for a final decision. Once a Holdout has been looked at, it is spent.
_Avoid_: test set, out-of-sample (unless naming a specific split)

**Parity**:
TradingView's strategy and the Python engine take the same trades on the same days, within one tick.

**Community Script**:
A published TradingView script by another author, studied for ideas and never copied as a whole.

**Score**:
The single number that ranks Rule Sets: profit per year when sized so the worst historical drawdown just fits the Account Profile's drawdown cap. Every result also reports its longest losing streak.
_Avoid_: best, performance (unqualified)

**Account Profile**:
The account a Rule Set is sized for: its capital, drawdown cap, instrument (MNQ) and costs. Default: $50k with a $2,000 max drawdown.

**Walk-Forward**:
Repeatedly choose parameters on the preceding years and test on the next unseen year, rolling through 2016–2024. The walk-forward years stitched together are the only in-sample evidence we trust.

**Forward Test**:
Paper trading from 2026-09-30 onward with frozen parameters. It is the final judge before real money.

**Portfolio**:
Several Rule Sets traded together. Each one earns its place by adding to the Portfolio's Score, not by its own Score alone.

**Day Type**:
A label for a Session known before its open (for example CPI day, FOMC day, mega-cap earnings day), used to switch Rule Sets on or off.
