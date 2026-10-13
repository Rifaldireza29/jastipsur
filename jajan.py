import streamlit as st
import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Jajan titip surya",
    page_icon="🍜",
    layout="wide"
)

# 10 Daftar Menu Jajanan Lengkap
MENU_JAJANAN = [
    {"id": 1, "nama": "Jambu Krisjon", "kategori": "Pedas", "harga": 5000, "deskripsi": "Seblak komplit dengan kerupuk, sosis, bakso, ceker, dan tulang."},
    {"id": 2, "nama": "Jambu Krisjon", "kategori": "Gurih", "harga": 10000, "deskripsi": "Cireng crispy di luar, kenyal di dalam, disajikan dengan sambal rujak pedas manis."},
    {"id": 3, "nama": "Baso Aci Garut", "kategori": "Pedas", "harga": 15000, "deskripsi": "Baso aci hangat dengan cuanki lidah, siomay mini, dan jeruk limau."},
    {"id": 4, "nama": "Pisang Goreng Keju Coklat", "kategori": "Manis", "harga": 14000, "deskripsi": "Pisang manis berlumur susu kental manis, keju parut, dan meses melimpah."},
    {"id": 5, "nama": "Dimsum Mentai (4 pcs)", "kategori": "Gurih", "harga": 20000, "deskripsi": "Dimsum ayam udang lembut dengan saus mentai *torch* yang gurih creamy."},
    {"id": 6, "nama": "Tahu Crispy Petis", "kategori": "Gurih", "harga": 10000, "deskripsi": "Tahu goreng kopong super renyah dicocol sambal petis khas madura."},
    {"id": 7, "nama": "Martabak Telur Mini", "kategori": "Gurih", "harga": 12000, "deskripsi": "Martabak mini isi daging cincang dan daun bawang dengan kuah cuka asam manis."},
    {"id": 8, "nama": "Es Teh Manis Melati", "kategori": "Minuman", "harga": 5000, "deskripsi": "Teh melati segar dengan es batu melimpah."},
    {"id": 9, "nama": "Es Jeruk Peras Asli", "kategori": "Minuman", "harga": 8000, "deskripsi": "Jeruk peras murni segar kaya vitamin C penawar pedas."},
    {"id": 10, "nama": "Es Susu Kopi Gula Aren", "kategori": "Minuman", "harga": 18000, "deskripsi": "Kopi susu espresso dipadu manisnya gula aren asli."}
]

# Inisialisasi Database Sederhana di Session State (Menyimpan semua riwayat pesanan)
if "all_orders" not in st.session_state:
    st.session_state.all_orders = []

# Header Aplikasi
st.title("🍜 Jajan Kuy - Form & Rekapitulasi")
st.subheader("sok gewat atuh nge list best bro, pilih tanggal tong poho!")
st.markdown("---")

# Tab Menu Aplikasi supaya rapi
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

    # Session state untuk keranjang sementara per input user
    if "current_cart" not in st.session_state:
        st.session_state.current_cart = []

    selected_menu = st.selectbox("Pilih Menu Jajanan:", [f"{item['nama']} - Rp {item['harga']:,}" for item in MENU_JAJANAN])

    # Ambil data menu yang dipilih
    selected_idx = [f"{item['nama']} - Rp {item['harga']:,}" for item in MENU_JAJANAN].index(selected_menu)
    item_terpilih = MENU_JAJANAN[selected_idx]

    col_qty, col_level = st.columns(2)
    with col_qty:
        jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1)
    with col_level:
        level_pedas = st.selectbox("Level Pedas (Opsional):", ["Tidak Pedas (jiga orok)", "Pedes Dikit (manusia normal)", "Pedas Sedang (set manusia set jurig)", "Pedas mampus (Jurigg siah)"])

    catatan_item = st.text_input("Catatan Khusus (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng, kuah dipisah, dll.")

    if st.button("➕ Tambah ke Daftar Pesanan Saya"):
        st.session_state.current_cart.append({
            "nama_menu": item_terpilih["nama"],
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
                # Masukkan semua item dari cart ke master database all_orders
                for cart_item in st.session_state.current_cart:
                    st.session_state.all_orders.append({
                        "tanggal": str(tanggal_jajan),
                        "nama_pemesan": nama_pemesan,
                        "nama_menu": cart_item["nama_menu"],
                        "harga": cart_item["harga"],
                        "qty": cart_item["qty"],
                        "level": cart_item["level"],
                        "catatan": cart_item["catatan"]
                    })
                # Kosongkan cart sementara
                st.session_state.current_cart = []
                st.success("Yeay! Pesanan berhasil disimpan dan digabungkan ke Master Rekap.")
                st.balloons()

with tab_rekap:
    st.markdown("### 📊 Rekapitulasi Gabungan Seluruh Pesanan")
    
    if not st.session_state.all_orders:
        st.info("Belum ada data pesanan yang masuk. Yuk isi form pesanan terlebih dahulu di tab sebelah!")
    else:
        # Tombol reset master rekap jika diperlukan
        if st.button("🗑️ Reset / Hapus Semua Rekap"):
            st.session_state.all_orders = []
            st.rerun()

        st.markdown("---")
        
        # Kelompokkan berdasarkan Tanggal
        unique_dates = sorted(list(set(order["tanggal"] for order in st.session_state.all_orders)))

        for tgl in unique_dates:
            st.markdown(f"### 📅 Tanggal: {tgl}")
            orders_on_date = [o for o in st.session_state.all_orders if o["tanggal"] == tgl]
            
            # Tampilkan rincian perorangan yang digabung
            total_biaya_tgl = 0
            for idx, ord_data in enumerate(orders_on_date):
                sub_harga = ord_data["harga"] * ord_data["qty"]
                total_biaya_tgl += sub_harga
                st.markdown(f"""
                - **{ord_data['nama_pemesan']}** memesan **{ord_data['nama_menu']}** ({ord_data['qty']}x)  
                  &nbsp;&nbsp;&nbsp;&nbsp;└ *Level:* {ord_data['level']} | *Catatan:* {ord_data['catatan']} | *Subtotal:* Rp {sub_harga:,}
                """)
            
            st.markdown(f"**💰 Total harga Masuk Tanggal {tgl}: Rp {total_biaya_tgl:,}**")
            
            # REKAP AKHIR SESUAI JENIS JAJANAN PADA TANGGAL TERSEBUT
            st.markdown("#### 🛒 Rekap Total Porsi Berdasarkan Jenis Jajanan:")
            
            # Hitung akumulasi qty per jenis menu di tanggal ini
            summary_menu = {}
            for ord_data in orders_on_date:
                m_name = ord_data["nama_menu"]
                m_qty = ord_data["qty"]
                summary_menu[m_name] = summary_menu.get(m_name, 0) + m_qty
            
            # Tampilkan dalam bentuk list/tabel ringkas
            for menu_name, total_qty in summary_menu.items():
                st.write(f"- **{menu_name}**: total **{total_qty} porsi**")
            
            st.markdown("---")