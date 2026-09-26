# =============================================================================
# CELL 0: UNIVERSAL DYNAMIC ENVIRONMENT SETUP
# Automatically detects: Colab / Kaggle / JupyterLab / VPS / Local
# =============================================================================

import os
import sys
import platform
from pathlib import Path

# =============================================================================
# DYNAMIC ENVIRONMENT DETECTOR
# =============================================================================

def detect_and_setup_environment():
    """Detect environment and setup accordingly"""
    
    env_config = {
        'platform': 'unknown',
        'is_cloud': False,
        'has_gpu': False,
        'base_path': str(Path.cwd()),
        'supports_drive': False,
        'project_paths': [],
        'setup_strategy': 'local'
    }
    
    print("🔍 DETECTING ENVIRONMENT...")
    print("=" * 50)
    
    # =================================================================
    # 1. GOOGLE COLAB
    # =================================================================
    try:
        import google.colab
        env_config.update({
            'platform': 'colab',
            'is_cloud': True,
            'base_path': '/content',
            'supports_drive': True,
            'setup_strategy': 'clone',
            'project_paths': [
                '/content/drive/MyDrive/ACOS',
                '/content/drive/MyDrive/ACOS-ASLI', 
                '/content'
            ]
        })
        
        print("🔗 GOOGLE COLAB detected")
        
        # Mount Google Drive
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            print("✅ Google Drive mounted: /content/drive")
            
            # Create backup directories
            backup_dirs = [
                '/content/drive/MyDrive/ACOS',
                '/content/drive/MyDrive/ACOS_V51_BACKUP'
            ]
            for backup_dir in backup_dirs:
                os.makedirs(backup_dir, exist_ok=True)
            print("📁 Backup directories ready")
            
        except Exception as e:
            print(f"⚠️  Drive mount failed: {e}")
        
        return env_config
        
    except ImportError:
        pass
    
    # =================================================================
    # 2. KAGGLE
    # =================================================================
    if os.path.exists('/kaggle'):
        env_config.update({
            'platform': 'kaggle', 
            'is_cloud': True,
            'base_path': '/kaggle/working',
            'setup_strategy': 'clone',
            'project_paths': ['/kaggle/working', '/kaggle/input']
        })
        
        print("🏆 KAGGLE detected")
        return env_config
    
    # =================================================================
    # 3. JUPYTER/JUPYTERLAB 
    # =================================================================
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            env_config.update({
                'platform': 'jupyter',
                'is_cloud': False,
                'setup_strategy': 'local_or_clone'
            })
            print("📓 JUPYTER detected")
    except:
        pass
    
    # =================================================================
    # 4. VPS/CLOUD SERVERS
    # =================================================================
    hostname = platform.node().lower()
    
    if any(cloud in hostname for cloud in ['aws', 'ec2', 'gcp', 'google', 'azure', 'droplet']):
        cloud_type = 'aws' if 'aws' in hostname or 'ec2' in hostname else \
                     'gcp' if 'gcp' in hostname or 'google' in hostname else \
                     'azure' if 'azure' in hostname else 'vps'
        
        env_config.update({
            'platform': cloud_type,
            'is_cloud': True,
            'setup_strategy': 'clone',
            'project_paths': [f'/home/ubuntu/ACOS-ASLI', f'/root/ACOS-ASLI', str(Path.cwd())]
        })
        
        print(f"☁️  {cloud_type.upper()} VPS detected")
        return env_config
    
    # =================================================================
    # 5. LOCAL DEVELOPMENT
    # =================================================================
    env_config.update({
        'platform': 'local',
        'is_cloud': False,
        'setup_strategy': 'local_path',
        'project_paths': [
            'd:/laragon/www/ACOS-ASLI',
            'D:/laragon/www/ACOS-ASLI',
            '/home/user/ACOS-ASLI',
            str(Path.home() / 'ACOS-ASLI'),
            str(Path.cwd())
        ]
    })
    
    print("💻 LOCAL environment detected")
    return env_config

