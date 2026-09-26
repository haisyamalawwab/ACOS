# Google Drive Setup for Colab
# Tambahkan ini sebagai cell pertama di notebook Colab V5.1

"""
# Cell 0: Google Drive Mount & Setup
from google.colab import drive
import os

# Mount Google Drive
drive.mount('/content/drive')

# Verify mount
if os.path.exists('/content/drive/MyDrive'):
    print("✅ Google Drive mounted successfully")
    print(f"Available space: {os.statvfs('/content/drive').f_bavail * os.statvfs('/content/drive').f_frsize / 1024**3:.1f} GB")
else:
    print("❌ Google Drive mount failed")

# Setup ACOS directories in Google Drive
gdrive_acos_dir = "/content/drive/MyDrive/ACOS"
gdrive_acos_asli_dir = "/content/drive/MyDrive/ACOS-ASLI" 
gdrive_backup_dir = "/content/drive/MyDrive/ACOS_V51_BACKUP"

for dir_path in [gdrive_acos_dir, gdrive_acos_asli_dir, gdrive_backup_dir]:
    os.makedirs(dir_path, exist_ok=True)
    print(f"📁 Created: {dir_path}")

print("🎯 Google Drive initialization complete!")
"""