import pandas as pd
import yaml
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import joblib
import os
import json

def train(params_dict=None, data_path=None, eval_path=None):
    """
    Huan luyen mo hinh. Co the nhan tham so truc tiep (cho Unit Test)
    hoac tu dong doc tu params.yaml (cho Pipeline).
    """
    # 1. Load params
    if params_dict is None:
        with open("params.yaml", "r") as f:
            params_full = yaml.safe_load(f)
            params = params_full["train"]
    else:
        params = params_dict

    model_type = params.get("model_type", "random_forest")
    n_estimators = params.get("n_estimators", 100)
    max_depth = params.get("max_depth", None)
    min_samples_split = params.get("min_samples_split", 2)

    # 2. Load data
    train_p = data_path if data_path else "data/train_phase1.csv"
    eval_p = eval_path if eval_path else "data/eval.csv"
    
    train_df = pd.read_csv(train_p)
    eval_df = pd.read_csv(eval_p)

    # Dung "quality" lam ten cot mac dinh (khop voi du lieu that)
    # Neu unit test truyen vao dataset co cot "target", chung ta linh hoat doi ten
    for df in [train_df, eval_df]:
        if "target" in df.columns and "quality" not in df.columns:
            df.rename(columns={"target": "quality"}, inplace=True)

    X_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    X_eval = eval_df.drop("quality", axis=1)
    y_eval = eval_df["quality"]

    # 3. Start MLflow run
    mlflow.set_experiment("Wine Quality MLOps")
    
    # Tracking URI, Username, Password se duoc lay tu bien moi truong (DagsHub)
    
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

        # 4. Evaluation
        y_pred = model.predict(X_eval)
        acc = accuracy_score(y_eval, y_pred)
        f1 = f1_score(y_eval, y_pred, average="weighted")
        
        # Confusion Matrix (Bonus 3)
        cm = confusion_matrix(y_eval, y_pred)
        print("\n--- CONFUSION MATRIX ---")
        print(cm)
        print("------------------------\n")

        # Precision/Recall Report (Bonus 3 extension)
        report_text = classification_report(y_eval, y_pred)
        print("--- CLASSIFICATION REPORT ---")
        print(report_text)
        
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/report.txt", "w") as f:
            f.write(f"Model Type: {model_type}\n")
            f.write(f"Accuracy: {acc:.4f}\n")
            f.write(f"F1 Score: {f1:.4f}\n\n")
            f.write("Confusion Matrix:\n")
            f.write(str(cm))
            f.write("\n\nClassification Report:\n")
            f.write(report_text)

        # 5. Logging
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        # 6. Save artifacts
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

        with open("outputs/metrics.json", "w") as f:
            json.dump({"accuracy": acc, "f1_score": f1}, f)

        print(f"Done! Accuracy: {acc:.4f}")
        return acc

if __name__ == "__main__":
    train()
