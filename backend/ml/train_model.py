
import joblib
import pandas as pd
from pathlib import Path

from sklearn.linear_model import LinearRegression

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from preprocessing import (
    load_dataset,
    create_supervised_data,
    split_time_series_data
)


def evaluate_model(name, actual, predicted):

    print(f"\n{name}")

    for column in actual.columns:

        mae = mean_absolute_error(
            actual[column],
            predicted[column]
        )

        rmse = mean_squared_error(
            actual[column],
            predicted[column]
        ) ** 0.5

        r2 = r2_score(
            actual[column],
            predicted[column]
        )

        print(f"\n{column}")
        print(f"MAE:  {mae:.6f}")
        print(f"RMSE: {rmse:.6f}")
        print(f"R2:   {r2:.6f}")


data = load_dataset()

model_directory = Path(__file__).resolve().parent / "saved_model"
model_directory.mkdir(parents=True, exist_ok=True)


for horizon in [1, 2, 3]:

    print("\n" + "=" * 50)
    print(f"FORECAST HORIZON: {horizon * 5} MINUTES")
    print("=" * 50)

    X, y = create_supervised_data(data, horizon=horizon)

    X_train, X_test, y_train, y_test = (
        split_time_series_data(X, y)
    )

    # Persistence baseline
    baseline_predictions = {
        "next_avg_cpu": X_test["avg_cpu_lag_0"].values,
        "next_avg_mem": X_test["avg_mem_lag_0"].values
    }

    print("\nPERSISTENCE BASELINE")

    for target in y.columns:
        predictions = baseline_predictions[target]

        print(
            f"{target} MAE: "
            f"{mean_absolute_error(y_test[target], predictions):.6f}"
        )

    # Train Linear Regression
    linear_model = LinearRegression()

    linear_model.fit(X_train, y_train)

    linear_predictions = pd.DataFrame(
        linear_model.predict(X_test),
        columns=y.columns,
        index=y_test.index
    )

    evaluate_model(
        "LINEAR REGRESSION",
        y_test,
        linear_predictions
    )

    # Save selected model
    joblib.dump(
        linear_model,
        model_directory / f"linear_regression_{horizon * 5}min.joblib"
    )

    print(f"\nLinear Regression saved for {horizon * 5}-minute forecast.")