import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Jajan titip surya",
    page_icon="🍜",
    layout="wide"
)

CONFIG_FILE = "config_menu.json"

# --- SETUP KONEKSI GOOGLE SHEETS (HANYA 1 SHEET: 'orders') ---
@st.cache_resource
def init_gspread():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Database_Jastipsur")
    return spreadsheet

try:
    sh = init_gspread()
    sheet_orders = sh.worksheet("orders")
    
    if len(sheet_orders.get_all_values()) == 0:
        sheet_orders.append_row(["id", "tanggal", "nama_pemesan", "nama_menu", "harga", "qty", "level", "catatan"])
except Exception as e:
    st.error(f"⚠️ Gagal terhubung ke Google Sheets. Pastikan file 'Database_Jastipsur' dan tab 'orders' sudah ada! Error: {e}")
    st.stop()

# --- FUNGSI CACHE DATA RECORDS (TTL 300 Detik) ---
@st.cache_data(ttl=300)
def get_cached_orders():
    return sheet_orders.get_all_records()

# --- DAFTAR MENU (MAKANAN & MINUMAN) ---
MENU_MAKANAN = [
    {"id": 8, "nama": "Basreng", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "baso goyeng."},
    {
        "id": 19, "nama": "Batagor", "tipe_menu": "varian",
        "varian": [{"nama": "Porsi 5rb", "harga": 5000}, {"nama": "Porsi 10rb", "harga": 10000}],
        "deskripsi": "Batagor gurih bumbu kacang mantap."
    },
    {"id": 17, "nama": "Bola Bola Ayam", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "Bola-bola ayam gurih lezat."},
    {"id": 12, "nama": "Cibay", "tipe_menu": "normal", "pilihan_harga": [5000], "deskripsi": "Aci ngambay endul."},
    {
        "id": 21, "nama": "Cimol Bojot", "tipe_menu": "varian",
        "varian": [
            {"nama": "Bojot Porsi Kecil", "harga": 6000},
            {"nama": "Bojot Porsi Besar", "harga": 12000},
            {"nama": "Moza Porsi Kecil", "harga": 10000},
            {"nama": "Moza Porsi Besar", "harga": 20000}
        ],
        "deskripsi": "Cimol bojot & moza aneka porsi pedas gurih."
    },
    {"id": 4, "nama": "Cilor", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "Cilor dekat mizan yang endul."},
    {"id": 18, "nama": "Cilok", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "Cilok kenyal bumbu nikmat."},
    {
        "id": 7, "nama": "Cireng ayam", "tipe_menu": "varian", 
        "varian": [{"nama": "Cireng Ayam Ori", "harga": 2500}, {"nama": "Cireng Ayam Pedas", "harga": 2500}, {"nama": "Cireng Ayam Keju", "harga": 2500}],
        "deskripsi": "hireng hanas aneka rasa."
    },
    {
        "id": 3, "nama": "Dimsum", "tipe_menu": "varian", 
        "varian": [{"nama": "Dimsum Ayam (Porsi 5rb)", "harga": 5000}, {"nama": "Dimsum Ayam (Porsi 10rb)", "harga": 10000}, {"nama": "Dimsum Campur (Porsi 5rb)", "harga": 5000}, {"nama": "Dimsum Campur (Porsi 10rb)", "harga": 10000}],
        "deskripsi": "dimsum ayam & campur aduk dijamin enak."
    },
    {"id": 1, "nama": "Jambu Krisjon", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "Jambu kristal panghegar yang manis ituh."},
    {"id": 13, "nama": "Kentang Goreng", "tipe_menu": "normal", "pilihan_harga": [5000], "deskripsi": "French fries crispy."},
    {"id": 6, "nama": "Kwetiaw", "tipe_menu": "normal", "pilihan_harga": [10000], "deskripsi": "kwetiau harga pasar rasa restoran."},
    {
        "id": 22, "nama": "Makaroni", "tipe_menu": "varian",
        "varian": [
            {"nama": "Makaroni Basah (Porsi 5rb)", "harga": 5000},
            {"nama": "Makaroni Basah (Porsi 10rb)", "harga": 10000},
            {"nama": "Makaroni Kering / Ngehe (Porsi 5rb)", "harga": 5000},
            {"nama": "Makaroni Kering / Ngehe (Porsi 10rb)", "harga": 10000}
        ],
        "deskripsi": "Makaroni basah atau kering gurih mantap."
    },
    {
        "id": 9, "nama": "Martabak Mini", "tipe_menu": "varian", 
        "varian": [{"nama": "Pisang", "harga": 2500}, {"nama": "Coklat", "harga": 2500}, {"nama": "Keju", "harga": 3000}, {"nama": "Pisang-Coklat", "harga": 3000}, {"nama": "Pisang-Keju", "harga": 3000}],
        "deskripsi": "Martabak mini manis aneka topping."
    },
    {"id": 16, "nama": "Mie Goreng Ayam Penyet", "tipe_menu": "normal", "pilihan_harga": [15000], "deskripsi": "Mie goreng dipadu ayam penyet gurih."},
    {"id": 14, "nama": "Nasi Goreng", "tipe_menu": "normal", "pilihan_harga": [12000], "deskripsi": "Nasi goreng mantap."},
    {"id": 15, "nama": "Paket Komplit Ayam Penyet + Nasi", "tipe_menu": "normal", "pilihan_harga": [15000], "deskripsi": "Ayam penyet komplit dengan nasi hangat."},
    {
        "id": 10, "nama": "Pangsit Ayam", "tipe_menu": "varian", 
        "varian": [{"nama": "Saos Bolognese Chilli Oil", "harga": 10000}, {"nama": "Saos Keju Chilli Oil", "harga": 10000}],
        "deskripsi": "Pangsit ayam gurih pedas nikmat."
    },
    {
        "id": 11, "nama": "Risol Asin", "tipe_menu": "varian", 
        "varian": [{"nama": "Mayo Ori", "harga": 3500}, {"nama": "Mayo Pedas", "harga": 3500}, {"nama": "Ayam Ori", "harga": 3500}, {"nama": "Ayam Pedas", "harga": 3500}, {"nama": "Coklat", "harga": 4000}, {"nama": "Matcha", "harga": 4000}],
        "deskripsi": "Risol aneka rasa asin & manis."
    },
    {
        "id": 2, "nama": "Roti bakar yomart", "tipe_menu": "varian", 
        "varian": [{"nama": "Coklat", "harga": 7000}, {"nama": "Strawberry", "harga": 7000}, {"nama": "Keju", "harga": 7000}, {"nama": "Blueberry", "harga": 7000}, {"nama": "Kacang", "harga": 7000}, {"nama": "Coklat-Keju", "harga": 9500}, {"nama": "Coklat-Kacang", "harga": 8500}, {"nama": "Kacang-Strawberry", "harga": 8500}],
        "deskripsi": "roti bakar yomart tea nu endul."
    },
    {
        "id": 20, "nama": "Rujak Buah", "tipe_menu": "varian",
        "varian": [{"nama": "Nanas + Pepaya + Mangga", "harga": 12000}, {"nama": "Campur", "harga": 12000}],
        "deskripsi": "Rujak buah segar bumbu pedas manis."
    },
    {"id": 5, "nama": "Usus crispy", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "usus kabeuki gerri trusted enak banget."}
]

