#!/usr/bin/env bash
# 깨졌으면 알려 준다. PR 전에 돌린다(전역 훅 pr_check.py 가 `gh pr create` 앞에서 부른다).
#
#   ./check.sh
#
# 1) index.html 의 인라인 <script> 전부 문법 검사 — 하나라도 깨지면 탭이 안 뜬다
# 2) 구간 표식 — 갱신 스크립트와 큐레이션이 경계로 쓰는 줄이 하나씩 있는지 (CLAUDE.md 「경고」)
# 3) JSON — news.json, models.json, index.html 안의 docsmap
# 4) scripts/*.py — 문법, 그리고 ruff 가 있으면 정의 안 된 이름
set -uo pipefail
cd "$(dirname "$0")"

fail=0
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# ── 1~3. index.html 과 JSON
python3 - "$work" <<'PY' || fail=1
import json, re, subprocess, sys
work = sys.argv[1]
src = open('index.html', encoding='utf-8').read()
bad = 0

blocks = re.findall(r'<script>(.*?)</script>', src, flags=re.S)
broken = []
for i, body in enumerate(blocks, 1):
    path = f'{work}/inline{i}.js'
    open(path, 'w', encoding='utf-8').write(body)
    r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
    if r.returncode:
        broken.append((i, r.stderr.strip().splitlines()[:4]))
if broken or not blocks:
    bad = 1
    print(f'✗ 인라인 스크립트 ({len(blocks)}개 중 {len(broken)}개 깨짐)')
    for i, lines in broken:
        print(f'   {i}번째 <script>')
        for line in lines: print('     ' + line)
else:
    print(f'✓ 인라인 스크립트 ({len(blocks)}개)')

marks = ['<!--CC-DATA-->', '<!--CX-DATA-->', '<!--AG-DATA-->',
         '<!--NEWS-->', '<!--/NEWS-->', '<!--MODELS-STATUS-->', '<!--/MODELS-STATUS-->',
         '<div id="data"', '<div class="tab on" id="new">']
off = [(m, src.count(m)) for m in marks if src.count(m) != 1]
if off:
    bad = 1
    print('✗ 구간 표식')
    for m, n in off: print(f'   {m} 가 {n}개 (1개여야 한다)')
else:
    print(f'✓ 구간 표식 ({len(marks)}개)')

jbad = []
for name in ('news.json', 'models.json'):
    try: json.load(open(name, encoding='utf-8'))
    except Exception as e: jbad.append(f'{name}: {e}')
m = re.search(r'<script type="application/json" id="docsmap">(.*?)</script>', src, flags=re.S)
if not m: jbad.append('index.html 에 docsmap 이 없다')
else:
    try: json.loads(m.group(1))
    except Exception as e: jbad.append(f'docsmap: {e}')
if jbad:
    bad = 1
    print('✗ JSON')
    for line in jbad: print('   ' + line)
else:
    print('✓ JSON (news.json, models.json, docsmap)')
sys.exit(bad)
PY

# ── 4. scripts/*.py
if out=$(python3 -m py_compile scripts/*.py 2>&1); then
  echo "✓ 파이썬 문법 ($(ls scripts/*.py | wc -l | tr -d ' ')개)"
else
  echo "✗ 파이썬 문법"; printf '%s\n' "$out" | tail -6 | sed 's/^/   /'; fail=1
fi
find scripts -name __pycache__ -type d -prune -exec rm -rf {} +

if command -v ruff >/dev/null; then
  # 정의 안 된 이름 같은 버그성만(F). 안 쓰는 import·변수와 빈 f-string 은 안 본다
  if out=$(ruff check --select F --ignore F401,F841,F541 --no-cache scripts 2>&1); then
    echo "✓ lint"
  else
    echo "✗ lint"; printf '%s\n' "$out" | grep -E "^\S+:[0-9]+:[0-9]+|^Found|^F[0-9]+" | head -20 | sed 's/^/   /'; fail=1
  fi
else
  echo "· lint 건너뜀 (ruff 없음)"
fi

[ "$fail" = 0 ] && echo "— 멀쩡하다" || echo "— 깨진 게 있다"
exit "$fail"
