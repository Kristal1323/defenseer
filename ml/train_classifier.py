import pandas as pd
import os

# Load dataset entries
from ml.dataset_entries import LARGE_DATASET

DATASET_CSV_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")


def load_dataset():
    """
    Convert the LARGE_DATASET list of (text, label) tuples into a DataFrame.
    """
    texts = []
    labels = []

    for text, label in LARGE_DATASET:
        texts.append(text)
        labels.append(label)

    df = pd.DataFrame({"text": texts, "label": labels})
    return df


def save_dataset_csv(df: pd.DataFrame):
    """
    Saves dataset.csv for transparency and version control.
    """
    try:
        df.to_csv(DATASET_CSV_PATH, index=False)
        print(f"[OK] dataset.csv exported to: {DATASET_CSV_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to write dataset.csv: {e}")


def main():
    print("[INFO] Loading in-memory vulnerability dataset...")
    df = load_dataset()

    print("[INFO] Dataset size:", len(df))
    print("[INFO] Label distribution:")
    print(df["label"].value_counts())

    print("[INFO] Saving dataset.csv...")
    save_dataset_csv(df)

    print("[DONE] Dataset load + CSV export complete.")



if __name__ == "__main__":
    main()
