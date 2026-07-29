from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_MODEL_NAME = "all-MiniLM-L6-v2"


def load_model():
    """Loads the sentence embedding model. Cache this in the app layer
    (e.g. with st.cache_resource) so it's only loaded once per session."""
    return SentenceTransformer(_MODEL_NAME)


def semantic_similarity(text_a, text_b, model):
    """Returns similarity as a percentage (0-100) based on meaning,
    not just exact word overlap."""
    embeddings = model.encode([text_a, text_b])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(sim) * 100, 2)
