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

// Perform RAG search and summarization
async function performQuery(query) {
    const searchingState = document.getElementById('searching-state');
    const resultsContainer = document.getElementById('results-container');
    const errorDisplay = document.getElementById('error-display');
    const summaryPreview = document.getElementById('summary-preview');
    const summaryFull = document.getElementById('summary-full');
    const summaryMetadata = document.getElementById('summary-metadata');
    const searchResultsSection = document.getElementById('search-results-section');
    const searchResults = document.getElementById('search-results');

    // Reset state
    searchingState.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    errorDisplay.classList.add('hidden');
    summaryPreview.textContent = '';
    summaryFull.textContent = '';
    summaryFull.classList.add('hidden');
    summaryMetadata.innerHTML = '';
    summaryMetadata.classList.add('hidden');
    searchResults.innerHTML = '';
    searchResultsSection.classList.add('hidden');

    try {
        // Call RAG summarize endpoint
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 5
            }),
        });

        if (!response.ok) {
            throw new Error(`Request failed: ${response.statusText}`);
        }

        // Hide searching state, show results
        searchingState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';
        let metadata = null;
        let fullText = '';

        // Start with streaming indicator
        summaryFull.classList.remove('hidden');
        summaryFull.classList.add('summary-streaming');

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                summaryFull.classList.remove('summary-streaming');

                // Set preview to first 3 lines
                const lines = fullText.split('\n').slice(0, 3);
                summaryPreview.textContent = lines.join('\n');

                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') {
                        summaryFull.classList.remove('summary-streaming');
                        continue;
                    }

                    try {
                        const json = JSON.parse(data);

                        // Handle metadata
                        if (json.metadata) {
                            metadata = json.metadata;

                            // Show metadata immediately
                            const speedBadge = getSpeedBadge(metadata.search_time_ms);
                            const cacheIndicator = getCacheIndicator(metadata.cache_hit);

                            summaryMetadata.innerHTML = `
                                <span class="meta-item">Model: ${metadata.model}</span>
                                <span class="meta-item">Search: ${metadata.search_time_ms}ms ${speedBadge}</span>
                                ${cacheIndicator}
                                <span class="meta-item">Results: ${metadata.results_found}</span>
                                <span class="meta-item">First token: ${metadata.time_to_first_token_ms}ms</span>
                            `;
                            summaryMetadata.classList.remove('hidden');
                        }
                        // Handle completion metadata
                        else if (json.done) {
                            summaryFull.classList.remove('summary-streaming');

                            // Update metadata with final stats
                            const speedBadge = getSpeedBadge(metadata?.search_time_ms || 0);
                            const cacheIndicator = getCacheIndicator(metadata?.cache_hit);

                            summaryMetadata.innerHTML = `
                                <span class="meta-item">Model: ${metadata?.model || 'unknown'}</span>
                                <span class="meta-item">Search: ${metadata?.search_time_ms || 0}ms ${speedBadge}</span>
                                ${cacheIndicator}
                                <span class="meta-item">Results: ${metadata?.results_found || 0}</span>
                                <span class="meta-item">First token: ${metadata?.time_to_first_token_ms || 0}ms</span>
                                <span class="meta-item">Last token: ${json.time_to_last_token_ms || 0}ms</span>
                                <span class="meta-item">Total: ${json.total_time_ms}ms</span>
                                <span class="meta-item">Tokens: ${json.token_count}</span>
                            `;
                        }
                        // Handle text content
                        else if (json.text) {
                            fullText += json.text;
                            summaryFull.textContent = fullText;
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE data:', e);
                    }
                }
            }
        }

        // Optionally fetch and display source documents
        // This would require a separate /search call or including results in /summarize response
        // For now, we'll fetch search results separately
        await fetchSearchResults(query);

    } catch (error) {
        searchingState.classList.add('hidden');
        errorDisplay.textContent = `Error: ${error.message}`;
        errorDisplay.classList.remove('hidden');
    }
}

// Fetch search results to show as sources
async function fetchSearchResults(query) {
    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}&top_k=5`);

        if (!response.ok) {
            console.error('Failed to fetch search results:', response.statusText);
            return;
        }

        const data = await response.json();
        const searchResultsSection = document.getElementById('search-results-section');
        const searchResults = document.getElementById('search-results');

        if (!data.results || data.results.length === 0) {
            return;
        }

        // Show search results section
        searchResultsSection.classList.remove('hidden');

        // Display results
        data.results.forEach((result, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            const title = document.createElement('div');
            title.className = 'result-title';
            title.textContent = result.title || `Source ${index + 1}`;

            const content = document.createElement('div');
            content.className = 'result-content';
            content.textContent = result.content || result.snippet || '';

            const meta = document.createElement('div');
            meta.className = 'result-meta';

            const scoreItem = document.createElement('span');
            scoreItem.className = 'meta-item';
            scoreItem.textContent = `Relevance: ${(result.score * 100).toFixed(1)}%`;
            meta.appendChild(scoreItem);

            resultItem.appendChild(title);
            resultItem.appendChild(content);
            resultItem.appendChild(meta);
            searchResults.appendChild(resultItem);
        });

    } catch (error) {
        console.error('Error fetching search results:', error);
    }
}

// Toggle summary expansion
function toggleSummary() {
    const summaryPreview = document.getElementById('summary-preview');
    const summaryFull = document.getElementById('summary-full');
    const expandButton = document.getElementById('expand-button');
    const expandText = expandButton.querySelector('.expand-text');

    if (summaryFull.classList.contains('hidden')) {
        // Expand
        summaryPreview.classList.add('hidden');
        summaryFull.classList.remove('hidden');
        expandText.textContent = 'Collapse Summary';
        expandButton.classList.add('expanded');
    } else {
        // Collapse
        summaryFull.classList.add('hidden');
        summaryPreview.classList.remove('hidden');
        expandText.textContent = 'Expand Summary';
        expandButton.classList.remove('expanded');
    }
}

// Initialize event listeners
function initializeEventListeners() {
    // Search button
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            performQuery(query);
        }
    });

    // Enter key in search input
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                performQuery(query);
            }
        }
    });

    // Example query chips
    const exampleChips = document.querySelectorAll('.example-chip');
    exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.textContent;
            searchInput.value = query;
            performQuery(query);
        });
    });

    // Summary expand/collapse
    const expandButton = document.getElementById('expand-button');
    const summaryHeader = document.getElementById('summary-header');

    expandButton.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleSummary();
    });

    summaryHeader.addEventListener('click', () => {
        toggleSummary();
    });
}

// Get speed badge based on search time
function getSpeedBadge(searchTimeMs) {
    if (searchTimeMs < 50) {
        return '<span class="speed-badge badge-lightning">⚡ Lightning Fast</span>';
    } else if (searchTimeMs < 100) {
        return '<span class="speed-badge badge-super">🚀 Super Quick</span>';
    } else if (searchTimeMs < 120) {
        return '<span class="speed-badge badge-fast">✓ Fast</span>';
    }
    return '';
}

// Get cache indicator
function getCacheIndicator(cacheHit) {
    if (cacheHit === true) {
        return '<span class="cache-indicator cache-hit">⚡ Cache Hit</span>';
    } else if (cacheHit === false) {
        return '<span class="cache-indicator cache-miss">🔍 Cache Miss</span>';
    }
    return '';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    initializeEventListeners();
});
