"""Refresh the "Latest work" table in the profile README.

Lists the most recently updated public repositories (excluding forks and this
profile repo) and rewrites the block between the LATEST-REPOS markers.
"""
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "MuskaanDhanda")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
LIMIT = 6
README = "README.md"
START, END = "<!-- LATEST-REPOS:START -->", "<!-- LATEST-REPOS:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=100"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def render(repos):
    rows = ["| Repository | What it is | Tech | Last updated |",
            "|------------|------------|------|--------------|"]
    for r in repos:
        desc = (r.get("description") or "").replace("|", "\\|")
        lang = r.get("language") or "Docs"
        date = r["pushed_at"][:10]
        rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {date} |")
    return "\n".join(rows)


def main():
    repos = [r for r in fetch_repos()
             if not r["fork"] and not r["private"] and not r["archived"]
             and r["name"].lower() != USER.lower()][:LIMIT]
    with open(README, encoding="utf-8") as f:
        text = f.read()
    block = f"{START}\n{render(repos)}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.S)
    if new != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print("README updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
