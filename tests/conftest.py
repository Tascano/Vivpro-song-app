import sys
import os
from unittest.mock import MagicMock, Mock
import pytest
from sqlalchemy.orm import Session

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock(spec=Session)
    db.commit = Mock()
    db.rollback = Mock()
    db.refresh = Mock()
    db.add = Mock()
    db.query = Mock()
    db.delete = Mock()
    return db


@pytest.fixture
def mock_song():
    """Mock Song object"""
    song = MagicMock()
    song.id = "test_song_1"
    song.title = "Test Song"
    song.song_class = "pop"
    song.rating = 0
    song.danceability = 0.5
    song.energy = 0.7
    song.key = 1
    song.loudness = -5.0
    song.mode = 1
    song.acousticness = 0.3
    song.instrumentalness = 0.1
    song.liveness = 0.2
    song.valence = 0.6
    song.tempo = 120.0
    song.duration_ms = 180000
    song.time_signature = 4
    song.num_bars = 100
    song.num_sections = 5
    song.num_segments = 200
    return song


@pytest.fixture
def mock_query():
    """Mock SQLAlchemy query object"""
    query = MagicMock()
    query.filter = Mock(return_value=query)
    query.order_by = Mock(return_value=query)
    query.offset = Mock(return_value=query)
    query.limit = Mock(return_value=query)
    query.count = Mock(return_value=10)
    query.all = Mock(return_value=[])
    query.first = Mock(return_value=None)
    query.delete = Mock(return_value=None)
    return query