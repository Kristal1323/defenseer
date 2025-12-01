import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

from ml.dataset_entries import LARGE_DATASET
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB


DATA_DIR = os.path.dirname(__file__)
DATASET_CSV_PATH = os.path.join(DATA_DIR, "dataset.csv")
VECTORIZER_TMP_PATH = os.path.join(DATA_DIR, "vectorizer_tmp.pkl")


# ---------------------------------------------------------
# Dataset Helpers
# ---------------------------------------------------------
def load_dataset():
    texts, labels = zip(*LARGE_DATASET)
    df = pd.DataFrame({"text": texts, "label": labels})
    return df


def save_dataset_csv(df):
    df.to_csv(DATASET_CSV_PATH, index=False)
    print(f"[OK] dataset.csv saved at: {DATASET_CSV_PATH}")


# ---------------------------------------------------------
# Load vectorizer fitted in Commit 7.2
# ---------------------------------------------------------
def load_vectorizer():
    if not os.path.exists(VECTORIZER_TMP_PATH):
        raise FileNotFoundError("vectorizer_tmp.pkl not found. Run commit 7.2 first.")
    return joblib.load(VECTORIZER_TMP_PATH)


# ---------------------------------------------------------
# Train models
# ---------------------------------------------------------
def train_models(X_train, y_train):
    print("\n[TRAIN] Training LinearSVC...")
    svc = LinearSVC()
    svc.fit(X_train, y_train)

    print("[TRAIN] Training LogisticRegression...")
    logreg = LogisticRegression(max_iter=400)
    logreg.fit(X_train, y_train)

    print("[TRAIN] Training MultinomialNB...")
    nb = MultinomialNB()
    nb.fit(X_train, y_train)

    return svc, logreg, nb


# ---------------------------------------------------------
# Evaluate model
# ---------------------------------------------------------
def evaluate_model(model, X_val, y_val, name):
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
# MAIN EXECUTION
# ---------------------------------------------------------
def main():
    print("[INFO] Loading dataset...")
    df = load_dataset()
    save_dataset_csv(df)

    print("[INFO] Loading vectorizer (Commit 7.2)...")
    vectorizer = load_vectorizer()

    print("[INFO] Vectorizing dataset...")
    X = vectorizer.transform(df["text"])
    y = df["label"]

    print("[INFO] Splitting into train/validation...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[INFO] Training base models...")
    svc, logreg, nb = train_models(X_train, y_train)

    print("\n[INFO] Evaluating models...")
    acc_svc = evaluate_model(svc, X_val, y_val, "LinearSVC")
    acc_log = evaluate_model(logreg, X_val, y_val, "LogisticRegression")
    acc_nb = evaluate_model(nb, X_val, y_val, "MultinomialNB")

    print("\n[SUMMARY] Model Accuracy Comparison")
    print(f"  LinearSVC:         {acc_svc:.4f}")
    print(f"  LogisticRegression:{acc_log:.4f}")
    print(f"  MultinomialNB:     {acc_nb:.4f}")

    print("\n[DONE] Commit 7.3 complete.")
    print("      Next: Commit 7.4 — Build ensemble + save model/vectorizer.")


if __name__ == "__main__":
    main()
