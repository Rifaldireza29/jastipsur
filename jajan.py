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
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# 23 Daftar Menu Jajanan Lengkap
MENU_JAJANAN = [
    {"id": 1, "nama": "Jambu Krisjon", "kategori": "makanan", "harga": 5000, "deskripsi": "Jambu kristal panghegar yang manis ituh."},
    {"id": 2, "nama": "Jambu Krisjon", "kategori": "makanan", "harga": 10000, "deskripsi": "Jambu kristal panghegar yang manis ituh"},
    {"id": 3, "nama": "Roti bakar coklat", "kategori": "makanan", "harga": 7000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 4, "nama": "Roti bakar strawberry", "kategori": "makanan", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 5, "nama": "Roti bakar keju", "kategori": "makanan", "harga": 7000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 6, "nama": "Roti bakar blueberry", "kategori": "makanan", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 7, "nama": "Roti bakar kacang", "kategori": "makanan", "harga": 6000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 8, "nama": "Roti bakar coklat-keju", "kategori": "makanan", "harga": 10000, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 9, "nama": "Roti bakar coklat-kacang", "kategori": "makanan", "harga": 9500, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 10, "nama": "Roti bakar kacang-strawberry", "kategori": "makanan", "harga": 8500, "deskripsi": "roti bakar yomart tea nu endul."},
    {"id": 11, "nama": "Dimsum ayam", "kategori": "makanan", "harga": 5000, "deskripsi": "dimsum ayam aja dijamin enak."},
    {"id": 12, "nama": "Dimsum ayam", "kategori": "makanan", "harga": 10000, "deskripsi": "dimsum ayam aja dijamin enak."},
    {"id": 13, "nama": "Dimsum campur", "kategori": "makanan", "harga": 5000, "deskripsi": "dimsum campur aduk makin enak."},
    {"id": 14, "nama": "Dimsum campur", "kategori": "makanan", "harga": 10000, "deskripsi": "Dimsum campur aduk makin enak."},
    {"id": 15, "nama": "Cilor", "kategori": "makanan", "harga": 5000, "deskripsi": "Cilor dekat mizan yang endul."},
    {"id": 16, "nama": "Cilor", "kategori": "makanan", "harga": 10000, "deskripsi": "Cilor dekat mizan yang endul."},
    {"id": 17, "nama": "Usus crispy", "kategori": "makanan", "harga": 5000, "deskripsi": "usus kabeuki gerri trusted enak banget."},
    {"id": 18, "nama": "Usus crispy", "kategori": "makanan", "harga": 10000, "deskripsi": "usus kabeuki gerri trusted enak banget."},
    {"id": 19, "nama": "Kwetiaw", "kategori": "makanan", "harga": 10000, "deskripsi": "kwetiau harga pasar rasa restoran."},
    {"id": 20, "nama": "cireng ayam ori", "kategori": "makanan", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 21, "nama": "cireng ayam pedas", "kategori": "makanan", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 22, "nama": "cireng ayam keju", "kategori": "makanan", "harga": 2500, "deskripsi": "hireng hanas."},
    {"id": 23, "nama": "Basreng", "kategori": "makanan", "harga": 5000, "deskripsi": "baso goyeng."},
    {"id": 24, "nama": "Basreng", "kategori": "makanan", "harga": 10000, "deskripsi": "baso goyeng."}
]

# Header Aplikasi
st.title("🍜 Jajan Kuy - Form & Rekapitulasi")
st.subheader("sok gewat atuh nge list best and bro, pilih tanggal tong poho!")
st.markdown("---")

# Tab Menu Aplikasi
tab_form, tab_rekap = st.tabs(["📝 Form Pesanan", "📊 Master Rekapitulasi Gabungan"])

with tab_form:
    st.markdown("### 1. 📋 Identitas & Tanggal Jajan")
    col_nama, col_tgl = st.columns(2)
    with col_nama:
        nama_pemesan = st.text_input("Nama Pemesan:", placeholder="Contoh: Surya / Rifaldy")
    with col_tgl:
        tanggal_jajan = st.date_input("Tanggal Jajan:", value=datetime.date.today())

    st.markdown("---")
    st.markdown("### 2. 🛒 Pilih Menu & Kustomisasi")

    if "current_cart" not in st.session_state:
        st.session_state.current_cart = []

    menu_options = [f"{item['nama']} (Rp {item['harga']:,}) - {item['deskripsi']}" for item in MENU_JAJANAN]
    selected_menu_str = st.selectbox("Pilih Menu Jajanan:", menu_options)

    selected_idx = menu_options.index(selected_menu_str)
    item_terpilih = MENU_JAJANAN[selected_idx]

    col_qty, col_level = st.columns(2)
    with col_qty:
        jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1)
    with col_level:
        level_pedas = st.selectbox("Level Pedas (Opsional):", ["Tidak Pedas (jiga orok)", "Pedes Dikit (manusia normal)", "Pedas Sedang (set manusia set jurig)", "Pedas mampus (Jurigg siah)"])

    catatan_item = st.text_input("Catatan Khusus (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng, kuah dipisah, dll.")

    if st.button("➕ Tambah ke Daftar Pesanan Saya"):
        st.session_state.current_cart.append({
            "nama_menu": f"{item_terpilih['nama']} (Rp {item_terpilih['harga']:,})",
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
                # Masukkan data ke Database SQLite permanen
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
    
    # Ambil semua data dari database SQLite
    cursor.execute("SELECT tanggal, nama_pemesan, nama_menu, harga, qty, level, catatan FROM orders")
    rows = cursor.fetchall()
    
    if not rows:
        st.info("Belum ada data pesanan yang masuk di database. Yuk isi form pesanan terlebih dahulu!")
    else:
        # Tombol reset database jika diperlukan
        if st.button("🗑️ Reset / Hapus Semua Rekap Database"):
            cursor.execute("DELETE FROM orders")
            conn.commit()
            st.rerun()

        st.markdown("---")
        
        # Ubah data sqlite ke format list of dictionary supaya gampang diproses
        all_orders_db = []
        for r in rows:
            all_orders_db.append({
                "tanggal": r[0],
                "nama_pemesan": r[1],
                "nama_menu": r[2],
                "harga": r[3],
                "qty": r[4],
                "level": r[5],
                "catatan": r[6]
            })

        unique_dates = sorted(list(set(order["tanggal"] for order in all_orders_db)))

        for tgl in unique_dates:
            st.markdown(f"### 📅 Tanggal: {tgl}")
            orders_on_date = [o for o in all_orders_db if o["tanggal"] == tgl]
            
            total_biaya_tgl = 0
            for idx, ord_data in enumerate(orders_on_date):
                sub_harga = ord_data["harga"] * ord_data["qty"]
                total_biaya_tgl += sub_harga
                st.markdown(f"""
                - **{ord_data['nama_pemesan']}** memesan **{ord_data['nama_menu']}** ({ord_data['qty']}x)  
                  &nbsp;&nbsp;&nbsp;&nbsp;└ *Level:* {ord_data['level']} | *Catatan:* {ord_data['catatan']} | *Subtotal:* Rp {sub_harga:,}
                """)
            
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