MENU_MINUMAN = [
    {"id": 101, "nama": "Thaitea", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 102, "nama": "Greentea", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 103, "nama": "Coklat", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 104, "nama": "Taro", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 105, "nama": "Mangga", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 106, "nama": "Strawberry", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 107, "nama": "Vanilla Ori", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 108, "nama": "Vanilla Latte", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 109, "nama": "Cheese Cake", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 110, "nama": "Choco Oreo", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 111, "nama": "Buble Gum", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 112, "nama": "Red Velvet", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 113, "nama": "Cappucino Cincau", "small": 6000, "medium": 8000, "large": 10000},
    {"id": 114, "nama": "Milo", "small": None, "medium": 8000, "large": 10000},
    {"id": 115, "nama": "Milky Orange", "small": None, "medium": 8000, "large": 10000},
    {"id": 116, "nama": "Vanilla Oreo", "small": 8000, "medium": 10000, "large": 12000},
    {"id": 117, "nama": "Es Teh / Teh Ijo", "small": None, "medium": 5000, "large": 8000},
    {"id": 118, "nama": "Mangga Yakult", "small": None, "medium": 10000, "large": 13000},
    {"id": 119, "nama": "Orange Yakult", "small": None, "medium": 10000, "large": 13000},
    {"id": 120, "nama": "Leci Yakult", "small": None, "medium": 10000, "large": 13000},
    {"id": 121, "nama": "Strawberry Yakult", "small": None, "medium": 10000, "large": 13000},
    {"id": 122, "nama": "Lemon Yakult", "small": None, "medium": None, "large": 13000},
    {"id": 123, "nama": "Thai Lemon Tea", "small": None, "medium": None, "large": 10000},
    {"id": 124, "nama": "Green Lemon Tea", "small": None, "medium": None, "large": 10000},
    {"id": 125, "nama": "Orange Tea", "small": None, "medium": None, "large": 10000},
    {"id": 126, "nama": "Vanilla Lemon", "small": None, "medium": None, "large": 13000},
    {"id": 127, "nama": "Coffe Susu", "small": None, "medium": None, "large": 10000},
    {"id": 128, "nama": "Coffe Milo", "small": None, "medium": None, "large": 13000},
    {"id": 129, "nama": "Thai Mix Milo", "small": None, "medium": None, "large": 13000},
    {"id": 130, "nama": "Green Mix Milo", "small": None, "medium": None, "large": 13000},
    {"id": 131, "nama": "Boba Brown Sugar", "small": None, "medium": 10000, "large": None},
    {"id": 132, "nama": "Josu", "small": 6000, "medium": None, "large": 10000},
    {"id": 133, "nama": "Kubimsu", "small": 6000, "medium": None, "large": 10000}
]

MENU_JAJANAN = MENU_MAKANAN + MENU_MINUMAN

# --- FUNGSI LOAD & SAVE CONFIG LOKAL (JSON) ---
def load_system_config():
    default_time = datetime.time(20, 0)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                tgl = datetime.datetime.strptime(data.get("tanggal", str(datetime.date.today())), "%Y-%m-%d").date()
                ids = data.get("active_ids", [item["id"] for item in MENU_JAJANAN])
                time_str = data.get("batas_waktu", "20:00:00")
                b_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                return tgl, ids, b_time
        except:
            pass
    return datetime.date.today(), [item["id"] for item in MENU_JAJANAN], default_time

