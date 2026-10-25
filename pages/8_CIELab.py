import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import colour

st.set_page_config(layout="wide")
st.write("## Biểu đồ CIELab: chuyển dịch màu từ Lab1 sang Lab2")

D50 = colour.CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]["D50"]


def lab_to_srgb(Lab):
    """Lab (D50) -> sRGB 0..1, có thích nghi màu D50 -> D65."""
    XYZ = colour.Lab_to_XYZ(Lab, illuminant=D50)
    return XYZ, colour.XYZ_to_sRGB(XYZ, illuminant=D50)


def mo_ta_do_lech(dE):
    if dE < 1:
        return "mắt người gần như không phân biệt được"
    if dE < 2:
        return "rất nhỏ, chỉ người có kinh nghiệm mới nhận ra"
    if dE < 3.5:
        return "nhỏ, nhận ra khi so sánh trực tiếp"
    if dE < 5:
        return "trung bình, nhận ra rõ"
    return "lớn, hai màu khác nhau rõ rệt"


def ten_hue(h):
    if h < 20 or h >= 340:
        return "đỏ-hồng"
    if h < 50:
        return "đỏ-cam"
    if h < 80:
        return "cam-vàng"
    if h < 110:
        return "vàng"
    if h < 160:
        return "vàng-lục"
    if h < 200:
        return "lục"
    if h < 250:
        return "lục lam-lam"
    if h < 290:
        return "xanh dương"
    if h < 340:
        return "tím-đỏ tím"
    return ""


# ---------------- Nhập liệu ----------------
c1, c2 = st.columns(2)
with c1:
    st.write("### Lab1 (màu gốc)")
    L1 = st.number_input("L1", 0.0, 100.0, 50.0, key="L1")
    a1 = st.number_input("a1", -128.0, 127.0, 40.0, key="a1")
    b1 = st.number_input("b1", -128.0, 127.0, 20.0, key="b1")
with c2:
    st.write("### Lab2 (màu sau khi dịch chuyển)")
    L2 = st.number_input("L2", 0.0, 100.0, 60.0, key="L2")
    a2 = st.number_input("a2", -128.0, 127.0, 20.0, key="a2")
    b2 = st.number_input("b2", -128.0, 127.0, 45.0, key="b2")

if not st.button("Vẽ và nhận xét"):
    st.stop()

Lab1 = np.array([L1, a1, b1])
Lab2 = np.array([L2, a2, b2])
XYZ1, rgb1 = lab_to_srgb(Lab1)
XYZ2, rgb2 = lab_to_srgb(Lab2)
xy1 = colour.XYZ_to_xy(XYZ1)
xy2 = colour.XYZ_to_xy(XYZ2)
rgb1c, rgb2c = np.clip(rgb1, 0, 1), np.clip(rgb2, 0, 1)

# ---------------- Tính toán ----------------
dL, da, db = Lab2 - Lab1
LCh1 = colour.Lab_to_LCHab(Lab1)
LCh2 = colour.Lab_to_LCHab(Lab2)
dC = LCh2[1] - LCh1[1]
dh = (LCh2[2] - LCh1[2] + 180) % 360 - 180
dE76 = colour.delta_E(Lab1, Lab2, method="CIE 1976")
dE00 = colour.delta_E(Lab1, Lab2, method="CIE 2000")

# ---------------- Ô màu ----------------
s1, s2 = st.columns(2)
for col, rgb, Lab, name in ((s1, rgb1c, Lab1, "Lab1"), (s2, rgb2c, Lab2, "Lab2")):
    hexc = "#%02X%02X%02X" % tuple((rgb * 255).round().astype(int))
    col.markdown(
        f"<div style='background:{hexc};height:70px;border:1px solid #888;"
        f"border-radius:6px;text-align:center;line-height:70px;'>"
        f"<b>{name}</b> {hexc}</div>",
        unsafe_allow_html=True)

# ---------------- Biểu đồ ----------------
g1, g2 = st.columns(2)

