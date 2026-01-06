"""
Unit tests for data_utils.py with mocked dependencies
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from sqlalchemy.orm import Session

from app.utils.data_utils import normalize_and_insert_data
from app.models.song import Song


class TestNormalizeAndInsertData:
    """Tests for normalize_and_insert_data function"""
    
    def test_column_oriented_new_songs(self, mock_db, mock_query):
        """Test column-oriented format with new songs"""
        # Setup column-oriented data
        column_data = {
            "id": {"0": "song1", "1": "song2"},
            "title": {"0": "Song 1", "1": "Song 2"},
            "class": {"0": "pop", "1": "rock"},
            "danceability": {"0": 0.5, "1": 0.7},
            "energy": {"0": 0.6, "1": 0.8},
            "key": {"0": 1, "1": 2},
            "loudness": {"0": -5.0, "1": -4.0},
            "mode": {"0": 1, "1": 0},
            "acousticness": {"0": 0.3, "1": 0.2},
            "instrumentalness": {"0": 0.1, "1": 0.2},
            "liveness": {"0": 0.2, "1": 0.3},
            "valence": {"0": 0.6, "1": 0.7},
            "tempo": {"0": 120.0, "1": 130.0},
            "duration_ms": {"0": 180000, "1": 200000},
            "time_signature": {"0": 4, "1": 4},
            "num_bars": {"0": 100, "1": 110},
            "num_sections": {"0": 5, "1": 6},
            "num_segments": {"0": 200, "1": 220}
        }
        
        # Mock query to return None (no existing songs)
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(column_data, mock_db)
        
        assert "Added 2 new songs" in result
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()
    
    def test_column_oriented_update_existing(self, mock_db, mock_query, mock_song):
        """Test column-oriented format updating existing songs"""
        column_data = {
            "id": {"0": "test_song_1"},
            "title": {"0": "Updated Title"},
            "class": {"0": "rock"},
            "danceability": {"0": 0.8}
        }
        
        # Mock query to return existing song
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_song
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(column_data, mock_db)
        
        assert mock_song.title == "Updated Title"
        assert mock_song.song_class == "rock"
        assert mock_song.danceability == 0.8
        assert mock_db.add.call_count == 0  # Should not add, only update
        mock_db.commit.assert_called_once()
    
    def test_column_oriented_empty_id_skipped(self, mock_db, mock_query):
        """Test column-oriented format skips entries with empty id"""
        column_data = {
            "id": {"0": "song1", "1": ""},
            "title": {"0": "Song 1", "1": "Song 2"}
        }
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(column_data, mock_db)
        
        # Should only add one song (the one with non-empty id)
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_new_songs(self, mock_db, mock_query):
        """Test row-oriented format with new songs"""
        row_data = [
            {
                "id": "row1",
                "title": "Row Song 1",
                "class": "pop",
                "danceability": 0.5,
                "energy": 0.6
            },
            {
                "id": "row2",
                "title": "Row Song 2",
                "class": "rock",
                "danceability": 0.7,
                "energy": 0.8
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        assert "Added 2 new songs" in result
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_update_existing(self, mock_db, mock_query, mock_song):
        """Test row-oriented format updating existing songs"""
        row_data = [
            {
                "id": "test_song_1",
                "title": "Updated Row Title",
                "class": "jazz",
                "danceability": 0.9
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_song
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        assert mock_song.title == "Updated Row Title"
        assert mock_song.song_class == "jazz"
        assert mock_song.danceability == 0.9
        assert mock_db.add.call_count == 0
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_wrapped_in_dict(self, mock_db, mock_query):
        """Test row-oriented format wrapped in dict with 'songs' key"""
        wrapped_data = {
            "songs": [
                {
                    "id": "wrapped1",
                    "title": "Wrapped Song",
                    "class": "pop"
                }
            ]
        }
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(wrapped_data, mock_db)
        
        assert "Added 1 new songs" in result
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_single_dict(self, mock_db, mock_query):
        """Test row-oriented format with single dict (not in list)"""
        single_dict = {
            "id": "single1",
            "title": "Single Song",
            "class": "pop"
        }
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(single_dict, mock_db)
        
        assert "Added 1 new songs" in result
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_missing_title_skipped(self, mock_db, mock_query):
        """Test row-oriented format skips entries without title"""
        row_data = [
            {
                "id": "row1",
                "title": "Valid Song"
            },
            {
                "id": "row2"
                # Missing title
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        # Should only add one song (the one with title)
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_empty_id_skipped(self, mock_db, mock_query):
        """Test row-oriented format skips entries with empty id"""
        row_data = [
            {
                "id": "row1",
                "title": "Valid Song"
            },
            {
                "id": "",
                "title": "Invalid Song"
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        # Should only add one song (the one with non-empty id)
        assert mock_db.add.call_count == 1
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_song_class_fallback(self, mock_db, mock_query, mock_song):
        """Test row-oriented format uses song_class if class is missing"""
        row_data = [
            {
                "id": "test_song_1",
                "title": "Test Song",
                "song_class": "alternative"  # Using song_class instead of class
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_song
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        assert mock_song.song_class == "alternative"
        mock_db.commit.assert_called_once()
    
    def test_invalid_format_raises_error(self, mock_db):
        """Test invalid format raises ValueError"""
        invalid_data = "not a dict or list"
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            normalize_and_insert_data(invalid_data, mock_db)
    
    def test_column_oriented_default_values(self, mock_db, mock_query):
        """Test column-oriented format uses default values for missing fields"""
        column_data = {
            "id": {"0": "minimal_song"},
            "title": {"0": "Minimal Song"}
            # Missing other fields
        }
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(column_data, mock_db)
        
        # Verify Song was created with defaults
        call_args = mock_db.add.call_args[0][0]
        assert call_args.id == "minimal_song"
        assert call_args.title == "Minimal Song"
        assert call_args.song_class == "0"  # Default
        assert call_args.rating == 0
        assert call_args.danceability == 0.0
        assert call_args.time_signature == 4  # Default
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_default_values(self, mock_db, mock_query):
        """Test row-oriented format uses default values for missing fields"""
        row_data = [
            {
                "id": "minimal_row",
                "title": "Minimal Row Song"
                # Missing other fields
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        # Verify Song was created with defaults
        call_args = mock_db.add.call_args[0][0]
        assert call_args.id == "minimal_row"
        assert call_args.title == "Minimal Row Song"
        assert call_args.rating == 0
        assert call_args.danceability == 0.0
        assert call_args.time_signature == 4
        mock_db.commit.assert_called_once()
    
    def test_column_oriented_mixed_new_and_existing(self, mock_db, mock_query, mock_song):
        """Test column-oriented format with mix of new and existing songs"""
        column_data = {
            "id": {"0": "test_song_1", "1": "new_song"},
            "title": {"0": "Updated", "1": "New"}
        }
        
        # First call returns existing, second returns None (new)
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [mock_song, None]
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(column_data, mock_db)
        
        # Should update one and add one
        assert mock_db.add.call_count == 1
        assert mock_song.title == "Updated"
        mock_db.commit.assert_called_once()
    
    def test_row_oriented_mixed_new_and_existing(self, mock_db, mock_query, mock_song):
        """Test row-oriented format with mix of new and existing songs"""
        row_data = [
            {
                "id": "test_song_1",
                "title": "Updated"
            },
            {
                "id": "new_song",
                "title": "New"
            }
        ]
        
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [mock_song, None]
        mock_db.query.return_value = mock_query
        
        result = normalize_and_insert_data(row_data, mock_db)
        
        # Should update one and add one
        assert mock_db.add.call_count == 1
        assert mock_song.title == "Updated"
        mock_db.commit.assert_called_once()

