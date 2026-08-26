#coding=utf-8

import codecs as cs
import os
import sys

if len(sys.argv) > 3:
    pred_file = sys.argv[1]
    domian_type = sys.argv[2]
    out_file = sys.argv[3]
else:
    base_dir = sys.argv[1]
    domian_type = sys.argv[2]
    cur_dir = os.path.join(base_dir, 'output', 'Extract-Classify-QUAD', domian_type)
    pred_file = os.path.join(cur_dir + '_1st', 'pred4pipeline.txt')
    # Check possible locations for tokenized_data
    if os.path.exists(os.path.join(base_dir, 'tokenized_data')):
        out_file = os.path.join(base_dir, 'tokenized_data', domian_type + '_test_pair_1st.tsv')
    elif os.path.exists(os.path.join(base_dir, 'Extract-Classify-ACOS', 'tokenized_data')):
        out_file = os.path.join(base_dir, 'Extract-Classify-ACOS', 'tokenized_data', domian_type + '_test_pair_1st.tsv')
    else:
        out_file = os.path.join(base_dir, 'ACOS-main', 'Extract-Classify-ACOS', 'tokenized_data', domian_type + '_test_pair_1st.tsv')

if not os.path.exists(pred_file):
    # Try alternate location
    if os.path.exists(os.path.join(base_dir, 'pred4pipeline.txt')):
        pred_file = os.path.join(base_dir, 'pred4pipeline.txt')

os.makedirs(os.path.dirname(out_file), exist_ok=True)
f = cs.open(pred_file, 'r', encoding='utf-8').readlines()
wf = cs.open(out_file, 'w', encoding='utf-8')

for line in f:
    asp = []; opi = []
    line = line.strip().split('\t')
    if len(line) <= 1:
        continue
    text = line[0]
    af = 0
    of = 0
    for ele in line[1:]:
        if ele.startswith('a'):
            asp.append(ele[2:])
            af = 1
        else:
            opi.append(ele[2:])
            of = 1
    if af == 0:
        asp.append('-1,-1')
    if of == 0:
        opi.append('-1,-1')
    if len(asp)>0 and len(opi)>0:
        pred = []

        for pa in asp:
            ast, aed = int(pa.split(',')[0]), int(pa.split(',')[1])
            for po in opi:
                ost, oed = int(po.split(',')[0]), int(po.split(',')[1])
                pred.append([pa, po])
        for ele in pred:  
            wf.write(text+'####'+ele[0]+' '+ele[1]+'\n')
