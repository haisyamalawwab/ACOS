import json, glob, ast
fs = sorted(glob.glob('notebooks/V1_1_*.ipynb')) + ['notebooks/00_ACOS_Master_Pipeline_V1_1_BERT.ipynb']
bad = 0
for f in fs:
    nb = json.load(open(f, encoding='utf-8'))
    n = 0
    for i, c in enumerate(nb['cells']):
        if c.get('cell_type') == 'code':
            n += 1
            try:
                ast.parse(''.join(c.get('source', [])))
            except SyntaxError as e:
                bad += 1
                print('SYNTAX', f, i, e)
    print(f.split('/')[-1], 'cells=%d code=%d OK' % (len(nb['cells']), n))
print('BAD=', bad)
t = open('notebooks/00_ACOS_Master_Pipeline_V1_1_BERT.ipynb', encoding='utf-8').read()
t1 = open('notebooks/00_ACOS_Master_Pipeline_V1_BERT.ipynb', encoding='utf-8').read()
for k in ['find_resumable_session', 'save_pipeline_state', 'auto_find_latest_state',
          'ensure_objects', 'STEP1_SKIP_TRAINING', 'STEP2_SKIP_TRAINING',
          'MAX_EPOCHS_THIS_RUN', 'FORCE_REEVAL', 'session_manifest',
          'step1_progress.json', 'step2_progress.json', 'run_result.json',
          'session_dir', 'candidate_result_roots', 'candidate_state_roots',
          'drive_candidates', 'RESUME_LAST_SESSION', 'update_mcp_manifest',
          'write_stage_progress', 'session_cache_score']:
    print('%-28s V1=%-4d V1.1=%d' % (k, t1.count(k), t.count(k)))
