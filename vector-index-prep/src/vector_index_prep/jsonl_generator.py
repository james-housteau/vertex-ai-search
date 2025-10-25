"""JSONL generator for Vertex AI Vector Search index preparation."""

import json
from typing import Any

from google.cloud import storage
from shared_contracts import TextChunk, Vector768


def generate_jsonl(
    chunks: list[TextChunk], embeddings: list[Vector768], output_path: str
) -> None:
    """Generate JSONL file from chunks and embeddings.

    Args:
        chunks: List of TextChunk objects.
        embeddings: List of Vector768 objects.
        output_path: Output path (GCS or local file).

    Raises:
        ValueError: If validation fails.
    """
    # Validate inputs
    if not chunks or not embeddings:
        raise ValueError("Chunks and embeddings cannot be empty")

    # Create embedding lookup by chunk_id
    embedding_map = {emb.chunk_id: emb for emb in embeddings}

    # Generate JSONL lines
    jsonl_lines = []
    for chunk in chunks:
        if chunk.chunk_id not in embedding_map:
            raise ValueError(f"No embedding found for chunk: {chunk.chunk_id}")

        embedding = embedding_map[chunk.chunk_id]

        # Build JSONL object
        jsonl_obj = {
            "id": chunk.chunk_id,
            "embedding": embedding.embedding,
            "restricts": _metadata_to_restricts(chunk.metadata),
        }

        jsonl_lines.append(json.dumps(jsonl_obj))

    # Write to output
    content = "\n".join(jsonl_lines) + "\n"

    if output_path.startswith("gs://"):
        _write_to_gcs(content, output_path)
    else:
        _write_to_local(content, output_path)


def _metadata_to_restricts(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert metadata dict to Vertex AI restricts format.

    Args:
        metadata: Metadata dictionary from TextChunk.

    Returns:
        List of restrict objects with namespace and allow fields.
    """
    restricts = []
    for key, value in metadata.items():
        # Convert value to list if it's not already
        allow_list = [value] if not isinstance(value, list) else value
        # Convert all values to strings
        allow_list = [str(v) for v in allow_list]
        restricts.append({"namespace": key, "allow": allow_list})
    return restricts


def _write_to_gcs(content: str, gcs_path: str) -> None:
    """Write content to GCS bucket.

    Args:
        content: JSONL content to write.
        gcs_path: GCS path in format gs://bucket/path/to/file.jsonl
    """
    # Parse GCS path
    path_parts = gcs_path.replace("gs://", "").split("/", 1)
    bucket_name = path_parts[0]
    blob_path = path_parts[1] if len(path_parts) > 1 else "output.jsonl"

    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content)


def _write_to_local(content: str, file_path: str) -> None:
    """Write content to local file.

    Args:
        content: JSONL content to write.
        file_path: Local file path.
    """
    with open(file_path, "w") as f:
        f.write(content)
