"""Prop Score (docs/adr/0004): net $/month from one Lucid Flex account slot, simulated through the full lifecycle.

Lifecycle of a slot (official Lucid help-center rules, checked 2026-09-30, Flex 50K defaults):
  EVALUATION: pay the fee; end-of-day trailing max loss (locks at start + $100 once the peak is high enough);
    pass at target when the largest day <= 50% of profit (otherwise keep trading); bust -> pay a reset, restart.
  FUNDED: new account balance; same trailing max loss. A payout cycle needs >= 5 days with day P&L >= $150 and
    positive profit; then request payout = min(50% of profit, cap) if >= $500. The trader receives 90%. After a
    payout the balance drops by the payout and the max-loss floor moves to the locked level (+$100).
    Bust -> buy a new evaluation. After `max_payouts` payouts the account goes live: counted as done and the
    slot restarts with a new evaluation (live money is not modelled; a conservative choice).
Daily P&L = daily R x dollars per R (separate sizes for evaluation and funded). Intraday drawdown not modelled.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class Flex:
    target: float = 3000
    mll: float = 2000
    lock: float = 100
    consistency: float = 0.5
    day_min: float = 150
    days_needed: int = 5
    payout_cap: float = 2000
    payout_frac: float = 0.5
    payout_min: float = 500
    split: float = 0.9
    max_payouts: int = 5
    eval_fee: float = 82.0     # $136 list with a typical 40% code
    reset_fee: float = 95.0


def simulate(daily_r, usd_eval, usd_funded, rules=Flex(), start=0, n_days=None):
    """Run one account slot from `start` for `n_days` Sessions. Returns cash flows and event counts."""
    x = np.asarray(daily_r, float)
    end = len(x) if n_days is None else min(len(x), start + n_days)
    cash = -rules.eval_fee
    ev = dict(evals=1, resets=0, passes=0, funded_busts=0, payouts=0, paid=0.0, live=0)
    phase, eq, peak, best, floor = "eval", 0.0, 0.0, 0.0, -rules.mll
    good_days, n_payouts = 0, 0
    for t in range(start, end):
        pnl = x[t] * (usd_eval if phase == "eval" else usd_funded)
        eq += pnl
        best = max(best, pnl)
        if eq <= floor:                                   # max-loss breach (end of day)
            if phase == "eval":
                cash -= rules.reset_fee
                ev["resets"] += 1
            else:
                cash -= rules.eval_fee
                ev["evals"] += 1
                ev["funded_busts"] += 1
            phase, eq, peak, best, floor, good_days, n_payouts = "eval", 0.0, 0.0, 0.0, -rules.mll, 0, 0
            continue
        peak = max(peak, eq)
        floor = min(max(floor, peak - rules.mll), rules.lock)
        if phase == "eval":
            if eq >= rules.target and best <= rules.consistency * eq:
                ev["passes"] += 1
                phase, eq, peak, best, floor, good_days, n_payouts = "funded", 0.0, 0.0, 0.0, -rules.mll, 0, 0
            continue
        if pnl >= rules.day_min:
            good_days += 1
        if good_days >= rules.days_needed and eq > 0:
            amount = min(rules.payout_frac * eq, rules.payout_cap)
            if amount >= rules.payout_min:
                cash += rules.split * amount
                ev["payouts"] += 1
                ev["paid"] += rules.split * amount
                eq -= amount
                floor = rules.lock if eq > rules.lock else eq - 1e-9  # loss limit moves to the locked level
                floor = min(floor, rules.lock)
                good_days = 0
                n_payouts += 1
                if n_payouts >= rules.max_payouts:          # goes live: stop modelling, restart the slot
                    ev["live"] += 1
                    cash -= rules.eval_fee
                    ev["evals"] += 1
                    phase, eq, peak, best, floor, good_days, n_payouts = "eval", 0.0, 0.0, 0.0, -rules.mll, 0, 0
    ev["cash"] = cash
    return ev


def prop_score(daily_r, usd_eval, usd_funded, rules=Flex(), horizon=252, step=21):
    """Average net $/month over rolling `horizon`-Session windows starting every `step` Sessions."""
    x = np.asarray(daily_r, float)
    starts = range(0, len(x) - horizon, step)
    runs = [simulate(x, usd_eval, usd_funded, rules, s, horizon) for s in starts]
    per_month = np.array([r["cash"] for r in runs]) / (horizon / 21)
    return dict(net_per_month=round(float(per_month.mean()), 0), p10=round(float(np.percentile(per_month, 10)), 0),
                p90=round(float(np.percentile(per_month, 90)), 0), losing_years=round(float((per_month < 0).mean()), 2),
                payouts_per_year=round(float(np.mean([r["payouts"] for r in runs])), 1),
                evals_per_year=round(float(np.mean([r["evals"] + r["resets"] for r in runs])), 1),
                funded_busts=round(float(np.mean([r["funded_busts"] for r in runs])), 2))
