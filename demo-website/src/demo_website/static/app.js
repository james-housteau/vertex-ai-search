// Configuration
let API_URL = 'https://search-api-546806894637.us-central1.run.app';

// Fetch configuration from backend
async function loadConfig() {
    try {
        const response = await fetch('/config');
        const config = await response.json();
        API_URL = config.api_url;
    } catch (error) {
        console.error('Failed to load config, using default:', error);
    }
}

// Tab switching
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;

            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Search functionality
async function performSearch(query) {
    const resultsDiv = document.getElementById('search-results');
    const loadingDiv = document.getElementById('search-loading');
    const errorDiv = document.getElementById('search-error');

    // Reset state
    resultsDiv.innerHTML = '';
    errorDiv.classList.add('hidden');
    loadingDiv.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}`);

        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }

        const data = await response.json();
        loadingDiv.classList.add('hidden');

        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = '<p>No results found.</p>';
            return;
        }

        // Display results
        data.results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            const title = document.createElement('div');
            title.className = 'result-title';
            title.textContent = result.title || 'Untitled';

            const content = document.createElement('div');
            content.className = 'result-content';
            content.textContent = result.content || result.snippet || '';

            const meta = document.createElement('div');
            meta.className = 'result-meta';

            if (data.latency_ms !== undefined) {
                const latencyItem = document.createElement('span');
                latencyItem.className = 'meta-item';
                latencyItem.textContent = `Latency: ${data.latency_ms}ms`;
                meta.appendChild(latencyItem);
            }

            if (data.cache_hit !== undefined) {
                const cacheItem = document.createElement('span');
                cacheItem.className = `meta-item ${data.cache_hit ? 'cache-hit' : 'cache-miss'}`;
                cacheItem.textContent = data.cache_hit ? 'Cache: HIT' : 'Cache: MISS';
                meta.appendChild(cacheItem);
            }

            resultItem.appendChild(title);
            resultItem.appendChild(content);
            resultItem.appendChild(meta);
            resultsDiv.appendChild(resultItem);
        });

    } catch (error) {
        loadingDiv.classList.add('hidden');
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.classList.remove('hidden');
    }
}

// Summary functionality with SSE streaming
async function performSummarize(content) {
    const resultsDiv = document.getElementById('summary-results');
    const loadingDiv = document.getElementById('summary-loading');
    const errorDiv = document.getElementById('summary-error');

    // Reset state
    resultsDiv.innerHTML = '';
    errorDiv.classList.add('hidden');
    loadingDiv.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content }),
        });

        if (!response.ok) {
            throw new Error(`Summarize failed: ${response.statusText}`);
        }

        loadingDiv.classList.add('hidden');

        // Create summary container
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'summary-content summary-streaming';
        resultsDiv.appendChild(summaryDiv);

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                summaryDiv.classList.remove('summary-streaming');
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') {
                        summaryDiv.classList.remove('summary-streaming');
                        continue;
                    }

                    try {
                        const json = JSON.parse(data);
                        if (json.text) {
                            summaryDiv.textContent += json.text;
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE data:', e);
                    }
                }
            }
        }

    } catch (error) {
        loadingDiv.classList.add('hidden');
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.classList.remove('hidden');
    }
}

// Event listeners
function initializeEventListeners() {
    // Search
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });

    // Summarize
    const summaryInput = document.getElementById('summary-input');
    const summaryButton = document.getElementById('summary-button');

    summaryButton.addEventListener('click', () => {
        const content = summaryInput.value.trim();
        if (content) {
            performSummarize(content);
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    initializeTabs();
    initializeEventListeners();
});
