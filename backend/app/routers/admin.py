from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db, User, Skill, SwapRequest, Feedback, AdminMessage
from app.schemas import (
    UserResponse, SkillResponse, SwapRequestResponse, 
    AdminMessageCreate, AdminMessageResponse
)
from app.auth import get_current_admin_user

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    is_active: bool = Query(None, description="Filter by active status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(offset).limit(limit).all()
    return users


@router.put("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban an admin user"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.username} has been banned"}


@router.put("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": f"User {user.username} has been unbanned"}


@router.get("/skills/pending", response_model=List[SkillResponse])
async def get_pending_skills(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    skills = db.query(Skill).filter(Skill.is_approved == False).all()
    return skills


@router.get("/swaps", response_model=List[SwapRequestResponse])
async def get_all_swaps(
    status_filter: str = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    query = db.query(SwapRequest)
    
    if status_filter:
        query = query.filter(SwapRequest.status == status_filter)
    
    swaps = query.order_by(desc(SwapRequest.created_at)).offset(offset).limit(limit).all()
    return swaps


@router.get("/stats")
async def get_platform_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    total_skills = db.query(func.count(Skill.id)).scalar()
    pending_skills = db.query(func.count(Skill.id)).filter(Skill.is_approved == False).scalar()
    
    total_swaps = db.query(func.count(SwapRequest.id)).scalar()
    pending_swaps = db.query(func.count(SwapRequest.id)).filter(SwapRequest.status == "pending").scalar()
    completed_swaps = db.query(func.count(SwapRequest.id)).filter(SwapRequest.status == "completed").scalar()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "skills": {
            "total": total_skills,
            "approved": total_skills - pending_skills,
            "pending": pending_skills
        },
        "swaps": {
            "total": total_swaps,
            "pending": pending_swaps,
            "completed": completed_swaps
        }
    }


@router.post("/messages", response_model=AdminMessageResponse)
async def create_admin_message(
    message: AdminMessageCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    db_message = AdminMessage(
        title=message.title,
        content=message.content,
        is_active=message.is_active
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/messages", response_model=List[AdminMessageResponse])
async def get_admin_messages(
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    query = db.query(AdminMessage)
    
    if is_active is not None:
        query = query.filter(AdminMessage.is_active == is_active)
    
    messages = query.order_by(desc(AdminMessage.created_at)).all()
    return messages


@router.put("/messages/{message_id}/toggle")
async def toggle_admin_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    message = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    message.is_active = not message.is_active
    db.commit()
    
    return {"message": f"Message {'activated' if message.is_active else 'deactivated'} successfully"}


@router.get("/reports/users")
async def get_user_activity_report(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    users_with_stats = db.query(
        User.id,
        User.username,
        User.email,
        User.created_at,
        User.is_active,
        func.count(SwapRequest.id).label("total_requests")
    ).outerjoin(
        SwapRequest, 
        (SwapRequest.requester_id == User.id) | (SwapRequest.requested_id == User.id)
    ).group_by(User.id).all()
    
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active,
            "total_requests": user.total_requests
        }
        for user in users_with_stats
    ]


@router.get("/reports/feedback")
async def get_feedback_report(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    feedback_stats = db.query(
        func.count(Feedback.id).label("total_feedback"),
        func.avg(Feedback.rating).label("average_rating"),
        func.min(Feedback.rating).label("min_rating"),
        func.max(Feedback.rating).label("max_rating")
    ).first()
    
    return {
        "total_feedback": feedback_stats.total_feedback or 0,
        "average_rating": float(feedback_stats.average_rating) if feedback_stats.average_rating else 0,
        "min_rating": feedback_stats.min_rating or 0,
        "max_rating": feedback_stats.max_rating or 0
    }
