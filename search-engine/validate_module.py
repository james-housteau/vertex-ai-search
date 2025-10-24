#!/usr/bin/env python3
"""Module validation script for search-engine."""

import sys
from pathlib import Path


def count_files(directory: Path) -> int:
    """Count total files in directory recursively."""
    count = 0
    for item in directory.rglob("*"):
        if item.is_file() and not item.name.startswith(".git"):
            count += 1
    return count


def check_pure_module_isolation():
    """Check Pure Module Isolation compliance."""
    print("🔍 Checking Pure Module Isolation compliance...")

    # Check file count
    module_dir = Path(__file__).parent
    file_count = count_files(module_dir)
    print(f"   Total files: {file_count}")

    if file_count < 60:
        print("   ✅ File count < 60 (Pure Module Isolation)")
    else:
        print("   ❌ File count >= 60 (violates Pure Module Isolation)")
        return False

    # Check for ../imports
    print("   Checking for ../imports...")
    python_files = list(module_dir.rglob("*.py"))
    has_parent_imports = False

    for file_path in python_files:
        try:
            content = file_path.read_text()
            if "../" in content and ("import" in content or "from" in content):
                print(f"   ❌ Found ../import in {file_path}")
                has_parent_imports = True
        except Exception as e:
            print(f"   ⚠️ Could not read {file_path}: {e}")

    if not has_parent_imports:
        print("   ✅ No ../imports found")

    return not has_parent_imports


def check_api_contract():
    """Check API contract implementation."""
    print("🔍 Checking API contract implementation...")

    try:
        # Import and verify SearchResult
        from src.search_engine.models import SearchResult

        print("   ✅ SearchResult dataclass imported")

        # Check SearchResult fields
        required_fields = [
            "query",
            "results",
            "result_count",
            "execution_time_ms",
            "relevance_scores",
            "success",
            "error_message",
        ]

        import dataclasses

        fields = [f.name for f in dataclasses.fields(SearchResult)]

        for field in required_fields:
            if field in fields:
                print(f"   ✅ SearchResult.{field} field present")
            else:
                print(f"   ❌ SearchResult.{field} field missing")
                return False

        # Import and verify SearchEngine
        from src.search_engine.search_engine import SearchEngine

        print("   ✅ SearchEngine class imported")

        # Check SearchEngine methods
        required_methods = ["__init__", "search", "batch_search", "validate_connection"]

        for method in required_methods:
            if hasattr(SearchEngine, method):
                print(f"   ✅ SearchEngine.{method} method present")
            else:
                print(f"   ❌ SearchEngine.{method} method missing")
                return False

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


def check_dependencies():
    """Check that required dependencies are specified."""
    print("🔍 Checking dependencies...")

    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if not pyproject_path.exists():
        print("   ❌ pyproject.toml not found")
        return False

    content = pyproject_path.read_text()
    required_deps = [
        "google-cloud-discoveryengine",
        "pydantic",
        "click",
        "python-dotenv",
    ]

    for dep in required_deps:
        if dep in content:
            print(f"   ✅ {dep} dependency found")
        else:
            print(f"   ❌ {dep} dependency missing")
            return False

    return True


def main():
    """Run all validation checks."""
    print("🚀 Validating search-engine module...")
    print("=" * 50)

    checks = [
        ("Pure Module Isolation", check_pure_module_isolation),
        ("API Contract", check_api_contract),
        ("Dependencies", check_dependencies),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        result = check_func()
        results.append((check_name, result))

    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")

    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("   Module is ready for integration.")
        return 0
    else:
        print("\n💥 Some validation checks failed!")
        print("   Please fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    # Add src to Python path for imports
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    exit_code = main()
    sys.exit(exit_code)
