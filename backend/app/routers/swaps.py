from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db, SwapRequest, User, Skill
from app.schemas import SwapRequestCreate, SwapRequestResponse, SwapRequestUpdate
from app.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[SwapRequestResponse])
async def get_my_swap_requests(
    status_filter: str = Query(None, description="Filter by status"),
    type_filter: str = Query("all", description="sent, received, or all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(SwapRequest)
    
    if type_filter == "sent":
        query = query.filter(SwapRequest.requester_id == current_user.id)
    elif type_filter == "received":
        query = query.filter(SwapRequest.requested_id == current_user.id)
    else:  # all
        query = query.filter(
            (SwapRequest.requester_id == current_user.id) | 
            (SwapRequest.requested_id == current_user.id)
        )
    
    if status_filter:
        query = query.filter(SwapRequest.status == status_filter)
    
    requests = query.order_by(SwapRequest.created_at.desc()).all()
    return requests


@router.post("/", response_model=SwapRequestResponse)
async def create_swap_request(
    swap_request: SwapRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Validate that the requested user exists and is active
    requested_user = db.query(User).filter(User.id == swap_request.requested_id).first()
    if not requested_user or not requested_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested user not found or inactive"
        )
    
    # Can't request from yourself
    if swap_request.requested_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request a swap with yourself"
        )
    
    # Validate skills exist
    skill_offered = db.query(Skill).filter(Skill.id == swap_request.skill_offered_id).first()
    skill_wanted = db.query(Skill).filter(Skill.id == swap_request.skill_wanted_id).first()
    
    if not skill_offered or not skill_wanted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both skills not found"
        )
    
    # Check if requester actually offers the skill they're proposing
    if skill_offered not in current_user.skills_offered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't offer the skill you're proposing to teach"
        )
    
    # Check if requested user has the skill the requester wants
    if skill_wanted not in requested_user.skills_offered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested user doesn't offer the skill you want to learn"
        )
    
    # Check for duplicate pending requests
    existing_request = db.query(SwapRequest).filter(
        SwapRequest.requester_id == current_user.id,
        SwapRequest.requested_id == swap_request.requested_id,
        SwapRequest.skill_offered_id == swap_request.skill_offered_id,
        SwapRequest.skill_wanted_id == swap_request.skill_wanted_id,
        SwapRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request for this skill swap already exists"
        )
    
    # Create the swap request
    db_request = SwapRequest(
        requester_id=current_user.id,
        requested_id=swap_request.requested_id,
        skill_offered_id=swap_request.skill_offered_id,
        skill_wanted_id=swap_request.skill_wanted_id,
        message=swap_request.message,
        status="pending"
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request


@router.get("/{request_id}", response_model=SwapRequestResponse)
async def get_swap_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    swap_request = db.query(SwapRequest).filter(SwapRequest.id == request_id).first()
    
    if not swap_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
    
    # Only the requester or requested user can view the request
    if swap_request.requester_id != current_user.id and swap_request.requested_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this swap request"
        )
    
    return swap_request


@router.put("/{request_id}", response_model=SwapRequestResponse)
async def update_swap_request(
    request_id: int,
    update_data: SwapRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    swap_request = db.query(SwapRequest).filter(SwapRequest.id == request_id).first()
    
    if not swap_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
    
    # Validate permissions based on action
    if update_data.status in ["accepted", "rejected"]:
        # Only the requested user can accept/reject
        if swap_request.requested_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requested user can accept or reject requests"
            )
    elif update_data.status == "cancelled":
        # Only the requester can cancel
        if swap_request.requester_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requester can cancel requests"
            )
    elif update_data.status == "completed":
        # Either party can mark as completed
        if swap_request.requester_id != current_user.id and swap_request.requested_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this request"
            )
    
    # Update the request
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(swap_request, field, value)
    
    db.commit()
    db.refresh(swap_request)
    
    return swap_request


@router.delete("/{request_id}")
async def delete_swap_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    swap_request = db.query(SwapRequest).filter(SwapRequest.id == request_id).first()
    
    if not swap_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
    
    # Only the requester can delete their own request, and only if it's pending
    if swap_request.requester_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can delete their own requests"
        )
    
    if swap_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending requests"
        )
    
    db.delete(swap_request)
    db.commit()
    
    return {"message": "Swap request deleted successfully"}
