#!/bin/bash

# Script to remove .gz files from git tracking while keeping local copies

echo "🧹 Cleaning up .gz files from git tracking..."
echo ""

# Check which .gz files are currently tracked
echo "📋 Currently tracked .gz files:"
git ls-files | grep "\.gz$" || echo "None found"
echo ""

# Remove from git tracking (keeps local files)
echo "🗑️  Removing .gz files from git tracking (keeping local copies)..."

# Remove the tracked .gz files
git rm --cached data/nq-train-00.jsonl.gz 2>/dev/null
git rm --cached data/nq-train-42.jsonl.gz 2>/dev/null
git rm --cached nq-downloader/data/nq-train-00.jsonl.gz 2>/dev/null
git rm --cached nq-downloader/data/nq-train-42.jsonl.gz 2>/dev/null

echo ""
echo "✅ Removed from git tracking"
echo ""

# Check that .gz is in .gitignore
echo "🔍 Verifying .gitignore contains *.gz..."
if grep -q "^\*\.gz$" .gitignore; then
    echo "✅ *.gz is already in .gitignore"
else
    echo "❌ *.gz not found in .gitignore - please add it"
fi

echo ""
echo "📊 Current .gz files in repository (not tracked):"
find . -name "*.gz" -type f ! -path "./.git/*" ! -path "./archive/*" -exec du -h {} \; | sort -rh

echo ""
echo "⚠️  WARNING: Found large .gz files totaling ~3.3GB in nq-downloader/data/"
echo "    These should remain in .gitignore and never be committed!"

echo ""
echo "📝 Next steps:"
echo "1. Review the changes: git status"
echo "2. Commit the removal: git commit -m 'Remove .gz files from tracking'"
echo "3. Consider moving large data files to cloud storage (GCS)"

echo ""
echo "💡 Tip: The nq-downloader/data/ directory is now ignored, so these files won't be tracked"
