#!/usr/bin/env python3
"""Create individual HTML files from extracted documents."""

import json
import sys
from pathlib import Path

# Add the filename-sanitizer to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "filename-sanitizer" / "src"))

from filename_sanitizer.sanitizer import sanitize_filename


def create_html_files(json_file: Path, output_dir: Path, limit: int | None = None):
    """Create individual HTML files from extracted JSON."""

    # Load extracted documents
    print(f"Loading documents from {json_file}...")
    with open(json_file) as f:
        documents = json.load(f)

    total = len(documents)
    if limit:
        documents = documents[:limit]
        print(f"Processing {len(documents)} of {total} documents (limit applied)")
    else:
        print(f"Processing {len(documents)} documents")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Track statistics
    created = 0
    skipped = 0

    # Create HTML files
    for i, doc in enumerate(documents, 1):
        title = doc.get("title", f"document_{i}")
        html_content = doc.get("html_content", "")

        # Sanitize filename
        filename = sanitize_filename(f"{title}.html", max_length=200)

        # Handle potential duplicates
        output_path = output_dir / filename
        counter = 1
        while output_path.exists():
            base = filename.replace(".html", "")
            filename = sanitize_filename(f"{base}_{counter}.html", max_length=200)
            output_path = output_dir / filename
            counter += 1

        # Write HTML file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            created += 1

            if created % 100 == 0:
                print(f"  Created {created}/{len(documents)} files...")
        except Exception as e:
            print(f"  Error creating {filename}: {e}")
            skipped += 1

    print("\nComplete!")
    print(f"  Created: {created} HTML files")
    print(f"  Skipped: {skipped} files")
    print(f"  Output directory: {output_dir}")


if __name__ == "__main__":
    json_file = Path(__file__).parent / "extracted_html" / "nq-train-00-documents.json"
    output_dir = Path(__file__).parent / "html_output"

    # For testing, let's start with 1600 documents as mentioned in the project description
    create_html_files(json_file, output_dir, limit=1600)
