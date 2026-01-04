const API_BASE = '/api/songs';

let state = {
    page: 1,
    limit: 10,
    sortBy: null,
    order: 'asc',
    searchQuery: '',
    total: 0
};

// Charts
let chartInstances = {
    scatter: null,
    histogram: null,
    acoustic: null,
    tempo: null
};

document.addEventListener('DOMContentLoaded', () => {
    fetchSongs();
    initCharts();
    setupEventListeners();
});

function setupEventListeners() {
    // Search
    document.getElementById('searchBtn').addEventListener('click', handleSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    document.getElementById('resetBtn').addEventListener('click', resetSearch);

    // Download
    document.getElementById('downloadBtn').addEventListener('click', downloadCSV);

    // Upload
    document.getElementById('confirmUploadBtn').addEventListener('click', handleUpload);

    // Clear All
    document.getElementById('clearAllBtn').addEventListener('click', handleClearAll);

    // Sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (state.sortBy === column) {
                state.order = state.order === 'asc' ? 'desc' : 'asc';
            } else {
                state.sortBy = column;
                state.order = 'asc';
            }
            fetchSongs();
            updateSortIcons();
        });
    });
}

function updateSortIcons() {
    document.querySelectorAll('th[data-sort] i').forEach(icon => {
        icon.className = 'bi bi-arrow-down-up small text-muted';
    });
    if (state.sortBy) {
        const th = document.querySelector(`th[data-sort="${state.sortBy}"]`);
        if (th) {
            const icon = th.querySelector('i');
            icon.className = state.order === 'asc' ? 'bi bi-arrow-up-short' : 'bi bi-arrow-down-short';
            icon.classList.remove('text-muted');
        }
    }
}

async function fetchSongs() {
    let url = `${API_BASE}?page=${state.page}&limit=${state.limit}`;
    if (state.sortBy) {
        url += `&sort_by=${state.sortBy}&order=${state.order}`;
    }

    // If search query exists, we use the search endpoint
    // Note: Search endpoint in backend doesn't support pagination/sorting in the current implementation
    // But the requirement says "Get Song" button... implies fetching specific song.
    // However, for the main table, we usually want to search/filter.
    // The backend `search_songs` returns a list.

    if (state.searchQuery) {
        url = `${API_BASE}/search?title=${encodeURIComponent(state.searchQuery)}&page=${state.page}&limit=${state.limit}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.items) {
            state.total = data.total;
            renderTable(data.items);
            renderPagination(data.total, data.page, data.size);

            const start = (data.page - 1) * data.size + 1;
            const end = Math.min(start + data.size - 1, data.total);
            document.getElementById('pageInfo').textContent = `Showing ${start}-${end} of ${data.total}`;

            // Update charts with current results
            await updateCharts();
        } else if (Array.isArray(data)) {
            // Fallback if backend returns direct list (legacy)
            state.total = data.length;
            renderTable(data);
            renderPagination(data.length, 1, data.length);
            document.getElementById('pageInfo').textContent = `Showing ${data.length} results`;
        }
    } catch (error) {
        console.error('Error fetching songs:', error);
        alert('Failed to load data');
    }
}

function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (query) {
        state.searchQuery = query;
        state.page = 1; // Reset to first page
        fetchSongs();
    }
}

function resetSearch() {
    document.getElementById('searchInput').value = '';
    state.searchQuery = '';
    state.page = 1;
    fetchSongs();
}

function renderTable(items) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="19" class="text-center">No songs found</td></tr>';
        return;
    }

    items.forEach(song => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${song.id}</td>
            <td>${song.title}</td>
            <td>${song.song_class}</td>
            <td>${song.danceability}</td>
            <td>${song.energy}</td>
            <td>${song.key}</td>
            <td>${song.loudness}</td>
            <td>${song.mode}</td>
            <td>${song.acousticness}</td>
            <td>${song.instrumentalness}</td>
            <td>${song.liveness}</td>
            <td>${song.valence}</td>
            <td>${song.tempo}</td>
            <td>${song.duration_ms}</td>
            <td>${song.time_signature}</td>
            <td>${song.num_bars}</td>
            <td>${song.num_sections}</td>
            <td>${song.num_segments}</td>
            <td>${renderStars(song.id, song.rating)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderStars(id, rating) {
    let starsHtml = '<div class="star-rating">';
    for (let i = 1; i <= 5; i++) {
        const filled = i <= rating ? '-fill' : '';
        const color = i <= rating ? 'text-warning' : 'text-muted';
        starsHtml += `<i class="bi bi-star${filled} ${color}" onclick="rateSong('${id}', ${i})"></i>`;
    }
    starsHtml += '</div>';
    return starsHtml;
}

window.rateSong = async function (id, rating) {
    try {
        const response = await fetch(`${API_BASE}/${id}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rating })
        });

        if (response.ok) {
            // Refresh table to show new rating
            // We could just update the DOM but fetching ensures consistency
            fetchSongs();
        } else {
            alert('Failed to update rating');
        }
    } catch (error) {
        console.error('Error rating song:', error);
    }
};

function renderPagination(total, currentPage, limit) {
    const totalPages = Math.ceil(total / limit);
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    // Prev
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#">Previous</a>`;
    prevLi.onclick = (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            state.page = currentPage - 1;
            fetchSongs();
        }
    };
    pagination.appendChild(prevLi);

    // Pages
    // Show limited pages if too many
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        li.onclick = (e) => {
            e.preventDefault();
            state.page = i;
            fetchSongs();
        };
        pagination.appendChild(li);
    }

    // Next
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#">Next</a>`;
    nextLi.onclick = (e) => {
        e.preventDefault();
        if (currentPage < totalPages) {
            state.page = currentPage + 1;
            fetchSongs();
        }
    };
    pagination.appendChild(nextLi);
}

