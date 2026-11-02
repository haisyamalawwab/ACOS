"""Audit kelengkapan notebook ipynb di ACOS-IndoBERT/notebooks (read-only)."""
import json, os, re, datetime

NB = os.path.join(os.path.dirname(__file__), '..', 'notebooks')
rows = []
for fn in sorted(os.listdir(NB)):
    if not fn.endswith('.ipynb'):
        continue
    p = os.path.join(NB, fn)
    size = os.path.getsize(p)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%d%m%Y_%H%M')
    try:
        nb = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        rows.append((fn, size, mtime, 'PARSE_FAIL', str(e)[:40], '', '', '', '', ''))
        continue
    cells = nb.get('cells', [])
    code = [c for c in cells if c.get('cell_type') == 'code']
    md = [c for c in cells if c.get('cell_type') == 'markdown']
    with_out = [c for c in code if c.get('outputs')]
    errs = [c for c in code for o in c.get('outputs', []) if o.get('output_type') == 'error']
    execs = [c.get('execution_count') for c in code if c.get('execution_count') is not None]
    src_all = '\n'.join(''.join(c.get('source', [])) for c in code)
    refs = []
    for pat, tag in [(r'acos_id', 'acos_id'), (r'tokenized_data', 'tokenized'),
                     (r'results', 'results'), (r'Apps-ACOS', 'Apps-ACOS'),
                     (r'cv_5fold|cv5fold', 'cv5'), (r'cv_10fold|cv10fold', 'cv10'),
                     (r'split_801010|split_701515|split_602020', 'ratio'),
                     (r'experiment_runner', 'exp_runner'), (r'indobert|IndoBERT|indobert-base', 'indobert'),
                     (r'laptop|rest16', 'en_domain')]:
        if re.search(pat, src_all):
            refs.append(tag)
    kernel = (nb.get('metadata', {}).get('kernelspec', {}) or {}).get('name', '')
    status = 'EXECUTED' if len(execs) == len(code) and code else ('PARTIAL' if execs else 'NOT_RUN')
    rows.append((fn, size, mtime, status,
                 'code=%d md=%d out=%d err=%d lastExec=%s' % (len(code), len(md), len(with_out), len(errs), max(execs) if execs else '-'),
                 kernel, ','.join(refs), ''))

w = max(len(r[0]) for r in rows)
for r in rows:
    print('%-*s %8d B %s %-9s | %-46s | %-14s | %s' % (w, r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    if r[3] == 'PARSE_FAIL':
        print('    !!', r[4])
