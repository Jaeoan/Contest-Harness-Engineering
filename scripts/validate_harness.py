#!/usr/bin/env python3
"""하네스 무결성 검사. 하네스를 고친 뒤와 PR CI에서 실행. 실패 시 exit 1."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def fm(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        errors.append(f"{path}: frontmatter 없음")
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


# 1) 에이전트
for p in sorted((ROOT / ".claude/agents").glob("*.md")):
    f = fm(p)
    if f.get("name") != p.stem:
        errors.append(f"{p.name}: name({f.get('name')}) != 파일명")
    if len(f.get("description", "")) < 30:
        errors.append(f"{p.name}: description이 너무 짧음(트리거 실패 위험)")

# 2) 스킬 (ext- 접두사는 외부 설치본이라 name 검사 생략)
for d in sorted((ROOT / ".claude/skills").iterdir()):
    s = d / "SKILL.md"
    if not s.exists():
        errors.append(f"{d.name}: SKILL.md 없음")
        continue
    f = fm(s)
    if not d.name.startswith("ext-") and f.get("name") != d.name:
        errors.append(f"{d.name}: name({f.get('name')}) != 폴더명")
    for ref in re.findall(r"`((?:references|scripts)/[\w./-]+)`", s.read_text(encoding="utf-8")):
        if not (d / ref).exists():
            errors.append(f"{d.name}: 참조 파일 없음 {ref}")

# 3) 고정 스택 규칙 보존
claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
for must in ["TypeScript(strict) + React + Tailwind CSS", "Spring Boot 3.x", "harness/protected.txt"]:
    if must not in claude_md:
        errors.append(f"CLAUDE.md: 필수 규칙 누락 '{must}'")
lock = (ROOT / ".claude/skills/frontend-stack-lock/SKILL.md").read_text(encoding="utf-8")
for must in ["**TypeScript**", "**React**", "**Tailwind CSS**"]:
    if must not in lock:
        errors.append(f"frontend-stack-lock: 고정 항목 누락 {must}")

# 4) 설정 파일
try:
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    for group in settings.get("hooks", {}).values():
        for g in group:
            for h in g.get("hooks", []):
                for m in re.findall(r"\.claude/hooks/[\w.-]+", h.get("command", "")):
                    if not (ROOT / m).exists():
                        errors.append(f"settings.json: 훅 파일 없음 {m}")
except Exception as e:
    errors.append(f"settings.json: {e}")

# 5) 보호 목록 경로 존재
for line in (ROOT / "harness/protected.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and not (ROOT / line.rstrip("/")).exists():
        errors.append(f"protected.txt: 존재하지 않는 경로 {line}")

if errors:
    print("VALIDATION FAILED")
    print("\n".join(f"- {e}" for e in errors))
    sys.exit(1)
print("VALIDATION OK")
