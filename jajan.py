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

# --- FUNGSI CACHE DATA RECORDS (TTL 60 Detik agar terhindar dari Error 429) ---
@st.cache_data(ttl=300)
def get_cached_orders():
    return sheet_orders.get_all_records()

# Daftar Menu Jajanan Diurutkan Sesuai Abjad (A - Z)
MENU_JAJANAN = [
    {"id": 8, "nama": "Basreng", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "baso goyeng."},
    {"id": 17, "nama": "Bola Bola Ayam", "tipe_menu": "normal", "pilihan_harga": [5000, 10000], "deskripsi": "Bola-bola ayam gurih lezat."},
    {"id": 12, "nama": "Cibay", "tipe_menu": "normal", "pilihan_harga": [5000], "deskripsi": "Aci ngambay endul."},
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
    
    # --- LIVE COUNTDOWN ANIMATION (WIB / UTC+07:00) ---
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
        available_menu = []
    else:
        available_menu = [item for item in MENU_JAJANAN if item["id"] in st.session_state.active_menu_ids]

    st.markdown(f"### 2. 🛒 Pilih Menu untuk Tanggal: {tanggal_jajan}")

    try:
        all_data_raw = get_cached_orders()
    except:
        all_data_raw = []

    if not available_menu:
        st.warning("⚠️ Belum ada menu jajanan yang diaktifkan atau waktu pemesanan sudah berakhir.")
    else:
        menu_options = [f"{item['nama']} - {item['deskripsi']}" for item in available_menu]
        selected_menu_str = st.selectbox("Pilih Menu Jajanan:", menu_options)

        selected_idx = menu_options.index(selected_menu_str)
        item_terpilih = available_menu[selected_idx]

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
            jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1)
        with col_level:
            level_pedas = st.selectbox("Level Pedas (Opsional):", ["-", "Tidak Pedas", "Pedes Dikit", "Pedas Sedang", "Pedasssss"])

        catatan_item = st.text_input("Catatan Khusus (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng, kuah dipisah, dll.")

        if st.button("➕ Tambah ke Daftar Pesanan Saya"):
            st.session_state.current_cart.append({
                "nama_menu": nama_pesanan_final,
                "harga": harga_final,
                "qty": jumlah_pesan,
                "level": level_pedas,
                "catatan": catatan_item if catatan_item else "-"
            })
            st.toast(f"Berhasil menambahkan {nama_pesanan_final}!")

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
            c1.write(f"**{cart_item['nama_menu']}** (x{cart_item['qty']}) - Level: {cart_item['level']}")
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
                        cart_item["catatan"],
                        "Belum Lunas"
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
                    "",
                    "Belum Lunas"
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
            st.markdown("#### 💳 Scan QRIS BCA - Rezha Surya Rifaldy")
            try:
                st.image("qr_bca.jpeg", width=280, caption="QRIS BCA - Rezha Surya Rifaldy")
            except Exception:
                st.warning("⚠️ File gambar `qr_bca.jpeg` belum dimasukkan ke folder kodingan.")
            st.info("Silakan transfer sesuai nominal total belanjaan kamu di atas, lalu kirim bukti transfer ke Surya ya!")
            
        if st.button("✅ Selesai / Tutup Menu Pembayaran"):
            st.session_state.show_payment_popup = False
            st.rerun()

