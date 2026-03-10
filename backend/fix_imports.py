# fix_imports.py
import subprocess
import sys

def fix_dependencies():
    """Fix the requests dependency warning"""
    print("Fixing dependency issues...")
    
    # Uninstall problematic packages
    packages = ['requests', 'urllib3', 'chardet', 'charset-normalizer']
    for package in packages:
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', package, '-y'])
    
    # Reinstall with compatible versions
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'urllib3==1.26.15'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'chardet==5.1.0'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'charset-normalizer==3.1.0'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests==2.31.0'])
    
    print("Dependencies fixed! Try running your app again.")

if __name__ == "__main__":
    fix_dependencies()