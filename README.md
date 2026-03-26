# Arsitek Finansial Pribadi

Aplikasi manajemen keuangan berbasis *Mobile-First UI* dengan desain **Clean, Modern SaaS** yang dibangun menggunakan Python, Streamlit, dan Supabase. Dasbor ini didesain khusus untuk *freelancer* dengan arus kas fluktuatif (pemasukan tidak teratur), agar mereka bisa terus memantau **Runway Health** (jumlah hari bertahan) dan merencanakan **Virtual Envelopes**.

## Fitur Utama (Minimum Viable Product)
1. **PIN Gate Authentication**: Proteksi dasbor dengan *PIN rahasia*.
2. **Quick Add Form**: Pengisian pemasukan & pengeluaran sangat cepat bergaya clean card.
3. **Runway Health Calculator**: Menghitung berapa lama sisa uang Anda bisa membiayai pengeluaran harian rata-rata Anda.
4. **Pending Income Tracker**: Buat tagihan proyek yang sedang jalan, klik "Tandai Cair" dan uang otomatis masuk ke Saldo. Anda juga bisa mensimulasikan potongan sekian persen untuk dialokasikan langsung ke pengeluaran pajak & admin.
5. **Virtual Envelopes Viewer**: Visualisasikan sisa saldo Anda ke pos amplop secara persentase dinamis.
6. **Purchase Simulator**: Masukkan harga *Wishlist* Anda, lihat dampaknya terhadap *Runway Health* Anda sebelum "Checkout" di toko online.

---

## Struktur Proyek (Modular)
```text
Personal Financial Dashboard/
│
├── .gitignore               # Melindungi API Key & Secrets
├── requirements.txt         # Dependensi PIP
├── app.py                   # Main Streamlit Router/App (Injeksi CSS)
├── README.md                # Dokumentasi & Git Tutorial
│
├── .streamlit/              
│   ├── config.toml          # Konfigurasi Tema Clean SaaS (Warna Indigo & Sans Serif)
│   └── secrets.toml         # [TIDAK DI-UPLOAD] Konfigurasi URL dan PIN Akses
│
├── utils/
│   ├── auth.py              # Logika PIN Gate
│   ├── db.py                # Wrapper Supabase DB Connection (CRUD Transactions dll)
│   └── calculations.py      # Rumus Runway Health, Rata-rata Pengeluaran, dll.
│
└── components/
    ├── quick_add.py         # Formulir Tambah Transaksi
    ├── runway_health.py     # Metrik Dashboard Utama
    ├── pending_income.py    # List Piutang & Action Cair dengan Pajak
    ├── virtual_envelopes.py # Progress Bar Alokasi Amplop
    └── purchase_simulator.py# Form Simulasi FOMO Mitigasi
```

---

## Cara Menjalankan Secara Lokal (Local Setup)

1. Pastikan Anda punya Python (>=3.9). Install dependensinya di Terminal:
   ```bash
   pip install -r requirements.txt
   ```
2. Anda WAJIB membuat file rahasia untuk Supabase Credential dan PIN Aplikasi di alamat rute folder ini: `.streamlit/secrets.toml`. (Folder `.streamlit` harus dibuat manual, file ini diabaikan oleh git agar sangat aman).
   Isi file tersebut:
   ```toml
   APP_PIN = "123456"
   SUPABASE_URL = "https://<GANTI_DENGAN_URL_SUPABASE_ANDA>.supabase.co"
   SUPABASE_KEY = "eyJhb...<GANTI_DENGAN_ANON_KEY_ANDA>"
   ```
3. Jika script SQL di Dasbor Supabase Anda sudah selesai di-*run* (tabel `transactions`, `envelopes`, dan `pending_incomes` terbuat) dan *Row Level Security* (RLS) pada ke-3 tabel tersebut sudah **dinonaktifkan** via konsol Supabase , maka jalankan di Terminal:
   ```bash
   streamlit run app.py
   ```
4. Aplikasi akan otomatis terbuka di `http://localhost:8501`. 

---

## Panduan Deployment (Streamlit Community Cloud) & Push GitHub

Agar web dasbor bisa diakses daring lewat HP di mana saja, Anda perlu mengunggahnya ke GitHub lalu menyambungkannya ke Streamlit Cloud.

### Langkah 1: Terminal Git ke GitHub
Buka Terminal / Command Prompt Anda dan arahkan direktori kerjanya persis di *root folder* proyek ini (`Personal Financial Dashboard`), lalu ketik instruksi di bawah ini dengan urut:

1. **Inisialisasi Git Repository lokal:**
   ```bash
   git init
   ```
2. **Cek Status (Pastikan `.gitignore` bekerja dan `<folder>/.streamlit` TIDAK MASUK di list merah):**
   ```bash
   git status
   ```
3. **Tambahkan Semua File ke Staging:**
   ```bash
   git add .
   ```
4. **Berikan Pesan Commit Pertama (Atau Commit Pembaruan UI):**
   ```bash
   git commit -m "feat: rilis UI SaaS modern untuk arsitek finansial"
   ```
5. **Ubah branch utama menjadi `main`:**
   ```bash
   git branch -M main
   ```
6. **Hubungkan ke Repositori GitHub Anda:**
   *(Ganti URL berwarna di bawah dengan URL asli *repository* yang Anda peroleh di halaman GitHub Anda).*
   ```bash
   git remote add origin https://github.com/USERNAME-ANDA/NAMA-REPO-ANDA.git
   ```
7. **Unggah Kode ke origin:**
   ```bash
   git push -u origin main
   ```

### Langkah 2: Publikasi Web (Streamlit Cloud)
1. Setelah kode berhasil masuk ke GitHub Anda, buka dan login ke situs [share.streamlit.io](https://share.streamlit.io/).
2. Klik tombol merah **New App**.
3. Pilih kolom *Repository* dengan Repo GitHub yang Anda buat tadi, *Branch* = `main`, lalu *Main file path* = `app.py`.
4. **PENTING: JANGAN LANGSUNG KLIK DEPLOY!** Di bagian bawah formulir, klik fitur/link bertuliskan **Advanced Settings**.
5. Akan muncul kolom teks besar bernama *Secrets*. Silakan *Copy-Paste* nilai dari `.streamlit/secrets.toml` lokal Anda ke kotak Secrets Cloud ini secara persis (yaitu `APP_PIN`, `SUPABASE_URL`, dan `SUPABASE_KEY`).
6. Klik *Save*, lalu baru klik *Deploy!*.
7. Selesai! Tunggu beberapa saat (animasi oven Streamlit), dan aplikasi dasbor keuangan "Arsitek Finansial Pribadi" Anda dengan UI Clean SaaS sudah *online* serta aman dikunjungi!