function downloadCSV() {
    // Build URL based on current search/filter state
    let url;
    if (state.searchQuery) {
        // If searching, get all search results (no pagination)
        url = `${API_BASE}/search?title=${encodeURIComponent(state.searchQuery)}&page=1&limit=10000`;
    } else {
        // If not searching, get all songs (no pagination)
        url = `${API_BASE}?page=1&limit=10000`;
        if (state.sortBy) {
            url += `&sort_by=${state.sortBy}&order=${state.order}`;
        }
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (!data.items || !data.items.length) {
                alert('No data to download');
                return;
            }

            const headers = Object.keys(data.items[0]).join(',');
            const rows = data.items.map(row => Object.values(row).map(value =>
                // Escape commas and quotes in CSV values
                typeof value === 'string' && (value.includes(',') || value.includes('"'))
                    ? `"${value.replace(/"/g, '""')}"`
                    : value
            ).join(','));
            const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join('\n');
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", state.searchQuery ? `search_results_${state.searchQuery}.csv` : "playlist_data.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch(error => {
            console.error('Error downloading CSV:', error);
            alert('Error downloading CSV');
        });
}



async function handleUpload() {
    const fileInput = document.getElementById('jsonFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const btn = document.getElementById('confirmUploadBtn');
        const originalText = btn.textContent;
        btn.textContent = 'Uploading...';
        btn.disabled = true;

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
            modal.hide();
            // Reset input
            fileInput.value = '';
            // Refresh list
            fetchSongs();
        } else {
            alert(`Upload failed: ${result.detail || 'Unknown error'}`);
        }

        btn.textContent = originalText;
        btn.disabled = false;

    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file');
        document.getElementById('confirmUploadBtn').disabled = false;
        document.getElementById('confirmUploadBtn').textContent = 'Upload';
    }
}

async function handleClearAll() {
    const button = document.getElementById('clearAllBtn');
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-trash"></i> Deleting...';

    if (!confirm('Are you sure you want to delete ALL songs from the database? This action cannot be undone!')) {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-trash"></i> Clear All';
        return;
    }

    try {
        const response = await fetch('/api/songs/all', {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            // Refresh the page to show empty state
            state.page = 1;
            state.searchQuery = '';
            fetchSongs();
        } else {
            alert(`Error: ${result.detail || 'Failed to delete songs'}`);
        }
    } catch (error) {
        console.error('Error deleting songs:', error);
        alert('Failed to delete songs');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-trash"></i> Clear All';
    }
}


async function initCharts() {
    // Initial load with all songs
    await updateCharts();
}

async function updateCharts() {
    try {
        // Fetch data based on current search/filter state
        // Note: Backend limits to 10000 items max, we use 1000 for analytics to avoid performance issues
        let url = state.searchQuery
            ? `${API_BASE}/search?title=${encodeURIComponent(state.searchQuery)}&page=1&limit=1000`
            : `${API_BASE}?page=1&limit=1000`;

        const response = await fetch(url);
        const data = await response.json();

        // Handle both paginated and direct array responses
        const chartData = data.items || data;

        // Destroy existing charts before creating new ones
        if (chartInstances.scatter) chartInstances.scatter.destroy();
        if (chartInstances.histogram) chartInstances.histogram.destroy();
        if (chartInstances.acoustic) chartInstances.acoustic.destroy();
        if (chartInstances.tempo) chartInstances.tempo.destroy();

        renderScatterChart(chartData);
        renderHistogramChart(chartData);
        renderAcousticChart(chartData);
        renderTempoChart(chartData);
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

function renderScatterChart(data) {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    const points = data.map(item => ({
        x: item.energy,
        y: item.danceability
    }));

    chartInstances.scatter = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Danceability vs Energy',
                data: points,
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Energy' } },
                y: { title: { display: true, text: 'Danceability' } }
            }
        }
    });
}

function renderHistogramChart(data) {
    const ctx = document.getElementById('histogramChart').getContext('2d');
    const durations = data.map(d => d.duration_ms / 1000);

    const bins = [0, 120, 180, 240, 300, 360];
    const counts = new Array(bins.length - 1).fill(0);

    durations.forEach(d => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (d >= bins[i] && d < bins[i + 1]) {
                counts[i]++;
                break;
            }
        }
    });

    chartInstances.histogram = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bins.slice(0, -1).map((b, i) => `${b}-${bins[i + 1]}s`),
            datasets: [{
                label: 'Song Duration Distribution',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Count' } },
                x: { title: { display: true, text: 'Duration (s)' } }
            }
        }
    });
}

function renderAcousticChart(data) {
    const ctx = document.getElementById('acousticChart').getContext('2d');
    // Limit to first 20 for readability
    const subset = data.slice(0, 20);

    chartInstances.acoustic = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: subset.map(d => d.title.substring(0, 10) + '...'),
            datasets: [{
                label: 'Acousticness',
                data: subset.map(d => d.acousticness),
                backgroundColor: 'rgba(255, 206, 86, 0.6)'
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderTempoChart(data) {
    const ctx = document.getElementById('tempoChart').getContext('2d');
    const subset = data.slice(0, 20);

    chartInstances.tempo = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: subset.map(d => d.title.substring(0, 10) + '...'),
            datasets: [{
                label: 'Tempo',
                data: subset.map(d => d.tempo),
                backgroundColor: 'rgba(153, 102, 255, 0.6)'
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

