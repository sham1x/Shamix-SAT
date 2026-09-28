# Shamix Prep SAT — Full-Stack Platform

A gamified SAT test-prep web application built with FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2, Vanilla JS (`api.js` layer), and Tailwind CSS.

---

## 🎯 Full-Stack Architecture & Mapping

The application operates as a full-stack platform:
- **Backend API**: Production FastAPI app serving structured endpoints under `/api`.
- **Frontend App**: Pure Vanilla JS SPA in `frontend/` (`index.html`, `api.js`, `app.js`, `styles.css`) served via FastAPI StaticFiles.

### Screen & API Mapping Table

| Screen View | API Endpoints Used | Fields & Features |
|---|---|---|
| **Auth (Sign In / Register)** | `POST /api/auth/login`<br>`POST /api/auth/register`<br>`GET /api/auth/me` | Username (3+), Email, Password (8+ with toggle), Display Name, Demo login link, JWT token storage in `localStorage["shamix_token"]`. |
| **Dashboard** | `GET /api/dashboard`<br>`PATCH /api/auth/me` | Today's recommended masterclass, pending homework drills, leaderboard rank, daily streak, XP, level, target test date countdown timer. |
| **Video Lessons** | `GET /api/lessons`<br>`GET /api/lessons/{id}`<br>`POST /api/lessons/{id}/progress` | Video player, duration, subject tags, transcript, key takeaways, debounced watch progress tracking, direct homework drill link. |
| **Homework Hub** | `GET /api/homework`<br>`GET /api/homework/{id}`<br>`POST /api/homework/{id}/start`<br>`POST /api/homework/{id}/answer`<br>`POST /api/homework/{id}/submit` | Filter tabs (Not Started, In Progress, Overdue, Completed), quiz runner flow, server-side grading, instant answer feedback & solution breakdown, celebratory confetti animation, XP & badge reward modal. |
| **Leaderboard** | `GET /api/leaderboard?period=week\|all_time` | Standing ranks (#1, #2, #3 gold/silver/bronze icons), generated initials SVG avatars, display name, XP, streak, current user highlight row & sticky rank footer. |
| **Attendance & Check-in** | `GET /api/attendance?month=YYYY-MM`<br>`POST /api/attendance/check-in` | Month grid navigation, present/absent/upcoming indicators, attendance percentage, idempotent daily check-in (+50 XP). |
| **Flashcards** | `GET /api/flashcards` | Interactive flip cards (Math formulas & Reading vocabulary). |
| **Badges** | `GET /api/badges` | Unlocked vs locked badges with criteria, icons, and progress tracking. |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+

### 2. Environment Setup
Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables & Secret Key Generation
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Generate a secure 64-character secret key using Python:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated string into your `.env` file as `SECRET_KEY`:
```env
SECRET_KEY=YOUR_GENERATED_SECURE_SECRET_KEY_MIN_32_CHARS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./backend/data/shamix.db
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

> ⚠️ **Note**: The application will refuse to start if `SECRET_KEY` is missing, under 32 characters long, or contains placeholder values.

### 4. Database Seeding
Seed the database with all lessons, homework, questions, flashcards, badges, and demo users:

```bash
python backend/seed.py
```

#### 🔑 Demo Account Credentials
- **Username**: `demo`
- **Password**: `Demo12345!` (Minimum password length is 8 characters)

---

## 🖥️ Running the Application Server

Launch the full-stack server (FastAPI backend serving `/api` API endpoints and static assets from `frontend/`):

```bash
uvicorn backend.app.main:app --port 8080 --reload
```

Open your browser at:
- 🌐 **Web App**: [http://localhost:8080](http://localhost:8080)
- 📖 **OpenAPI Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 🧪 Running Automated Tests

Run the full pytest suite:

```bash
pytest -v
```

---

## 🔒 Security Hardening & Quality Control

1. **XSS Prevention**: All user-controlled text (`display_name`, `username`, question stems, titles) is sanitized using an `escapeHtml()` helper before DOM insertion.
2. **Static File Isolation**: Frontend files (`index.html`, `api.js`, `app.js`, `styles.css`) are served strictly from `frontend/`. System files (`.env`, `.git/config`, `backend/data/shamix.db`, `config.py`, test files) return `404 Not Found`.
3. **Secret Key Enforcement**: `SECRET_KEY` must be configured via environment/`.env` and must be at least 32 characters long without placeholders.
4. **Password Security**: Passwords require a minimum length of 8 characters enforced in Pydantic schemas, route handlers, and client forms.
5. **CORS Hardening**: Wildcard CORS fallbacks are disabled. Empty `ALLOWED_ORIGINS` permits no cross-origin requests.
6. **Rate Limiting**: Auth endpoints (`/auth/login`, `/auth/register`) return `429 Too Many Requests` when limits are exceeded.
7. **Initials Avatars**: Hotlinked external person images are replaced with generated initials SVG avatars using deterministic background gradients.
