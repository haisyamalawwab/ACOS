# =============================================================================
# CELL 0: Complete Setup untuk V5.1 Notebook (Google Drive + Dependencies + Path Fix)
# =============================================================================

# 1. Mount Google Drive jika di Colab
try:
    from google.colab import drive
    drive.mount('/content/drive')
    print("✅ Google Drive berhasil di-mount pada /content/drive")
    
    # Setup ACOS directories di Google Drive
    import os
    gdrive_dirs = [
        "/content/drive/MyDrive/ACOS",
        "/content/drive/MyDrive/ACOS-ASLI", 
        "/content/drive/MyDrive/ACOS_V51_BACKUP",
        "/content/drive/MyDrive/ACOS/ACOS-IndoBERT/results"
    ]
    for dir_path in gdrive_dirs:
        os.makedirs(dir_path, exist_ok=True)
    print("📁 Google Drive directories created")
    
except Exception:
    print("💻 Berjalan pada lingkungan Lokal / Colab tanpa drive mount.")

# 2. Instalasi dependensi yang dibutuhkan
!pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm openpyxl tabulate

# 3. Pre-setup sys.path untuk mencegah bert_utils import issue
import sys
import os
from pathlib import Path

# Function untuk setup path dengan benar
def _setup_acos_paths():
    """Setup sys.path untuk ACOS project dengan urutan yang benar"""
    
    # Kandidat lokasi project
    candidates = [
        "/content",
        "/content/drive/MyDrive/ACOS",
        "/content/drive/MyDrive/ACOS-ASLI", 
        "d:/laragon/www/ACOS-ASLI",
        "D:/laragon/www/ACOS-ASLI"
    ]
    
    def _is_upstream(d):
        """Check if directory contains valid Extract-Classify-ACOS"""
        return (os.path.isfile(os.path.join(d, 'modeling.py')) and 
                os.path.isfile(os.path.join(d, 'bert_utils', 'tokenization.py')))
    
    def _prepend_path(p):
        """Force path to front of sys.path"""
        if not os.path.isdir(p):
            return None
        p_str = str(Path(p).resolve())
        while p_str in sys.path:
            sys.path.remove(p_str)
        sys.path.insert(0, p_str)
        return p_str
    
    # Cari struktur project yang ada
    for base_cand in candidates:
        if not os.path.isdir(base_cand):
            continue
            
        extract_path = os.path.join(base_cand, "Extract-Classify-ACOS")
        indo_path = os.path.join(base_cand, "ACOS-IndoBERT")
        
        if _is_upstream(extract_path):
            # Setup sys.path dengan urutan yang benar
            _prepend_path(extract_path)  # Extract-Classify-ACOS HARUS PERTAMA
            if os.path.isdir(indo_path):
                _prepend_path(indo_path) # ACOS-IndoBERT kedua
            _prepend_path(base_cand)     # Base directory ketiga
            
            print(f"🎯 ACOS paths configured:")
            print(f"  Extract-Classify-ACOS: {extract_path}")
            print(f"  ACOS-IndoBERT: {indo_path}")
            print(f"  sys.path[0]: {sys.path[0]}")
            
            # Verify bert_utils accessibility
            bert_utils_path = os.path.join(extract_path, 'bert_utils', 'tokenization.py')
            if os.path.exists(bert_utils_path):
                print("✅ bert_utils.tokenization.py accessible")
            
            return True
    
    print("⚠️  No existing ACOS project found - will clone in Cell 3")
    return False

# Setup paths jika project sudah ada
_setup_acos_paths()

print("\n🚀 Setup complete! Ready to run V5.1 notebook cells.")
print("📝 Note: Cell 3 import issue should now be resolved.")