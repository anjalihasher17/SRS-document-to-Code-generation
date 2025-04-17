from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models import Pod, PodAssignment

router = APIRouter()

class PodRequest(BaseModel):
    pod_id: str

class PodResponse(BaseModel):
    pod_id: str
    pod_name: str
    members: List[PodAssignment]

@router.get("/api/pods/{pod_id}/details")
async def get_pod_details(pod_id: str, token: str = Depends(oauth2_scheme)):
    pod = SessionLocal.query(Pod).get(pod_id)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    members = SessionLocal.query(PodAssignment).filter(PodAssignment.pod_id == pod_id).all()
    return {"pod_id": pod.id, "pod_name": pod.name, "members": members}

@router.post("/api/pods/{pod_id}/recommend")
async def recommend_user(pod_id: str, recommended_user_id: str, token: str = Depends(oauth2_scheme)):
    pod = SessionLocal.query(Pod).get(pod_id)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    user = SessionLocal.query(User).filter(User.token == token).first()
    if user.role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")
    pod_recommendation = PodRecommendation(pod_id=pod_id, recommended_user_id=recommended_user_id)
    SessionLocal.add(pod_recommendation)
    SessionLocal.commit()
    return {"message": "Recommendation sent successfully"}