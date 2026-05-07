# HANDOFF — Lab Day 21: CI/CD for AI Systems ✅ COMPLETED

> **Trạng thái**: Hoàn thành 100% yêu cầu bài lab. Hệ thống đã hoạt động ổn định trên AWS.

---

## 1. Thông Tin Tổng Kết

| Thông tin | Giá trị |
|---|---|
| **S3 Bucket** | `mlops-lab21` (Chứa dữ liệu DVC và Model artifact) |
| **GitHub Repo** | `https://github.com/Wandseven/Day21-Track2-CI-CD-for-AI-Systems.git` |
| **VM IP (Public)** | `13.221.44.201` |
| **Service URL** | `http://13.221.44.201:8000` |
| **Accuracy Cuối** | `> 0.70` (Vượt qua Eval Gate) |

---

## 2. Nhật Ký Thực Hiện

### BƯỚC 1 — Thực nghiệm cục bộ ✅
- Hoàn thành training script với MLflow.
- Tuning hyperparameters: `n_estimators=1000, max_depth=30`.
- Kết quả tốt nhất ban đầu: `0.6780`.

### BƯỚC 2 — Pipeline CI/CD & Eval Gate ✅
- Cấu hình GitHub Actions với 4 Jobs.
- **Demo Eval Gate**: Pipeline lần 1 thất bại tại bước Eval (vì accuracy 0.678 < 0.70). Code không được deploy.
- Sửa lỗi AWS Authentication và Deploy Script (thêm retry loop).

### BƯỚC 3 — Continuous Training & Deploy ✅
- Thêm 3000 mẫu dữ liệu mới.
- Cập nhật DVC và push lên S3.
- Pipeline lần 2 tự động trigger, accuracy tăng lên vượt ngưỡng 0.70.
- **Deploy thành công**: Hệ thống tự động cài đặt model mới lên EC2 và khởi động lại service.

---

## 3. Hướng Dẫn Kiểm Tra Cuối Cùng

### Test API (Chạy tại local terminal)
```powershell
# Kiểm tra sức khỏe
curl.exe http://13.221.44.201:8000/health

# Thử dự đoán
curl.exe -X POST http://13.221.44.201:8000/predict -H "Content-Type: application/json" -d "{\"features\": [7.0, 0.27, 0.36, 20.7, 0.045, 45.0, 170.0, 1.001, 3.0, 0.45, 8.8, 1.0]}"
```

---

## 4. Checklist Minh Chứng (Dành cho báo cáo)
- [x] Ảnh MLflow UI (nhiều run).
- [x] Ảnh GitHub Actions thành công (4 ticks xanh).
- [x] Ảnh GitHub Actions thất bại (Eval đỏ - minh chứng gate hoạt động).
- [x] Ảnh S3 Bucket (chứa model).
- [x] Ảnh kết quả `curl` từ máy cá nhân.

---
*Cảm ơn bạn đã cùng tôi thực hiện bài lab này!*
