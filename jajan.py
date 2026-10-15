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

    # Pengecekan Waktu Habis secara Mutlak di Server Python (WIB)
    is_expired = False
    if deadline_str:
        now_local = datetime.datetime.now()
        target_dt = datetime.datetime.combine(tanggal_jajan, datetime.datetime.strptime(deadline_str, "%H:%M").time())
        if now_local > target_dt:
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
                    document.getElementById("live-timer").innerHTML = hours + " jam " + minutes + " menit " + seconds + " detik lagi";
                }}
            }}, 1000);
        </script>
        """
        components.html(timer_code, height=65)

    available_menu = [item for item in MENU_JAJANAN if item["id"] in active_menu_ids]

    # LOGIKA UTAMA PENGUNCIAN MEMBER
    if not available_menu:
        st.warning(f"🚫 Belum ada menu yang dibuka oleh Admin untuk tanggal **{tanggal_jajan}**. Coba pilih tanggal lain atau hubungi Surya ya!")
    elif is_expired and not is_admin:
        # Jika waktu habis DAN yang akses adalah Member, blokir total form!
        st.error(f"⌛ **Waktu Pemesanan Telah Habis!** Batas waktu pengisian untuk tanggal {tanggal_jajan} pukul {deadline_str} WIB sudah terlewati. Form pemesanan ditutup.")
    else:
        if is_expired and is_admin:
            st.warning(f"⚠️ **Perhatian Admin:** Waktu pemesanan tanggal {tanggal_jajan} (Deadline: {deadline_str} WIB) sudah lewat, tapi Anda dalam mode Admin sehingga tetap bisa menguji form.")

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
        st.markdown(f"Biaya Jastip (monmaap ada biaya jastip yak untuk modal nikah ya wkwkwk): Rp {biaya_jastip:,}")
        st.markdown(f"### Total Biaya Kesimpulan (Termasuk Jastip): **Rp {total_biaya_akhir:,}**")

        if st.button("🚀 Simpan & Masukkan ke Rekap Utama"):
            if is_expired and not is_admin:
                st.error("Waktu pemesanan sudah habis, tidak dapat menyimpan pesanan!")
            elif not nama_pemesan:
                st.error("Mohon isi Nama Pemesan terlebih dahulu!")
            else:
                for cart_item in st.session_state.current_cart:
                    cursor.execute("""
                        INSERT INTO orders (tanggal, nama_pemesan, nama_menu, harga, qty, level, catatan)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(tanggal_jajan),
                        nama_pemesan,
                        cart_item["nama_menu"],
                        cart_item["harga"],
                        cart_item["qty"],
                        cart_item["level"],
                        cart_item["catatan"]
                    ))
                    conn.commit()

                cursor.execute("""
                    INSERT INTO orders (tanggal, nama_pemesan, nama_menu, harga, qty, level, catatan)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(tanggal_jajan),
                    nama_pemesan,
                    "Biaya Jastip",
                    biaya_jastip,
                    1,
                    "-",
                    "monmaap ada biaya jastip yak untuk modal nikah ya wkwkwk"
                ))
                conn.commit()

                st.session_state.last_total_pay = total_biaya_akhir
                st.session_state.last_nama_pay = nama_pemesan
                st.session_state.show_payment_popup = True
                
                st.session_state.current_cart = []
                st.success("Yeay! Pesanan berhasil disimpan.")
                st.balloons()
                st.rerun()

    # --- POP-UP PEMBAYARAN PRIBADI MEMBER ---
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
        st.markdown("### 📊 Rekapitulasi Gabungan Seluruh Pesanan (Eksklusif Admin)")
        
        cursor.execute("SELECT id, tanggal, nama_pemesan, nama_menu, harga, qty, level, catatan FROM orders")
        rows = cursor.fetchall()
        
        if not rows:
            st.info("Belum ada data pesanan yang masuk di database.")
        else:
            if st.button("🗑️ Reset / Hapus Semua Rekap Database"):
                cursor.execute("DELETE FROM orders")
                conn.commit()
                st.rerun()

            st.markdown("---")
            
            all_orders_db = []
            for r in rows:
                all_orders_db.append({
                    "id": r[0],
                    "tanggal": r[1],
                    "nama_pemesan": r[2],
                    "nama_menu": r[3],
                    "harga": r[4],
                    "qty": r[5],
                    "level": r[6],
                    "catatan": r[7]
                })

            unique_dates = sorted(list(set(order["tanggal"] for order in all_orders_db)))

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

                for nama, items in grouped_by_person.items():
                    st.markdown(f"👤 **{nama}**")
                    subtotal_orang = 0
                    
                    for ord_data in items:
                        sub_harga = ord_data["harga"] * ord_data["qty"]
                        subtotal_orang += sub_harga
                        
                        col_item, col_btn = st.columns([5, 1])
                        with col_item:
                            if ord_data["nama_menu"] == "Biaya Jastip":
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **Biaya Jastip** — Rp {sub_harga:,} *( {ord_data['catatan']} )*")
                            else:
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **{ord_data['nama_menu']}** ({ord_data['qty']}x) | Level: {ord_data['level']} | Catatan: {ord_data['catatan']} — **Rp {sub_harga:,}**")
                        with col_btn:
                            if st.button("❌ Hapus", key=f"del_db_{ord_data['id']}"):
                                cursor.execute("DELETE FROM orders WHERE id = ?", (ord_data['id'],))
                                conn.commit()
                                st.rerun()

                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;👉 *Total Belanja {nama}:* **Rp {subtotal_orang:,}**")
                    st.markdown("---")
                    total_biaya_tgl += subtotal_orang
                
                st.markdown(f"**💰 Total Uang Masuk Tanggal {tgl}: Rp {total_biaya_tgl:,}**")
                
                st.markdown("#### 🛒 Rekap Total Porsi Jajanan Hari Ini:")
                
                summary_menu = {}
                for ord_data in orders_on_date:
                    m_name = ord_data["nama_menu"]
                    if m_name != "Biaya Jastip":
                        m_qty = ord_data["qty"]
                        summary_menu[m_name] = summary_menu.get(m_name, 0) + m_qty
                
                if summary_menu:
                    for menu_name, total_qty in summary_menu.items():
                        st.write(f"- **{menu_name}**: total **{total_qty} porsi**")
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
        
        cursor.execute("SELECT menu_id FROM active_menu WHERE tanggal = ?", (str(admin_tgl),))
        active_ids = [row[0] for row in cursor.fetchall()]
        
        selected_menu_ids = []
        for item in MENU_JAJANAN:
            is_checked = item["id"] in active_ids
            check = st.checkbox(f"{item['nama']} - {item['deskripsi']}", value=is_checked, key=f"menu_chk_tab_{item['id']}")
            if check:
                selected_menu_ids.append(item["id"])
                
        if st.button("💾 Simpan Perubahan Menu & Batas Waktu"):
            cursor.execute("DELETE FROM active_menu WHERE tanggal = ?", (str(admin_tgl),))
            deadline_str = admin_deadline.strftime("%H:%M")
            for m_id in selected_menu_ids:
                cursor.execute("INSERT INTO active_menu (tanggal, menu_id, deadline_time) VALUES (?, ?, ?)", (str(admin_tgl), m_id, deadline_str))
            conn.commit()
            st.success(f"Berhasil menyimpan menu aktif & batas waktu jam {deadline_str} untuk tanggal {admin_tgl}!")