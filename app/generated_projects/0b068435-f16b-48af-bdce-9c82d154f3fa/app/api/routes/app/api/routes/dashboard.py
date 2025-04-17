from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models import Tile

router = APIRouter()

class Tile(BaseModel):
    id: str
    title: str
    content: str

@router.get("/api/dashboard/tiles")
async def get_tiles(token: str = Depends(oauth2_scheme)):
    tiles = SessionLocal.query(Tile).all()
    return {"tiles": tiles}