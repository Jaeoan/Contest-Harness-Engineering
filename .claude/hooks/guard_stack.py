#!/usr/bin/env python3
"""PreToolUse 훅: 고정 스택 위반과 보호 파일 수정을 차단한다.
exit 2 → 도구 호출 차단, stderr 메시지가 Claude에게 전달된다."""
import json
import os
import re
import sys
from pathlib import Path

FORBIDDEN_PKGS = [
    "vue", "@angular/core", "svelte", "solid-js", "styled-components", "@emotion/react",
    "@emotion/styled", "bootstrap", "react-bootstrap", "@mui/material", "@chakra-ui/react",
    "antd", "jquery", "sass",
]
PKG_RE = re.compile(r'"(' + "|".join(re.escape(p) for p in FORBIDDEN_PKGS) + r')"\s*:')
INSTALL_RE = re.compile(r"\b(npm\s+(i|install|add)|pnpm\s+(add|i|install)|yarn\s+add|bun\s+add)\b(.*)")


def block(msg: str) -> None:
    print(f"[guard-stack] 차단: {msg}\n고정 스택(TypeScript+React+Tailwind)과 harness/protected.txt 규칙은 CLAUDE.md 0절 참고.", file=sys.stderr)
    sys.exit(2)


def protected_paths(root: Path) -> list[str]:
    f = root / "harness" / "protected.txt"
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", data.get("cwd", ".")))

    if tool == "Bash":
        cmd = ti.get("command", "")
        m = INSTALL_RE.search(cmd)
        if m:
            args = m.group(0).split()
            for p in FORBIDDEN_PKGS:
                if any(a == p or a.startswith(p + "@") for a in args):
                    block(f"금지 패키지 설치 시도: {p}")
        sys.exit(0)

    path = ti.get("file_path", "")
    if not path:
        sys.exit(0)
    try:
        rel = Path(path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = path

    if os.environ.get("HARNESS_AUTO") == "1":
        for p in protected_paths(root):
            if rel == p or (p.endswith("/") and rel.startswith(p)):
                block(f"자동 모드에서 보호 파일 수정 불가: {rel} → harness/proposals.md에 제안으로 작성하세요.")

    if rel.startswith("frontend/src/") and rel.endswith((".js", ".jsx")):
        block(f"프론트엔드 소스는 .ts/.tsx만 허용: {rel}")

    if rel.endswith("frontend/package.json") or rel == "package.json":
        texts = [ti.get("content", ""), ti.get("new_string", "")]
        texts += [e.get("new_string", "") for e in ti.get("edits", []) or []]
        for t in texts:
            m = PKG_RE.search(t or "")
            if m:
                block(f"금지 의존성 추가: {m.group(1)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
