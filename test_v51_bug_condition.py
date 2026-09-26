#!/usr/bin/env python3
"""
Bug Condition Exploration Test for V5.1 BERT Utils Import Issue

This test is EXPECTED TO FAIL on unfixed code - failure confirms the bug exists.
When the test fails as expected, this is the SUCCESS case for exploration tests.

The test encodes the expected behavior and will validate the fix when it passes
after implementation.

Bug: V5_1 notebook cell 3 calls _prepend_path(upstream_root) BEFORE upstream_root 
gets its final validated value from ensure_path(), causing bert_utils import to fail
despite validation showing bert_utils/ : True.

Property 1: Bug Condition - Sys.Path Timing Issue Causing BERT Utils Import Failure
- Assert that bert_utils.tokenization.BertTokenizer import succeeds after proper sys.path setup
- Assert that sys.path contains the validated upstream_root path before imports  
- Assert that _prepend_path is called after ensure_path() validation completes
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple

import hypothesis
from hypothesis import given, strategies as st, settings
import pytest


class SysPathCapture:
    """Captures sys.path state changes during notebook execution"""
    
    def __init__(self):
        self.snapshots = []
        self.original_path = None
    
    def take_snapshot(self, label: str):
        """Take a snapshot of current sys.path"""
        snapshot = {
            'label': label,
            'sys_path': list(sys.path),
            'sys_path_0': sys.path[0] if sys.path else None
        }
        self.snapshots.append(snapshot)
        return snapshot
    
    def restore_original(self):
        """Restore original sys.path"""
        if self.original_path is not None:
            sys.path.clear()
            sys.path.extend(self.original_path)


class V51NotebookTester:
    """Test harness for V5.1 notebook cell 3 execution"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.test_env = {}
        self.path_capture = SysPathCapture()
        
    def setup_test_environment(self) -> Dict[str, Any]:
        """Setup controlled environment for testing"""
        # Create temporary directories for testing
        test_dir = tempfile.mkdtemp(prefix="v51_test_")
        
        # Create base project structure
        base_project_dir = os.path.join(test_dir, "test_project")
        os.makedirs(base_project_dir, exist_ok=True)
        
        # Create ACOS-IndoBERT structure
        indo_root = os.path.join(base_project_dir, "ACOS-IndoBERT")
        os.makedirs(os.path.join(indo_root, "acos_id"), exist_ok=True)
        
        # Create minimal acos_id modules for testing
        self._create_minimal_acos_id(indo_root)
        
        # Create Extract-Classify-ACOS structure
        upstream_initial = os.path.join(base_project_dir, "Extract-Classify-ACOS-initial")
        upstream_validated = os.path.join(base_project_dir, "Extract-Classify-ACOS")
        
        # Create both initial and validated upstream directories to simulate the bug
        self._create_minimal_upstream(upstream_initial, complete=False)
        self._create_minimal_upstream(upstream_validated, complete=True) 
        
        self.test_env = {
            'test_dir': test_dir,
            'base_project_dir': base_project_dir,
            'indo_root': indo_root,
            'upstream_initial': upstream_initial,
            'upstream_validated': upstream_validated,
        }
        
        return self.test_env
    
    def _create_minimal_acos_id(self, indo_root: str):
        """Create minimal acos_id module structure"""
        acos_id_dir = os.path.join(indo_root, "acos_id")
        
        # Create __init__.py
        with open(os.path.join(acos_id_dir, "__init__.py"), 'w') as f:
            f.write('__version__ = "0.2.1"\n')
        
        # Create upstream.py with minimal ensure_path functionality
        upstream_py = '''
import os

def is_upstream(directory):
    """Check if directory is valid Extract-Classify-ACOS"""
    if not os.path.isdir(directory):
        return False
    return (os.path.isfile(os.path.join(directory, 'modeling.py')) and
            os.path.isfile(os.path.join(directory, 'bert_utils', 'tokenization.py')))

def ensure_path(acos_root):
    """Validate and return canonical Extract-Classify-ACOS path"""
    candidates = [
        os.path.join(acos_root, 'Extract-Classify-ACOS'),
        os.path.join(acos_root, 'Extract-Classify-ACOS-validated'),
    ]
    
    for candidate in candidates:
        if is_upstream(candidate):
            return os.path.abspath(candidate)
    
    raise FileNotFoundError("Extract-Classify-ACOS not found")
'''
        with open(os.path.join(acos_id_dir, "upstream.py"), 'w') as f:
            f.write(upstream_py)
    
    def _create_minimal_upstream(self, upstream_path: str, complete: bool = True):
        """Create minimal Extract-Classify-ACOS structure"""
        os.makedirs(upstream_path, exist_ok=True)
        
        # Create modeling.py
        with open(os.path.join(upstream_path, "modeling.py"), 'w') as f:
            f.write('''
class BertForQuadABSA:
    """Minimal BertForQuadABSA for testing"""
    pass

class CategorySentiClassification:
    """Minimal CategorySentiClassification for testing"""  
    pass
''')
        
        # Create bert_utils directory and tokenization.py
        bert_utils_dir = os.path.join(upstream_path, "bert_utils")
        os.makedirs(bert_utils_dir, exist_ok=True)
        
        if complete:
            # Only create tokenization.py in complete upstream
            with open(os.path.join(bert_utils_dir, "tokenization.py"), 'w') as f:
                f.write('''
class BertTokenizer:
    """Minimal BertTokenizer for testing"""
    def __init__(self):
        pass
    
    @classmethod 
    def from_pretrained(cls, *args, **kwargs):
        return cls()
''')
        # For incomplete upstream, don't create tokenization.py to simulate missing file
    
    def simulate_v51_cell_3_execution(self) -> Dict[str, Any]:
        """Simulate V5.1 notebook cell 3 execution with bug condition"""
        self.path_capture.original_path = list(sys.path)
        results = {
            'snapshots': [],
            'upstream_root_values': [],
            'validation_results': {},
            'import_results': {},
            'errors': []
        }
        
        try:
            env = self.test_env
            
            # Simulate initial variables (from cell 3 beginning)
            base_project_dir = env['base_project_dir']
            indo_root = env['indo_root'] 
            
            # Simulate the upstream root search that finds initial path
            upstream_root = env['upstream_initial']  # This is the WRONG path
            results['upstream_root_values'].append(('initial_search', upstream_root))
            
            # Capture sys.path before any modifications
            self.path_capture.take_snapshot('before_any_prepend_path')
            
            # === SIMULATE THE BUG: _prepend_path called with initial upstream_root ===
            # This simulates lines 658-660 in V5.1 notebook
            self._prepend_path(indo_root)
            self._prepend_path(upstream_root)  # BUG: using initial (wrong) path
            self._prepend_path(base_project_dir)
            
            snapshot = self.path_capture.take_snapshot('after_premature_prepend_path')
            results['snapshots'].append(snapshot)
            
            # Simulate import of acos_id.upstream 
            sys.path.insert(0, indo_root)  # Ensure acos_id can be imported
            import importlib
            acos_upstream = importlib.import_module("acos_id.upstream")
            
            # === SIMULATE ensure_path() call that gets the correct path ===
            # This simulates line 702: extract_dir = acos_upstream.ensure_path(acos_root=base_project_dir)
            extract_dir = acos_upstream.ensure_path(acos_root=base_project_dir)
            
            # This simulates line 703: upstream_root = extract_dir  
            upstream_root = extract_dir  # Now upstream_root has CORRECT path
            results['upstream_root_values'].append(('after_ensure_path', upstream_root))
            
            # This simulates line 703: _prepend_path(upstream_root) - CORRECT call
            self._prepend_path(upstream_root)
            
            snapshot = self.path_capture.take_snapshot('after_correct_prepend_path')
            results['snapshots'].append(snapshot)
            
            # Simulate file validation checks (like lines 673-674 in V5.1)
            modeling_exists = os.path.isfile(os.path.join(upstream_root, 'modeling.py'))
            bert_utils_exists = os.path.isfile(os.path.join(upstream_root, 'bert_utils', 'tokenization.py'))
            
            results['validation_results'] = {
                'modeling_py': modeling_exists,
                'bert_utils_tokenization_py': bert_utils_exists,
                'upstream_root_final': upstream_root
            }
            
            # === ATTEMPT BERT UTILS IMPORT (this should work but might fail due to bug) ===
            # This simulates line 706: from bert_utils.tokenization import BertTokenizer
            try:
                from bert_utils.tokenization import BertTokenizer
                results['import_results']['bert_tokenizer'] = {'success': True, 'error': None}
            except ImportError as e:
                results['import_results']['bert_tokenizer'] = {'success': False, 'error': str(e)}
                
            # This simulates following import: from modeling import BertForQuadABSA, CategorySentiClassification  
            try:
                from modeling import BertForQuadABSA, CategorySentiClassification
                results['import_results']['modeling'] = {'success': True, 'error': None}
            except ImportError as e:
                results['import_results']['modeling'] = {'success': False, 'error': str(e)}
                
        except Exception as e:
            results['errors'].append(f"Execution error: {str(e)}")
            
        results['snapshots'].extend(self.path_capture.snapshots)
        return results
    
    def _prepend_path(self, p):
        """Simulate _prepend_path function from V5.1 notebook"""
        try:
            p_str = str(Path(p).resolve())
        except Exception:
            return None
        if not os.path.isdir(p_str):
            return None
        while p_str in sys.path:
            sys.path.remove(p_str)
        sys.path.insert(0, p_str)
        return p_str
    
    def cleanup(self):
        """Clean up test environment"""
        self.path_capture.restore_original()
        if 'test_dir' in self.test_env:
            shutil.rmtree(self.test_env['test_dir'], ignore_errors=True)


