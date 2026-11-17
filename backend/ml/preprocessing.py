
import pandas as pd
from pathlib import Path


# Locate the original dataset
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "instance_usage_grouped_300_seconds_month.csv"


def load_dataset():
    """Load and validate the original workload dataset."""

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "avg_cpu",
        "avg_mem",
        "avg_assigned_mem",
        "avg_cycles_per_instruction"
    ]

    # Check required columns
    if not all(column in df.columns for column in required_columns):
        raise ValueError("Dataset is missing required columns.")

    # Check missing and invalid values
    df = df[required_columns].copy()
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna()

    if df.empty:
        raise ValueError("No valid records found.")

    return df

def create_supervised_data(df, horizon=1):
    """
    Create lag features to predict future workload.

    horizon=1: 5 minutes ahead
    horizon=2: 10 minutes ahead
    horizon=3: 15 minutes ahead
    """

    feature_columns = [
        "avg_cpu",
        "avg_mem",
        "avg_assigned_mem",
        "avg_cycles_per_instruction"
    ]

    X = pd.DataFrame(index=df.index)

    # Historical workload features
    for column in feature_columns:
        for lag in [0, 1, 2, 3, 6, 12]:
            X[f"{column}_lag_{lag}"] = df[column].shift(lag)

    # Future workload targets
    y = pd.DataFrame({
        "next_avg_cpu": df["avg_cpu"].shift(-horizon),
        "next_avg_mem": df["avg_mem"].shift(-horizon)
    })

    combined = pd.concat([X, y], axis=1).dropna()

    X = combined[X.columns]
    y = combined[y.columns]

    return X, y

def split_time_series_data(X, y):
    """Split observations chronologically into training and testing sets."""

    split_index = int(len(X) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    data = load_dataset()

    X, y = create_supervised_data(data)

    X_train, X_test, y_train, y_test = split_time_series_data(X, y)

    print("Total records:", len(X))
    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    print("\nTraining period:")
    print(X_train.index[0], "to", X_train.index[-1])

    print("\nTesting period:")
    print(X_test.index[0], "to", X_test.index[-1])