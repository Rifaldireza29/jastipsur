import streamlit as st
import datetime
import sqlite3
import streamlit.components.v1 as components

# Konfigurasi halaman
st.set_page_config(
    page_title="Jajan titip surya",
    page_icon="🍜",
    layout="wide"
)

# --- SETUP DATABASE SQLITE ---
def init_db():
    conn = sqlite3.connect("database_jajan.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            nama_pemesan TEXT,
            nama_menu TEXT,
            harga INTEGER,
            qty INTEGER,
            level TEXT,
            catatan TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_menu (
            tanggal TEXT,
            menu_id INTEGER,
            deadline_time TEXT,
            PRIMARY KEY (tanggal, menu_id)
        )
    """)
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# --- INISIALISASI SESSION STATE ---
if "current_cart" not in st.session_state:
    st.session_state.current_cart = []
if "show_payment_popup" not in st.session_state:
    st.session_state.show_payment_popup = False

# Daftar Menu Jajanan Diurutkan Sesuai Abjad (A - Z)
MENU_JAJANAN = [
    {
        "id": 8, 
        "nama": "Basreng", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "baso goyeng."
    },
    {
        "id": 17, 
        "nama": "Bola Bola Ayam", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "Bola-bola ayam gurih lezat."
    },
    {
        "id": 12, 
        "nama": "Cibay", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000], 
        "deskripsi": "Aci ngambay endul."
    },
    {
        "id": 4, 
        "nama": "Cilor", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "Cilor dekat mizan yang endul."
    },
    {
        "id": 18, 
        "nama": "Cilok", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "Cilok kenyal bumbu nikmat."
    },
    {
        "id": 7, 
        "nama": "Cireng ayam", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Cireng Ayam Ori", "harga": 2500},
            {"nama": "Cireng Ayam Pedas", "harga": 2500},
            {"nama": "Cireng Ayam Keju", "harga": 2500}
        ],
        "deskripsi": "hireng hanas aneka rasa."
    },
    {
        "id": 3, 
        "nama": "Dimsum", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Dimsum Ayam (Porsi 5rb)", "harga": 5000},
            {"nama": "Dimsum Ayam (Porsi 10rb)", "harga": 10000},
            {"nama": "Dimsum Campur (Porsi 5rb)", "harga": 5000},
            {"nama": "Dimsum Campur (Porsi 10rb)", "harga": 10000}
        ],
        "deskripsi": "dimsum ayam & campur aduk dijamin enak."
    },
    {
        "id": 1, 
        "nama": "Jambu Krisjon", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "Jambu kristal panghegar yang manis ituh."
    },
    {
        "id": 13, 
        "nama": "Kentang Goreng", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000], 
        "deskripsi": "French fries crispy."
    },
    {
        "id": 6, 
        "nama": "Kwetiaw", 
        "tipe_menu": "normal", 
        "pilihan_harga": [10000], 
        "deskripsi": "kwetiau harga pasar rasa restoran."
    },
    {
        "id": 9, 
        "nama": "Martabak Mini", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Pisang", "harga": 2500},
            {"nama": "Coklat", "harga": 2500},
            {"nama": "Keju", "harga": 3000},
            {"nama": "Pisang-Coklat", "harga": 3000},
            {"nama": "Pisang-Keju", "harga": 3000}
        ],
        "deskripsi": "Martabak mini manis aneka topping."
    },
    {
        "id": 16, 
        "nama": "Mie Goreng Ayam Penyet", 
        "tipe_menu": "normal", 
        "pilihan_harga": [15000], 
        "deskripsi": "Mie goreng dipadu ayam penyet gurih."
    },
    {
        "id": 14, 
        "nama": "Nasi Goreng", 
        "tipe_menu": "normal", 
        "pilihan_harga": [12000], 
        "deskripsi": "Nasi goreng mantap."
    },
    {
        "id": 15, 
        "nama": "Paket Komplit Ayam Penyet + Nasi", 
        "tipe_menu": "normal", 
        "pilihan_harga": [15000], 
        "deskripsi": "Ayam penyet komplit dengan nasi hangat."
    },
    {
        "id": 10, 
        "nama": "Pangsit Ayam", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Saos Bolognese Chilli Oil", "harga": 10000},
            {"nama": "Saos Keju Chilli Oil", "harga": 10000}
        ],
        "deskripsi": "Pangsit ayam gurih pedas nikmat."
    },
    {
        "id": 11, 
        "nama": "Risol Asin", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Mayo Ori", "harga": 3500},
            {"nama": "Mayo Pedas", "harga": 3500},
            {"nama": "Ayam Ori", "harga": 3500},
            {"nama": "Ayam Pedas", "harga": 3500},
            {"nama": "Coklat", "harga": 4000},
            {"nama": "Matcha", "harga": 4000}
        ],
        "deskripsi": "Risol aneka rasa asin & manis."
    },
    {
        "id": 2, 
        "nama": "Roti bakar yomart", 
        "tipe_menu": "varian", 
        "varian": [
            {"nama": "Coklat", "harga": 7000},
            {"nama": "Strawberry", "harga": 6000},
            {"nama": "Keju", "harga": 7000},
            {"nama": "Blueberry", "harga": 6000},
            {"nama": "Kacang", "harga": 6000},
            {"nama": "Coklat-Keju", "harga": 10000},
            {"nama": "Coklat-Kacang", "harga": 9500},
            {"nama": "Kacang-Strawberry", "harga": 8500}
        ],
        "deskripsi": "roti bakar yomart tea nu endul."
    },
    {
        "id": 5, 
        "nama": "Usus crispy", 
        "tipe_menu": "normal", 
        "pilihan_harga": [5000, 10000], 
        "deskripsi": "usus kabeuki gerri trusted enak banget."
    }
]

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

# --- TAMPILAN TAB BERDASARKAN PERAN ---
if is_admin:
    tab_form, tab_rekap, tab_admin_menu = st.tabs(["📝 Form Pesanan", "📊 Master Rekap Gabungan", "🛠️ Panel Kontrol Menu"])
else:
    tab_form = st.container()

# ================= TAB 1: FORM PESANAN MEMBER =================
with tab_form:
    if is_admin:
        st.markdown("### 🛠️ Mode Admin: Anda sedang melihat halaman member (Bebas akses)")
    
    st.markdown("### 1. 📋 Identitas & Tanggal Jajan")
    col_nama, col_tgl = st.columns(2)
    
    with col_nama:
        nama_pemesan = st.text_input("Nama Pemesan:", placeholder="Contoh: Surya / Rifaldy")
    with col_tgl:
        tanggal_jajan = st.date_input("Tanggal Jajan:", value=datetime.date.today(), key="member_tgl")

    st.markdown("---")
    st.markdown(f"### 2. 🛒 Pilih Menu yang Dibuka Admin untuk Tanggal: {tanggal_jajan}")

    # Cek menu aktif dan waktu deadline dari database
    cursor.execute("SELECT menu_id, deadline_time FROM active_menu WHERE tanggal = ?", (str(tanggal_jajan),))
    active_rows = cursor.fetchall()
    active_menu_ids = [r[0] for r in active_rows]
    deadline_str = active_rows[0][1] if active_rows and active_rows[0][1] else None

    # Menggunakan Zona Waktu WIB (UTC+7) secara pasti
    WIB = datetime.timezone(datetime.timedelta(hours=7))
    now_wib = datetime.datetime.now(WIB)

    is_expired = False
    if deadline_str:
        target_dt = datetime.datetime.combine(
            tanggal_jajan, 
            datetime.datetime.strptime(deadline_str, "%H:%M").time()
        ).replace(tzinfo=WIB)
        
        if now_wib > target_dt:
            is_expired = True

    # Tampilkan Live Countdown Timer interaktif berbasis JS
    if deadline_str and not is_expired:
        target_datetime_str = f"{tanggal_jajan}T{deadline_str}:00"
        timer_code = f"""
        <div style="background-color: #ff4b4b; padding: 12px; border-radius: 8px; color: white; text-align: center; font-family: sans-serif; font-weight: bold; margin-bottom: 15px;">
            ⏳ Sisa Waktu Pemesanan: <span id="live-timer" style="font-size: 1.2em; background: rgba(0,0,0,0.2); padding: 2px 8px; border-radius: 4px;">Memuat...</span>
        </div>
        <script>
            var targetDate = new Date("{target_datetime_str}").getTime();
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = targetDate - now;
                
                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("live-timer").innerHTML = "WAKTU HABIS!";
                    window.location.reload();
                }} else {{
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById("live-timer