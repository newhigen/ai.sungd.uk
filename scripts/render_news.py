# -*- coding: utf-8 -*-
"""소식 그리기 — news_judged.json(claude -p 가 가른 것)을 news.json 에 쌓고 index.html 의 <!--NEWS--> 구간을 다시 그린다.
판단이 없으면 쌓지 않고 지금 news.json 으로 다시 그리기만 한다. 토큰 0.

화면은 시안 A — 이번 주를 HN 점수 순 한 줄 목록으로(날짜, 점수 막대, 회사, 갈래, 한 줄, → 메모).
행사 정리 글은 안의 발표를 갈래별로 처음부터 펼친다. 버림은 그리지 않는다. 지난 주는 한 줄씩."""
import json, os, re, sys, html, math, datetime

KST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(KST).date()
KEEP_DAYS = 42
GR = {'event': '행사', 'try': '써 볼 것', 'know': '알아 둘 것', 'buzz': '화제'}
ORDER = {'event': 0, 'try': 1, 'know': 2, 'buzz': 3}
CO = {'Anthropic': ('an', 'Anthropic'), 'OpenAI': ('oa', 'OpenAI'), 'Google': ('go', 'Google')}
e = html.escape

state = json.load(open('news.json', encoding='utf-8')) if os.path.exists('news.json') else {'items': []}
def tidy(t):  # 줄 끝의 HN 점수와 앞의 도메인은 뗀다 — 화면이 점수를 따로 붙인다
    return re.sub(r'^[a-z0-9-]+(\.[a-z0-9-]+)+ — ', '', re.sub(r'\s*[—(-]\s*HN \d+\s*점?\)?$', '', t.strip()))

items = {i['key']: dict(i, line=tidy(i['line'])) for i in state['items']}

# ── 쌓기 ──
try:
    cands = {c['key']: c for c in json.load(open('news_new.json', encoding='utf-8'))}
    judged = json.load(open('news_judged.json', encoding='utf-8'))
except (OSError, ValueError):
    cands, judged = {}, []
added = 0
for j in judged if isinstance(judged, list) else []:
    base = cands.get(j.get('of') or j.get('key'))
    if not base or j.get('group') not in ('try', 'know', 'buzz', 'event', 'skip') or not j.get('line'): continue
    sub = bool(j.get('of'))
    items[j['key']] = dict(
        key=j['key'], of=j.get('of'), title='' if sub else base['title'], group=j['group'], line=tidy(j['line']), short=(j.get('short') or j['line'].split(' — ')[0]).strip(),
        note=(j.get('note') or '').strip(), w=int(j.get('w') or 1), event=j.get('event') or '',
        url=(j.get('url') or base['url']) if sub else base['url'], co=base['co'], date=base['date'],
        pts=0 if sub else base['pts'], hn=None if sub else base.get('hn'), gn=(base.get('gn') or {}).get('tid') if not sub else None,
        all=[x for x in (j.get('all') or []) if isinstance(x, dict) and x.get('name')] if j['group'] == 'event' else [])
    added += 1