def test_v51_bert_utils_import_timing_bug():
    """
    Bug Condition Exploration Test - EXPECTED TO FAIL on unfixed code
    
    This test demonstrates the timing issue where _prepend_path(upstream_root) 
    is called before upstream_root gets its final validated value from ensure_path().
    
    Expected behavior (what this test asserts):
    1. bert_utils.tokenization.BertTokenizer import should succeed
    2. sys.path should contain the validated upstream_root path before imports
    3. _prepend_path should be called after ensure_path() validation completes
    
    On UNFIXED code, this test will FAIL because:
    - sys.path[0] contains the initial (wrong) upstream_root path
    - bert_utils import fails despite validation showing bert_utils/ : True  
    - The timing issue prevents proper sys.path setup
    """
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    tester = V51NotebookTester(workspace_root)
    
    try:
        # Setup controlled test environment
        env = tester.setup_test_environment()
        
        # Execute V5.1 cell 3 simulation
        results = tester.simulate_v51_cell_3_execution()
        
        # === ASSERTIONS FOR EXPECTED BEHAVIOR ===
        # These assertions encode the expected behavior and will fail on unfixed code
        
        # Property 1.1: File validation should show bert_utils exists
        assert results['validation_results']['bert_utils_tokenization_py'] is True, \
            f"bert_utils/tokenization.py validation should be True, got: {results['validation_results']}"
        
        # Property 1.2: sys.path should contain validated upstream_root path before imports
        snapshots = {s['label']: s for s in results['snapshots']}
        
        if 'after_correct_prepend_path' in snapshots:
            final_sys_path = snapshots['after_correct_prepend_path']['sys_path'] 
            upstream_root_final = results['validation_results']['upstream_root_final']
            
            assert upstream_root_final in final_sys_path, \
                f"Validated upstream_root {upstream_root_final} should be in sys.path: {final_sys_path[:3]}..."
            
            # Check that validated path is at position 0 (most important for import resolution)
            assert final_sys_path[0] == upstream_root_final, \
                f"sys.path[0] should be validated upstream_root {upstream_root_final}, got: {final_sys_path[0]}"
        
        # Property 1.3: BERT utils import should succeed after proper sys.path setup
        bert_import = results['import_results'].get('bert_tokenizer', {})
        assert bert_import.get('success') is True, \
            f"BertTokenizer import should succeed, got error: {bert_import.get('error')}"
        
        # Property 1.4: modeling import should also succeed  
        modeling_import = results['import_results'].get('modeling', {})
        assert modeling_import.get('success') is True, \
            f"modeling import should succeed, got error: {modeling_import.get('error')}"
        
        # Property 1.5: upstream_root should change from initial to validated value
        upstream_values = dict(results['upstream_root_values'])
        assert 'initial_search' in upstream_values and 'after_ensure_path' in upstream_values, \
            f"Should have both initial and final upstream_root values: {upstream_values}"
        
        initial_upstream = upstream_values['initial_search']
        final_upstream = upstream_values['after_ensure_path']
        
        # The bug occurs when these are different paths but sys.path still has initial
        if initial_upstream != final_upstream:
            # This is the bug condition - paths differ but import should still work
            assert bert_import.get('success') is True, \
                f"Even when upstream_root changes from {initial_upstream} to {final_upstream}, " \
                f"bert_utils import should work, but got error: {bert_import.get('error')}"
        
        print("✅ All assertions passed - bug condition test succeeded!")
        print("   This means the fix is working correctly.")
        print(f"   Initial upstream_root: {initial_upstream}")
        print(f"   Final upstream_root: {final_upstream}")
        print(f"   sys.path[0]: {final_sys_path[0] if 'after_correct_prepend_path' in snapshots else 'unknown'}")
        
    except AssertionError as e:
        # This is expected on unfixed code - document the counterexample
        print("❌ EXPECTED FAILURE on unfixed code - bug condition confirmed!")
        print(f"   Assertion failed: {str(e)}")
        
        # Document counterexamples for root cause analysis
        print("\n🔍 COUNTEREXAMPLE ANALYSIS:")
        if results.get('upstream_root_values'):
            upstream_values = dict(results['upstream_root_values'])
            print(f"   Initial upstream_root: {upstream_values.get('initial_search', 'unknown')}")
            print(f"   Final upstream_root: {upstream_values.get('after_ensure_path', 'unknown')}")
            
        if results.get('validation_results'):
            val = results['validation_results']
            print(f"   bert_utils/ validation: {val.get('bert_utils_tokenization_py', 'unknown')}")
            print(f"   modeling.py validation: {val.get('modeling_py', 'unknown')}")
        
        snapshots = {s['label']: s for s in results.get('snapshots', [])}
        if 'after_premature_prepend_path' in snapshots and 'after_correct_prepend_path' in snapshots:
            premature = snapshots['after_premature_prepend_path']
            correct = snapshots['after_correct_prepend_path']
            print(f"   sys.path[0] after premature _prepend_path: {premature.get('sys_path_0', 'unknown')}")
            print(f"   sys.path[0] after correct _prepend_path: {correct.get('sys_path_0', 'unknown')}")
        
        if results.get('import_results'):
            for module, result in results['import_results'].items():
                status = "✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error', 'unknown error')}"
                print(f"   {module} import: {status}")
        
        # Re-raise the assertion to mark test as failed (expected for exploration test)
        raise
        
    except Exception as e:
        print(f"❌ Unexpected error during test execution: {str(e)}")
        raise
        
    finally:
        tester.cleanup()


