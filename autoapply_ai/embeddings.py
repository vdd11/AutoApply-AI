from __future__ import annotations
from functools import lru_cache
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception:
        return None

def semantic_similarity(a: str, b: str) -> tuple[float, str]:
    a=a or ''; b=b or ''
    if not a.strip() or not b.strip(): return 0.0, 'empty'
    model=_model()
    if model is not None:
        try:
            emb=model.encode([a,b], normalize_embeddings=True)
            return float(np.dot(emb[0], emb[1])), 'sentence-transformers'
        except Exception:
            pass
    try:
        mat=TfidfVectorizer(stop_words='english', ngram_range=(1,2), max_features=6000).fit_transform([a,b])
        return float(cosine_similarity(mat[0:1], mat[1:2])[0][0]), 'tfidf-fallback'
    except Exception:
        return 0.0, 'fallback-error'
