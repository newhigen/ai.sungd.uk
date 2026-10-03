# -*- coding: utf-8 -*-
"""모델 현황 — 「모델」 탭 맨 위 <!--MODELS-STATUS--> 구간을 다시 그린다. 토큰 0.

1. Artificial Analysis 의 Terminal-Bench 4.0 페이지 HTML 에서 모델 출시일(releaseDate)과
   처음 보이는 30개 모델의 점수를 읽어 models.json 에 쌓는다. 못 받으면 지금 models.json 으로 그린다.
2. 회사 → 라인(Opus, Sol, Flash…)으로 묶어 지난 6개월 출시를 타임라인에 찍고, 지금 최신, 나온 날,
   TB 4.0 점수, 내 도구(CC/CX/AG 릴리스 노트에 이름이 나왔나)를 붙인다.
3. 30일 안에 나온 세 회사 최신 모델이 아래 차트(MD)에 없으면 차트 기준일에 data-new 를 달아 「갱신할 때」를 알린다.

라인 규칙(LINES)에 안 걸리는 세 회사의 새 이름은 「새 이름」 줄로 받는다 — 보이면 LINES 에 넣을 것.
"""
import datetime as dt, html, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX, STORE = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'models.json')
URL = 'https://artificialanalysis.ai/evaluations/terminalbench-4-0'
KST = dt.timezone(dt.timedelta(hours=9))
TODAY = dt.datetime.now(KST).date()
FROM, TO = TODAY - dt.timedelta(days=185), TODAY + dt.timedelta(days=7)
RECENT, NEWNAME = 14, 30

# (회사, 색, 노트 구간, 도구 이름, 이름 머리, [(라인, 정규식 — 처음 잡힌 묶음이 점 위 짧은 표기)])
LINES = [
  ('Anthropic', '#d97757', 'CC', 'Claude Code', 'Claude ', [
    ('Fable', r'^Claude (?:Fable ([\d.]+)|(Mythos [\d.]+))$'),
    ('Opus', r'^Claude Opus ([\d.]+)$'),
    ('Sonnet', r'^Claude Sonnet ([\d.]+)$'),
    ('Haiku', r'^Claude Haiku ([\d.]+)$'),
  ]),
  ('OpenAI', '#1c1e23', 'CX', 'Codex', 'GPT-', [
    ('Astra', r'^GPT-([\d.]+)(?: Astra)?$'),
    ('Sol', r'^GPT-([\d.]+) Sol$'),
    ('Luna', r'^GPT-(?:([\d.]+) Luna|([\d.]+ mini))$'),
  ]),
  ('Google', '#3b6fd6', 'AG', 'Antigravity', 'Gemini ', [
    ('Pro', r'^Gemini ([\d.]+ (?:Pro|Argon|Ultra))(?: Preview)?$'),
    ('Flash', r'^Gemini ([\d.]+) Flash$'),
  ]),
  ('그 밖', '#8a8d93', None, None, None, [
    ('xAI Grok', r'^Grok ([\d.]+)$'),
    ('Z.ai GLM', r'^GLM-([\d.]+)$'),
    ('Qwen', r'^Qwen([\d.]+) (?:Max|Plus)$'),
    ('DeepSeek', r'^DeepSeek (V[\d.]+)(?: Pro| Flash)?(?: \d{4})?$'),
    ('Kimi', r'^Kimi (K[\d.]+)(?: Code)?$'),
  ]),
]
OPEN = {'Z.ai GLM', 'Qwen', 'DeepSeek', 'Kimi'}


def fetch():
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (ai.sungd.uk model status)'})
    s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8')
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', s, re.S)
    big = ''.join(json.loads('"' + c + '"') for c in chunks)
    # 모델 객체 하나 안에서 name 뒤에 releaseDate 가 온다(사이에 shortName 등). 괄호 붙은 effort 변형은 뺀다
    rel = {}
    for m in re.finditer(r'"name":"([^"(]+?)"[^{}]{0,300}?"releaseDate":"(\d{4}-\d\d-\d\d)"', big):
        rel.setdefault(m.group(1).strip(), m.group(2))
    tb = {}
    i = big.find('"initialModels":')
    if i >= 0:
        arr, _ = json.JSONDecoder().raw_decode(big[i + len('"initialModels":'):])
        for m in arr:
            v = m.get('terminalBench40')
            if isinstance(v, (int, float)):
                base = re.sub(r'\s*\(.*\)$', '', m['name']).strip()
                tb[base] = max(tb.get(base, 0), round(v * 100, 1))
    return rel, tb


