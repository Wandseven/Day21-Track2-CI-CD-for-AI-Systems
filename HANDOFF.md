# HANDOFF — Lab Day 21: CI/CD for AI Systems

> **Mục đích**: File này ghi lại toàn bộ công việc đã làm và việc còn lại để agent kế tiếp có thể tiếp tục ngay mà không cần đọc lại README.

---

## 1. Thông Tin Cơ Bản

| Thông tin | Giá trị |
|---|---|
| **Workspace** | `c:\Users\Admin\Desktop\VinAi\LabCoding\Day 21\Day21-Track2-CI-CD-for-AI-Systems` |
| **Cloud Provider** | **AWS** |
| **AWS Region** | `us-east-1` |
| **S3 Bucket** | `mlops-lab21` |
| **GitHub Repo** | `https://github.com/Wandseven/Day21-Track2-CI-CD-for-AI-Systems.git` |
| **VM IP** | `13.221.44.201` |
| **VM User** | `ubuntu` |
| **Python venv** | `.venv\Scripts\python.exe` (đã tạo) |

---

## 2. Kiến Trúc Pipeline Mục Tiêu

```
[Local machine]
    |-- git push
    v
[GitHub repo: Wandseven/Day21-Track2-CI-CD-for-AI-Systems]
    |-- GitHub Actions trigger
    v
[Runner: Unit Test -> Train -> Eval (>= 0.70) -> Deploy]
    |                                   |
    | dvc pull                          | s3.upload (model)
    v                                   v
[S3: mlops-lab21]               [EC2 VM: 13.221.44.201]
  dvc/                            mlops-serve (FastAPI)
  models/latest/model.pkl           POST /predict
```

---

## 3. Files Đã Được Viết / Chỉnh Sửa

### 3.1 `requirements.txt` ✅ DONE
- Thay `dvc[gs]` → `dvc[s3]`
- Thay `google-cloud-storage` → `boto3==1.34.69`
- Nâng `mlflow>=2.14.0` (tương thích Python 3.12)

### 3.2 `src/train.py` ✅ DONE
### 3.3 `tests/test_train.py` ✅ DONE
### 3.4 `src/serve.py` ✅ DONE (AWS version)
### 3.5 `.github/workflows/mlops.yml` ✅ DONE (AWS version)

---

## 4. Checklist Tiến Độ

### BƯỚC 1 — Thực nghiệm cục bộ ✅ DONE
- [x] Fix pip install (`mlflow 3.12.0`)
- [x] Generate data
- [x] Chạy 6 thí nghiệm (Best accuracy: 0.6780)
- [x] Cập nhật `params.yaml` (`n_estimators: 1000, max_depth: 30`)

### BƯỚC 2 — CI/CD [/] IN PROGRESS
- [x] **DVC init + kết nối S3** (Done)
- [x] **Tạo GitHub repo mới + push code lên** (Done)
- [x] **Tạo SSH deploy key** (Done: `mlops_deploy` created and public key added to VM)
- [x] **Cài đặt VM** (Done: `python3-venv` + dependencies installed)
- [x] **Upload serve.py lên VM** (Done)
- [x] **Tạo systemd service trên VM** (Done)
- [x] **Add 6 GitHub Secrets** (Done)
- [/] **Trigger pipeline** (Code đã push, đang chạy GitHub Actions đợt 1)

**Trạng thái mong đợi**: Pipeline đợt 1 sẽ **FAIL** ở job Eval vì accuracy (0.678) < 0.70. Đây là hành vi đúng để demo "Eval Gate".

### BƯỚC 3 — Continuous Training [/] IN PROGRESS
- [x] **Thêm dữ liệu mới**: `python add_new_data.py` (Done: 5996 mẫu)
- [ ] **Update DVC + Push code**:
  ```powershell
  dvc add data/train_phase1.csv
  git add data/train_phase1.csv.dvc
  git commit -m "data: added more training data"
  dvc push
  git push origin main
  ```
- [ ] **Verify**: Pipeline đợt 2 thành công, tự động deploy.

---

## 5. Ảnh Chụp Màn Hình Cần Nộp

| # | Nội dung | Trạng thái |
|---|---|---|
| 1 | MLflow UI: ≥3 runs với hyperparams khác nhau | ⬜ Chưa |
| 2 | GitHub Actions: 4 jobs màu xanh (Bước 2) | ⬜ Chưa |
| 3 | GitHub Actions: 4 jobs màu xanh (Bước 3, trigger bởi data commit) | ⬜ Chưa |
| 4 | `curl http://13.221.44.201:8000/health` output | ⬜ Chưa |
| 5 | `curl http://13.221.44.201:8000/predict` output | ⬜ Chưa |
| 6 | S3 Console: file trong `dvc/` + `models/latest/model.pkl` | ⬜ Chưa |
