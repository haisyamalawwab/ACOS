#!/usr/bin/env python
# coding=utf-8
"""Fix import errors in notebook by replacing incorrect module names."""

import json
import sys

notebook_path = "01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb"

print(f"Reading {notebook_path}...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find and fix the imports in Cell 3
fixed = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
            
        # Check if this is the cell with the broken imports
        if 'import processor_utils as acos_proc' in source_text:
            print("Found cell with incorrect imports!")
            print("Fixing imports...")
            
            # Replace the incorrect imports
            new_source = source_text.replace(
                '# Import modul upstream\n' + 
                'from bert_utils.tokenization import BertTokenizer\n' +
                'import processor_utils as acos_proc\n' +
                'import model_utils as acos_model\n',
                
                '# Import modul upstream (Extract-Classify-ACOS)\n' +
                'from bert_utils.tokenization import BertTokenizer\n' +
                'from modeling import BertForQuadABSA, CategorySentiClassification\n' +
                'import acos_id.model_wrappers as model_wrappers\n'
            )
            
            # Convert back to list format for notebook
            cell['source'] = new_source.split('\n')
            # Add back newlines at end of each line except last
            cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line 
                            for i, line in enumerate(cell['source'])]
            fixed = True
            print("✓ Imports fixed!")
            break

if not fixed:
    print("ERROR: Could not find the cell with imports to fix")
    sys.exit(1)

# Also need to fix references to acos_proc and acos_model in Cell 8
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
            
        # Fix the train_one_run function
        if 'def train_one_run(cfg: dict)' in source_text:
            print("Fixing train_one_run function...")
            
            # Replace acos_proc.load_and_cache_examples
            new_source = source_text.replace(
                'acos_proc.load_and_cache_examples(',
                'model_wrappers.load_and_cache_examples('
            )
            
            # Replace acos_proc.compute_tp_fp_fn
            new_source = new_source.replace(
                'acos_proc.compute_tp_fp_fn(',
                'model_wrappers.compute_tp_fp_fn('
            )
            
            # Replace acos_model.BertForQuadABSA
            new_source = new_source.replace(
                'acos_model.BertForQuadABSA.',
                'BertForQuadABSA.'
            )
            
            # Convert back to list format
            cell['source'] = new_source.split('\n')
            cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line 
                            for i, line in enumerate(cell['source'])]
            print("✓ train_one_run function fixed!")
            break

# Save the fixed notebook
output_path = notebook_path
print(f"\nSaving fixed notebook to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✓ Notebook fixed successfully!")
print("\nChanges made:")
print("1. Replaced 'import processor_utils as acos_proc' with proper imports")
print("2. Replaced 'import model_utils as acos_model' with proper imports")
print("3. Updated function calls in train_one_run to use correct module references")
