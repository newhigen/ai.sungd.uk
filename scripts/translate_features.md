index.html(「오늘 뭐 써볼까」, ai.sungd.uk)의 **패치노트 기능(feature) 항목만** 한국어로 번역한다. 그 외엔 절대 아무것도 바꾸지 마라. 토큰 절약 — 미번역 항목만 최소 편집.

너는 GitHub Actions 러너에서 헤드리스(`claude -p`)로 도는 중이다. **`index.html`을 워킹트리에서 직접 Edit 해라.** 커밋·푸시 금지(워크플로가 처리). 끝나면 종료.

## 할 일 (이것만)
`.entry[data-type="feature"]` 안의 `<span class="e-desc">` 중 **`data-en` 속성이 없는 것**(=미번역)을 한국어로 의역한다.
- 대상: Claude Code(`id="v2.1.*"`)·Codex(`id="cx0.*"`)·Antigravity(`id="ag1.*"`) 버전블록(셋 다 `<div id="data">` 안에 있다) 중 **위에서부터 최신 ~20개**. 그 안의 미번역 feature `e-desc` 전부 (반쪽 금지 — 한 블록 시작했으면 그 블록 feature 전부).
- 방식: e-desc 텍스트를 간결한 한국어로 의역(핵심만). `<code>`·명령어·플래그·이슈번호는 그대로 verbatim. 영어 원문은 `data-en`에 보존(안의 큰따옴표는 `&quot;`).
  - 예: `<span class="e-desc">Added <code>--foo</code> flag for X</span>` → `<span class="e-desc" data-en="Added <code>--foo</code> flag for X">X용 <code>--foo</code> 플래그 추가</span>`
- 이미 `data-en` 있는 e-desc는 건너뛴다.

## 절대 금지
- improve·security·fix 항목(탭 안 `.coll-item`, data-type≠feature)·화면 두 개(`#new`·`#use` 안의 `.it`·`.ci`)·상단바·디자인/CSS/JS·마크업 구조는 **일절 건드리지 마라**. 오직 feature `.e-desc`의 텍스트(+data-en 추가)만.
- 클래스·속성 순서·인라인 태그(`<code>` 등) 불변. 확신 없으면 그 항목 건너뛴다.
