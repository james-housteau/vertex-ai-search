"""Natural Questions JSONL.gz dataset processing functionality."""

import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class Stats:
    """Statistics for extracted documents."""

    total_entries: int
    unique_documents: int
    duplicates_removed: int


@dataclass
class ExtractResult:
    """Result of Natural Questions dataset processing."""

    success: bool
    documents: List[Dict] = field(default_factory=list)
    stats: Optional[Stats] = None
    error_message: str = ""


class NaturalQuestionsExtractor:
    """Extract HTML documents from Natural Questions JSONL.gz files."""

    def extract_html_documents(self, jsonl_gz_path: Path) -> ExtractResult:
        """Parse JSONL.gz and extract unique HTML documents by title."""
        try:
            documents = []
            total_entries = 0

            with gzip.open(jsonl_gz_path, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        total_entries += 1
                        entry = json.loads(line)

                        if "document_html" in entry and "document_title" in entry:
                            documents.append(
                                {
                                    "title": entry["document_title"],
                                    "html_content": entry["document_html"],
                                    "url": entry.get("document_url", ""),
                                    "question_id": entry.get("example_id", ""),
                                }
                            )

            unique_docs = self.deduplicate_by_title(documents)
            stats = self.generate_statistics(documents, unique_docs, total_entries)

            return ExtractResult(success=True, documents=unique_docs, stats=stats)

        except Exception as e:
            return ExtractResult(
                success=False, error_message=f"Failed to process JSONL.gz file: {e}"
            )

    def deduplicate_by_title(self, documents: List[Dict]) -> List[Dict]:
        """Remove duplicates based on document title."""
        seen_titles: Set[str] = set()
        unique_documents = []

        for doc in documents:
            title = doc.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_documents.append(doc)

        return unique_documents

    def generate_statistics(
        self, all_docs: List[Dict], unique_docs: List[Dict], total_entries: int
    ) -> Stats:
        """Generate extraction statistics report."""
        return Stats(
            total_entries=total_entries,
            unique_documents=len(unique_docs),
            duplicates_removed=len(all_docs) - len(unique_docs),
        )
