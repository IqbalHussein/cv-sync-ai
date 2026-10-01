import os

from sentence_transformers import SentenceTransformer, util
import torch

DEFAULT_MODEL = os.environ.get("SEMANTIC_MODEL", "all-MiniLM-L6-v2")

CHUNK_WORDS = 150

_matchers: dict[str, "SemanticMatcher"] = {}


def get_semantic_matcher(model_name: str = DEFAULT_MODEL) -> "SemanticMatcher":
    """
    Return a cached SemanticMatcher for the given model.

    Loading a SentenceTransformer is expensive, so each model is loaded once
    per process and reused across calls.
    """
    if model_name not in _matchers:
        _matchers[model_name] = SemanticMatcher(model_name)
    return _matchers[model_name]


def _chunk_text(text: str, chunk_words: int = CHUNK_WORDS) -> list[str]:
    """
    Split text into consecutive windows of at most chunk_words words.

    all-MiniLM-L6-v2 truncates input at 256 word-piece tokens; the default of
    150 words stays under that, so long postings are embedded in full rather
    than cut off after the header.

    Args:
        text: Input string.
        chunk_words: Maximum number of words per chunk.

    Returns:
        List of chunk strings; empty if the text has no words.
    """
    words = text.split()
    return [" ".join(words[i:i + chunk_words]) for i in range(0, len(words), chunk_words)]


class SemanticMatcher:
    """
    A helper class to perform semantic similarity comparisons using Sentence Transformers.

    This class loads a pre-trained model to generate embeddings for text inputs
    and calculates cosine similarity between them. It is designed to capture
    contextual meaning beyond exact keyword matching.
    """
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize the SemanticMatcher with a specific transformer model.

        Prefer get_semantic_matcher() so the model is only loaded once.

        Args:
            model_name: The HuggingFace model identifier to load.
                       Defaults to 'all-MiniLM-L6-v2' which offers a good
                       balance of speed and accuracy.
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> torch.Tensor:
        """
        Generate embedding for a given text.

        Args:
            text: Input string.

        Returns:
            A pytorch tensor representing the text embedding.
        """
        return self.encode_many([text])[0]

    def encode_many(self, texts: list[str], batch_size: int = 32) -> list[torch.Tensor]:
        """
        Generate embeddings for several texts in a single batched model call.

        Each text is split into chunks that fit the model's input limit; the
        chunk embeddings are mean-pooled so the whole text contributes.
        Empty texts get a zero vector.

        Args:
            texts: Input strings.
            batch_size: Number of chunks encoded per forward pass.

        Returns:
            One embedding tensor per input text, in the same order.
        """
        chunks: list[str] = []
        spans: list[tuple[int, int]] = []
        for text in texts:
            text_chunks = _chunk_text(text)
            spans.append((len(chunks), len(chunks) + len(text_chunks)))
            chunks.extend(text_chunks)

        dim = self.model.get_sentence_embedding_dimension()
        if not chunks:
            return [torch.zeros(dim) for _ in texts]

        chunk_embs = self.model.encode(chunks, batch_size=batch_size, convert_to_tensor=True)

        out = []
        for start, end in spans:
            if start == end:
                out.append(torch.zeros(dim, device=chunk_embs.device))
            else:
                out.append(chunk_embs[start:end].mean(dim=0))
        return out

    def compute_similarity_score(self, embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
        """
        Compute cosine similarity between two pre-computed embeddings.

        Args:
            embedding1: First tensor.
            embedding2: Second tensor.

        Returns:
            Float similarity score [-1.0, 1.0].
        """
        cosine_scores = util.cos_sim(embedding1, embedding2)
        return float(cosine_scores[0][0])

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute the cosine similarity score between two text strings.

        Generates embeddings for both input texts and calculates the cosine
        similarity between their vectors.

        Args:
            text1: The first text string (e.g., resume content).
            text2: The second text string (e.g., job description).

        Returns:
            A float value between -1.0 and 1.0 representing the semantic similarity,
            where 1.0 indicates identical semantic meaning.
        """
        embeddings1, embeddings2 = self.encode_many([text1, text2])
        return self.compute_similarity_score(embeddings1, embeddings2)
