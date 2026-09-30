"""Prop-firm evaluation simulator: start an evaluation on every historical Session and replay the daily P&L.

Rules modelled: profit target; end-of-day trailing max loss that stops trailing at `lock` above the start
(Lucid: start + $100); a daily loss limit that is either hard (breach ends the evaluation) or soft (the day
is flattened at the limit and trading resumes next day, Lucid-style); minimum trading days; and an optional
consistency rule checked when the target is reached (largest day <= x of total profit; otherwise keep
trading). Daily P&L = daily R x dollars per R. Intraday drawdown is not modelled.
"""
import numpy as np

LUCID = {  # evaluation rules by account size (third-party summary dated 2026-09-10; confirm with Lucid)
    "Pro 50K": dict(target=3000, trail_dd=2000, daily_loss=1200, dll="soft", consistency=None),
    "Pro 100K": dict(target=6000, trail_dd=3000, daily_loss=1800, dll="soft", consistency=None),
    "Pro 150K": dict(target=9000, trail_dd=4500, daily_loss=2700, dll="soft", consistency=None),
    "Flex 50K": dict(target=3000, trail_dd=2000, daily_loss=None, dll=None, consistency=0.5),
    "Flex 100K": dict(target=6000, trail_dd=3000, daily_loss=None, dll=None, consistency=0.5),
    "Flex 150K": dict(target=9000, trail_dd=4500, daily_loss=None, dll=None, consistency=0.5),
}


def evaluate(daily_r, usd_per_r, target=3000, trail_dd=2000, daily_loss=1000, dll="hard", min_days=1,
             consistency=None, lock=100.0, max_days=252):
    x = np.asarray(daily_r, float) * usd_per_r
    n = len(x)
    passed, bust, still, days = 0, 0, 0, []
    for s in range(n):
        eq = peak = best = 0.0
        floor = -trail_dd
        traded = 0
        result = None
        for t in range(s, min(n, s + max_days)):
            pnl = x[t]
            if daily_loss and pnl <= -daily_loss:
                if dll == "hard":
                    result = "bust"
                    break
                pnl = -daily_loss                      # soft limit: flattened at the limit, resume tomorrow
            eq += pnl
            if pnl != 0:
                traded += 1
                best = max(best, pnl)
            if eq <= floor:
                result = "bust"
                break
            peak = max(peak, eq)
            floor = min(max(floor, peak - trail_dd), lock)  # trails end-of-day, locks at start + lock
            if eq >= target and traded >= min_days and (consistency is None or best <= consistency * eq):
                result = "pass"
                days.append(t - s + 1)
                break
        if result == "pass":
            passed += 1
        elif result == "bust":
            bust += 1
        else:
            still += 1
    return dict(pass_rate=round(passed / n, 3), bust_rate=round(bust / n, 3), unresolved=round(still / n, 3),
                median_days=int(np.median(days)) if days else None)
