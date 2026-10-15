# Look-ahead Check: does a signal use bars it could not have seen?

2026-10-15. Code: `orb/lookahead.py` (the checker), `research/lookahead_check.py` (runs it on everything below). Data: `research/lookahead_check.csv`. Idea from freqtrade's `lookahead-analysis` / `recursive-analysis`.

## Why
A screenshot of MNQ 1m with buy/sell arrows exactly on every swing high and low ("Too easy") raised the question of how the arrows got there. Pivot-based arrows are only known N bars after the swing but are drawn on the swing bar. [[Top TradingView Indicators]] found that Jev judged 54% of the top 150 indicators able to repaint, but that judgment comes from reading code. This check runs the code instead.

## How
- **Signals** (`check_signal`): cut the bar series after sampled bars t and rerun on bars 0..t, which is what a live chart has. The value at t must equal the full backtest's value at t.
- **Rule Sets** (`check_rule_set`): the Days matrix has fixed columns, so later Sessions are dropped and the cut Session is replaced from the open of bar j on by a different random path (trending hard up, then down). Everything known at that open must be unchanged:
  - every Session before the cut, in full;
  - in the cut Session, a trade entered before bar j or at its open, its direction, entry and stop;
  - an exit before bar j.
  
  Half the cuts are on the backtest's own entry bar, where a one-bar-early decision shows.
- **`orb.data.build`** (`check_build`): prior close, ATR14 and the bar matrices of Session i must not change when later Sessions are dropped.
- **Planted look-aheads** must be caught, or the script exits 1:
  - pivot arrows drawn on the pivot bar;
  - ORB v1 trading in the direction of the Session's own close;
  - ORB v1 keeping only trades whose fill bar closes in their favour.

## Result (synthetic random walk, 160 Sessions)
| Checked | Verdict |
|---|---|
| 13 indicators of `research/indicator_nq_test.py` (5m) | all pass (0/60 cuts) |
| ORB v1, Ensemble v3 Legs 5/15/30/60 | all pass (0/40) |
| `run()`: every entry type, stop, target, BE, trail and Filter | all pass (0/40) |
| `orb.data.build` per-Session context | pass (0/8) |
| Planted: pivot arrows on the pivot bar | caught 22/60 |
| Planted: direction of the Session close | caught 20/40 |
| Planted: fill bar must close in favour | caught 9/40 |

**Pivot arrows on the same random walk, gross:** drawn on the pivot bar **+376 pts/Session, Sharpe +34**. Traded when known (5 bars later) **−3.4 pts/Session, Sharpe −0.46**. A random walk has no edge, so that profit is the look-ahead alone. This is how a "Too easy" screenshot is made.

## Limits
- A pass is evidence, not proof. A look-ahead that no sampled cut exposes stays hidden.
- A stop entry filled *inside* bar j is not judged at that cut. A Filter that peeks at the close of its own stop-entry bar is therefore not caught. Open fills (candle, close, gap-through) are judged.
- Daily-P&L families (`late_day`, `fade`, `vwap_fade`) return only R per Session. For those, only a cross-Session look-ahead could be checked, so they are not in the list yet.
- `build` drops thin Sessions (< 200 bars) using the whole Session's count. This is a small selection look-ahead (holidays and data gaps), left as is.
- The run here is synthetic. On the machine with the data: `python research/lookahead_check.py --real --days 400`.
