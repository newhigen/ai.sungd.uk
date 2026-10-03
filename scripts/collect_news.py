# -*- coding: utf-8 -*-
"""소식 후보 수집 — 지난 8일 동안 문턱을 넘은 글 중 아직 판단 안 한 것만 news_new.json 으로.
토큰 0. 판단은 news_prompt.md(claude -p), 그리기는 render_news.py 가 한다.

문턱
  - Hacker News 300점 이상 (세 회사 이름이 제목이나 주소에 든 글)
  - 공식 도메인 글은 HN 100점 이상, 또는 공식 피드의 제품 글
  - 세 회사 밖 AI 글(Jev, DeepSeek, Mistral, Meta …)은 HN 500점 이상
  - 긱뉴스에만 있는 AI 글은 20점 이상
  - ElevenLabs 는 HN 점수가 안 나와 공식 블로그 글을 다 받는다(주인이 직접 고른 관심 회사).
    글 안 링크를 붙여 두면 판단이 그중 샘플 페이지를 demo 로 고른다
묶음 글(행사 정리 등)은 본문을 r.jina.ai 로 받아 둔다 — openai.com 은 봇을 막는다."""
import re, json, os, time, subprocess, datetime, urllib.parse, html
from email.utils import parsedate_to_datetime

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36'
KST = datetime.timezone(datetime.timedelta(hours=9))
NOW = int(time.time())
T0 = NOW - int(os.environ.get('NEWS_DAYS', 8)) * 86400  # 처음 채울 때만 넓힌다

def fetch(u, t=20):
    try: return subprocess.run(['curl', '-sL', '--max-time', str(t), '-A', UA, u], capture_output=True, text=True, timeout=t + 5).stdout
    except Exception: return ''

def norm(u):
    u = re.sub(r'^https?://(www\.)?', '', u.strip()).rstrip('/')
    return u if 'ycombinator.com' in u else u.split('?')[0].split('#')[0]

def kst(ts): return datetime.datetime.fromtimestamp(ts, KST).strftime('%Y-%m-%d')
def dom(u): return re.sub(r'^www\.', '', u.split('/')[2]) if '://' in u else ''

AI = re.compile(r'openai|anthropic|claude|chatgpt|gemini|codex|deepmind|\bgpt|sora|antigravity|mythos|fable|\bopus\b|\bsonnet\b', re.I)
OFFICIAL = {'openai.com': 'OpenAI', 'developers.openai.com': 'OpenAI', 'help.openai.com': 'OpenAI', 'alignment.openai.com': 'OpenAI',
            'chatgpt.com': 'OpenAI', 'learn.chatgpt.com': 'OpenAI',
            'anthropic.com': 'Anthropic', 'claude.com': 'Anthropic', 'code.claude.com': 'Anthropic', 'support.claude.com': 'Anthropic',
            'platform.claude.com': 'Anthropic', 'claude.dev': 'Anthropic',
            'blog.google': 'Google', 'deepmind.google': 'Google', 'developers.googleblog.com': 'Google', 'gemini.google': 'Google'}
BUNDLE = re.compile(r'recap|everything we announced|announcements|devday|google i/o|code with claude|news we announced|총정리', re.I)

def company(title, url):
    d = dom(url)
    if d in OFFICIAL: return OFFICIAL[d]
    t = (title + ' ' + url).lower()
    for k, v in (('anthropic', 'Anthropic'), ('claude', 'Anthropic'), ('openai', 'OpenAI'), ('chatgpt', 'OpenAI'),
                 ('codex', 'OpenAI'), ('gpt', 'OpenAI'), ('gemini', 'Google'), ('deepmind', 'Google'), ('google', 'Google')):
        if k in t: return v
    return '기타'

state = json.load(open('news.json', encoding='utf-8')) if os.path.exists('news.json') else {'items': []}
judged = {i['key'] for i in state['items']}
cand = {}

titles = {re.sub(r'\W+', ' ', i.get('title', '')).strip().lower() for i in state['items']}

def add(key, **kw):
    if key in judged: return
    tk = re.sub(r'\W+', ' ', kw.get('title', '')).strip().lower()
    if key not in cand and tk in titles: return  # 같은 글이 다른 주소로(blog.google 과 deepmind.google)
    if key in cand:  # 같은 글이 HN 과 공식 피드에 다 있으면 하나로 — HN 점수와 댓글을 붙인다
        c = cand[key]
        if kw.get('pts', 0) > c['pts']: c.update(pts=kw['pts'], cmt=kw.get('cmt', 0), hn=kw.get('hn'))
        return
    titles.add(tk)
    cand[key] = dict(dict(hn=None, pts=0, cmt=0, src='', desc='', gn=None), key=key, **kw)

