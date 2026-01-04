# Technical Documentation

This document provides comprehensive technical details about the Playlist Management Application, including implementation decisions, architecture choices, and development guidelines.

## 🏗️ Architecture Overview

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

## ⚙️ Configuration & Environment

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./playlist.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Development
RELOAD=True
LOG_LEVEL=INFO
```

### Configuration Management

**Database Configuration** (`app/core/database.py`):
- SQLAlchemy engine with connection pooling
- Session management with proper cleanup
- Automatic table creation on startup

**CORS Configuration** (`app/main.py`):
- Configured for local development
- Allows all origins, methods, and headers
- Production should restrict to specific domains

## 🔄 Development Workflow

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
├── main.py           # Entry point, routes, app config
├── core/             # Infrastructure (database, config)
├── models/           # Data models (SQLAlchemy)
├── routers/          # Route handlers (FastAPI)
├── services/         # Business logic
├── schemas/          # Pydantic models (validation)
└── utils/            # Utilities (data processing)
```

**Dependency Injection**:
- FastAPI's `Depends()` for database sessions
- Automatic session cleanup
- Test-friendly with overrides

## 📊 Data Processing & Validation

### JSON Format Detection

**Column-Oriented Detection**:
```python
is_column_oriented = isinstance(data, dict) and all(isinstance(v, dict) for v in data.values())
```

**Row-Oriented Detection**:
```python
is_row_oriented = isinstance(data, list) and all(isinstance(item, dict) for item in data)
```

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

## 🧪 Testing Strategy

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

## 📝 Logging & Monitoring

### Logging Configuration

**Setup** (`app/main.py`):
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**Log Levels**:
- **INFO**: Normal operations (startup, successful uploads)
- **WARNING**: Non-critical issues (missing fields)
- **ERROR**: Failures (database errors, invalid requests)

### Health Check Endpoint

**GET /health**:
```json
{"status": "ok"}
```

**Usage**: Load balancer health checks, monitoring systems

## 🚨 Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (validation errors, invalid JSON)
- **404**: Not Found (song doesn't exist)
- **500**: Internal Server Error (database failures, unexpected errors)

### Validation Errors

**Pydantic Models**:
```python
class RatingRequest(BaseModel):
    rating: int = Field(ge=0, le=5)
```

**Custom Validation**:
- Rating range checking
- File format validation
- Required field presence

### Exception Handling

**Global Exception Handler** (FastAPI automatic)
- Converts exceptions to appropriate HTTP responses
- Logs errors for debugging
- Returns user-friendly error messages

## 🔍 API Implementation Details

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

**ILIKE Query**:
```sql
SELECT * FROM songs WHERE title ILIKE '%love%'
```

**Case-Insensitive**: Works with SQLite's ILIKE extension
**Partial Matching**: Finds "Love Song" when searching "love"

### File Upload Processing

**Multipart Handling**:
```python
@app.post("/api/songs/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    data = json.loads(content.decode())
    # Process data...
```

**Content Validation**:
- JSON parsing
- Format detection
- Data normalization
- Database insertion

## 🎨 Frontend Architecture

### State Management

**Client-Side State**:
- Current page, search query, sort order
- Cached data for current view
- Chart data synchronization

**URL Synchronization**:
```javascript
// Update URL with current state
window.history.pushState(null, null, `?page=${page}&search=${query}`);
```

### Chart Integration

**Dynamic Updates**:
```javascript
function updateCharts(data) {
    // Update all charts with new data
    danceabilityChart.data.datasets[0].data = data.map(song => song.danceability);
    danceabilityChart.update();
}
```

**Chart.js Configuration**:
- Scatter plots for correlations
- Histograms for distributions
- Responsive design
- Interactive tooltips

## 🗄️ Database Design

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

**Current Indexes**:
- Primary key on `pk`
- Unique index on `id`
- Index on `title` (for search)

**Performance Considerations**:
- SQLite automatically indexes primary keys
- Additional indexes added as needed for query patterns

## 🔒 Security Considerations

### Input Sanitization

**SQL Injection Prevention**:
- SQLAlchemy parameterized queries
- No raw SQL string concatenation

**File Upload Security**:
- Content-Type validation
- JSON parsing with error handling
- No execution of uploaded content

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

**Production**: Restrict origins to specific domains

## 📈 Performance Optimization

### Database Optimizations

**Connection Pooling**:
- SQLAlchemy handles connection reuse
- Automatic cleanup of connections

**Query Optimization**:
- Selective field loading
- Pagination prevents large result sets
- Indexed queries for search

### Frontend Optimizations

**Efficient DOM Updates**:
- Minimal reflows during table updates
- Debounced search input
- Lazy chart rendering

**Memory Management**:
- Cleanup of unused chart instances
- Efficient data structures for large datasets

## 🚀 Deployment & Production

### Production Configuration

**Environment Variables**:
```bash
DATABASE_URL=sqlite:///./prod_playlist.db
DEBUG=False
LOG_LEVEL=WARNING
```

**Production Server**:
```bash
# Use production ASGI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Monitoring & Maintenance

**Health Checks**:
- `/health` endpoint for load balancers
- Database connectivity verification

**Backup Strategy**:
- SQLite file can be copied for backup
- Automated backup scripts for production

## 🔮 Future Enhancements

### Planned Features

**Backend**:
- User authentication and authorization
- Advanced search filters (genre, artist, year)
- Bulk operations (batch rating, export)
- API versioning
- Rate limiting

**Frontend**:
- Progressive Web App (PWA) features
- Keyboard shortcuts
- Advanced filtering UI
- Data import/export wizards

**Infrastructure**:
- Database migration system
- Caching layer (Redis)
- Background job processing
- API documentation enhancements

### Scalability Considerations

**Database Scaling**:
- Migrate to PostgreSQL for production
- Add read replicas for heavy read loads
- Implement database sharding if needed

**API Scaling**:
- Implement caching for frequent queries
- Add request/response compression
- Consider GraphQL for complex queries

**Frontend Scaling**:
- Implement virtual scrolling for large tables
- Add pagination for chart data
- Progressive loading of features