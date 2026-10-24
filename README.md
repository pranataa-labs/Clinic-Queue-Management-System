<div align="center">

# 🏥 Clinic Queue Management System
### *Modern Polyclinic Audio Queue Calling & Real-Time TV Display System*

[![Next.js](https://img.shields.io/badge/Next.js-16.4-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Laravel](https://img.shields.io/badge/Laravel-12.0-FF2D20?style=for-the-badge&logo=laravel)](https://laravel.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![shadcn/ui](https://img.shields.io/badge/Theme-shadcn_Green-16a34a?style=for-the-badge)](https://ui.shadcn.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

*Sistem antrean poliklinik rumah sakit terintegrasi dengan pemanggilan suara otomatis (Indonesian TTS), interkom mikrofon langsung via WebRTC, dan antarmuka display TV berdesain modern bertema shadcn Green.*

---

</div>

## 📌 Gambaran Umum Sistem

**Clinic Queue Management System** adalah platform otomasi manajemen antrean layanan kesehatan modern yang dirancang untuk faskes, klinik pratama, dan rumah sakit. Sistem ini menggantikan pemanggilan antrean konvensional dengan perpaduan audio sintesis fonetik berkualitas tinggi, siaran mikrofon interkom langsung dokter ke pengeras suara TV, serta pemisahan hak akses kerja (*Role-Based Workspace Isolation*).

Sistem memiliki 4 modul utama:
1. **Layar Display TV (`/`)**: Layar display publik ruang tunggu dengan sorotan antrean aktif, rotasi 5 bilik/ruangan dokter, dan teks berjalan (*running text*).
2. **Konsol Dokter (`/console`)**: Konsol pemeriksaan dokter terisolasi per ruangan. Dokter memanggil pasien berikutnya (*Next*), panggil ulang (*Recall*), lewati (*Skip*), dan berbicara langsung via mikrofon interkom WebRTC dengan pengaman *auto-off* 30 detik.
3. **Kiosk Pendaftaran Mandiri (`/kiosk`)**: Anjungan tiket mandiri pasien untuk memilih poliklinik tujuan dan kategori (Umum, BPJS, Prioritas) dengan cetak struk antrean realtime.
4. **Dashboard Admin (`/admin`)**: Panel manajemen terpusat untuk mengelola master data ruangan/bilik, master poliklinik, monitoring antrean seluruh poli, dan konfigurasi teks display TV.

---

## ✨ Fitur Utama

- **🎙️ Dual Audio Engine (TTS Fonetik + WebRTC Intercom):**
  - Pemanggilan suara antrean berbahasa Indonesia dengan nada lonceng (*chime*) ganda (Standard Bell & Urgent Dingdong).
  - Normalisasi fonetik singkatan nama poli (contoh: "Poli Gigi & Mulut", "Poli Spesialis Jantung").
  - Mikrofon interkom dokter langsung ke speaker TV via WebRTC dengan proteksi *anti-lupa* (otomatis mati dalam 30 detik) dan pencegahan tabrakan audio (*audio collision avoidance*).
- **🔒 Isolasi Hak Akses Per Ruangan:**
  - Setiap dokter hanya dapat mengakses, melihat antrean, dan memanggil pasien di ruangannya sendiri.
  - Halaman publik (TV & Kiosk) steril dari tautan konsol dokter dan menu admin.
- **🎨 UI/UX Bersih Bertema shadcn Green:**
  - Mengadopsi prinsip desain `leoMirandaa/shadcn-landing-page` (shadcn Green theme, zinc neutrals, hairline borders).
  - Tipografi tegas dan tebal (*subpixel antialiased ClearType*) yang nyaman dan mudah terbaca dari jarak pandang jauh di ruang tunggu.
- **⚡ Arsitektur Terintegrasi & Performa Tinggi:**
  - Frontend Next.js 16 (Turbopack, App Router) dengan reaktivitas state cepat.
  - Backend Laravel 12 REST API dengan seeder klinik komprehensif dan integritas pengujian otomatis 100%.

---

## 🏗️ Arsitektur Teknologi

| Komponen | Teknologi | Keterangan |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16.4 (React 19, TypeScript) | Server & Client Components dengan Turbopack |
| **Styling** | Tailwind CSS v4 & Lucide Icons | Desain bertema shadcn Green (`hsl(142.1 76.2% 36.3%)`) |
| **Backend API** | Laravel 12 (PHP 8.2+) | Endpoint RESTful untuk antrean, display state, dan admin CRUD |
| **Database** | MySQL / SQLite | Didukung migrasi skema relasional dan seeder poliklinik |
| **Audio Engine** | Web Speech Synthesis & Web Audio API | Sintesis suara fonetik & generator chime sintetis |
| **Intercom** | WebRTC DataChannel & MediaStream | Siaran mikrofon live dokter ke speaker TV |

---

## 🚀 Panduan Instalasi & Menjalankan Proyek

### Prasyarat
- PHP >= 8.2 & Composer
- Node.js >= 20.x & npm
- MySQL (atau SQLite)

### 1. Kloning Repositori
```bash
git clone https://github.com/pranataa-labs/Clinic-Queue-Management-System.git
cd Clinic-Queue-Management-System
```

### 2. Konfigurasi Backend (Laravel)
```bash
cd backend
composer install
cp .env.example .env
php artisan key:generate

# Konfigurasi database di file .env sesuai lingkungan Anda, lalu jalankan:
php artisan migrate:fresh --seed
php artisan serve --port=8000
```
*Backend akan aktif di `http://localhost:8000`.*

### 3. Konfigurasi Frontend (Next.js)
Buka terminal baru di direktori root:
```bash
cd frontend
npm install
npm run dev -- -p 3000
```
*Frontend akan aktif di `http://localhost:3000`.*

---

## 🖥️ Rute & Navigasi Antarmuka

| URL | Halaman | Pengguna Sasaran |
| :--- | :--- | :--- |
| `http://localhost:3000/` | **Layar Display TV** | Ruang Tunggu Pasien (Monitor TV) |
| `http://localhost:3000/console` | **Konsol Ruangan Dokter** | Dokter & Tenaga Medis Pemeriksa |
| `http://localhost:3000/kiosk` | **Anjungan Kiosk Pasien** | Pasien / Pengunjung Mandiri |
| `http://localhost:3000/admin` | **Dashboard Admin** | Petugas Administrasi / IT RS |

---

## 🧪 Pengujian Otomatis

Jalankan test suite backend untuk memverifikasi integritas API antrean:
```bash
cd backend
php artisan test
```

Verifikasi build produksi frontend Next.js:
```bash
cd frontend
npm run build
```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi [MIT License](LICENSE).

<div align="center">
  <sub>Developed with ❤️ by <a href="https://github.com/pranataa-labs">Pranataa Labs</a></sub>
</div>