# ── Hacker News ──
for q in ['openai', 'anthropic', 'claude', 'chatgpt', 'gemini', 'codex', 'deepmind', 'gpt', 'opus', 'sonnet']:
    u = 'https://hn.algolia.com/api/v1/search?' + urllib.parse.urlencode({
        'query': q, 'tags': 'story', 'hitsPerPage': 200, 'restrictSearchableAttributes': 'title,url',
        'numericFilters': f'created_at_i>{T0},points>=100'})
    try: hits = json.loads(fetch(u))['hits']
    except Exception: hits = []
    for h in hits:
        url = h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}"
        if not AI.search(h['title'] + ' ' + url): continue
        off = dom(url) in OFFICIAL
        if h['points'] < (100 if off else 300): continue
        add(norm(url), url=url, title=h['title'], co=company(h['title'], url), official=off, pts=h['points'],
            cmt=h.get('num_comments') or 0, hn=h['objectID'], date=kst(h['created_at_i']), src='hn')

# ── 세 회사 밖 AI 글: HN 500점 이상만 ──
OTHER = re.compile(r'\bAI\b|\bLLMs?\b|\bagents?\b|\bagentic\b|deepseek|qwen|mistral|llama|kimi|grok|\bxai\b|nvidia|cursor|copilot|'
                   r'vibe.cod|prompt|transformer|inference|hugging ?face|perplexity|\bMCP\b|\bmodels?\b|neural|reasoning', re.I)
for q in ['AI', 'LLM', 'agent', 'model', 'DeepSeek', 'Qwen', 'Mistral', 'Llama', 'Grok', 'Kimi', 'Cursor', 'Copilot',
          'Nvidia', 'MCP', 'Hugging Face', 'Perplexity', 'vibe coding', 'inference']:
    u = 'https://hn.algolia.com/api/v1/search?' + urllib.parse.urlencode({
        'query': q, 'tags': 'story', 'hitsPerPage': 200, 'restrictSearchableAttributes': 'title,url',
        'numericFilters': f'created_at_i>{T0},points>=500'})
    try: hits = json.loads(fetch(u))['hits']
    except Exception: hits = []
    for h in hits:
        url = h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}"
        if AI.search(h['title'] + ' ' + url) or not OTHER.search(h['title'] + ' ' + url): continue
        add(norm(url), url=url, title=h['title'], co='기타', official=False, pts=h['points'],
            cmt=h.get('num_comments') or 0, hn=h['objectID'], date=kst(h['created_at_i']), src='hn')

# ── 공식 피드 ──
x = fetch('https://openai.com/news/rss.xml')
for it in re.findall(r'<item>(.*?)</item>', x, re.S):
    g = lambda p: (re.search(p, it, re.S) or [None, ''])[1]
    try: ts = int(parsedate_to_datetime(g(r'<pubDate>(.*?)</pubDate>')).timestamp())
    except Exception: continue
    if ts < T0: continue
    title, cat, desc = g(r'<title><!\[CDATA\[(.*?)\]\]>'), g(r'<category><!\[CDATA\[(.*?)\]\]>'), g(r'<description><!\[CDATA\[(.*?)\]\]>')
    if cat not in ('Product', 'API', 'Engineering') and not BUNDLE.search(title + ' ' + desc): continue
    url = g(r'<link>(.*?)</link>')
    add(norm(url), url=url, title=title, co='OpenAI', official=True, date=kst(ts), src='rss', desc=desc[:300])

GOOG = re.compile(r'^(Introducing|Announcing|Gemini \d|Let |The Gemini app|A new wave|Advancing)|now available|rolling out|we announced', re.I)
for f in ['https://deepmind.google/blog/rss.xml', 'https://blog.google/products/gemini/rss/']:
    for it in re.findall(r'<item>(.*?)</item>', fetch(f), re.S):
        t = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', it, re.S); l = re.search(r'<link>(.*?)</link>', it); d = re.search(r'<pubDate>(.*?)</pubDate>', it)
        if not (t and l and d): continue
        try: ts = int(parsedate_to_datetime(d.group(1)).timestamp())
        except Exception: continue
        title = html.unescape(t.group(1).strip())
        if ts < T0 or not GOOG.search(title): continue
        add(norm(l.group(1)), url=l.group(1).strip(), title=title, co='Google', official=True, date=kst(ts), src='rss')

x = fetch('https://www.anthropic.com/news')
for m in re.finditer(r'href="(/news/[a-z0-9-]+)".{0,1500}?([A-Z][a-z]{2} \d{1,2}, 20\d\d)', x, re.S):
    try: ts = int(datetime.datetime.strptime(m.group(2), '%b %d, %Y').replace(tzinfo=KST).timestamp())
    except ValueError: continue
    if ts < T0: continue
    url = 'https://www.anthropic.com' + m.group(1)
    if norm(url) in cand or norm(url) in judged: continue
    t = re.search(r'og:title" content="([^"]*)"', fetch(url))
    add(norm(url), url=url, title=html.unescape(t.group(1)) if t else m.group(1).split('/')[-1], co='Anthropic', official=True, date=kst(ts), src='news')

