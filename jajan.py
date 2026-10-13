import streamlit as st
import urllib.parse

# Konfigurasi halaman
st.set_page_config(
    page_title="Pemesanan Jajanan Kafe",
    page_icon="🍜",
    layout="wide"
)

# 10 Daftar Menu Jajanan Lengkap
MENU_JAJANAN = [
    {"id": 1, "nama": "Seblak Jebred Spesial", "kategori": "Pedas", "harga": 18000, "deskripsi": "Seblak komplit dengan kerupuk, sosis, bakso, ceker, dan tulang."},
    {"id": 2, "nama": "Cireng Bumbu Rujak", "kategori": "Gurih", "harga": 12000, "deskripsi": "Cireng crispy di luar, kenyal di dalam, disajikan dengan sambal rujak pedas manis."},
    {"id": 3, "nama": "Baso Aci Garut", "kategori": "Pedas", "harga": 15000, "deskripsi": "Baso aci hangat dengan cuanki lidah, siomay mini, dan jeruk limau."},
    {"id": 4, "nama": "Pisang Goreng Keju Coklat", "kategori": "Manis", "harga": 14000, "deskripsi": "Pisang manis berlumur susu kental manis, keju parut, dan meses melimpah."},
    {"id": 5, "nama": "Dimsum Mentai (4 pcs)", "kategori": "Gurih", "harga": 20000, "deskripsi": "Dimsum ayam udang lembut dengan saus mentai *torch* yang gurih creamy."},
    {"id": 6, "nama": "Tahu Crispy Petis", "kategori": "Gurih", "harga": 10000, "deskripsi": "Tahu goreng kopong super renyah dicocol sambal petis khas madura."},
    {"id": 7, "nama": "Martabak Telur Mini", "kategori": "Gurih", "harga": 12000, "deskripsi": "Martabak mini isi daging cincang dan daun bawang dengan kuah cuka asam manis."},
    {"id": 8, "nama": "Es Teh Manis Melati", "kategori": "Minuman", "harga": 5000, "deskripsi": "Teh melati segar dengan es batu melimpah."},
    {"id": 9, "nama": "Es Jeruk Peras Asli", "kategori": "Minuman", "harga": 8000, "deskripsi": "Jeruk peras murni segar kaya vitamin C penawar pedas."},
    {"id": 10, "nama": "Es Susu Kopi Gula Aren", "kategori": "Minuman", "harga": 18000, "deskripsi": "Kopi susu espresso dipadu manisnya gula aren asli."}
]

# Header Kafe
st.title("🍜 Kedai Jajanan & Kuliner Kita")
st.subheader("Silakan isi data pesanan, pilih menu, atur level pedas, dan catatan khusus!")
st.markdown("---")

# Form Data Pelanggan (Mirip sistem kasir kafe)
st.markdown("### 1. 📋 Identitas Pemesan")
col_nama, col_meja = st.columns(2)
with col_nama:
    nama_pemesan = st.text_input("Nama Pemesan / Pelanggan:", placeholder="Contoh: Budi Santoso")
with col_meja:
    tipe_pesanan = st.selectbox("Jenis Layanan:", ["Dine-In (Makan di Tempat)", "Takeaway (Bungkus)", "Delivery (Ojol/Kurir)"])

# Jika Dine-In, minta nomor meja
nomor_meja = ""
if "Dine-In" in tipe_pesanan:
    nomor_meja = st.text_input("Nomor Meja:", placeholder="Contoh: Meja 05")

st.markdown("---")
st.markdown("### 2. 🛒 Pilih Menu & Kustomisasi")

# Menyimpan data pesanan sementara di Session State
if "order_list" not in st.session_state:
    st.session_state.order_list = []

# Tampilkan pilihan 10 menu menggunakan selectbox/form interaktif per item
selected_menu = st.selectbox("Pilih Menu Jajanan:", [f"{item['nama']} - Rp {item['harga']:,}" for item in MENU_JAJANAN])

# Ambil data menu yang dipilih
selected_idx = [f"{item['nama']} - Rp {item['harga']:,}" for item in MENU_JAJANAN].index(selected_menu)
item_terpilih = MENU_JAJANAN[selected_idx]

