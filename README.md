# KinD Paper Analysis — Newspaper Page Enhancement Demo

Ứng dụng minh họa xử lý ảnh trang báo hoặc trang tài liệu thiếu sáng của Nhóm 11, lớp 74DCTT25.

## Phạm vi

Đồ án tham khảo bài báo:

> Y. Zhang, J. Zhang, X. Guo, *Kindling the Darkness: A Practical Low-light Image Enhancer*, ACM Multimedia 2019. DOI: [10.1145/3343031.3350926](https://doi.org/10.1145/3343031.3350926).

KinD là mô hình học sâu gồm ba mô-đun phân rã, phục hồi phản xạ và điều chỉnh chiếu sáng. Repo này **không chứa checkpoint và không chạy mạng KinD**. Ứng dụng là demo nhẹ chạy local, sử dụng:

- Gamma làm mốc tăng sáng toàn cục.
- Ước lượng chiếu sáng Gaussian và phép chia nền lấy cảm hứng từ Retinex.
- Ngưỡng cục bộ Sauvola để tạo bản đen–trắng hỗ trợ quan sát chữ.

Mã nguồn KinD chính thức của tác giả: <https://github.com/zhangyhuaee/KinD>.

## Cài đặt

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\Newspaper_Page_Enhancer.py
```

Mở địa chỉ `localhost` được in trong terminal. Web chỉ hoạt động khi tiến trình Streamlit vẫn đang chạy.

## Cách thử

1. Chọn trang mẫu thiếu sáng có sẵn hoặc tải ảnh PNG/JPG/WebP/TIFF.
2. Điều chỉnh mức hiệu chỉnh chiếu sáng, sigma, gamma và hệ số Sauvola.
3. So sánh ảnh đầu vào, gamma, ảnh hiệu chỉnh và ảnh nhị phân.
4. Tải kết quả PNG về máy.

## Cấu trúc

- `Newspaper_Page_Enhancer.py`: điểm vào của Streamlit.
- `newspaper_parts/ui.py`: giao diện, đọc ảnh và tải kết quả.
- `newspaper_parts/processor.py`: các hàm xử lý ảnh và tạo trang mẫu.

## Giới hạn

Trang mẫu lấy từ `skimage.data.page()` và được mô phỏng thiếu sáng. Kết quả hiện tại không thay thế đánh giá trên ảnh báo thật, không thực hiện OCR và không đại diện cho các chỉ số PSNR/SSIM/LOE/NIQE của KinD.

