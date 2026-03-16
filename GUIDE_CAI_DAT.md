# Hướng Dẫn Cài Đặt & Chạy Hệ Thống LiveTalking (MuseTalk)

Tài liệu này tổng hợp lại toàn bộ các bước cài đặt, cấu hình mô hình và các bản sửa lỗi (fix) cần thiết để chạy hệ thống trên máy Linux (Ubuntu/Debian).

## 1. Môi trường Python (Conda)

Khuyến khích dùng **Conda** để quản lý môi trường:

```bash
conda create -n livetalking_py310 python=3.10
conda activate livetalking_py310
```

### Các thư viện quan trọng cần lưu ý:
- **Numpy**: Phải dùng bản `< 2.0` để tránh lỗi tương thích OpenCV.
- **OpenCV**: Bản ổn định `4.9.0.80`.
- **Transformers**: Cần bản mới (từ `5.3.0` trở lên) để chạy mô hình Whisper.
- **MMCV**: Do lỗi biên dịch C++ trên một số máy, chúng ta dùng bản vá "Dummy" (chi tiết ở mục 3).

## 2. Danh sách Mô hình AI (Models Hierarchy)

Đây là các mô hình cần tải từ HuggingFace (HF). Các link dưới đây là bản Mirror công khai không cần đăng nhập.

### Cấu trúc thư mục `models/` chuẩn:
```text
/LiveTalking/models/
├── musetalkV15/
│   ├── unet.pth (Tải từ afrizalha/musetalk-models/musetalk/pytorch_model.bin)
│   └── musetalk.json (Tải từ afrizalha/musetalk-models/musetalk/musetalk.json)
├── sd-vae/
│   ├── config.json (Tải từ stabilityai/sd-vae-ft-mse)
│   └── diffusion_pytorch_model.bin
├── dwpose/
│   └── dw-ll_ucoco_384.pth (Tải từ afrizalha/musetalk-models/dwpose/dw-ll_ucoco_384.pth)
├── face-parse-bisent/
│   ├── resnet18-5c106cde.pth
│   └── 79999_iter.pth (Tải từ afrizalha/musetalk-models/face-parse-bisent)
├── whisper/
│   ├── config.json
│   └── pytorch_model.bin (Tải từ openai/whisper-tiny)
└── wav2lip.pth (Mô hình bổ trợ)
```

## 3. Các bản vá lỗi (Essential Fixes)

### Lỗi MMCV (Import Error):
Nếu gặp lỗi `ModuleNotFoundError: No module named 'mmcv._ext'`, hãy tạo file dummy tại:
`miniconda3/envs/livetalking_py310/lib/python3.10/site-packages/mmcv/_ext.py`
Nội dung: `def __getattr__(name): return lambda *args, **kwargs: None`

### Lỗi Transformers:
Bản `diffusers` mới yêu cầu `Dinov2WithRegistersConfig`. Cần nâng cấp:
```bash
pip install -U transformers diffusers accelerate
```

## 4. Lệnh thực thi

### Bước 1: Tạo Avatar từ Video của bạn
```bash
python musetalk/genavatar.py --avatar_id custom_kling --file path/to/your/video.mp4
```

### Bước 2: Khởi chạy ứng dụng
```bash
python app.py --model musetalk --avatar_id custom_kling --transport webrtc
```

### Bước 3: Truy cập UI
Mở link: `http://localhost:8010/dashboard.html`

## 5. Tự động hoá
Bạn có thể dùng script `download_models.py` trong thư mục gốc để tự động hóa việc tải và sắp xếp tệp tin.

---

# 🚀 Hướng Dẫn Cho Người Nhận Bản Nén (Zip Full)

Nếu bạn đã nhận được bản nén bao gồm cả thư mục `models/` (nặng ~6GB), bạn chỉ cần thực hiện 3 bước sau để chạy:

### Bước 1: Cài đặt phần mềm nền (Chỉ làm 1 lần)
1. **Cài đặt FFmpeg**: 
   - Linux: `sudo apt install ffmpeg`
   - Windows: Tải FFmpeg exe và thêm vào PATH.
2. **Cài đặt NVIDIA Driver & CUDA**: Đảm bảo máy có card đồ họa NVIDIA (khuyên dùng RTX 3060 trở lên).

### Bước 2: Thiết lập môi trường Python
Mở terminal tại thư mục dự án và chạy:
```bash
# 1. Tạo môi trường mới
conda create -n livetalking python=3.10 -y
conda activate livetalking

# 2. Cài đặt toàn bộ thư viện (đã đóng băng phiên bản chuẩn)
pip install -r requirements.txt
```

### Bước 3: Chạy ứng dụng ngay lập tức
Không cần tải thêm mô hình AI vì đã có sẵn trong bản zip. Chạy lệnh:
```bash
python app.py --model musetalk --avatar_id custom_kling --transport webrtc
```
Truy cập giao diện tại: `http://localhost:8010/dashboard.html`

> [!IMPORTANT]
> **Lưu ý về lỗi MMCV**: Nếu khi chạy báo lỗi `mmcv._ext`, hãy kiểm tra xem file `miniconda3/envs/livetalking/lib/python3.10/site-packages/mmcv/_ext.py` đã có nội dung "vá lỗi" như ở **Mục 3** phía trên chưa.