with g1:
    figure, axes = colour.plotting.plot_chromaticity_diagram_CIE1931(show=False)
    axes.set_xlim([-0.1, 0.85])
    axes.set_ylim([-0.1, 0.90])
    axes.set_title("CIE 1931 xy: Lab1 → Lab2")
    axes.plot(*xy1, "o", ms=9, mfc=rgb1c, mec="k", label="Lab1")
    axes.plot(*xy2, "s", ms=9, mfc=rgb2c, mec="k", label="Lab2")
    axes.annotate("", xy=xy2, xytext=xy1,
                  arrowprops=dict(arrowstyle="->", color="k", lw=1.5))
    axes.legend(loc="upper right")
    st.pyplot(figure, clear_figure=True)

with g2:
    r = np.linspace(-110, 110, 221)
    A, B = np.meshgrid(r, r)
    Lm = (L1 + L2) / 2
    lab_grid = np.dstack([np.full_like(A, Lm), A, B])
    _, rgb_grid = lab_to_srgb(lab_grid)
    ngoai = np.any((rgb_grid < 0) | (rgb_grid > 1), axis=2)
    rgb_grid = np.clip(rgb_grid, 0, 1)
    rgb_grid[ngoai] = 0.92          # vùng ngoài gamut sRGB -> xám nhạt

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.imshow(rgb_grid, extent=[-110, 110, -110, 110], origin="lower")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.axvline(0, color="k", lw=0.6)
    ax2.plot(a1, b1, "o", ms=10, mfc=rgb1c, mec="k", label="Lab1")
    ax2.plot(a2, b2, "s", ms=10, mfc=rgb2c, mec="k", label="Lab2")
    ax2.annotate("", xy=(a2, b2), xytext=(a1, b1),
                 arrowprops=dict(arrowstyle="->", color="k", lw=1.8))
    ax2.set_xlabel("a*  (−lục ... +đỏ)")
    ax2.set_ylabel("b*  (−lam ... +vàng)")
    ax2.set_title(f"Mặt phẳng a*b* (nền vẽ tại L* = {Lm:.0f})")
    ax2.legend(loc="upper right")
    st.pyplot(fig2, clear_figure=True)

# ---------------- Bảng số liệu ----------------
st.write("### Kết quả tính toán")
st.table({
    "Đại lượng": ["ΔL*", "Δa*", "Δb*", "ΔC*ab", "Δh°ab", "ΔE*ab (CIE76)", "ΔE00 (CIEDE2000)"],
    "Giá trị": [f"{dL:+.2f}", f"{da:+.2f}", f"{db:+.2f}", f"{dC:+.2f}",
                f"{dh:+.1f}", f"{dE76:.2f}", f"{dE00:.2f}"],
})

# ---------------- Nhận xét tự động ----------------
st.write("### Nhận xét sự chuyển dịch màu từ Lab1 sang Lab2")
nx = []
if abs(dL) < 0.5:
    nx.append("- **Độ sáng (L\\*)**: gần như không đổi.")
else:
    nx.append(f"- **Độ sáng (L\\*)**: {'sáng hơn' if dL > 0 else 'tối hơn'} "
              f"{abs(dL):.1f} đơn vị (L\\*: {L1:.1f} → {L2:.1f}).")
if abs(da) >= 0.5:
    nx.append(f"- **Trục a\\***: dịch về phía {'đỏ' if da > 0 else 'lục'} "
              f"({abs(da):.1f} đơn vị).")
if abs(db) >= 0.5:
    nx.append(f"- **Trục b\\***: dịch về phía {'vàng' if db > 0 else 'lam'} "
              f"({abs(db):.1f} đơn vị).")
if abs(dC) >= 0.5:
    nx.append(f"- **Độ bão hoà (C\\*)**: {'tăng' if dC > 0 else 'giảm'}: "
              f"C\\* {LCh1[1]:.1f} → {LCh2[1]:.1f} → màu "
              f"{'rực hơn' if dC > 0 else 'xỉn (nhạt màu) hơn'}.")
if abs(dh) >= 1:
    nx.append(f"- **Góc sắc (h°)**: {LCh1[2]:.0f}° ({ten_hue(LCh1[2])}) → "
              f"{LCh2[2]:.0f}° ({ten_hue(LCh2[2])}), lệch {abs(dh):.0f}° "
              f"theo chiều {'ngược' if dh > 0 else 'thuận'} kim đồng hồ.")
nx.append(f"- **Mức chênh lệch tổng**: ΔE\\*ab = {dE76:.2f}, ΔE00 = {dE00:.2f} → "
          f"{mo_ta_do_lech(dE00)}.")
st.markdown("\n".join(nx))
