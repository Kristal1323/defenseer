import os
import joblib
from ml.train_classifier import EnsembleClassifier  # ensure class available for unpickling
import sys


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "vectorizer.pkl")


class ClassifierSingleton:
    _model = None
    _vectorizer = None

    @classmethod
    def load(cls):
        # The model was pickled when EnsembleClassifier lived in __main__ during training,
        # so expose the class under __main__ to satisfy unpickling.
        sys.modules["__main__"].EnsembleClassifier = EnsembleClassifier

        if cls._model is None or cls._vectorizer is None:
            print("[INFO] Loading ML model + vectorizer...")
            cls._model = joblib.load(MODEL_PATH)
            cls._vectorizer = joblib.load(VECTORIZER_PATH)
        return cls._model, cls._vectorizer


def predict_label(text: str) -> str:
    model, vect = ClassifierSingleton.load()
    X = vect.transform([text])
    return model.predict(X)[0]


def predict_with_confidence(text: str):
    """
    Returns (label, confidence%)
    """
    model, vect = ClassifierSingleton.load()
    X = vect.transform([text])

    label = model.predict(X)[0]
    conf = float(model.confidence(X)[0])  # ensemble confidence %

    return label, conf
