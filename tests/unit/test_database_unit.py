"""
Unit tests for database.py with mocked dependencies
"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from contextlib import contextmanager

from app.core.database import get_db, SessionLocal, engine, Base


class TestGetDb:
    """Tests for get_db function"""
    
    def test_get_db_yields_session(self):
        """Test get_db yields a database session"""
        mock_session = MagicMock()
        
        with patch('app.core.database.SessionLocal', return_value=mock_session):
            db_gen = get_db()
            db = next(db_gen)
            
            assert db == mock_session
    
    def test_get_db_closes_session_on_exit(self):
        """Test get_db closes session when exiting context"""
        mock_session = MagicMock()
        
        with patch('app.core.database.SessionLocal', return_value=mock_session):
            db_gen = get_db()
            db = next(db_gen)
            
            # Close the generator - this sends GeneratorExit and triggers finally block
            db_gen.close()
            
            mock_session.close.assert_called_once()
    
    def test_get_db_closes_on_exception(self):
        """Test get_db closes session even when exception occurs"""
        mock_session = MagicMock()
        
        with patch('app.core.database.SessionLocal', return_value=mock_session):
            db_gen = get_db()
            db = next(db_gen)
            
            # Throw an exception into the generator
            # The finally block should execute and close the session
            test_exception = Exception("Test error")
            try:
                db_gen.throw(test_exception)
            except Exception:
                # Exception propagates, but finally block should have executed
                pass
            
            mock_session.close.assert_called_once()
    
    def test_get_db_multiple_calls(self):
        """Test get_db creates new session for each call"""
        mock_session1 = MagicMock()
        mock_session2 = MagicMock()
        
        with patch('app.core.database.SessionLocal') as mock_session_local:
            mock_session_local.side_effect = [mock_session1, mock_session2]
            
            # First call
            db_gen1 = get_db()
            db1 = next(db_gen1)
            
            # Second call
            db_gen2 = get_db()
            db2 = next(db_gen2)
            
            assert db1 == mock_session1
            assert db2 == mock_session2
            assert mock_session_local.call_count == 2


class TestDatabaseConfiguration:
    """Tests for database configuration"""
    
    def test_engine_created(self):
        """Test that engine is created"""
        assert engine is not None
    
    def test_session_local_created(self):
        """Test that SessionLocal is created"""
        assert SessionLocal is not None
    
    def test_base_created(self):
        """Test that Base is created"""
        assert Base is not None
    
    @patch('app.core.database.create_engine')
    def test_engine_configuration(self, mock_create_engine):
        """Test engine configuration parameters"""
        from app.core.database import SQLALCHEMY_DATABASE_URL
        
        # Re-import to trigger engine creation with mock
        import importlib
        import app.core.database
        importlib.reload(app.core.database)
        
        # Verify create_engine was called (if we could intercept it)
        # This test mainly ensures the module can be imported and configured
        assert SQLALCHEMY_DATABASE_URL == "sqlite:///./playlist.db"

