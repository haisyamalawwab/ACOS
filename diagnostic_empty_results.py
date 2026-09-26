# =============================================================================
# DIAGNOSTIC: Why Are Results Empty?
# =============================================================================

import os
from pathlib import Path

def diagnose_empty_results():
    """Diagnose why experiment results are empty"""
    
    print("🔍 DIAGNOSING EMPTY RESULTS ISSUE")
    print("=" * 60)
    
    # Expected results path (from your output)
    results_root = "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results/experiments"
    
    # Check 1: Folder exists and permissions
    print("\n1️⃣  CHECKING FOLDER PERMISSIONS")
    print("-" * 60)
    
    if os.path.exists(results_root):
        print(f"✅ Results folder exists: {results_root}")
        
        # Check write permissions
        try:
            test_file = os.path.join(results_root, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print("✅ Write permissions OK")
        except Exception as e:
            print(f"❌ Write permission DENIED: {e}")
            return "PERMISSION_ISSUE"
    else:
        print(f"❌ Results folder NOT FOUND: {results_root}")
        return "FOLDER_NOT_FOUND"
    
    # Check 2: DRY_RUN status
    print("\n2️⃣  CHECKING DRY_RUN STATUS")
    print("-" * 60)
    
    try:
        dry_run = globals().get('DRY_RUN', None)
        if dry_run is None:
            print("⚠️  DRY_RUN variable not defined yet")
        elif dry_run == True:
            print("❌ DRY_RUN = True (Preview mode - NO ACTUAL TRAINING)")
            print("   💡 Solution: Set CONFIG['DRY_RUN'] = False in Cell 2")
            return "DRY_RUN_ENABLED"
        else:
            print(f"✅ DRY_RUN = {dry_run} (Training enabled)")
    except Exception as e:
        print(f"⚠️  Cannot check DRY_RUN: {e}")
    
    # Check 3: Experiment execution status
    print("\n3️⃣  CHECKING EXPERIMENT EXECUTION")
    print("-" * 60)
    
    # Look for any partial results
    subdirs = ['csv', 'plots', 'md', 'logs', 'checkpoints']
    any_files = False
    
    for subdir in subdirs:
        subdir_path = os.path.join(results_root, subdir)
        if os.path.exists(subdir_path):
            file_count = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
            print(f"  {subdir:12s}: {file_count} files")
            if file_count > 0:
                any_files = True
        else:
            print(f"  {subdir:12s}: folder not created yet")
    
    if not any_files:
        print("\n❌ NO FILES FOUND - Training has not completed successfully")
        return "NO_EXECUTION"
    
    # Check 4: Look for error logs
    print("\n4️⃣  CHECKING FOR ERROR LOGS")
    print("-" * 60)
    
    error_indicators = []
    
    # Check for Colab output logs
    colab_logs = ['/content/.config/logs', '/tmp/colab_logs']
    for log_dir in colab_logs:
        if os.path.exists(log_dir):
            print(f"  Checking: {log_dir}")
    
    # Check 5: Training state
    print("\n5️⃣  CHECKING TRAINING STATE")
    print("-" * 60)
    
    try:
        # Check if any models were trained
        checkpoint_dir = os.path.join(results_root, "checkpoints")
        if os.path.exists(checkpoint_dir):
            checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.pt') or f.endswith('.pth')]
            if checkpoints:
                print(f"✅ Found {len(checkpoints)} checkpoint(s)")
                for ckpt in checkpoints[:3]:
                    print(f"   - {ckpt}")
            else:
                print("❌ No checkpoints found - training did not save models")
        else:
            print("❌ Checkpoint directory does not exist")
            return "NO_TRAINING"
    except Exception as e:
        print(f"⚠️  Error checking checkpoints: {e}")
    
    # Check 6: ResultSaver status
    print("\n6️⃣  CHECKING RESULTSAVER STATUS")
    print("-" * 60)
    
    try:
        result_saver = globals().get('ResultSaver', None)
        if result_saver is None:
            print("❌ ResultSaver class not imported")
            return "RESULTSAVER_NOT_IMPORTED"
        else:
            print("✅ ResultSaver class available")
    except Exception as e:
        print(f"⚠️  Cannot check ResultSaver: {e}")
    
    return "UNKNOWN"

# =============================================================================
# SOLUTIONS BASED ON DIAGNOSIS
# =============================================================================

def provide_solution(issue_type):
    """Provide solution based on diagnosed issue"""
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDED SOLUTIONS")
    print("=" * 60)
    
    solutions = {
        "DRY_RUN_ENABLED": """
🔧 SOLUTION: Disable DRY_RUN mode

In Cell 2, change:
    CONFIG = {
        'DRY_RUN': False,  # ← Change True to False
        ...
    }

Then:
1. Re-run Cell 2
2. Continue to Cell 9 (run_all_experiments)
3. Wait for training to complete
        """,
        
        "NO_EXECUTION": """
🔧 SOLUTION: Run the training cells

1. Make sure DRY_RUN = False in Cell 2
2. Run all cells in order: 1 → 2 → 3 → ... → 9
3. Wait for Cell 9 to complete (may take hours)
4. Check results in Cell 11
        """,
        
        "PERMISSION_ISSUE": """
🔧 SOLUTION: Fix Google Drive permissions

1. Re-mount Google Drive:
   from google.colab import drive
   drive.mount('/content/drive', force_remount=True)

2. Check folder permissions in Google Drive web interface

3. Or change results path to local:
   results_dir = "/content/results"  # Local, not Drive
        """,
        
        "NO_TRAINING": """
🔧 SOLUTION: Check training execution

1. Verify Cell 9 ran without errors
2. Check if there are error messages in cell output
3. Look for Python exceptions or stack traces
4. Verify GPU is available (Cell 1 output)
5. Check if experiments were defined (Cell 6)
        """,
        
        "FOLDER_NOT_FOUND": """
🔧 SOLUTION: Create results folder

Run this in a new cell:
    import os
    results_root = "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results/experiments"
    os.makedirs(results_root, exist_ok=True)
    for subdir in ['csv', 'plots', 'md', 'logs', 'checkpoints']:
        os.makedirs(os.path.join(results_root, subdir), exist_ok=True)
    print("✅ Folders created")
        """,
        
        "UNKNOWN": """
🔧 SOLUTION: General troubleshooting

1. Check Cell 9 output for errors
2. Verify DRY_RUN = False
3. Ensure GPU is available
4. Check Colab runtime hasn't timed out
5. Look for Python exceptions in any cell
6. Re-run notebook from Cell 1
        """
    }
    
    print(solutions.get(issue_type, solutions["UNKNOWN"]))

# =============================================================================
# QUICK CHECK TO PASTE IN COLAB
# =============================================================================

def quick_check_in_colab():
    """Quick diagnostic to paste directly in Colab cell"""
    
    print("🔍 QUICK DIAGNOSTIC")
    print("=" * 50)
    
    # Check 1: DRY_RUN
    dry_run = globals().get('DRY_RUN', 'NOT_SET')
    print(f"DRY_RUN: {dry_run}")
    if dry_run == True:
        print("  ❌ PROBLEM: Training is in preview mode only!")
        print("  💡 FIX: Set DRY_RUN = False in Cell 2")
    
    # Check 2: Results path
    results_dir = globals().get('results_dir', 'NOT_SET')
    print(f"\nResults dir: {results_dir}")
    if results_dir != 'NOT_SET' and os.path.exists(results_dir):
        file_count = sum([len(files) for _, _, files in os.walk(results_dir)])
        print(f"  Files in results: {file_count}")
        if file_count == 0:
            print("  ❌ PROBLEM: No results files created!")
    
    # Check 3: Check if training ran
    try:
        experiment_grid = globals().get('experiment_grid', None)
        if experiment_grid:
            print(f"\nExperiment grid: {len(experiment_grid)} experiments")
        else:
            print("\n⚠️  Experiment grid not created yet")
    except:
        pass
    
    print("\n" + "=" * 50)
    print("📋 CHECKLIST:")
    print("  ☐ DRY_RUN = False in Cell 2")
    print("  ☐ All cells 1-9 executed without errors")
    print("  ☐ Cell 9 completed (training finished)")
    print("  ☐ Google Drive has write permissions")

# Run diagnostics
if __name__ == "__main__":
    issue = diagnose_empty_results()
    provide_solution(issue)
    
    print("\n" + "=" * 60)
    print("📝 COPY THIS TO COLAB CELL FOR QUICK CHECK:")
    print("=" * 60)
    print('''
# Quick diagnostic cell - paste this in Colab
dry_run_status = globals().get('DRY_RUN', 'NOT_SET')
print(f"DRY_RUN = {dry_run_status}")
if dry_run_status == True:
    print("❌ PROBLEM: Change DRY_RUN to False in Cell 2!")
else:
    print("✅ DRY_RUN is disabled")

results_dir = globals().get('results_dir', 'NOT_SET') 
if results_dir != 'NOT_SET' and os.path.exists(results_dir):
    import os
    file_count = sum([len(files) for _, _, files in os.walk(results_dir)])
    print(f"Results folder: {file_count} files")
else:
    print("❌ Results folder not found")
''')