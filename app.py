import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import cv2
import re
import easyocr
from supabase.client import create_client
import tensorflow as tf

# -----------------------------
# SUPABASE INIT
# -----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
 
# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title=" Smart Kühlschrank",
    layout="centered",
    initial_sidebar_state="collapsed"
)
 
# -----------------------------
# CUSTOM CSS — Bunt & Freundlich
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');
 
/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}
 
/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #fef9f0 0%, #f0f8ff 50%, #f9f0fe 100%);
    min-height: 100vh;
}
 
/* ── Main Title ── */
h1 {
    font-family: 'Fredoka One', cursive !important;
    font-size: 2.8rem !important;
    background: linear-gradient(90deg, #ff6b6b, #ffa94d, #51cf66, #339af0, #cc5de8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.2rem !important;
    letter-spacing: 1px;
}
 
/* ── Section Headers ── */
h2, h3 {
    font-family: 'Fredoka One', cursive !important;
    color: #5c4a8f !important;
    font-size: 1.4rem !important;
    margin-top: 1.5rem !important;
}
 
/* ── Subtitle banner ── */
.subtitle-banner {
    text-align: center;
    font-size: 1rem;
    color: #888;
    font-weight: 600;
    margin-bottom: 2rem;
    letter-spacing: 0.5px;
}
 
/* ── Cards / Sections ── */
.section-card {
    background: white;
    border-radius: 20px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 2px solid transparent;
    transition: border 0.2s;
}
 
/* ── Inventory row container ── */
.inv-header {
    display: grid;
    grid-template-columns: 3fr 2fr 2fr 1fr;
    gap: 8px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    padding: 0.7rem 1.2rem;
    border-radius: 12px;
    font-weight: 800;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}
 
.inv-row {
    display: grid;
    grid-template-columns: 3fr 2fr 2fr 1fr;
    gap: 8px;
    padding: 0.6rem 1.2rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
    align-items: center;
    background: #f8f9ff;
    margin-bottom: 6px;
    border-left: 5px solid #e9ecef;
    transition: transform 0.1s;
}
 
.inv-row:hover {
    transform: translateX(4px);
}
 
.inv-row.danger { border-left-color: #ff6b6b; background: #fff5f5; }
.inv-row.warn   { border-left-color: #ffa94d; background: #fff9f0; }
.inv-row.ok     { border-left-color: #51cf66; background: #f0fff4; }
 
/* ── Streamlit Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: #f0f0f0;
    border-radius: 30px !important;
    padding: 0.4rem 1.2rem !important;
    font-weight: 700;
    font-family: 'Nunito', sans-serif;
    font-size: 0.9rem;
    border: none !important;
    color: #555;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    color: white !important;
}
 
/* ── Buttons ── */
.stButton > button {
    border-radius: 30px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    padding: 0.5rem 1.8rem !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
 
/* Primary save button */
div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button {
    background: linear-gradient(90deg, #51cf66, #20c997) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(81,207,102,0.4) !important;
}
div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 6px 20px rgba(81,207,102,0.5) !important;
}
 
/* Delete buttons */
.stButton > button[kind="secondary"] {
    background: #ffe3e3 !important;
    color: #fa5252 !important;
    font-size: 0.8rem !important;
    padding: 0.2rem 0.6rem !important;
}
 
/* ── Success / Info messages ── */
.stAlert {
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
}
 
/* ── Text inputs ── */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #e0e0e0 !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: border 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
}
 
/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 2.5rem;
    color: #aaa;
    font-size: 1.1rem;
    font-weight: 700;
}
.empty-state span {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.5rem;
}
 
/* ── Detected food pill ── */
.food-pill {
    display: inline-block;
    background: linear-gradient(90deg, #ffa94d, #ff6b6b);
    color: white;
    border-radius: 30px;
    padding: 0.4rem 1.2rem;
    font-weight: 800;
    font-size: 1rem;
    margin-top: 0.5rem;
    letter-spacing: 0.3px;
}
 
/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-chip {
    border-radius: 20px;
    padding: 0.5rem 1.2rem;
    font-weight: 800;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.stat-chip.total  { background: #e7f5ff; color: #1971c2; }
.stat-chip.danger { background: #fff5f5; color: #c92a2a; }
.stat-chip.warn   { background: #fff9db; color: #e67700; }
.stat-chip.ok     { background: #ebfbee; color: #2f9e44; }
 
/* ── Divider ── */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, #667eea22, #764ba222, #667eea22);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)
 
# -----------------------------
# MODELS (cached)
# ── Teachable Machines: keras_model.h5 + labels.txt ins App-Verzeichnis legen ──
# ── Modell: Input 224x224x3, Output 6 Klassen (Softmax) ──
# -----------------------------
@st.cache_resource
def load_models():
    model = tf.keras.models.load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r", encoding="utf-8") as f:
        # Teachable Machines schreibt "0 Gurke", "1 Paprika" — wir nehmen nur den Namen
        class_names = [line.strip().split(" ", 1)[-1] for line in f.readlines() if line.strip()]
    return model, class_names

model, labels = load_models()

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['de', 'en'])
 
ocr = load_ocr()

# -----------------------------
# CLASSIFY (Teachable Machines)
# ── Input 224x224, Normalisierung: (x / 127.5) - 1  (Standard TM) ──
# ── Schwellwert 70%: darunter → None (verhindert falsche Labels) ──
# -----------------------------
CONFIDENCE_THRESHOLD = 0.70

def classify_image(image):
    img = image.convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = (arr / 127.5) - 1.0         # Teachable Machines Normalisierung
    arr = np.expand_dims(arr, axis=0)  # → (1, 224, 224, 3)
    predictions = model.predict(arr, verbose=0)
    index = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][index])
    if confidence < CONFIDENCE_THRESHOLD:
        return None                    # zu unsicher → kein Label ausgeben
    return labels[index]

# -----------------------------
# SESSION STATE
# -----------------------------
if "food_item" not in st.session_state:
    st.session_state.food_item = None
if "mhd_value" not in st.session_state:
    st.session_state.mhd_value = None
 
# -----------------------------
# HELPERS
# -----------------------------
def normalize_date(value):
    if not value:
        return None
    value = value.strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value
    match = re.match(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})", value)
    if match:
        d, m, y = match.groups()
        if len(y) == 2:
            y = "20" + y
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return None
 
def extract_mhd(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(3.0, (8, 8))
    gray = clahe.apply(gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    result = ocr.readtext(thresh, detail=0)
    text = " ".join(result)
    match = re.search(r"\d{2}[.\-/]\d{2}[.\-/]\d{2,4}", text)
    return match.group() if match else None
 
# -----------------------------
# HEADER
# -----------------------------
st.markdown("<h1> Smart Kühlschrank</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-banner'>Dein intelligenter Lebensmittel-Assistent ✨</div>", unsafe_allow_html=True)
 
# -----------------------------
# LEBENSMITTEL ERKENNUNG
# -----------------------------
with st.container():
    st.markdown("### 🍎 Lebensmittel erkennen")

    food_tab1, food_tab2, food_tab3 = st.tabs(["📷 Kamera", "📁 Upload", "✏️ Manuell"])
    image = None

    with food_tab1:
        cam = st.camera_input("Foto aufnehmen")
        if cam:
            image = Image.open(cam).convert("RGB")

    with food_tab2:
        up = st.file_uploader("Bild hochladen", type=["jpg", "png"])
        if up:
            image = Image.open(up).convert("RGB")

    with food_tab3:
        manual_food = st.text_input(
            "Lebensmittel eingeben",
            placeholder="z. B. Joghurt, Milch …"
        )
        if manual_food:
            st.session_state.food_item = manual_food

    # -----------------------------
    # IMAGE DISPLAY + PREDICTION
    # -----------------------------
    if image is not None:

        col_img, col_info = st.columns([1, 1])

        with col_img:
            try:
                st.image(image, use_container_width=True)
            except Exception:
                st.warning("Bild konnte nicht angezeigt werden")

        with col_info:
            with st.spinner("🔍 Erkenne Lebensmittel …"):
                result = classify_image(image)

            if result is None:
                st.warning("⚠️ Nicht erkannt. Bitte nochmal versuchen oder manuell eingeben.")
            else:
                st.session_state.food_item = result
                st.markdown("**Erkannt:**")
                st.markdown(
                    f"<div class='food-pill'>✅ {st.session_state.food_item}</div>",
                    unsafe_allow_html=True
                )

    elif st.session_state.food_item:
        st.markdown(
            f"<div class='food-pill'>✅ {st.session_state.food_item}</div>",
            unsafe_allow_html=True
        )

st.markdown("<hr>", unsafe_allow_html=True)
 
# -----------------------------
# MHD ERKENNUNG
# -----------------------------
with st.container():
    st.markdown("### 📅 Mindesthaltbarkeitsdatum")
 
    mhd_tab1, mhd_tab2, mhd_tab3 = st.tabs(["📷 Kamera", "📁 Upload", "✏️ Manuell"])
    mhd_image = None
 
    with mhd_tab1:
        cam_mhd = st.camera_input("MHD Foto aufnehmen")
        if cam_mhd:
            mhd_image = Image.open(cam_mhd)
 
    with mhd_tab2:
        up_mhd = st.file_uploader("MHD Bild hochladen", type=["jpg", "png"], key="mhd")
        if up_mhd:
            mhd_image = Image.open(up_mhd)
 
    with mhd_tab3:
        manual_mhd = st.text_input("Datum eingeben", placeholder="z. B. 31.12.2025")
        if manual_mhd:
            st.session_state.mhd_value = manual_mhd
 
    if mhd_image:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.image(mhd_image, use_container_width=True)
        with col_m2:
            if st.button("📅 Datum erkennen"):
                with st.spinner("🔍 Lese Datum …"):
                    st.session_state.mhd_value = extract_mhd(mhd_image)
                if st.session_state.mhd_value:
                    st.success(f"Erkannt: **{st.session_state.mhd_value}**")
                else:
                    st.warning("Kein Datum gefunden. Bitte manuell eingeben.")
 
    elif st.session_state.mhd_value:
        st.info(f"📅 MHD: **{st.session_state.mhd_value}**")
 
st.markdown("<hr>", unsafe_allow_html=True)
 
# -----------------------------
# SPEICHERN
# -----------------------------
with st.container():
    st.markdown("### 💾 Speichern")
 
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        if st.session_state.food_item:
            mhd_display = st.session_state.mhd_value or "kein MHD"
            st.markdown(f"🛒 **{st.session_state.food_item}** · 📅 {mhd_display}")
        else:
            st.markdown("_Noch kein Lebensmittel erkannt._")
 
    with col_btn:
        if st.session_state.food_item:
            if st.button("➕ Speichern", type="primary"):
                now = datetime.now() + timedelta(hours=2)
                mhd_clean = normalize_date(st.session_state.mhd_value)
                supabase.table("fridge_inventory").insert({
                    "food_name": st.session_state.food_item,
                    "mhd": mhd_clean,
                    "added_at": now.date().isoformat()
                }).execute()
                st.success("🎉 Gespeichert!")
                st.session_state.food_item = None
                st.session_state.mhd_value = None
                st.rerun()
 
st.markdown("<hr>", unsafe_allow_html=True)
 
# -----------------------------
# INVENTAR
# -----------------------------
st.markdown("### 📦 Mein Inventar")
 
data = supabase.table("fridge_inventory").select("*").execute().data
 
if data:
    def parse_date(v):
        try:
            return datetime.fromisoformat(v)
        except:
            return datetime.max
 
    data = sorted(data, key=lambda x: parse_date(x["mhd"]) if x["mhd"] else datetime.max)
 
    today = datetime.now().date()
 
    # ── Stats ──
    total = len(data)
    danger_count = 0
    warn_count = 0
    ok_count = 0
 
    for row in data:
        try:
            mhd_date = datetime.fromisoformat(row["mhd"]).date()
            diff = (mhd_date - today).days
            if diff <= 2:
                danger_count += 1
            elif diff <= 5:
                warn_count += 1
            else:
                ok_count += 1
        except:
            ok_count += 1
 
    st.markdown(f"""
    <div class='stats-bar'>
        <div class='stat-chip total'>📦 {total} Produkte</div>
        <div class='stat-chip danger'>🔴 {danger_count} Ablaufend</div>
        <div class='stat-chip warn'>🟠 {warn_count} Bald ablaufend</div>
        <div class='stat-chip ok'>🟢 {ok_count} Frisch</div>
    </div>
    """, unsafe_allow_html=True)
 
    # ── Header ──
    h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
    h1.markdown("**🍽 Lebensmittel**")
    h2.markdown("**📅 MHD**")
    h3.markdown("**➕ Hinzugefügt**")
    h4.markdown("")
 
    # ── Rows ──
    for row in data:
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
 
        added_date = str(row["added_at"]).split("T")[0]
 
        badge = ""
        row_style = ""
 
        try:
            mhd_date = datetime.fromisoformat(row["mhd"]).date()
            diff = (mhd_date - today).days
            if diff <= 2:
                badge = "🔴"
                row_style = "color:#c92a2a; font-weight:800;"
            elif diff <= 5:
                badge = "🟠"
                row_style = "color:#e67700; font-weight:700;"
            else:
                badge = "🟢"
                row_style = "color:#2f9e44;"
        except:
            badge = "⚪"
            row_style = "color:#555;"
 
        c1.markdown(f"<span style='{row_style}'>{badge} {row['food_name']}</span>", unsafe_allow_html=True)
        c2.markdown(f"<span style='{row_style}'>{row['mhd'] or '—'}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:#888;'>{added_date}</span>", unsafe_allow_html=True)
 
        if c4.button("🗑️", key=row["id"], help="Löschen"):
            supabase.table("fridge_inventory").delete().eq("id", row["id"]).execute()
            st.rerun()
 
else:
    st.markdown("""
    <div class='empty-state'>
        <span>🧺</span>
        Dein Kühlschrank ist noch leer.<br>Füge dein erstes Lebensmittel hinzu!
    </div>
    """, unsafe_allow_html=True)
