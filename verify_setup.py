#!/usr/bin/env python3
"""Quick verification script for Lakehead University Chatbot setup.

Run this script to verify all components are in place before starting.
"""

import os
import sys
from pathlib import Path


def print_status(message: str, status: bool):
    """Print status message with emoji."""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")


def check_file(filepath: Path, description: str) -> bool:
    """Check if a file exists."""
    exists = filepath.exists()
    print_status(f"{description}: {filepath.name}", exists)
    return exists


def check_directory(dirpath: Path, description: str) -> bool:
    """Check if a directory exists and has files."""
    exists = dirpath.exists()
    if exists:
        file_count = len(list(dirpath.iterdir())) if dirpath.is_dir() else 0
        print_status(f"{description}: {dirpath.name} ({file_count} files)", exists)
    else:
        print_status(f"{description}: {dirpath.name}", False)
    return exists


def main():
    """Run verification checks."""
    print("=" * 70)
    print("Lakehead University Chatbot - Setup Verification")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent
    all_checks_passed = True

    # Check backend files
    print("📦 Backend Files:")
    backend_files = [
        (project_root / "backend" / "app" / "__init__.py", "App factory"),
        (project_root / "backend" / "app" / "api_routes.py", "API routes"),
        (project_root / "backend" / "app" / "config.py", "Configuration"),
        (project_root / "backend" / "app" / "services" / "dialogflow_service.py", "Dialogflow service"),
        (project_root / "backend" / "run.py", "Development server"),
        (project_root / "backend" / "wsgi.py", "WSGI config"),
        (project_root / "backend" / "requirements.txt", "Dependencies"),
    ]

    for filepath, description in backend_files:
        if not check_file(filepath, description):
            all_checks_passed = False

    # Check for Dialogflow key
    print()
    dialogflow_key = project_root / "backend" / "dialogflow_key.json"
    if not check_file(dialogflow_key, "Dialogflow credentials"):
        all_checks_passed = False
        print("   ⚠️  You need to add dialogflow_key.json to the backend/ directory")

    # Check frontend files
    print()
    print("🌐 Frontend Files:")
    frontend_files = [
        (project_root / "frontend" / "index.html", "Chat interface"),
        (project_root / "frontend" / "serve.py", "Dev server"),
        (project_root / "frontend" / "README.md", "Frontend docs"),
    ]

    for filepath, description in frontend_files:
        if not check_file(filepath, description):
            all_checks_passed = False

    # Check Dialogflow intents
    print()
    print("🤖 Dialogflow Data:")
    dialogflow_dirs = [
        (project_root / "data" / "dialogflow_ready" / "intents", "Intent files"),
        (project_root / "data" / "dialogflow_ready" / "entities", "Entity files"),
    ]

    for dirpath, description in dialogflow_dirs:
        if not check_directory(dirpath, description):
            all_checks_passed = False

    # Check documentation
    print()
    print("📚 Documentation:")
    doc_files = [
        (project_root / "README.md", "Main README"),
        (project_root / "QUICK_START.md", "Quick start guide"),
        (project_root / "DIALOGFLOW_SETUP.md", "Dialogflow setup"),
        (project_root / "TESTING_CHECKLIST.md", "Testing checklist"),
        (project_root / "PROJECT_SUMMARY.md", "Project summary"),
        (project_root / "PROTOTYPE_READY.md", "Ready status"),
    ]

    for filepath, description in doc_files:
        if not check_file(filepath, description):
            all_checks_passed = False

    # Check Python installation
    print()
    print("🐍 Python Environment:")
    python_version = sys.version.split()[0]
    version_parts = [int(x) for x in python_version.split('.')]
    python_ok = version_parts[0] == 3 and version_parts[1] >= 8

    print_status(f"Python version: {python_version} (3.8+ required)", python_ok)
    if not python_ok:
        all_checks_passed = False

    # Final summary
    print()
    print("=" * 70)
    if all_checks_passed:
        print("✅ All checks passed! Your setup is ready.")
        print()
        print("Next steps:")
        print("1. Upload intents to Dialogflow (see DIALOGFLOW_SETUP.md)")
        print("2. Start backend: cd backend && python run.py")
        print("3. Start frontend: cd frontend && python3 serve.py")
        print("4. Open browser: http://localhost:8080")
        print()
        print("For detailed instructions, see QUICK_START.md")
    else:
        print("❌ Some checks failed. Please review the issues above.")
        print()
        print("Common fixes:")
        print("- Ensure you've cloned the entire repository")
        print("- Add dialogflow_key.json to backend/ directory")
        print("- Run generate_dialogflow_intents.py if intents are missing")
        print()
        print("For help, see QUICK_START.md troubleshooting section")

    print("=" * 70)

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())

