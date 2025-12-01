import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from ml.dataset_entries import LARGE_DATASET

DATASET_CSV_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer_tmp.pkl")


# ---------------------------------------------------------
# 7.2 — Vectorizer Upgrade
# ---------------------------------------------------------
def build_vectorizer():
    """
    Return a high-quality vectorizer suitable for security-text classification.
    """
    return TfidfVectorizer(
        lowercase=True,
        sublinear_tf=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 3),
        max_features=20000,
    )


# ---------------------------------------------------------
# Dataset helpers (From 7.1.5)
# ---------------------------------------------------------
def load_dataset():
    texts = []
    labels = []
    for text, label in LARGE_DATASET:
        texts.append(text)
        labels.append(label)
    df = pd.DataFrame({"text": texts, "label": labels})
    return df


def save_dataset_csv(df: pd.DataFrame):
    try:
        df.to_csv(DATASET_CSV_PATH, index=False)
        print(f"[OK] dataset.csv saved to: {DATASET_CSV_PATH}")
    except Exception as e:
        print(f"[ERROR] Could not write dataset.csv: {e}")


# ---------------------------------------------------------
# 7.2 — Fit vectorizer ONLY (no classifiers yet)
# ---------------------------------------------------------
def fit_vectorizer(df: pd.DataFrame):
    """
    Fit the TF-IDF vectorizer on the complete dataset (text-only).
    Saves a temporary vectorizer for next commits.
    """
    print("[INFO] Fitting upgraded TF-IDF vectorizer...")
    vectorizer = build_vectorizer()
    vectorizer.fit(df["text"])

    # Save temporarily — final vectorizer.pkl saved in commit 7.4
    import joblib
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"[OK] Temporary vectorizer saved: {VECTORIZER_PATH}")

    return vectorizer


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    print("[INFO] Loading dataset...")
    df = load_dataset()

    print("[INFO] Dataset size:", len(df))
    print(df["label"].value_counts())

    print("[INFO] Exporting dataset.csv...")
    save_dataset_csv(df)

    print("[INFO] Building TF-IDF vectorizer (Commit 7.2)...")
    vectorizer = fit_vectorizer(df)

    print("[DONE] Commit 7.2 complete.")
    print("      Next: Commit 7.3 — Train SVC/LogReg/NB models.")


if __name__ == "__main__":
    main()
