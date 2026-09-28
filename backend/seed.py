import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import (
    User, Lesson, Homework, Question, Flashcard, Badge, ClassSession,
    UserBadge, XPEvent, AttendanceRecord, HomeworkAttempt, AttemptAnswer
)
from backend.app.security import hash_password
from backend.app.services.gamification import DEFAULT_TARGET_DATE

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        print("Seeding Shamix Prep SAT Database...")

        # 1. SEED BADGES
        badges_data = [
            {"id": "b1", "code": "night_owl", "name": "Night Learner 🌙", "description": "Complete 3 lessons after 8 PM", "icon": "fa-solid fa-moon text-indigo-400", "criteria": {"target": 3}},
            {"id": "b2", "code": "math_wiz", "name": "Math Wiz 📐", "description": "Score 100% on 5 Math homework drills", "icon": "fa-solid fa-calculator text-cyan-400", "criteria": {"target": 5}},
            {"id": "b3", "code": "7_day_flame", "name": "7-Day Flame 🔥", "description": "Maintain a 7-day study streak", "icon": "fa-solid fa-fire text-amber-400", "criteria": {"target": 7}},
            {"id": "b4", "code": "sat_1500_club", "name": "SAT 1500+ Club 🎯", "description": "Reach 1500+ predicted SAT score", "icon": "fa-solid fa-bullseye text-rose-400", "criteria": {"target": 1500}},
            {"id": "b5", "code": "perfect_attendance", "name": "Perfect Attendance 📅", "description": "Check in 15 days in a month", "icon": "fa-solid fa-calendar-check text-emerald-400", "criteria": {"target": 15}},
            {"id": "b6", "code": "graphing_dynamo", "name": "Graphing Dynamo ⚡", "description": "Use Graphing Calculator simulator 10 times", "icon": "fa-solid fa-bolt text-yellow-400", "criteria": {"target": 10}},
        ]
        for b in badges_data:
            existing_b = db.query(Badge).filter(Badge.id == b["id"]).first()
            if not existing_b:
                db.add(Badge(id=b["id"], code=b["code"], name=b["name"], description=b["description"], icon=b["icon"], criteria=b["criteria"]))
            else:
                existing_b.name = b["name"]
                existing_b.description = b["description"]

        # 2. SEED LESSONS
        lessons_data = [
            {
                "id": "les-1",
                "title": "Linear Equations & Slope-Intercept Mastery",
                "subject": "Math",
                "module": "Heart of Algebra",
                "duration_sec": 1080,
                "duration_str": "18 mins",
                "order": 1,
                "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
                "description": "Master system of linear equations, standard vs slope-intercept form, parallel/perpendicular lines, and SAT speed tricks.",
                "materials": {
                    "keyTakeaways": [
                        "Slope formula: m = (y2 - y1) / (x2 - x1)",
                        "Perpendicular slopes are negative reciprocals (m1 * m2 = -1)",
                        "System has infinitely many solutions when lines are identical"
                    ],
                    "transcript": [
                        {"time": 0, "text": "Welcome to today's Shamix Prep SAT lesson on Linear Equations!"},
                        {"time": 15, "text": "Let's first review the slope-intercept form y = mx + b."},
                        {"time": 45, "text": "Notice how the SAT frequently tests infinite solutions vs no solutions."},
                        {"time": 90, "text": "When two lines are parallel, their slopes m1 and m2 are equal."},
                        {"time": 130, "text": "Let's practice a real Digital SAT question from Module 1."}
                    ],
                    "relatedHomeworkId": "hw-1"
                }
            },
            {
                "id": "les-2",
                "title": "Digital SAT Reading: Deciphering Craft & Structure",
                "subject": "Reading & Writing",
                "module": "Information & Ideas",
                "duration_sec": 1320,
                "duration_str": "22 mins",
                "order": 2,
                "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
                "description": "Learn how to analyze author's tone, text structure, function of highlighted sentences, and vocabulary in context.",
                "materials": {
                    "keyTakeaways": [
                        "Eliminate answers with extreme language (e.g. 'always', 'never')",
                        "Locate pivot words like 'however', 'nonetheless', 'conversely'",
                        "Substitute choices back into sentence for context vocabulary"
                    ],
                    "transcript": [
                        {"time": 0, "text": "Craft and Structure makes up 28% of the Digital SAT Reading section."},
                        {"time": 30, "text": "Always read 1 sentence before and after the underlined text."}
                    ],
                    "relatedHomeworkId": "hw-2"
                }
            },
            {
                "id": "les-3",
                "title": "Advanced Circle Theorems & Coordinate Geometry",
                "subject": "Math",
                "module": "Geometry & Trig",
                "duration_sec": 1500,
                "duration_str": "25 mins",
                "order": 3,
                "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
                "description": "Master circle equations (x-h)² + (y-k)² = r², arc length ratios, radian conversions, and inscribed angle theorems.",
                "materials": {
                    "keyTakeaways": [
                        "Standard Circle Equation: (x - h)² + (y - k)² = r²",
                        "Complete the square to find center (h, k) and radius r",
                        "Radians to Degrees: Multiply by 180 / π"
                    ],
                    "transcript": [
                        {"time": 0, "text": "Circle geometry questions appear on every SAT test."}
                    ],
                    "relatedHomeworkId": "hw-3"
                }
            }
        ]
        for l in lessons_data:
            if not db.query(Lesson).filter(Lesson.id == l["id"]).first():
                db.add(Lesson(
                    id=l["id"], title=l["title"], subject=l["subject"], module=l["module"],
                    duration_sec=l["duration_sec"], duration_str=l["duration_str"], order=l["order"],
                    video_url=l["video_url"], description=l["description"], materials=l["materials"]
                ))

        # 3. SEED HOMEWORK & QUESTIONS
        homeworks_data = [
            {
                "id": "hw-1", "lesson_id": "les-1", "title": "Quadratic & Linear Systems Speed Drill",
                "subject": "Math", "skill": "Heart of Algebra", "due_date": "2026-10-15", "xp_reward": 150, "est_time": "12 mins",
                "questions": [
                    {
                        "stem": "If 3x + 2y = 18 and y = 2x - 5, what is the value of x?",
                        "options": ["A) x = 3", "B) x = 4", "C) x = 5", "D) x = 6"],
                        "correct_index": 1,
                        "explanation": "Substitute y = 2x - 5 into 3x + 2y = 18: 3x + 2(2x - 5) = 18 => 3x + 4x - 10 = 18 => 7x = 28 => x = 4.",
                        "topic": "Heart of Algebra", "difficulty": "Medium"
                    },
                    {
                        "stem": "A line in the xy-plane passes through (2, 7) and (4, 15). What is the slope of a line perpendicular to this line?",
                        "options": ["A) 4", "B) -4", "C) -1/4", "D) 1/4"],
                        "correct_index": 2,
                        "explanation": "Slope m = (15 - 7) / (4 - 2) = 8 / 2 = 4. The perpendicular slope is the negative reciprocal: -1/4.",
                        "topic": "Algebra / Systems", "difficulty": "Hard"
                    },
                    {
                        "stem": "Which of the following is equivalent to the expression (2x + 3)(x - 5)?",
                        "options": ["A) 2x² - 7x - 15", "B) 2x² - 13x - 15", "C) 2x² + 7x - 15", "D) 2x² - 2x - 15"],
                        "correct_index": 0,
                        "explanation": "FOIL expansion: 2x(x) + 2x(-5) + 3(x) + 3(-5) = 2x² - 10x + 3x - 15 = 2x² - 7x - 15.",
                        "topic": "Advanced Math", "difficulty": "Medium"
                    }
                ]
            },
            {
                "id": "hw-2", "lesson_id": "les-2", "title": "Paired Passages & Synthesis Reading Practice",
                "subject": "Reading & Writing", "skill": "Information & Ideas", "due_date": "2026-10-18", "xp_reward": 200, "est_time": "15 mins",
                "questions": [
                    {
                        "stem": "Passage 1 argues that solar flares primarily disrupt low-orbit satellite telemetry, while Passage 2 emphasizes their effect on high-voltage power grids. Based on both texts, how would the author of Passage 2 most likely respond to Passage 1's claim?",
                        "options": [
                            "A) By arguing that low-orbit satellite damage is vastly overstated.",
                            "B) By agreeing that space infrastructure is vulnerable, while noting ground infrastructure faces equal risk.",
                            "C) By claiming that high-voltage grids are completely immune to atmospheric electromagnetic pulses.",
                            "D) By suggesting that solar flares occur too infrequently to warrant concern."
                        ],
                        "correct_index": 1,
                        "explanation": "Passage 2 acknowledges space hazards but broadens the scope to terrestrial energy grids, making option B the most nuanced agreement.",
                        "topic": "Craft & Structure", "difficulty": "Hard"
                    }
                ]
            },
            {
                "id": "hw-3", "lesson_id": "les-3", "title": "Standard English Conventions & Transitions",
                "subject": "Reading & Writing", "skill": "Expression of Ideas", "due_date": "2026-09-25", "xp_reward": 120, "est_time": "10 mins",
                "questions": [
                    {
                        "stem": "Botanists studying the Amazonian canopy discovered three unclassified orchid species; ____ they published their findings in the International Journal of Plant Sciences.",
                        "options": ["A) consequently,", "B) however,", "C) nevertheless,", "D) on the other hand,"],
                        "correct_index": 0,
                        "explanation": "'Consequently' indicates a cause-and-effect relationship resulting from their discovery.",
                        "topic": "Standard English Conventions", "difficulty": "Easy"
                    }
                ]
            },
            {
                "id": "hw-4", "lesson_id": None, "title": "Geometry & Unit Circle Fundamentals",
                "subject": "Math", "skill": "Geometry & Trig", "due_date": "2026-09-20", "xp_reward": 150, "est_time": "15 mins",
                "questions": [
                    {
                        "stem": "In a right triangle, one angle measures 30° and the hypotenuse is 12. What is the length of the side opposite to the 30° angle?",
                        "options": ["A) 6", "B) 6√3", "C) 12√3", "D) 3"],
                        "correct_index": 0,
                        "explanation": "In a 30°-60°-90° special right triangle, the side opposite the 30° angle is half the length of the hypotenuse (12 / 2 = 6).",
                        "topic": "Geometry & Trig", "difficulty": "Medium"
                    }
                ]
            }
        ]
        for hw_item in homeworks_data:
            hw_obj = db.query(Homework).filter(Homework.id == hw_item["id"]).first()
            if not hw_obj:
                hw_obj = Homework(
                    id=hw_item["id"], lesson_id=hw_item["lesson_id"], title=hw_item["title"],
                    subject=hw_item["subject"], skill=hw_item["skill"], due_date=hw_item["due_date"],
                    xp_reward=hw_item["xp_reward"], est_time=hw_item["est_time"]
                )
                db.add(hw_obj)
                db.flush()

                for q_item in hw_item["questions"]:
                    db.add(Question(
                        homework_id=hw_obj.id, stem=q_item["stem"], options=q_item["options"],
                        correct_index=q_item["correct_index"], explanation=q_item["explanation"],
                        topic=q_item["topic"], difficulty=q_item["difficulty"]
                    ))

        # 4. SEED FLASHCARDS
        flashcards_data = [
            {"id": "fc-1", "deck": "default", "category": "Math Formula", "title": "Quadratic Formula", "front": "What is the Quadratic Formula to find roots of ax² + bx + c = 0?", "back": "x = (-b ± √(b² - 4ac)) / (2a)\n\nDiscriminant b² - 4ac:\n> 0 : 2 real roots\n= 0 : 1 real root\n< 0 : 0 real roots (complex)"},
            {"id": "fc-2", "deck": "default", "category": "Math Formula", "title": "Circle Standard Equation", "front": "What is the standard equation of a circle centered at (h, k) with radius r?", "back": "(x - h)² + (y - k)² = r²\n\nCenter: (h, k)\nRadius: r = √r²"},
            {"id": "fc-3", "deck": "default", "category": "Reading Vocab", "title": "Pragmatic (adj)", "front": "Define 'Pragmatic' & use it in a sentence", "back": "Definition: Dealing with things sensibly and realistically based on practical considerations.\n\nExample: 'The committee took a pragmatic approach to budget allocation.'"},
            {"id": "fc-4", "deck": "default", "category": "Reading Vocab", "title": "Ambivalent (adj)", "front": "Define 'Ambivalent' & give a synonym", "back": "Definition: Having mixed feelings or contradictory ideas about something.\n\nSynonyms: Equivocal, uncertain, undecided."}
        ]
        for fc in flashcards_data:
            if not db.query(Flashcard).filter(Flashcard.id == fc["id"]).first():
                db.add(Flashcard(id=fc["id"], deck=fc["deck"], category=fc["category"], title=fc["title"], front=fc["front"], back=fc["back"]))

        # 5. SEED CLASS SESSIONS
        sessions_data = [
            {"id": 1, "title": "SAT Math 800 Secrets Live Masterclass", "date": "2026-09-29", "day_num": 29, "time": "18:00 PM EST", "instructor": "Dr. Aris Thorne", "subject": "Math"},
            {"id": 2, "title": "Digital SAT Reading Speed & Vocabulary", "date": "2026-09-30", "day_num": 30, "time": "19:00 PM EST", "instructor": "Prof. Sarah Lin", "subject": "Reading & Writing"}
        ]
        for s in sessions_data:
            if not db.query(ClassSession).filter(ClassSession.id == s["id"]).first():
                db.add(ClassSession(id=s["id"], title=s["title"], date=s["date"], day_num=s["day_num"], time=s["time"], instructor=s["instructor"], subject=s["subject"]))

        # 6. SEED DEMO USER & 12 LEADERBOARD USERS
        demo_users_data = [
            {"username": "demo", "email": "demo@shamixprep.sat", "display_name": "Alex Stargazer (You)", "xp": 3450, "streak_current": 12, "streak_best": 15},
            {"username": "sophia_c", "email": "sophia@shamixprep.sat", "display_name": "Sophia Chen", "xp": 5820, "streak_current": 28, "streak_best": 30},
            {"username": "marcus_v", "email": "marcus@shamixprep.sat", "display_name": "Marcus Vance", "xp": 4210, "streak_current": 19, "streak_best": 22},
            {"username": "emily_t", "email": "emily@shamixprep.sat", "display_name": "Emily Thorne", "xp": 3100, "streak_current": 15, "streak_best": 18},
            {"username": "devon_k", "email": "devon@shamixprep.sat", "display_name": "Devon Kim", "xp": 2890, "streak_current": 8, "streak_best": 12},
            {"username": "zara_p", "email": "zara@shamixprep.sat", "display_name": "Zara Patel", "xp": 2450, "streak_current": 5, "streak_best": 10},
            {"username": "leo_r", "email": "leo@shamixprep.sat", "display_name": "Leo Rodriguez", "xp": 2100, "streak_current": 4, "streak_best": 8},
            {"username": "hannah_m", "email": "hannah@shamixprep.sat", "display_name": "Hannah Miller", "xp": 1850, "streak_current": 3, "streak_best": 6},
            {"username": "noah_w", "email": "noah@shamixprep.sat", "display_name": "Noah Wright", "xp": 1500, "streak_current": 2, "streak_best": 5},
            {"username": "olivia_d", "email": "olivia@shamixprep.sat", "display_name": "Olivia Davis", "xp": 1200, "streak_current": 1, "streak_best": 4},
            {"username": "ethan_h", "email": "ethan@shamixprep.sat", "display_name": "Ethan Hunt", "xp": 950, "streak_current": 0, "streak_best": 3},
            {"username": "chloe_b", "email": "chloe@shamixprep.sat", "display_name": "Chloe Bennett", "xp": 600, "streak_current": 0, "streak_best": 2}
        ]

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for u_data in demo_users_data:
            user = db.query(User).filter(User.username == u_data["username"]).first()
            if not user:
                password_str = "Demo12345!" if u_data["username"] == "demo" else "Password123!"
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    password_hash=hash_password(password_str),
                    display_name=u_data["display_name"],
                    xp=u_data["xp"],
                    level=max(1, int(u_data["xp"] / 500) + 1),
                    streak_current=u_data["streak_current"],
                    streak_best=u_data["streak_best"],
                    last_activity_date=today_str,
                    target_test_date=DEFAULT_TARGET_DATE
                )
                db.add(user)
                db.flush()

                # Generate XP Events for user
                db.add(XPEvent(user_id=user.id, amount=u_data["xp"], reason="Initial seed XP", created_at=datetime.now(timezone.utc)))

                # Generate Attendance records for user
                attended_days = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25, 26, 27]
                for day in attended_days[:15]:
                    check_str = f"2026-09-{str(day).zfill(2)}"
                    db.add(AttendanceRecord(user_id=user.id, check_date=check_str, status="present"))

                # Assign badges for demo user
                if u_data["username"] == "demo":
                    db.add(UserBadge(user_id=user.id, badge_id="b1"))
                    db.add(UserBadge(user_id=user.id, badge_id="b2"))
                    db.add(UserBadge(user_id=user.id, badge_id="b3"))
                    db.add(UserBadge(user_id=user.id, badge_id="b6"))

                    # Assign homework completion for demo user
                    att = HomeworkAttempt(
                        user_id=user.id, homework_id="hw-4", status="completed",
                        score="100%", started_at=datetime.now(timezone.utc), submitted_at=datetime.now(timezone.utc)
                    )
                    db.add(att)

        db.commit()
        print("Shamix Prep SAT Database Seeded Successfully!")
        print("--------------------------------------------------")
        print("DEMO ACCOUNT CREDENTIALS:")
        print("   Username: demo")
        print("   Password: Demo12345!")
        print("--------------------------------------------------")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
