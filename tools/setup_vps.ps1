# One-shot setup of the trading VPS for Claude Code: nt8-mcp (NinjaTrader 8 bridge) + the ORB strategies.
# Run from the ORB checkout on the VPS, in a normal (not admin) PowerShell, with NinjaTrader 8 installed:
#   powershell -ExecutionPolicy Bypass -File tools\setup_vps.ps1
# What it does:
#   1. clones github.com/mlalewicz/nt8-mcp at a pinned, reviewed commit into %USERPROFILE%\nt8-mcp
#   2. installs its NT8Bridge AddOn (HTTP on localhost:7891 only; order entry is off unless you opt in)
#   3. pip-installs its MCP server and registers it with Claude Code as "nt8" (user scope)
#   4. copies ninja\ORBv1.cs and ninja\ORBEnsembleV3.cs into NinjaTrader's Strategies folder
# Afterwards: start NinjaTrader 8 (or press F5 in the NinjaScript Editor), then run "nt8 health".
# Safe to run again: it updates in place.
$ErrorActionPreference = 'Stop'
$Nt8McpCommit = '56d40c006b939081e59d4c12faeaf794772ea3ea'  # reviewed 2026-10-15; bump only after reading the diff
$Repo = Join-Path $env:USERPROFILE 'nt8-mcp'
$Custom = Join-Path $env:USERPROFILE 'Documents\NinjaTrader 8\bin\Custom'

function Need($cmd, $hint) {
	if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "$cmd not found: $hint" }
}
Need git 'install Git for Windows (https://git-scm.com/download/win)'
Need python 'install Python 3.10+ from python.org and tick "Add python.exe to PATH"'
if (-not (Test-Path $Custom)) { throw "no NinjaTrader 8 Custom folder at ${Custom}: install NinjaTrader 8 and start it once" }
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
	Write-Warning 'dotnet not found: nt_check (offline compile) will not work; everything else will. Install the .NET 8 SDK to enable it.'
}

# 1. nt8-mcp at the pinned commit
if (-not (Test-Path (Join-Path $Repo '.git'))) { git clone https://github.com/mlalewicz/nt8-mcp $Repo }
git -C $Repo fetch --quiet origin
git -C $Repo checkout --quiet $Nt8McpCommit
Write-Output "nt8-mcp at $Nt8McpCommit"

# 2. the AddOn
& (Join-Path $Repo 'scripts\install-addon.ps1')

# 3. the MCP server + Claude Code registration
python -m pip install --quiet -e (Join-Path $Repo 'server')
if (Get-Command claude -ErrorAction SilentlyContinue) {
	claude mcp get nt8 *> $null
	if ($LASTEXITCODE -ne 0) { claude mcp add --scope user nt8 -- nt8-mcp } else { Write-Output 'Claude Code already has the nt8 server' }
} else {
	Write-Warning 'claude not found: after installing Claude Code run  claude mcp add --scope user nt8 -- nt8-mcp'
}

# 4. the ORB strategies
$strategies = Join-Path $Custom 'Strategies'
foreach ($f in Get-ChildItem -Path (Join-Path $PSScriptRoot '..\ninja') -Filter '*.cs' -File | Where-Object { $_.Extension -eq '.cs' }) {
	Copy-Item -LiteralPath $f.FullName -Destination $strategies -Force
	Write-Output "installed strategy $($f.Name)"
}

Write-Output ''
Write-Output 'Done. Next: start NinjaTrader 8 (it recompiles in 20-150 s, or press F5 in the NinjaScript Editor),'
Write-Output 'then run:  nt8 health   (connection refused = NinjaTrader not running or the AddOn not compiled yet).'
