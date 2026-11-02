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
        sheet_orders.append_row(["id", "tanggal", "nama_pemesan", "nama_menu", "harga", "qty", "level", "catatan", "status_lunas"])
except Exception as e:
    st.error(f"⚠️ Gagal terhubung ke Google Sheets. Pastikan file 'Database_Jastipsur' dan tab 'orders' sudah ada! Error: {e}")
    st.stop()

# --- FUNGSI CACHE DATA RECORDS (TTL 300 Detik) ---
@st.cache_data(ttl=300)
def get_cached_orders():
    return sheet_orders.get_all_records()

# Daftar Menu Jajanan Diurutkan Sesuai Abjad (A - Z) Beserta Menu Baru
MENU_JAJANAN = [
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
        st.session_state[key_name] = item["id"] in st.session_state.active_menu