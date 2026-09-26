#!/usr/bin/env python3
"""
Test script untuk membuktikan bahwa bert_utils bisa diimport 
dengan sys.path setup yang benar.
"""

import sys
import os

# Setup path yang benar
project_root = r"d:\laragon\www\ACOS-ASLI"
extract_classify_path = os.path.join(project_root, "Extract-Classify-ACOS")
acos_indobert_path = os.path.join(project_root, "ACOS-IndoBERT")

# Tambahkan ke sys.path
if extract_classify_path not in sys.path:
    sys.path.insert(0, extract_classify_path)
    
if acos_indobert_path not in sys.path:
    sys.path.insert(0, acos_indobert_path)

print(f"Extract-Classify-ACOS path: {extract_classify_path}")
print(f"Path exists: {os.path.exists(extract_classify_path)}")
print(f"bert_utils path: {os.path.join(extract_classify_path, 'bert_utils', 'tokenization.py')}")
print(f"tokenization.py exists: {os.path.exists(os.path.join(extract_classify_path, 'bert_utils', 'tokenization.py'))}")
print(f"sys.path[0]: {sys.path[0]}")

# Test import
try:
    from bert_utils.tokenization import BertTokenizer
    print("✅ SUCCESS: bert_utils.tokenization.BertTokenizer imported successfully!")
    print(f"BertTokenizer class: {BertTokenizer}")
except ImportError as e:
    print(f"❌ FAIL: {e}")
    print("Available modules in sys.path[0]:")
    if os.path.exists(extract_classify_path):
        for item in os.listdir(extract_classify_path):
            print(f"  - {item}")

# Test modeling import
try:
    from modeling import BertForQuadABSA
    print("✅ SUCCESS: modeling.BertForQuadABSA imported successfully!")
except ImportError as e:
    print(f"❌ FAIL modeling: {e}")