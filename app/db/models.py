"""Pydantic and Database Schemas for AI-VPS."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ProjectBase(BaseModel):
    name: str
    mode: str
    target_language: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    status: str
    created_at: str
    updated_at: str
