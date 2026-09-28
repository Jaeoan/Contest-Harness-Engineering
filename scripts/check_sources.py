#!/usr/bin/env python3
"""감시 소스 변경 감지 (LLM 호출 없음 → 매시간 돌려도 비용 0).

  python3 scripts/check_sources.py                 # 변경 감지 → harness/pending_changes.json
  python3 scripts/check_sources.py --commit-state  # pending을 state에 확정

출력 첫 줄: BASELINE | NO_CHANGES | CHANGES <n>
GITHUB_TOKEN 환경변수가 있으면 사용 (시간당 한도 60 → 5000).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "harness" / "sources.json"
STATE = ROOT / "harness" / "state.json"
PENDING = ROOT / "harness" / "pending_changes.json"


def gh(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "harness-watch"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def snapshot(src: dict) -> dict:
    repo = src["repo"]
    out = {}
    if "commits" in src.get("watch", []):
        q = "?per_page=1" + (f"&path={urllib.parse.quote(src['path'])}" if src.get("path") else "")
        c = gh(f"https://api.github.com/repos/{repo}/commits{q}")
        if c:
            out["commit"] = c[0]["sha"]
            out["commit_msg"] = c[0]["commit"]["message"].splitlines()[0][:120]
    if "releases" in src.get("watch", []):
        r = gh(f"https://api.github.com/repos/{repo}/releases/latest")
        if r:
            out["release"] = r["tag_name"]
            out["release_url"] = r.get("html_url")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit-state", action="store_true")
    a = ap.parse_args()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}

    if a.commit_state:
        if PENDING.exists():
            for ch in json.loads(PENDING.read_text())["changes"]:
                state[ch["repo"]] = ch["new"]
            PENDING.unlink()
        STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        print("STATE_COMMITTED")
        return

    sources = json.loads(SOURCES.read_text())["repos"]
    first = not state
    changes, errors = [], []
    limited = False
    for src in sources:
        try:
            snap = snapshot(src)
        except urllib.error.HTTPError as e:
            errors.append(f"{src['repo']}: {e}")
            if e.code in (403, 429):  # 한도 초과 → 나머지는 다음 시간에
                errors.append("RATE_LIMITED (GITHUB_TOKEN 설정 권장)")
                limited = True
                break
            continue
        except Exception as e:  # 네트워크 오류는 다음 시간에 재시도
            errors.append(f"{src['repo']}: {e}")
            continue
        old = state.get(src["repo"], {})
        keys = [k for k in ("commit", "release") if k in snap]
        if first or not old:
            state[src["repo"]] = snap
            continue
        if any(snap.get(k) != old.get(k) for k in keys):
            ch = {"repo": src["repo"], "team": src.get("team"), "why": src.get("why"), "old": old, "new": snap}
            if old.get("commit") and snap.get("commit") and old["commit"] != snap["commit"]:
                ch["compare_url"] = f"https://github.com/{src['repo']}/compare/{old['commit'][:12]}...{snap['commit'][:12]}"
            changes.append(ch)

    if errors:
        print("WARN " + " | ".join(errors), file=sys.stderr)
    if first:
        STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        print(f"BASELINE {len(state)}")
        return
    if not changes and limited:
        print("RATE_LIMITED")
        return
    if not changes:
        STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))  # 신규 소스 반영
        print("NO_CHANGES")
        return
    PENDING.write_text(json.dumps({"detected_at": datetime.now(timezone.utc).isoformat(), "changes": changes},
                                  indent=2, ensure_ascii=False))
    print(f"CHANGES {len(changes)}" + (" (partial: rate limited)" if limited else ""))
    for c in changes:
        print(f"- {c['repo']} ({c['team']}): {c['old'].get('release') or c['old'].get('commit','')[:8]} -> "
              f"{c['new'].get('release') or c['new'].get('commit','')[:8]} {c['new'].get('commit_msg','')}")


if __name__ == "__main__":
    main()
