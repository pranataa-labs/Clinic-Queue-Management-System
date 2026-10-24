# Project: pranataa-labs

**Stack:** Python Data & Software Application  
**Standards & Operating Workflow:** Terintegrasi penuh dengan [Workflow Master](https://github.com/pranataa-labs/workflow-master).

---

## 1. Operating Discipline & Engineering Workflow
Semua pekerjaan rekayasa pada repositori ini WAJIB mematuhi 9 tahapan alur kerja di workflow-master:
1. **Triage:** Pahami tujuan, klasifikasikan tipe tugas dan tingkat risiko (Low / Medium / High).
2. **Discover:** Periksa file terkait, konfigurasi, dan kontrak sebelum modifikasi.
3. **Design:** Rancang acceptance criteria dan batasan error.
4. **Plan:** Tentukan file dan urutan perubahan secara minimalis dan modular.
5. **Implement:** Tulis kode bersih, aman, dan mematuhi konvensi proyek.
6. **Verify:** Jalankan test suite, linter, atau typechecker yang tersedia.
7. **Review:** Periksa diff, otorisasi, dan cegah kebocoran rahasia / data.
8. **Release:** Verifikasi kesehatan rilis dan kelayakan deploy.
9. **Report:** Laporkan hasil verifikasi secara transparan.

---

## 2. Aturan Spesifik Proyek
- Utamakan kode terstruktur, reproduktifitas data, dan efisiensi komputasi.
- **Autonomous Project Scaffolding:** Ketika diminta membuat sistem/aplikasi baru berbasis domain (misal: toko buku, antrian klinik, kasir/POS), jangan tanyakan kebutuhan dasar (auth, keranjang, warna, font). Langsung terapkan **Rule 16 (Autonomous Domain Archetypes & Scaffolding)**: bangun full-stack dua sisi (Customer Flow + Admin Backoffice), terapkan sistem desain modern (*Smooth Blue & Slate*, font *Inter*), dan sertakan data awal realistis (*seed data*) beserta akun demo siap pakai.
