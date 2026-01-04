import logging
from sqlalchemy.orm import Session
from ..models.song import Song

logger = logging.getLogger(__name__)

def normalize_and_insert_data(data, db: Session):
    """Normalize JSON data and insert into database. Handles both column-oriented and row-oriented formats."""
    added_count = 0
    
    # Check if column-oriented (like Playlist.json from problem statement)
    is_column_oriented = isinstance(data, dict) and all(isinstance(v, dict) for v in data.values())
    
    if is_column_oriented:
        # Handle column-oriented format: {"id": {"0": "...", "1": "..."}, "title": {"0": "...", "1": "..."}}
        logger.info("Detected column-oriented JSON format")
        song_indices = data['id'].keys()
        
        for idx in song_indices:
            s_id = str(data['id'][idx])
            if not s_id:
                continue
            
            existing = db.query(Song).filter(Song.id == s_id).first()
            if existing:
                # Update existing
                existing.title = str(data['title'].get(idx, existing.title))
                existing.song_class = str(data.get('class', {}).get(idx, existing.song_class))
                existing.danceability = float(data.get('danceability', {}).get(idx, existing.danceability))
                existing.energy = float(data.get('energy', {}).get(idx, existing.energy))
                existing.key = int(data.get('key', {}).get(idx, existing.key))
                existing.loudness = float(data.get('loudness', {}).get(idx, existing.loudness))
                existing.mode = int(data.get('mode', {}).get(idx, existing.mode))
                existing.acousticness = float(data.get('acousticness', {}).get(idx, existing.acousticness))
                existing.instrumentalness = float(data.get('instrumentalness', {}).get(idx, existing.instrumentalness))
                existing.liveness = float(data.get('liveness', {}).get(idx, existing.liveness))
                existing.valence = float(data.get('valence', {}).get(idx, existing.valence))
                existing.tempo = float(data.get('tempo', {}).get(idx, existing.tempo))
                existing.duration_ms = int(data.get('duration_ms', {}).get(idx, existing.duration_ms))
                existing.time_signature = int(data.get('time_signature', {}).get(idx, existing.time_signature))
                existing.num_bars = int(data.get('num_bars', {}).get(idx, existing.num_bars))
                existing.num_sections = int(data.get('num_sections', {}).get(idx, existing.num_sections))
                existing.num_segments = int(data.get('num_segments', {}).get(idx, existing.num_segments))
            else:
                # Create new
                new_song = Song(
                    id=s_id,
                    title=str(data['title'].get(idx, "Unknown Title")),
                    song_class=str(data.get('class', {}).get(idx, "0")),
                    rating=0,
                    danceability=float(data.get('danceability', {}).get(idx, 0.0)),
                    energy=float(data.get('energy', {}).get(idx, 0.0)),
                    key=int(data.get('key', {}).get(idx, 0)),
                    loudness=float(data.get('loudness', {}).get(idx, 0.0)),
                    mode=int(data.get('mode', {}).get(idx, 0)),
                    acousticness=float(data.get('acousticness', {}).get(idx, 0.0)),
                    instrumentalness=float(data.get('instrumentalness', {}).get(idx, 0.0)),
                    liveness=float(data.get('liveness', {}).get(idx, 0.0)),
                    valence=float(data.get('valence', {}).get(idx, 0.0)),
                    tempo=float(data.get('tempo', {}).get(idx, 0.0)),
                    duration_ms=int(data.get('duration_ms', {}).get(idx, 0)),
                    time_signature=int(data.get('time_signature', {}).get(idx, 4)),
                    num_bars=int(data.get('num_bars', {}).get(idx, 0)),
                    num_sections=int(data.get('num_sections', {}).get(idx, 0)),
                    num_segments=int(data.get('num_segments', {}).get(idx, 0))
                )
                db.add(new_song)
                added_count += 1
        
        db.commit()
        return f"Processed {len(song_indices)} items. Added {added_count} new songs."
    
    else:
        # Handle row-oriented format: [{"id": "...", "title": "..."}, ...]
        logger.info("Detected row-oriented JSON format")
        
        # Normalize if it's a wrapped dict
        if isinstance(data, dict):
            if "songs" in data:
                data = data["songs"]
            else:
                data = [data]
        elif not isinstance(data, list):
            raise ValueError("Invalid JSON format")
            
        # Process and insert
        for item in data:
            if "title" not in item:
                continue
                
            s_id = str(item.get("id", ""))
            if not s_id: 
                continue
                
            existing = db.query(Song).filter(Song.id == s_id).first()
            if existing:
                # Update existing
                existing.title = item.get("title")
                existing.song_class = item.get("class", item.get("song_class", ""))
                existing.danceability = float(item.get("danceability", existing.danceability))
                existing.energy = float(item.get("energy", existing.energy))
                existing.key = int(item.get("key", existing.key))
                existing.loudness = float(item.get("loudness", existing.loudness))
                existing.mode = int(item.get("mode", existing.mode))
                existing.acousticness = float(item.get("acousticness", existing.acousticness))
                existing.instrumentalness = float(item.get("instrumentalness", existing.instrumentalness))
                existing.liveness = float(item.get("liveness", existing.liveness))
                existing.valence = float(item.get("valence", existing.valence))
                existing.tempo = float(item.get("tempo", existing.tempo))
                existing.duration_ms = int(item.get("duration_ms", existing.duration_ms))
                existing.time_signature = int(item.get("time_signature", existing.time_signature))
                existing.num_bars = int(item.get("num_bars", existing.num_bars))
                existing.num_sections = int(item.get("num_sections", existing.num_sections))
                existing.num_segments = int(item.get("num_segments", existing.num_segments))
            else:
                new_song = Song(
                    id=s_id,
                    title=item.get("title"),
                    song_class=item.get("class", item.get("song_class", "")),
                    rating=0,
                    danceability=float(item.get("danceability", 0.0)),
                    energy=float(item.get("energy", 0.0)),
                    key=int(item.get("key", 0)),
                    loudness=float(item.get("loudness", 0.0)),
                    mode=int(item.get("mode", 0)),
                    acousticness=float(item.get("acousticness", 0.0)),
                    instrumentalness=float(item.get("instrumentalness", 0.0)),
                    liveness=float(item.get("liveness", 0.0)),
                    valence=float(item.get("valence", 0.0)),
                    tempo=float(item.get("tempo", 0.0)),
                    duration_ms=int(item.get("duration_ms", 0)),
                    time_signature=int(item.get("time_signature", 4)),
                    num_bars=int(item.get("num_bars", 0)),
                    num_sections=int(item.get("num_sections", 0)),
                    num_segments=int(item.get("num_segments", 0))
                )
                db.add(new_song)
                added_count += 1
        
        db.commit()
        return f"Processed {len(data)} items. Added {added_count} new songs."