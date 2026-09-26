# =============================================================================
# PASTE THIS CELL IN COLAB TO DIAGNOSE EMPTY RESULTS
# =============================================================================

import os
from pathlib import Path

print("🔍 V5.1 EMPTY RESULTS DIAGNOSTIC")
print("=" * 60)

# Check 1: DRY_RUN Status
print("\n1️⃣  DRY_RUN STATUS")
print("-" * 60)
dry_run = globals().get('DRY_RUN', 'NOT_DEFINED')
print(f"DRY_RUN = {dry_run}")

if dry_run == True:
    print("❌ PROBLEM FOUND: DRY_RUN = True")
    print("   This means notebook is in PREVIEW MODE only")
    print("   NO ACTUAL TRAINING is happening!")
    print()
    print("💡 SOLUTION:")
    print("   1. Go to Cell 2")
    print("   2. Find: CONFIG = {")
    print("   3. Change: 'DRY_RUN': False,  # ← Change True to False")
    print("   4. Re-run Cell 2")
    print("   5. Then run Cell 9 again")
elif dry_run == False:
    print("✅ DRY_RUN = False (Training should be active)")
else:
    print("⚠️  DRY_RUN not set yet - run Cell 2 first")

# Check 2: Results Directory
print("\n2️⃣  RESULTS DIRECTORY")
print("-" * 60)
results_dir = globals().get('results_dir', None)

if results_dir:
    print(f"Results path: {results_dir}")
    if os.path.exists(results_dir):
        print("✅ Results folder exists")
        
        # Count files recursively
        file_count = 0
        for root, dirs, files in os.walk(results_dir):
            file_count += len(files)
        
        print(f"Total files: {file_count}")
        
        if file_count == 0:
            print("❌ PROBLEM: Folder exists but NO FILES created")
            print()
            print("💡 POSSIBLE CAUSES:")
            print("   • Training hasn't run yet (run Cell 9)")
            print("   • Training is in progress (wait)")
            print("   • Training failed with error (check Cell 9 output)")
            print("   • ResultSaver not working (check for errors)")
        else:
            print("✅ Results files found!")
            
            # Show breakdown by subfolder
            subdirs = ['csv', 'plots', 'md', 'logs', 'checkpoints']
            print("\nBreakdown by type:")
            for subdir in subdirs:
                subdir_path = os.path.join(results_dir, subdir)
                if os.path.exists(subdir_path):
                    count = len([f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))])
                    status = "✅" if count > 0 else "❌"
                    print(f"   {status} {subdir:12s}: {count} files")
    else:
        print(f"❌ Results folder DOES NOT EXIST: {results_dir}")
        print()
        print("💡 SOLUTION: Create folder")
        print(f"   os.makedirs('{results_dir}', exist_ok=True)")
else:
    print("❌ results_dir variable not defined")
    print("   Run Cells 1-3 first to setup paths")

# Check 3: Training State
print("\n3️⃣  TRAINING EXECUTION STATUS")
print("-" * 60)

# Check if experiment grid was created
experiment_grid = globals().get('experiment_grid', None)
if experiment_grid:
    print(f"✅ Experiment grid created: {len(experiment_grid)} experiments")
else:
    print("❌ Experiment grid not found")
    print("   Run Cell 6 to create experiment grid")

# Check if run_all_experiments was called
try:
    # This is a heuristic - check if Cell 9 defined any results
    if 'all_results' in globals():
        print("✅ run_all_experiments() appears to have been called")
    else:
        print("⚠️  run_all_experiments() may not have been called yet")
        print("   Run Cell 9 to start training")
except:
    pass

# Check 4: GPU Status
print("\n4️⃣  GPU AVAILABILITY")
print("-" * 60)

try:
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ GPU available: {gpu_name}")
    else:
        print("⚠️  No GPU - training will be VERY slow on CPU")
except:
    print("⚠️  Cannot check GPU status")

# Check 5: Google Drive Mount (for Colab)
print("\n5️⃣  GOOGLE DRIVE STATUS")
print("-" * 60)

if os.path.exists('/content/drive'):
    print("✅ Google Drive appears to be mounted")
    
    # Check write permissions
    try:
        test_path = '/content/drive/MyDrive/.write_test'
        with open(test_path, 'w') as f:
            f.write('test')
        os.remove(test_path)
        print("✅ Drive has write permissions")
    except Exception as e:
        print(f"❌ Drive write permission DENIED: {e}")
        print()
        print("💡 SOLUTION:")
        print("   from google.colab import drive")
        print("   drive.mount('/content/drive', force_remount=True)")
else:
    print("❌ Google Drive not mounted (not on Colab?)")

# Summary and Action Items
print("\n" + "=" * 60)
print("📋 ACTION ITEMS CHECKLIST")
print("=" * 60)

action_items = []

if dry_run == True:
    action_items.append("☐ CRITICAL: Set DRY_RUN = False in Cell 2")

if not results_dir or not os.path.exists(results_dir):
    action_items.append("☐ Create results directory")

if not experiment_grid:
    action_items.append("☐ Run Cell 6 to create experiment grid")

file_count = 0
if results_dir and os.path.exists(results_dir):
    file_count = sum([len(files) for _, _, files in os.walk(results_dir)])

if file_count == 0 and dry_run == False:
    action_items.append("☐ Run Cell 9 (run_all_experiments) to start training")
    action_items.append("☐ Wait for training to complete (may take hours)")

if action_items:
    for item in action_items:
        print(f"  {item}")
else:
    print("  ✅ No immediate action items")
    print("  💡 If results still empty, check Cell 9 output for errors")

print("\n" + "=" * 60)
print("🎯 MOST COMMON ISSUE: DRY_RUN = True")
print("   → Change to False in Cell 2 and re-run!")
print("=" * 60)