def save_system_config(tgl, ids, b_time):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "tanggal": str(tgl), 
                "active_ids": ids,
                "batas_waktu": b_time.strftime("%H:%M:%S")
            }, f)
    except Exception as e:
        st.warning(f"Gagal menyimpan config lokal: {e}")

# --- INISIALISASI SESSION STATE ---
if "current_cart" not in st.session_state:
    st.session_state.current_cart = []
if "show_payment_popup" not in st.session_state:
    st.session_state.show_payment_popup = False
if "editing_item_id" not in st.session_state:
    st.session_state.editing_item_id = None

saved_tgl, saved_ids, saved_time = load_system_config()
if "active_menu_date" not in st.session_state:
    st.session_state.active_menu_date = saved_tgl
if "active_menu_ids" not in st.session_state:
    st.session_state.active_menu_ids = saved_ids
if "active_batas_waktu" not in st.session_state:
    st.session_state.active_batas_waktu = saved_time

for item in MENU_JAJANAN:
    key_name = f"toggle_menu_{item['id']}"
    if key_name not in st.session_state:
        st.session_state[key_name] = item["id"] in st.session_state.active_menu_ids

# Header Aplikasi
st.title("🍜 Jajan Kuy - pengisian form jajan")
st.subheader("sok gewat atuh nge list best and bro, pilih tanggal tong poho!")
st.markdown("---")

# Sidebar Mode Admin / Member
st.sidebar.title("🔐 Mode Akses")
mode_akses = st.sidebar.radio("Pilih Peran:", ["Member (Pemesan)", "Admin (Surya)"])

is_admin = False
if mode_akses == "Admin (Surya)":
    st.sidebar.markdown("---")
    password_admin = st.sidebar.text_input("Password Admin:", type="password")
    
    if password_admin == "surya123": 
        is_admin = True
        st.sidebar.success("Mode Admin Aktif! 🔓")
    else:
        st.sidebar.warning("⚠️ Masukkan password admin yang benar.")

# --- RENDER KONTEN BERDASARKAN PERAN ---
if is_admin:
    tab_form, tab_rekap, tab_admin_menu = st.tabs(["📝 Form Pesanan", "📊 Master Rekap Gabungan", "🛠️ Panel Kontrol Menu"])
else:
    tab_form = st.container()
    tab_rekap = None
    tab_admin_menu = None

