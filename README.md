# ORB

Opening Range Breakout research and strategy for NQ/MNQ.

- `orb/` Python engine: `data.py` (1m bars to RTH day matrix), `backtest.py` (vectorized ORB), `noise.py` (noise-area momentum), `grid.py` (train/validate/holdout grid)
- `pine/orb.pine` TradingView strategy "ORB v0", in parity with the engine
- `tools/` TradingView bridge (tradingview-mcp submodule) and CDP helpers: `bt.mjs` backtest/grid on the live chart, `push_pine.mjs`, `new_pine.mjs`, `export_bars.mjs`
- `vault/` Obsidian vault: literature review and results

Setup: `py -3.13 -m venv .venv && .venv/Scripts/pip install numpy pandas pyarrow`; NQ 1m data is read from `C:\Users\user\Model\data\nq_1m_lse.csv`.
Run: `.venv/Scripts/python -m orb.grid core|filters`.
