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
              소식 — collect_news.py(수집) → news_prompt.md(claude -p 가 가름) → render_news.py(news.json 에 쌓고 그림)
news.json     소식 탭 원본. 6주치. render_news.py 만 고친다
              모델 현황 — update_models.py 가 Artificial Analysis 출시일과 세 노트로 「모델」 탭 맨 위를 매시 다시 그린다
models.json   모델 출시일과 Terminal-Bench 4.0 점수. update_models.py 가 쌓는다
```

## 배포

GitHub Pages 가 main 루트를 그대로 서빙한다. `.github/workflows/daily-update.yml` 이 매시 5분에 돈다.

1. 버전 수집 — 새 버전이 없으면 여기서 끝나고 비용이 없다.
2. 글 수집 — Anthropic, OpenAI 새 글을 `new_blog.json` 으로.
3. 큐레이션 — 새 버전이 있을 때만 헤드리스 `claude -p` 가 `curate_prompt.md` 대로 `index.html` 을 고친다.

인증은 repo Secrets 의 `CLAUDE_CODE_OAUTH_TOKEN` (구독 토큰, API 키 아님).

## ⚠ 경고

- `<div id="data">` 는 화면에 안 보이지만 지우면 안 된다. 갱신 스크립트가 여기에 새 버전을 꽂고 큐레이션이 여기서 원본을 읽는다.
- 구간 표식(`<!--CC-DATA-->`, `<!--CX-DATA-->`, `<!--AG-DATA-->`, `<!--NEWS-->`, `<!--MODELS-STATUS-->`)은 스크립트가 경계로 쓴다. 그대로 둔다.
- 탭은 홈, 새로 나온 것, 모델, 소식이다. 홈은 마지막 `<script>` 의 `home()` 이 페이지가 뜰 때 켜고 조립한다(이번 주 써 볼 것을 옮기고, `.mh` 와 소식에서 핵심을 읽는다). `<div class="tab on" id="new">` 은 그대로 둔다 — Now 의 `ai_picks.py` 와 `curate_prompt.md` 가 이 줄을 표식으로 쓴다. 용도별은 「새로 나온 것」 안의 「날짜순 / 용도별」 전환이다.
- 체크 칸은 화면에서 뺐다(`data-check="off"` 기본, 해봄 수와 켜고 끄는 단추 숨김). 상태 저장과 Now 연동 코드는 남아 있다 — 해봄은 Now 에서 한다. 시안 생성기는 `~/dev/analyses/ai-sungd-uk-design/make_home.py`(`SITE=<index.html>` 이면 사이트 파일을 고친다).
- 「모델」 탭 아래 차트(MD)는 손으로 갱신한다. 30일 안에 나온 세 회사 최신 모델이 차트에 없으면 `update_models.py` 가 차트 기준일에 `data-new` 를 달아 흐리게 한다. 값은 Artificial Analysis 막대 툴팁의 합계로 읽는다(데이터 내려받기는 유료).
- 모델 현황의 라인은 `update_models.py` 의 `LINES` 정규식으로 묶는다. 규칙에 안 걸리는 세 회사의 새 이름은 「새 이름」 줄로 뜨니, 보이면 `LINES` 에 넣는다.
- 「소식」 탭은 주인(`sd_owner` 쿠키)에게만 보인다. 주인 구독이 바뀌면 `scripts/news_prompt.md` 의 표와 `render_news.py` 의 「기준」 줄을 같이 고친다.
- 3단계가 `index.html` 을 직접 고친다. 뒤이은 JS 무결성 검사에 실패하면 자동으로 되돌린다.
- 「새로 나온 것」, 「용도별」은 큐레이션이 그린 HTML 을 마지막 `<script>` 끝의 `skin()` 이 화면에서 다시 배치한다(이번 주 써 볼 것, 날짜 맞춤 3단, 용도별 최신순). 기대는 class 는 `.tw.t-cc/cx/ag`, `.box0`, `.c-day`(안에 `YYYY-MM-DD`), `.it.t1~t3`, `.row .sev .box .cmd .tt .ds`, `.det` 의 「해보기」, `#use .cat .ci .cv .more` 다. 큐레이션이 이 구조를 바꾸면 `skin()` 이 실패하고 원래 화면으로 돌아간다. 시안 생성기는 `~/dev/analyses/ai-sungd-uk-design/make_new.py`.
