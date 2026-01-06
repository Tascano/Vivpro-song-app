"""
Unit tests for Song model
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.song import Song
from app.core.database import Base


class TestSongModel:
    """Tests for Song model"""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory database session for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
        Base.metadata.drop_all(engine)
    
    def test_song_creation(self, db_session):
        """Test creating a Song instance"""
        song = Song(
            id="test_1",
            title="Test Song",
            song_class="pop",
            rating=4,
            danceability=0.7,
            energy=0.8,
            key=1,
            loudness=-5.0,
            mode=1,
            acousticness=0.3,
            instrumentalness=0.1,
            liveness=0.2,
            valence=0.6,
            tempo=120.0,
            duration_ms=180000,
            time_signature=4,
            num_bars=100,
            num_sections=5,
            num_segments=200
        )
        
        db_session.add(song)
        db_session.commit()
        
        assert song.id == "test_1"
        assert song.title == "Test Song"
        assert song.song_class == "pop"
        assert song.rating == 4
    
    def test_song_default_values(self, db_session):
        """Test Song model default values"""
        song = Song(
            id="test_2",
            title="Default Song"
        )
        
        db_session.add(song)
        db_session.commit()
        
        assert song.rating == 0
        assert song.danceability == 0.0
        assert song.energy == 0.0
        assert song.key == 0
        assert song.loudness == 0.0
        assert song.mode == 0
        assert song.acousticness == 0.0
        assert song.instrumentalness == 0.0
        assert song.liveness == 0.0
        assert song.valence == 0.0
        assert song.tempo == 0.0
        assert song.duration_ms == 0
        assert song.time_signature == 4
        assert song.num_bars == 0
        assert song.num_sections == 0
        assert song.num_segments == 0
    
    def test_song_unique_id(self, db_session):
        """Test that Song id must be unique"""
        song1 = Song(id="unique_1", title="Song 1")
        song2 = Song(id="unique_1", title="Song 2")  # Same ID
        
        db_session.add(song1)
        db_session.commit()
        
        db_session.add(song2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_song_retrieval(self, db_session):
        """Test retrieving a Song from database"""
        song = Song(id="retrieve_1", title="Retrieve Song", rating=5)
        db_session.add(song)
        db_session.commit()
        
        retrieved = db_session.query(Song).filter(Song.id == "retrieve_1").first()
        
        assert retrieved is not None
        assert retrieved.id == "retrieve_1"
        assert retrieved.title == "Retrieve Song"
        assert retrieved.rating == 5
    
    def test_song_update(self, db_session):
        """Test updating a Song"""
        song = Song(id="update_1", title="Original Title", rating=2)
        db_session.add(song)
        db_session.commit()
        
        song.title = "Updated Title"
        song.rating = 5
        db_session.commit()
        
        updated = db_session.query(Song).filter(Song.id == "update_1").first()
        assert updated.title == "Updated Title"
        assert updated.rating == 5
    
    def test_song_deletion(self, db_session):
        """Test deleting a Song"""
        song = Song(id="delete_1", title="Delete Song")
        db_session.add(song)
        db_session.commit()
        
        db_session.delete(song)
        db_session.commit()
        
        deleted = db_session.query(Song).filter(Song.id == "delete_1").first()
        assert deleted is None
    
    def test_song_all_fields(self, db_session):
        """Test Song with all fields populated"""
        song = Song(
            id="full_1",
            title="Full Song",
            song_class="rock",
            rating=3,
            danceability=0.65,
            energy=0.75,
            key=5,
            loudness=-6.5,
            mode=0,
            acousticness=0.25,
            instrumentalness=0.15,
            liveness=0.18,
            valence=0.65,
            tempo=125.5,
            duration_ms=195000,
            time_signature=3,
            num_bars=120,
            num_sections=6,
            num_segments=250
        )
        
        db_session.add(song)
        db_session.commit()
        
        retrieved = db_session.query(Song).filter(Song.id == "full_1").first()
        assert retrieved.danceability == 0.65
        assert retrieved.energy == 0.75
        assert retrieved.key == 5
        assert retrieved.loudness == -6.5
        assert retrieved.mode == 0
        assert retrieved.acousticness == 0.25
        assert retrieved.instrumentalness == 0.15
        assert retrieved.liveness == 0.18
        assert retrieved.valence == 0.65
        assert retrieved.tempo == 125.5
        assert retrieved.duration_ms == 195000
        assert retrieved.time_signature == 3
        assert retrieved.num_bars == 120
        assert retrieved.num_sections == 6
        assert retrieved.num_segments == 250

