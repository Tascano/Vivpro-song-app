import sys
import os
import json

# Add parent directory to path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

client = TestClient(app)

def setup_module():
    """Setup that runs before all tests - initialize DB and upload sample data"""
    # Manually initialize database since TestClient may not run startup events
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    sample_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sample_data', 'Playlist.json')
    with open(sample_file_path, 'rb') as f:
        response = client.post("/api/songs/upload", files={"file": ("Playlist.json", f, "application/json")})
        assert response.status_code == 200
        print(f"Uploaded sample data: {response.json()}")

def test_read_songs():
    response = client.get("/api/songs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 10  # Default limit

def test_search_song():
    # Assuming "3AM" exists in the data (it does, id 0)
    response = client.get("/api/songs/search?title=3AM")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    found = False
    for item in data["items"]:
        if item["title"] == "3AM":
            found = True
            break
    assert found

def test_rate_song():
    # First get a song ID
    response = client.get("/api/songs")
    items = response.json()["items"]
    if not items:
        return # Skip if no data
        
    song_id = items[0]["id"]
    
    # Rate it
    response = client.post(f"/api/songs/{song_id}/rate", json={"rating": 5})
    assert response.status_code == 200
    assert response.json()["rating"] == 5
    
    # Verify rating
    # We need to fetch the song again. Since we don't have get_song_by_id, we use search or list.
    # List is easiest if it's on the first page.
    response = client.get("/api/songs")
    items = response.json()["items"]
    # Find the song
    for item in items:
        if item["id"] == song_id:
            assert item["rating"] == 5
            break

def test_invalid_rating():
    response = client.get("/api/songs")
    items = response.json()["items"]
    if not items:
        return
        
    song_id = items[0]["id"]
    response = client.post(f"/api/songs/{song_id}/rate", json={"rating": 6})
    assert response.status_code == 400

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_search_no_results():
    response = client.get("/api/songs/search?title=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0

def test_pagination():
    response = client.get("/api/songs/search?title=the&page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2

def test_rate_nonexistent_song():
    response = client.post("/api/songs/nonexistent/rate", json={"rating": 3})
    assert response.status_code == 404

def test_upload_row_oriented():
    # Test row-oriented JSON upload
    row_data = [
        {
            "id": "row_test_1",
            "title": "Row Test Song",
            "duration": "3:00",
            "class": "pop",
            "rating": 0
        }
    ]
    response = client.post("/api/songs/upload", files={"file": ("test.json", json.dumps(row_data).encode(), "application/json")})
    assert response.status_code == 200
    assert "Added 1 new songs" in response.json()["message"]

def test_invalid_upload():
    response = client.post("/api/songs/upload", files={"file": ("test.txt", b"invalid json", "application/json")})
    assert response.status_code == 400

def test_songs_with_params():
    response = client.get("/api/songs?page=1&limit=5&order=desc")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5

def test_invalid_sort_by():
    response = client.get("/api/songs?sort_by=invalid_field")
    assert response.status_code == 200  # Should not sort, just return data

def test_upload_column_data_again():
    # Upload the same column data again to cover update path
    sample_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sample_data', 'Playlist.json')
    with open(sample_file_path, 'rb') as f:
        response = client.post("/api/songs/upload", files={"file": ("Playlist.json", f, "application/json")})
    assert response.status_code == 200
    # Should update existing songs

def test_upload_wrapped_row_data():
    # Test row data wrapped in {"songs": [...]}
    wrapped_data = {
        "songs": [
            {
                "id": "wrapped_test_1",
                "title": "Wrapped Test Song",
                "class": "pop"
            }
        ]
    }
    
    response = client.post("/api/songs/upload", files={"file": ("test.json", json.dumps(wrapped_data).encode(), "application/json")})
    assert response.status_code == 200

def test_upload_invalid_format():
    # Test invalid format (not list or dict)
    response = client.post("/api/songs/upload", files={"file": ("test.json", b"\"string\"", "application/json")})
    assert response.status_code == 500

def test_upload_dict_without_songs():
    # Test dict without "songs" key
    dict_data = {"id": "dict_test", "title": "Dict Test"}
    response = client.post("/api/songs/upload", files={"file": ("test.json", json.dumps(dict_data).encode(), "application/json")})
    assert response.status_code == 200

def test_upload_row_update():
    # Upload row data, then upload again with same ID to cover update path
    row_data = [
        {
            "id": "update_test_1",
            "title": "Update Test Song",
            "class": "rock"
        }
    ]
    # First upload
    response = client.post("/api/songs/upload", files={"file": ("test.json", json.dumps(row_data).encode(), "application/json")})
    assert response.status_code == 200
    # Second upload with same ID
    response = client.post("/api/songs/upload", files={"file": ("test.json", json.dumps(row_data).encode(), "application/json")})
    assert response.status_code == 200

def test_songs_sorting():
    response = client.get("/api/songs?sort_by=title&order=desc")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data