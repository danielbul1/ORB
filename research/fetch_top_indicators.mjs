// Find TradingView's most-liked public indicators: many category searches + Editors' Picks, dedup, rank by likes.
// Then download open-source code via pine-facade. Output: research/top_indicators.json
import { writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const { tvFetch } = await import(pathToFileURL('C:/Users/user/ORB/tools/tvfetch.mjs').href);
const { disconnect } = await import(pathToFileURL('C:/Users/user/ORB/tools/tradingview-mcp/src/connection.js').href);

const Q = ['indicator','trend','momentum','oscillator','volume','volatility','support resistance','moving average','ema','rsi','macd',
 'stochastic','bollinger','atr','supertrend','vwap','volume profile','squeeze','wavetrend','divergence','pivot','market structure',
 'smart money','order block','fair value gap','liquidity','ict','session','killzone','trend line','channel','breakout','scalping',
 'buy sell','signals','strategy','machine learning','regression','kernel','nadaraya','heikin ashi','ichimoku','fibonacci','zigzag',
 'adx','cci','williams','obv','cvd','delta','order flow','range filter','ut bot','chandelier','hull','ssl','qqe','vix fix','relative strength',
 'screener','dashboard','multi timeframe','candlestick patterns','harmonic','elliott','gann','money flow','accumulation','keltner','donchian',
 'parabolic sar','alligator','tema','lsma','linear regression','trend magic','half trend','alpha trend','twin range','lux','lazybear'];

const found = new Map();
for (let i = 0; i < Q.length; i += 10) {
  const urls = Q.slice(i, i + 10).map((q) => `/pubscripts-suggest-json/?search=${encodeURIComponent(q)}`);
  const res = await tvFetch(urls);
  for (const [u, r] of Object.entries(res)) {
    if (r.status !== 200) { console.error('fail', u, r.status); continue; }
    for (const x of JSON.parse(r.body).results) {
      const prev = found.get(x.scriptIdPart);
      if (prev) { prev.q.push(decodeURIComponent(u.split('=')[1])); continue; }
      found.set(x.scriptIdPart, { id: x.scriptIdPart, name: x.scriptName, title: x.title, author: x.author?.username,
        access: +x.access, type: +x.type, likes: +x.agreeCount || 0, recommended: !!x.isRecommended,
        kind: x.extra?.kind, q: [decodeURIComponent(u.split('=')[1])], source: x.scriptSource || '' });
    }
  }
  console.error(`queries ${i + 10}: ${found.size} unique`);
}
const all = [...found.values()].sort((a, b) => b.likes - a.likes);
// Download source for the top open-source ones that came without source.
const top = all.filter((x) => x.access === 1).slice(0, 150);
for (let i = 0; i < top.length; i += 10) {
  const need = top.slice(i, i + 10).filter((x) => !x.source);
  if (!need.length) continue;
  const res = await tvFetch(need.map((x) => `https://pine-facade.tradingview.com/pine-facade/get/${encodeURIComponent(x.id)}/last`));
  need.forEach((x, j) => { const r = Object.values(res)[j]; try { x.source = JSON.parse(r.body).source || ''; } catch { x.status = r.status; } });
}
writeFileSync('C:/Users/user/ORB/research/top_indicators.json', JSON.stringify({ queries: Q, items: all }, null, 1));
console.error(`total ${all.length}; open-source in top150 with code: ${top.filter((x) => x.source).length}`);
await disconnect();
