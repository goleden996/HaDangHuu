import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import colour

st.set_page_config(layout="wide")
st.write("## Biểu đồ CIE dạng band (400 – 700 nm)")

WL_MIN, WL_MAX = 400, 700


@st.cache_data
def band_colors():
    """Màu hiển thị (sRGB) của từng bước sóng đơn sắc 400-700 nm."""
    cmfs = colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
    cmfs = cmfs.copy().align(colour.SpectralShape(WL_MIN, WL_MAX, 1))
    wl = np.array(cmfs.wavelengths)
    XYZ = np.array(cmfs.values)

    rgb = colour.XYZ_to_sRGB(XYZ / XYZ.max(), apply_cctf_encoding=False)
    # Màu đơn sắc nằm ngoài gamut sRGB -> pha thêm trắng để đưa về RGB >= 0
    rgb = rgb - np.minimum(rgb.min(axis=1, keepdims=True), 0)
    rgb = rgb / rgb.max(axis=1, keepdims=True)           # độ sáng cực đại
    rgb = np.clip(colour.cctf_encoding(rgb), 0, 1)       # mã hoá gamma sRGB
    return wl, rgb, XYZ


wl, rgb, XYZ = band_colors()

buoc = st.sidebar.selectbox("Bước chia trục bước sóng (nm)", [10, 20, 25, 50], index=3)
cao = st.sidebar.slider("Chiều cao band", 1, 5, 2)
hien_cmf = st.sidebar.checkbox("Hiển thị đường cong CMF x̄, ȳ, z̄", value=True)

fig, axes = plt.subplots(2 if hien_cmf else 1, 1,
                         figsize=(10, 3 + 3 * hien_cmf),
                         gridspec_kw={"height_ratios": [cao, 3]} if hien_cmf else None)
ax_band = axes[0] if hien_cmf else axes

img = np.tile(rgb[np.newaxis, :, :], (20, 1, 1))
ax_band.imshow(img, extent=[WL_MIN, WL_MAX, 0, 1], aspect="auto")
ax_band.set_yticks([])
ax_band.set_xticks(np.arange(WL_MIN, WL_MAX + 1, buoc))
ax_band.set_xlim(WL_MIN, WL_MAX)
ax_band.set_xlabel("Bước sóng (nm)")
ax_band.set_title("CIE band: màu đơn sắc từ 400 đến 700 nm")

if hien_cmf:
    ax = axes[1]
    ax.plot(wl, XYZ[:, 0], "r", label="x̄(λ)")
    ax.plot(wl, XYZ[:, 1], "g", label="ȳ(λ)")
    ax.plot(wl, XYZ[:, 2], "b", label="z̄(λ)")
    ax.set_xlim(WL_MIN, WL_MAX)
    ax.set_xticks(np.arange(WL_MIN, WL_MAX + 1, buoc))
    ax.set_xlabel("Bước sóng (nm)")
    ax.set_ylabel("Giá trị CMF")
    ax.set_title("Hàm màu CIE 1931 (2° Standard Observer)")
    ax.grid(alpha=0.3)
    ax.legend()

fig.tight_layout()
_, col, _ = st.columns([1, 6, 1])
with col:
    st.pyplot(fig, clear_figure=True)

st.info("Lưu ý: màu đơn sắc nằm ngoài gamut sRGB nên được pha thêm trắng để hiển thị "
        "trên màn hình; màu trên band chỉ mang tính minh hoạ.")
