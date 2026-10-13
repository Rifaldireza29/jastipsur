import streamlit as st
import datetime
import sqlite3

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
    # Tabel pesanan
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
    # Tabel untuk menyimpan status menu yang diaktifkan admin per tanggal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_menu (
            tanggal TEXT,
            menu_id INTEGER,
            PRIMARY KEY (tanggal, menu_id)
        )
    """)
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# 23 Daftar Menu Jajanan Lengkap
MENU_JAJANAN = [
    {"id": 1, "nama": "Jambu Krisjon", "lokasi": "Panghegar", "harga": 5000, "deskripsi": "Jambu kristal panghegar yang manis ituh."},
    {"id": 2, "nama": "Jambu Krisjon", "lokasi": "Panghegar", "harga": 10000, "deskripsi": "Jambu kristal panghegar yang manis ituh"},
    {"id": 3, "nama": "Roti bakar coklat", "lokasi": "Yomart", "harga": 7000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 4, "nama": "Roti bakar strawberry", "lokasi": "Yomart", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 5, "nama": "Roti bakar keju", "lokasi": "Yomart", "harga": 7000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 6, "nama": "Roti bakar blueberry", "lokasi": "Yomart", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 7, "nama": "Roti bakar kacang", "lokasi": "Yomart", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 8, "nama": "Roti bakar coklat-keju", "lokasi": "Yomart", "harga": 10000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 9, "nama": "Roti bakar coklat-kacang", "lokasi": "Yomart", "harga": 9500, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 10, "nama": "Roti bakar kacang-strawberry", "lokasi": "Yomart", "harga": 8500, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 11, "nama": "Dimsum ayam", "lokasi": "Lainnya", "harga": 5000, "deskripsi": "dimsum ayam aja dijamin enak."},
    {"id": 12, "nama": "Dimsum ayam", "lokasi": "Lainnya", "harga": 10000, "deskripsi": "dimsum ayam aja dijamin enak."},
    {"id": 13, "nama": "Dimsum campur", "lokasi": "Lainnya", "harga": 5000, "deskripsi": "dimsum ayam aja dijamin enak."},
    {"id": 14, "nama": "Dimsum campur", "lokasi": "Lainnya", "harga": 10000, "deskripsi": "Dimsum campur aduk makin enak."},
    {"id": 15, "nama": "Cilor", "lokasi": "Mizan", "harga": 5000, "deskripsi": "Cilor dekat mizan yang endul."},
    {"id": 16, "nama": "Cilor", "lokasi": "Mizan", "harga": 10000, "deskripsi": "Cilor dekat mizan yang endul."},
    {"id": 17, "nama": "Usus crispy", "lokasi": "Kabeuki Gerri", "harga": 5000, "deskripsi": "usus kabeuki gerri trusted enak banget."},
    {"id": 18, "nama": "Usus crispy", "lokasi": "Kabeuki Gerri", "harga": 10000, "deskripsi": "usus kabeuki gerri trusted enak banget."},
    {"id": 19, "nama": "Kwetiaw", "lokasi": "Lainnya", "harga": 10000, "deskripsi": "kwetiau harga pasar rasa restoran."},
    {"id": 20, "nama": "cireng ayam ori", "lokasi": "Hanas", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 21, "nama": "cireng ayam pedas", "lokasi": "Hanas", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 22, "nama": "cireng ayam keju", "lokasi": "Hanas", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 23, "nama": "Basreng", "lokasi": "Lainnya", "harga": 5000, "deskripsi": "baso goyeng."},
    {"id": 24, "nama": "Basreng", "lokasi": "Lainnya", "harga": 10000, "deskripsi": "baso goyeng."}
]

# Header Aplikasi
st.title("🍜 Jajan Kuy - Form & Rekapitulasi")
st.subheader("sok gewat atuh nge list best and bro, pilih tanggal tong poho!")
st.markdown("---")

# Sidebar untuk Mode Admin / Member
st.sidebar.title("🔐 Mode Akses")
mode_akses = st.sidebar.radio("Pilih Peran:", ["Member (Pemesan)", "Admin (Surya)"])

# Jika masuk mode Admin
if mode_akses == "Admin (Surya)":
    st.sidebar.markdown("---")
    password_admin = st.sidebar.text_input("Password Admin:", type="password")
    
    # Ganti "surya123" dengan password rahasia pilihan kamu
    if password_admin == "rezareza": 
        st.sidebar.success("Mode Admin Aktif! 🔓")
        st.markdown("## 🛠️ Panel Kontrol Admin (Buka Menu Harian)")
        
        admin_tgl = st.date_input("Pilih Tanggal Menu yang Mau Dibuka:", value=datetime.date.today(), key="admin_tgl")
        
        st.write("Silakan centang menu apa saja yang **dibuka** untuk tanggal tersebut:")
        
        # Ambil menu yang sudah aktif sebelumnya di tanggal ini
        cursor.execute("SELECT menu_id FROM active_menu WHERE tanggal = ?", (str(admin_tgl),))
        active_ids = [row[0] for row in cursor.fetchall()]
        
        # Form checklist menu
        selected_menu_ids = []
        for item in MENU_JAJANAN:
            is_checked = item["id"] in active_ids
            check = st.checkbox(f"[{item['lokasi']}] {item['nama']} - Rp {item['harga']:,} ({item['deskripsi']})", value=is_checked, key=f"menu_chk_{item['id']}")
            if check:
                selected_menu_ids.append(item["id"])
                
        if st.button("💾 Simpan Menu yang Dibuka Hari Ini"):
            # Hapus setting lama untuk tanggal tersebut lalu masukkan yang baru
            cursor.execute("DELETE FROM active_menu WHERE tanggal = ?", (str(admin_tgl),))
            for m_id in selected_menu_ids:
                cursor.execute("INSERT INTO active_menu (tanggal, menu_id) VALUES (?, ?)", (str(admin_tgl), m_id))
            conn.commit()
            st.success(f"Berhasil menyimpan menu aktif untuk tanggal {admin_tgl}!")
            
    else:
        st.warning("⚠️ Masukkan password admin yang benar di sidebar untuk mengakses panel kontrol.")
        st.stop()

# Tab Menu Utama untuk Member & Rekap
tab_form, tab_rekap = st.tabs(["📝 Form Pesanan Member", "📊 Master Rekapitulasi Gabungan"])

with tab_form:
    st.markdown("### 1. 📋 Identitas & Tanggal Jajan")
    col_nama, col_tgl = st.columns(2)
    
    with col_nama:
        nama_pemesan = st.text_input("Nama Pemesan:", placeholder="Contoh: Budi / Rifaldy")
    with col_tgl:
        tanggal_jajan = st.date_input("Tanggal Jajan:", value=datetime.date.today())

    st.markdown("---")
    st.markdown("### 2. 🛒 Pilih Menu yang Tersedia Hari Ini")

    # Ambil menu yang diaktifkan oleh admin untuk tanggal tersebut
    cursor.execute("SELECT menu_id FROM active_menu WHERE tanggal = ?", (str(tanggal_jajan),))
    active_rows = cursor.fetchall()
    active_menu_ids = [r[0] for r in active_rows]

    # Filter menu berdasarkan yang di-approve admin
    available_menu = [item for item in MENU_JAJANAN if item["id"] in active_menu_ids]

    if not available_menu:
        st.warning(f"🚫 Belum ada menu yang dibuka oleh Admin untuk tanggal **{tanggal_jajan}**. Coba hubungi Surya ya buat buka menunya!")
    else:
        if "current_cart" not in st.session_state:
            st.session_state.current_cart = []

        menu_options = [f"[{item['lokasi']}] {item['nama']} (Rp {item['harga']:,}) - {item['deskripsi']}" for item in available_menu]
        selected_menu_str = st.selectbox("Pilih Menu Jajanan:", menu_options)

        selected_idx = menu_options.index(selected_menu_str)
        item_terpilih = available_menu[selected_idx]

        col_qty, col_level = st.columns(2)
        with col_qty:
            jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1)
        with col_level:
            level_pedas = st.selectbox("Level Pedas (Opsional):", ["Tidak Pedas (jiga orok)", "Pedes Dikit (manusia normal)", "Pedas Sedang (set manusia set jurig)", "Pedas mampus (Jurigg siah)"])

        catatan_item = st.text_input("Catatan Khusus (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng, kuah dipisah, dll.")

        if st.button("➕ Tambah ke Daftar Pesanan Saya"):
            st.session_state.current_cart.append({
                "nama_menu": f"[{item_terpilih['lokasi']}] {item_terpilih['nama']} (Rp {item_terpilih['harga']:,})",
                "harga": item_terpilih["harga"],
                "qty": jumlah_pesan,
                "level": level_pedas,
                "catatan": catatan_item if catatan_item else "-"
            })
            st.toast(f"Berhasil menambahkan {item_terpilih['nama']}!")

    st.markdown("---")
    st.markdown("### 🧾 Preview Pesanan Kamu")

    if not st.session_state.current_cart:
        st.info("Belum ada menu yang ditambahkan.")
    else:
        subtotal_sementara = 0
        for idx, cart_item in enumerate(st.session_state.current_cart):
            sub = cart_item["harga"] * cart_item["qty"]
            subtotal_sementara += sub
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{cart_item['nama_menu']}** (x{cart_item['qty']}) - Level: {cart_item['level']}")
            c2.write(f"Catatan: {cart_item['catatan']}")
            c3.write(f"Rp {sub:,}")
            if st.button("Hapus Item", key=f"del_cart_{idx}"):
                st.session_state.current_cart.pop(idx)
                st.rerun()

        st.markdown(f"**Total Biaya Pesanan Kamu: Rp {subtotal_sementara:,}**")

        if st.button("🚀 Simpan & Masukkan ke Rekap Utama"):
            if not nama_pemesan:
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

                st.session_state.current_cart = []
                st.success("Yeay! Pesanan berhasil disimpan dan masuk ke Master Rekap Bersama!")
                st.balloons()

with tab_rekap:
    st.markdown("### 📊 Rekapitulasi Gabungan Seluruh Pesanan (Live Database)")
    
    cursor.execute("SELECT id, tanggal, nama_pemesan, nama_menu, harga, qty, level, catatan FROM orders")
    rows = cursor.fetchall()
    
    if not rows:
        st.info("Belum ada data pesanan yang masuk di database. Yuk isi form pesanan terlebih dahulu!")
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
            
            total_biaya_tgl = 0
            for idx, ord_data in enumerate(orders_on_date):
                sub_harga = ord_data["harga"] * ord_data["qty"]
                total_biaya_tgl += sub_harga
                
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""
                    - **{ord_data['nama_pemesan']}** memesan **{ord_data['nama_menu']}** ({ord_data['qty']}x)  
                      &nbsp;&nbsp;&nbsp;&nbsp;└ *Level:* {ord_data['level']} | *Catatan:* {ord_data['catatan']} | *Subtotal:* Rp {sub_harga:,}
                    """)
                with col_btn:
                    if st.button("❌ Hapus", key=f"del_db_{ord_data['id']}"):
                        cursor.execute("DELETE FROM orders WHERE id = ?", (ord_data['id'],))
                        conn.commit()
                        st.rerun()
            
            st.markdown(f"**💰 Total harga Masuk Tanggal {tgl}: Rp {total_biaya_tgl:,}**")
            
            st.markdown("#### 🛒 Rekap Total Porsi Berdasarkan Jenis Jajanan:")
            
            summary_menu = {}
            for ord_data in orders_on_date:
                m_name = ord_data["nama_menu"]
                m_qty = ord_data["qty"]
                summary_menu[m_name] = summary_menu.get(m_name, 0) + m_qty
            
            for menu_name, total_qty in summary_menu.items():
                st.write(f"- **{menu_name}**: total **{total_qty} porsi**")
            
            st.markdown("---")
            
    # --- BAGIAN QR CODE BCA ASLI DI AKHIR REKAP ---
    st.markdown("---")
    st.markdown("### 💳 Pembayaran Transfer QRIS BCA")
    st.write("Silakan scan QR di bawah ini untuk melakukan pembayaran transfer jajanan ke rekening **Rezha Surya Rifaldy**[cite: 3]:")
    
    try:
        st.image("qr_bca.jpeg", width=300, caption="QRIS BCA - Rezha Surya Rifaldy[cite: 3]")
    except Exception:
        st.warning("⚠️ File gambar `qr_bca.jpeg` belum dimasukkan ke folder kodingan. Pastikan file fotonya sudah disatukan di folder yang sama ya!")
    
    st.info("Catatan: Jangan lupa kirim bukti transfer setelah scan ya, brader!")