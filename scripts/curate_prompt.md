「오늘 뭐 써볼까」(`index.html`, ai.sungd.uk) 큐레이션 갱신. 토큰 절약 — 꼭 필요한 최소 편집만. 확신 없으면 아무것도 바꾸지 말 것.

너는 GitHub Actions 러너에서 헤드리스(`claude -p`)로 도는 중이다. **`index.html`을 워킹트리에서 직접 Edit 해라.** 커밋·푸시 금지(워크플로가 처리). 작업 끝나면 그냥 종료.

## 화면은 둘뿐이다

| 화면 | 축 | 어디 |
|---|---|---|
| 새로 나온 것 | 시간 — 언제 나왔나 | `<div class="tab on" id="new">` 안 `.t-cc` / `.t-cx` / `.t-ag` |
| 용도별 | 일 — 무슨 일 할 때 | `<div class="tab" id="use">` 안 `.t-cc` / `.t-cx` / `.t-ag` |

Manus·뉴스·블로그 화면은 **없앴다**. 그런 내용은 이제 아무 데도 넣지 마라.

`<div id="data">` 는 화면에 안 나오는 자료칸이다. 버전블록·명령어 문서표가 들어 있고 **여기는 절대 손대지 마라** — 버전블록은 스크립트(추가)와 전용 번역 스텝이 다룬다.

## 입력 (repo 루트, Read로 읽어라 — 없거나 `[]`면 그 단계 건너뜀)
- `new-features.json` — 새 Claude Code feature (version, date, text).
- `new-codex-features.json` — 새 Codex feature (version=v0.x, date, text).
- `new-agy-features.json` — 새 Antigravity CLI feature (version=1.x, date, text).
- `new_blog.json` — 새 blog/news 글. **화면에 올리지 않는다.** 철회·중단 감지(§4)에만 쓴다.

## 공통 원칙
- **기존 줄 하나를 그대로 복사해 값만 교체한다.** 마크업 구조·클래스·속성 순서를 절대 바꾸지 말 것.
- 한국어 간결한 톤(~함/~음). 영문 직역 금지 — 핵심만 의역. 과장·추측 금지, **검증된 사실만**.
- 편집할 게 없으면 그 영역은 그대로 둔다.
- `data-en` 은 더 이상 쓰지 않는다(영어 전환 기능을 뺐다). 새 줄에 넣지 마라.

## 체크 키 — 두 화면을 잇는 끈 ★
줄마다 `data-k` 가 있다. 이 키가 같아야 **새로 나온 것에서 체크한 게 용도별에도 뜬다.**

**이름이 아니라 출처로 잡는다** — `도구:버전#e항목번호` (`cc:2.1.224#e6`).
항목번호는 그 버전 `.version-block` 안에서 그 기능을 적은 `.e-desc` 가 **몇 번째인가**(0부터).

