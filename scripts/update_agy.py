# -*- coding: utf-8 -*-
"""ai-pick Antigravity CLI 탭 갱신.

google-antigravity/antigravity-cli GitHub Releases 에서 index.html 의 최신 추적(ag*)
버전보다 새로운 릴리스를 가져와 Antigravity 자료 구간에 version-block 을 prepend 한다.
- 릴리스 노트는 머리글 없는 불릿 목록이다. `Fixed …` 로 시작하면 Fix, 나머지는 기능
- <!--AG-DATA--> 구간 안에서만 편집 (다른 도구 오염 방지)
- 변경이 있으면 index.html 갱신 + GITHUB_OUTPUT 플래그, 없으면 멱등

stage-2(헤드리스 claude -p)가 Antigravity 픽 큐레이션을 이어서 처리한다.
"""
import re, json, sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from update_codex import fetch, ver_tuple, md_to_html, fmt_date

HTML_PATH = 'index.html'
RELEASES_URL = 'https://api.github.com/repos/google-antigravity/antigravity-cli/releases?per_page=100'


def out(**kv):
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a') as f:
            for k, v in kv.items():
                f.write(f'{k}={v}\n')


def parse_items(body):
    by = {'feature': [], 'fix': []}
    for ln in body.replace('\r\n', '\n').split('\n'):
        m = re.match(r'^\s*[-*]\s+(.*)$', ln)
        if not m or not m.group(1).strip():
            continue
        it = m.group(1).strip()
        by['fix' if re.match(r'(?i)fix', it) else 'feature'].append(it)
    return by


def gen_block(ver, by, date):
    feats, fixes = by['feature'], by['fix']
    if not feats and not fixes:
        return ''
    ko, en = fmt_date(date)
    pills = []
    if feats:
        pills.append(f'<span class="pill feature">기능 ×{len(feats)}</span>')
    if fixes:
        pills.append(f'<span class="pill fix">Fix ×{len(fixes)}</span>')
    o = [f'    <div class="version-block" id="ag{ver}" data-date="{date}">',
         f'      <div class="version-head">',
         f'        <span class="ver-badge">v{ver}</span><span class="ver-date" data-en="{en}">{ko}</span><span class="ver-ago"></span>',
         f'        <div class="ver-summary">{"".join(pills)}</div>',
         f'      </div>']
    for f in feats:
        o.append(f'      <div class="entry row-divider" data-type="feature"><span class="pill feature" data-en="Feature">기능</span><span class="e-desc">{md_to_html(f)}</span></div>')
    for f in fixes:
        o.append(f'      <div class="entry row-divider" data-type="fix"><span class="pill fix">Fix</span><span class="e-desc">{md_to_html(f)}</span></div>')
    o.append(f'    </div>')
    return '\n'.join(o)


def main():
    html = open(HTML_PATH, encoding='utf-8').read()
    s = html.index('<!--AG-DATA-->')
    e = html.index('<!--/AG-DATA-->')
    ag = html[s:e]

    existing = set(re.findall(r'id="ag(\d+\.\d+\.\d+)"', ag))
    latest = max(existing, key=ver_tuple) if existing else '0.0.0'

    try:
        releases = json.loads(fetch(RELEASES_URL))
    except Exception as ex:  # 네트워크/일시 API 오류 → CI 실패 대신 멱등 no-op
        print(f'antigravity releases fetch failed ({ex}); skipping this run', file=sys.stderr)
        out(ag_changed='false', ag_has_features='false')
        return
    new = []
    for r in releases:
        m = re.match(r'^v?(\d+\.\d+\.\d+)$', r.get('tag_name', ''))
        if not m or r.get('prerelease') or r.get('draft'):
            continue
        v = m.group(1)
        if v not in existing and ver_tuple(v) > ver_tuple(latest):
            new.append((v, r['published_at'][:10], r.get('body') or ''))
    if not new:
        print(f'No new antigravity versions. Latest tracked: ag{latest}')
        out(ag_changed='false', ag_has_features='false')
        return
    new.sort(key=lambda x: ver_tuple(x[0]), reverse=True)

    blocks, feat_queue = [], []
    for ver, date, body in new:
        by = parse_items(body)
        b = gen_block(ver, by, date)
        if b:
            blocks.append(b)
        for it in by['feature']:
            feat_queue.append({'version': ver, 'date': date, 'text': md_to_html(it)})
    if not blocks:
        print('New antigravity versions had no parseable items.')
        out(ag_changed='false', ag_has_features='false')
        return

    # 첫 ag version-block 앞(없으면 범위 줄 뒤)에 삽입
    m = re.search(r'^    <div class="version-block" id="ag', ag, flags=re.MULTILINE)
    idx = m.start() if m else ag.index('</p>', ag.index('class="range"')) + len('</p>\n')
    ag = ag[:idx] + '\n'.join(blocks) + '\n' + ag[idx:]

    # 범위 머리 갱신
    vers = re.findall(r'id="ag(\d+\.\d+\.\d+)" data-date="([\d-]+)"', ag)
    lo = min(vers, key=lambda x: ver_tuple(x[0]))
    hi = max(vers, key=lambda x: ver_tuple(x[0]))
    d0, d1 = (datetime.strptime(x[1], '%Y-%m-%d') for x in (lo, hi))
    rng = f'{d0.year}.{d0.month}.{d0.day} – {d1.year}.{d1.month}.{d1.day}'
    ag = re.sub(r'<p class="range">.*?</p>',
                f'<p class="range"><strong>v{lo[0]}</strong> → <strong>v{hi[0]}</strong> &nbsp;·&nbsp; '
                f'<span class="range-dates" data-en="{rng}">{rng}</span></p>', ag, count=1)

    html = html[:s] + ag + html[e:]
    open(HTML_PATH, 'w', encoding='utf-8').write(html)

    json.dump(feat_queue, open('new-agy-features.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    added = ', '.join(f'v{v}' for v, _, _ in new)
    print(f'Added {len(new)} antigravity version(s): {added}')
    print(f'New antigravity features needing judgment: {len(feat_queue)}')
    out(ag_changed='true', ag_has_features='true' if feat_queue else 'false', ag_added_versions=added)


if __name__ == '__main__':
    main()
