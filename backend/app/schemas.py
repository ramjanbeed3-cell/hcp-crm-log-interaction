from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    hcp_id: int
    rep_id: str = "rep_demo"
    interaction_type: str = "visit"
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    attendees: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    user_sentiment: Optional[str] = None  # rep-selected: positive | neutral | negative


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    sentiment: Optional[str] = None
    attendees: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None


class InteractionOut(BaseModel):
    id: int
    hcp_id: int
    rep_id: str
    interaction_type: str
    interaction_date: datetime
    products_discussed: Optional[str]
    notes: Optional[str]
    attendees: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    ai_summary: Optional[str]
    ai_entities: Optional[str]
    sentiment: Optional[str]
    logged_via_chat: bool

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    hcp_id: Optional[int] = None
    rep_id: str = "rep_demo"


class ChatResponse(BaseModel):
    reply: str
    tool_calls: List[str] = []
