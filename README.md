<div align="center">

# 🏥 Clinic Queue Management System
### *Modern Polyclinic Audio Queue Calling & Real-Time TV Display System*

[![Next.js](https://img.shields.io/badge/Next.js-16.4.3-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.3.0-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![Laravel](https://img.shields.io/badge/Laravel-13.38-FF2D20?style=for-the-badge&logo=laravel)](https://laravel.com/)
[![PHP](https://img.shields.io/badge/PHP-8.3%2B-777BB4?style=for-the-badge&logo=php)](https://www.php.net/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4.3-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![shadcn/ui](https://img.shields.io/badge/Theme-shadcn_Smooth_Blue-2563eb?style=for-the-badge)](https://ui.shadcn.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

<br/>

[![typescript](https://img.shields.io/badge/typescript-%23007acc.svg?style=flat-square&logo=typescript&logoColor=white)](https://github.com/topics/typescript)
[![nextjs](https://img.shields.io/badge/nextjs-%23000000.svg?style=flat-square&logo=nextdotjs&logoColor=white)](https://github.com/topics/nextjs)
[![laravel](https://img.shields.io/badge/laravel-%23FF2D20.svg?style=flat-square&logo=laravel&logoColor=white)](https://github.com/topics/laravel)
[![queue-management](https://img.shields.io/badge/queue--management-2563eb?style=flat-square)](https://github.com/topics/queue-management)
[![tailwind](https://img.shields.io/badge/tailwind-%2338B2AC.svg?style=flat-square&logo=tailwind-css&logoColor=white)](https://github.com/topics/tailwind)
[![hospital-system](https://img.shields.io/badge/hospital--system-0284c7?style=flat-square)](https://github.com/topics/hospital-system)
[![shadcn-ui](https://img.shields.io/badge/shadcn--ui-0f172a?style=flat-square&logo=shadcnui&logoColor=white)](https://github.com/topics/shadcn-ui)
[![webrtc](https://img.shields.io/badge/webrtc-333333?style=flat-square&logo=webrtc&logoColor=white)](https://github.com/topics/webrtc)
[![speech-synthesis](https://img.shields.io/badge/speech--synthesis-10b981?style=flat-square)](https://github.com/topics/speech-synthesis)
[![healthcare](https://img.shields.io/badge/healthcare-4338ca?style=flat-square)](https://github.com/topics/healthcare)

<br/>

*An integrated clinic and hospital queue management platform featuring automated phonetic voice announcements (Indonesian TTS), live microphone broadcast via WebRTC, and a soothing shadcn Smooth Blue interface.*

---

</div>

## 📸 Screenshots

### 1. Waiting Room Public TV Display (`/`)
*Real-time public display for clinic waiting areas featuring large active queue ticket typography, 5-room queue status overview, automatic cyclical room rotation, and announcement running text.*

![Waiting Room TV Display](docs/screenshots/tv-display.png)

### 2. Doctor Examination Console (`/console`)
*Room-isolated examination workspace for practitioners with queue calling controls (Next / Recall), consultation lifecycle tracking, patient skip, live WebRTC microphone intercom to TV speakers, and Ishoma break toggle.*

![Doctor Examination Console](docs/screenshots/doctor-console.png)

---

## 📌 System Overview

**Clinic Queue Management System** is a modern healthcare queue automation platform engineered for medical facilities, primary care clinics, and specialized hospitals. It modernizes traditional clinic queue operations through high-fidelity phonetic voice synthesis, direct browser-to-TV microphone intercom, and strict Role-Based Workspace Isolation.

The platform provides 4 specialized portals:
1. **Public TV Display (`/`)**: High-contrast waiting room monitor displaying the actively called patient, multi-room status rotation, and announcement ticker.
2. **Doctor Console (`/console`)**: Dedicated medical staff console isolated per room. Physicians can call next patients, recall missing visitors, start/complete consultations, and speak directly through TV speakers via WebRTC with a 30-second safety countdown.
3. **Self-Service Kiosk (`/kiosk`)**: Patient ticketing terminal for autonomous registration across clinics and coverage categories (General, BPJS, and Priority).
4. **Admin Workspace (`/admin`)**: Centralized management dashboard for doctor rooms, polyclinic master records, live queue tracking, and TV display customization.

---

## ✨ Key Features

- **🎙️ Dual Audio Engine (Phonetic TTS + WebRTC Intercom):**
  - Indonesian voice synthesis with dual synthesized chime presets (Standard Bell & Urgent Dingdong).
  - Phonetic normalization for medical acronyms and abbreviations (e.g., "Poli Gigi & Mulut", "Poli Spesialis Jantung").
  - Live doctor microphone streaming to waiting room TV speakers over WebRTC with automatic timeout (30 seconds) and audio collision prevention.
- **🔒 Room-Level Access Isolation:**
  - Medical staff are strictly constrained to their designated room and assigned polyclinic queues.
  - Public portals (TV display and kiosk) are sanitized of administrative and physician control links.
- **☕ Service Pause & Ishoma (Prayer/Break) Mode:**
  - One-click break mode for practitioners with animated pause banners on TV displays and kiosk notices informing incoming patients of prayer and rest intervals.
- **🎨 Soothing shadcn Smooth Blue Design System:**
  - Clinical azure palette (`oklch(0.52 0.17 250)`) designed for high visual comfort in healthcare environments without harsh glare.
  - Crisp Google Font Inter typography optimized for long-distance legibility on waiting room displays.
- **⚡ High-Performance Architecture:**
  - Fast client/server rendering powered by Next.js 16 (Turbopack, App Router).
  - Robust Laravel 13 REST API backend backed by 100% automated test coverage.

---

## 🏗️ Technical Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | [Next.js 16.4.3](https://nextjs.org/) (React 19.3, TypeScript 5.9) | App Router architecture with Turbopack |
| **Styling & Icons** | [Tailwind CSS v4.3](https://tailwindcss.com/) & Lucide React | Soothing shadcn Smooth Blue design system (`oklch(0.52 0.17 250)`) |
| **Backend REST API** | [Laravel 13.38](https://laravel.com/) (PHP 8.3+) | Clean service-layer REST endpoints and seeders |
| **Database** | MySQL 8.0 / SQLite 3 | Relational schema with transactional queue integrity |
| **Audio Engine** | Web Speech Synthesis & Web Audio API | Client-side phonetic Indonesian TTS & algorithmic chime synthesis |
| **Live Intercom** | WebRTC DataChannel & MediaStream | Zero-latency browser-to-browser audio broadcast |
| **Test Suite** | PHPUnit 12.5 | 21 comprehensive feature tests (133 assertions) |

---

## 🚀 Installation & Getting Started

### Prerequisites
- **PHP** >= 8.3 & Composer
- **Node.js** >= 20.x (Recommended: v22 / v24) & npm
- **MySQL** >= 8.0 (or SQLite 3)

### 1. Clone the Repository
```bash
git clone https://github.com/pranataa-labs/Clinic-Queue-Management-System.git
cd Clinic-Queue-Management-System
```

### 2. Configure Backend (Laravel 13)
```bash
cd backend
composer install
cp .env.example .env
php artisan key:generate

# Configure your database credentials in .env, then migrate & seed:
php artisan migrate:fresh --seed
php artisan serve --port=8000
```
*Backend API will run at `http://localhost:8000`.*

### 3. Configure Frontend (Next.js 16)
Open a new terminal window in the project root:
```bash
cd frontend
npm install
npm run dev -- -p 3000
```
*Frontend application will run at `http://localhost:3000`.*

---

## 🖥️ Portal Navigation & Endpoints

| Endpoint URL | Portal Name | Target Audience / Device |
| :--- | :--- | :--- |
| `http://localhost:3000/` | **Waiting Room TV Display** | Public Waiting Hall (Wall-Mounted Smart TV) |
| `http://localhost:3000/console` | **Doctor Examination Console** | Physician Desks & Examination Rooms |
| `http://localhost:3000/kiosk` | **Self-Service Ticketing Kiosk** | Clinic Entrance / Reception Kiosk |
| `http://localhost:3000/admin` | **Central Admin Dashboard** | Clinic Administrators & IT Operators |

---

## 🧪 Automated Testing

Execute the backend test suite to verify queue dispatching, transaction safety, and edge cases:
```bash
cd backend
php artisan test
```

Execute static typing and Next.js production build verification:
```bash
cd frontend
npm run build
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<div align="center">
  <sub>Engineered with dedication by <a href="https://github.com/pranataa-labs">Pranataa Labs</a></sub>
</div>
