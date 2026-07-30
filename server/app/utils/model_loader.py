# app/utils/model_loader.py

from sentence_transformers import SentenceTransformer

_model = None

print("model_loader imported")

def get_model():
    global _model
    print("get_model called")

    if _model is None:
        print("Loading SentenceTransformer...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model