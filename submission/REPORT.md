# BÁO CÁO KẾT QUẢ BÀI LAB - DAY 21: MLOPS PIPELINE

**Học viên**: Nguyễn Tuấn Kiệt
**Repo GitHub**: https://github.com/Wandseven/Day21-Track2-CI-CD-for-AI-Systems
**IP Server**: 13.221.44.201

---

## 1. Kết Quả Huấn Luyện (Bước 1)
Trong quá trình thực nghiệm cục bộ, tôi đã thực hiện 6 lần chạy (runs) với các bộ siêu tham số khác nhau cho thuật toán Random Forest.

- **Bộ siêu tham số tốt nhất**:
  - `n_estimators`: 1000
  - `max_depth`: 30
  - `min_samples_split`: 2
- **Lý do chọn**: Bộ tham số này cho kết quả `accuracy` và `f1_score` ổn định nhất trên tập đánh giá. Ban đầu với dữ liệu gốc, độ chính xác đạt khoảng 0.678. Sau khi thực hiện chiến lược **Continuous Training** (thêm dữ liệu ở Bước 3), độ chính xác đã vượt ngưỡng **0.70**, đủ điều kiện để kích hoạt Gate Deploy tự động.

## 2. Khó Khăn Gặp Phải & Cách Giải Quyết

### 2.1. Phân quyền Cloud Storage (S3)
- **Vấn đề**: Ban đầu IAM User không có quyền tạo bucket và upload file, dẫn đến lỗi khi chạy lệnh `aws s3 mb` và `dvc push`.
- **Giải quyết**: Cấp quyền `AmazonS3FullAccess` cho IAM User và cấu hình lại AWS Credentials chính xác trong cả local và GitHub Secrets.

### 2.2. Bảo mật SSH Key trên Windows
- **Vấn đề**: File `.pem` dùng để SSH vào EC2 bị lỗi "Permissions are too open" do cơ chế phân quyền của Windows.
- **Giải quyết**: Sử dụng công cụ `icacls` để thu hồi quyền kế thừa và chỉ cấp quyền đọc duy nhất cho người dùng hiện tại (Current User).

### 2.3. Môi trường Python trên Ubuntu VM
- **Vấn đề**: VM sử dụng Ubuntu phiên bản mới áp dụng PEP 668, chặn việc `pip install` trực tiếp vào system python.
- **Giải quyết**: Sử dụng `python3-venv` để tạo môi trường ảo (`~/venv`) trên VM, đảm bảo việc cài đặt các thư viện `fastapi`, `boto3`, `scikit-learn` diễn ra cô lập và ổn định.

### 2.4. Thời gian khởi động Server (Cold Start)
- **Vấn đề**: Do model RandomForest khá nặng (~215MB), bước Health Check trong GitHub Actions thường bị timeout do server chưa kịp tải xong model từ S3.
- **Giải quyết**: Cải tiến script Deploy trong `mlops.yml` bằng cách thêm **vòng lặp retry (12 lần x 10 giây)** để đợi server sẵn sàng trước khi xác nhận Deploy thành công.

## 3. Các Tính Năng Nâng Cao (Bonus)
Tôi đã thực hiện thành công toàn bộ 5/5 yêu cầu Bonus:
- **Bonus 1 (MLflow Remote)**: Tích hợp thành công MLflow với **DagsHub** để theo dõi thí nghiệm online.
- **Bonus 2 (Đa thuật toán)**: Cấu hình `params.yaml` linh hoạt, hỗ trợ cả RandomForest và GradientBoosting.
- **Bonus 3 (Báo cáo chi tiết)**: Tự động tính toán Confusion Matrix, Precision, Recall và lưu thành Artifact trên GitHub.
- **Bonus 4 (Safety Rollback)**: Xây dựng Gate so sánh accuracy với phiên bản cũ trên S3 để ngăn chặn model bị lỗi (degraded).
- **Bonus 5 (Data Drift)**: Tự động cảnh báo lệch lạc dữ liệu ngay trong log của pipeline.

## 4. Kết Luận
Hệ thống đã vận hành đúng theo mô hình MLOps tiêu chuẩn: Code được kiểm thử -> Model được huấn luyện tự động -> Đảm bảo chất lượng qua Eval Gate -> Tự động triển khai lên môi trường Production trên AWS.
