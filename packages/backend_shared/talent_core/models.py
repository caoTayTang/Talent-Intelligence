from pgvector.sqlalchemy import Vector
import enum
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# ==========================================
# 1. ENUMS (Các kiểu dữ liệu giới hạn)
# ==========================================
class UserRole(str, enum.Enum):
    hr = "hr"
    candidate = "candidate"


class ApplicationStatus(str, enum.Enum):
    pending_cv = "pending_cv"
    cv_passed = "cv_passed"
    cv_failed = "cv_failed"
    test_submitted = "test_submitted"
    test_scored = "test_scored"
    test_failed = "test_failed"
    interview_scheduled = "interview_scheduled"
    interview_completed = "interview_completed"
    interview_failed = "interview_failed"
    accepted = "accepted"


class AgentRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


# BỔ SUNG ENUM CHO CHAT VÀ THÔNG BÁO
class SenderRole(str, enum.Enum):
    user = "user"
    agent = "agent"


class NotificationType(str, enum.Enum):
    test_unlocked = "test_unlocked"
    interview_invited = "interview_invited"
    system_alert = "system_alert"


class InterviewStatus(str, enum.Enum):
    scheduled = "scheduled"  # Đã lên lịch, chưa tới giờ
    ongoing = "ongoing"  # Đang diễn ra (HR và Ứng viên đang trong phòng Jitsi)
    completed = "completed"  # Đã phỏng vấn xong
    cancelled = "cancelled"  # Đã hủy


# ==========================================
# 2. BẢNG TÀI KHOẢN & THÔNG BÁO
# ==========================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))

    auth_provider: Mapped[str] = mapped_column(String, default="local")
    hashed_password: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    applications: Mapped[List["Application"]] = relationship(back_populates="candidate")
    interview_slots: Mapped[List["InterviewSlot"]] = relationship(back_populates="hr")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        back_populates="candidate"
    )


class Notification(Base):
    """Chuông thông báo góc màn hình"""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type")
    )
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="notifications")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String)
    logo_url: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    jobs: Mapped[List["Job"]] = relationship(back_populates="company")


# ==========================================
# 3. BẢNG NGHIỆP VỤ (JOB, APPLICATION & CHAT)
# ==========================================
class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)

    # Nơi lưu đề thi gốc do HR cung cấp
    test_content: Mapped[dict | list | None] = mapped_column(JSONB)
    test_object_url: Mapped[str | None] = mapped_column(String)
    scorecard_json: Mapped[dict | None] = mapped_column(JSONB)
    jd_object_url: Mapped[str | None] = mapped_column(String)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    company: Mapped[Company] = relationship(back_populates="jobs")
    applications: Mapped[List["Application"]] = relationship(back_populates="job")
    chat_sessions: Mapped[List["ChatSession"]] = relationship(back_populates="job")


class ChatSession(Base):
    """Phiên chat hỏi đáp JD giữa 1 Candidate và 1 Job"""

    __tablename__ = "chat_sessions"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    candidate: Mapped[User] = relationship(back_populates="chat_sessions")
    job: Mapped[Job] = relationship(back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session",
        order_by="ChatMessage.created_at",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    """Từng dòng tin nhắn trong phiên chat"""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id")
    )

    sender_role: Mapped[SenderRole] = mapped_column(
        Enum(SenderRole, name="sender_role")
    )
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    # Nơi lưu Bài làm và Đề riêng của ứng viên
    cv_object_key: Mapped[str | None] = mapped_column(String)
    dynamic_test_content: Mapped[dict | list | None] = mapped_column(
        JSONB
    )  # Nội dung đề do AI tự sinh
    test_submission_url: Mapped[list[str] | None] = mapped_column(
        JSONB
    )  # Link các file nộp bài
    test_answer: Mapped[dict | list | None] = mapped_column(JSONB)  # Text nộp bài
    interview_audio_url: Mapped[str | None] = mapped_column(String)
    interview_transcript: Mapped[dict | list | None] = mapped_column(JSONB)

    # Scoring & Feedback
    cv_score: Mapped[float | None] = mapped_column(Float)
    total_score: Mapped[float | None] = mapped_column(Float)
    interview_score: Mapped[float | None] = mapped_column(Float)
    detailed_score_json: Mapped[dict | None] = mapped_column(JSONB)

    test_deadline: Mapped[datetime | None] = mapped_column(DateTime)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.pending_cv,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    candidate: Mapped[User] = relationship(back_populates="applications")
    job: Mapped[Job] = relationship(back_populates="applications")
    agent_runs: Mapped[List["AgentRun"]] = relationship(back_populates="application")
    interview_meeting: Mapped["InterviewSlot | None"] = relationship(
        back_populates="application"
    )


# ==========================================
# 4. BẢNG HỖ TRỢ (LỊCH PHỎNG VẤN & LOG AI)
# ==========================================
class InterviewSlot(Base):
    __tablename__ = "interview_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hr_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)

    # 1. Tên phòng Jitsi: Chỉ lưu chuỗi định danh (VD: "ai_interview_550e8400-e29b...")
    jitsi_room_name: Mapped[str] = mapped_column(String, unique=True)

    # 2. Mật khẩu phòng (Tùy chọn): Jitsi cho phép set pass qua JS, lưu sẵn ở đây để cấp cho ứng viên
    room_password: Mapped[str | None] = mapped_column(String)

    # 3. Trạng thái buổi phỏng vấn
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus, name="interview_status"),
        default=InterviewStatus.scheduled,
    )
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hr: Mapped["User"] = relationship(back_populates="interview_slots")
    application: Mapped["Application"] = relationship(
        back_populates="interview_meeting"
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id")
    )
    agent_type: Mapped[str] = mapped_column(String)
    input_json: Mapped[dict] = mapped_column(JSONB)
    output_json: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agent_run_status")
    )
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    application: Mapped["Application"] = relationship(back_populates="agent_runs")


class DocumentOwnerType(str, enum.Enum):
    job = "job"
    application = "application"


class DocumentChunkSource(str, enum.Enum):
    jd = "jd"
    cv = "cv"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    owner_type: Mapped[DocumentOwnerType] = mapped_column(
        Enum(DocumentOwnerType, name="document_owner_type"), index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

    source: Mapped[DocumentChunkSource] = mapped_column(
        Enum(DocumentChunkSource, name="document_chunk_source"), index=True
    )

    section: Mapped[str | None] = mapped_column(String)
    chunk_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(2048))
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
