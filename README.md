# Shamix Prep SAT — Full-Stack Platform

A gamified Digital SAT test-prep platform built with FastAPI, SQLite (SQLAlchemy 2.0), Pydantic v2, Vanilla JS (`api.js` client layer), and Tailwind CSS.

---

## 📸 Screenshots Overview

The application includes responsive UI layouts supporting both desktop (1440px) and mobile (390px) viewports:

- **Auth View**: `docs/screenshots/01-auth-1440px.png` & `01-auth-390px.png`
- **Dashboard**: `docs/screenshots/dashboard-1440px.png` & `dashboard-390px.png`
- **Video Lessons**: `docs/screenshots/lessons-1440px.png` & `lessons-390px.png`
- **Lesson Detail & Player**: `docs/screenshots/lesson-modal-1440px.png` & `lesson-modal-390px.png`
- **Homework Hub**: `docs/screenshots/homework-1440px.png` & `homework-390px.png`
- **Interactive Quiz Runner**: `docs/screenshots/quiz-modal-1440px.png` & `quiz-modal-390px.png`
- **Stardust Leaderboard**: `docs/screenshots/leaderboard-1440px.png` & `leaderboard-390px.png`
- **Attendance & Check-in**: `docs/screenshots/attendance-1440px.png` & `attendance-390px.png`
- **Formula & Vocab Flashcards**: `docs/screenshots/flashcards-1440px.png` & `flashcards-390px.png`
- **Achievement Badges**: `docs/screenshots/badges-1440px.png` & `badges-390px.png`

---

## 🏛️ Text-Based Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  BROWSER CLIENT                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Single Page Application (frontend/index.html, app.js, styles.css)            |  |
|  | - Vanilla JS state manager & HTML renderer                                  |  |
|  | - XSS Sanitization via escapeHtml()                                         |  |
|  | - Responsive Layout (Desktop Sidebar / Mobile Bottom Navigation)              |  |
|  +-----------------------------------------------------------------------------+  |
|                                        |                                          |
|                       REST API requests (Bearer JWT Token)                        |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  | API Client Layer (frontend/api.js)                                           |  |
|  | - Fetch wrapper with timeout, 401 token eviction & error handler             |  |
|  +-----------------------------------------------------------------------------+  |
+----------------------------------------|------------------------------------------+
                                         |
                                  HTTP / JSON (REST)
                                         v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND SERVER                              |
|  +-----------------------------------------------------------------------------+  |
|  | FastAPI App (backend/app/main.py)                                            |  |
|  | - Dedicated StaticFiles mount ONLY on /frontend (System files return 404)    |  |
|  | - CORS Middleware & Rate Limiting                                          |  |
|  +-----------------------------------------------------------------------------+  |
|  | API Routers (/api/auth, /dashboard, /lessons, /homework, /leaderboard, etc.)  |  |
|  +-----------------------------------------------------------------------------+  |
|  | Services & Security                                                        |  |
|  | - JWT Auth & Bcrypt password hashing                                       |  |
|  | - Gamification Engine (Idempotent XP, streaks, level calculation, badges)   |  |
|  +-----------------------------------------------------------------------------+  |
|  | ORM Layer & Database                                                       |  |
|  | - SQLAlchemy 2.0 typed models & SQLite file (backend/data/shamix.db)         |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## ✨ Full Feature List

1. **Authentication & User Management**:
   - Register new student accounts (username 3+, email, password 8+).
   - Sign in with JWT access tokens stored securely in `localStorage["shamix_token"]`.
   - "Try Demo Account" shortcut link (`demo` / `Demo12345!`).
   - Password visibility toggle & user profile dropdown menu with sign out.
2. **Dashboard**:
   - Real-time user stats (XP, level title, current streak, target test date).
   - Today's recommended masterclass & pending homework drills list.
   - Customizable SAT target test date countdown timer.
3. **Video Lessons**:
   - Masterclass video player with transcript and key takeaways.
   - Debounced watch progress tracking (`POST /api/lessons/{id}/progress`).
   - Direct link to practice homework drill.
4. **Homework Hub & Interactive Quiz Runner**:
   - Server-computed status filters (`not_started`, `in_progress`, `overdue`, `completed`).
   - Quiz flow (`start` ➔ `answer` ➔ `submit`).
   - Server-side grading (correct answer index & explanation hidden until submitted).
   - Celebratory canvas confetti animation & XP reward display upon completion.
5. **Leaderboard**:
   - Standings table with `#1`, `#2`, `#3` gold/silver/bronze badges and generated initials SVG avatars.
   - Week vs. All Time period toggle.
   - Highlight caller row with `(You)` suffix & sticky rank summary footer.
6. **Attendance & Daily Check-in**:
   - Month grid navigation (`?month=YYYY-MM`) with present, absent, and upcoming indicators.
   - Idempotent daily check-in button awarding +50 XP and streak increment.
7. **Flashcards & Badges**:
   - Interactive 3D flip cards for SAT Math formulas & Reading vocabulary.
   - Achievement badges gallery (Unlocked vs Locked) including `"Night Learner 🌙"`.

---

## 🚀 How to Run & Setup

### 1. Environment Setup
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

### 2. Environment Variables & Secret Key Generation
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Generate a secure 64-character secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Configure `.env`:
```env
SECRET_KEY=YOUR_GENERATED_SECURE_SECRET_KEY_MIN_32_CHARS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./backend/data/shamix.db
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### 3. Database Seeding
Seed the database with mock lessons, homework, questions, flashcards, badges, and demo users:
```bash
python backend/seed.py
```

#### 🔑 Demo Credentials
- **Username**: `demo`
- **Password**: `Demo12345!`

### 4. Running Application Server
```bash
uvicorn backend.app.main:app --port 8080 --reload
```
Open browser at:
- 🌐 **Web App**: [http://localhost:8080](http://localhost:8080)
- 📖 **OpenAPI Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 🔒 Security Hardening

- **Static File Isolation**: StaticFiles mounted strictly on `frontend/`. Direct requests for system files (`/.env`, `/.git/config`, `/backend/data/shamix.db`, `/backend/app/config.py`, `/tests/conftest.py`) return **HTTP 404 Not Found**.
- **XSS Prevention**: All API data (`display_name`, `username`, question stems, titles) is sanitized via `escapeHtml()` prior to DOM insertion.
- **Secret Key Enforcement**: Application refuses startup if `SECRET_KEY` is missing, under 32 characters, or contains default placeholders.
- **Password Length**: Minimum 8 characters enforced across schemas, routes, and client forms.
- **Server-Side Grading**: Correct answers & explanations are withheld until student answers are submitted.

---

## ⚠️ Known Limitations

1. **In-Memory Rate Limiting**: Auth rate limiting uses an in-memory dictionary. In multi-process production deployments, Redis or Memcached should back the rate limiter.
2. **SQLite Database**: Uses single-file SQLite database suitable for development/demo. Production deployments should migrate to PostgreSQL.
3. **Demo Video Asset**: Video lessons point to a locally generated 10-second MP4 demo video (`/assets/demo-lesson.mp4`). Production video streaming would use HLS/DASH or Cloud Storage CDN.
4. **CDN Dependencies**: Frontend uses CDN links for Tailwind CSS, FontAwesome, and Canvas-Confetti with system font fallbacks (`Plus Jakarta Sans`, `system-ui`) and native font icon fallback labels.