cut = (TODAY - datetime.timedelta(days=KEEP_DAYS)).isoformat()
state['items'] = sorted((i for i in items.values() if i['date'] >= cut), key=lambda i: (i['date'], i['key']), reverse=True)
if added: state['judged_at'] = int(datetime.datetime.now(KST).timestamp())
json.dump(state, open('news.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ── 그리기 ──
WD = '월화수목금토일'
def monday(d): x = datetime.date.fromisoformat(d); return x - datetime.timedelta(days=x.weekday())
def span(m):
    end = m + datetime.timedelta(days=6)
    return f'{m.month}/{m.day} ~ {end.day}' if end.month == m.month else f'{m.month}/{m.day} ~ {end.month}/{end.day}'
def md(d): x = datetime.date.fromisoformat(d); return f'{x.month}/{x.day:02d} {WD[x.weekday()]}'
def rank(i): return (i['group'] != 'event', -i['pts'], ORDER[i['group']], -i['w'])
def nk(t): return re.sub(r'[^0-9a-z가-힣]', '', t.lower())
def link(u, t, cls=''): return f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer"{cls}>{t}</a>'
def hn(i):
    if not i.get('pts'): return ''
    t = f'HN {i["pts"]}'
    return link(f'https://news.ycombinator.com/item?id={i["hn"]}', t, ' class="hp"') if i.get('hn') else f'<span class="hp">{t}</span>'
def bar(i):  # HN 점수 막대 — 100점에서 2300점까지 로그 눈금, 500점부터 진하게
    p = i['pts']
    if not p: return '<span class="np nop">—</span>'
    w = round(min(1, math.log(max(p, 100) / 100, 2) / math.log(23, 2)) * 44) or 2
    b = f'<span class="np{" big" if p >= 500 else ""}"><i style="width:{w}px"></i><b>{p}</b></span>'
    return link(f'https://news.ycombinator.com/item?id={i["hn"]}', b, ' class="pl"') if i.get('hn') else b
def row(i):
    c, cn = CO.get(i['co'], ('et', '—'))
    note = f'<span class="to">→ {e(i["note"])}</span>' if i['note'] else ''
    return (f'<div class="ar g-{i["group"]}"><span class="dt">{md(i["date"])}</span>{bar(i)}'
            f'<span class="co {c}">{cn}</span><span class="gp">{GR[i["group"]]}</span>'
            f'<span class="tt">{link(i["url"], e(i["line"]))}{note}</span></div>')
def find(d, k):  # 이름으로 짝 찾기 — 「GPT-6.1 Sol」과 「GPT 6.1 Sol」, 「dots」와 「dots — 늘 켜 두는 에이전트」
    if not k: return None
    if k in d: return d[k]
    return next((v for kk, v in d.items() if len(min(k, kk, key=len)) >= 3 and (kk.startswith(k) or k.startswith(kk))), None)
def bundle(ev, pool):
    subs = {nk(s['short']): s for s in pool if s.get('of') == ev['key']}
    tops = {nk(s['short']): s for s in pool if not s.get('of') and s['group'] != 'skip' and s['pts']}
    cats = {}
    for x in ev['all']: cats.setdefault(x.get('cat') or '발표', []).append(x)
    def item(x):
        k = nk(x['name']); u = x.get('url') or ''
        s = find(subs, k) or (next((v for v in subs.values() if u and u != ev['url'] and v['url'] == u), None))  # 이름이 달라도 링크가 같으면 짝
        t = find(tops, k)
        pick = f'<em class="pk g-{s["group"]}">{GR[s["group"]]}</em>' if s and s['group'] in ('try', 'know') else ''
        note = f'<span class="to">→ {e(s["note"])}</span>' if s and s['note'] else ''
        return f'<p>{link(x.get("url") or ev["url"], e(x["name"]))} <span>{e(x.get("line", ""))}</span>{pick}{hn(t) if t else ""}{note}</p>'
    return ('<div class="bgs">' + ''.join(f'<div class="bg"><p class="bgh">{e(c)}</p>' + ''.join(item(x) for x in xs) + '</div>' for c, xs in cats.items())
            + f'<p class="bgf">{link(ev["url"], "원문 ↗")} · 따로 HN 에 뜬 것만 점수를 붙였어요</p></div>')

pool = [i for i in state['items'] if i['group'] != 'skip']
weeks = {}
for i in pool: weeks.setdefault(monday(i['date']), []).append(i)
out = []
ws = sorted(weeks, reverse=True)
if ws:
    top = [i for i in weeks[ws[0]] if not i.get('of')]
    big = sum(1 for i in top if i['pts'] >= 500)
    out.append(f'<div class="c-day"><span>── {span(ws[0])}</span><em>500점 넘은 것 {big}개 · 모두 {len(top)}개</em><i></i></div>')
    for i in sorted(top, key=rank):
        out.append(row(i))
        if i['group'] == 'event' and i.get('all'): out.append(bundle(i, pool))
    for m in ws[1:5]:
        xs = sorted((i for i in weeks[m] if i['group'] in ('event', 'try', 'know') and not i.get('of')), key=lambda i: (-i['w'], -i['pts']))[:3]
        bz = sorted((i for i in weeks[m] if i['group'] == 'buzz'), key=lambda i: -i['pts'])[:1]
        out.append(f'<p class="pw"><span class="wk2">{span(m)}</span>' + ', '.join(link(i['url'], e(i['short'])) for i in xs)
                   + ''.join(f'<span class="pb">화제</span>{link(i["url"], e(i["short"]))}{hn(i)}' for i in bz) + '</p>')
else:
    out.append('<p class="pw">아직 모은 소식이 없어요.</p>')

src = open('index.html', encoding='utf-8').read()
new = re.sub(r'(<!--NEWS-->).*?(<!--/NEWS-->)', lambda m: m.group(1) + '\n' + '\n'.join(out) + '\n' + m.group(2), src, count=1, flags=re.S)
if new == src and '<!--NEWS-->' not in src: sys.exit('index.html 에 <!--NEWS--> 구간이 없다')
open('index.html', 'w', encoding='utf-8').write(new)
print(f'소식 {added}개 쌓음 · 모두 {len(state["items"])}개 · 주 {len(ws)}개')
