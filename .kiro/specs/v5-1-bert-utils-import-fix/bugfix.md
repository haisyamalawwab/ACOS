# Bugfix Requirements Document

## Introduction

V5_1 notebook (`01_ACOS_V5_1_FullExperiment_GPU_ROCM_CUDA_DriveSync.ipynb`) fails to import `bert_utils.tokenization.BertTokenizer` in cell 3 (line 236) despite:
- File validation showing `bert_utils/tokenization.py` exists and returns True
- The `upstream_root` path being successfully identified and printed
- V4 and V4_1 notebooks successfully importing the same modules using similar patterns

The bug prevents the notebook from initializing, blocking all subsequent training experiments. The issue stems from incorrect sys.path manipulation timing where the path is added to sys.path before the final validated upstream_root value is determined.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN cell 3 executes the path setup logic THEN the system calls `_prepend_path(upstream_root)` at line ~686 before `upstream_root` is reassigned by `extract_dir = acos_upstream.ensure_path(acos_root=base_project_dir)` at line ~702

1.2 WHEN the import statement `from bert_utils.tokenization import BertTokenizer` executes at line 236 (in actual execution, line 705 in source) THEN the system raises `ModuleNotFoundError: No module named 'bert_utils'` because sys.path does not contain the correct validated upstream_root path

1.3 WHEN the validation print statement shows `bert_utils/ : True` THEN this validation check uses the initial `upstream_root` variable value from the manual search loop (lines 635-671), but the subsequent `acos_upstream.ensure_path()` call at line 702 reassigns `upstream_root` without re-calling `_prepend_path()`

### Expected Behavior (Correct)

2.1 WHEN cell 3 executes the path setup logic THEN the system SHALL call `_prepend_path(upstream_root)` AFTER `upstream_root` has been assigned its final value from `acos_upstream.ensure_path()` to ensure sys.path contains the correct validated path

2.2 WHEN the import statement `from bert_utils.tokenization import BertTokenizer` executes THEN the system SHALL successfully import BertTokenizer without raising ModuleNotFoundError

2.3 WHEN the system calls `acos_upstream.ensure_path()` and it returns a valid extract_dir THEN the system SHALL update sys.path with this validated path before attempting any imports from bert_utils or modeling modules

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the Extract-Classify-ACOS directory exists and is valid in the initial search (lines 635-671) THEN the system SHALL CONTINUE TO identify and validate it correctly with `_is_upstream()` checks

3.2 WHEN validation prints show file existence status (modeling.py, bert_utils/) THEN the system SHALL CONTINUE TO display accurate True/False values based on actual file existence

3.3 WHEN the notebook needs to clone Extract-Classify-ACOS repository because it's missing THEN the system SHALL CONTINUE TO perform the git clone operation and copy files to the target location

3.4 WHEN `_prepend_path()` is called with a valid directory path THEN the system SHALL CONTINUE TO remove any existing occurrences of that path from sys.path and insert it at position 0

3.5 WHEN imports succeed for other modules like `acos_id.taxonomy`, `acos_id.checkpoint`, `modeling.BertForQuadABSA` THEN the system SHALL CONTINUE TO import these modules successfully as they do in V4/V4_1 patterns
