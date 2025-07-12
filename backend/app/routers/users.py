from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db, User, Skill
from app.schemas import UserResponse, UserUpdate, UserPublic, UserSearchParams, SkillResponse
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/search", response_model=List[UserPublic])
async def search_users(
    skill: str = Query(None, description="Search by skill name"),
    location: str = Query(None, description="Filter by location"),
    category: str = Query(None, description="Filter by skill category"),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(
        User.is_public == True,
        User.is_active == True,
        User.id != current_user.id  # Exclude current user from search
    )
    
    # Filter by location
    if location:
        query = query.filter(User.location.ilike(f"%{location}%"))
    
    # Filter by skill
    if skill:
        query = query.join(User.skills_offered).filter(
            Skill.name.ilike(f"%{skill}%")
        )
    
    # Filter by skill category
    if category:
        query = query.join(User.skills_offered).filter(
            Skill.category.ilike(f"%{category}%")
        )
    
    users = query.offset(offset).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only return public profiles or the user's own profile
    if not user.is_public and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )
    
    return user


@router.get("/{user_id}/skills/offered", response_model=List[SkillResponse])
async def get_user_skills_offered(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only return public profiles or the user's own profile
    if not user.is_public and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )
    
    return user.skills_offered


@router.get("/{user_id}/skills/wanted", response_model=List[SkillResponse])
async def get_user_skills_wanted(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only return public profiles or the user's own profile
    if not user.is_public and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )
    
    return user.skills_wanted


@router.post("/me/skills/offered/{skill_id}")
async def add_skill_offered(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if skill not in current_user.skills_offered:
        current_user.skills_offered.append(skill)
        db.commit()
    
    return {"message": "Skill added successfully"}


@router.delete("/me/skills/offered/{skill_id}")
async def remove_skill_offered(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if skill in current_user.skills_offered:
        current_user.skills_offered.remove(skill)
        db.commit()
    
    return {"message": "Skill removed successfully"}


@router.post("/me/skills/wanted/{skill_id}")
async def add_skill_wanted(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if skill not in current_user.skills_wanted:
        current_user.skills_wanted.append(skill)
        db.commit()
    
    return {"message": "Skill added successfully"}


@router.delete("/me/skills/wanted/{skill_id}")
async def remove_skill_wanted(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if skill in current_user.skills_wanted:
        current_user.skills_wanted.remove(skill)
        db.commit()
    
    return {"message": "Skill removed successfully"}