# ================= TAB 1: FORM PESANAN MEMBER =================
def render_form_pesanan():
    if is_admin:
        st.markdown("### 🛠️ Mode Admin: Anda sedang melihat halaman member (Bebas akses)")
    
    target_iso = datetime.datetime.combine(st.session_state.active_menu_date, st.session_state.active_batas_waktu).isoformat()
    formatted_time_str = st.session_state.active_batas_waktu.strftime('%H:%M')
    
    countdown_html = f"""
    <div style="padding: 12px 16px; background-color: #e8f4fd; border-radius: 8px; border-left: 5px solid #1f77b4; font-family: sans-serif; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-weight: bold; color: #1f77b4;">⏳ Batas Waktu Pemesanan ({st.session_state.active_menu_date}):</span>
            <span id="countdown" style="font-weight: bold; color: #d9534f; margin-left: 8px; font-size: 1.1em;">Menghitung waktu...</span>
        </div>
        <div style="color: #555; font-size: 0.9em;">
            (Pukul {formatted_time_str} WIB)
        </div>
    </div>

    <script>
    const targetDate = new Date("{target_iso}+07:00").getTime();

    function updateCountdown() {{
        const now = new Date().getTime();
        const distance = targetDate - now;

        const countdownElement = document.getElementById("countdown");

        if (distance < 0) {{
            countdownElement.innerHTML = "Waktu Pemesanan Telah Ditutup!";
            countdownElement.style.color = "red";
            return;
        }}

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        countdownElement.innerHTML = hours + " jam " + minutes + " menit " + seconds + " detik lagi";
    }}

    setInterval(updateCountdown, 1000);
    updateCountdown();
    </script>
    """
    components.html(countdown_html, height=65)

    wib_tz = datetime.timezone(datetime.timedelta(hours=7))
    now_wib = datetime.datetime.now(wib_tz)
    target_dt_wib = datetime.datetime.combine(st.session_state.active_menu_date, st.session_state.active_batas_waktu).replace(tzinfo=wib_tz)
    is_expired = (now_wib >= target_dt_wib) and not is_admin

    st.markdown("### 1. 📋 Identitas & Tanggal Jajan")
    col_nama, col_tgl = st.columns(2)
    
    with col_nama:
        nama_pemesan = st.text_input("Nama Pemesan:", placeholder="Contoh: Surya / Rifaldy")
    with col_tgl:
        tanggal_jajan = st.date_input("Tanggal Jajan:", value=datetime.date.today(), key="member_tgl")

    st.markdown("---")
    
    if (tanggal_jajan != st.session_state.active_menu_date and not is_admin) or is_expired:
        st.warning(f"⚠️ Form pemesanan ditutup atau tanggal berbeda. Jadwal aktif saat ini adalah tanggal **{st.session_state.active_menu_date}** (Batas pukul {formatted_time_str} WIB).")
        available_makanan = []
        available_minuman = []
    else:
        available_makanan = [item for item in MENU_MAKANAN if item["id"] in st.session_state.active_menu_ids]
        available_minuman = [item for item in MENU_MINUMAN if item["id"] in st.session_state.active_menu_ids]

    st.markdown(f"### 2. 🛒 Pilih Kategori & Menu untuk Tanggal: {tanggal_jajan}")

    try:
        all_data_raw = get_cached_orders()
    except:
        all_data_raw = []

    if not available_makanan and not available_minuman:
        st.warning("⚠️ Belum ada menu jajanan yang diaktifkan atau waktu pemesanan sudah berakhir.")
    else:
        kategori_pilihan = st.radio("Pilih Kategori:", ["🍔 Makanan", "🥤 Minuman (Maycha Thaitea & Boba)"], horizontal=True)

        if kategori_pilihan == "🍔 Makanan":
            if not available_makanan:
                st.info("Belum ada menu makanan yang aktif.")
            else:
                menu_options = [f"{item['nama']} - {item['deskripsi']}" for item in available_makanan]
                selected_menu_str = st.selectbox("Pilih Menu Makanan:", menu_options, key="sel_makanan")

                selected_idx = menu_options.index(selected_menu_str)
                item_terpilih = available_makanan[selected_idx]

                if item_terpilih["tipe_menu"] == "varian":
                    pilihan_varian = st.selectbox(
                        "Pilih Varian Rasa / Jenis:", 
                        item_terpilih["varian"], 
                        format_func=lambda x: f"{x['nama']} (Rp {x['harga']:,})"
                    )
                    nama_pesanan_final = f"{item_terpilih['nama']} - {pilihan_varian['nama']}"
                    harga_final = pilihan_varian["harga"]
                else:
                    if len(item_terpilih["pilihan_harga"]) > 1:
                        pilihan_harga_pilih = st.radio(
                            "Pilih Varian Harga:", 
                            item_terpilih["pilihan_harga"], 
                            format_func=lambda x: f"Rp {x:,}"
                        )
                    else:
                        pilihan_harga_pilih = item_terpilih["pilihan_harga"][0]
                        st.write(f"**Harga:** Rp {pilihan_harga_pilih:,}")
                    
                    nama_pesanan_final = f"{item_terpilih['nama']} (Rp {pilihan_harga_pilih:,})"
                    harga_final = pilihan_harga_pilih

                col_qty, col_level = st.columns(2)
                with col_qty:
                    jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1, key="qty_mkn")
                with col_level:
                    level_pedas = st.selectbox("Level Pedas (Opsional):", ["-", "Tidak Pedas", "Pedes Dikit", "Pedas Sedang", "Pedasssss"], key="lvl_mkn")

                catatan_item = st.text_input("Catatan Khusus (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng", key="cat_mkn")

                if st.button("➕ Tambah ke Daftar Pesanan Saya", key="btn_add_mkn"):
                    st.session_state.current_cart.append({
                        "nama_menu": nama_pesanan_final,
                        "harga": harga_final,
                        "qty": jumlah_pesan,
                        "level": level_pedas,
                        "catatan": catatan_item if catatan_item else "-"
                    })
                    st.toast(f"Berhasil menambahkan {nama_pesanan_final}!")

        else: # KATEGORI MINUMAN
            if not available_minuman:
                st.info("Belum ada menu minuman yang aktif.")
            else:
                minuman_options = [item['nama'] for item in available_minuman]
                selected_minuman_str = st.selectbox("Pilih Menu Minuman:", minuman_options, key="sel_minum")

                drink_obj = next((item for item in available_minuman if item['nama'] == selected_minuman_str), None)

                if drink_obj:
                    available_sizes = []
                    if drink_obj["small"] is not None:
                        available_sizes.append("Small")
                    if drink_obj["medium"] is not None:
                        available_sizes.append("Medium")
                    if drink_obj["large"] is not None:
                        available_sizes.append("Large")

                    selected_size = st.radio("Pilih Ukuran Cup:", available_sizes, horizontal=True, key="radio_size")

                    if selected_size == "Small":
                        base_price = drink_obj["small"]
                    elif selected_size == "Medium":
                        base_price = drink_obj["medium"]
                    else:
                        base_price = drink_obj["large"]

                    st.write(f"**Harga Ukuran {selected_size}:** Rp {base_price:,}")

                    free_topping = st.selectbox("Pilih Free Topping (Gratis):", ["Boba / Buble", "Jelly", "Nutrijel"], key="free_top")

                    extra_options = st.multiselect(
                        "Pilih Extra Topping (Opsional - Berbayar):", 
                        ["Boba Meletus (+Rp 3.000)", "Cream Cheese (+Rp 3.000)", "Oreo (+Rp 2.000)", "Cincau (+Rp 2.000)"],
                        key="extra_top"
                    )

                    extra_price_total = 0
                    extra_names = []
                    for ext in extra_options:
                        if "Boba Meletus" in ext or "Cream Cheese" in ext:
                            extra_price_total += 3000
                        else:
                            extra_price_total += 2000
                        extra_names.append(ext.split(" (+")[0])

                    final_drink_price = base_price + extra_price_total

                    topping_str = f"Free: {free_topping}"
                    if extra_names:
                        topping_str += f" | Extra: {', '.join(extra_names)}"

                    nama_pesanan_minuman_final = f"{drink_obj['nama']} ({selected_size}) - [{topping_str}]"

                    col_q_minum, col_lvl_minum = st.columns(2)
                    with col_q_minum:
                        jumlah_minum = st.number_input("Jumlah Gelas:", min_value=1, max_value=20, value=1, key="qty_minum")
                    with col_lvl_minum:
                        gula_es = st.selectbox("Catatan Es / Manis:", ["Normal Ice / Normal Sweet", "Less Ice", "No Ice", "Less Sugar"], key="gula_es")

                    catatan_minum = st.text_input("Catatan Khusus Minuman (Opsional):", placeholder="Contoh: Plastik dipisah", key="cat_minum")

                    if st.button("➕ Tambah Minuman ke Daftar Pesanan Saya", key="btn_add_minum"):
                        st.session_state.current_cart.append({
                            "nama_menu": nama_pesanan_minuman_final,
                            "harga": final_drink_price,
                            "qty": jumlah_minum,
                            "level": gula_es,
                            "catatan": catatan_minum if catatan_minum else "-"
                        })
                        st.toast(f"Berhasil menambahkan {drink_obj['nama']}!")

    st.markdown("---")
    st.markdown("### 🧾 Preview Pesanan Kamu")

    if not st.session_state.current_cart:
        st.info("Belum ada menu yang ditambahkan.")
    else:
        subtotal_menu = 0
        for idx, cart_item in enumerate(st.session_state.current_cart):
            sub = cart_item["harga"] * cart_item["qty"]
            subtotal_menu += sub
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{cart_item['nama_menu']}** (x{cart_item['qty']}) - Note: {cart_item['level']}")
            c2.write(f"Catatan: {cart_item['catatan']}")
            c3.write(f"Rp {sub:,}")
            if st.button("Hapus Item", key=f"del_cart_{idx}"):
                st.session_state.current_cart.pop(idx)
                st.rerun()

        biaya_jastip = 1000
        total_biaya_akhir = subtotal_menu + biaya_jastip

        st.markdown(f"Subtotal Menu: Rp {subtotal_menu:,}")
        st.markdown(f"Biaya Jastip: Rp {biaya_jastip:,}")
        st.markdown(f"### Total Biaya Kesimpulan (Termasuk Jastip): **Rp {total_biaya_akhir:,}**")

        if st.button("🚀 Simpan & Masukkan ke Rekap Utama"):
            if not nama_pemesan:
                st.error("Mohon isi Nama Pemesan terlebih dahulu!")
            else:
                new_id = len(all_data_raw) + 1

                for cart_item in st.session_state.current_cart:
                    sheet_orders.append_row([
                        new_id,
                        str(tanggal_jajan),
                        nama_pemesan,
                        cart_item["nama_menu"],
                        int(cart_item["harga"]),
                        int(cart_item["qty"]),
                        cart_item["level"],
                        cart_item["catatan"]
                    ])
                    new_id += 1

                sheet_orders.append_row([
                    new_id,
                    str(tanggal_jajan),
                    nama_pemesan,
                    "Biaya Jastip",
                    int(biaya_jastip),
                    1,
                    "-",
                    ""
                ])

                st.session_state.last_total_pay = total_biaya_akhir
                st.session_state.last_nama_pay = nama_pemesan
                st.session_state.show_payment_popup = True
                
                st.session_state.current_cart = []
                st.success("Yeay! Pesanan berhasil disimpan ke Google Sheets.")
                st.balloons()
                st.rerun()

    if st.session_state.show_payment_popup:
        st.markdown("---")
        st.info(f"🎉 **Terima kasih, {st.session_state.last_nama_pay}!** Pesanan kamu sudah tercatat.")
        st.markdown(f"### 💰 Total tagihan pribadi kamu (Sudah termasuk Jastip Rp 1.000): **Rp {st.session_state.last_total_pay:,}**")
        
        pilihan_bayar = st.radio("Mau langsung bayar sekarang atau nanti?", ["Bayar Sekarang (Scan QRIS)", "Nanti Saja"], key="radio_pilih_bayar")
        
        if pilihan_bayar == "Bayar Sekarang (Scan QRIS)":
            st.markdown("#### 💳 Scan QRIS Jastip - Rezha Surya Rifaldy")
            try:
                st.image("qr_jastipsur.jpeg", width=280, caption="QRIS Jastip - Rezha Surya Rifaldy")
            except Exception:
                st.warning("⚠️ File gambar `qr_jastipsur.jpeg` belum dimasukkan ke folder kodingan.")
            st.info("Silakan transfer sesuai nominal total belanjaan kamu di atas, lalu kirim bukti transfer ke Surya ya!")
            
        if st.button("✅ Selesai / Tutup Menu Pembayaran"):
            st.session_state.show_payment_popup = False
            st.rerun()

