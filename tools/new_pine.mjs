// Put a local .pine file into the open *Untitled* Pine editor tab, save it as a new script, add it to the chart.
// Refuses unless the tab is untitled, so it can never overwrite a saved script.
// Create the tab first via the editor's script menu: Create new -> Strategy.
// Usage: node tools/new_pine.mjs pine/orb.pine
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const TV_MCP = process.env.TV_MCP_DIR || 'C:/Users/user/ORB/tools/tradingview-mcp';
const pine = await import(pathToFileURL(`${TV_MCP}/src/core/pine.js`).href);
const { evaluate } = await import(pathToFileURL(`${TV_MCP}/src/connection.js`).href);

const header = () => evaluate(`(function(){var b=[...document.querySelectorAll('button')].find(function(x){return /^(Add to chart|Update on chart|Save and add to chart)/i.test(x.textContent.trim());});
  var p=b;for(var i=0;i<6&&p;i++)p=p.parentElement;return p?p.innerText.split(String.fromCharCode(10))[0]:null;})()`);
const before = await header();
if (before !== 'Untitled script') { console.error(`ABORT: editor tab is "${before}", not an untitled script.`); process.exit(1); }
await pine.setSource({ source: readFileSync(process.argv[2], 'utf8').replace(/\r\n/g, '\n') });
console.log('save:', JSON.stringify(await pine.save()));
await new Promise((r) => setTimeout(r, 1500));
console.log('tab now:', await header());
console.log('add:', JSON.stringify(await pine.smartCompile()));
process.exit(0);