store = json.load(open(STORE, encoding='utf-8')) if os.path.exists(STORE) else {'release': {}, 'tb4': {}}
try:
    rel, tb = fetch()
    if len(rel) < 50: raise ValueError(f'출시일이 {len(rel)}개뿐 — 페이지 구조가 바뀐 듯')
    store['release'].update(rel)
    for k, v in tb.items(): store['tb4'][k] = v
except Exception as e:
    print(f'::warning::Artificial Analysis 를 못 읽어 지금 models.json 으로 그린다 — {e}')
REL, TB = store['release'], store['tb4']

s = open(INDEX, encoding='utf-8').read()
NOTES = {t: s[s.index(f'<!--{t}-DATA-->'):s.index(f'<!--/{t}-DATA-->')] for t in ['CC', 'CX', 'AG']}


def in_notes(tool, name, head):
    """노트에 모델 이름이 나왔나. 「GPT-6 Sol and Luna」, 「GPT-6-Astra」, 「Opus 5.5」 모양을 다 받는다"""
    bare = name[len(head):] if head and name.startswith(head) else name
    m = re.match(r'([\d.]+)\s*(.*)$', bare)
    if head == 'Claude ':
        pat = r'\b' + re.escape(bare) + r'(?![\d]|\.\d)'
    elif m:
        ver, fam = m.group(1), m.group(2).replace(' Preview', '')
        pat = re.escape(head.strip().rstrip('-')) + r'[- ]?' + re.escape(ver) + r'(?!\d|\.\d)' + (r'[^.<]{0,24}?\b' + re.escape(fam) + r'\b' if fam else '')
    else:
        return False
    return re.search(pat, NOTES[tool]) is not None


D = dt.date.fromisoformat
WD = '월화수목금토일'
def when(d):
    n = (TODAY - d).days
    if n == 0: return '오늘'
    if n == 1: return f'어제 ({WD[d.weekday()]})'
    if 0 < n <= 7: return f'{n}일 전 ({WD[d.weekday()]})'
    return f'{d.month}/{d.day} ({WD[d.weekday()]})'
pct = lambda d: round((d - FROM).days / (TO - FROM).days * 100, 2)
E = html.escape

rows, recent, missing, latest = [], [], [], []
for co, col, tk, tool, head, lines in LINES:
    body, taken = [], set()
    groups = []
    for ln, pat in lines:
        rx = re.compile(pat)
        pts = {}
        for name, d in REL.items():
            m = rx.match(name)
            if not m: continue
            taken.add(name)
            sh = next(g for g in m.groups() if g)
            if sh not in pts or d < pts[sh][0]: pts[sh] = (d, name)   # 같은 표기(Qwen3.7 Max·Plus, V4 Pro·Flash)는 처음 나온 하나만
        pts = sorted((D(d), sh, nm) for sh, (d, nm) in pts.items())
        if pts and pts[-1][0] >= FROM: groups.append((ln, pts))
    if head:   # 라인 규칙에 안 걸린 새 이름
        new = sorted((D(d), n[len(head):], n) for n, d in REL.items()
                     if n.startswith(head) and n not in taken and (TODAY - D(d)).days <= NEWNAME and '(' not in n)
        if new: groups.append(('새 이름', new))
    if not groups: continue
    rows.append(f'<div class="mh-co"><span class="mh-cn"><i style="background:{col}"></i>{E(co)}</span><span class="mh-tr"></span><span></span></div>')
    for ln, pts in groups:
        cur = pts[-1]
        dots = []
        for d, sh, nm in pts:
            if d < FROM: continue
            new = (TODAY - d).days <= RECENT
            cls = 'mh-dot' + (' new' if new else '') + (' cur' if (d, sh, nm) == cur else '')
            dots.append(f'<span class="{cls}" style="left:{pct(d)}%;--c:{col}" title="{E(nm)} · {d.month}/{d.day}"><i></i><em>{E(sh)}</em></span>')
            if new: recent.append((co, nm))
        d, sh, nm = cur
        if tk: latest.append((nm, d))
        sc = TB.get(nm)
        if tk:
            if in_notes(tk, nm, head): chip = f'<span class="mh-tool ok">{E(tool)} <b>✓</b></span>'
            else: chip = f'<span class="mh-tool no">{E(tool)} 아직</span>'; missing.append((nm, tool))
        elif ln in OPEN: chip = '<span class="mh-tool ow">오픈 웨이트</span>'
        else: chip = ''
        isnew = ' new' if (TODAY - d).days <= RECENT else ''
        now = (f'<span class="mh-nm{isnew}" style="--c:{col}">{E(nm.replace("Claude ", ""))}</span>'
               f'<span class="mh-d">{when(d)}</span><span class="mh-sc">{f"{sc:.1f}" if sc else "—"}</span>{chip}')
        rows.append(f'<div class="mh-ln"><span class="mh-lb">{E(ln)}</span><span class="mh-tr">{"".join(dots)}</span><span class="mh-now">{now}</span></div>')

