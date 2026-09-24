#!/usr/bin/env python
# coding=utf-8
"""Fix import to use simpler approach."""

import json

notebook_path = "01_ACOS_MI300X_V5_FullExperiment_GPU_AMD_MI300X.ipynb"

print(f"Reading {notebook_path}...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Cell 3 and simplify the import
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'import acos_id.model_wrappers as model_wrappers' in source:
            print("Found cell with complex import!")
            print("Simplifying import...")
            
            # Replace complex import with simpler one
            new_source = source.replace(
                'import acos_id.model_wrappers as model_wrappers',
                '# Import model_wrappers after acos_id\n# (will be imported later after sys.path is set)'
            )
            
            # Also remove the duplicate import later
            new_source = new_source.replace(
                'from acos_id import model_wrappers\n',
                ''
            )
            
            # Add it AFTER the acos_id.experiment_runner import
            new_source = new_source.replace(
                'from acos_id.experiment_runner import (\n    prepare_all_data, run_all_experiments, aggregate_cv_results,\n)',
                'from acos_id.experiment_runner import (\n    prepare_all_data, run_all_experiments, aggregate_cv_results,\n)\nfrom acos_id import model_wrappers'
            )
            
            cell['source'] = [line + '\n' if i < len(new_source.split('\n')) - 1 else line 
                            for i, line in enumerate(new_source.split('\n'))]
            print("✓ Import simplified!")
            break

# Save fixed notebook
print(f"\nSaving fixed notebook...")
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✓ Import fixed!")
print("\nChanges:")
print("- Moved model_wrappers import to after other acos_id imports")
print("- This ensures sys.path is properly set before importing")
