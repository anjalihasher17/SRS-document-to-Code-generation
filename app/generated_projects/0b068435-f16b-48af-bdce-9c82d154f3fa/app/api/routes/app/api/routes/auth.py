from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import SessionLocal
from app.models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str
    user: User

@router.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = SessionLocal.query(User).filter(User.email == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = user.generate_token()
    return {"token": token, "user": user}

@router.get("/api/auth/user")
async def get_user(token: str = Depends(oauth2_scheme)):
    user = SessionLocal.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user