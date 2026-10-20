import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components
import pandas as pd

# Konfigurasi halaman
st.set_page_config(
    page_title="Jajan titip surya",
    page_icon="🍜",
    layout="wide"
)

# --- SETUP KONEKSI GOOGLE SHEETS VIA STREAMLIT SECRETS ---
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
    sheet_active_menu = sh.worksheet("active_menu")
    sheet_payment = sh.worksheet("payment_status")
except Exception as e:
    st.error(f"⚠️ Gagal terhubung ke Google Sheets. Pastikan file 'Database_Jastipsur' dan ketiga tab sudah ada! Error: {e}")
    st.stop()

# --- FUNGSI CACHE DATA UNTUK MENCEGAH ERROR 429 (QUOTA EXCEEDED) ---
@st.cache_data(ttl=5)
def get_cached_records(sheet_type):
    if sheet_type == "orders":
        return sheet_orders.get_all_records()
    elif sheet_type == "active_menu":
        return sheet_active_menu.get_all_records()
    elif sheet_type == "payment_status":
        return sheet_payment.get_all_records()
    return []

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
            {"nama": "Strawberry", "harga": 7000},
            {"nama": "Keju", "harga": 7000},
            {"nama": "Blueberry", "harga": 7000},
            {"nama": "Kacang", "harga": 7000},
            {"nama": "Coklat-Keju", "harga": 9500},
            {"nama": "Coklat-Kacang", "harga": 8500},
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

    active_rows_raw = get_cached_records("active_menu")
    active_menu_ids = []
    deadline_str = None
    
    for r in active_rows_raw:
        if str(r.get("tanggal")) == str(tanggal_jajan):
            try:
                active_menu_ids.append(int(r.get("menu_id")))
            except:
                pass
            if r.get("deadline_time"):
                deadline_str = str(r.get("deadline_time"))

    WIB = datetime.timezone(datetime.timedelta(hours=7))
    now_wib = datetime.datetime.now(WIB)

    is_expired = False
    if deadline_str:
        try:
            target_dt = datetime.datetime.combine(
                tanggal_jajan, 
                datetime.datetime.strptime(deadline_str, "%H:%M").time()
            ).replace(tzinfo=WIB)
            
            if now_wib > target_dt:
                is_expired = True
        except:
            pass

    if deadline_str and not is_expired:
        target_datetime_str = f"{tanggal_jajan}T{deadline_str}:00"
        timer_code = """
        <div style="background-color: #ff4b4b; padding: 12px; border-radius: 8px; color: white; text-align: center; font-family: sans-serif; font-weight: bold; margin-bottom: 15px;">
            ⏳ Sisa Waktu Pemesanan: <span id="live-timer" style="font-size: 1.2em; background: rgba(0,0,0,0.2); padding: 2px 8px; border-radius: 4px;">Memuat...</span>
        </div>
        <script>
            var targetDate = new Date("TARGET_DATE_PLACEHOLDER").getTime();
            var x = setInterval(function() {
                var now = new Date().getTime();
                var distance = targetDate - now;
                
                if (distance < 0) {
                    clearInterval(x);
                    document.getElementById("live-timer").innerHTML = "WAKTU HABIS!";
                    window.location.reload();
                } else {
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById("live-timer").innerHTML = hours + " jam " + minutes + " menit " + seconds + " detik lagi";
                }
            }, 1000);
        </script>
        """.replace("TARGET_DATE_PLACEHOLDER", target_datetime_str)
        components.html(timer_code, height=65)

    available_menu = [item for item in MENU_JAJANAN if item["id"] in active_menu_ids]

    if not available_menu:
        st.warning(f"🚫 Belum ada menu yang dibuka oleh Admin untuk tanggal **{tanggal_jajan}**. Coba pilih tanggal lain atau buka menu melalui Panel Kontrol Admin ya!")
    elif is_expired and not is_admin:
        st.error(f"⌛ **Waktu Pemesanan Telah Habis!** Batas waktu pengisian untuk tanggal {tanggal_jajan} pukul {deadline_str} WIB sudah terlewati. Form pemesanan dikunci mutlak.")
    else:
        if is_expired and is_admin:
            st.warning(f"⚠️ **Perhatian Admin:** Waktu pemesanan tanggal {tanggal_jajan} (Deadline: {deadline_str} WIB) sudah lewat, tapi Anda dalam mode Admin sehingga tetap bisa mengakses form.")

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
            if is_expired and not is_admin:
                st.error("Waktu pemesanan sudah habis, tidak dapat menambah pesanan!")
            else:
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
            if is_expired and not is_admin:
                st.error("Waktu pemesanan sudah habis, tidak dapat menyimpan pesanan!")
            elif not nama_pemesan:
                st.error("Mohon isi Nama Pemesan terlebih dahulu!")
            else:
                try:
                    all_orders_data = get_cached_records("orders")
                except:
                    all_orders_data = []
                new_id = len(all_orders_data) + 1

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
if is_admin:
    with tab_rekap:
        col_title, col_btn = st.columns([3, 1])
        with col_title:
            st.markdown("### 📊 Rekapitulasi Gabungan Seluruh Pesanan (Eksklusif Admin)")
        with col_btn:
            if st.button("🔄 Refresh Data Rekap"):
                st.cache_data.clear()
                st.rerun()
        
        try:
            orders_data_raw = get_cached_records("orders")
        except:
            orders_data_raw = []
        
        if not orders_data_raw:
            st.info("Belum ada data pesanan yang masuk di Google Sheet.")
        else:
            if st.button("🗑️ Reset / Hapus Semua Rekap Spreadsheet"):
                sheet_orders.clear()
                sheet_orders.append_row(["id", "tanggal", "nama_pemesan", "nama_menu", "harga", "qty", "level", "catatan"])
                sheet_payment.clear()
                sheet_payment.append_row(["tanggal", "nama_pemesan", "is_lunas"])
                st.cache_data.clear()
                st.rerun()

            st.markdown("---")
            
            all_orders_db = []
            for r in orders_data_raw:
                if r.get("id") != "" and r.get("id") is not None:
                    try:
                        all_orders_db.append({
                            "id": int(r.get("id", 0)),
                            "tanggal": str(r.get("tanggal", "")),
                            "nama_pemesan": str(r.get("nama_pemesan", "")),
                            "nama_menu": str(r.get("nama_menu", "")),
                            "harga": int(r.get("harga", 0)),
                            "qty": int(r.get("qty", 0)),
                            "level": str(r.get("level", "")),
                            "catatan": str(r.get("catatan", ""))
                        })
                    except:
                        pass

            unique_dates = sorted(list(set(order["tanggal"] for order in all_orders_db if order["tanggal"])))

            try:
                payment_rows_raw = get_cached_records("payment_status")
            except:
                payment_rows_raw = []

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

                    is_currently_lunas = False
                    for pr in payment_rows_raw:
                        if str(pr.get("tanggal")) == str(tgl) and str(pr.get("nama_pemesan")) == str(nama):
                            if int(pr.get("is_lunas", 0)) == 1:
                                is_currently_lunas = True

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
                                    val_to_set = 1 if ubah_lunas else 0
                                    found_pay = False
                                    cell_row = None
                                    for idx_p, pr in enumerate(payment_rows_raw):
                                        if str(pr.get("tanggal")) == str(tgl) and str(pr.get("nama_pemesan")) == str(nama):
                                            found_pay = True
                                            cell_row = idx_p + 2
                                            break
                                    
                                    if found_pay and cell_row:
                                        sheet_payment.update_cell(cell_row, 3, val_to_set)
                                    else:
                                        sheet_payment.append_row([str(tgl), str(nama), val_to_set])
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
                            if st.button("❌", key=f"del_btn_{m_item['id']}"):
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
    with tab_admin_menu:
        st.markdown("## 🛠️ Panel Kontrol Admin (Buka Menu Harian & Deadline)")
        
        admin_tgl = st.date_input("Pilih Tanggal Jajan yang Mau Disetting Menunya:", value=datetime.date.today(), key="admin_tgl_tab")
        admin_deadline = st.time_input("Tentukan Batas Waktu (Jam Penutupan Pesanan):", value=datetime.time(10, 0), key="admin_deadline_time")
        
        st.info(f"💡 Mengatur menu & batas waktu untuk tanggal: **{admin_tgl}** (Deadline: **{admin_deadline.strftime('%H:%M')} WIB**) ")
        st.write("Silakan centang menu apa saja yang **dibuka**:")
        
        try:
            active_menu_raw = get_cached_records("active_menu")
        except:
            active_menu_raw = []

        active_ids = [int(row["menu_id"]) for row in active_menu_raw if str(row.get("tanggal")) == str(admin_tgl) and str(row.get("menu_id", "")) != ""]
        
        selected_menu_ids = []
        for item in MENU_JAJANAN:
            is_checked = item["id"] in active_ids
            check = st.checkbox(f"{item['nama']} - {item['deskripsi']}", value=is_checked, key=f"menu_chk_tab_{item['id']}")
            if check:
                selected_menu_ids.append(item["id"])
                
        if st.button("💾 Simpan Perubahan Menu & Batas Waktu"):
            cell_list = sheet_active_menu.findall(str(admin_tgl))
            row_indices_to_delete = sorted([c.row for c in cell_list], reverse=True)
            for r_idx in row_indices_to_delete:
                sheet_active_menu.delete_rows(r_idx)

            deadline_str = admin_deadline.strftime("%H:%M")
            for m_id in selected_menu_ids:
                sheet_active_menu.append_row([str(admin_tgl), int(m_id), str(deadline_str)])

            st.cache_data.clear()
            st.success(f"Berhasil menyimpan menu aktif & batas waktu jam {deadline_str} untuk tanggal {admin_tgl} ke Google Sheets!")
            st.rerun()