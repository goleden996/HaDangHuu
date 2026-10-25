import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import colour

st.set_page_config(layout="wide")
st.write("## So sánh gamut các không gian màu / thiết bị")

SPACES = {
    "sRGB": "k",
    "Adobe RGB (1998)": "tab:blue",
    "DCI-P3": "tab:green",
    "ITU-R BT.2020": "tab:red",
}


def dien_tich(px, py):
    """Diện tích đa giác (công thức Shoelace)."""
    return 0.5 * abs(np.dot(px, np.roll(py, -1)) - np.dot(py, np.roll(px, -1)))


chon = st.sidebar.multiselect("Chọn không gian màu", list(SPACES), default=list(SPACES))
csv_file = st.sidebar.file_uploader("(Tuỳ chọn) File gamut máy in .csv", type=["csv"])

figure, axes = colour.plotting.plot_chromaticity_diagram_CIE1931(show=False)
axes.set_xlim([-0.1, 0.85])
axes.set_ylim([-0.1, 0.90])
axes.set_title("So sánh gamut trên CIE 1931 xy")

areas = {}
for name in chon:
    cs = colour.RGB_COLOURSPACES[name]
    p = np.array(cs.primaries)
    px = np.append(p[:, 0], p[0, 0])
    py = np.append(p[:, 1], p[0, 1])
    axes.plot(px, py, color=SPACES[name], lw=1.8, label=name)
    areas[name] = dien_tich(px[:-1], py[:-1])

if csv_file is not None:
    df = pd.read_csv(csv_file).set_index("ColorSpace")
    px, py = [], []
    for ch in ["R", "Y", "G", "C", "B", "M"]:
        xy = colour.XYZ_to_xy(colour.Lab_to_XYZ(df[ch].to_numpy()))
        px.append(xy[0])
        py.append(xy[1])
    areas["Máy in (từ file)"] = dien_tich(np.array(px), np.array(py))
    px.append(px[0])
    py.append(py[0])
    axes.plot(px, py, "m--", lw=2, label="Máy in (từ file)")

axes.legend(loc="upper right")
c1, c2 = st.columns([3, 2])
with c1:
    st.pyplot(figure, clear_figure=True)
with c2:
    if areas:
        ref = areas.get("sRGB", list(areas.values())[0])
        st.write("### Diện tích gamut (trên mặt phẳng xy)")
        st.dataframe(pd.DataFrame({
            "Không gian màu": list(areas),
            "Diện tích": [round(v, 4) for v in areas.values()],
            "So với sRGB (%)": [round(v / areas.get("sRGB", ref) * 100, 1)
                                for v in areas.values()],
        }), hide_index=True)
        st.caption("Diện tích tính trên xy chỉ để so sánh tương đối; "
                   "u'v' hoặc a*b* phản ánh cảm nhận thị giác tốt hơn.")
