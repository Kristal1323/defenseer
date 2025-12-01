import pickle
from pathlib import Path

VEC_PATH = Path("ml/vectorizer.pkl")
MODEL_PATH = Path("ml/model.pkl")


class MLClassifier:
    def __init__(self):
        try:
            with open(VEC_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)

            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)

            self.loaded = True
        except Exception:
            self.loaded = False

    def classify(self, issue_text: str) -> str:
        """
        Returns 'real' or 'false_positive'.
        If classifier not loaded, defaults to 'real'.
        """
        if not self.loaded:
            return "real"

        X = self.vectorizer.transform([issue_text])
        pred = self.model.predict(X)[0]
        return pred


# Singleton instance for easy importing
ml_classifier = MLClassifier()
