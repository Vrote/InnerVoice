# backend/database/models.py
import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    streak_count = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)

    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    voice_profile = relationship("VoiceProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    followup_question = Column(Text, nullable=True)
    followup_answer = Column(Text, nullable=True)
    followup_pending = Column(Boolean, default=False)
    session_id = Column(String, nullable=True)
    processing_status = Column(String, default="pending") # pending|thinking|waiting_for_user|done|error
    agent_plan = Column(Text, nullable=True)       # JSON string of plan
    tools_used = Column(Text, nullable=True)       # JSON string array of tools

    user = relationship("User", back_populates="messages")

class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    primary_emotion = Column(String, nullable=False)
    secondary_emotion = Column(String, nullable=True)
    intensity = Column(Float, nullable=False)
    mood_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    raw_metadata = Column(Text, nullable=True)      # JSON string metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    memory_text = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False)    # goal|hobby|relationship|fear|achievement|habit|preference|context
    importance_score = Column(Float, default=0.5)
    source_message_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_referenced = Column(DateTime, nullable=True)
    reference_count = Column(Integer, default=0)

class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(String, nullable=True)        # career|health|habit|relationship|learning|personal
    status = Column(String, default="active")        # active|completed|paused|abandoned
    progress_notes = Column(Text, default="[]")      # JSON string array
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    target_date = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    source_message_id = Column(String, nullable=True)
    ai_suggested = Column(Boolean, default=True)

class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    pattern_description = Column(Text, nullable=False)
    pattern_type = Column(String, nullable=True)     # emotional|behavioral|temporal|social
    confidence = Column(Float, nullable=True)
    first_detected = Column(DateTime, default=datetime.datetime.utcnow)
    last_confirmed = Column(DateTime, nullable=True)
    occurrence_count = Column(Integer, default=1)

class FollowupTurn(Base):
    __tablename__ = "followup_turns"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    turn_number = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    avg_sentence_length = Column(Float, default=0.0)
    avg_entry_length = Column(Float, default=0.0)
    formality_score = Column(Float, default=0.5)
    hinglish_ratio = Column(Float, default=0.0)
    uses_english_only = Column(Boolean, default=True)
    detected_languages = Column(String, default="english")
    uses_ellipsis = Column(Boolean, default=False)
    uses_caps_emphasis = Column(Boolean, default=False)
    uses_emoji = Column(Boolean, default=False)
    exclamation_ratio = Column(Float, default=0.0)
    question_ratio = Column(Float, default=0.0)
    dominant_tone = Column(String, default="neutral") # casual|formal|poetic|blunt|expressive|analytical|introspective|humorous
    vocabulary_richness = Column(Float, default=0.5)
    voice_sample_phrases = Column(Text, default="[]")  # JSON string array
    signature_words = Column(Text, default="[]")       # JSON string array
    style_summary = Column(Text, default="")
    response_style_instructions = Column(Text, default="")
    entries_analyzed = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    raw_style_analysis = Column(Text, default="{}")    # JSON string representation

    user = relationship("User", back_populates="voice_profile")

class WeeklySummary(Base):
    __tablename__ = "weekly_summaries"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    summary_text = Column(Text, nullable=False)
    most_common_emotion = Column(String, nullable=True)
    most_positive_day = Column(String, nullable=True)
    most_stressful_day = Column(String, nullable=True)
    biggest_achievement = Column(Text, nullable=True)
    average_mood_score = Column(Float, nullable=True)
    entries_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class MirrorMeReport(Base):
    __tablename__ = "mirror_me_reports"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    report_data = Column(Text, nullable=False)        # JSON string containing all details
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
