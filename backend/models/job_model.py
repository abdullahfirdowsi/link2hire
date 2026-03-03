"""
Pydantic models for job data validation and structure.
These models ensure strict type checking and validation across the application.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class WorkMode(str, Enum):
    """Supported work modes."""
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"
    UNKNOWN = "Unknown"


class ConversationState(str, Enum):
    """Conversation flow states."""
    INITIAL = "initial"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class JobRole(BaseModel):
    """Individual job role information."""
    title: str = Field(..., description="Job title/role name")
    description: Optional[str] = Field(None, description="Role-specific description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "description": "Backend development with Python"
            }
        }


class ExtractedJobData(BaseModel):
    """
    Structured job data extracted by AI.
    This schema is strictly enforced for extraction agent output.
    """
    company: str = Field(..., description="Company name")
    roles: List[JobRole] = Field(..., min_length=1, description="List of job roles")
    location: str = Field(..., description="Job location (city, country)")
    work_mode: WorkMode = Field(default=WorkMode.UNKNOWN, description="Work arrangement")
    experience: str = Field(..., description="Required experience level")
    eligibility: str = Field(..., description="Eligibility criteria")
    salary: Optional[str] = Field(None, description="Salary range or compensation details")
    apply_link: str = Field(..., description="Application URL")
    deadline: Optional[str] = Field(None, description="Application deadline")
    
    @validator('roles')
    def validate_roles(cls, v):
        """Ensure at least one role exists."""
        if not v or len(v) == 0:
            raise ValueError("At least one role must be specified")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "TechCorp Inc.",
                "roles": [
                    {"title": "Backend Engineer", "description": "Python/FastAPI expert"}
                ],
                "location": "San Francisco, CA",
                "work_mode": "Hybrid",
                "experience": "3-5 years",
                "eligibility": "Bachelor's in CS or equivalent",
                "salary": "$120k-$180k",
                "apply_link": "https://example.com/apply",
                "deadline": "2024-04-30"
            }
        }


class DecisionOutput(BaseModel):
    """Decision agent output structure."""
    requires_clarification: bool = Field(..., description="Whether user input is needed")
    clarification_message: Optional[str] = Field(None, description="Message to show user")
    can_proceed: bool = Field(default=False, description="Whether to proceed with processing")
    detected_roles_count: int = Field(default=0, description="Number of roles detected")
    missing_fields: List[str] = Field(default_factory=list, description="Missing required fields")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requires_clarification": True,
                "clarification_message": "Detected 3 roles. Create combined entry or separate entries?",
                "can_proceed": False,
                "detected_roles_count": 3,
                "missing_fields": []
            }
        }


class ClarificationChoice(str, Enum):
    """User's clarification choice."""
    COMBINED = "combined"
    SEPARATE = "separate"


class ClarificationRequest(BaseModel):
    """User's response to clarification."""
    conversation_id: str = Field(..., description="Conversation identifier")
    choice: ClarificationChoice = Field(..., description="User's decision")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456",
                "choice": "separate"
            }
        }


class JobProcessingRequest(BaseModel):
    """Initial job processing request."""
    raw_job_text: str = Field(..., min_length=50, description="Raw job posting text")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_job_text": "TechCorp is hiring Backend Engineer and Frontend Engineer...",
                "user_context": {"source": "linkedin", "urgency": "high"}
            }
        }


class LinkedInPost(BaseModel):
    """Generated LinkedIn post content."""
    post_text: str = Field(..., max_length=3000, description="LinkedIn post content")
    hashtags: List[str] = Field(default_factory=list, description="Relevant hashtags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_text": "🚀 Exciting opportunity at TechCorp! Looking for talented engineers...",
                "hashtags": ["hiring", "techjobs", "backend", "python"]
            }
        }


class JobEntry(BaseModel):
    """Complete job entry for database storage."""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    conversation_id: str = Field(..., description="Related conversation ID")
    raw_input: str = Field(..., description="Original job text")
    extracted_data: ExtractedJobData = Field(..., description="Structured job data")
    linkedin_post: Optional[LinkedInPost] = Field(None, description="Generated post")
    posted_to_sheets: bool = Field(default=False, description="Google Sheets sync status")
    posted_to_linkedin: bool = Field(default=False, description="LinkedIn posting status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456",
                "raw_input": "Original job posting text...",
                "extracted_data": {},
                "posted_to_sheets": True,
                "posted_to_linkedin": False
            }
        }


class Conversation(BaseModel):
    """Conversation state tracking."""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    state: ConversationState = Field(default=ConversationState.INITIAL)
    raw_input: str = Field(..., description="Original user input")
    extracted_data: Optional[ExtractedJobData] = Field(None)
    decision_output: Optional[DecisionOutput] = Field(None)
    user_choice: Optional[ClarificationChoice] = Field(None)
    job_entry_ids: List[str] = Field(default_factory=list, description="Created job entry IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ProcessingResponse(BaseModel):
    """API response for job processing."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable message")
    conversation_id: str = Field(..., description="Conversation identifier")
    state: ConversationState = Field(..., description="Current conversation state")
    requires_clarification: bool = Field(default=False)
    clarification_message: Optional[str] = Field(None)
    job_entries_created: Optional[List[str]] = Field(default=None, description="Created job IDs")
    linkedin_post: Optional[LinkedInPost] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Job processed successfully!",
                "conversation_id": "conv_123456",
                "state": "completed",
                "requires_clarification": False,
                "job_entries_created": ["job_001", "job_002"]
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid job data format",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "company", "issue": "required field missing"}
            }
        }
