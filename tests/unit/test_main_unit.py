"""
Unit tests for main.py endpoints with mocked dependencies
"""
import pytest
import json
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app, get_songs, search_songs, upload_file, get_all_songs, delete_all_songs, rate_song
from app.models.song import Song


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint returns ok"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGetSongs:
    """Tests for GET /api/songs endpoint"""
    
    def test_get_songs_default_params(self, mock_db, mock_query, mock_song):
        """Test get_songs with default parameters"""
        # Setup mocks
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song]
        mock_db.query.return_value = mock_query
        
        # Call function
        result = get_songs(page=1, limit=10, sort_by=None, order="asc", db=mock_db)
        
        # Assertions
        assert result["total"] == 1
        assert result["page"] == 1
        assert result["size"] == 10
        assert len(result["items"]) == 1
        mock_db.query.assert_called_once_with(Song)
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
    
    def test_get_songs_with_pagination(self, mock_db, mock_query, mock_song):
        """Test get_songs with pagination"""
        mock_query.count.return_value = 25
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song] * 5
        mock_db.query.return_value = mock_query
        
        result = get_songs(page=2, limit=5, sort_by=None, order="asc", db=mock_db)
        
        assert result["total"] == 25
        assert result["page"] == 2
        assert result["size"] == 5
        assert len(result["items"]) == 5
        mock_query.offset.assert_called_once_with(5)
        mock_query.limit.assert_called_once_with(5)
    
    def test_get_songs_with_sorting_asc(self, mock_db, mock_query, mock_song):
        """Test get_songs with ascending sort"""
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song]
        mock_db.query.return_value = mock_query
        
        # Mock Song model to have title attribute
        mock_column = Mock()
        mock_column.asc = Mock(return_value=Mock())
        with patch.object(Song, 'title', mock_column, create=True):
            result = get_songs(page=1, limit=10, sort_by="title", order="asc", db=mock_db)
        
        assert result["total"] == 1
        mock_query.order_by.assert_called()
    
    def test_get_songs_with_sorting_desc(self, mock_db, mock_query, mock_song):
        """Test get_songs with descending sort"""
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song]
        mock_db.query.return_value = mock_query
        
        # Mock column with desc() method
        mock_column = Mock()
        mock_column.desc = Mock(return_value=Mock())
        with patch.object(Song, 'title', mock_column, create=True):
            result = get_songs(page=1, limit=10, sort_by="title", order="desc", db=mock_db)
        
        assert result["total"] == 1
        mock_column.desc.assert_called_once()
    
    def test_get_songs_invalid_sort_column(self, mock_db, mock_query, mock_song):
        """Test get_songs with invalid sort column"""
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song]
        mock_db.query.return_value = mock_query
        
        # Invalid field should not exist on Song model
        result = get_songs(page=1, limit=10, sort_by="invalid_field", order="asc", db=mock_db)
        
        assert result["total"] == 1
        mock_query.order_by.assert_not_called()


class TestSearchSongs:
    """Tests for GET /api/songs/search endpoint"""
    
    def test_search_songs_found(self, mock_db, mock_query, mock_song):
        """Test search_songs finds matching songs"""
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song]
        mock_db.query.return_value = mock_query
        
        result = search_songs(title="Test", page=1, limit=10, db=mock_db)
        
        assert result["total"] == 1
        assert result["page"] == 1
        assert result["size"] == 10
        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "test_song_1"
        assert result["items"][0]["title"] == "Test Song"
        mock_query.filter.assert_called_once()
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
    
    def test_search_songs_no_results(self, mock_db, mock_query):
        """Test search_songs with no results"""
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        result = search_songs(title="Nonexistent", page=1, limit=10, db=mock_db)
        
        assert result["total"] == 0
        assert len(result["items"]) == 0
    
    def test_search_songs_pagination(self, mock_db, mock_query, mock_song):
        """Test search_songs with pagination"""
        mock_query.count.return_value = 15
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_song] * 5
        mock_db.query.return_value = mock_query
        
        result = search_songs(title="Test", page=2, limit=5, db=mock_db)
        
        assert result["total"] == 15
        assert result["page"] == 2
        assert result["size"] == 5
        assert len(result["items"]) == 5
        mock_query.offset.assert_called_once_with(5)


