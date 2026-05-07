import pandas as pd
import yaml
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import joblib
import os
import json
import boto3
from botocore.exceptions import ClientError

def train(params_dict=None, data_path=None, eval_path=None):
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

    for df in [train_df, eval_df]:
        if "target" in df.columns and "quality" not in df.columns:
            df.rename(columns={"target": "quality"}, inplace=True)

    X_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    X_eval = eval_df.drop("quality", axis=1)
    y_eval = eval_df["quality"]

    # --- BONUS 5: Data Drift Warning ---
    print("\n--- DATA DISTRIBUTION CHECK ---")
    counts = y_train.value_counts(normalize=True)
    dist_dict = counts.to_dict()
    drift_warning = False
    for label, ratio in dist_dict.items():
        print(f"Class {label}: {ratio:.2%}")
        if ratio < 0.10:
            print(f"⚠️ WARNING: Class {label} is under-represented (< 10%)!")
            drift_warning = True
    if not drift_warning:
        print("✅ Data distribution is balanced.")
    print("--------------------------------\n")

    # 3. Start MLflow run
    mlflow.set_experiment("Wine Quality MLOps")
    
    with mlflow.start_run(run_name=f"{model_type}_depth_{max_depth}"):
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
        
        report_text = classification_report(y_eval, y_pred)
        print("\n--- CLASSIFICATION REPORT ---")
        print(report_text)
        
        # --- BONUS 4: Rollback Check ---
        old_acc = 0.0
        s3_bucket = os.getenv("S3_BUCKET")
        if s3_bucket:
            s3 = boto3.client("s3")
            try:
                s3.download_file(s3_bucket, "metrics/latest.json", "old_metrics.json")
                with open("old_metrics.json", "r") as f:
                    old_acc = json.load(f).get("accuracy", 0.0)
                print(f"Previous Accuracy: {old_acc:.4f}")
            except ClientError:
                print("No previous metrics found on S3. Skipping comparison.")

        print(f"Current Accuracy: {acc:.4f}")
        
        degraded = False
        if acc < old_acc:
            print("❌ ACCURACY DEGRADED! New model is worse than the current one.")
            degraded = True
        else:
            print("✅ Accuracy improved or stable. Model is safe to deploy.")

        # Save artifacts
        os.makedirs("outputs", exist_ok=True)
        metrics_data = {
            "accuracy": acc, 
            "f1_score": f1, 
            "distribution": {str(k): float(v) for k, v in dist_dict.items()},
            "degraded": degraded
        }
        with open("outputs/metrics.json", "w") as f:
            json.dump(metrics_data, f)
            
        with open("outputs/report.txt", "w") as f:
            f.write(f"Model Type: {model_type}\n")
            f.write(f"Accuracy: {acc:.4f} (Old: {old_acc:.4f})\n")
            f.write(f"Status: {'DEGRADED' if degraded else 'IMPROVED'}\n\n")
            f.write("Distribution:\n" + str(dist_dict) + "\n\n")
            f.write("Confusion Matrix:\n" + str(cm) + "\n\n")
            f.write("Classification Report:\n" + report_text)

        # Logging
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

        print(f"Done! Accuracy: {acc:.4f}")
        return acc

if __name__ == "__main__":
    train()
