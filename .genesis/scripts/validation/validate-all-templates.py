#!/usr/bin/env python3
"""Validate all Jinja2 templates in the project."""

import sys
from pathlib import Path

from jinja2 import Template, TemplateSyntaxError


def validate_template(file_path: Path) -> tuple[bool, str]:
    """Validate a single template file.

    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path) as f:
            content = f.read()

        # Try to compile the template
        Template(content)
        return (True, "")
    except TemplateSyntaxError as e:
        return (False, f"Line {e.lineno}: {e.message}")
    except Exception as e:
        return (False, str(e))


def find_all_templates(root_dir: Path) -> list[Path]:
    """Find all .template files recursively."""
    templates = []
    for path in root_dir.rglob("*.template"):
        templates.append(path)
    return sorted(templates)


def main():
    """Main validation function."""
    root_dir = Path(__file__).parent.parent.parent.parent / "templates"

    print(f"🔍 Scanning for templates in: {root_dir}")
    templates = find_all_templates(root_dir)

    print(f"📋 Found {len(templates)} template files\n")

    errors = []
    warnings = []

    for template_path in templates:
        relative_path = template_path.relative_to(root_dir)
        success, error_msg = validate_template(template_path)

        if success:
            print(f"✅ {relative_path}")
        else:
            print(f"❌ {relative_path}: {error_msg}")
            errors.append((relative_path, error_msg))

    # Check for common issues
    for template_path in templates:
        with open(template_path) as f:
            content = f.read()

        relative_path = template_path.relative_to(root_dir)

        # Check for bash array syntax that might cause issues
        if "${#" in content and "{% raw %}" not in content:
            warnings.append(
                (
                    relative_path,
                    "Contains ${# which might be interpreted as Jinja2 comment",
                )
            )

        # Check for undefined variables (common ones)
        common_vars = ["{{project_name}}", "{{module_name}}", "{{command_name}}"]
        for var in common_vars:
            if var in content:
                # This is expected, just noting for summary
                pass

    # Print summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total templates: {len(templates)}")
    print(f"Valid templates: {len(templates) - len(errors)}")
    print(f"Invalid templates: {len(errors)}")

    if warnings:
        print(f"⚠️  Warnings: {len(warnings)}")
        for path, warning in warnings:
            print(f"   - {path}: {warning}")

    if errors:
        print("\n❌ ERRORS FOUND:")
        for path, error in errors:
            print(f"   - {path}: {error}")
        sys.exit(1)
    else:
        print("\n✅ All templates are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
