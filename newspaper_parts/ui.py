"""Streamlit interface for the standalone newspaper-page enhancement demo."""

from __future__ import annotations

import numpy as np
import streamlit as st
from PIL import Image

from .processor import (
    gamma_baseline,
    grayscale_float,
    retinex_illumination_correction,
    sample_low_light_page,
    sauvola_binarize,
)


def _read_upload(uploaded_file) -> np.ndarray:
    with Image.open(uploaded_file) as opened:
        return grayscale_float(np.asarray(opened.convert("RGB")))


def _png_bytes(image: np.ndarray) -> bytes:
    pixels = np.clip(image, 0.0, 1.0)
    output = Image.fromarray((pixels * 255.0 + 0.5).astype(np.uint8), mode="L")
    from io import BytesIO

    buffer = BytesIO()
    output.save(buffer, format="PNG")
    return buffer.getvalue()


def render_app() -> None:
    st.title("Khôi phục ảnh chụp một trang báo")
    st.caption(
        "Thử cân bằng ánh sáng không đều và làm rõ chữ trên ảnh trang giấy. "
        "Đây là công cụ xử lý ảnh, không phải OCR."
    )

    with st.sidebar:
        st.header("Ảnh đầu vào")
        source_choice = st.radio(
            "Chọn nguồn",
            ["Trang mẫu thiếu sáng", "Tải ảnh trang báo"],
            help="Ảnh mẫu có bóng tối và nhiễu mô phỏng để thử trước.",
        )
        uploaded = None
        if source_choice == "Tải ảnh trang báo":
            uploaded = st.file_uploader(
                "Chọn ảnh chụp hoặc ảnh scan",
                type=["png", "jpg", "jpeg", "webp", "tif", "tiff"],
            )

        st.header("Tham số")
        strength = st.slider("Mức cân bằng ánh sáng", 0.0, 1.0, 0.85, 0.05)
        sigma_fraction = st.slider("Độ rộng vùng ước lượng ánh sáng", 0.04, 0.24, 0.12, 0.01)
        gamma = st.slider("Gamma làm sáng (mốc so sánh)", 0.25, 1.0, 0.55, 0.05)
        sauvola_k = st.slider("Ngưỡng Sauvola k", 0.05, 0.40, 0.20, 0.01)

        st.divider()
        st.markdown(
            "[Bài báo KinD trên arXiv](https://arxiv.org/abs/1905.04161)  \n"
            "[Mã nguồn KinD của tác giả](https://github.com/zhangyhuaee/KinD)"
        )

    if source_choice == "Trang mẫu thiếu sáng":
        source = sample_low_light_page()
    elif uploaded is not None:
        source = _read_upload(uploaded)
    else:
        st.info("Tải ảnh trang báo lên thanh bên để bắt đầu; hiện đang dùng trang mẫu.")
        source = sample_low_light_page()

    gamma_result = gamma_baseline(source, gamma=gamma)
    corrected, illumination = retinex_illumination_correction(
        source,
        strength=strength,
        sigma_fraction=sigma_fraction,
    )
    binary = sauvola_binarize(corrected, k=sauvola_k)

    st.subheader("So sánh kết quả")
    first, second = st.columns(2, gap="large")
    with first:
        st.image(source, caption="Ảnh đầu vào", width="stretch", clamp=True)
    with second:
        st.image(gamma_result, caption="Tăng sáng gamma toàn cục", width="stretch", clamp=True)

    third, fourth = st.columns(2, gap="large")
    with third:
        st.image(
            corrected,
            caption="Hiệu chỉnh chiếu sáng lấy cảm hứng từ Retinex",
            width="stretch",
            clamp=True,
        )
    with fourth:
        st.image(binary, caption="Bản đen-trắng Sauvola để đọc chữ", width="stretch", clamp=True)

    with st.expander("Xem bản đồ ánh sáng ước lượng"):
        st.image(illumination, caption="L: ánh sáng nền ước lượng bằng làm trơn Gaussian", width="stretch", clamp=True)

    st.info(
        "KinD trong bài báo là mạng học sâu được huấn luyện bằng các cặp ảnh sáng/tối. "
        "Bản demo này không nạp checkpoint KinD; nó minh họa ý tưởng tách ánh sáng nền "
        "theo kiểu Retinex bằng phép làm trơn, sau đó dùng ngưỡng Sauvola cho tài liệu chữ."
    )

    st.subheader("Tải kết quả")
    download_a, download_b = st.columns(2)
    with download_a:
        st.download_button(
            "Tải ảnh cân bằng ánh sáng",
            data=_png_bytes(corrected),
            file_name="newspaper_illumination_corrected.png",
            mime="image/png",
        )
    with download_b:
        st.download_button(
            "Tải trang đen-trắng",
            data=_png_bytes(binary),
            file_name="newspaper_sauvola.png",
            mime="image/png",
        )

    st.caption(
        "Ảnh chỉ được xử lý trong phiên local hiện tại; không có OCR, không tự lưu ảnh gốc. "
        "Với ảnh thật, kết quả phụ thuộc độ nét, bóng, góc chụp và độ phân giải."
    )
