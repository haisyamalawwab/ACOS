#!/usr/bin/env python3
"""Hitung proyeksi set per baris pada ACOS TSV; bukan eksperimen model."""
from pathlib import Path
from collections import Counter
import csv

ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS = {'Aspect': (0,), 'Category': (1,), 'Opinion': (3,),
               'Sentiment_per_row': (2,), 'AS Pair': (0, 2), 'AO Pair': (0, 3),
               'AOS Triple': (0, 3, 2), 'ACS Triple': (0, 1, 2), 'ACOS Quadruple': (0, 1, 3, 2)}
NULL = '-1,-1'

def count(path):
    stats = Counter()
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        cells = line.split('\t')
        if len(cells) < 2 or not cells[0].strip():
            raise ValueError(f'{path}:{n}: baris tidak valid')
        qs = []
        for cell in cells[1:]:
            v = tuple(cell.split())
            if len(v) != 4:
                raise ValueError(f'{path}:{n}: quadruple tidak valid: {cell!r}')
            qs.append(v)
        stats['Rows'] += 1
        stats['Raw quadruples'] += len(qs)
        stats['Duplicate quadruples'] += len(qs) - len(set(qs))
        for label, indexes in PROJECTIONS.items():
            stats[label] += len({tuple(q[i] for i in indexes) for q in qs})
        for a, o in ((False, False), (False, True), (True, False), (True, True)):
            stats[f'IA={int(a)},IO={int(o)}'] += sum((q[0] == NULL) == a and (q[3] == NULL) == o for q in qs)
        stats['AO explicit only'] += len({(q[0], q[3]) for q in qs if q[0] != NULL and q[3] != NULL})
        stats['ACOS explicit only'] += len({q for q in qs if q[0] != NULL and q[3] != NULL})
    return stats

def main():
    sources = {'AppsID': ROOT/'ACOS-IndoBERT/data/Apps-ACOS', 'Restaurant-ACOS': ROOT/'data/Restaurant-ACOS', 'Laptop-ACOS': ROOT/'data/Laptop-ACOS'}
    prefix = {'AppsID': 'appsid', 'Restaurant-ACOS': 'rest16', 'Laptop-ACOS': 'laptop'}
    rows=[]
    for dataset, folder in sources.items():
        total = Counter()
        for split in ('train', 'dev', 'test'):
            file = folder/f'{prefix[dataset]}_quad_{split}.tsv'
            c = count(file); total.update(c)
            rows.append({'dataset': dataset, 'split': split, **c})
        rows.append({'dataset': dataset, 'split': 'total', **total})
    out = ROOT/'reports/055_estadistik_acos_projection.csv'
    fields = list(rows[0]);
    with out.open('w', encoding='utf-8', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    for row in rows:
        print(row)
    print('Saved:', out)
if __name__ == '__main__': main()