# Detail kustomisasi untuk menu yang dipilih
col_qty, col_level = st.columns(2)
with col_qty:
    jumlah_pesan = st.number_input("Jumlah Porsi:", min_value=1, max_value=20, value=1)

with col_level:
    level_pedas = st.selectbox("Level Pedas (Opsional):", ["Tidak Pedas (Level 0)", "Sedang (Level 1)", "Pedas (Level 2)", "Super Pedas (Level 3)", "Wajib Pedas Mampus (Level 5)"])

catatan_item = st.text_input("Catatan Khusus untuk Menu Ini (Opsional):", placeholder="Contoh: Jangan pakai bawang goreng, kuah dipisah, dll.")

if st.button("➕ Masukkan ke Daftar Pesanan"):
    # Masukkan ke list pesanan aktif
    st.session_state.order_list.append({
        "nama": item_terpilih["nama"],
        "harga": item_terpilih["harga"],
        "qty": jumlah_pesan,
        "level": level_pedas,
        "catatan": catatan_item if catatan_item else "-"
    })
    st.toast(f"Berhasil menambahkan {item_terpilih['nama']}!")

st.markdown("---")

# 3. Rekapitulasi Pesanan (Struk Sementara)
st.markdown("### 🧾 Rincian Pesanan Kamu")

if not st.session_state.order_list:
    st.info("Belum ada menu yang dimasukkan ke daftar pesanan.")
else:
    total_tagihan = 0
    formatted_pesanan_wa = []
    
    for i, ord_item in enumerate(st.session_state.order_list):
        subtotal = ord_item["harga"] * ord_item["qty"]
        total_tagihan += subtotal
        
        with st.container():
            col_a, col_b, col_c = st.columns([3, 2, 1])
            col_a.write(f"**{i+1}. {ord_item['nama']}** (x{ord_item['qty']})")
            col_b.write(f"Level: {ord_item['level']}\n\n*Catatan:* {ord_item['catatan']}")
            col_c.write(f"**Rp {subtotal:,}**")
            
            # Tombol Hapus per item
            if st.button(f"Hapus", key=f"del_{i}"):
                st.session_state.order_list.pop(i)
                st.rerun()
            st.divider()

        # Susunan teks untuk WhatsApp
        formatted_pesanan_wa.append(
            f"{i+1}. {ord_item['nama']} ({ord_item['qty']}x) - Rp {subtotal:,}\n   └ Level: {ord_item['level']}\n   └ Catatan: {ord_item['catatan']}"
        )

    st.markdown(f"### Total Keseluruhan: **Rp {total_tagihan:,}**")
    
    # Tombol Reset Keranjang
    if st.button("🗑️ Kosongkan Semua Pesanan"):
        st.session_state.order_list = []
        st.rerun()

    st.markdown("---")
    
    # Tombol Kirim ke WhatsApp Kasir / Dapur
    if st.button("🚀 Kirim Pesanan ke WhatsApp Kasir"):
        if not nama_pemesan:
            st.error("Mohon isi Nama Pemesan di bagian atas dulu ya!")
        else:
            nomor_whatsapp_kasir = "6281234567890" # Ganti nomor WhatsApp tujuan (format 62...)
            
            info_tempat = f"*Nomor Meja:* {nomor_meja}" if "Dine-In" in tipe_pesanan else f"*Jenis:* {tipe_pesanan}"
            
            teks_wa = f"""Halo Kak, saya mau pesan jajanan dengan detail berikut:

*Nama Pemesan:* {nama_pemesan}
{info_tempat}

*Daftar Pesanan:*
""" + "\n\n".join(formatted_pesanan_wa) + f"""

*Total Pembayaran: Rp {total_tagihan:,}*

Mohon segera diproses ya, terima kasih! 🙏"""

            encoded_text = urllib.parse.quote(teks_wa)
            wa_link = f"https://wa.me/{nomor_whatsapp_kasir}?text={encoded_text}"
            
            st.success("Pesanan berhasil direkap! Silakan klik tombol di bawah untuk mengirim ke WhatsApp:")
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; padding:12px 24px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:16px;">Kirim Pesanan ke WhatsApp 🚀</button></a>', unsafe_allow_html=True)