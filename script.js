// Replace the form submission handler in the frontend with this:
form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const entryText = document.getElementById('journal-entry').value;
    if (!entryText) return;
    
    // Show loading
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    
    // Send to backend
    fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ journal_entry: entryText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show results
            emotionLabel.textContent = data.emotion;
            emotionScore.textContent = (data.score * 100).toFixed(2) + '%';
            resultDiv.classList.remove('hidden');
            
            // Create emotion chart
            createEmotionChart(data.emotion, data.score);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    })
    .finally(() => {
        // Hide loading
        loadingDiv.classList.add('hidden');
    });
});

// Replace the loadHistory function with this:
function loadHistory() {
    fetch('http://localhost:5000/api/entries')
        .then(response => response.json())
        .then(entries => {
            const entriesList = document.getElementById('entries-list');
            
            if (entries.length === 0) {
                entriesList.innerHTML = '<p>No entries yet. <a href="#" id="start-journal">Write your first journal entry</a>.</p>';
                if (document.getElementById('start-journal')) {
                    document.getElementById('start-journal').addEventListener('click', function(e) {
                        e.preventDefault();
                        navNew.click();
                    });
                }
                return;
            }
            
            // Clear previous entries
            entriesList.innerHTML = '';
            
            // Add entries to the list
            entries.forEach(entry => {
                const entryEl = document.createElement('div');
                entryEl.className = 'journal-entry';
                
                const date = new Date(entry.created_at);
                entryEl.innerHTML = `
                    <div class="entry-date">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</div>
                    <div class="entry-text">${entry.entry_text}</div>
                    <div class="entry-sentiment">
                        Emotion: <span class="emotion-tag">${entry.sentiment_label}</span> (${(entry.sentiment_score * 100).toFixed(2)}%)
                    </div>
                `;
                
                entriesList.appendChild(entryEl);
            });
            
            // Load chart data
            return fetch('http://localhost:5000/api/entries/chart');
        })
        .then(response => response.json())
        .then(chartData => {
            createMoodTrendChart(chartData);
        })
        .catch(error => {
            console.error('Error loading history:', error);
        });
}