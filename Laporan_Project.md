# Laporan Project Basis Data / Fuzzy Logic

**1. Nama Personel Kelompok Project:**
* Fikry Mumtaz Pratama (H1D024106)
* Aditya (H1D024107)
* Prapasha Budi Harimawan(H1D024112)

---

# Laporan Project Basis Data / Fuzzy Logic

**1. Nama Personel Kelompok Project:**
* Fikry Mumtaz Pratama (H1D024106)
* Aditya (H1D024107)
* Prapasha Budi Harimawan(H1D024112)

---

## 1. Metode
Aplikasi ini diimplementasikan menggunakan **Fuzzy Inference System (FIS) Mamdani**. Metode ini dipilih karena kemampuannya dalam memproses bahasa linguistik manusia (seperti "sangat bersih", "lancar", "menjanjikan") menjadi skor numerik (0-100) melalui proses defuzzifikasi. Implementasi teknis dilakukan menggunakan library `scikit-fuzzy` (`skfuzzy`) dalam bahasa pemrograman Python.

## 2. Alur Aplikasi (Application Flow)
Aplikasi berbasis web ini dikembangkan menggunakan framework **FastAPI** dengan alur kerja sebagai berikut:
1. **Input Pengguna:** Pengguna mengisi formulir evaluasi melalui antarmuka web (UI) yang mencakup: Judul Game, Kepadatan Bug, Frame Rate (FPS), Jumlah Wishlist, dan Sisa Budget (%).
2. **Proses Evaluasi:** Data dikirim via metode `POST` ke endpoint `/api/evaluate`. Backend memanggil fungsi `evaluate_quality()` untuk menjalankan logika Fuzzy Mamdani.
3. **Inferensi Fuzzy:** Sistem melakukan fuzzifikasi, evaluasi basis aturan, dan defuzzifikasi untuk menentukan skor akhir serta status kelayakan rilis.
4. **Penyimpanan Data:** Hasil evaluasi dan data input disimpan ke dalam database **SQLite** (pada tabel `draft_indie`).
5. **Output (Visualisasi):** Pengguna diarahkan kembali ke halaman utama. Halaman web menampilkan tabel riwayat evaluasi dengan fitur *pagination* dan filter status.

## 3. Implementasi Fuzzy
Implementasi FIS Mamdani terbagi dalam empat tahapan utama:

### A. Fuzzifikasi
Mengubah nilai numerik menjadi derajat keanggotaan menggunakan fungsi keanggotaan trapesium (`trapmf`):
* **Kepadatan Bug [0-15]:** Sangat Bersih [0, 0, 1, 3], Wajar [2, 4, 6, 8], Rusak [7, 9, 15, 15]
* **Performa (FPS) [0-120]:** Patah-patah [0, 0, 20, 30], Stabil [20, 30, 45, 55], Lancar [45, 60, 120, 120]
* **Jumlah Wishlist [0-50.000]:** Sedikit [0, 0, 4000, 6000], Menjanjikan [4000, 10000, 15000, 22000], Meledak [18000, 25000, 50000, 50000]
* **Sisa Anggaran [0-100%]:** Kritis [0, 0, 8, 12], Aman [8, 15, 35, 45], Melimpah [35, 45, 100, 100]
* **Output (Release Quality) [0-100]:** Tunda [0, 0, 35, 45], Akses Awal [35, 50, 65, 80], Siap Rilis [70, 85, 100, 100]

### B. Basis Aturan (Rule Base)
Sistem menggunakan logika IF-THEN untuk menentukan output:
* **Rule 1 (Kondisi Ekstrim):** IF (Bug: Rusak) OR (FPS: Patah) OR (Budget: Kritis) THEN (Quality: Tunda). *(Penjelasan: Sebagai fail-safe untuk menghindari reputasi buruk/review bombing.)*
* **Rule 2 (Kondisi Sempurna):** IF (Bug: Bersih) AND (FPS: Lancar) AND (Wishlist: Meledak) AND (Budget: Aman/Melimpah) THEN (Quality: Siap Rilis). *(Penjelasan: Skenario ideal untuk perilisan penuh 1.0.)*
* **Rule 3 (Kondisi Standar):** IF (Bug: Wajar) AND (FPS: Stabil) AND (Wishlist: Menjanjikan/Meledak) THEN (Quality: Akses Awal). *(Penjelasan: Memvalidasi model Early Access sebagai langkah pengembangan.)*
* **Rule 4 (Kualitas Tinggi, Marketing Kurang):** IF (Bug: Bersih) AND (FPS: Lancar) AND (Wishlist: Menjanjikan) THEN (Quality: Akses Awal).
* **Rule 5 (High Hype, High Bug):** IF (Bug: Rusak) AND (Wishlist: Meledak) AND (Budget: Melimpah) THEN (Quality: Akses Awal).
* **Rule 6 (Game Standar, Sepi):** IF (Bug: Wajar) AND (FPS: Stabil) AND (Wishlist: Sedikit) THEN (Quality: Tunda).
* **Rule 7 (Fallback - Main Aman):** IF (Bug: Bersih) AND (FPS: Stabil) AND (Wishlist: Sedikit) AND (Budget: Aman) THEN (Quality: Akses Awal).
* **Rule 8 (Fallback - Modal Besar):** IF (Bug: Wajar) AND (FPS: Lancar) AND (Budget: Melimpah) THEN (Quality: Akses Awal).
* **Rule 9 (Fallback - Kerugian Maksimal):** IF (Wishlist: Sedikit) AND (Budget: Aman) THEN (Quality: Tunda).

### C. Mesin Inferensi
Menggunakan fungsi implikasi (MIN) untuk memotong fungsi keanggotaan konsekuen dan agregasi (MAX) untuk menggabungkan area konsekuen.

### D. Defuzzifikasi & Fallback
Menggunakan metode **Centroid** untuk mendapatkan skor (0-100). Jika sistem mengalami *blind-spot* (`KeyError`), digunakan perhitungan empiris:
`Skor = (Norm_Bug * 30%) + (Norm_FPS * 30%) + (Norm_Wishlist * 20%) + (Norm_Budget * 20%)`

**Klasifikasi Keputusan Akhir:**
* **Skor ≤ 40:** Tunda / Rombak Total
* **Skor 41 - 75:** Rilis Akses Awal
* **Skor > 75:** Siap Rilis Penuh
