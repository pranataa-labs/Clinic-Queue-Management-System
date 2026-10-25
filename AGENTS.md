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
- **Machine Learning & Model Engineering:** Ketika membangun model Machine Learning (klasifikasi, regresi, time-series, clustering), WAJIB mematuhi **Rule 17 (Machine Learning & MLOps Engineering Rules)**: terapkan *Simple Baseline First*, kunci random seed global untuk reproduktifitas, cegah *Data Leakage* dengan `Pipeline` terpadu (fit hanya pada train set), lakukan evaluasi berorientasi bisnis (*Slice Analysis* & *Behavioral Tests*), serta lindungi inferensi runtime dengan validasi skema ketat.
- **AI Operational Discipline & Recurrent Error Prevention:** WAJIB mematuhi **Rule 18 (Agent Operational Discipline & Anti-Patterns)**:
  - *Contextual Synthesis over Blind Mimicry:* Jangan menyalin teks/topik referensi eksternal secara buta; sesuaikan dengan manifest aktual proyek (`package.json`, dll.).
  - *Clean Production Handoff:* Bersihkan seluruh bypass demo dan form pre-filled sebelum menyerahkan UI produksi.
  - *Strict Auth & Session Boundaries:* Kunci aksi tamu vs member (keranjang, checkout) dan sembunyikan elemen UI khusus member bagi tamu.
  - *Permanent Cache-Busting:* Gunakan nama file baru saat memperbarui gambar dokumentasi GitHub agar tidak terjebak cache proxy GitHub Camo.
  - *Feature-First Documentation:* Utamakan kapabilitas teknis dan fitur bisnis; jangan boroskan ruang untuk tabel kode warna.
  - *Unboxed Brand Assets:* Sajikan logo dan lambang brand melayang bebas (*free-floating*) tanpa kotak kartu pembungkus kaku.
- **Rule 12.1 — Dual-Account Co-Authorship & Pairing (Otomatis Tanpa Perintah):** Pada SETIAP commit Git di repositori ini, AI WAJIB menyertakan trailer co-author untuk akun kedua pengguna secara otomatis dan mandiri, TANPA perlu diminta atau diperintahkan lagi oleh pengguna:
  ```text
  Co-authored-by: aria sastra <192975116+ariasastra-dev@users.noreply.github.com>
  ```
  Aturan ini bersifat permanen dan non-negotiable serta membiasakan alur cabang & PR untuk menjaga sinkronisasi kontribusi dan membuka/meningkatkan tier badge GitHub (**Pair Extraordinaire**, **Pull Shark**, dan **YOLO**). DILARANG membuat commit tanpa trailer ini.
