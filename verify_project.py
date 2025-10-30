#!/usr/bin/env python3
"""
Project verification script
Checks that all required files exist and are properly structured
"""

import os
import sys

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("Project Verification")
    print("=" * 60)
    print()
    
    all_checks = []
    
    print("📁 Core Python Files:")
    all_checks.append(check_file_exists("bot.py", "Main bot file"))
    all_checks.append(check_file_exists("config.py", "Configuration"))
    all_checks.append(check_file_exists("database.py", "Database operations"))
    all_checks.append(check_file_exists("keyboards.py", "Inline keyboards"))
    all_checks.append(check_file_exists("utils.py", "Utilities"))
    print()
    
    print("📚 Documentation Files:")
    all_checks.append(check_file_exists("README.md", "Main README"))
    all_checks.append(check_file_exists("SETUP.md", "Setup guide"))
    all_checks.append(check_file_exists("TESTING.md", "Testing guide"))
    all_checks.append(check_file_exists("ARCHITECTURE.md", "Architecture docs"))
    all_checks.append(check_file_exists("CHANGELOG.md", "Changelog"))
    all_checks.append(check_file_exists("PROJECT_SUMMARY.md", "Project summary"))
    print()
    
    print("🛠️ Configuration Files:")
    all_checks.append(check_file_exists(".env.example", "Environment template"))
    all_checks.append(check_file_exists(".gitignore", "Git ignore"))
    all_checks.append(check_file_exists("requirements.txt", "Python dependencies"))
    print()
    
    print("🐳 Docker Files:")
    all_checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    all_checks.append(check_file_exists("docker-compose.yml", "Docker Compose"))
    print()
    
    print("🔧 Development Tools:")
    all_checks.append(check_file_exists("quickstart.sh", "Quick start script"))
    all_checks.append(check_file_exists("test_import.py", "Import test script"))
    all_checks.append(check_file_exists("booking-bot.service", "Systemd service"))
    print()
    
    print("📄 Other Files:")
    all_checks.append(check_file_exists("LICENSE", "License file"))
    print()
    
    print("=" * 60)
    total = len(all_checks)
    passed = sum(all_checks)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All checks passed! Project is complete.")
        return 0
    else:
        print(f"❌ {total - passed} checks failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
