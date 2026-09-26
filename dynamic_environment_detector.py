# =============================================================================
# DYNAMIC ENVIRONMENT DETECTOR - Universal Platform Detection
# =============================================================================
# Deteksi otomatis: Colab / Kaggle / JupyterLab / VPS / Local

import os
import sys
import platform
from pathlib import Path

def detect_environment():
    """
    Detect current execution environment dynamically
    Returns: dict with environment info and optimal configurations
    """
    
    env_info = {
        'platform': 'unknown',
        'is_cloud': False,
        'has_gpu': False,
        'base_path': str(Path.cwd()),
        'temp_path': '/tmp',
        'supports_drive_mount': False,
        'supports_datasets': False,
        'memory_limit': 'unknown',
        'gpu_type': 'unknown',
        'project_candidates': [],
        'clone_strategy': 'local'
    }
    
    # =================================================================
    # 1. GOOGLE COLAB DETECTION
    # =================================================================
    try:
        import google.colab
        env_info.update({
            'platform': 'colab',
            'is_cloud': True,
            'base_path': '/content',
            'temp_path': '/tmp',
            'supports_drive_mount': True,
            'clone_strategy': 'git_clone',
            'project_candidates': [
                '/content/drive/MyDrive/ACOS',
                '/content/drive/MyDrive/ACOS-ASLI',
                '/content'
            ]
        })
        
        # Try to get GPU info in Colab
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                env_info['has_gpu'] = True
                env_info['gpu_type'] = gpu_name
                
                # Determine memory based on GPU
                if 'T4' in gpu_name:
                    env_info['memory_limit'] = '12-16GB RAM'
                elif 'L4' in gpu_name:
                    env_info['memory_limit'] = '22-24GB RAM'
                elif 'V100' in gpu_name:
                    env_info['memory_limit'] = '25-27GB RAM'
                elif 'A100' in gpu_name:
                    env_info['memory_limit'] = '40-80GB RAM'
        except:
            pass
            
        return env_info
    except ImportError:
        pass
    
    # =================================================================
    # 2. KAGGLE DETECTION  
    # =================================================================
    if os.path.exists('/kaggle'):
        env_info.update({
            'platform': 'kaggle',
            'is_cloud': True,
            'base_path': '/kaggle/working',
            'temp_path': '/tmp',
            'supports_datasets': True,
            'clone_strategy': 'git_clone',
            'project_candidates': [
                '/kaggle/input',
                '/kaggle/working'
            ]
        })
        
        # Kaggle GPU detection
        if os.path.exists('/opt/bin/nvidia-smi'):
            env_info['has_gpu'] = True
            env_info['gpu_type'] = 'Kaggle GPU (T4/P100)'
            env_info['memory_limit'] = '13-16GB RAM'
            
        return env_info
    
    # =================================================================
    # 3. JUPYTER/JUPYTERLAB DETECTION
    # =================================================================
    if 'jupyter' in sys.modules or 'IPython' in sys.modules:
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            
            if ipython is not None:
                env_info.update({
                    'platform': 'jupyter',
                    'is_cloud': False,
                    'clone_strategy': 'local_or_clone'
                })
                
                # Detect if it's JupyterLab vs Classic Notebook
                if hasattr(ipython, 'kernel'):
                    env_info['platform'] = 'jupyterlab'
        except:
            pass
    
    # =================================================================
    # 4. VPS/CLOUD SERVER DETECTION
    # =================================================================
    hostname = platform.node().lower()
    
    # AWS Detection
    if any(x in hostname for x in ['aws', 'ec2', 'compute']):
        env_info.update({
            'platform': 'aws',
            'is_cloud': True,
            'clone_strategy': 'git_clone'
        })
    
    # Google Cloud Detection  
    elif any(x in hostname for x in ['gcp', 'google', 'gce']):
        env_info.update({
            'platform': 'gcp',
            'is_cloud': True,
            'clone_strategy': 'git_clone'
        })
    
    # Azure Detection
    elif any(x in hostname for x in ['azure', 'microsoft']):
        env_info.update({
            'platform': 'azure',
            'is_cloud': True,
            'clone_strategy': 'git_clone'
        })
    
    # Digital Ocean / Linode / VPS
    elif any(x in hostname for x in ['droplet', 'linode', 'vultr']):
        env_info.update({
            'platform': 'vps',
            'is_cloud': True,
            'clone_strategy': 'git_clone'
        })
    
    # =================================================================
    # 5. LOCAL DEVELOPMENT DETECTION
    # =================================================================
    else:
        env_info.update({
            'platform': 'local',
            'is_cloud': False,
            'clone_strategy': 'local_path'
        })
    
    # =================================================================
    # 6. COMMON DETECTION FOR ALL PLATFORMS
    # =================================================================
    
    # GPU Detection (universal)
    try:
        import torch
        if torch.cuda.is_available():
            env_info['has_gpu'] = True
            if env_info['gpu_type'] == 'unknown':
                env_info['gpu_type'] = torch.cuda.get_device_name(0)
    except:
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                env_info['has_gpu'] = True
                env_info['gpu_type'] = 'NVIDIA GPU (detected via nvidia-smi)'
        except:
            pass
    
    # Memory Detection
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        env_info['memory_limit'] = f'{memory_gb:.1f}GB RAM'
    except:
        pass
    
    # Set project candidates based on platform
    if env_info['platform'] == 'local':
        env_info['project_candidates'] = [
            "d:/laragon/www/ACOS-ASLI",
            "D:/laragon/www/ACOS-ASLI", 
            "/home/user/ACOS-ASLI",
            str(Path.home() / "ACOS-ASLI"),
            str(Path.cwd())
        ]
    elif not env_info['project_candidates']:  # VPS/Cloud without specific paths
        env_info['project_candidates'] = [
            "/home/ubuntu/ACOS-ASLI",
            "/root/ACOS-ASLI",
            str(Path.home() / "ACOS-ASLI"),
            str(Path.cwd())
        ]
    
    return env_info

