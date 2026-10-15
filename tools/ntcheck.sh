#!/bin/bash
# Compile-check ninja/*.cs without NinjaTrader, against the stub API in tools/ntstub (C# 5, like NT8's editor).
# Needs the .NET 8 SDK. Catches syntax/type errors and misspelled members; NinjaTrader's own F5 compile is still final.
# Usage: tools/ntcheck.sh   -> prints errors, then CHECK_OK on success
out="$(mktemp -d)"
dotnet build "$(dirname "$0")/ntstub/ntstub.csproj" -nologo -v q -o "$out/bin" -p:BaseIntermediateOutputPath="$out/obj/" 2>&1 \
  | grep -E "error|warning CS" | sed 's/ \[.*csproj\]//' | sort -u
rc=${PIPESTATUS[0]}
rm -rf "$out"
test "$rc" -eq 0 && echo "CHECK_OK"
