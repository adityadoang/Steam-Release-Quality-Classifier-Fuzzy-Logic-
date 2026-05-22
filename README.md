# 🎮 Steam Release Quality Classifier

Sebuah aplikasi web berbasis **Fuzzy Database System** yang dirancang untuk memprediksi apakah suatu draft game indie sudah layak untuk mendapatkan pendanaan dan dirilis di platform seperti Steam, berdasarkan data teknis awal pengembangan.

Aplikasi ini menggunakan **Mamdani Fuzzy Inference System** untuk mengevaluasi parameter game dan mengategorikannya ke dalam tiga keputusan: *Tunda/Rombak Total*, *Rilis Akses Awal (Early Access)*, atau *Siap Rilis Penuh*.

---

## 🛠️ Teknologi yang Digunakan
- **Backend:** Python dengan Framework **FastAPI**
- **Fuzzy Logic Engine:** `scikit-fuzzy`
- **Database:** SQLite dengan ORM **SQLAlchemy**
- **Frontend:** HTML, CSS, dan **Bootstrap 5** (Jinja2 Templates)

---

## ⚙️ Variabel Fuzzy Logic
Sistem menggunakan 4 variabel Input (Antecedent) dan 1 variabel Output (Consequent):

### Input:
1. **Bug Density** (Bugs per jam bermain)
   - Sangat Bersih (0-2), Wajar (3-7), Rusak (>8)
2. **Optimization** (Rata-rata Frame Rate / FPS)
   - Patah-patah (0-25), Stabil 30fps (25-50), Lancar 60fps+ (>50)
3. **Wishlist Count** (Jumlah pemain yang menantikan game)
   - Sedikit (0-5000), Menjanjikan (5000-20000), Meledak (>20000)
4. **Remaining Budget** (Sisa anggaran produksi dalam %)
   - Kritis (0-10%), Aman (10-40%), Melimpah (>40%)

### Output:
- **Tunda/Rombak Total** (Skor: 0-40)
- **Rilis Akses Awal** (Skor: 40-75)
- **Siap Rilis Penuh** (Skor: 75-100)

*(Catatan: Jika ada kombinasi input yang tidak tercakup dalam Rule Base utama, sistem akan melakukan estimasi kalkulasi bobot (Fallback) untuk memastikan stabilitas).*

---

## 🚀 Cara Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal:

### 1. Buat dan Aktifkan Virtual Environment
Buka terminal (Command Prompt / PowerShell) di dalam folder project ini, lalu jalankan:
```bash
python -m venv venv

# Untuk Windows (PowerShell/CMD):
.\venv\Scripts\activate

# Untuk Mac/Linux:
source venv/bin/activate
```

### 2. Instal Dependensi (Library)
```bash
pip install -r requirements.txt
```

### 3. Seed Database (Opsional, untuk data awal)
Jalankan script ini **sekali saja** untuk membuat file database `indie_games.db` dan mengisinya dengan 5 game contoh (dummy):
```bash
python seed.py
```

### 4. Jalankan Server FastAPI
```bash
uvicorn main:app --reload
```

### 5. Akses Aplikasi
Buka browser (Chrome, Firefox, Edge) dan kunjungi alamat berikut:
👉 **http://localhost:8000**

---

## 📂 Struktur Direktori
```text
📦 projek
 ┣ 📂 templates           # Direktori berisi file HTML (UI Frontend)
 ┃ ┗ 📜 index.html        # Halaman dashboard utama
 ┣ 📜 database.py         # Konfigurasi koneksi database SQLite (SQLAlchemy)
 ┣ 📜 fuzzy_logic.py      # Implementasi Mamdani Fuzzy Rules & Fallback
 ┣ 📜 main.py             # File utama FastAPI (Routing, API, & Controller)
 ┣ 📜 models.py           # Skema tabel database (DraftIndie)
 ┣ 📜 requirements.txt    # Daftar library Python yang dibutuhkan
 ┣ 📜 seed.py             # Script untuk mengisi mock data ke dalam database
 ┗ 📜 .gitignore          # File pengecualian git
```
