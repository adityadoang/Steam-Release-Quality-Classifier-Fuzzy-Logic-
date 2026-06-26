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
**SQLite** (Diimplementasikan menggunakan library bawaan Python `sqlite3` dan file database lokal `indie_games.db`). Database ini dirancang sebagai **Fuzzy Relational Database** (Model Tahani/Umano) yang secara fisik menyimpan nilai derajat keanggotaan ($\mu$) untuk masing-masing atribut linguistik di dalam kolom tabel, yaitu:
* `mu_bug_sangat_bersih`, `mu_bug_wajar`, `mu_bug_rusak` (derajat keanggotaan Kepadatan Bug)
* `mu_fps_patah_patah`, `mu_fps_stabil`, `mu_fps_lancar` (derajat keanggotaan Kualitas FPS)
* `mu_wishlist_sedikit`, `mu_wishlist_menjanjikan`, `mu_wishlist_meledak` (derajat keanggotaan Jumlah Wishlist)
* `mu_budget_kritis`, `mu_budget_aman`, `mu_budget_melimpah` (derajat keanggotaan Sisa Anggaran)
* `mu_quality_tunda`, `mu_quality_akses_awal`, `mu_quality_siap_rilis` (derajat keanggotaan Status Hasil Evaluasi)

---

**4. Query Database (Minimal 5) dan Masing-masing Peruntukannya:**

Berikut adalah 5 query/operasi database utama yang digunakan di dalam aplikasi (pada `database.py`, `main.py`, dan `seed.py`):

**Query 1: Pembuatan Tabel dengan Kolom Derajat Keanggotaan Fuzzy (DDL)**
```sql
CREATE TABLE IF NOT EXISTS draft_indie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    bug_density REAL,
    fps REAL,
    wishlist INTEGER,
    remaining_budget REAL,
    score REAL,
    status TEXT,
    -- Kolom Fuzzy Membership Degrees (μ)
    mu_bug_sangat_bersih REAL,
    mu_bug_wajar REAL,
    mu_bug_rusak REAL,
    mu_fps_patah_patah REAL,
    mu_fps_stabil REAL,
    mu_fps_lancar REAL,
    mu_wishlist_sedikit REAL,
    mu_wishlist_menjanjikan REAL,
    mu_wishlist_meledak REAL,
    mu_budget_kritis REAL,
    mu_budget_aman REAL,
    mu_budget_melimpah REAL,
    mu_quality_tunda REAL,
    mu_quality_akses_awal REAL,
    mu_quality_siap_rilis REAL
)
```
* **Peruntukan:** Dijalankan saat inisialisasi awal sistem (`database.py`) untuk membuat tabel `draft_indie` dengan skema fuzzy lengkap jika tabel belum ada.

**Query 2: Memasukkan Data Evaluasi Baru beserta Derajat Keanggotaannya (DML - Insert)**
```sql
INSERT INTO draft_indie (
    title, bug_density, fps, wishlist, remaining_budget, score, status,
    mu_bug_sangat_bersih, mu_bug_wajar, mu_bug_rusak,
    mu_fps_patah_patah, mu_fps_stabil, mu_fps_lancar,
    mu_wishlist_sedikit, mu_wishlist_menjanjikan, mu_wishlist_meledak,
    mu_budget_kritis, mu_budget_aman, mu_budget_melimpah,
    mu_quality_tunda, mu_quality_akses_awal, mu_quality_siap_rilis
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```
* **Peruntukan:** Digunakan pada endpoint `/api/evaluate` dan script `seed.py` untuk menyimpan data game baru beserta hasil evaluasi skor, status, dan 15 nilai derajat keanggotaan fuzzy ($\mu$) yang dihitung secara dinamis.

**Query 3: Penghitungan Jumlah Baris yang Memenuhi Kriteria Fuzzy (DML - Select Count)**
```sql
-- Contoh kueri dinamis untuk operator AND (MIN)
SELECT COUNT(*) FROM draft_indie WHERE mu_bug_sangat_bersih >= ? AND mu_fps_lancar >= ?
```
* **Peruntukan:** Digunakan di fungsi `get_fuzzy_games` (`main.py`) untuk menghitung total data game yang memenuhi kriteria fuzzy query dengan batas minimal alpha-cut tertentu, guna kebutuhan pagination secara dinamis langsung dari database.

**Query 4: Kueri Fuzzy Model Tahani (DML - Evaluasi Kondisi, Kalkulasi Derajat Kecocokan & Filter)**
```sql
-- Contoh kueri dinamis untuk operator AND (MIN)
SELECT *, MIN(mu_bug_sangat_bersih, mu_fps_lancar) AS match_degree
FROM draft_indie
WHERE mu_bug_sangat_bersih >= ? AND mu_fps_lancar >= ?
ORDER BY match_degree DESC, id DESC
LIMIT ? OFFSET ?
```
* **Peruntukan:** Merealisasikan kueri pencarian fuzzy Model Tahani langsung di level database SQLite. Pengguna dapat mencari game dengan kriteria fuzzy (misal: `Bug Bersih AND FPS Lancar`) dengan batas minimal tingkat kecocokan (Alpha-Cut) tertentu. Fungsi `MIN` (untuk `AND`) atau `MAX` (untuk `OR`) menghitung `match_degree` ($\mu$), menyaring baris berdasarkan alpha-cut di level database, mengurutkannya dari yang paling cocok, dan membatasi jumlah data per halaman.

**Query 5: Filter Kueri Standar Berdasarkan Status Kelayakan Tegas (DML - Select with Where)**
```sql
SELECT * FROM draft_indie WHERE status = ? ORDER BY id DESC LIMIT ? OFFSET ?
```
* **Peruntukan:** Digunakan pada pencarian kueri standar untuk menyaring riwayat game berdasarkan status kelayakan tegas (*crisp*) pilihan user secara cepat menggunakan index.

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
