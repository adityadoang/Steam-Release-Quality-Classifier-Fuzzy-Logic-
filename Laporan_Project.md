# Laporan Project Basis Data / Fuzzy Logic

**1. Nama Personel Kelompok Project:**
* Fikry Mumtaz Pratama (H1D024106)
* Aditya (H1D024107)
* Prapasha Budi Harimawan(H1D024112)

---

**2. Topik Project yang Diangkat:**
**Steam Release Quality Classifier** 
Sebuah aplikasi web berbasis **Fuzzy Database System** yang dirancang untuk memprediksi apakah suatu draft game indie sudah layak untuk mendapatkan pendanaan dan dirilis di platform (seperti Steam). Aplikasi ini mengevaluasi data teknis pengembangan (bug density, fps, wishlist, remaining budget) menggunakan Mamdani Fuzzy Inference System untuk mengklasifikasikan status rilis game (Tunda/Rombak Total, Rilis Akses Awal, atau Siap Rilis Penuh).

---

**3. Database yang Dipakai:**
**SQLite** (Diimplementasikan menggunakan library bawaan Python `sqlite3` dan file database lokal `indie_games.db`).

---

**4. Query Database (Minimal 5) dan Masing-masing Peruntukannya:**

Berikut adalah 5 query SQL utama yang digunakan di dalam aplikasi (pada `database.py`, `main.py`, dan `seed.py`):

**Query 1: Pembuatan Tabel (DDL)**
```sql
CREATE TABLE IF NOT EXISTS draft_indie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    bug_density REAL,
    fps REAL,
    wishlist INTEGER,
    remaining_budget REAL,
    score REAL,
    status TEXT
)
```
* **Peruntukan:** Digunakan saat inisialisasi awal sistem (`database.py`) untuk membuat skema tabel `draft_indie` jika tabel tersebut belum ada di database. Tabel ini berfungsi untuk menyimpan seluruh data input game beserta hasil perhitungan fuzzzynya.

**Query 2: Menampilkan Seluruh Data (DML - Select)**
```sql
SELECT * FROM draft_indie
```
* **Peruntukan:** Digunakan pada route halaman utama (`/` di `main.py`) untuk mengambil keseluruhan data game yang telah tersimpan di dalam database, untuk kemudian ditampilkan ke dalam bentuk tabel di halaman web pengguna (dashboard).

**Query 3: Memasukkan Data Evaluasi Baru (DML - Insert)**
```sql
INSERT INTO draft_indie (title, bug_density, fps, wishlist, remaining_budget, score, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
```
* **Peruntukan:** Digunakan pada endpoint `/api/evaluate` (`main.py`) untuk menyimpan data game baru yang diinputkan pengguna melalui form (beserta hasil skor dan status perhitungan fuzzy logic) ke dalam database.

**Query 4: Filter Data Berdasarkan Status (DML - Select with Where)**
```sql
SELECT * FROM draft_indie WHERE status = ?
```
* **Peruntukan:** Digunakan pada endpoint `/api/query` (`main.py`) untuk fitur filter pencarian. Query ini mengambil daftar game secara spesifik berdasarkan hasil status kelayakannya (misal: hanya menampilkan game yang berstatus "Siap Rilis Penuh").

**Query 5: Mengecek Jumlah Data (DML - Aggregate)**
```sql
SELECT COUNT(*) FROM draft_indie
```
* **Peruntukan:** Digunakan di dalam fungsi seeding (`seed.py`) untuk menghitung total baris/record yang ada di tabel. Tujuannya adalah untuk memastikan agar mock data/data awal tidak dimasukkan dua kali (data hanya di-insert jika tabel masih kosong/jumlahnya 0).

---

**5. Screenshot Pemakaian Database dan Query-nya:**

*(Instruksi untuk Anda: Sisipkan screenshot di bawah ini sebelum di-convert ke PDF)*

* **Screenshot 1: Struktur Tabel atau Isi Data di Database Client (misal: menggunakan DB Browser for SQLite atau DBeaver)**
  
  ![[Sisipkan Screenshot Database Disini]]()

* **Screenshot 2: Tampilan Web saat menampilkan hasil query `SELECT * FROM draft_indie` (Halaman Utama/Tabel Dashboard)**
  
  ![[Sisipkan Screenshot Tabel di Web Disini]]()

* **Screenshot 3: Penggunaan fitur Filter Status (Hasil query `SELECT * FROM draft_indie WHERE status = ?`) di Web**
  
  ![[Sisipkan Screenshot Filter Disini]]()

---
*Catatan: Dokumen ini dalam format Markdown (.md). Anda bisa menggunakan fitur "Export to PDF" di aplikasi seperti VS Code (menggunakan ekstensi Markdown PDF), Typora, atau convert secara online (seperti markdowntopdf.com) setelah mengisi bagian yang kosong.*
