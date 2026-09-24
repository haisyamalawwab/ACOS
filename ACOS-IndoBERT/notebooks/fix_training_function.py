#!/usr/bin/env python
# coding=utf-8
"""Fix the train_one_run function to use correct helper functions."""

import json

notebook_path = "01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb"

print(f"Reading {notebook_path}...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 3 (imports) and fix it
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if '# Import modul acos_id' in source and 'from acos_id import taxonomy as acos_taxonomy' in source:
            print("Fixing Cell 3 imports...")
            
            # Ensure correct imports
            new_source = source
            
            # Add the helper import if not there
            if 'from acos_id import model_wrappers' not in new_source:
                # Find the line after acos_taxonomy import
                lines = new_source.split('\n')
                new_lines = []
                for line in lines:
                    new_lines.append(line)
                    if 'from acos_id import taxonomy as acos_taxonomy' in line:
                        new_lines.append('from acos_id import model_wrappers')
                new_source = '\n'.join(new_lines)
            
            cell['source'] = [line + '\n' if i < len(new_source.split('\n')) - 1 else line 
                            for i, line in enumerate(new_source.split('\n'))]
            print("✓ Cell 3 fixed")
            break

# Find Cell 8 (train_one_run) and fix data loading
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'def train_one_run(cfg: dict)' in source:
            print("Fixing Cell 8 train_one_run function...")
            
            # Fix the load_loader function
            new_source = source.replace(
                """    def load_loader(split, batch_size, shuffle):
        path = os.path.join(tok_dir, f'appsid_{split}_quad_bert.tsv')
        dataset = model_wrappers.load_and_cache_examples(
            task='acos_extraction', data_file=path,
            tokenizer=tokenizer, max_seq_length=MAX_SEQ_LENGTH)
        return DataLoader(dataset, batch_size=batch_size,
                          shuffle=shuffle, num_workers=NUM_WORKERS)""",
                """    def load_loader(split, batch_size, shuffle):
        path = os.path.join(tok_dir, f'appsid_{split}_quad_bert.tsv')
        dataset = model_wrappers.load_quad_tsv_dataset(
            path, tokenizer, max_seq_length=MAX_SEQ_LENGTH)
        return DataLoader(dataset, batch_size=batch_size,
                          shuffle=shuffle, num_workers=NUM_WORKERS)"""
            )
            
            # Fix the evaluation metrics computation
            new_source = new_source.replace(
                """        # Evaluasi dev
        model.eval()
        tp = fp = fn = 0
        with torch.no_grad():
            for batch in dev_loader:
                batch = {k: v.to(DEVICE) for k, v in batch.items()}
                preds = model.predict(**batch)
                _tp, _fp, _fn = model_wrappers.compute_tp_fp_fn(preds, batch)
                tp += _tp; fp += _fp; fn += _fn

        prec = tp / (tp + fp + 1e-9)
        rec  = tp / (tp + fn + 1e-9)
        f1   = 2 * prec * rec / (prec + rec + 1e-9) * 100""",
                """        # Evaluasi dev
        eval_results = model_wrappers.compute_extraction_metrics(
            model, dev_loader, DEVICE)
        f1 = eval_results['f1']
        prec = eval_results['precision']
        rec = eval_results['recall']"""
            )
            
            cell['source'] = [line + '\n' if i < len(new_source.split('\n')) - 1 else line 
                            for i, line in enumerate(new_source.split('\n'))]
            print("✓ Cell 8 fixed")
            break

# Save fixed notebook
print(f"\nSaving fixed notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✓ Notebook training function fixed!")
print("\nChanges made:")
print("1. Added import for model_wrappers helper module")
print("2. Updated data loading to use load_quad_tsv_dataset")
print("3. Updated evaluation to use compute_extraction_metrics")
