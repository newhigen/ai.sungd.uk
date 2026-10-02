# -*- coding: utf-8 -*-
"""소식 그리기 — news_judged.json(claude -p 가 가른 것)을 news.json 에 쌓고 index.html 의 <!--NEWS--> 구간을 다시 그린다.
판단이 없으면 쌓지 않고 지금 news.json 으로 다시 그리기만 한다. 토큰 0.

화면은 한 주에 7줄 안팎 — 써 볼 것 4, 알아 둘 것 3, 화제 2 까지 펴고 나머지는 접는다. 지난 주는 한 줄씩."""
import json, os, re, sys, html, datetime

KST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(KST).date()
KEEP_DAYS = 42
SHOW = {'try': 4, 'know': 3, 'buzz': 2}
GROUP = [('try', '써 볼 것'), ('know', '알아 둘 것'), ('buzz', '화제')]
CO = {'Anthropic': 'an', 'OpenAI': 'oa', 'Google': 'go'}
e = html.escape

state = json.load(open('news.json', encoding='utf-8')) if os.path.exists('news.json') else {'items': []}
items = {i['key']: i for i in state['items']}

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
        key=j['key'], of=j.get('of'), title='' if sub else base['title'], group=j['group'], line=re.sub(r'\s*[—(-]\s*HN \d+\s*점?\)?$', '', j['line'].strip()), short=(j.get('short') or j['line'].split(' — ')[0]).strip(),
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
def monday(d): x = datetime.date.fromisoformat(d); return x - datetime.timedelta(days=x.weekday())
def span(m):
    end = m + datetime.timedelta(days=6)
    return f'{m.month}/{m.day} ~ {end.day}' if end.month == m.month else f'{m.month}/{m.day} ~ {end.month}/{end.day}'
def rank(i): return (-i['w'], -i['pts'], i['date'])
def dot(i): return f'<span class="cd {CO.get(i["co"], "")}"></span>'
def a(i, cls=''): return f'<a href="{e(i["url"])}" target="_blank" rel="noopener noreferrer"{cls}>{e(i["line"])}</a>'
def hn(i):  # 점수는 줄 끝에 작게 — 누르면 HN 댓글
    if not i.get('pts'): return ''
    t = f'HN {i["pts"]}'
    return f'<a class="hp" href="https://news.ycombinator.com/item?id={i["hn"]}" target="_blank" rel="noopener noreferrer">{t}</a>' if i.get('hn') else f'<span class="hp">{t}</span>'
def ln(i, strong):
    note = f'<span class="to">→ {e(i["note"])}</span>' if i['note'] else ''
    ev = f'<span class="evn">{e(i["event"])}</span>' if i.get('event') else ''
    return f'<p class="ln">{dot(i)}<span class="lc">{ev}{a(i, " class=b" if strong else "")}{hn(i)}{note}</span></p>'

weeks = {}
for i in state['items']:
    if i['group'] != 'skip': weeks.setdefault(monday(i['date']), []).append(i)
out = []
ws = sorted(weeks, reverse=True)
if ws:
    top = weeks[ws[0]]
    out.append(f'<p class="wk">{span(ws[0])} <em>Claude Max, ChatGPT Plus, Google AI Pro 기준</em></p>')
    for i in sorted((i for i in top if i['group'] == 'event'), key=rank):
        out.append(f'<p class="ln ev"><span class="evt">행사</span><span class="lc">{a(i, " class=b")}{hn(i)}</span></p>')
        if i.get('all'):
            out.append(f'<details class="evl"><summary>발표 {len(i["all"])}개 펼치기</summary>' + ''.join(
                f'<p><a href="{e(x.get("url") or i["url"])}" target="_blank" rel="noopener noreferrer">{e(x["name"])}</a> <span>{e(x.get("line", ""))}</span></p>'
                for x in i['all']) + '</details>')
    rest = []
    for g, name in GROUP:
        xs = sorted((i for i in top if i['group'] == g), key=rank)
        if not xs: continue
        out.append(f'<p class="gh">{name}</p>' + ''.join(ln(i, g == 'try') for i in xs[:SHOW[g]]))
        rest += xs[SHOW[g]:]
    skipped = [i for i in state['items'] if i['group'] == 'skip' and monday(i['date']) == ws[0]]
    if rest or skipped:
        out.append(f'<details class="more"><summary>나머지 {len(rest) + len(skipped)}개</summary>'
                   + ''.join(ln(i, False) for i in sorted(rest, key=rank))
                   + ''.join(f'<p class="ln dim">{dot(i)}<span class="lc">{a(i)}{hn(i)}</span></p>' for i in sorted(skipped, key=rank)) + '</details>')
    for m in ws[1:5]:
        xs = sorted((i for i in weeks[m] if i['group'] in ('event', 'try', 'know') and not i.get('of')), key=rank)[:3] \
             or sorted(weeks[m], key=rank)[:2]
        bz = sorted((i for i in weeks[m] if i['group'] == 'buzz'), key=lambda i: -i['pts'])[:1]
        out.append(f'<p class="pw"><span class="wk2">{span(m)}</span>'
                   + ', '.join(f'<a href="{e(i["url"])}" target="_blank" rel="noopener noreferrer">{e(i["short"])}</a>' for i in xs)
                   + ''.join(f'<span class="pb">화제</span><a href="{e(i["url"])}" target="_blank" rel="noopener noreferrer">{e(i["short"])}</a>{hn(i)}' for i in bz) + '</p>')
else:
    out.append('<p class="wk">아직 모은 소식이 없어요.</p>')

src = open('index.html', encoding='utf-8').read()
new = re.sub(r'(<!--NEWS-->).*?(<!--/NEWS-->)', lambda m: m.group(1) + '\n' + '\n'.join(out) + '\n' + m.group(2), src, count=1, flags=re.S)
if new == src and '<!--NEWS-->' not in src: sys.exit('index.html 에 <!--NEWS--> 구간이 없다')
open('index.html', 'w', encoding='utf-8').write(new)
print(f'소식 {added}개 쌓음 · 모두 {len(state["items"])}개 · 주 {len(ws)}개')