# =============================================================================
# DYNAMIC SETUP BASED ON ENVIRONMENT
# =============================================================================

def setup_environment_dynamically():
    """Setup paths, mounts, and configurations based on detected environment"""
    
    env = detect_environment()
    
    print("🔍 ENVIRONMENT DETECTION")
    print("=" * 50)
    print(f"Platform        : {env['platform'].upper()}")
    print(f"Cloud Platform  : {'Yes' if env['is_cloud'] else 'No'}")
    print(f"GPU Available   : {'Yes' if env['has_gpu'] else 'No'}")
    if env['has_gpu']:
        print(f"GPU Type        : {env['gpu_type']}")
    print(f"Memory          : {env['memory_limit']}")
    print(f"Base Path       : {env['base_path']}")
    print("=" * 50)
    
    # =================================================================
    # PLATFORM-SPECIFIC SETUP
    # =================================================================
    
    if env['platform'] == 'colab':
        # Google Colab Setup
        print("🔗 Setting up Google Colab...")
        
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            print("✅ Google Drive mounted successfully")
            
            # Create ACOS directories in Drive
            gdrive_dirs = [
                '/content/drive/MyDrive/ACOS',
                '/content/drive/MyDrive/ACOS-ASLI',
                '/content/drive/MyDrive/ACOS_V51_BACKUP'
            ]
            for dir_path in gdrive_dirs:
                os.makedirs(dir_path, exist_ok=True)
            print("📁 Google Drive directories ready")
            
        except Exception as e:
            print(f"⚠️  Drive mount failed: {e}")
    
    elif env['platform'] == 'kaggle':
        # Kaggle Setup
        print("🏆 Setting up Kaggle environment...")
        
        # Kaggle datasets are usually in /kaggle/input
        # Working directory is /kaggle/working
        print("📁 Kaggle workspace ready")
    
    elif env['platform'] in ['aws', 'gcp', 'azure', 'vps']:
        # Cloud VPS Setup
        print(f"☁️  Setting up {env['platform'].upper()} environment...")
        
        # Ensure we have git for cloning
        try:
            import subprocess
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print("✅ Git available for repository cloning")
        except:
            print("⚠️  Git not found - may need to install")
    
    else:
        # Local/Jupyter Setup
        print("💻 Setting up local development environment...")
    
    # =================================================================
    # INSTALL DEPENDENCIES (PLATFORM-AWARE)
    # =================================================================
    
    print("\n📦 Installing dependencies...")
    
    if env['platform'] in ['colab', 'kaggle']:
        # Cloud platforms - use pip install
        os.system('pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm openpyxl tabulate')
    else:
        # Local/VPS - check if running in notebook
        try:
            get_ipython()  # This will fail if not in IPython/Jupyter
            # In notebook - can use !pip
            os.system('pip install -q pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm openpyxl tabulate')
        except NameError:
            # In regular Python script
            print("💡 Run this to install dependencies:")
            print("pip install pytorch-crf transformers huggingface_hub seaborn scikit-learn matplotlib pandas boto3 tqdm openpyxl tabulate")
    
    print("✅ Dependencies installed")
    
    # =================================================================
    # RETURN ENVIRONMENT CONFIG
    # =================================================================
    
    return env

# Test the detector
if __name__ == "__main__":
    env = setup_environment_dynamically()
    print(f"\n🎯 Environment setup complete for {env['platform'].upper()}!")
    print(f"📋 Project candidates: {env['project_candidates']}")