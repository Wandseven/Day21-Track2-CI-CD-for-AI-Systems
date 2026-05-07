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
| **GitHub Repo** | `https://github.com/Wandseven/mlops-day21.git` |
| **VM IP** | `13.221.44.201` |
| **VM User** | `ubuntu` |
| **Python venv** | `.venv\Scripts\python.exe` (đã tạo) |

> ⚠️ **AWS credentials** nằm trong `lab_config.md` (đã add vào `.gitignore`, không bị commit).

---

## 2. Kiến Trúc Pipeline Mục Tiêu

```
[Local machine]
    |-- git push
    v
[GitHub repo: Wandseven/mlops-day21]
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

### 3.2 `src/train.py` ✅ DONE
Đã implement đầy đủ tất cả TODO:
- Đọc CSV với `pd.read_csv()`
- Tách X/y, bỏ cột `target`
- `mlflow.start_run()` + `log_params()` + `log_metric(accuracy, f1_score)` + `log_model()`
- Lưu `outputs/metrics.json`
- Lưu `models/model.pkl`
- `return acc`

### 3.3 `tests/test_train.py` ✅ DONE
Đã implement đầy đủ tất cả TODO:
- `_make_temp_data(tmp_path)`: tạo 200 dòng random, split 160/40
- `test_train_returns_float`: assert float trong [0, 1]
- `test_metrics_file_created`: assert `outputs/metrics.json` có `accuracy` + `f1_score`
- `test_model_file_created`: assert `models/model.pkl` tồn tại

### 3.4 `src/serve.py` ✅ DONE (AWS version)
- Import `boto3` thay vì `google.cloud.storage`
- Biến môi trường: `S3_BUCKET` (thay vì `GCS_BUCKET`)
- `download_model()`: dùng `boto3.client("s3").download_file()`
- `GET /health` → `{"status": "ok"}`
- `POST /predict` → validate 12 features, trả `{"prediction": int, "label": str}`
- Labels: `0→"thap"`, `1→"trung_binh"`, `2→"cao"`

### 3.5 `.github/workflows/mlops.yml` ✅ DONE (AWS version)
4 jobs theo thứ tự:
1. **Unit Test**: `pytest tests/ -v`
2. **Train**: authenticate AWS → `dvc pull` → train → đọc accuracy → upload model lên S3
3. **Eval**: check `accuracy >= 0.70` hoặc exit 1
4. **Deploy**: SSH vào VM → `sudo systemctl restart mlops-serve` → health check

**⚠️ Quan trọng — GitHub Secrets cần add:**

Workflow dùng các secret name sau (cần add vào GitHub repo Settings > Secrets):

| Secret Name | Giá trị lấy từ |
|---|---|
| `CLOUD_CREDENTIALS_KEY` | `AWS_ACCESS_KEY_ID` trong `lab_config.md` |
| `CLOUD_CREDENTIALS_SECRET` | `AWS_SECRET_ACCESS_KEY` trong `lab_config.md` |
| `CLOUD_BUCKET` | `mlops-lab21` |
| `VM_HOST` | `13.221.44.201` |
| `VM_USER` | `ubuntu` |
| `VM_SSH_KEY` | nội dung private key SSH (xem mục 5 bên dưới) |

---

## 4. Việc Đang Dở — `pip install` Thất Bại

Đã chạy:
```powershell
.venv\Scripts\pip install -r requirements.txt
```

**Kết quả**: exit code 1. Lỗi cụ thể chưa xác định rõ (output bị truncate).

**Việc cần làm tiếp theo:**
```powershell
cd "c:\Users\Admin\Desktop\VinAi\LabCoding\Day 21\Day21-Track2-CI-CD-for-AI-Systems"
.venv\Scripts\pip install -r requirements.txt 2>&1 | Select-String "ERROR"
```

Nếu lỗi do version conflict, thử:
```powershell
# Thử install từng gói một để tìm gói lỗi
.venv\Scripts\pip install mlflow==2.13.0 scikit-learn==1.4.2 pandas==2.2.2 2>&1
.venv\Scripts\pip install "dvc[s3]==3.50.1" 2>&1
.venv\Scripts\pip install boto3==1.34.69 fastapi==0.111.0 uvicorn==0.29.0 2>&1
```

---

## 5. Checklist Công Việc Còn Lại

### BƯỚC 1 — Thực nghiệm cục bộ (làm trên local)

- [x] **Fix pip install** (Done: `mlflow 3.12.0` installed)
- [x] **Generate data** (Done: `train_phase1.csv`, `eval.csv`, `train_phase2.csv` created)
- [x] **Chạy 3+ thí nghiệm** (Done: Best accuracy 0.6780 in Run 4/6)
- [x] **Xem MLflow UI + chụp màn hình** (Done: `mlflow.db` created)
- [x] Cập nhật `params.yaml` với bộ params tốt nhất (Done: `n_estimators: 1000, max_depth: 30`)

### BƯỚC 2 — CI/CD

- [ ] **DVC init + kết nối S3**:
  ```powershell
  .venv\Scripts\dvc init
  .venv\Scripts\dvc remote add -d myremote s3://mlops-lab21/dvc
  .venv\Scripts\dvc add data/train_phase1.csv data/eval.csv data/train_phase2.csv
  .venv\Scripts\dvc push
  ```
- [ ] **Tạo GitHub repo mới + push code lên**:
  ```powershell
  git remote add origin https://github.com/Wandseven/mlops-day21.git
  git add .gitignore src/ tests/ .github/ params.yaml requirements.txt generate_data.py add_new_data.py data/*.dvc .dvc/
  # *** HỎI USER TRƯỚC KHI COMMIT ***
  git commit -m "feat: initial MLOps lab setup"
  git push -u origin main
  ```
- [ ] **Tạo SSH deploy key**:
  ```powershell
  ssh-keygen -t ed25519 -f ~/.ssh/mlops_deploy -N "" -C "github-actions-deploy"
  # Copy public key lên VM:
  # cat ~/.ssh/mlops_deploy.pub  --> paste vào ~/.ssh/authorized_keys trên VM
  ```
- [ ] **Cài đặt VM** (SSH vào `ubuntu@13.221.44.201`):
  ```bash
  sudo apt update && sudo apt install -y python3-pip
  pip3 install fastapi uvicorn scikit-learn joblib boto3
  mkdir -p ~/models ~/src
  ```
- [ ] **Upload serve.py lên VM**:
  ```bash
  scp src/serve.py ubuntu@13.221.44.201:~/src/serve.py
  ```
- [ ] **Tạo systemd service trên VM** (SSH vào VM):
  ```bash
  sudo tee /etc/systemd/system/mlops-serve.service > /dev/null <<EOF
  [Unit]
  Description=MLOps Model Inference Server
  After=network.target

  [Service]
  User=ubuntu
  WorkingDirectory=/home/ubuntu
  Environment="S3_BUCKET=mlops-lab21"
  Environment="AWS_ACCESS_KEY_ID=<key>"
  Environment="AWS_SECRET_ACCESS_KEY=<secret>"
  Environment="AWS_DEFAULT_REGION=us-east-1"
  ExecStart=/usr/bin/python3 /home/ubuntu/src/serve.py
  Restart=always
  RestartSec=5

  [Install]
  WantedBy=multi-user.target
  EOF

  sudo systemctl daemon-reload
  sudo systemctl enable mlops-serve
  # CHƯA start — chờ pipeline lần đầu upload model lên S3 trước
  ```
- [ ] **Add 6 GitHub Secrets** (Settings > Secrets > Actions):
  - `CLOUD_CREDENTIALS_KEY` = AWS_ACCESS_KEY_ID
  - `CLOUD_CREDENTIALS_SECRET` = AWS_SECRET_ACCESS_KEY
  - `CLOUD_BUCKET` = `mlops-lab21`
  - `VM_HOST` = `13.221.44.201`
  - `VM_USER` = `ubuntu`
  - `VM_SSH_KEY` = nội dung `~/.ssh/mlops_deploy` (private key)
- [ ] **Trigger pipeline** (push code → Actions tab màu xanh)
- [ ] **Sau khi pipeline xanh**, start service:
  ```bash
  ssh ubuntu@13.221.44.201 "sudo systemctl start mlops-serve"
  ```
- [ ] **Test endpoint + chụp màn hình**:
  ```bash
  curl http://13.221.44.201:8000/health
  curl -X POST http://13.221.44.201:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
  ```

### BƯỚC 3 — Continuous Training

- [ ] **Thêm dữ liệu mới**:
  ```powershell
  .venv\Scripts\python add_new_data.py
  # train_phase1.csv: 2998 -> 5996 mẫu
  ```
- [ ] **Version hóa + trigger** (ĐÚNG THỨ TỰ: dvc push TRƯỚC git push):
  ```powershell
  .venv\Scripts\dvc add data/train_phase1.csv
  git add data/train_phase1.csv.dvc
  # *** HỎI USER TRƯỚC KHI COMMIT ***
  git commit -m "data: bo sung 2998 mau du lieu moi (train_phase2)"
  .venv\Scripts\dvc push
  git push origin main
  ```
- [ ] Chụp màn hình Actions run được trigger bởi commit data

---

## 6. Ảnh Chụp Màn Hình Cần Nộp

| # | Nội dung | Trạng thái |
|---|---|---|
| 1 | MLflow UI: ≥3 runs với hyperparams khác nhau | ⬜ Chưa |
| 2 | GitHub Actions: 4 jobs màu xanh (Bước 2) | ⬜ Chưa |
| 3 | GitHub Actions: 4 jobs màu xanh (Bước 3, trigger bởi data commit) | ⬜ Chưa |
| 4 | `curl http://13.221.44.201:8000/health` output | ⬜ Chưa |
| 5 | `curl http://13.221.44.201:8000/predict` output | ⬜ Chưa |
| 6 | S3 Console: file trong `dvc/` + `models/latest/model.pkl` | ⬜ Chưa |

---

## 7. Quy Tắc Bắt Buộc

> ⚠️ **KHÔNG được `git commit` hoặc `git push` bất kỳ thứ gì mà không hỏi user trước.**

---

## 8. Cấu Trúc Thư Mục Sau Khi Hoàn Thành

```
Day21-Track2-CI-CD-for-AI-Systems/
├── .github/workflows/mlops.yml   ✅ Đã viết (AWS)
├── .dvc/config                   ⬜ Tạo khi dvc init + remote add
├── data/
│   ├── train_phase1.csv.dvc      ⬜ Tạo khi dvc add
│   ├── eval.csv.dvc              ⬜ Tạo khi dvc add
│   └── train_phase2.csv.dvc      ⬜ Tạo khi dvc add
├── src/
│   ├── __init__.py               ✅ Đã có
│   ├── train.py                  ✅ Đã viết đầy đủ
│   └── serve.py                  ✅ Đã viết đầy đủ (AWS S3)
├── tests/
│   ├── __init__.py               ✅ Đã có
│   └── test_train.py             ✅ Đã viết đầy đủ
├── generate_data.py              ✅ Đã có (không sửa)
├── add_new_data.py               ✅ Đã có (không sửa)
├── params.yaml                   ✅ Đã có (cần cập nhật sau run 3)
├── requirements.txt              ✅ Đã cập nhật (boto3, dvc[s3])
├── lab_config.md                 ✅ Đã điền (trong .gitignore)
└── .gitignore                    ✅ Đã có lab_config.md
```
