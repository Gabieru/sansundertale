from fastapi import FastAPI, HTTPException, Path, Cookie, Query, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional
import uuid
import json

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI(
    title="Simple User JSON Backend",
    description="A basic backend to handle user JSON data",
    version="1.0.0"
)

import os

# --- Database Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DBModpack(Base):
    __tablename__ = "modpacks"

    id = Column(String, primary_key=True, index=True)
    gameId = Column(String, index=True)
    userId = Column(String, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    mods = Column(Text)  # store JSON string

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ModpackCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str = Field(..., max_length=500)
    mods: Any 

class Modpack(ModpackCreate):
    id: str
    gameId: str
    userId: str
    
    model_config = ConfigDict(from_attributes=True)


@app.get("/game/{gameId}/modpacks", response_model=List[Modpack])
def get_game_modpacks(
    gameId: str = Path(..., title="The ID of the game"),
    page: int = Query(1, ge=1, title="Page number"),
    db: Session = Depends(get_db)
):
    """
    retorna 10 modpacks de un juego
    """
    limit = 10
    offset = (page - 1) * limit
    
    db_modpacks = db.query(DBModpack).filter(DBModpack.gameId == gameId).offset(offset).limit(limit).all()
    
    result = []
    for db_mp in db_modpacks:
        mp = Modpack.model_validate(db_mp)
        mp.mods = json.loads(db_mp.mods) if db_mp.mods else None
        result.append(mp)
        
    return result

@app.get("/user/modpacks", response_model=List[Modpack])
def get_user_modpacks(
    user_id: Optional[str] = Cookie(None, title="User ID from cookie"),
    db: Session = Depends(get_db)
):
    """
    retorna todos los modpacks de un usuario
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    db_modpacks = db.query(DBModpack).filter(DBModpack.userId == user_id).all()
    
    result = []
    for db_mp in db_modpacks:
        mp = Modpack.model_validate(db_mp)
        mp.mods = json.loads(db_mp.mods) if db_mp.mods else None
        result.append(mp)
        
    return result

@app.post("/game/{gameId}/modpacks", status_code=201, response_model=Modpack)
def create_modpack(
    modpack_in: ModpackCreate,
    gameId: str = Path(..., title="The ID of the game"),
    user_id: Optional[str] = Cookie(None, title="User ID from cookie"),
    db: Session = Depends(get_db)
):
    """
    crea el modpack
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    new_db_modpack = DBModpack(
        id=str(uuid.uuid4()),
        gameId=gameId,
        userId=user_id,
        nombre=modpack_in.nombre,
        descripcion=modpack_in.descripcion,
        mods=json.dumps(modpack_in.mods)
    )
    db.add(new_db_modpack)
    db.commit()
    db.refresh(new_db_modpack)
    
    new_modpack = Modpack.model_validate(new_db_modpack)
    new_modpack.mods = json.loads(new_db_modpack.mods)
    return new_modpack
