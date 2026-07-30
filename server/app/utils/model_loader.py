print("model_loader imported")

_model = None


def get_model():
    global _model

    if _model is None:
        print("Loading SentenceTransformer...")

        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model
