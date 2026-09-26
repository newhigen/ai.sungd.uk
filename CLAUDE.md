# ai.sungd.uk

Claude Code, Codex, Antigravity CLI 릴리스에서 오늘 써 볼 것을 체크리스트로 준다. 단일 정적 HTML, 빌드 없음.

## 실행

```sh
python3 -m http.server   # 로컬 확인
```

## 어디를 고치나

```
index.html    전부 (화면, 스타일, 스크립트 + <div id="data"> 안의 버전 블록)
scripts/      갱신 자동화 — update_changelog.py, update_codex.py, update_agy.py, collect_blog.py, curate_prompt.md
```

## 배포

GitHub Pages 가 main 루트를 그대로 서빙한다. `.github/workflows/daily-update.yml` 이 매시 5분에 돈다.

1. 버전 수집 — 새 버전이 없으면 여기서 끝나고 비용이 없다.
2. 글 수집 — Anthropic, OpenAI 새 글을 `new_blog.json` 으로.
3. 큐레이션 — 새 버전이 있을 때만 헤드리스 `claude -p` 가 `curate_prompt.md` 대로 `index.html` 을 고친다.

인증은 repo Secrets 의 `CLAUDE_CODE_OAUTH_TOKEN` (구독 토큰, API 키 아님).

## ⚠ 경고

- `<div id="data">` 는 화면에 안 보이지만 지우면 안 된다. 갱신 스크립트가 여기에 새 버전을 꽂고 큐레이션이 여기서 원본을 읽는다.
- 구간 표식(`<!--CC-DATA-->`, `<!--CX-DATA-->`, `<!--AG-DATA-->`)은 스크립트가 경계로 쓴다. 그대로 둔다.
- 3단계가 `index.html` 을 직접 고친다. 뒤이은 JS 무결성 검사에 실패하면 자동으로 되돌린다.
