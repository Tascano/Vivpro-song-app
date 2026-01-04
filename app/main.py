import logging
import json
import os
import shutil
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Body, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from .core.database import get_db, engine, Base
from .models.song import Song
from .utils.data_utils import normalize_and_insert_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)  # Drop all tables first
    Base.metadata.create_all(bind=engine)  # Recreate empty tables
    logger.info("Database ready with fresh, empty tables.")
    yield
    # Shutdown (if needed)

app = FastAPI(title="Playlist API", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RatingRequest(BaseModel):
    rating: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoints

@app.get("/api/songs")
def get_songs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=10000),
    sort_by: Optional[str] = None,
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Song)
    
    # Sorting
    if sort_by:
        # Check if column exists to avoid SQL injection/errors
        if hasattr(Song, sort_by):
            column = getattr(Song, sort_by)
            if order == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": limit
    }

@app.get("/api/songs/search")
def search_songs(
    title: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    
    # Perform case-insensitive title search
    query = db.query(Song).filter(Song.title.ilike(f"%{title}%"))
    
    total = query.count()
    results = query.offset(offset).limit(limit).all()
    
    items = []
    for row in results:
        item = {
            "id": row.id,
            "title": row.title,
            "song_class": row.song_class,
            "rating": row.rating,
            "score": 0.0,
            "danceability": row.danceability,
            "energy": row.energy,
            "key": row.key,
            "loudness": row.loudness,
            "mode": row.mode,
            "acousticness": row.acousticness,
            "instrumentalness": row.instrumentalness,
            "liveness": row.liveness,
            "valence": row.valence,
            "tempo": row.tempo,
            "duration_ms": row.duration_ms,
            "time_signature": row.time_signature,
            "num_bars": row.num_bars,
            "num_sections": row.num_sections,
            "num_segments": row.num_segments
        }
        items.append(item)
            
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": limit
    }

@app.post("/api/songs/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")
    
    try:
        content = await file.read()
        data = json.loads(content.decode())
        
        message = normalize_and_insert_data(data, db)
        return {"message": message}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/songs/all")
def get_all_songs(db: Session = Depends(get_db)):
    return db.query(Song).all()

@app.delete("/api/songs/all")
def delete_all_songs(db: Session = Depends(get_db)):
    """Delete all songs from the database"""
    try:
        count = db.query(Song).count()
        db.query(Song).delete()
        db.commit()
        logger.info(f"Deleted all {count} songs from database")
        return {"message": f"Successfully deleted {count} songs"}
    except Exception as e:
        logger.error(f"Error deleting songs: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/songs/{song_id}/rate")
def rate_song(song_id: str, request: RatingRequest, db: Session = Depends(get_db)):
    if request.rating < 0 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
    
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song.rating = request.rating
    db.commit()
    db.refresh(song)
    
    return {"message": "Rating updated", "song_id": song_id, "rating": request.rating}

# Mount static files - MUST be last
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
