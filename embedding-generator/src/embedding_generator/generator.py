"""Embedding generator implementation."""

import time

import vertexai
from shared_contracts import TextChunk, Vector768
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel


class EmbeddingGenerator:
    """Generate 768-dimensional embeddings using Vertex AI text-embedding-004."""

    def __init__(
        self,
        project_id: str,
        location: str,
        batch_size: int,
        max_retries: int,
    ) -> None:
        """Initialize the embedding generator."""
        self.project_id = project_id
        self.location = location
        self.batch_size = batch_size
        self.max_retries = max_retries

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Load the embedding model
        self.model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    def generate(self, chunks: list[TextChunk]) -> list[Vector768]:
        """Generate embeddings for text chunks."""
        if not chunks:
            return []

        results: list[Vector768] = []

        # Process chunks in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            batch_embeddings = self._generate_batch(batch)
            results.extend(batch_embeddings)

        return results

    def _generate_batch(self, batch: list[TextChunk]) -> list[Vector768]:
        """Generate embeddings for a single batch with retry logic."""
        texts: list[str | TextEmbeddingInput] = [chunk.content for chunk in batch]

        for attempt in range(self.max_retries):
            try:
                # Call Vertex AI API
                embeddings = self.model.get_embeddings(texts)

                # Convert to Vector768 objects
                return [
                    Vector768(
                        chunk_id=chunk.chunk_id,
                        embedding=emb.values,
                        model="text-embedding-004",
                    )
                    for chunk, emb in zip(batch, embeddings, strict=False)
                ]

            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                # Exponential backoff
                wait_time = 2**attempt
                time.sleep(wait_time)

        # This should never be reached due to raise above, but satisfies type checker
        return []
