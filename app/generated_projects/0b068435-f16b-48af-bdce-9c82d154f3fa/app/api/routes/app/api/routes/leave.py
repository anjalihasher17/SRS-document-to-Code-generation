from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models import LeaveRequest

router = APIRouter()

class LeaveRequestRequest(BaseModel):
    start_date: str
    end_date: str
    reason: str

class LeaveRequestResponse(BaseModel):
    message: str
    status: str

@router.post("/api/lms/leaves/apply")
async def apply_leave(leave_request: LeaveRequestRequest, token: str = Depends(oauth2_scheme)):
    user = SessionLocal.query(User).filter(User.token == token).first()
    leave_request = LeaveRequest(user_id=user.id, **leave_request.dict())
    SessionLocal.add(leave_request)
    SessionLocal.commit()
    return {"message": "Leave request submitted successfully", "status": "pending"}

@router.patch("/api/lms/leaves/{leave_id}/approve")
async def approve_leave(leave_id: int, status: str, token: str = Depends(oauth2_scheme)):
    leave_request = SessionLocal.query(LeaveRequest).get(leave_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    user = SessionLocal.query(User).filter(User.token == token).first()
    if user.role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")
    leave_request.status = status
    SessionLocal.commit()
    return {"message": "Leave request approved", "status": leave_request.status}