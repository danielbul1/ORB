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

**Alt Baseline**:
alttrading.ai's published Rule Sets (ATX ORB Sniper V1–V4, Mike's ORB Signal Pro, and the rules stated in their prose), reproduced as they run and measured for comparison only. Never traded; spends no Hypothesis.
_Avoid_: Alt strategy, B1 (their unpublished system, which we cannot reproduce)

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

**Portfolio Member**:
One Rule Set inside a Portfolio. A candidate is judged by what it adds to the Portfolio (its Score and Prop Score), and low correlation with the other members counts in its favour.
_Avoid_: member (alone), which is ambiguous with Leg

**Leg**:
One of the fixed parts inside an ensemble Rule Set, such as the ORB-15 Leg of Ensemble v3 (OR lengths 5/15/30/60). Sizing is quoted per Leg ("1 MNQ per Leg").
_Avoid_: member (older notes use it with this meaning)

**Hypothesis**:
One pre-registered idea (a Filter, Day Type or Portfolio Member), written down with its rule, parameters and pass bar before it is run. Each budget is fixed by an ADR: 10 to beat Ensemble v3 (ADR 0006, spent), 5 for the Alt Trading track (ADR 0008).
_Avoid_: idea, tweak (for anything that gets backtested)

**Day Type**:
A label for a Session known before its open (for example CPI day, FOMC day, mega-cap earnings day), used to switch Rule Sets on or off.

**Prop Score**:
The objective for prop-firm trading: expected net dollars per month across the Account Portfolio, meaning 90% of payouts received minus evaluation and reset fees, simulated under the firm's exact evaluation *and* funded rules. It replaces Score when choosing how to trade prop accounts. Score still judges whether a Rule Set has an Edge.

**Evaluation**:
A paid prop-firm challenge. It is passed by reaching the profit target without breaching the max loss (and, on Lucid Flex, with the largest day ≤ 50% of profit). No money is paid out.

**Funded Account**:
A prop account that has passed its Evaluation. Money leaves it only through Payouts, under the firm's payout rules.

**Payout**:
A withdrawal from a Funded Account. On Lucid Flex 50K a request needs 5 days of ≥ $150 in the cycle; it is capped at 50% of profit and $2,000, and the trader receives 90%.

**Account Portfolio**:
All prop accounts traded at once (Lucid: up to 5 funded, 10 in total per household). They may differ in Rule Set, size and start date so that busts and payouts don't cluster.

**Kill Switch**:
Conditions fixed in advance (ADR 0005) under which live trading stops for investigation. A losing streak alone is not one.

**Scaling Ladder**:
The fixed order in which size and accounts grow (ADR 0005). Each rung is unlocked only by evidence from the previous one.
