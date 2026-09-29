"""Pull the full author description out of saved TradingView script pages."""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
PAT = re.compile(r'"description":"((?:[^"\\]|\\.)*)"')

for i, name in [(1, "ORB_Suite"), (2, "ORB_Ultimate_Pro")]:
    page = (HERE / f"page{i}.html").read_text(encoding="utf8")
    best = max(PAT.findall(page), key=len, default="")
    text = json.loads(f'"{best}"')
    (HERE / f"{name}_description.md").write_text(text, encoding="utf8")
    print(f"===== {name} ({len(text)} chars)\n{text}\n")