- 이름으로 잡으면 같은 기능을 두 화면이 다르게 적을 때 끊긴다 —
  `agent()` ↔ `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 처럼. 출처는 하나라 안 끊긴다.
- 같은 기능을 두 화면에 넣을 땐 **같은 항목번호를 쓴다.**
- 그 버전 블록에 대응 항목이 없으면(릴리스 노트에 안 적힌 것) 예전 꼴 `도구:명령어첫낱말@버전` 을 써도 된다.
  대신 두 화면에서 **똑같이** 적어야 한다.

## 1) 새로 나온 것 — Claude Code (new-features.json)
`<div class="tab on" id="new">` 안 `<div class="tw t-cc on">` 의 `.box0`.

- **날짜 줄이 먼저다.** 그 날짜의 `<div class="c-day">` 가 이미 있으면 그 아래에 줄을 넣고,
  없으면 위쪽 날짜 줄을 복사해 새로 만든다. **최신 날짜가 위**다. 꼴은 이렇다.

```
<div class="c-day"><span>── 2026-08-13 목 · <a class="vl" href="…">v2.1.230</a></span><i></i><em>지난주</em></div>
```

  `<i>` 는 점선이 늘어나는 자리다. **상대주(`<em>`)는 `<i>` 뒤 — 줄 맨 오른쪽**에 둔다.
  이번 주면 `<em>` 을 아예 뺀다. 날짜는 여기에만 있고 기능 줄에는 없다.
- 줄은 이 꼴이다. 기존 `.it` 하나를 복사해 값만 갈아라.

```
<div class="it t2 nw" data-t="제목" data-k="cc:/foo@2.1.230"><div class="row">
<span class="sev">추천</span>
<button class="box" data-off="[x]">[ ]</button>
<span class="cmd">/foo</span>
<span class="tt">제목</span><span class="ds">좋은 점</span></div>
<div class="det">…자세히…</div></div>
```

- `t3`=핵심 `t2`=추천 `t1`=일반, `.sev` 글자도 같이 맞춘다.
- ⚠ **`nw` 는 이번 실행에서 넣은 줄에만 붙인다.** 시작할 때 화면에 남아 있는 것을 **먼저 지운다** —
  `class="it t2 nw"` → `class="it t2"`. 그다음 이번에 넣은 줄에만 붙인다.
  **안 지우면 계속 쌓여 「새로 들어온 것」이 늘기만 한다.**
  `nw` 는 화면에 표시가 없고 머리말 집계에만 쓰인다 — `<b>새로 들어온 것 N개</b>` 의 N 과
  「그중 안 해본 것」이 이 클래스를 센다. N 도 이번에 넣은 수로 맞춘다.
- `data-t` 는 `.tt` 와 같은 글. **줄에 날짜 칸은 없다** — 날짜는 위 날짜 줄이 맡는다.
- **`.ds` 는 왜 쓸모 있나 한 줄**이다. 자세히에는 이 문장이 없으니 여기서 제 몫을 해야 한다 —
  제목을 딴 말로 되풀이하지 말고, 제목이 안 말한 이득을 적는다.
- ⚠ **명령어에 링크를 걸지 마라.** `<span class="cmd">/foo</span>` — 글자만 둔다.
  줄 아무 데나(명령어 자리 포함) 누르면 자세히가 뜨는 게 이 화면의 규칙이라,
  명령어에 링크가 있으면 그 자리만 딴 데로 튄다.
- **밖으로 나가는 길은 버전 링크 하나로 모은다.** 명령어마다 걸던 글자 조각
  (`#:~:text=…`)은 브라우저가 강조만 하고 그 줄로 안 내려가는 일이 잦아 2026-08-13 에 걷어냈다.
  - **새로 나온 것**: 날짜 줄의 `<a class="vl">`. 그 날짜에 버전이 둘이면 ` · ` 로 잇는다.
    `https://code.claude.com/docs/en/changelog#2-1-230` · Codex 는
    `https://github.com/openai/codex/releases/tag/rust-v0.148.0`.
    **날짜 줄을 새로 만들 때 버전 링크를 빠뜨리지 마라** — 그 아래 줄들이 통째로 원문에 닿을
    길을 잃는다(예전 날짜 줄 14개가 그랬다).
  - **용도별**: 줄 오른쪽 끝 `<a class="cv">`. **줄마다 하나씩 반드시** 있어야 한다.
- 명령어가 없는 항목은 `<span class="cmd dash">—</span>` 로 둔다. 링크 자리가 아니다.
- 다 고친 뒤 `python3 scripts/check_links.py` 로 한 번 훑을 수 있다.

### 자세히(`.det`) — 두 줄, 순서 고정
```
<p><span class="dk">해보기</span>…</p>
<p><span class="dk">알아둘 것</span>…</p>
```

**이 팝업은 읽을거리가 아니라 실행 카드다.** 무엇인지와 왜 좋은지는 목록 줄(`.tt`·`.ds`)이 이미
답했다. 줄을 눌렀다는 건 마음이 정해졌다는 뜻이고, 남은 질문은 하나뿐이다 —
**"그래서 지금 뭘 하면 되는데?"** 두 줄은 그 질문에만 답한다.

- **해보기 — 반드시 넣는다.** 세 조건을 모두 만족해야 한다.
  ① **동사로 끝난다**(…해본다/…돌려본다/…센다) ② **한 번에 끝난다**(한 세션·한 명령 분량)
  ③ **됐는지 스스로 판단된다** — 절차가 아니라 **합격 기준**으로 적는다.
  - 좋음: `codex --approve-for-me 로 다음 작업을 한 번 돌리고, 승인 클릭이 몇 번 줄었는지 센다.`
  - 좋음: `settings.json 의 plugins 배열에 소스를 넣고 새 세션을 연다. /plugin list 에 뜨면 된 것.`
  - 나쁨: `…로드됐는지 확인한다.` — 확인하라는 말은 무엇을 보면 되는지를 안 알려준다.
  - 나쁨: `요금, /fast 토글, Opus 5 vs Sonnet 5 선택 기준` — 이건 할 일이 아니라 목차다.
  - 무엇을 해볼지 정말 모르겠으면 **그 항목은 픽에서 빼라.** 해볼 수 없는 것은 「새로 나온 것」이 아니다.
