import requests
import json
import os

BASE_URL = "http://localhost:8000"
TEST_FILE = "test_upload.json"

def create_test_file():
    data = [
        {
            "id": "test_1",
            "title": "Unique Test Song Alpha",
            "duration": "3:00",
            "class": "pop",
            "rating": 0
        },
        {
            "id": "test_2",
            "title": "Unique Test Song Beta",
            "duration": "2:30",
            "class": "rock",
            "rating": 0
        }
    ]
    with open(TEST_FILE, "w") as f:
        json.dump(data, f)
    print(f"Created {TEST_FILE}")

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

def test_upload_and_search():
    print("Testing Upload and Search...")
    
    # 1. Upload
    with open(TEST_FILE, "rb") as f:
        files = {"file": (TEST_FILE, f, "application/json")}
        response = requests.post(f"{BASE_URL}/api/songs/upload", files=files)
        
    if response.status_code != 200:
        print(f"FAILED: Upload failed. {response.text}")
        return
        
    print(f"Upload response: {response.json()}")
    
    # 2. Search for uploaded song
    query = "Alpha"
    print(f"Searching for '{query}'...")
    response = requests.get(f"{BASE_URL}/api/songs/search", params={"title": query})
    
    if response.status_code != 200:
        print(f"FAILED: Search failed. {response.text}")
        return
        
    data = response.json()
    items = data['items']
    print(f"Found {len(items)} results")
    
    found = False
    for item in items:
        if item['id'] == "test_1":
            found = True
            print(f"SUCCESS: Found uploaded song: {item['title']} (Score: {item.get('score')})")
            break
            
    if not found:
        print("FAILED: Uploaded song not found in search results")
    
    cleanup()

    # Cleanup
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

if __name__ == "__main__":
    create_test_file()
    test_upload_and_search()
