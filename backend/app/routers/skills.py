from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db, Skill
from app.schemas import SkillCreate, SkillResponse
from app.auth import get_current_active_user, get_current_admin_user
from app.database import User

router = APIRouter()


@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    category: str = Query(None, description="Filter by category"),
    search: str = Query(None, description="Search by skill name"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Skill).filter(Skill.is_approved == True)
    
    if category:
        query = query.filter(Skill.category.ilike(f"%{category}%"))
    
    if search:
        query = query.filter(Skill.name.ilike(f"%{search}%"))
    
    skills = query.offset(offset).limit(limit).all()
    return skills


@router.get("/categories", response_model=List[str])
async def get_skill_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    categories = db.query(Skill.category).filter(
        Skill.category.is_not(None),
        Skill.is_approved == True
    ).distinct().all()
    
    return [category[0] for category in categories if category[0]]


@router.post("/", response_model=SkillResponse)
async def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if skill already exists
    existing_skill = db.query(Skill).filter(Skill.name.ilike(skill.name)).first()
    
    if existing_skill:
        if existing_skill.is_approved:
            return existing_skill
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill exists but is pending approval"
            )
    
    # Create new skill
    db_skill = Skill(
        name=skill.name.strip().title(),
        category=skill.category.strip().title() if skill.category else None,
        description=skill.description,
        is_approved=True  # Auto-approve for now, admin can moderate later
    )
    
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    
    return db_skill


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return skill


@router.put("/{skill_id}/approve")
async def approve_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    skill.is_approved = True
    db.commit()
    
    return {"message": "Skill approved successfully"}


@router.put("/{skill_id}/reject")
async def reject_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    skill.is_approved = False
    db.commit()
    
    return {"message": "Skill rejected successfully"}


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    db.delete(skill)
    db.commit()
    
    return {"message": "Skill deleted successfully"}