# 결론 한 줄 — 지난 2주에 주력 모델을 바꾼 회사, 아직 내 도구에 없는 최신 모델
big3 = [c for c, *_ in LINES[:3]]
cos = [c for c in big3 if any(r[0] == c for r in recent)]
if len(cos) == 3: lead = '지난 2주에 세 회사가 모두 새 모델을 냈어요.'
elif cos: lead = f'지난 2주에 {", ".join(cos)} 가 새 모델을 냈어요.'
else: lead = '지난 2주에 세 회사의 새 모델은 없어요.'
fresh_missing = [(n, t) for n, t in missing if any(n == r[1] for r in recent)]
if len(fresh_missing) == 1:
    n, t = fresh_missing[0]; lead += f' {n.replace("Claude ", "")} 은 아직 {t} 에 없어요.'
elif fresh_missing:
    lead += ' ' + ', '.join(f'{n.replace("Claude ", "")}({t})' for n, t in fresh_missing) + ' 은 아직 내 도구에 없어요.'

months = []
m = dt.date(FROM.year, FROM.month, 1)
while m <= TO:
    if m >= FROM and abs(pct(m) - pct(TODAY)) > 5: months.append(f'<span style="left:{pct(m)}%">{m.month}월</span>')
    m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
bl, br = pct(TODAY - dt.timedelta(days=RECENT)), pct(TODAY)

BLOCK = f'''<!--MODELS-STATUS--><!-- scripts/update_models.py 가 매시 다시 그린다. 손으로 고치지 말 것 -->
<div class="mh">
<p class="lead"><b>모델 현황</b> <span class="masof">{TODAY.isoformat()} 기준</span></p>
<p class="mh-sum">{E(lead)}</p>
<div class="mh-g" style="--bl:{bl / 100:.4f};--bw:{(br - bl) / 100:.4f}">
<div class="mh-hd"><span></span><span class="mh-tr mh-mo">{"".join(months)}<span class="mh-tdl" style="left:{br}%">오늘</span></span><span class="mh-nh"><span>지금 최신</span><span>나온 날</span><span>TB 4.0</span><span>내 도구</span></span></div>
{"".join(rows)}
</div>
<p class="mfoot">점 하나가 출시 하나예요. 파란 띠는 지난 2주, 채운 점이 그 안에 나온 모델이에요. TB 4.0 은 아래 차트와 같은 Terminal-Bench 4.0 최고 effort 점수예요.<br>
출시일 <a href="{URL}" target="_blank" rel="noopener noreferrer">Artificial Analysis ↗</a> · 내 도구는 Claude Code, Codex, Antigravity 릴리스 노트에 모델 이름이 나왔는지로 봐요.</p>
</div>
<!--/MODELS-STATUS-->'''

a, b = s.index('<!--MODELS-STATUS-->'), s.index('<!--/MODELS-STATUS-->') + len('<!--/MODELS-STATUS-->')
out = s[:a] + BLOCK + s[b:]

# 30일 안에 나온 세 회사 최신 모델이 차트(MD)에 없으면 → 기준일에 data-new
absent = [n.replace('Claude ', '') for n, d in latest if (TODAY - d).days <= 30 and f'["{n.replace("Claude ", "")}",' not in out]
out = re.sub(r'(<span class="masof" data-asof="[\d-]+")(?: data-new="[^"]*")?', lambda m: m.group(1) + (f' data-new="{E(", ".join(absent))}"' if absent else ''), out, count=1)

changed = out != s
if changed: open(INDEX, 'w', encoding='utf-8').write(out)
json.dump(store, open(STORE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print(f'모델 현황: 줄 {sum(1 for r in rows if "mh-ln" in r)}개, 바뀜 {changed} · {lead}' + (f' · 차트에 없음: {absent}' if absent else ''))
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f: f.write(f'models_changed={"true" if changed else "false"}\n')
