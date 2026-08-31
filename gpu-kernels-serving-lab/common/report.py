"""Small HTML helpers shared by generated tutorial pages."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


STYLE = """
:root{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--faint:#5A6577;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--amber:#E3A63A;--rose:#E0748A;--green:#74B87A;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.72;font-size:17px}
.wrap{max-width:900px;margin:0 auto;padding:0 24px 72px}
p{color:var(--soft);margin:0 0 16px}b{color:var(--ink)}
nav{display:flex;gap:16px;flex-wrap:wrap;align-items:center;font-family:var(--mono);font-size:12.5px;padding:14px 0;border-bottom:1px solid var(--line);margin-bottom:4px}
nav .brand{color:var(--accent);text-decoration:none;font-weight:700}
nav span{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap}
nav span a{color:var(--dim);text-decoration:none}nav span a:hover{color:var(--accent)}
.kick{font-family:var(--mono);font-size:11.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent)}
h1{font-family:var(--serif);font-size:clamp(34px,6vw,54px);line-height:1.05;margin:14px 0 0;color:#fff}
h2{font-family:var(--serif);font-size:27px;margin:0 0 8px;color:#fff}
header{padding:58px 0 26px}.dek{font-size:19px;color:var(--soft);margin-top:18px;max-width:66ch}
section{padding:38px 0;border-top:1px solid var(--line)}
.eye{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim);margin-bottom:12px}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-top:14px}
.why{background:var(--bg2);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:12px;padding:16px 20px;margin:18px 0}
.why h3{margin:0 0 6px;font-size:12px;font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
.why p{margin:0;font-size:15px}.mono{font-family:var(--mono)}
table{width:100%;border-collapse:collapse;font-size:13.5px}th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);font-weight:600}
td{color:var(--soft)}td.ok{color:var(--green);font-family:var(--mono)}td.warn{color:var(--amber);font-family:var(--mono)}td.bad{color:var(--rose);font-family:var(--mono)}
pre{background:#0C1119;border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow:auto;color:var(--soft);font-size:12px}
.next{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:12px}.next a{color:var(--accent);text-decoration:none}
a{color:var(--accent)}
"""


def esc(value: Any) -> str:
    return html.escape(str(value))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def page(title: str, body: str) -> str:
    return f'<meta charset="utf-8">\n<title>{esc(title)}</title>\n<style>{STYLE}</style>\n<div class="wrap">\n{body}\n</div>\n'
