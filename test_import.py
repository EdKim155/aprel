#!/usr/bin/env python3
"""
Simple script to test if all modules can be imported correctly.
This helps verify that there are no syntax errors or import issues.
"""

import sys

def test_imports():
    print("Testing imports...")
    
    try:
        print("  - Importing config...")
        import config
        print("    ✓ config imported successfully")
    except Exception as e:
        print(f"    ✗ Error importing config: {e}")
        return False
    
    try:
        print("  - Importing database...")
        import database
        print("    ✓ database imported successfully")
    except Exception as e:
        print(f"    ✗ Error importing database: {e}")
        return False
    
    try:
        print("  - Importing keyboards...")
        import keyboards
        print("    ✓ keyboards imported successfully")
    except Exception as e:
        print(f"    ✗ Error importing keyboards: {e}")
        return False
    
    try:
        print("  - Importing utils...")
        import utils
        print("    ✓ utils imported successfully")
    except Exception as e:
        print(f"    ✗ Error importing utils: {e}")
        return False
    
    print("\n✓ All modules imported successfully!")
    return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