# =============================================================================
# GPU & SYSTEM INFO DETECTION
# =============================================================================

def detect_gpu_info(env_config):
    """Detect GPU and system information"""
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            env_config.update({
                'has_gpu': True,
                'gpu_name': gpu_name,
                'gpu_memory': f'{gpu_memory:.1f}GB'
            })
            
            print(f"🎮 GPU: {gpu_name} ({gpu_memory:.1f}GB VRAM)")
        else:
            print("💻 CPU-only execution")
    except:
        print("❓ GPU detection unavailable")
    
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / 1024**3
        env_config['ram'] = f'{ram_gb:.1f}GB'
        print(f"💾 RAM: {ram_gb:.1f}GB")
    except:
        pass
    
    return env_config

# =============================================================================
# DYNAMIC DEPENDENCY INSTALLATION
# =============================================================================

def install_dependencies(env_config):
    """Install dependencies based on environment"""
    
    print("\\n📦 Installing dependencies...")
    
    deps = [
        'pytorch-crf', 'transformers', 'huggingface_hub', 
        'seaborn', 'scikit-learn', 'matplotlib', 'pandas', 
        'boto3', 'tqdm', 'openpyxl', 'tabulate'
    ]
    
    if env_config['platform'] in ['colab', 'kaggle']:
        # Cloud platforms
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-q'] + deps, 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("⚠️  Some dependencies may have failed to install")
    
    elif env_config['platform'] == 'jupyter':
        # Jupyter notebook
        try:
            get_ipython().system(f'pip install -q {" ".join(deps)}')
            print("✅ Dependencies installed via Jupyter")
        except:
            print("💡 Please run: pip install " + " ".join(deps))
    
    else:
        # Local/VPS
        print("💡 To install dependencies, run:")
        print(f"pip install {' '.join(deps)}")

# =============================================================================
# MAIN SETUP EXECUTION
# =============================================================================

print("🚀 UNIVERSAL ENVIRONMENT SETUP")
print("=" * 60)

# Detect environment
env_config = detect_and_setup_environment()

# Detect GPU/System info
env_config = detect_gpu_info(env_config)

# Install dependencies
install_dependencies(env_config)

# Print summary
print("\\n" + "=" * 60)
print("📋 ENVIRONMENT SUMMARY")
print("=" * 60)
print(f"Platform      : {env_config['platform'].upper()}")
print(f"Cloud         : {'Yes' if env_config['is_cloud'] else 'No'}")
print(f"Base Path     : {env_config['base_path']}")
print(f"Setup Strategy: {env_config['setup_strategy']}")
if env_config.get('has_gpu'):
    print(f"GPU           : {env_config.get('gpu_name', 'Unknown')}")
if env_config.get('ram'):
    print(f"RAM           : {env_config['ram']}")
print(f"Project Paths : {len(env_config['project_paths'])} candidates")

# Store config for next cells
globals()['ENV_CONFIG'] = env_config

print("\\n🎯 Environment setup complete!")
print("💡 ENV_CONFIG variable available for Cell 3 path setup")

# =============================================================================
# EXAMPLE USAGE IN CELL 3
# =============================================================================

print("\\n" + "=" * 60)
print("📝 USAGE IN CELL 3:")
print("=" * 60)
print("""
# In Cell 3, use ENV_CONFIG for path setup:

env = globals().get('ENV_CONFIG', {})

if env.get('platform') == 'colab':
    # Use Colab-specific paths
    project_candidates = env.get('project_paths', ['/content'])
    
elif env.get('platform') == 'kaggle':
    # Use Kaggle-specific paths  
    project_candidates = ['/kaggle/working']
    
elif env.get('setup_strategy') == 'local_path':
    # Use local paths
    project_candidates = env.get('project_paths', [])
    
else:
    # VPS/Cloud - clone strategy
    project_candidates = env.get('project_paths', [str(Path.cwd())])

# Then proceed with ACOS project setup...
""")