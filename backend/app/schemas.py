from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# Auth Schemas
class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not v[0].isupper():
            raise ValueError("Password must start with a capital letter (A-Z)")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Password must contain at least one special symbol (!@#$%^&*)")
        return v

class UserLoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdateSchema(BaseModel):
    display_name: Optional[str] = None
    target_test_date: Optional[str] = None

class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    xp: int
    level: int
    streak_current: int
    streak_best: int
    target_test_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Question & Homework Schemas
class QuestionPublicSchema(BaseModel):
    id: int
    stem: str
    options: List[str]
    topic: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)

class QuestionAnswerSubmitSchema(BaseModel):
    selected_index: int

class AnswerResultSchema(BaseModel):
    question_id: int
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str

class HomeworkSubmitResultSchema(BaseModel):
    homework_id: str
    status: str
    score: str
    xp_rewarded: int
    newly_unlocked_badges: List[str] = []
    results: List[AnswerResultSchema]

class HomeworkPublicSchema(BaseModel):
    id: str
    lesson_id: Optional[str] = None
    title: str
    subject: str
    skill: str
    dueDate: str
    status: str # computed: not_started | in_progress | overdue | completed
    questionCount: int
    estTime: str
    xpReward: int
    score: Optional[str] = None

class HomeworkDetailSchema(HomeworkPublicSchema):
    questions: List[QuestionPublicSchema]

# Lesson Schemas
class LessonPublicSchema(BaseModel):
    id: str
    title: str
    subject: str
    module: Optional[str] = None
    duration: str
    duration_sec: int
    progress: int # computed from watched_seconds
    completed: bool
    videoUrl: str
    description: str
    keyTakeaways: List[str]
    transcript: List[Dict[str, Any]]
    relatedHomeworkId: Optional[str] = None

class LessonProgressUpdateSchema(BaseModel):
    watched_seconds: int
    completed: Optional[bool] = False

# Dashboard Schema
class DashboardSchema(BaseModel):
    user: UserPublicSchema
    targetDate: str
    headerCountdownText: str
    todayLesson: Optional[LessonPublicSchema] = None
    pendingHomework: List[HomeworkPublicSchema]
    leaderboardRank: int
    leaderboardTier: str
    attendanceRate: float

# Leaderboard Schema
class LeaderboardEntrySchema(BaseModel):
    rank: int
    name: str
    xp: int
    streak: int
    badge: str
    isUser: bool = False

class LeaderboardSchema(BaseModel):
    standings: List[LeaderboardEntrySchema]
    userRank: LeaderboardEntrySchema

# Attendance Schema
class AttendanceSessionSchema(BaseModel):
    day: int
    title: str
    time: str
    instructor: str

class AttendanceSchema(BaseModel):
    daysAttended: List[int]
    daysMissed: List[int]
    attendanceRate: float
    upcomingLiveSessions: List[AttendanceSessionSchema]

class CheckInResponseSchema(BaseModel):
    message: str
    xp_reward: int
    current_streak: int

# Badge Schema
class BadgePublicSchema(BaseModel):
    id: str
    code: str
    title: str
    desc: str
    unlocked: bool
    progress: str
    icon: str

# Flashcard Schema
class FlashcardSchema(BaseModel):
    id: str
    category: str
    title: str
    front: str
    back: str

    model_config = ConfigDict(from_attributes=True)