- **알아둘 것 — 있을 때만.** 해보기 전에 몰랐으면 막혔을 것만 적는다. 없으면 그 `<p>` 를 통째로 뺀다.
  - 담는 것: 조건(플랜·OS·모델), 값이 드는 것(요금), 대안(`mode:"link"` 로도 된다), 함정(세션마다 다시 실행됨).
  - 안 담는 것: **제목·`.ds` 를 딴 말로 되풀이한 문장.** 목록에 이미 있는 말을 다시 쓰면 열어본 값이 없다.
  - 억지로 채우지 마라. 한 줄짜리 팝업은 흠이 아니다.
- 명령·플래그는 `<code>` 로 verbatim.

## 2) 새로 나온 것 — Codex (new-codex-features.json)
`<div class="tw t-cx">` 안. 마크업·규칙은 §1과 같고 이것만 다르다.

- 키는 `cx:…@0.148.0` (`v` 없이).
- 버전 링크는 `https://github.com/openai/codex/releases/tag/rust-v0.148.0`.
  `https://developers.openai.com/codex/` 같은 첫 페이지로 보내지 마라.
- **Codex 픽도 자세히를 채운다.** 예전엔 한 줄짜리였는데 이제 Claude Code 와 같은 대접이다.

## 2-1) 새로 나온 것 — Antigravity CLI (new-agy-features.json)
`<div class="tw t-ag">` 안. 마크업·규칙은 §1과 같고 이것만 다르다.

- 키는 `ag:1.2.8#e0` (`v` 없이).
- 버전 링크는 `https://github.com/google-antigravity/antigravity-cli/releases/tag/1.2.8` (태그에 `v` 없음).
- 릴리스가 거의 매일 나오고 대부분이 `Improved …` 다. **해볼 수 있는 새 명령·플래그·설정(`Added …`, 기본값을 바꾼 `Changed …`)만** 픽 후보다.
  내부 개선·성능·렌더링 손질은 넣지 마라 — 하루 한두 줄이면 충분하고, 없으면 안 넣는다.

## 3) 용도별 (세 도구 모두)
`<div class="tab" id="use">` 안, 여덟 칸 중 맞는 `<div class="cat" id="u-cc-N">`(Codex 는 `u-cx-N`, Antigravity 는 `u-ag-N`) 에 넣는다.
줄이 하나도 없던 칸이면 그 도구의 다른 칸을 복사해 칸과 `.catnav` 항목을 함께 만든다.

칸: 긴 작업 맡기기 / Subagent · 멀티 세션 / PR · 코드 리뷰 / 비용 · 토큰 / 일상 UI · 네비 / Plugin · MCP · 확장 / Hook · 모니터링 / 모델 · Enterprise

```
<div class="ci" data-k="cc:/foo@2.1.230"><button class="box" data-off="[x]">[ ]</button>
<span class="cmd">/foo</span>
<span class="cd">무엇을 하나</span>
<a class="cv" href="https://code.claude.com/docs/en/changelog#2-1-230" …>v2.1.230</a></div>
```

- 칸 머리(`.cathead`)의 개수 `<b>N</b>` 과 위쪽 칸 목록(`.catnav`)의 `<span class="n">N</span>` 을 **같이 올려라.** 안 맞으면 눈에 띈다.
- 일곱 번째부터는 접히므로 새 줄에 `over` 클래스를 붙인다 — `<div class="ci over" …>`. 칸의 앞 여섯 개만 `over` 가 없다.
- 한 칸에 너무 몰리지 않게(칸당 25개 안쪽).
- **§1·§2 에서 넣은 것과 같은 기능이면 `data-k` 를 똑같이 맞춰라.**

## 4) 철회·중단 감지 ★
새 입력이 **이전에 올린 기능·모델의 철회·중단·접근차단·deprecated·superseded·이름변경**을 알리면 반영한다.

- **신호**: 중단/철회/접근 차단/withdrawn/suspended/discontinued/deprecated/sunset/superseded/롤백/이름변경.
- **조치**: 해당 줄을 ① **삭제** 또는 ② 등급을 낮추고(`t3`→`t1`, `.sev` 도) 제목 끝에 상태 표기(예: "— 중단").
- 확신 없으면(정말 회수인지 모호하면) 그대로 둔다.

## 절대 금지
- `<div id="data">` 안(버전블록·문서표) 은 **일절 건드리지 마라.**
- 「모델」 탭의 `<!--MODELS-->` … `<!--/MODELS-->` 구간은 **건드리지 마라.** 사람이 손으로 갱신한다.
- 상단바·CSS·`<script>` 는 건드리지 마라.
- **명백한 플레이스홀더만 건너뛴다** ("Bug fixes and reliability improvements", "Internal infrastructure improvements" 등). 새 모델·플래그십 출시는 임의로 빼지 말 것 — 최우선 `t3` 후보다.
- 마크업 형식을 깨지 말 것. 확신 없으면 그 항목은 건너뛴다.
