# Jev news-catalyst test is pre-registered before any headlines are pulled

Finance research (e.g. Chan 2003; arXiv 2507.04481) finds that price moves with a news catalyst tend to continue, while moves without news tend to revert. Our Edge lives on gap days that become trend days, so a gap explained by real news should suit Ensemble v2 better than an unexplained one. Code can't tell the two apart; Jev can read the headlines. Fixed on 2026-09-29, before any data is downloaded:

- **Headlines:** the GDELT DOC 2.0 API, English-language articles matching `(nasdaq OR "stock market" OR "wall street" OR "stock futures" OR "federal reserve" OR tariffs OR inflation OR earnings)`, seen between the previous Session's 16:00 ET and 09:25 ET. Up to 75 per morning, ranked by relevance. Sessions from 2017-02 (GDELT DOC coverage) onward.
- **Jev questions** (model `jev-latest`, state = the headline titles plus the gap direction and size):
  - `catalyst` (Noul): "Is there major market-moving news in `headlines` that plausibly explains a large overnight move in US stock index futures?"
  - `aligned` (Noul): "Do the news in `headlines` point toward US stocks moving in `gap_direction`?"
- **Rule under test:** Ensemble v2 trades only on Sessions where `catalyst ≥ 0.5` and `aligned ≥ 0.5`, compared with Ensemble v2 on all Sessions.
- **Pass:** the filtered Ensemble has a higher Score *and* a higher average R per traded Session than unfiltered Ensemble v2 in **both** 2017–2021 and 2022–2024, with at least 100 traded Sessions in each. 2025–26 is reported for information only.
- If it fails, Jev stays out of the trading rules and remains a research tool.

**Addendum (2026-09-30): forward arm.** GDELT throttles the history pull to about one morning every 5 minutes, and TradingView's news feed only reaches back to 2022-09, so the historical test waits for GDELT (traded Sessions first). Using TradingView headlines for 2022–24 now was rejected, because it would spend part of the test sample before the test. In addition, from 2026-09-30 every Forward Test Session gets the same two questions, the same model and the same 0.5 thresholds, with that morning's pre-open headlines from TradingView's public feed (SPX, NDX and NQ1! merged). Results go to `results/forward_news.csv`, with the headlines kept in `results/forward_news/`. The forward arm is judged on **Ensemble v3**, the current Rule Set, with the same pass bar once it has ≥ 100 traded Sessions. It logs only and never changes a trade.
