import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ApplicationStatus(str, Enum):
    applied = "applied"
    interviewing = "interviewing"
    offered = "offered"
    rejected = "rejected"
    ghosted = "ghosted"


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, index=True)
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    status: ApplicationStatus = Field(default=ApplicationStatus.applied)
    date_applied: date
    job_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
