#!/usr/bin/env python3
"""Refresh the Repo constellation table in README.md from GitHub API."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

USERNAME = "CircuitFae"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- REPO-TABLE-START -->"
END = "<!-- REPO-TABLE-END -->"

# Curated blurbs override empty or generic GitHub descriptions.
DESCRIPTIONS: dict[str, str] = {
    "InterviewAI-Pro": "GenAI interview prep · resume analyzer · voice mocks · coding judge",
    "trading-engine-simulator": "Java 17 · multithreaded exchange · FIFO & pro-rata matching",
    "AI-medichatbot-AURA-": "Streamlit · IBM Cloud · NLP medichatbot (AURA)",
    "decentralized-blue-carbon-mrv": "SupraThon · React · Ethereum · blue carbon MRV",
    "SudokuSolverPRNG": "C++ PRNG Sudoku engine · backtracking in milliseconds",
    "Ai---Travel-Planner": "AI travel planning experiments",
    "AI-Debate-platform-": "Debate tooling with models in the loop",
    "Layers_Shop_Website": "E-commerce UI · layered product showcase",
    "Youtube_Chatbot": "Python chatbot wired to YouTube context",
    "flood-risk-classification-metro-manila": "MATLAB · flood risk classification · Metro Manila",
    "Paytm_clone": "TailwindCSS Paytm clone · learning build",
    "CircuitFae": "This profile README · animations & stats",
}

SKIP = {USERNAME}  # profile repo itself


def fetch_repos() -> list[dict]:
    req = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "CircuitFae-readme-bot"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def blurb(repo: dict) -> str:
    name = repo["name"]
    if name in DESCRIPTIONS:
        return DESCRIPTIONS[name]
    desc = (repo.get("description") or "").strip()
    lang = repo.get("language") or ""
    if desc and lang:
        return f"{desc} · {lang}"
    if desc:
        return desc
    if lang:
        return f"{lang} project"
    return "Open source build"


def row(repo: dict) -> str:
    name = repo["name"]
    url = repo["html_url"]
    text = blurb(repo)
    return (
        f'<tr><td align="left"><a href="{url}"><b style="color:#e2d9f3;">{name}</b></a></td>'
        f'<td align="left" style="color:#c4b5fd;">{text}</td>'
        f'<td align="center"><a href="{url}">'
        f'<img src="https://img.shields.io/badge/code-181717?style=flat-square&logo=github&logoColor=white" '
        f'alt="Open {name} repo"/></a></td></tr>'
    )


def badge(repo: dict) -> str:
    name = repo["name"]
    url = repo["html_url"]
    label = name.replace("-", " ")[:18]
    colors = ["B57BFF", "7C3AED", "F0ABFC", "4361EE", "4CC9F0", "f72585", "b5179e", "fcd34d", "7209b7"]
    color = colors[hash(name) % len(colors)]
    return (
        f'<a href="{url}"><img src="https://img.shields.io/badge/{label.replace(" ", "%20")}-'
        f'{color}?style=for-the-badge&logo=github&logoColor=white&labelColor=0d0d2b" alt="{name}"/></a>'
    )


def build_table(repos: list[dict]) -> str:
    featured = [r for r in repos if not r.get("fork") and r["name"] not in SKIP]
    featured.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
    rows = "\n".join(row(r) for r in featured)
    badges = "\n".join(f"  {badge(r)}" for r in featured[:9])
    return f"""{START}
<table width="100%" align="center" cellpadding="12" cellspacing="0" border="0">
<tr bgcolor="#1a0a2e">
<th align="left" width="38%" style="color:#fcd34d;">Repository</th>
<th align="left" width="52%" style="color:#b57bff;">What lives there</th>
<th align="center" width="10%" style="color:#fcd34d;">Open</th>
</tr>
{rows}
</table>

<div align="center"><br/>
{badges}
</div>
{END}"""


def patch_readme(block: str) -> str:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        print("Markers not found in README.md", file=sys.stderr)
        sys.exit(1)
    return pattern.sub(block, text)


def main() -> None:
    try:
        repos = fetch_repos()
    except urllib.error.URLError as exc:
        print(f"GitHub API error: {exc}", file=sys.stderr)
        sys.exit(1)
    block = build_table(repos)
    README.write_text(patch_readme(block), encoding="utf-8")
    count = len([r for r in repos if not r.get("fork") and r["name"] not in SKIP])
    print(f"Updated repo table with {count} repositories.")


if __name__ == "__main__":
    main()
