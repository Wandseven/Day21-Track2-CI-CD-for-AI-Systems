import pandas as pd
import yaml
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import joblib
import os
import json

def train():
    # Load params
    with open("params.yaml", "r") as f:
        params_full = yaml.safe_load(f)
        params = params_full["train"]

    model_type = params.get("model_type", "random_forest")
    n_estimators = params["n_estimators"]
    max_depth = params["max_depth"]
    min_samples_split = params["min_samples_split"]

    # Load data
    train_df = pd.read_csv("data/train_phase1.csv")
    eval_df = pd.read_csv("data/eval.csv")

    X_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    X_eval = eval_df.drop("quality", axis=1)
    y_eval = eval_df["quality"]

    # Start MLflow run
    mlflow.set_experiment("Wine Quality MLOps")
    
    with mlflow.start_run(run_name=f"{model_type}_depth_{max_depth}"):
        # Chon thu thuat toan (Bonus 2)
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                random_state=42
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        model.fit(X_train, y_train)

        # Evaluation
        y_pred = model.predict(X_eval)
        acc = accuracy_score(y_eval, y_pred)
        f1 = f1_score(y_eval, y_pred, average="weighted")
        
        # Confusion Matrix (Bonus 3)
        cm = confusion_matrix(y_eval, y_pred)
        print("\n--- CONFUSION MATRIX ---")
        print(cm)
        print("------------------------\n")

        # Logging
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        print(f"Model: {model_type}, Accuracy: {acc:.4f}, F1: {f1:.4f}")

        # Save artifacts locally for pipeline usage
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

        os.makedirs("outputs", exist_ok=True)
        with open("outputs/metrics.json", "w") as f:
            json.dump({"accuracy": acc, "f1_score": f1}, f)

if __name__ == "__main__":
    train()
