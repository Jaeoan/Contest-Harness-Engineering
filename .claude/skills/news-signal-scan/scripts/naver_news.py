#!/usr/bin/env python3
"""네이버 검색 API(뉴스)로 키워드별 기사 목록 수집 → CSV.
필요: 환경변수 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET (developers.naver.com 에서 발급)

  python3 naver_news.py "스쿨존 교통사고" "어린이보호구역 안양" --max 300 --out docs/news/schoolzone.csv

- 결과는 제목·링크·날짜·요약(API 제공 description)만 저장. 본문은 저장하지 않는다.
- 연도별 건수는 수집된 기사 기준(API는 최대 1,000건까지만 조회)이므로 '대략'으로 쓴다.
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from email.utils import parsedate_to_datetime

API = "https://openapi.naver.com/v1/search/news.json"


def fetch(query: str, start: int, display: int = 100) -> dict:
    url = f"{API}?query={urllib.parse.quote(query)}&display={display}&start={start}&sort=date"
    req = urllib.request.Request(url, headers={
        "X-Naver-Client-Id": os.environ["NAVER_CLIENT_ID"],
        "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"],
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def clean(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="+")
    ap.add_argument("--max", type=int, default=300, help="키워드당 최대 수집 건수(≤1000)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not (os.environ.get("NAVER_CLIENT_ID") and os.environ.get("NAVER_CLIENT_SECRET")):
        sys.exit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 필요합니다. 없으면 WebSearch로 진행하세요.")

    rows, seen = [], set()
    for q in a.queries:
        total = None
        for start in range(1, min(a.max, 1000) + 1, 100):
            data = fetch(q, start)
            total = data.get("total", total)
            items = data.get("items", [])
            for it in items:
                link = it.get("originallink") or it.get("link")
                if link in seen:
                    continue
                seen.add(link)
                d = parsedate_to_datetime(it["pubDate"])
                rows.append({"query": q, "date": d.strftime("%Y-%m-%d"), "title": clean(it["title"]),
                             "summary": clean(it["description"])[:120], "link": link})
            if len(items) < 100:
                break
        print(f"[{q}] API total≈{total}, 수집 {sum(r['query']==q for r in rows)}", file=sys.stderr)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["query", "date", "title", "summary", "link"])
        w.writeheader()
        w.writerows(rows)
    by_year = Counter(r["date"][:4] for r in rows)
    print("연도별(수집 기준):", dict(sorted(by_year.items())), file=sys.stderr)


if __name__ == "__main__":
    main()
