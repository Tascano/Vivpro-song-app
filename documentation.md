# Technical Documentation

This document provides comprehensive technical details about the Playlist Management Application, including implementation decisions, architecture choices, and development guidelines.

## Architecture Overview

### System Components

**Backend (FastAPI)**
- **API Layer**: RESTful endpoints for CRUD operations
- **Business Logic**: Data processing and validation
- **Data Access**: SQLAlchemy ORM with SQLite
- **File Processing**: JSON upload and normalization

**Frontend (Vanilla JS)**
- **UI Components**: Dynamic table, forms, charts
- **State Management**: Client-side data handling
- **API Integration**: AJAX calls to backend

**Database (SQLite)**
- **Schema**: Single `songs` table with analytics columns
- **Indexing**: Optimized for search and pagination
- **Migrations**: Automatic table creation on startup

### Design Principles

- **Simplicity**: Minimal dependencies, straightforward architecture
- **Testability**: Comprehensive test coverage at multiple levels
- **Maintainability**: Clear separation of concerns, documented code
- **Performance**: Efficient queries, pagination, minimal data transfer

## Configuration & Environment

### Configuration Management

**Database Configuration** (`app/core/database.py`):
- SQLAlchemy engine with SQLite database
- Database URL hardcoded as `sqlite:///./playlist.db`
- Session management with proper cleanup
- Automatic table creation on startup (drops and recreates tables on each startup)

**CORS Configuration** (`app/main.py`):
- Configured for local development
- Allows all origins, methods, and headers
- Production should restrict to specific domains

## Development Workflow

### Local Development Setup

1. **Clone and Setup**:
   ```bash
   git clone <repo>
   cd playlist-management-app
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Initialization**:
   - Automatic on first run
   - Fresh database created each startup
   - No manual migration scripts needed

3. **Testing Cycle**:
   ```bash
   # Fast unit tests
   pytest tests/unit/ -v

   # Integration tests (requires server)
   uvicorn app.main:app --host 0.0.0.0 --port 8000 &
   python tests/integ/verify_upload.py

   # Manual testing
   # Open http://localhost:8000
   ```

### Code Organization

**Import Structure**:
```
app/
├── main.py           # Entry point, routes, app config, Pydantic models
├── core/             # Infrastructure (database, config)
│   └── database.py   # Database engine and session management
├── models/           # Data models (SQLAlchemy)
│   └── song.py       # Song model definition
└── utils/            # Utilities (data processing)
    └── data_utils.py # JSON normalization and data insertion
```

**Dependency Injection**:
- FastAPI's `Depends()` for database sessions
- Automatic session cleanup
- Test-friendly with overrides

## Data Processing & Validation

### JSON Format Detection

**Column-Oriented Detection**:
```python
is_column_oriented = isinstance(data, dict) and all(isinstance(v, dict) for v in data.values())
```

**Row-Oriented Detection**:
The code handles row-oriented format as the fallback case when data is not column-oriented. It checks if data is a list or a dict containing a "songs" key.

### Data Normalization Process

1. **Format Detection**: Automatically determines input format
2. **Field Mapping**: Maps JSON fields to database columns
3. **Validation**: Ensures required fields present
4. **Deduplication**: Updates existing records, inserts new ones
5. **Type Conversion**: Safely converts strings to appropriate types

### Error Handling in Data Processing

- **Invalid JSON**: Returns 400 with descriptive message
- **Missing Fields**: Uses defaults, logs warnings
- **Type Errors**: Safe conversion with fallbacks
- **Large Files**: No explicit size limits (SQLite handles gracefully)

## Testing Strategy

### Unit Testing (`tests/unit/`)

**TestClient Usage**:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_songs():
    response = client.get("/api/songs")
    assert response.status_code == 200
```

**Coverage Areas**:
- API endpoint responses
- Data validation
- Error conditions
- Business logic

### Integration Testing (`tests/integ/`)

**Live Server Testing**:
```python
import requests

BASE_URL = "http://localhost:8000"

def test_upload_integration():
    with open("test_data.json", "rb") as f:
        response = requests.post(f"{BASE_URL}/api/songs/upload", files={"file": f})
    assert response.status_code == 200
```

**Test Scenarios**:
- End-to-end file upload
- Search functionality
- Data persistence
- Cross-endpoint interactions

### Test Data Management

**conftest.py**: Pytest configuration and fixtures
- Database session management
- Test data cleanup
- Common test utilities


## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (validation errors, invalid JSON)
- **404**: Not Found (song doesn't exist)
- **500**: Internal Server Error (database failures, unexpected errors)

### Validation Errors

**Pydantic Models**:
```python
class RatingRequest(BaseModel):
    rating: int
```

**Custom Validation**:
- Rating range checking (0-5) performed in endpoint handler
- File format validation (must be .json)
- Required field presence handled with defaults in data processing

### Exception Handling

**Global Exception Handler** (FastAPI automatic)
- Converts exceptions to appropriate HTTP responses
- Logs errors for debugging
- Returns user-friendly error messages

## API Implementation Details

### Pagination Logic

**Offset-Based Pagination**:
```python
def get_songs(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    query = db.query(Song).offset(offset).limit(limit)
    return query.all()
```

**Response Format**:
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 10
}
```

### Search Implementation

**Case-Insensitive Search**:
```python
query = db.query(Song).filter(Song.title.ilike(f"%{title}%"))
```

**Case-Insensitive**: Uses SQLAlchemy's `ilike()` method for case-insensitive matching
**Partial Matching**: Finds "Love Song" when searching "love"

### File Upload Processing

**Multipart Handling**:
```python
@app.post("/api/songs/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")
    content = await file.read()
    data = json.loads(content.decode())
    message = normalize_and_insert_data(data, db)
    return {"message": message}
```

**Content Validation**:
- Filename extension check (.json required)
- JSON parsing with error handling
- Format detection (column vs row-oriented)
- Data normalization
<<<<<<< HEAD
- Database insertion/update
=======
- Database insertion

>>>>>>> 228e4e206efd091b335cb050fdd2345d72540843

## Database Design

### Song Model Schema

```sql
CREATE TABLE songs (
    pk INTEGER PRIMARY KEY,
    id VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    song_class VARCHAR,
    rating INTEGER DEFAULT 0,
    danceability FLOAT DEFAULT 0.0,
    energy FLOAT DEFAULT 0.0,
    -- ... other analytics columns
);
```

### Indexing Strategy

**Current Indexes** (defined in `app/models/song.py`):
- Primary key on `pk` (automatic with `primary_key=True`)
- Unique index on `id` (`unique=True, index=True`)
- Index on `title` (`index=True` for search optimization)

**Performance Considerations**:
- SQLite automatically indexes primary keys
- Additional indexes added as needed for query patterns

## Security Considerations

### Input Sanitization

**SQL Injection Prevention**:
- SQLAlchemy parameterized queries
- No raw SQL string concatenation

**File Upload Security**:
- Filename extension validation (must be .json)
- JSON parsing with error handling
- No execution of uploaded content
<<<<<<< HEAD
=======

### CORS Configuration

**Development Settings**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Monitoring & Maintenance

**Health Checks**:
- `/health` endpoint for load balancers
- Database connectivity verification

**Backup Strategy**:
- SQLite file can be copied for backup
- Automated backup scripts for production
>>>>>>> 228e4e206efd091b335cb050fdd2345d72540843
