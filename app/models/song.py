from sqlalchemy import Column, Integer, String, Float
from ..core.database import Base


class Song(Base):
    __tablename__ = "songs"

    pk = Column(Integer, primary_key=True, index=True)
    id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    song_class = Column(String)
    rating = Column(Integer, default=0)
    
    # Analytics fields
    danceability = Column(Float, default=0.0)
    energy = Column(Float, default=0.0)
    key = Column(Integer, default=0)
    loudness = Column(Float, default=0.0)
    mode = Column(Integer, default=0)
    acousticness = Column(Float, default=0.0)
    instrumentalness = Column(Float, default=0.0)
    liveness = Column(Float, default=0.0)
    valence = Column(Float, default=0.0)
    tempo = Column(Float, default=0.0)
    duration_ms = Column(Integer, default=0)
    time_signature = Column(Integer, default=4)
    num_bars = Column(Integer, default=0)
    num_sections = Column(Integer, default=0)
    num_segments = Column(Integer, default=0)