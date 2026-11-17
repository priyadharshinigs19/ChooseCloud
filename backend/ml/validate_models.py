
import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import TimeSeriesSplit

from preprocessing import (
    load_dataset,
    create_supervised_data
)


def calculate_metrics(actual, predicted):

    results = {}

    for column in actual.columns:

        results[column] = {
            "MAE": mean_absolute_error(
                actual[column], predicted[column]
            ),
            "RMSE": mean_squared_error(
                actual[column], predicted[column]
            ) ** 0.5,
            "R2": r2_score(
                actual[column], predicted[column]
            )
        }

    return results


def create_models():

    return {
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=2
        ),
        "Linear Regression": LinearRegression()
    }


data = load_dataset()

# Test all three forecasting horizons
for horizon in [1, 2, 3]:

    print("\n" + "=" * 55)
    print(f"3-FOLD VALIDATION: {horizon * 5}-MINUTE FORECAST")
    print("=" * 55)

    X, y = create_supervised_data(data, horizon=horizon)

    # Expanding-window chronological validation.
    # Gap prevents training targets from overlapping
    # the beginning of the validation period.
    tscv = TimeSeriesSplit(
        n_splits=3,
        gap=horizon
    )

    model_results = {
        "Baseline": [],
        "Random Forest": [],
        "Linear Regression": [],
        "Gradient Boosting": []
    }

    for fold, (train_index, test_index) in enumerate(
        tscv.split(X), start=1
    ):

        print(f"\n--- FOLD {fold} ---")

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        # Persistence baseline
        baseline_predictions = pd.DataFrame({
            "next_avg_cpu": X_test["avg_cpu_lag_0"].values,
            "next_avg_mem": X_test["avg_mem_lag_0"].values
        }, index=y_test.index)

        model_results["Baseline"].append(
            calculate_metrics(y_test, baseline_predictions)
        )

        # Random Forest and Linear Regression
        for name, model in create_models().items():

            model.fit(X_train, y_train)

            predictions = pd.DataFrame(
                model.predict(X_test),
                columns=y.columns,
                index=y_test.index
            )

            model_results[name].append(
                calculate_metrics(y_test, predictions)
            )

        # Separate Gradient Boosting models
        gradient_predictions = {}

        for target in y.columns:

            model = HistGradientBoostingRegressor(
                max_iter=150,
                learning_rate=0.05,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=42
            )

            model.fit(X_train, y_train[target])

            gradient_predictions[target] = model.predict(X_test)

        gradient_predictions = pd.DataFrame(
            gradient_predictions,
            index=y_test.index
        )

        model_results["Gradient Boosting"].append(
            calculate_metrics(y_test, gradient_predictions)
        )
        print(f"\nFOLD {fold} RESULTS")

        for model_name, fold_results in model_results.items():
            print(f"\n{model_name}")

            for target, metrics in fold_results[-1].items():
                print(
                    f"{target}: "
                    f"MAE={metrics['MAE']:.6f}, "
                    f"RMSE={metrics['RMSE']:.6f}, "
                    f"R2={metrics['R2']:.6f}"
                )

        print(
            f"Training records: {len(X_train)} | "
            f"Testing records: {len(X_test)}"
        )

    # Average results across all three folds
    print("\nAVERAGE VALIDATION RESULTS")

    for model_name, fold_results in model_results.items():

        print(f"\n{model_name}")

        for target in y.columns:

            print(f"\n{target}")

            for metric in ["MAE", "RMSE", "R2"]:

                average = sum(
                    result[target][metric]
                    for result in fold_results
                ) / len(fold_results)

                print(f"{metric}: {average:.6f}")