# ================= TAB 2: MASTER REKAP GABUNGAN =================
def render_master_rekap():
    if "editing_item_id" not in st.session_state:
        st.session_state.editing_item_id = None

    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown("### 📊 Rekapitulasi Pesanan (Admin)")
    with col_btn:
        if st.button("🔄 Refresh Data Rekap"):
            st.cache_data.clear()
            st.rerun()
    
    try:
        orders_data_raw = get_cached_orders()
    except:
        orders_data_raw = []
    
    all_orders_db = []
    for r in orders_data_raw:
        r_lower = {str(k).lower().strip().replace(" ", "_"): v for k, v in r.items() if k is not None}
        if r_lower.get("nama_pemesan") and r_lower.get("nama_menu"):
            try:
                all_orders_db.append({
                    "id": int(r_lower.get("id", 0) or 0),
                    "tanggal": str(r_lower.get("tanggal", "")),
                    "nama_pemesan": str(r_lower.get("nama_pemesan", "")),
                    "nama_menu": str(r_lower.get("nama_menu", "")),
                    "harga": int(r_lower.get("harga", 0) or 0),
                    "qty": int(r_lower.get("qty", 1) or 1),
                    "level": str(r_lower.get("level", "-")),
                    "catatan": str(r_lower.get("catatan", ""))
                })
            except:
                pass

    if not all_orders_db:
        st.info("Belum ada data pesanan yang masuk di Google Sheet.")
    else:
        if st.button("🗑️ Reset / Hapus Semua Rekap Spreadsheet"):
            sheet_orders.clear()
            sheet_orders.append_row(["id", "tanggal", "nama_pemesan", "nama_menu", "harga", "qty", "level", "catatan"])
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        
        unique_dates = sorted(list(set(order["tanggal"] for order in all_orders_db if order["tanggal"])), reverse=True)
        filter_options = ["🌐 Semua Tanggal (Continue)"] + unique_dates

        st.markdown("#### 🔍 Filter Berdasarkan Tanggal:")
        selected_filter = st.selectbox(
            "Pilih Tanggal Rekap:",
            options=filter_options,
            key="admin_filter_date_v14"
        )
        
        st.markdown("---")

        if selected_filter == "🌐 Semua Tanggal (Continue)":
            dates_to_render = unique_dates
        else:
            dates_to_render = [selected_filter]

        for tgl in dates_to_render:
            st.markdown(f"### 📅 Tanggal: {tgl}")
            orders_on_date = [o for o in all_orders_db if o["tanggal"] == tgl]
            
            grouped_by_person = {}
            for ord_data in orders_on_date:
                nama = ord_data["nama_pemesan"]
                if nama not in grouped_by_person:
                    grouped_by_person[nama] = []
                grouped_by_person[nama].append(ord_data)

            total_biaya_tgl = 0
            no_urut = 1

            st.markdown("#### 📋 Tabel Master Pesanan:")
            
            header_cols = st.columns([0.4, 1.8, 2.5, 1.2, 0.6, 1.4, 2.2, 2.2, 1.0])
            header_cols[0].markdown("**No**")
            header_cols[1].markdown("**Pemesan**")
            header_cols[2].markdown("**Menu / Item**")
            header_cols[3].markdown("**Harga**")
            header_cols[4].markdown("**Qty**")
            header_cols[5].markdown("**Level**")
            header_cols[6].markdown("**Catatan**")
            header_cols[7].markdown("**Subtotal**")
            header_cols[8].markdown("**Aksi**")
            st.markdown("<hr style='margin: 4px 0px;'>", unsafe_allow_html=True)

            for nama, items in grouped_by_person.items():
                menu_items = [i for i in items if i["nama_menu"] != "Biaya Jastip"]
                
                subtotal_murni_makanan = sum([i["harga"] * i["qty"] for i in menu_items])
                subtotal_orang_dengan_jastip = subtotal_murni_makanan + 1000
                total_biaya_tgl += subtotal_orang_dengan_jastip

                for idx, m_item in enumerate(menu_items):
                    harga_satuan_str = f"Rp {m_item['harga']:,}"
                    
                    display_no = str(no_urut) if idx == 0 else ""
                    display_nama = nama if idx == 0 else ""
                    
                    is_last_item = (idx == len(menu_items) - 1)
                    if is_last_item:
                        subtotal_text = f"**Rp {subtotal_orang_dengan_jastip:,} (sdh jastip)**"
                    else:
                        subtotal_text = ""

                    row_cols = st.columns([0.4, 1.8, 2.5, 1.2, 0.6, 1.4, 2.2, 2.2, 1.0])
                    row_cols[0].write(display_no)
                    row_cols[1].write(display_nama)
                    row_cols[2].write(m_item["nama_menu"])
                    row_cols[3].write(harga_satuan_str)
                    row_cols[4].write(str(m_item["qty"]))
                    row_cols[5].write(m_item["level"])
                    row_cols[6].write(m_item["catatan"])
                    row_cols[7].write(subtotal_text)
                    
                    with row_cols[8]:
                        col_edit_btn, col_del_btn = st.columns(2)
                        with col_edit_btn:
                            if st.button("✏️", key=f"edit_btn_{tgl}_{nama}_{idx}_{m_item['id']}", help="Edit atau Tambah Menu"):
                                st.session_state.editing_item_id = m_item['id']
                                st.rerun()
                        with col_del_btn:
                            if st.button("❌", key=f"del_btn_{tgl}_{nama}_{idx}_{m_item['id']}", help="Hapus Item Ini"):
                                cell = sheet_orders.find(str(m_item['id']))
                                if cell:
                                    sheet_orders.delete_rows(cell.row)
                                st.cache_data.clear()
                                st.rerun()

                    # --- FORM EDIT PESANAN & TAMBAH MENU BARU DI DALAM BARIS ITEM ---
                    if st.session_state.editing_item_id == m_item['id']:
                        with st.form(key=f"form_edit_{m_item['id']}"):
                            st.markdown(f"### 🛠️ Edit Pesanan ID #{m_item['id']} ({nama})")
                            st.markdown("*Ubah detail item yang ada di bawah ini:*")
                            
                            new_menu_edit = st.text_input("Nama Menu:", value=m_item['nama_menu'])
                            c_e1, c_e2 = st.columns(2)
                            with c_e1:
                                new_harga_edit = st.number_input("Harga Satuan (Rp):", value=int(m_item['harga']), step=500)
                                new_qty_edit = st.number_input("Qty:", min_value=1, max_value=20, value=int(m_item['qty']))
                            with c_e2:
                                new_level_edit = st.text_input("Level:", value=m_item['level'])
                                new_catatan_edit = st.text_input("Catatan:", value=m_item['catatan'])
                            
                            st.markdown("---")
                            st.markdown(f"#### ➕ Atau Mau Sekalian Tambah Menu Baru untuk **{nama}**?")
                            
                            active_menu_list = [item for item in MENU_JAJANAN if item["id"] in st.session_state.active_menu_ids]
                            if not active_menu_list:
                                active_menu_list = MENU_JAJANAN
                            
                            add_menu_options = ["- Tidak Menambah Menu Baru -"] + [f"{item['nama']}" for item in active_menu_list]
                            chosen_add_str = st.selectbox("Pilih Menu Tambahan (Sesuai Menu Aktif):", add_menu_options, key=f"sub_add_menu_{m_item['id']}")
                            
                            sub_added_menu_name = None
                            sub_added_price = 0
                            sub_added_qty = 1
                            sub_added_level = "-"
                            sub_added_catatan = "-"

                            if chosen_add_str != "- Tidak Menambah Menu Baru -":
                                sub_added_menu_name = chosen_add_str
                                sub_added_price = st.number_input("Harga Tambahan (Rp):", value=5000, step=500, key=f"sub_add_prc_{m_item['id']}")
                                c_sa1, c_sa2 = st.columns(2)
                                with c_sa1:
                                    sub_added_qty = st.number_input("Qty Tambahan:", min_value=1, max_value=20, value=1, key=f"sub_add_q_{m_item['id']}")
                                with c_sa2:
                                    sub_added_level = st.text_input("Level/Catatan Tambahan:", value="-", key=f"sub_add_l_{m_item['id']}")
                                sub_added_catatan = st.text_input("Catatan Tambahan:", placeholder="Contoh: Kuah dipisah", key=f"sub_add_c_{m_item['id']}")

                            st.markdown("---")
                            col_submit_edit, col_cancel_edit = st.columns(2)
                            with col_submit_edit:
                                submit_change = st.form_submit_button("💾 Simpan Perubahan")
                            with col_cancel_edit:
                                cancel_change = st.form_submit_button("❌ Batal")

                            if submit_change:
                                cell = sheet_orders.find(str(m_item['id']))
                                if cell:
                                    sheet_orders.update_cell(cell.row, 4, new_menu_edit)
                                    sheet_orders.update_cell(cell.row, 5, int(new_harga_edit))
                                    sheet_orders.update_cell(cell.row, 6, int(new_qty_edit))
                                    sheet_orders.update_cell(cell.row, 7, new_level_edit)
                                    sheet_orders.update_cell(cell.row, 8, new_catatan_edit)
                                
                                if chosen_add_str != "- Tidak Menambah Menu Baru -" and sub_added_menu_name:
                                    fresh_orders_check = get_cached_orders()
                                    new_id = len(fresh_orders_check) + 1
                                    sheet_orders.append_row([
                                        new_id,
                                        tgl,
                                        nama,
                                        sub_added_menu_name,
                                        int(sub_added_price),
                                        int(sub_added_qty),
                                        sub_added_level,
                                        sub_added_catatan if sub_added_catatan else "-"
                                    ])

                                st.session_state.editing_item_id = None
                                st.cache_data.clear()
                                st.success("✅ Pesanan berhasil diperbarui & menu tambahan berhasil disimpan!")
                                st.rerun()

                            if cancel_change:
                                st.session_state.editing_item_id = None
                                st.rerun()

                no_urut += 1
                st.markdown("<hr style='border: 0.5px solid #eee; margin: 2px 0px;'>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"### 💰 Total Uang Masuk Tanggal {tgl}: **Rp {total_biaya_tgl:,}**")
            
            # --- PEMISAHAN REKAP MAKANAN & MINUMAN ---
            summary_makanan = {}
            summary_minuman = {}
            
            list_nama_minuman = [
                "Thaitea", "Greentea", "Coklat", "Taro", "Mangga", "Strawberry", 
                "Vanilla Ori", "Vanilla Latte", "Cheese Cake", "Choco Oreo", "Buble Gum", 
                "Red Velvet", "Cappucino Cincau", "Milo", "Milky Orange", "Vanilla Oreo", 
                "Es Teh / Teh Ijo", "Mangga Yakult", "Orange Yakult", "Leci Yakult", 
                "Strawberry Yakult", "Lemon Yakult", "Thai Lemon Tea", "Green Lemon Tea", 
                "Orange Tea", "Vanilla Lemon", "Coffe Susu", "Coffe Milo", "Thai Mix Milo", 
                "Green Mix Milo", "Boba Brown Sugar", "Josu", "Kubimsu"
            ]

            for ord_data in orders_on_date:
                m_name = ord_data["nama_menu"]
                if m_name != "Biaya Jastip":
                    m_qty = ord_data["qty"]
                    m_pemesan = ord_data["nama_pemesan"]
                    
                    is_minuman = any(m_name.startswith(minum) for minum in list_nama_minuman)
                    target_dict = summary_minuman if is_minuman else summary_makanan
                    
                    if m_name not in target_dict:
                        target_dict[m_name] = {"total_qty": 0, "pemesan_list": []}
                    
                    target_dict[m_name]["total_qty"] += m_qty
                    target_dict[m_name]["pemesan_list"].append(f"{m_pemesan} ({m_qty})")
            
            # 1. Rekap Makanan
            st.markdown("#### 🍔 Rekap Total Porsi Makanan (Urut A-Z):")
            if summary_makanan:
                sorted_summary_makanan = sorted(summary_makanan.items())
                for menu_name, data_val in sorted_summary_makanan:
                    gabungan_nama = ", ".join(data_val["pemesan_list"])
                    st.write(f"- **{menu_name}**: total **{data_val['total_qty']} porsi** — *({gabungan_nama})*")
            else:
                st.write("- Belum ada porsi makanan.")

            st.markdown("")

            # 2. Rekap Minuman
            st.markdown("#### 🥤 Rekap Total Porsi Minuman (Urut A-Z):")
            if summary_minuman:
                sorted_summary_minuman = sorted(summary_minuman.items())
                for menu_name, data_val in sorted_summary_minuman:
                    gabungan_nama = ", ".join(data_val["pemesan_list"])
                    st.write(f"- **{menu_name}**: total **{data_val['total_qty']} porsi** — *({gabungan_nama})*")
            else:
                st.write("- Belum ada porsi minuman.")
            
            st.markdown("====================")

# ================= TAB 3: PANEL KONTROL MENU ADMIN =================
def render_panel_kontrol():
    st.markdown("## 🛠️ Panel Kontrol Admin (Pengaturan Jadwal & Menu)")
    st.info("💡 Atur tanggal, batas waktu tutup pesanan, dan centang menu jajanan yang ingin dibuka.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        selected_control_date = st.date_input("📅 Set Tanggal Jajan Aktif:", value=st.session_state.active_menu_date, key="control_date_input")
    with col_c2:
        selected_control_time = st.time_input("⏰ Set Batas Jam Tutup Order (WIB):", value=st.session_state.active_batas_waktu, key="control_time_input")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Pilih Semua Menu"):
            for item in MENU_JAJANAN:
                st.session_state[f"toggle_menu_{item['id']}"] = True
            st.rerun()
    with col_btn2:
        if st.button("❌ Kosongkan / Matikan Semua"):
            for item in MENU_JAJANAN:
                st.session_state[f"toggle_menu_{item['id']}"] = False
            st.rerun()

    st.markdown("---")
    
    st.markdown("#### 🍔 Menu Makanan")
    for item in MENU_MAKANAN:
        key_name = f"toggle_menu_{item['id']}"
        st.checkbox(f"**{item['nama']}** — *{item['deskripsi']}*", key=key_name)

    st.markdown("---")

    st.markdown("#### 🥤 Menu Minuman (Maycha Thaitea & Boba)")
    all_minuman_active = all(st.session_state.get(f"toggle_menu_{item['id']}", False) for item in MENU_MINUMAN)
    
    Master_minuman_toggle = st.checkbox("🌟 **[MASTER] Aktifkan / Nonaktifkan Semua Menu Minuman**", value=all_minuman_active, key="master_minuman_checkbox")
    
    if Master_minuman_toggle != all_minuman_active:
        for item in MENU_MINUMAN:
            st.session_state[f"toggle_menu_{item['id']}"] = Master_minuman_toggle
        st.rerun()

    with st.expander("📂 Lihat / Atur Detail Menu Minuman Satuan (Opsional)"):
        for item in MENU_MINUMAN:
            key_name = f"toggle_menu_{item['id']}"
            st.checkbox(f"**{item['nama']}** (S: {item['small']}, M: {item['medium']}, L: {item['large']})", key=key_name)
            
    st.markdown("---")
    if st.button("💾 Simpan Pengaturan Jadwal & Menu"):
        new_active = []
        for item in MENU_JAJANAN:
            if st.session_state.get(f"toggle_menu_{item['id']}", False):
                new_active.append(item["id"])
        
        save_system_config(selected_control_date, new_active, selected_control_time)

        st.session_state.active_menu_date = selected_control_date
        st.session_state.active_batas_waktu = selected_control_time
        st.session_state.active_menu_ids = new_active
        st.cache_data.clear()
        st.success("✅ Tanggal, batas waktu (WIB), dan pengaturan menu berhasil disimpan permanen!")
        st.rerun()

# --- PENEMPATAN KONTEN KE DALAM TAB ---
if is_admin:
    with tab_form:
        render_form_pesanan()
    with tab_rekap:
        render_master_rekap()
    with tab_admin_menu:
        render_panel_kontrol()
else:
    render_form_pesanan()