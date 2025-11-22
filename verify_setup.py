"""
Setup Verification Script
Run this to verify all components are properly installed
"""

import sys
import os

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}")
        return True
    else:
        print(f"[MISSING] {description}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'upstox_client',
        'pandas',
        'numpy',
        'sklearn',
        'flask',
        'ta',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} installed")
        except ImportError:
            print(f"[MISSING] {package}")
            missing.append(package)
    
    return len(missing) == 0

def main():
    print("=" * 60)
    print("AI TRADING BOT - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_good = True
    
    # Check core files
    print("Checking Core Files:")
    print("-" * 60)
    files_to_check = [
        ('main.py', 'Main application'),
        ('config.py', 'Configuration'),
        ('upstox_handler.py', 'Upstox API client'),
        ('trading_engine.py', 'Trading engine'),
        ('signal_generator.py', 'Signal generator'),
        ('risk_manager.py', 'Risk manager'),
        ('indicators.py', 'Technical indicators'),
        ('order_flow.py', 'Order flow analysis'),
        ('database.py', 'Database manager'),
        ('logger.py', 'Logger'),
        ('dashboard.py', 'Dashboard backend'),
        ('requirements.txt', 'Dependencies list'),
        ('.env.example', 'Environment template'),
        ('README.md', 'Documentation')
    ]
    
    for filename, description in files_to_check:
        filepath = os.path.join(base_dir, filename)
        if not check_file(filepath, description):
            all_good = False
    
    print()
    
    # Check directories
    print("Checking Directories:")
    print("-" * 60)
    dirs_to_check = [
        ('templates', 'Dashboard templates'),
        ('static', 'Dashboard static files')
    ]
    
    for dirname, description in dirs_to_check:
        dirpath = os.path.join(base_dir, dirname)
        if not check_file(dirpath, description):
            all_good = False
    
    print()
    
    # Check dashboard files
    print("Checking Dashboard Files:")
    print("-" * 60)
    dashboard_files = [
        ('templates/index.html', 'Dashboard HTML'),
        ('static/style.css', 'Dashboard CSS'),
        ('static/script.js', 'Dashboard JavaScript')
    ]
    
    for filename, description in dashboard_files:
        filepath = os.path.join(base_dir, filename)
        if not check_file(filepath, description):
            all_good = False
    
    print()
    
    # Check dependencies
    print("Checking Python Dependencies:")
    print("-" * 60)
    deps_ok = check_dependencies()
    if not deps_ok:
        all_good = False
        print()
        print("[WARNING] Some dependencies are missing. Install them with:")
        print("  pip install -r requirements.txt")
    
    print()
    
    # Check environment file
    print("Checking Configuration:")
    print("-" * 60)
    env_file = os.path.join(base_dir, '.env')
    if os.path.exists(env_file):
        print("[OK] .env file exists")
        print("  Make sure to add your Upstox API credentials")
    else:
        print("[WARNING] .env file not found")
        print("  Copy .env.example to .env and add your credentials:")
        print("  copy .env.example .env")
        all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("[SUCCESS] ALL CHECKS PASSED!")
        print()
        print("Next steps:")
        print("1. Add your Upstox API credentials to .env file")
        print("2. Run: python main.py")
        print("3. Complete authentication when prompted")
        print("4. Access dashboard at http://localhost:5000")
    else:
        print("[FAILED] SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running the bot")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
