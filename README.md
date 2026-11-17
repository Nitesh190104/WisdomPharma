# Wisdom Pharma (Django + React)

A production-grade B2B + B2C pharmaceutical management and e-commerce platform built with **Django 5 (Python)** and **React 19 (Vite + Tailwind CSS)**, aligned with the **INT253: Web Development in Python using Django** curriculum.

---

## 🌟 Overview

Wisdom Pharma bridges pharmaceutical manufacturers, medical stores (B2B wholesale), and retail consumers (B2C) with role-based access, inventory tracking, prescription verification, order management, and AI-assisted care.

### Features
* **B2C Consumer Portal**: Browse medicines with images, retail pricing with GST breakdown, prescription upload, cart & checkout, order tracking, and Gemini AI Care Assistant.
* **B2B Medical Store Portal**: Register with GST and Drug License numbers, bulk ordering with tiered wholesale pricing, minimum order thresholds, and store analytics.
* **Admin Management Panel**: Real-time business analytics (revenue charts, order distribution, low-stock alerts), inventory controls, prescription verification, and medical store approvals.
* **INT253 Syllabus Portal (`/portal/`)**: Django template-based portal demonstrating all 6 units of the INT253 curriculum.

---

## 🏗️ Tech Stack

* **Backend**: Django 5.2, Django REST Framework (DRF), SimpleJWT Authentication, CORS Headers, WhiteNoise, Gunicorn
* **Frontend**: React 19, Vite, Tailwind CSS, Zustand, Framer Motion, Recharts, React Hot Toast
* **AI & External Integrations**: Google Gemini AI (Chatbot & Assistant), Razorpay Payment Gateway, SMTP Mail

---

## 📁 Repository Structure

```text
├── django_backend/          # Django 5 Backend & REST API
│   ├── apps/               # Modular Django apps (auth, medicines, cart, orders, etc.)
│   ├── templates/          # Django DTL templates (INT253 Units II, III, IV, VI)
│   ├── wisdom_pharma/      # Core settings, WSGI, ASGI, middleware, and root URLs
│   ├── Medicines/          # High-resolution .avif product images
│   ├── manage.py           # Django management CLI
│   ├── requirements.txt    # Python dependencies
│   ├── seed_data.py        # Database seeder (40 medicines, 8 categories, test accounts)
│   ├── Procfile            # Deployment process definition (Render/Railway/Heroku)
│   └── .env.example        # Environment variable template
├── frontend/               # React 19 + Vite Frontend SPA
│   ├── src/                # Components, pages, hooks, store, and services
│   ├── vercel.json         # SPA routing configuration for Vercel deployment
│   ├── package.json        # Node dependencies & build scripts
│   └── .env.example        # Frontend environment variable template
├── Medicines/              # Original catalog image assets
├── .gitignore              # Master gitignore protecting secrets and databases
└── README.md
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
* Python 3.10+ (Recommended: Python 3.12)
* Node.js 18+ & npm

### 2. Backend Setup (Django)
```bash
cd django_backend

# 1. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env from template
copy .env.example .env     # Windows
cp .env.example .env       # Linux/Mac

# 4. Run database migrations
python manage.py migrate

# 5. Seed the database with catalog and test users
python seed_data.py

# 6. Start the development server
python manage.py runserver 127.0.0.1:8000
```
Backend API will be accessible at: `http://127.0.0.1:8000/api/`  
Django Admin: `http://127.0.0.1:8000/admin/`  
Syllabus Portal: `http://127.0.0.1:8000/portal/`

### 3. Frontend Setup (React / Vite)
```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Create .env from template
copy .env.example .env     # Windows
cp .env.example .env       # Linux/Mac

# 3. Start development server
npm run dev
```
Frontend will be accessible at: `http://localhost:5173/`

---

## 🔑 Test Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `wisdom.admin@wisdompharma.com` | `WisdomAdmin@123` |
| **Consumer** | `rahul@example.com` | `password123` |
| **Medical Store** | `priya@medstore.com` | `password123` |

---

## 🚢 Deployment Guide

### Deploying the Backend (Render / Railway / VPS)
1. Set the **Root Directory** to `django_backend`.
2. **Build Command**:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python seed_data.py && python manage.py collectstatic --noinput
   ```
3. **Start Command**:
   ```bash
   gunicorn wisdom_pharma.wsgi --log-file -
   ```
4. Set environment variables based on `django_backend/.env.example`:
   * `SECRET_KEY`
   * `DEBUG=False`
   * `ALLOWED_HOSTS=*`
   * `FRONTEND_URL=https://your-frontend-deployment.vercel.app`
   * `GEMINI_API_KEY=your_key`

### Deploying the Frontend (Vercel / Netlify)
1. Connect this repository and set **Root Directory** to `frontend`.
2. **Framework Preset**: Vite
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`
5. Set Environment Variables:
   * `VITE_API_URL=https://your-backend.onrender.com/api`
   * `VITE_API_BASE_URL=https://your-backend.onrender.com/api`

---

## 📄 License
MIT License. Built for academic and educational purposes.
