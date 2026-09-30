// Fetch TradingView URLs from inside the logged-in TV Desktop page (CDP), print JSON {url: {status, body}}.
//   node tools/tvfetch.mjs <url> [url...]      (relative URLs resolve against tradingview.com)
import { pathToFileURL } from 'node:url';
const TV_MCP = process.env.TV_MCP_DIR || 'C:/Users/user/ORB/tools/tradingview-mcp';
const { evaluateAsync, disconnect } = await import(pathToFileURL(`${TV_MCP}/src/connection.js`).href);
export async function tvFetch(urls) {
  return evaluateAsync(`(async()=>{const out={};for(const u of ${JSON.stringify(urls)}){try{const r=await fetch(u,{credentials:'include'});out[u]={status:r.status,body:await r.text()};}catch(e){out[u]={status:0,body:String(e)};}}return JSON.stringify(out);})()`).then(JSON.parse);
}
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const res = await tvFetch(process.argv.slice(2));
  process.stdout.write(JSON.stringify(res));
  await disconnect();
}