# ================= TAB 2: MASTER REKAP GABUNGAN (KHUSUS ADMIN) =================
def render_master_rekap():
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown("### 📊 Rekapitulasi Gabungan Seluruh Pesanan (Eksklusif Admin)")
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
                    "catatan": str(r_lower.get("catatan", "")),
                    "status_lunas": str(r_lower.get("status_lunas", "Belum Lunas"))
                })
            except:
                pass

    if not all_orders_db:
        st.info("Belum ada data pesanan yang masuk di Google Sheet.")
    else:
        if st.button("🗑️ Reset / Hapus Semua Rekap Spreadsheet"):
            sheet_orders.clear()
            sheet_orders.append_row(["id", "tanggal", "nama_pemesan", "nama_menu", "harga", "qty", "level", "catatan", "status_lunas"])
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        
        unique_dates = sorted(list(set(order["tanggal"] for order in all_orders_db if order["tanggal"])))

        for tgl in unique_dates:
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

            st.markdown("#### 📋 Tabel Master Semua Pesanan:")
            
            header_cols = st.columns([0.4, 1.5, 1.8, 2.2, 1.0, 0.5, 1.2, 2.0, 2.2, 0.8])
            header_cols[0].markdown("**No**")
            header_cols[1].markdown("**Pemesan**")
            header_cols[2].markdown("**Status**")
            header_cols[3].markdown("**Menu / Item**")
            header_cols[4].markdown("**Harga**")
            header_cols[5].markdown("**Qty**")
            header_cols[6].markdown("**Level**")
            header_cols[7].markdown("**Catatan**")
            header_cols[8].markdown("**Subtotal**")
            header_cols[9].markdown("**Aksi**")
            st.markdown("<hr style='margin: 4px 0px;'>", unsafe_allow_html=True)

            for nama, items in grouped_by_person.items():
                menu_items = [i for i in items if i["nama_menu"] != "Biaya Jastip"]
                
                subtotal_murni_makanan = sum([i["harga"] * i["qty"] for i in menu_items])
                subtotal_orang_dengan_jastip = subtotal_murni_makanan + 1000
                total_biaya_tgl += subtotal_orang_dengan_jastip

                is_currently_lunas = items[0]["status_lunas"] == "Lunas" if items else False

                for idx, m_item in enumerate(menu_items):
                    harga_satuan_str = f"Rp {m_item['harga']:,}"
                    
                    display_no = str(no_urut) if idx == 0 else ""
                    display_nama = nama if idx == 0 else ""
                    
                    is_last_item = (idx == len(menu_items) - 1)
                    if is_last_item:
                        subtotal_text = f"**Rp {subtotal_orang_dengan_jastip:,} (sdh jastip)**"
                    else:
                        subtotal_text = ""

                    row_cols = st.columns([0.4, 1.5, 1.8, 2.2, 1.0, 0.5, 1.2, 2.0, 2.2, 0.8])
                    row_cols[0].write(display_no)
                    row_cols[1].write(display_nama)
                    
                    if idx == 0:
                        with row_cols[2]:
                            ubah_lunas = st.checkbox("Lunas", value=is_currently_lunas, key=f"chk_lunas_{tgl}_{nama}")
                            if ubah_lunas != is_currently_lunas:
                                status_str = "Lunas" if ubah_lunas else "Belum Lunas"
                                for item_grup in items:
                                    cell = sheet_orders.find(str(item_grup['id']))
                                    if cell:
                                        sheet_orders.update_cell(cell.row, 9, status_str)
                                st.cache_data.clear()
                                st.rerun()
                    else:
                        row_cols[2].write("")

                    row_cols[3].write(m_item["nama_menu"])
                    row_cols[4].write(harga_satuan_str)
                    row_cols[5].write(str(m_item["qty"]))
                    row_cols[6].write(m_item["level"])
                    row_cols[7].write(m_item["catatan"])
                    row_cols[8].write(subtotal_text)
                    
                    with row_cols[9]:
                        # PERBAIKAN: Key delete dibuat unik menggunakan gabungan tanggal, nama, index, dan ID
                        if st.button("❌", key=f"del_btn_{tgl}_{nama}_{idx}_{m_item['id']}"):
                            cell = sheet_orders.find(str(m_item['id']))
                            if cell:
                                sheet_orders.delete_rows(cell.row)
                            st.cache_data.clear()
                            st.rerun()

                no_urut += 1
                st.markdown("<hr style='border: 0.5px solid #eee; margin: 2px 0px;'>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"### 💰 Total Uang Masuk Tanggal {tgl}: **Rp {total_biaya_tgl:,}**")
            
            st.markdown("#### 🛒 Rekap Total Porsi Jajanan Hari Ini (Urut A-Z):")
            
            summary_menu = {}
            for ord_data in orders_on_date:
                m_name = ord_data["nama_menu"]
                if m_name != "Biaya Jastip":
                    m_qty = ord_data["qty"]
                    m_pemesan = ord_data["nama_pemesan"]
                    
                    if m_name not in summary_menu:
                        summary_menu[m_name] = {"total_qty": 0, "pemesan_list": []}
                    
                    summary_menu[m_name]["total_qty"] += m_qty
                    summary_menu[m_name]["pemesan_list"].append(f"{m_pemesan} ({m_qty})")
            
            if summary_menu:
                sorted_summary_menu = sorted(summary_menu.items())
                for menu_name, data_val in sorted_summary_menu:
                    gabungan_nama = ", ".join(data_val["pemesan_list"])
                    st.write(f"- **{menu_name}**: total **{data_val['total_qty']} porsi** — *({gabungan_nama})*")
            else:
                st.write("- Belum ada porsi jajanan makanan.")
            
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
    
    for item in MENU_JAJANAN:
        key_name = f"toggle_menu_{item['id']}"
        st.checkbox(f"**{item['nama']}** — *{item['deskripsi']}*", key=key_name)
            
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