class TestUploadFile:
    """Tests for POST /api/songs/upload endpoint"""
    
    @pytest.mark.asyncio
    async def test_upload_file_valid_json(self, mock_db):
        """Test upload_file with valid JSON"""
        mock_file = AsyncMock()
        mock_file.filename = "test.json"
        mock_file.read = AsyncMock(return_value=json.dumps([
            {"id": "1", "title": "Test Song", "class": "pop"}
        ]).encode())
        
        with patch('app.main.normalize_and_insert_data', return_value="Added 1 new songs"):
            result = await upload_file(file=mock_file, db=mock_db)
        
        assert result["message"] == "Added 1 new songs"
        mock_file.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_extension(self, mock_db):
        """Test upload_file with invalid file extension"""
        mock_file = AsyncMock()
        mock_file.filename = "test.txt"
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_file(file=mock_file, db=mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Only JSON files are allowed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_json(self, mock_db):
        """Test upload_file with invalid JSON"""
        mock_file = AsyncMock()
        mock_file.filename = "test.json"
        mock_file.read = AsyncMock(return_value=b"invalid json")
        
        with pytest.raises(HTTPException) as exc_info:
            await upload_file(file=mock_file, db=mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Invalid JSON" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_upload_file_processing_error(self, mock_db):
        """Test upload_file with processing error"""
        mock_file = AsyncMock()
        mock_file.filename = "test.json"
        mock_file.read = AsyncMock(return_value=json.dumps({"test": "data"}).encode())
        
        with patch('app.main.normalize_and_insert_data', side_effect=Exception("Processing error")):
            with pytest.raises(HTTPException) as exc_info:
                await upload_file(file=mock_file, db=mock_db)
        
        assert exc_info.value.status_code == 500


class TestGetAllSongs:
    """Tests for GET /api/songs/all endpoint"""
    
    def test_get_all_songs(self, mock_db, mock_query, mock_song):
        """Test get_all_songs returns all songs"""
        mock_query.all.return_value = [mock_song] * 3
        mock_db.query.return_value = mock_query
        
        result = get_all_songs(db=mock_db)
        
        assert len(result) == 3
        mock_db.query.assert_called_once_with(Song)
        mock_query.all.assert_called_once()


class TestDeleteAllSongs:
    """Tests for DELETE /api/songs/all endpoint"""
    
    def test_delete_all_songs_success(self, mock_db, mock_query):
        """Test delete_all_songs successfully deletes all songs"""
        mock_query.count.return_value = 5
        mock_query.delete.return_value = None
        mock_db.query.return_value = mock_query
        
        result = delete_all_songs(db=mock_db)
        
        assert result["message"] == "Successfully deleted 5 songs"
        mock_db.commit.assert_called_once()
        mock_query.delete.assert_called_once()
    
    def test_delete_all_songs_error(self, mock_db, mock_query):
        """Test delete_all_songs handles errors"""
        mock_query.count.return_value = 5
        mock_query.delete.side_effect = Exception("Database error")
        mock_db.query.return_value = mock_query
        
        with pytest.raises(HTTPException) as exc_info:
            delete_all_songs(db=mock_db)
        
        assert exc_info.value.status_code == 500
        mock_db.rollback.assert_called_once()


class TestRateSong:
    """Tests for POST /api/songs/{song_id}/rate endpoint"""
    
    def test_rate_song_success(self, mock_db, mock_query, mock_song):
        """Test rate_song successfully updates rating"""
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_song
        mock_db.query.return_value = mock_query
        
        from app.main import RatingRequest
        request = RatingRequest(rating=4)
        
        result = rate_song(song_id="test_song_1", request=request, db=mock_db)
        
        assert result["message"] == "Rating updated"
        assert result["song_id"] == "test_song_1"
        assert result["rating"] == 4
        assert mock_song.rating == 4
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_song)
    
    def test_rate_song_invalid_rating_too_high(self, mock_db):
        """Test rate_song with rating > 5"""
        from app.main import RatingRequest
        request = RatingRequest(rating=6)
        
        with pytest.raises(HTTPException) as exc_info:
            rate_song(song_id="test_song_1", request=request, db=mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Rating must be between 0 and 5" in str(exc_info.value.detail)
    
    def test_rate_song_invalid_rating_too_low(self, mock_db):
        """Test rate_song with rating < 0"""
        from app.main import RatingRequest
        request = RatingRequest(rating=-1)
        
        with pytest.raises(HTTPException) as exc_info:
            rate_song(song_id="test_song_1", request=request, db=mock_db)
        
        assert exc_info.value.status_code == 400
        assert "Rating must be between 0 and 5" in str(exc_info.value.detail)
    
    def test_rate_song_not_found(self, mock_db, mock_query):
        """Test rate_song with non-existent song"""
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        from app.main import RatingRequest
        request = RatingRequest(rating=3)
        
        with pytest.raises(HTTPException) as exc_info:
            rate_song(song_id="nonexistent", request=request, db=mock_db)
        
        assert exc_info.value.status_code == 404
        assert "Song not found" in str(exc_info.value.detail)
    
    def test_rate_song_boundary_values(self, mock_db, mock_query, mock_song):
        """Test rate_song with boundary values (0 and 5)"""
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_song
        mock_db.query.return_value = mock_query
        
        from app.main import RatingRequest
        
        # Test rating = 0
        request = RatingRequest(rating=0)
        result = rate_song(song_id="test_song_1", request=request, db=mock_db)
        assert result["rating"] == 0
        
        # Test rating = 5
        request = RatingRequest(rating=5)
        result = rate_song(song_id="test_song_1", request=request, db=mock_db)
        assert result["rating"] == 5

