import requests
import time
import os

BASE_URL = "http://localhost:8000"

def upload_sample_data():
    sample_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sample_data', 'Playlist.json')
    with open(sample_file_path, 'rb') as f:
        response = requests.post(f"{BASE_URL}/api/songs/upload", files={"file": ("Playlist.json", f, "application/json")})
        if response.status_code == 200:
            print("Uploaded sample data")
        else:
            print("Failed to upload sample data")

def cleanup():
    # Import here to avoid issues if app not running
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from app.core.database import get_db
    from app.models.song import Song
    from sqlalchemy.orm import Session
    
    db: Session = next(get_db())
    db.query(Song).delete()
    db.commit()
    print("Database cleaned up")

def test_persistence():
    upload_sample_data()
    print("Testing Database Persistence...")
    
    # 1. Get a song
    response = requests.get(f"{BASE_URL}/api/songs", params={"limit": 1})
    if response.status_code != 200:
        print("FAILED: Could not fetch songs")
        return
        
    song = response.json()['items'][0]
    song_id = song['id']
    original_rating = song['rating']
    print(f"Song: {song['title']} (ID: {song_id}), Rating: {original_rating}")
    
    # 2. Rate the song
    new_rating = 5 if original_rating != 5 else 4
    print(f"Updating rating to {new_rating}...")
    
    response = requests.post(f"{BASE_URL}/api/songs/{song_id}/rate", json={"rating": new_rating})
    if response.status_code != 200:
        print(f"FAILED: Could not rate song. {response.text}")
        return
        
    # 3. Verify update
    response = requests.get(f"{BASE_URL}/api/songs", params={"limit": 1}) # Assuming order hasn't changed or we find it
    # Better to search for it or get all and find it, but let's assume it's the same one for now or fetch by ID if we had an endpoint
    # We don't have a get_song_by_id endpoint, so let's use search if unique, or just trust the response for now.
    # Actually, let's just use the search endpoint with the specific title to find it.
    
    # But wait, search uses BM25 which might not be updated instantly if we were adding songs, but rating is in DB.
    # Search gets IDs from BM25 then fetches from DB, so rating should be fresh.
    
    search_response = requests.get(f"{BASE_URL}/api/songs/search", params={"title": song['title'], "limit": 1})
    updated_song = search_response.json()['items'][0]
    
    if updated_song['id'] == song_id and updated_song['rating'] == new_rating:
        print(f"SUCCESS: Rating updated to {updated_song['rating']}")
    else:
        print(f"FAILED: Rating mismatch. Expected {new_rating}, got {updated_song['rating']}")
    
    cleanup()