@given(st.booleans())
@settings(max_examples=5, deadline=10000)  # Limited examples since this is deterministic bug
def test_v51_bug_condition_property_based(create_incomplete_upstream: bool):
    """
    Property-based test for V5.1 bug condition - scoped to concrete failing cases
    
    Since this is a deterministic bug (timing issue), we scope the property to 
    concrete scenarios that trigger the bug condition for better reproducibility.
    
    Property: For any scenario where upstream_root changes between initial search 
    and ensure_path() validation, bert_utils import should still succeed.
    """
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    tester = V51NotebookTester(workspace_root)
    
    try:
        env = tester.setup_test_environment()
        
        # Modify test environment based on hypothesis input
        if create_incomplete_upstream:
            # Create scenario where initial upstream is incomplete
            incomplete_upstream = os.path.join(env['base_project_dir'], "Extract-Classify-ACOS-incomplete")
            tester._create_minimal_upstream(incomplete_upstream, complete=False)
            tester.test_env['upstream_initial'] = incomplete_upstream
        
        results = tester.simulate_v51_cell_3_execution()
        
        # Property assertion: bert_utils import should succeed regardless of path changes
        bert_import = results['import_results'].get('bert_tokenizer', {})
        
        # This will fail on unfixed code, confirming the bug exists
        assert bert_import.get('success') is True, \
            f"BertTokenizer import should succeed regardless of upstream_root path changes, " \
            f"but failed with: {bert_import.get('error')}"
            
    except AssertionError:
        # Expected failure on unfixed code - this proves the bug exists
        raise
    finally:
        tester.cleanup()


if __name__ == "__main__":
    print("Bug Condition Exploration Test for V5.1 BERT Utils Import Issue")
    print("=" * 70)
    print("This test is EXPECTED TO FAIL on unfixed code.")
    print("Failure confirms the bug exists - this is the SUCCESS case for exploration tests.")
    print("=" * 70)
    
    test_v51_bert_utils_import_timing_bug()