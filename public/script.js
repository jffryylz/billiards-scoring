let matchState = {
    team_a_score: 0,
    team_b_score: 0,
    team_a_selected: [],
    team_b_selected: [],
    team_a_history: [],
    team_b_history: [],
    winner: null
};

const API_BASE = window.location.origin + '/api';

// Initialize the app
async function init() {
    await loadMatchState();
    renderUI();
}

// Load match state from API
async function loadMatchState() {
    try {
        const response = await fetch(`${API_BASE}/match`);
        if (response.ok) {
            matchState = await response.json();
        } else {
            console.error('Failed to load match state');
        }
    } catch (error) {
        console.error('Error loading match state:', error);
    }
}

// Save match state to API
async function saveMatchState() {
    try {
        // The API automatically saves the state when scoring/undoing
        // This function can be used if we need manual saves
        await loadMatchState(); // Reload to get latest state
        renderUI();
    } catch (error) {
        console.error('Error saving match state:', error);
    }
}

// Render the UI based on current state
function renderUI() {
    // Update scores
    document.getElementById('score-a').textContent = matchState.team_a_score;
    document.getElementById('score-b').textContent = matchState.team_b_score;
    
    // Update winner state
    const teamAPanel = document.querySelector('.team-a');
    const teamBPanel = document.querySelector('.team-b');
    const winnerAMessage = document.getElementById('winner-a');
    const winnerBMessage = document.getElementById('winner-b');
    
    if (matchState.winner === 'A') {
        teamAPanel.classList.add('winner');
        teamBPanel.classList.remove('winner');
        winnerAMessage.style.display = 'block';
        winnerBMessage.style.display = 'none';
    } else if (matchState.winner === 'B') {
        teamAPanel.classList.remove('winner');
        teamBPanel.classList.add('winner');
        winnerAMessage.style.display = 'none';
        winnerBMessage.style.display = 'block';
    } else {
        teamAPanel.classList.remove('winner');
        teamBPanel.classList.remove('winner');
        winnerAMessage.style.display = 'none';
        winnerBMessage.style.display = 'none';
    }
    
    // Render number buttons
    renderNumberButtons('A');
    renderNumberButtons('B');
    
    // Update undo buttons
    updateUndoButtons();
}

// Render number buttons for a team
function renderNumberButtons(team) {
    const container = document.getElementById(`numbers-${team.toLowerCase()}`);
    const selected = team === 'A' ? matchState.team_a_selected : matchState.team_b_selected;
    
    container.innerHTML = '';
    
    for (let i = 1; i <= 15; i++) {
        if (!selected.includes(i)) {
            const button = document.createElement('button');
            button.className = 'number-btn';
            button.textContent = i;
            button.onclick = () => addScore(team, i);
            container.appendChild(button);
        }
    }
}

// Add score for a team
async function addScore(team, number) {
    if (matchState.winner) {
        return; // Game is already won
    }
    
    try {
        const response = await fetch(`${API_BASE}/score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                team: team,
                number: number
            })
        });
        
        if (response.ok) {
            matchState = await response.json();
            renderUI();
        } else {
            const error = await response.json();
            console.error('Failed to add score:', error.detail);
            alert('Error: ' + error.detail);
        }
    } catch (error) {
        console.error('Error adding score:', error);
        alert('Error adding score. Please try again.');
    }
}

// Undo last score for a team
async function undoScore(team) {
    try {
        const response = await fetch(`${API_BASE}/undo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                team: team
            })
        });
        
        if (response.ok) {
            matchState = await response.json();
            renderUI();
        } else {
            const error = await response.json();
            console.error('Failed to undo:', error.detail);
            alert('Error: ' + error.detail);
        }
    } catch (error) {
        console.error('Error undoing score:', error);
        alert('Error undoing score. Please try again.');
    }
}

// Update undo buttons state
function updateUndoButtons() {
    const undoA = document.getElementById('undo-a');
    const undoB = document.getElementById('undo-b');
    
    undoA.disabled = matchState.team_a_history.length === 0 || matchState.winner !== null;
    undoB.disabled = matchState.team_b_history.length === 0 || matchState.winner !== null;
}

// Confirm reset
function confirmReset() {
    if (confirm('Are you sure you want to reset the match? This will clear all scores and start a new game.')) {
        resetMatch();
    }
}

// Reset the match
async function resetMatch() {
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            matchState = await response.json();
            renderUI();
        } else {
            const error = await response.json();
            console.error('Failed to reset match:', error.detail);
            alert('Error: ' + error.detail);
        }
    } catch (error) {
        console.error('Error resetting match:', error);
        alert('Error resetting match. Please try again.');
    }
}

// Auto-refresh every 5 seconds to sync with other devices
setInterval(async () => {
    if (!document.hidden) { // Only refresh if tab is active
        await loadMatchState();
        renderUI();
    }
}, 5000);

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
