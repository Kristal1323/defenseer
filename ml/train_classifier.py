import os
import joblib
import pandas as pd

from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

from ml.dataset_entries import LARGE_DATASET

DATA_DIR = os.path.dirname(__file__)
DATASET_CSV_PATH = os.path.join(DATA_DIR, "dataset.csv")
VECTORIZER_TMP_PATH = os.path.join(DATA_DIR, "vectorizer_tmp.pkl")
FINAL_VECTORIZER_PATH = os.path.join(DATA_DIR, "vectorizer.pkl")
FINAL_MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")


# ---------------------------------------------------------
# Dataset helper
# ---------------------------------------------------------
def load_dataset():
    texts, labels = zip(*LARGE_DATASET)
    df = pd.DataFrame({"text": texts, "label": labels})
    return df


# ---------------------------------------------------------
# Vectorizer
# ---------------------------------------------------------
def build_vectorizer():
    return TfidfVectorizer(
        lowercase=True,
        sublinear_tf=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 3),
        max_features=20000,
    )


def ensure_vectorizer(df):
    if os.path.exists(VECTORIZER_TMP_PATH):
        print("[INFO] Loading existing temporary vectorizer...")
        return joblib.load(VECTORIZER_TMP_PATH)

    print("[INFO] Building new TF-IDF vectorizer...")
    vectorizer = build_vectorizer()
    vectorizer.fit(df["text"])
    joblib.dump(vectorizer, VECTORIZER_TMP_PATH)
    print(f"[OK] Saved vectorizer_tmp.pkl to: {VECTORIZER_TMP_PATH}")
    return vectorizer


# ---------------------------------------------------------
# Base models (from Commit 7.3)
# ---------------------------------------------------------
def train_base_models(X_train, y_train):
    print("\n[TRAIN] LinearSVC...")
    svc = LinearSVC()
    svc.fit(X_train, y_train)

    print("[TRAIN] LogisticRegression...")
    logreg = LogisticRegression(max_iter=400)
    logreg.fit(X_train, y_train)

    print("[TRAIN] MultinomialNB...")
    nb = MultinomialNB()
    nb.fit(X_train, y_train)

    return svc, logreg, nb


def evaluate(model, X_val, y_val, name):
    preds = model.predict(X_val)
    acc = accuracy_score(y_val, preds)
    prec = precision_score(y_val, preds, pos_label="real")
    rec = recall_score(y_val, preds, pos_label="real")

    print(f"\n[RESULT] {name}")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")

    return acc


# ---------------------------------------------------------
# Ensemble Class
# ---------------------------------------------------------
class EnsembleClassifier:
    def __init__(self, svc, logreg, nb):
        self.svc = svc
        self.logreg = logreg
        self.nb = nb
        self.weights = {
            "svc": 3,
            "logreg": 2,
            "nb": 1
        }

    def predict(self, X):
        svc_pred = (self.svc.predict(X) == "real").astype(int)
        logreg_pred = (self.logreg.predict(X) == "real").astype(int)
        nb_pred = (self.nb.predict(X) == "real").astype(int)

        combined = (
            svc_pred * self.weights["svc"] +
            logreg_pred * self.weights["logreg"] +
            nb_pred * self.weights["nb"]
        )

        # threshold: > half of total weight (3+2+1)=6 → >3 means real
        labels = ["real" if c > 3 else "false_positive" for c in combined]

        return labels

    def confidence(self, X):
        svc_pred = (self.svc.predict(X) == "real").astype(int)
        logreg_pred = (self.logreg.predict(X) == "real").astype(int)
        nb_pred = (self.nb.predict(X) == "real").astype(int)

        combined = (
            svc_pred * self.weights["svc"] +
            logreg_pred * self.weights["logreg"] +
            nb_pred * self.weights["nb"]
        )

        return (combined / sum(self.weights.values())) * 100


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    print("[INFO] Loading dataset...")
    df = load_dataset()

    print("[INFO] Saving dataset.csv...")
    df.to_csv(DATASET_CSV_PATH, index=False)

    print("[INFO] Ensuring vectorizer...")
    vectorizer = ensure_vectorizer(df)

    print("[INFO] Vectorizing dataset...")
    X = vectorizer.transform(df["text"])
    y = df["label"]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[INFO] Training base models...")
    svc, logreg, nb = train_base_models(X_train, y_train)

    print("\n[INFO] Evaluating base models...")
    evaluate(svc, X_val, y_val, "LinearSVC")
    evaluate(logreg, X_val, y_val, "LogisticRegression")
    evaluate(nb, X_val, y_val, "MultinomialNB")

    print("\n[INFO] Building ensemble classifier...")
    ensemble = EnsembleClassifier(svc, logreg, nb)

    print("[INFO] Saving final vectorizer + ensemble model...")
    joblib.dump(vectorizer, FINAL_VECTORIZER_PATH)
    joblib.dump(ensemble, FINAL_MODEL_PATH)

    print(f"[OK] Final vectorizer saved: {FINAL_VECTORIZER_PATH}")
    print(f"[OK] Final model saved: {FINAL_MODEL_PATH}")

    print("\n[DONE] Ensemble saved successfully.")


if __name__ == "__main__":
    main()
