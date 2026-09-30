"""Best Lucid Flex setup: account x Rule Set x eval $/R x funded $/R, judged on 2016-24 AND 2025-26.

Ranking = the WORSE of the two eras' net $/month per slot (1-year rolling windows in both eras so they are
comparable). Account rules: Lucid Flex (review sites, 2026-09-30). Fees: only the 50K list price is known
($136); the others are assumed from the LucidPro price ladder ($90-$245), all with a 40% code; reset = eval fee.
Usage: python research/prop_search.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import beat_v3 as B  # noqa: E402
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.families import ORB_V1  # noqa: E402
from orb.propscore import Flex, prop_score  # noqa: E402

CODE = 0.6  # typical 40% discount code
ACCOUNTS = {  # target, max loss, min payout day, payout cap, list fee (assumed except 50K)
    "Flex 25K": (1250, 1000, 100, 1000, 100),
    "Flex 50K": (3000, 2000, 150, 2000, 136),
    "Flex 100K": (6000, 3000, 200, 2500, 200),
    "Flex 150K": (9000, 4500, 250, 3000, 245),
}
USD_PER_LEG_MNQ = 80  # ~risk of 1 MNQ at a 0.10 ATR stop; v3 R = mean of 4 Legs, so 1 MNQ/Leg = $320/R


def main():
    d = L.load()
    E = L.eras(d)
    v3 = B.combine(B.legs(d))
    v1r = run(d, **ORB_V1, **L.COST)
    v1 = np.where(v1r["ok"], v1r["r"], 0.0)
    sets = {"Ensemble v3": (v3, 4), "ORB v1": (v1, 1), "v1 + v3": (None, None)}
    eras = {"2016-24": E["B 2016-24"], "2025-26": E["spent 25-26"]}
    rows = []
    for acc, (tgt, mll, day_min, cap, fee) in ACCOUNTS.items():
        rules = Flex(target=tgt, mll=mll, day_min=day_min, payout_cap=cap,
                     eval_fee=fee * CODE, reset_fee=fee * CODE)
        for name, (x, n_legs) in sets.items():
            for ke in (1, 2, 3, 4, 6):
                for kf in (1, 2, 3, 4, 6):
                    if name == "v1 + v3":  # ke MNQ on v1 and ke MNQ per v3 Leg
                        ue, uf = 1.0, 1.0
                        series = lambda m, k: (v1[m] * k * USD_PER_LEG_MNQ + v3[m] * k * 4 * USD_PER_LEG_MNQ)
                    else:
                        series = None
                        ue = ke * n_legs * USD_PER_LEG_MNQ
                        uf = kf * n_legs * USD_PER_LEG_MNQ
                    micros = {"Ensemble v3": 4, "ORB v1": 1, "v1 + v3": 5}[name] * max(ke, kf)
                    if micros > {"Flex 25K": 20, "Flex 50K": 40, "Flex 100K": 60, "Flex 150K": 100}[acc]:
                        continue
                    out = {"account": acc, "rule_set": name, "eval MNQ": ke, "funded MNQ": kf}
                    for ek, m in eras.items():
                        if series is None:
                            p = prop_score(x[m], ue, uf, rules, horizon=252)
                        else:  # $ series: pass dollars as R with $1/R, eval and funded sizes via ratio
                            p = prop_score(series(m, 1), ke, kf, rules, horizon=252)
                        out[f"$/mo {ek}"] = p["net_per_month"]
                        out[f"p10 {ek}"] = p["p10"]
                        out[f"losing {ek}"] = p["losing_years"]
                        out[f"busts/yr {ek}"] = p["funded_busts"]
                    out["worse era $/mo"] = min(out["$/mo 2016-24"], out["$/mo 2025-26"])
                    rows.append(out)
    df = pd.DataFrame(rows).sort_values("worse era $/mo", ascending=False)
    df.to_csv(ROOT / "results" / "prop_search.csv", index=False)
    pd.set_option("display.width", 250)
    cols = ["account", "rule_set", "eval MNQ", "funded MNQ", "$/mo 2016-24", "p10 2016-24", "losing 2016-24",
            "$/mo 2025-26", "p10 2025-26", "losing 2025-26", "worse era $/mo"]
    print(f"{len(df)} setups searched\n\nTOP 20 by the worse era:")
    print(df[cols].head(20).to_string(index=False))
    print("\nBest per account:")
    print(df.groupby("account", sort=False).head(1)[cols].to_string(index=False))
    print("\nCurrent plan (Flex 150K, v3, eval 3 / funded 2 MNQ per Leg):")
    print(df[(df.account == "Flex 150K") & (df.rule_set == "Ensemble v3") & (df["eval MNQ"] == 3)
             & (df["funded MNQ"] == 2)][cols].to_string(index=False))


if __name__ == "__main__":
    main()
