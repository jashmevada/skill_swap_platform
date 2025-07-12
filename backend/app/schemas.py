from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    availability: Optional[str] = None
    is_public: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    availability: Optional[str] = None
    is_public: Optional[bool] = None
    profile_photo: Optional[str] = None


class UserResponse(UserBase):
    id: int
    profile_photo: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    availability: Optional[str] = None
    
    class Config:
        from_attributes = True


# Skill Schemas
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int
    is_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Swap Request Schemas
class SwapRequestBase(BaseModel):
    requested_id: int
    skill_offered_id: int
    skill_wanted_id: int
    message: Optional[str] = None


class SwapRequestCreate(SwapRequestBase):
    pass


class SwapRequestUpdate(BaseModel):
    status: str  # pending, accepted, rejected, completed, cancelled
    message: Optional[str] = None


class SwapRequestResponse(SwapRequestBase):
    id: int
    requester_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackBase(BaseModel):
    swap_request_id: int
    receiver_id: int
    rating: int  # 1-5
    comment: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: int
    giver_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Admin Schemas
class AdminMessageBase(BaseModel):
    title: str
    content: str
    is_active: bool = True


class AdminMessageCreate(AdminMessageBase):
    pass


class AdminMessageResponse(AdminMessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search and Filter Schemas
class UserSearchParams(BaseModel):
    skill: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    category: Optional[str] = None


class SkillSearchParams(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
