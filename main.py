from flask import Flask, request, jsonify
import uuid
import json

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

app = Flask(__name__)

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

def modpack_to_dict(mp):
    return {
        "id": mp.id,
        "gameId": mp.gameId,
        "userId": mp.userId,
        "nombre": mp.nombre,
        "descripcion": mp.descripcion,
        "mods": json.loads(mp.mods) if mp.mods else None
    }

@app.route("/game/<gameId>/modpacks", methods=["GET"])
def get_game_modpacks(gameId):
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
        
    limit = 10
    offset = (page - 1) * limit
    
    db = SessionLocal()
    try:
        db_modpacks = db.query(DBModpack).filter(DBModpack.gameId == gameId).offset(offset).limit(limit).all()
        return jsonify([modpack_to_dict(mp) for mp in db_modpacks])
    finally:
        db.close()

@app.route("/user/modpacks", methods=["GET"])
def get_user_modpacks():
    user_id = request.cookies.get("user_id")
    if not user_id:
        return jsonify({"detail": "Not authenticated"}), 401
        
    db = SessionLocal()
    try:
        db_modpacks = db.query(DBModpack).filter(DBModpack.userId == user_id).all()
        return jsonify([modpack_to_dict(mp) for mp in db_modpacks])
    finally:
        db.close()

@app.route("/game/<gameId>/modpacks", methods=["POST"])
def create_modpack(gameId):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return jsonify({"detail": "Not authenticated"}), 401
        
    data = request.json
    if not data or not data.get("nombre") or not data.get("descripcion") or "mods" not in data:
        return jsonify({"detail": "Missing fields"}), 422
        
    db = SessionLocal()
    try:
        new_db_modpack = DBModpack(
            id=str(uuid.uuid4()),
            gameId=gameId,
            userId=user_id,
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            mods=json.dumps(data["mods"])
        )
        db.add(new_db_modpack)
        db.commit()
        db.refresh(new_db_modpack)
        
        return jsonify(modpack_to_dict(new_db_modpack)), 201
    finally:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)
