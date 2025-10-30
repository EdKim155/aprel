#!/usr/bin/env python3
"""Verify client project structure without importing dependencies."""

import os
from pathlib import Path

def check_file(path: str, min_size: int = 0) -> tuple:
    """Check if file exists and meets size requirement.
    
    Returns:
        (exists: bool, size: int)
    """
    file_path = Path(path)
    exists = file_path.exists()
    size = file_path.stat().st_size if exists else 0
    return (exists and size >= min_size, size)

def main():
    """Verify project structure."""
    print("=" * 60)
    print("CLIENT PROJECT STRUCTURE VERIFICATION")
    print("=" * 60)
    
    files_to_check = [
        # Core modules
        ("auto_booking/__init__.py", 100),
        ("auto_booking/core/__init__.py", 100),
        ("auto_booking/core/client.py", 1000),
        ("auto_booking/core/bot_handler.py", 1000),
        ("auto_booking/core/button_clicker.py", 1000),
        ("auto_booking/core/scheduler.py", 1000),
        
        # Config modules
        ("auto_booking/config/__init__.py", 50),
        ("auto_booking/config/settings.py", 1000),
        ("auto_booking/config/session_manager.py", 1000),
        
        # Utils modules
        ("auto_booking/utils/__init__.py", 50),
        ("auto_booking/utils/logger.py", 500),
        ("auto_booking/utils/metrics.py", 1000),
        ("auto_booking/utils/notifier.py", 1000),
        
        # Main entry point
        ("main.py", 2000),
        
        # Configuration files
        ("config.example.yaml", 100),
        
        # Documentation
        ("CLIENT_README.md", 5000),
        ("CLIENT_ARCHITECTURE.md", 10000),
        ("QUICKSTART_CLIENT.md", 5000),
        ("CLIENT_PROJECT_SUMMARY.md", 5000),
        
        # Scripts
        ("setup_client.sh", 500),
        ("test_client.py", 1000),
        
        # Requirements
        ("requirements-client.txt", 50),
    ]
    
    print("\nChecking files:")
    print("-" * 60)
    
    all_good = True
    total_size = 0
    
    for file_path, min_size in files_to_check:
        exists, size = check_file(file_path, min_size)
        status = "✓" if exists else "✗"
        
        if exists:
            total_size += size
            print(f"{status} {file_path:<45} ({size:>6} bytes)")
        else:
            print(f"{status} {file_path:<45} MISSING or too small")
            all_good = False
    
    print("-" * 60)
    print(f"\nTotal size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    # Check directories
    print("\nChecking directories:")
    print("-" * 60)
    
    dirs_to_check = [
        "auto_booking",
        "auto_booking/core",
        "auto_booking/config",
        "auto_booking/utils",
    ]
    
    for dir_path in dirs_to_check:
        exists = Path(dir_path).is_dir()
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
        if not exists:
            all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED")
        print("=" * 60)
        print("\nProject structure is complete!")
        print("\nNext steps:")
        print("  1. Install dependencies: ./setup_client.sh")
        print("  2. Configure: cp config.example.yaml config.yaml")
        print("  3. Edit config.yaml with your credentials")
        print("  4. Run: python main.py --mode immediate")
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        print("\nSome files or directories are missing.")
    
    print()
    return 0 if all_good else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
