# Sample Data

This folder contains sample data files demonstrating different JSON formats supported by the playlist application.

## Folder Structure

### `column_based/`
Contains JSON files in **column-oriented format**. Each field is a key with an object containing indices as keys and values as values.

Example:
```json
{
  "id": {"0": "song1", "1": "song2"},
  "title": {"0": "Song One", "1": "Song Two"},
  "danceability": {"0": 0.8, "1": 0.6}
}
```

- `Playlist.json` - Full dataset with 100 songs in column format
- `sample_column_data.json` - Small sample with 3 songs

### `row_based/`
Contains JSON files in **row-oriented format**. Each song is an object in an array.

Example:
```json
[
  {
    "id": "song1",
    "title": "Song One",
    "danceability": 0.8
  },
  {
    "id": "song2",
    "title": "Song Two",
    "danceability": 0.6
  }
]
```

- `batch_*.json` - Generated test data files (10 files)
- `sample_row_data.json` - Small sample with 3 songs

## Supported Fields

Both formats support all audio analysis features:
- Basic: id, title, song_class, rating
- Audio features: danceability, energy, key, loudness, mode, acousticness, instrumentalness, liveness, valence, tempo, duration_ms
- Structural: time_signature, num_bars, num_sections, num_segments

## Usage

Upload these files through the web interface or use them for testing the data import functionality.