# ── 관심 회사(음성): 목록에서 최근 글만 골라 글 페이지에서 제목, 날짜, 글 안 링크를 받는다 ──
MEDIA = [('ElevenLabs', 'https://elevenlabs.io', '/blog', r'/blog/(?!category/|authors/)[a-z0-9-]+')]
DATE = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2},? 20\d\d'
def day(s):
    s = s.replace('.', '').replace(',', '')
    for f in ('%b %d %Y', '%B %d %Y'):
        try: return datetime.datetime.strptime(s, f).replace(tzinfo=KST).timestamp()
        except ValueError: pass
    return None
for co, host, path, pat in MEDIA:
    x = fetch(host + path)
    for p in list(dict.fromkeys(re.findall(r'href="(' + pat + r')"', x)))[:12]:
        url = host + p
        if norm(url) in cand or norm(url) in judged: continue
        d = re.search(DATE, x[x.index('"' + p + '"'):][:2500])  # 목록의 날짜는 거르기만 — 짝이 밀릴 수 있어 글 페이지 날짜를 쓴다
        if d and (day(d.group(0)) or NOW) < T0 - 7 * 86400: continue
        y = fetch(url)
        t = re.search(r'og:title" content="([^"]*)"', y); pd = re.search(r'(?:article:published_time" content="|"datePublished":")(\d{4}-\d\d-\d\d)', y)
        if not (t and pd) or pd.group(1) < kst(T0): continue
        a = re.search(r'<article.*?</article>', y, re.S)
        links = []
        for m in re.finditer(r'<a [^>]*href="([^"#]+)"[^>]*>(.*?)</a>', a.group(0) if a else y, re.S):
            lu, lt = m.group(1), html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
            if lu.startswith('/'): lu = host + lu
            if lt and lu.startswith('http') and not re.search(r'sign-?up|login|/authors/|/category/|twitter|x\.com|linkedin', lu) and [lu, lt] not in links:
                links.append([lu, lt[:60]])
        dd = re.search(r'og:description" content="([^"]*)"', y)
        add(norm(url), url=url, title=html.unescape(t.group(1)), co=co, official=True, date=pd.group(1), src='blog',
            desc=html.unescape(dd.group(1))[:300] if dd else '', links=links[:30],
            media=len(set(re.findall(r'[\w./:%-]+\.(?:mp4|webm|mov|mp3|wav|m4a)\b', y))))  # 글에 박힌 영상과 소리 수

# ── 긱뉴스: 한국어 제목과 요약을 붙이고, 긱뉴스에만 있는 글도 줍는다 ──
R = (r"<a href='([^']+)' rel='nofollow' id='tr\d+' class='topic-title-link'><h2 class='topic-title-heading'>(.*?)</h2>"
     r".*?<a href='topic\?id=(\d+)' class='c99 breakall'>(.*?)</a>.*?<span id='tp\d+'>(\d+)</span> points.*?data-date=\"([\d-]+)\"")
gn = {}
for p in (1, 2, 3, 4, 5):
    rows = re.findall(R, fetch(f'https://news.hada.io/?page={p}'), re.S)
    for url, title, tid, desc, pts, date in rows:
        if url.startswith('http'):
            gn[norm(url)] = dict(tid=tid, title=html.unescape(title), desc=html.unescape(re.sub('<[^>]+>', '', desc)), pts=int(pts), date=date, url=url)
    if not rows or rows[-1][5] < kst(T0): break
    time.sleep(0.4)
GNAI = re.compile(AI.pattern + r'|에이전트|agent|llm|\bAI\b|AI', re.I)
for k, g in gn.items():
    if k in judged: continue
    if k in cand: cand[k]['gn'] = g; continue
    if g['pts'] >= 20 and g['date'] >= kst(T0) and GNAI.search(g['title'] + ' ' + g['desc'][:80]):
        add(k, url=g['url'], title=g['title'], co='기타', official=False, date=g['date'], src='gn')
        cand[k]['gn'] = g

# ── 묶음 글은 본문을 받아 둔다 ──
for c in cand.values():
    c['bundle'] = bool(c['official'] and BUNDLE.search(c['title'] + ' ' + c.get('desc', '')))
    if c['bundle']:
        # 이미지 주소는 걷어 낸다(설명만 남게). 받을 때마다 길이가 달라 넉넉히 6만 자
        c['body'] = re.sub(r'\]\(https?://[^)]*\.(?:png|jpe?g|webp|gif)[^)]*\)', ']', fetch('https://r.jina.ai/' + c['url'], 60))[:60000]

new = sorted(cand.values(), key=lambda c: (-c['pts'], c['date']))
# 판단(claude -p)은 3시간에 한 번 — 공식 발표나 1000점 넘는 글이 오면 바로
big = any(c['official'] or c['pts'] >= 1000 for c in new)
if new and not big and NOW - state.get('judged_at', 0) < 3 * 3600:
    print(f'소식 후보 {len(new)}개 — 3시간 안에 판단했으니 다음에'); new = []
json.dump(new, open('news_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
gh = os.environ.get('GITHUB_OUTPUT')
if gh: open(gh, 'a').write(f'news_has_new={"true" if new else "false"}\n')
print(f'소식 후보 {len(new)}개' + (': ' + ', '.join(c['title'][:30] for c in new[:8]) if new else ''))
