import requests
import json
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

def test_search():
    upload_sample_data()
    print("Testing Search API...")
    
    # Test 1: Basic Search
    query = "the"
    response = requests.get(f"{BASE_URL}/api/songs/search", params={"title": query, "limit": 5})
    
    if response.status_code != 200:
        print(f"FAILED: Status code {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print(f"Search for '{query}': Found {data['total']} results")
    
    if not data['items']:
        print("FAILED: No items found")
        return

    first_item = data['items'][0]
    print(f"Top result: {first_item.get('title')} (Score: {first_item.get('score')})")
    
    # Test 2: Pagination
    print("\nTesting Pagination...")
    page1 = requests.get(f"{BASE_URL}/api/songs/search", params={"title": query, "page": 1, "limit": 2}).json()
    page2 = requests.get(f"{BASE_URL}/api/songs/search", params={"title": query, "page": 2, "limit": 2}).json()
    
    print(f"Page 1 items: {[item['title'] for item in page1['items']]}")
    print(f"Page 2 items: {[item['title'] for item in page2['items']]}")
    
    if page1['items'][0]['id'] == page2['items'][0]['id']:
        print("FAILED: Page 1 and Page 2 have same first item")
    else:
        print("SUCCESS: Pagination seems to work")
    
    cleanup()

if __name__ == "__main__":
    test_search()
