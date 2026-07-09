from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database import Base


class HCP(Base):
    """A Healthcare Professional record (doctor / specialist)."""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    """A logged interaction between a field rep and an HCP."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    rep_id = Column(String(100), nullable=False, default="rep_demo")

    interaction_type = Column(String(50), default="visit")  # call | visit | email
    interaction_date = Column(DateTime, default=datetime.utcnow)

    # Structured-form fields
    products_discussed = Column(String(500))
    notes = Column(Text)

    # AI-derived fields (populated by the LangGraph "Log Interaction" tool)
    ai_summary = Column(Text)
    ai_entities = Column(Text)  # JSON-encoded extracted entities
    sentiment = Column(String(50))

    # Chat-mode originals
    raw_transcript = Column(Text)
    logged_via_chat = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
    followups = relationship("FollowUp", back_populates="interaction")


class FollowUp(Base):
    """A follow-up task created from an interaction (Schedule Follow-up tool)."""

    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    reason = Column(String(500))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    interaction = relationship("Interaction", back_populates="followups")
