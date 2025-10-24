"""
Script untuk mengecek dependency yang diperlukan.
Jalankan script ini untuk memastikan semua package sudah terinstall.
"""

import sys

def check_dependencies():
    """Check all required dependencies and report missing ones."""
    missing_packages = []
    installed_packages = []
    
    dependencies = {
        'selenium': 'selenium>=4.15.0',
        'bs4': 'beautifulsoup4>=4.12.0',
        'lxml': 'lxml>=4.9.0',
        'pandas': 'pandas>=2.0.0',
        'numpy': 'numpy>=1.24.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'docx': 'python-docx>=1.0.0',
        'requests': 'requests>=2.31.0',
        'dotenv': 'python-dotenv>=1.0.0'
    }
    
    print("=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
            installed_packages.append(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - MISSING")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Installed: {len(installed_packages)}/{len(dependencies)}")
    print(f"Missing: {len(missing_packages)}/{len(dependencies)}")
    
    if missing_packages:
        print("\n" + "=" * 60)
        print("INSTALLATION COMMAND")
        print("=" * 60)
        print("Jalankan command berikut untuk install package yang hilang:\n")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nATAU install semua dari requirements.txt:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✅ Semua dependency sudah terinstall!")
        print("GUI siap dijalankan dengan: python src/gui/app.py")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
