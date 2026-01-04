# Playlist Management Application

A full-stack web application for managing and analyzing song playlists, built with FastAPI and vanilla JavaScript.

## 🎯 Overview

This application solves the challenge of processing and managing song playlist data in multiple JSON formats, providing a complete web interface for data analysis and management.

### Key Features
- **Dual Format Support**: Automatically handles both column-oriented and row-oriented JSON formats
- **Interactive Dashboard**: Search, sort, paginate, and visualize song data
- **Data Normalization**: Transforms complex JSON structures into relational database format
- **Rating System**: User-friendly star rating for songs
- **Export Functionality**: Download data as CSV
- **Comprehensive Testing**: Unit tests, integration tests, and manual UI testing

## 🚀 Quick Start

Get up and running in minutes:

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd playlist-management-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Development Workflow

```bash
# Start development server
uvicorn app.main:app --reload

# Open in browser: http://localhost:8000
```

### 3. Load Sample Data

1. Open `http://localhost:8000` in your browser
2. Click "Upload JSON" and select a file from `sample_data/`
3. Try both formats:
   - `Playlist.json` (column-oriented, 100 songs)
   - `sample_column_data.json` (row-oriented, 3 songs)

## 📊 Data Processing

The application handles JSON files in two formats:

### Column-Oriented Format (Playlist.json)
```json
{
  "id": {"0": "song1", "1": "song2"},
  "title": {"0": "Song One", "1": "Song Two"},
  "danceability": {"0": 0.8, "1": 0.7}
}
```

### Row-Oriented Format (batch_*.json)
```json
[
  {"id": "song1", "title": "Song One", "danceability": 0.8},
  {"id": "song2", "title": "Song Two", "danceability": 0.7}
]
```

Both formats are automatically detected and normalized into a SQLite database.

## 🏗️ Project Structure

```
playlist_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & API endpoints
│   ├── core/
│   │   └── database.py      # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── song.py          # SQLAlchemy Song model
│   ├── routers/
│   │   └── songs.py         # API route handlers
│   ├── schemas/
│   ├── services/
│   │   └── song_service.py  # Business logic
│   └── utils/
│       └── data_utils.py    # Data normalization utilities
├── static/
│   ├── index.html           # Frontend UI
│   ├── script.js            # Frontend logic
│   └── style.css            # Frontend styles
├── sample_data/             # Sample JSON files
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   └── integ/               # Integration tests
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── documentation.md        # Detailed technical docs
```

## 🛠️ Development Workflow

### Local Development

1. **Setup**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Start Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Open in Browser**:
   - Navigate to `http://localhost:8000`
   - Upload sample data and start exploring

### Testing
See the comprehensive [Testing](#testing) section below for all testing approaches.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/songs` | Get paginated songs with sorting |
| GET | `/api/songs/search?title=query` | Search songs by title |
| POST | `/api/songs/upload` | Upload JSON file |
| POST | `/api/songs/{id}/rate` | Rate a song (0-5 stars) |
| DELETE | `/api/songs/all` | Clear all songs |
| GET | `/api/songs/all` | Export all songs as JSON |
| GET | `/health` | Health check |

### Example API Usage

```bash
# Get first page of songs
curl "http://localhost:8000/api/songs?page=1&limit=10"

# Search for songs
curl "http://localhost:8000/api/songs/search?title=love"

# Rate a song
curl -X POST "http://localhost:8000/api/songs/song_id/rate" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5}'

# Upload data
curl -X POST -F "file=@sample_data/batch_1.json" \
  http://localhost:8000/api/songs/upload
```

## 🧪 Testing

The application includes comprehensive testing at multiple levels:

### Unit Tests (Fast, Isolated)
Run without starting the server - test individual components:

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage report
pytest --cov=app tests/unit/ --cov-report=term-missing

# Run specific test
pytest tests/unit/test_main.py::test_upload_row_oriented -v
```

**Coverage**: 81% - tests API endpoints, data processing, validation, and error handling.

### Integration Tests (Full System)
Test complete workflows with live server:

```bash
# Start server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3

# Run integration tests
python tests/integ/verify_upload.py    # Test file upload & normalization
python tests/integ/verify_search.py    # Test search functionality
python tests/integ/verify_db.py        # Test rating persistence
```

### Manual UI Testing
Interactive testing through the web interface:

1. **Start the server**: `uvicorn app.main:app --reload`
2. **Open browser**: `http://localhost:8000`
3. **Test scenarios**:
   - **Upload**: Try both `Playlist.json` (100 songs) and `batch_1.json` (10 songs)
   - **Search**: Enter queries, verify results and chart updates
   - **Pagination**: Navigate through pages
   - **Sorting**: Click column headers
   - **Rating**: Rate songs with stars
   - **Export**: Download CSV
   - **Clear Data**: Test the clear functionality

### API Testing with Swagger
Interactive API documentation at `http://localhost:8000/docs`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs` - Try endpoints directly in browser
- **ReDoc**: `http://localhost:8000/redoc` - Clean API reference

### Authentication & Headers
All endpoints are public. Use standard HTTP methods and JSON payloads.

### Error Handling
- **400**: Bad Request (invalid data, validation errors)
- **404**: Not Found (song doesn't exist)
- **500**: Internal Server Error

## Deployment

Currently the app is deployed to https://vivpro-song-app.fastapicloud.dev/ using fastapi deploy.

## � Troubleshooting

### Common Issues

**Server won't start**:
- Check if port 8000 is available: `lsof -i :8000`
- If port is in use, kill the process: `kill -9 $(lsof -t -i :8000)`
- Ensure virtual environment is activated
- Verify all dependencies are installed
- If getting bind errors, try: `uvicorn app.main:app --host 127.0.0.1 --port 8000`

**Database issues**:
- Delete `playlist.db` to start fresh
- Check file permissions
- Ensure SQLite is available

**Upload fails**:
- Check file format (must be valid JSON)
- Verify file size limits
- Check server logs for detailed errors

**Tests fail**:
- Ensure dependencies are installed: `pip install -r requirements.txt`
- For integration tests, ensure server is running on port 8000
- Check database is accessible


## 📖 Additional Resources

- **Technical Documentation**: See [documentation.md](documentation.md) for detailed implementation notes
- **API Schema**: Visit `/docs` when server is running
- **Sample Data**: Check `sample_data/` directory for test files
