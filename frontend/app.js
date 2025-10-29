// API Configuration
const API_URL = 'http://localhost:5000';

// DOM Elements
const pages = {
    home: document.getElementById('homePage'),
    analyze: document.getElementById('analyzePage'),
    about: document.getElementById('aboutPage')
};

const navLinks = document.querySelectorAll('.nav-link');
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const retryBtn = document.getElementById('retryBtn');
const newSongBtn = document.getElementById('newSongBtn');
const downloadBtn = document.getElementById('downloadBtn');

// State
let selectedFile = null;
let currentResults = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupNavigation();
    setupResultsTabs();
});

// Navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.getAttribute('data-page');
            navigateToPage(targetPage);
        });
    });
}

function navigateToPage(pageName) {
    Object.values(pages).forEach(page => page.classList.remove('active'));
    
    if (pages[pageName]) {
        pages[pageName].classList.add('active');
    }
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageName) {
            link.classList.add('active');
        }
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Results Tabs
function setupResultsTabs() {
    const tabButtons = document.querySelectorAll('.results-nav-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            document.querySelectorAll('.results-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            const targetTabElement = document.getElementById(`${targetTab}Tab`);
            if (targetTabElement) {
                targetTabElement.classList.add('active');
            }
        });
    });
}

// Event Listeners
function setupEventListeners() {
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    uploadBox.addEventListener('dragover', handleDragOver);
    uploadBox.addEventListener('dragleave', handleDragLeave);
    uploadBox.addEventListener('drop', handleDrop);
    uploadBox.addEventListener('click', () => fileInput.click());
    
    analyzeBtn.addEventListener('click', analyzeSong);
    retryBtn.addEventListener('click', resetApp);
    newSongBtn.addEventListener('click', resetApp);
    downloadBtn.addEventListener('click', downloadResults);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        selectFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadBox.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file) {
        selectFile(file);
    }
}

function selectFile(file) {
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/x-m4a'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['mp3', 'wav', 'ogg', 'flac', 'm4a'];
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showError('Please select a valid audio file (MP3, WAV, OGG, FLAC, M4A)');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showError('File size must be less than 50MB');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = `✓ ${file.name}`;
    analyzeBtn.style.display = 'block';
}

async function analyzeSong() {
    if (!selectedFile) {
        showError('Please select a file first');
        return;
    }
    
    document.getElementById('uploadWrapper').style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    animateLoadingSteps();
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch(`${API_URL}/api/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data;
            displayResults(data);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

function animateLoadingSteps() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep > 0) {
            document.getElementById(steps[currentStep - 1]).classList.remove('active');
        }
        if (currentStep < steps.length) {
            document.getElementById(steps[currentStep]).classList.add('active');
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 1500);
}

function displayResults(data) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    displayOverviewTab(data);
    displayChordsTab(data);
    displayStrummingTab(data);
    displayPluckingTab(data);
    displayKeyTab(data);
    displayPracticeTab(data);
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayOverviewTab(data) {
    // Song Info
    const songInfoDiv = document.getElementById('songInfo');
    const songInfo = data.song_info;
    
    songInfoDiv.innerHTML = `
        <div class="info-item">
            <span class="info-label">Duration</span>
            <span class="info-value">${formatDuration(songInfo.duration)}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Tempo</span>
            <span class="info-value">${Math.round(songInfo.tempo)} BPM</span>
        </div>
        <div class="info-item">
            <span class="info-label">Time Signature</span>
            <span class="info-value">${songInfo.time_signature}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Key</span>
            <span class="info-value">${songInfo.key}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Energy</span>
            <span class="info-value">${formatEnergy(songInfo.energy)}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Groove</span>
            <span class="info-value">${songInfo.groove}</span>
        </div>
    `;
    
    // Playing Breakdown
    const breakdownDiv = document.getElementById('playingBreakdown');
    const totalSections = songInfo.total_chord_sections + songInfo.total_plucking_sections + songInfo.total_solo_sections;
    const chordPercentage = totalSections > 0 ? (songInfo.total_chord_sections / totalSections) * 100 : 0;
    const pluckingPercentage = totalSections > 0 ? (songInfo.total_plucking_sections / totalSections) * 100 : 0;
    const soloPercentage = totalSections > 0 ? (songInfo.total_solo_sections / totalSections) * 100 : 0;
    
    breakdownDiv.innerHTML = `
        <div class="breakdown-item">
            <span class="breakdown-label">Chord Sections</span>
            <div class="breakdown-bar">
                <div class="breakdown-fill" style="width: ${chordPercentage}%">${songInfo.total_chord_sections}</div>
            </div>
        </div>
        <div class="breakdown-item">
            <span class="breakdown-label">Plucking Sections</span>
            <div class="breakdown-bar">
                <div class="breakdown-fill" style="width: ${pluckingPercentage}%; background: linear-gradient(135deg, #6ba587 0%, #578e73 100%);">${songInfo.total_plucking_sections}</div>
            </div>
        </div>
        <div class="breakdown-item">
            <span class="breakdown-label">Solo Sections</span>
            <div class="breakdown-bar">
                <div class="breakdown-fill" style="width: ${soloPercentage}%; background: linear-gradient(135deg, #c95d5d 0%, #b84c4c 100%);">${songInfo.total_solo_sections}</div>
            </div>
        </div>
    `;
    
    // Key & Capo Info
    const keyCapoDiv = document.getElementById('keyCapoInfo');
    const capo = data.capo_suggestion;
    
    keyCapoDiv.innerHTML = `
        <div class="info-item">
            <span class="info-label">Detected Key</span>
            <span class="info-value">${data.key_analysis.detected_key}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Key Confidence</span>
            <span class="info-value">${(data.key_analysis.confidence * 100).toFixed(0)}%</span>
        </div>
        <div class="info-item">
            <span class="info-label">Capo Position</span>
            <span class="info-value">${capo.position === 0 ? 'No Capo' : `Fret ${capo.position}`}</span>
        </div>
    `;
    
    // Difficulty Rating
    const difficultyDiv = document.getElementById('difficultyRating');
    const avgDiff = songInfo.avg_chord_difficulty;
    const diffPercentage = (avgDiff / 10) * 100;
    
    let diffLabel = 'Easy';
    if (avgDiff > 6) diffLabel = 'Hard';
    else if (avgDiff > 3) diffLabel = 'Medium';
    
    difficultyDiv.innerHTML = `
        <div class="difficulty-meter">
            <div class="difficulty-indicator" style="left: ${diffPercentage}%"></div>
        </div>
        <div class="difficulty-label">${diffLabel}</div>
        <div class="difficulty-description">Average Chord Difficulty: ${avgDiff.toFixed(1)}/10</div>
    `;
    
    // Timeline
    displayTimeline(data.segments.all_segments);
}

function displayTimeline(segments) {
    const timelineDiv = document.getElementById('timelineChart');
    
    if (!segments || segments.length === 0) {
        timelineDiv.innerHTML = '<p>No timeline data available</p>';
        return;
    }
    
    timelineDiv.innerHTML = segments.map(segment => {
        let typeClass = 'timeline-chord';
        let typeBadge = 'Chord';
        let label = segment.chord || 'N/A';
        
        if (segment.type === 'plucking') {
            typeClass = 'timeline-plucking';
            typeBadge = 'Plucking';
            label = segment.pattern ? segment.pattern.type : 'Fingerpicking';
        } else if (segment.type === 'solo') {
            typeClass = 'timeline-solo';
            typeBadge = 'Solo';
            label = 'Guitar Solo';
        } else if (segment.type === 'transition') {
            typeClass = 'timeline-transition';
            typeBadge = 'Transition';
            label = 'Transition';
        }
        
        return `
            <div class="timeline-segment">
                <div class="timeline-time">${formatTime(segment.start_time)}</div>
                <div class="timeline-content ${typeClass}">
                    <span class="timeline-type type-${segment.type}">${typeBadge}</span>
                    <div class="timeline-label">${label}</div>
                    <div class="timeline-duration">${segment.duration.toFixed(1)}s</div>
                </div>
            </div>
        `;
    }).join('');
}

function displayChordsTab(data) {
    const chordSections = data.segments.chord_sections;
    const uniqueChords = data.unique_chords;
    const chordAnalysis = data.chord_analysis;
    
    // Summary
    document.getElementById('uniqueChordCount').textContent = uniqueChords.length;
    document.getElementById('chordChangeCount').textContent = chordSections.length;
    document.getElementById('chordDifficulty').textContent = data.song_info.avg_chord_difficulty.toFixed(1);
    
    // Unique Chords with Difficulty
    const uniqueChordsDiv = document.getElementById('uniqueChordsList');
    uniqueChordsDiv.innerHTML = uniqueChords.map(chord => {
        const difficulty = chordAnalysis.difficulties[chord] || 5;
        return `
            <div class="chord-card">
                <div class="chord-name-display">${chord}</div>
                <div class="fingering-difficulty diff-${difficulty}">
                    Difficulty: ${difficulty}/10
                </div>
            </div>
        `;
    }).join('');
    
    // Chord Fingerings
    const fingeringsDiv = document.getElementById('chordFingerings');
    const fingerings = chordAnalysis.fingerings;
    
    if (Object.keys(fingerings).length > 0) {
        fingeringsDiv.innerHTML = Object.entries(fingerings).map(([chord, data]) => `
            <div class="fingering-card">
                <div class="fingering-chord-name">${chord}</div>
                <div class="fingering-diagram">
                    <div class="fingering-frets">${data.frets}</div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">
                        Fingers: ${data.fingers}
                    </div>
                </div>
                <div class="fingering-difficulty diff-${data.difficulty}">
                    Level ${data.difficulty}/10
                </div>
            </div>
        `).join('');
    } else {
        fingeringsDiv.innerHTML = '<p>Chord fingering diagrams not available for these chords</p>';
    }
    
    // Chord Transitions
    const transitionsDiv = document.getElementById('chordTransitions');
    const transitions = chordAnalysis.transitions;
    
    if (transitions && transitions.length > 0) {
        transitionsDiv.innerHTML = transitions.slice(0, 10).map(trans => {
            let diffClass = 'transition-easy';
            if (trans.difficulty > 6) diffClass = 'transition-hard';
            else if (trans.difficulty > 3) diffClass = 'transition-medium';
            
            return `
                <div class="transition-item">
                    <div>
                        <div class="transition-chords">
                            <span>${trans.from}</span>
                            <span class="transition-arrow">→</span>
                            <span>${trans.to}</span>
                        </div>
                        <div class="transition-tips">${trans.tips}</div>
                    </div>
                    <div class="transition-difficulty ${diffClass}">
                        ${trans.difficulty}/10
                    </div>
                </div>
            `;
        }).join('');
    } else {
        transitionsDiv.innerHTML = '<p>No transition analysis available</p>';
    }
    
    // Chord Progression
    const progressionDiv = document.getElementById('chordProgression');
    progressionDiv.innerHTML = chordSections.map(section => `
        <div class="progression-item">
            <div class="progression-chord">${section.chord}</div>
            <div class="progression-timing">
                <span>⏱️ ${formatTime(section.start_time)} - ${formatTime(section.end_time)}</span>
                <span>⏳ ${section.duration.toFixed(1)}s</span>
            </div>
        </div>
    `).join('');
}
// Add after displayChordsTab function

function displayChordsTab(data) {
    const chordSections = data.segments.chord_sections;
    const uniqueChords = data.unique_chords;
    const chordAnalysis = data.chord_analysis;
    
    // Summary
    document.getElementById('uniqueChordCount').textContent = uniqueChords.length;
    document.getElementById('chordChangeCount').textContent = chordSections.length;
    document.getElementById('chordDifficulty').textContent = data.song_info.avg_chord_difficulty.toFixed(1);
    
    // Unique Chords with Difficulty - MAKE CLICKABLE
    const uniqueChordsDiv = document.getElementById('uniqueChordsList');
    uniqueChordsDiv.innerHTML = uniqueChords.map(chord => {
        const difficulty = chordAnalysis.difficulties[chord] || 5;
        return `
            <div class="chord-card" onclick="showChordDetails('${chord}')">
                <div class="chord-name-display">${chord}</div>
                <div class="fingering-difficulty diff-${difficulty}">
                    Difficulty: ${difficulty}/10
                </div>
            </div>
        `;
    }).join('');
    
    // Chord Fingerings
    const fingeringsDiv = document.getElementById('chordFingerings');
    const fingerings = chordAnalysis.fingerings;
    
    if (Object.keys(fingerings).length > 0) {
        fingeringsDiv.innerHTML = Object.entries(fingerings).map(([chord, data]) => `
            <div class="fingering-card" onclick="showChordDetails('${chord}')">
                <div class="fingering-chord-name">${chord}</div>
                <div class="fingering-diagram">
                    <div class="fingering-frets">${data.frets}</div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">
                        Fingers: ${data.fingers}
                    </div>
                </div>
                <div class="fingering-difficulty diff-${data.difficulty}">
                    Level ${data.difficulty}/10
                </div>
            </div>
        `).join('');
    } else {
        fingeringsDiv.innerHTML = '<p>Chord fingering diagrams not available for these chords</p>';
    }
    
    // Chord Transitions - MAKE TRANSITION CHORDS CLICKABLE
    const transitionsDiv = document.getElementById('chordTransitions');
    const transitions = chordAnalysis.transitions;
    
    if (transitions && transitions.length > 0) {
        transitionsDiv.innerHTML = transitions.slice(0, 10).map(trans => {
            let diffClass = 'transition-easy';
            if (trans.difficulty > 6) diffClass = 'transition-hard';
            else if (trans.difficulty > 3) diffClass = 'transition-medium';
            
            return `
                <div class="transition-item">
                    <div>
                        <div class="transition-chords">
                            <span class="clickable-chord" onclick="showChordDetails('${trans.from}')">${trans.from}</span>
                            <span class="transition-arrow">→</span>
                            <span class="clickable-chord" onclick="showChordDetails('${trans.to}')">${trans.to}</span>
                        </div>
                        <div class="transition-tips">${trans.tips}</div>
                    </div>
                    <div class="transition-difficulty ${diffClass}">
                        ${trans.difficulty}/10
                    </div>
                </div>
            `;
        }).join('');
    } else {
        transitionsDiv.innerHTML = '<p>No transition analysis available</p>';
    }
    
    // Chord Progression - MAKE CLICKABLE
    const progressionDiv = document.getElementById('chordProgression');
    progressionDiv.innerHTML = chordSections.map(section => `
        <div class="progression-item" onclick="showChordDetails('${section.chord}')">
            <div class="progression-chord">${section.chord}</div>
            <div class="progression-timing">
                <span>⏱️ ${formatTime(section.start_time)} - ${formatTime(section.end_time)}</span>
                <span>⏳ ${section.duration.toFixed(1)}s</span>
            </div>
        </div>
    `).join('');
}

// Chord Modal Functions
function showChordDetails(chordName) {
    // Fetch chord details from backend
    fetch(`${API_URL}/api/chord-details/${encodeURIComponent(chordName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayChordModal(data.chord_details);
            } else {
                alert('Chord details not available for: ' + chordName);
            }
        })
        .catch(error => {
            console.error('Error fetching chord details:', error);
            alert('Could not load chord details');
        });
}

function displayChordModal(chordDetails) {
    const modal = document.getElementById('chordModal');
    
    // Set chord name
    document.getElementById('modalChordName').textContent = chordDetails.name + ' - ' + chordDetails.description;
    
    // Display ASCII diagram
    document.getElementById('chordDiagram').innerHTML = `<pre>${chordDetails.diagram}</pre>`;
    
    // Display visual fret diagram
    displayVisualFretDiagram(chordDetails.frets, chordDetails.fingers);
    
    // Display finger positions
    const fingerPositionsDiv = document.getElementById('fingerPositions');
    if (chordDetails.finger_details) {
        fingerPositionsDiv.innerHTML = Object.entries(chordDetails.finger_details)
            .map(([string, instruction]) => `
                <div class="finger-position-item">
                    <div class="finger-number">${string.charAt(0)}</div>
                    <div class="finger-instruction">${instruction}</div>
                </div>
            `).join('');
    } else {
        fingerPositionsDiv.innerHTML = '<p>Detailed finger positions not available</p>';
    }
    
    // Display tips
    const tipsDiv = document.getElementById('chordTips');
    if (chordDetails.tips && chordDetails.tips.length > 0) {
        tipsDiv.innerHTML = chordDetails.tips.map(tip => `<li>${tip}</li>`).join('');
    } else {
        tipsDiv.innerHTML = '<li>No specific tips available</li>';
    }
    
    // Display metadata
    const metadataDiv = document.getElementById('chordMetadata');
    metadataDiv.innerHTML = `
        <div class="metadata-item">
            <span class="metadata-label">Difficulty</span>
            <span class="metadata-value">${chordDetails.difficulty}/10</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Type</span>
            <span class="metadata-value">${chordDetails.barre ? 'Barre Chord' : 'Open Chord'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Fret Pattern</span>
            <span class="metadata-value">${chordDetails.frets}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Finger Pattern</span>
            <span class="metadata-value">${chordDetails.fingers}</span>
        </div>
    `;
    
    // Display common transitions
    const transitionsDiv = document.getElementById('commonTransitions');
    if (chordDetails.common_transitions && chordDetails.common_transitions.length > 0) {
        transitionsDiv.innerHTML = chordDetails.common_transitions
            .map(trans => `<div class="transition-chip" onclick="showChordDetails('${trans}')">${trans}</div>`)
            .join('');
    } else {
        transitionsDiv.innerHTML = '<p>No common transitions data</p>';
    }
    
    // Show modal
    modal.style.display = 'flex';
}

function displayVisualFretDiagram(fretsString, fingersString) {
    const stringsContainer = document.querySelector('.strings-container');
    const fretNumbers = document.querySelector('.fret-numbers');
    
    // String names (low E to high E)
    const stringNames = ['E', 'A', 'D', 'G', 'B', 'e'];
    
    fretNumbers.innerHTML = stringNames.map(name => `<div>${name}</div>`).join('');
    
    stringsContainer.innerHTML = '';
    
    for (let i = 0; i < 6; i++) {
        const fretValue = fretsString[i];
        const fingerValue = fingersString[i];
        
        const stringDiv = document.createElement('div');
        stringDiv.className = 'string-display';
        
        let fretClass = 'fret-position';
        let displayValue = '';
        
        if (fretValue === 'x') {
            fretClass += ' muted';
            displayValue = 'X';
        } else if (fretValue === '0') {
            fretClass += ' open';
            displayValue = 'O';
        } else {
            fretClass += ' active';
            displayValue = fingerValue !== '0' ? fingerValue : fretValue;
        }
        
        stringDiv.innerHTML = `
            <div class="${fretClass}">${displayValue}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 5px;">
                ${fretValue === 'x' ? 'Muted' : fretValue === '0' ? 'Open' : `Fret ${fretValue}`}
            </div>
        `;
        
        stringsContainer.appendChild(stringDiv);
    }
}

function closeChordModal() {
    document.getElementById('chordModal').style.display = 'none';
}

// Setup modal close handlers
document.getElementById('modalClose').addEventListener('click', closeChordModal);
document.getElementById('chordModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeChordModal();
    }
});

// Add CSS for clickable chords
const style = document.createElement('style');
style.textContent = `
    .clickable-chord {
        cursor: pointer;
        text-decoration: underline;
        text-decoration-style: dotted;
        transition: all 0.3s ease;
    }
    
    .clickable-chord:hover {
        color: var(--accent-gold);
        text-decoration-style: solid;
    }
    
    .chord-card,
    .fingering-card,
    .progression-item {
        cursor: pointer;
    }
`;
document.head.appendChild(style);

// Make function globally accessible
window.showChordDetails = showChordDetails;
function displayStrummingTab(data) {
    const strumming = data.strumming;
    
    // Recommended Pattern
    const recommendedDiv = document.getElementById('recommendedPattern');
    recommendedDiv.innerHTML = formatStrummingPattern(strumming.recommended);
    
    // Alternative Patterns
    const alternativesDiv = document.getElementById('alternativePatterns');
    if (strumming.alternatives && strumming.alternatives.length > 0) {
        alternativesDiv.innerHTML = `
            <div class="alternatives-grid">
                ${strumming.alternatives.map(pattern => `
                    <div class="alternative-pattern">
                        ${formatStrummingPattern(pattern)}
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        alternativesDiv.innerHTML = '<p>No alternative patterns available.</p>';
    }
    
    // Fingerpicking Pattern
    if (strumming.fingerpicking) {
        document.getElementById('fingerpickingSection').style.display = 'block';
        document.getElementById('fingerpickingPattern').innerHTML = formatFingerpickingPattern(strumming.fingerpicking);
    } else {
        document.getElementById('fingerpickingSection').style.display = 'none';
    }
    
    // Tempo Analysis
    const tempoAnalysisDiv = document.getElementById('tempoAnalysis');
    const tempoInfo = strumming.tempo_analysis;
    tempoAnalysisDiv.innerHTML = `
        <div class="analysis-item">
            <div class="analysis-label">Category</div>
            <div class="analysis-value">${tempoInfo.category}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Guidance</div>
            <div class="analysis-value">${tempoInfo.guidance}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Practice Tip</div>
            <div class="analysis-value">${tempoInfo.practice_tip}</div>
        </div>
    `;
    
    // Energy Analysis
    const energyAnalysisDiv = document.getElementById('energyAnalysis');
    const energyInfo = strumming.energy_analysis;
    energyAnalysisDiv.innerHTML = `
        <div class="analysis-item">
            <div class="analysis-label">Category</div>
            <div class="analysis-value">${energyInfo.category}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Dynamics</div>
            <div class="analysis-value">${energyInfo.dynamics}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Technique</div>
            <div class="analysis-value">${energyInfo.technique}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Tip</div>
            <div class="analysis-value">${energyInfo.tip}</div>
        </div>
    `;
}

function formatStrummingPattern(pattern) {
    return `
        <div class="pattern-header">
            <div class="pattern-name">${pattern.name}</div>
            <span class="pattern-difficulty difficulty-${pattern.difficulty}">${pattern.difficulty}</span>
        </div>
        <div class="pattern-notation">${pattern.pattern}</div>
        <div class="pattern-description">${pattern.description}</div>
        ${pattern.timing_notes ? `
            <div class="timing-notes">
                <h4>💡 Timing & Technique Notes</h4>
                <ul>
                    ${pattern.timing_notes.map(note => `<li>${note}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        ${pattern.genres ? `
            <div style="margin-top: 1rem; text-align: center;">
                <strong>Genres:</strong> ${pattern.genres.join(', ')}
            </div>
        ` : ''}
    `;
}

function formatFingerpickingPattern(pattern) {
    return `
        <div class="fingerpicking-pattern-display">
            <h4>${pattern.name}</h4>
            <div class="fingerpicking-notation">${pattern.pattern}</div>
            <div class="pattern-description">${pattern.description}</div>
            
            ${pattern.notation_detail ? `
                <div class="fingerpicking-details">
                    ${Object.entries(pattern.notation_detail).map(([key, value]) => `
                        <div class="fingerpicking-detail">
                            <strong>${key}:</strong> ${value}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${pattern.tips ? `
                <div class="fingerpicking-tips">
                    <h4>Practice Tips</h4>
                    <ul>
                        ${pattern.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function displayPluckingTab(data) {
    const pluckingSections = data.segments.plucking_sections;
    const soloSections = data.segments.solo_sections;
    const pluckingDiv = document.getElementById('pluckingSections');
    const soloDiv = document.getElementById('soloSections');
    
    // Display Plucking Sections
    if (!pluckingSections || pluckingSections.length === 0) {
        pluckingDiv.innerHTML = `
            <div class="no-plucking">
                <div class="no-plucking-icon">🎸</div>
                <h3>No Plucking Sections Detected</h3>
                <p>This song appears to be primarily strummed. Check the Strumming tab for patterns.</p>
            </div>
        `;
    } else {
        pluckingDiv.innerHTML = `
            <h3 style="margin-bottom: 2rem;">Fingerpicking Sections (${pluckingSections.length})</h3>
            ${pluckingSections.map((section, index) => {
                const pattern = section.pattern;
                const chordInfo = section.chord ? `<p><strong>Over Chord:</strong> ${section.chord}</p>` : '';
                
                return `
                    <div class="plucking-section">
                        <div class="plucking-header">
                            <span class="plucking-type">${pattern.type}</span>
                            <span class="plucking-time">${formatTime(section.start_time)} - ${formatTime(section.end_time)}</span>
                        </div>
                        
                        ${chordInfo}
                        
                        <div class="plucking-description">
                            ${pattern.description}
                        </div>
                        
                        <div class="plucking-details">
                            <div class="plucking-detail-item">
                                <div class="detail-label">Notes per Second</div>
                                <div class="detail-value">${pattern.notes_per_second.toFixed(1)}</div>
                            </div>
                            <div class="plucking-detail-item">
                                <div class="detail-label">Total Notes</div>
                                <div class="detail-value">${pattern.num_notes}</div>
                            </div>
                            <div class="plucking-detail-item">
                                <div class="detail-label">Duration</div>
                                <div class="detail-value">${section.duration.toFixed(1)}s</div>
                            </div>
                            <div class="plucking-detail-item">
                                <div class="detail-label">Confidence</div>
                                <div class="detail-value">${(section.confidence * 100).toFixed(0)}%</div>
                            </div>
                        </div>
                        
                        <div class="plucking-notation">
                            <div class="notation-label">Suggested Pattern:</div>
                            <div class="notation-pattern">${pattern.notation}</div>
                            ${pattern.prominent_notes && pattern.prominent_notes.length > 0 ? 
                                `<p style="margin-top: 1rem; color: var(--text-secondary);">
                                    <strong>Prominent Notes:</strong> ${pattern.prominent_notes.join(', ')}
                                </p>` : ''}
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    }
    
    // Display Solo Sections
    if (!soloSections || soloSections.length === 0) {
        soloDiv.innerHTML = `
            <div style="margin-top: 3rem;">
                <h3>No Guitar Solos Detected</h3>
                <p style="color: var(--text-secondary); margin-top: 1rem;">
                    This song doesn't appear to have distinct guitar solo sections.
                </p>
            </div>
        `;
    } else {
        soloDiv.innerHTML = `
            <h3 style="margin-top: 3rem; margin-bottom: 2rem;">Guitar Solo Sections (${soloSections.length})</h3>
            ${soloSections.map((section, index) => `
                <div class="solo-section">
                    <div class="solo-header">
                        <span class="solo-badge">🎸 Solo ${index + 1}</span>
                        <span class="solo-time">${formatTime(section.start_time)} - ${formatTime(section.end_time)}</span>
                    </div>
                    
                    <div class="solo-details">
                        <div class="solo-detail-item">
                            <div class="detail-label">Duration</div>
                            <div class="detail-value">${section.duration.toFixed(1)}s</div>
                        </div>
                        <div class="solo-detail-item">
                            <div class="detail-label">Confidence</div>
                            <div class="detail-value">${(section.confidence * 100).toFixed(0)}%</div>
                        </div>
                        ${section.underlying_chord ? `
                            <div class="solo-detail-item">
                                <div class="detail-label">Underlying Chord</div>
                                <div class="detail-value">${section.underlying_chord}</div>
                            </div>
                        ` : ''}
                    </div>
                    
                    <p style="margin-top: 1rem; color: var(--text-secondary); font-style: italic;">
                        💡 This section features melodic lead guitar playing. Focus on single-note accuracy and phrasing.
                    </p>
                </div>
            `).join('')}
        `;
    }
}

function displayKeyTab(data) {
    const keyAnalysis = data.key_analysis;
    const capoSuggestion = data.capo_suggestion;
    const scaleInfo = keyAnalysis.scale_info;
    
    // Detected Key
    const detectedKeyDiv = document.getElementById('detectedKey');
    detectedKeyDiv.innerHTML = `
        <div class="key-name">${keyAnalysis.detected_key}</div>
        <div class="key-confidence">Confidence: ${(keyAnalysis.confidence * 100).toFixed(0)}%</div>
    `;
    
    // Capo Suggestion
    const capoDiv = document.getElementById('capoSuggestion');
    if (capoSuggestion.position === 0) {
        capoDiv.innerHTML = `
            <div class="capo-position no-capo">No Capo Needed</div>
            <div class="capo-reason">${capoSuggestion.reason}</div>
        `;
    } else {
        capoDiv.innerHTML = `
            <div class="capo-position">Capo on Fret ${capoSuggestion.position}</div>
            <div class="capo-reason">${capoSuggestion.reason}</div>
            ${capoSuggestion.new_chords ? `
                <div style="margin-top: 1rem; padding: 1rem; background: var(--secondary-bg); border-radius: 8px;">
                    <strong>New Chords with Capo:</strong><br>
                    ${capoSuggestion.new_chords.slice(0, 8).join(', ')}
                </div>
            ` : ''}
        `;
    }
    
    // Scale Information
    const scaleDiv = document.getElementById('scaleInfo');
    scaleDiv.innerHTML = `
        <div class="scale-info-text">
            <strong>${scaleInfo.key}</strong> ${scaleInfo.type} Scale
        </div>
        <div class="scale-notes">
            ${scaleInfo.notes.map(note => `
                <div class="scale-note">${note}</div>
            `).join('')}
        </div>
        <div class="scale-info-text">
            Use these notes for improvisation and melody creation
        </div>
    `;
    
    // Related Keys
    const relatedKeysDiv = document.getElementById('relatedKeys');
    relatedKeysDiv.innerHTML = `
        <div class="related-keys-display">
            <div class="related-key-item">
                <div class="related-key-label">Current Key</div>
                <div class="related-key-value">${scaleInfo.key}</div>
            </div>
            <div class="related-key-item">
                <div class="related-key-label">Relative ${scaleInfo.type === 'Major' ? 'Minor' : 'Major'}</div>
                <div class="related-key-value">${scaleInfo.relative_key}</div>
            </div>
        </div>
        <p style="text-align: center; color: var(--text-secondary); margin-top: 1.5rem;">
            The relative key shares the same notes and can be used for modulation or variation
        </p>
    `;
}

function displayPracticeTab(data) {
    const routine = data.practice_routine;
    const practiceDiv = document.getElementById('practiceRoutine');
    
    practiceDiv.innerHTML = `
        <div class="practice-total-time">
            ⏱️ Total Practice Time: ${routine.total_time}
        </div>
        
        <div class="practice-steps">
            ${routine.steps.map(step => `
                <div class="practice-step">
                    <div class="step-number">${step.step}</div>
                    <div class="step-content">
                        <div class="step-title">${step.title}</div>
                        <div class="step-description">${step.description}</div>
                        <div class="step-duration">⏱️ ${step.duration}</div>
                        ${step.exercises ? `
                            <ul style="margin-top: 1rem; padding-left: 1.5rem; color: var(--text-secondary);">
                                ${step.exercises.map(ex => `<li>${ex}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="practice-tips">
            <h4>💡 Practice Tips</h4>
            <div class="tips-list">
                ${routine.tips.map(tip => `
                    <div class="tip-item">
                        <span class="tip-icon">✓</span>
                        <span class="tip-text">${tip}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${routine.weekly_plan ? `
            <div class="weekly-plan">
                <h4>📅 Weekly Practice Plan</h4>
                ${Object.entries(routine.weekly_plan).map(([day, activity]) => `
                    <div class="week-day">
                        <div class="week-day-label">${day.replace(/_/g, ' ').replace(/day /gi, 'Day ')}</div>
                        <div class="week-day-activity">${activity}</div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
}

// Utility Functions
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatEnergy(energy) {
    if (energy < 0.3) return 'Low ⚡';
    if (energy < 0.6) return 'Medium ⚡⚡';
    return 'High ⚡⚡⚡';
}

function downloadResults() {
    if (!currentResults) return;
    
    const resultsText = generateResultsText(currentResults);
    const blob = new Blob([resultsText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `guitar-analysis-${selectedFile.name.replace(/\.[^/.]+$/, '')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function generateResultsText(data) {
    const songInfo = data.song_info;
    const chordSections = data.segments.chord_sections;
    const pluckingSections = data.segments.plucking_sections;
    const soloSections = data.segments.solo_sections;
    const uniqueChords = data.unique_chords;
    const strumming = data.strumming;
    const keyAnalysis = data.key_analysis;
    const capo = data.capo_suggestion;
    
    let text = `
╔════════════════════════════════════════════════════════════╗
║      GUITAR COVER ASSISTANT - COMPREHENSIVE ANALYSIS       ║
╚════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════
SONG INFORMATION
═══════════════════════════════════════════════════════════════

Duration: ${formatDuration(songInfo.duration)}
Tempo: ${Math.round(songInfo.tempo)} BPM
Time Signature: ${songInfo.time_signature}
Key: ${songInfo.key} (${(keyAnalysis.confidence * 100).toFixed(0)}% confidence)
Energy Level: ${formatEnergy(songInfo.energy)}
Groove: ${songInfo.groove}
Average Chord Difficulty: ${songInfo.avg_chord_difficulty.toFixed(1)}/10

═══════════════════════════════════════════════════════════════
SONG STRUCTURE
═══════════════════════════════════════════════════════════════

Chord Sections: ${songInfo.total_chord_sections}
Plucking Sections: ${songInfo.total_plucking_sections}
Solo Sections: ${songInfo.total_solo_sections}

═══════════════════════════════════════════════════════════════
KEY & SCALE ANALYSIS
═══════════════════════════════════════════════════════════════

Detected Key: ${keyAnalysis.detected_key}
Scale Type: ${keyAnalysis.scale_info.type}
Scale Notes: ${keyAnalysis.scale_info.notes.join(' - ')}
Relative Key: ${keyAnalysis.scale_info.relative_key}

═══════════════════════════════════════════════════════════════
CAPO SUGGESTION
═══════════════════════════════════════════════════════════════

Position: ${capo.position === 0 ? 'No Capo Needed' : `Fret ${capo.position}`}
Reason: ${capo.reason}
${capo.new_chords ? `\nChords with Capo: ${capo.new_chords.join(', ')}` : ''}

═══════════════════════════════════════════════════════════════
UNIQUE CHORDS (${uniqueChords.length} total)
═══════════════════════════════════════════════════════════════

${uniqueChords.map(chord => {
    const diff = data.chord_analysis.difficulties[chord] || 5;
    return `${chord.padEnd(8)} - Difficulty: ${diff}/10`;
}).join('\n')}

═══════════════════════════════════════════════════════════════
RECOMMENDED STRUMMING PATTERN
═══════════════════════════════════════════════════════════════

Name: ${strumming.recommended.name}
Pattern: ${strumming.recommended.pattern}
Difficulty: ${strumming.recommended.difficulty}
Description: ${strumming.recommended.description}
Genres: ${strumming.recommended.genres.join(', ')}

Timing Notes:
${strumming.recommended.timing_notes ? 
    strumming.recommended.timing_notes.map(note => `  • ${note}`).join('\n') : 'None'}

═══════════════════════════════════════════════════════════════
ALTERNATIVE STRUMMING PATTERNS
═══════════════════════════════════════════════════════════════

${strumming.alternatives.map((pattern, index) => `
${index + 1}. ${pattern.name}
   Pattern: ${pattern.pattern}
   Difficulty: ${pattern.difficulty}
   ${pattern.description}
   Genres: ${pattern.genres.join(', ')}
`).join('\n')}

${strumming.fingerpicking ? `
═══════════════════════════════════════════════════════════════
FINGERPICKING PATTERN
═══════════════════════════════════════════════════════════════

Name: ${strumming.fingerpicking.name}
Pattern: ${strumming.fingerpicking.pattern}
Difficulty: ${strumming.fingerpicking.difficulty}
Description: ${strumming.fingerpicking.description}

${strumming.fingerpicking.tips ? `Tips:\n${strumming.fingerpicking.tips.map(tip => `  • ${tip}`).join('\n')}` : ''}
` : ''}

═══════════════════════════════════════════════════════════════
CHORD PROGRESSION TIMELINE
═══════════════════════════════════════════════════════════════

${chordSections.map(section => 
    `${formatTime(section.start_time)} - ${formatTime(section.end_time)} | ${section.chord.padEnd(8)} (${section.duration.toFixed(1)}s)`
).join('\n')}

${pluckingSections.length > 0 ? `
═══════════════════════════════════════════════════════════════
PLUCKING/FINGERPICKING SECTIONS
═══════════════════════════════════════════════════════════════

${pluckingSections.map((section, index) => {
    const pattern = section.pattern;
    return `
Section ${index + 1}: ${formatTime(section.start_time)} - ${formatTime(section.end_time)}
Type: ${pattern.type}
Description: ${pattern.description}
${section.chord ? `Chord: ${section.chord}` : ''}
Notes per Second: ${pattern.notes_per_second.toFixed(1)}
Total Notes: ${pattern.num_notes}
Pattern Notation: ${pattern.notation}
${pattern.prominent_notes && pattern.prominent_notes.length > 0 ? 
    `Prominent Notes: ${pattern.prominent_notes.join(', ')}` : ''}
Confidence: ${(section.confidence * 100).toFixed(0)}%
`;
}).join('\n─────────────────────────────────────────────────────────────\n')}
` : 'No plucking sections detected in this song.\n'}

${soloSections.length > 0 ? `
═══════════════════════════════════════════════════════════════
GUITAR SOLO SECTIONS
═══════════════════════════════════════════════════════════════

${soloSections.map((section, index) => `
Solo ${index + 1}: ${formatTime(section.start_time)} - ${formatTime(section.end_time)}
Duration: ${section.duration.toFixed(1)}s
${section.underlying_chord ? `Underlying Chord: ${section.underlying_chord}` : ''}
Confidence: ${(section.confidence * 100).toFixed(0)}%
`).join('\n─────────────────────────────────────────────────────────────\n')}
` : ''}

${data.chord_analysis.transitions && data.chord_analysis.transitions.length > 0 ? `
═══════════════════════════════════════════════════════════════
CHORD TRANSITIONS
═══════════════════════════════════════════════════════════════

${data.chord_analysis.transitions.slice(0, 15).map(trans => `
${trans.from} → ${trans.to}
Difficulty: ${trans.difficulty}/10
Tip: ${trans.tips}
`).join('\n─────────────────────────────────────────────────────────────\n')}
` : ''}

═══════════════════════════════════════════════════════════════
TEMPO & ENERGY ANALYSIS
═══════════════════════════════════════════════════════════════

Tempo Category: ${strumming.tempo_analysis.category}
Guidance: ${strumming.tempo_analysis.guidance}
Practice Tip: ${strumming.tempo_analysis.practice_tip}

Energy Category: ${strumming.energy_analysis.category}
Dynamics: ${strumming.energy_analysis.dynamics}
Technique: ${strumming.energy_analysis.technique}
Tip: ${strumming.energy_analysis.tip}

═══════════════════════════════════════════════════════════════
PRACTICE ROUTINE
═══════════════════════════════════════════════════════════════

Total Time: ${data.practice_routine.total_time}

${data.practice_routine.steps.map(step => `
Step ${step.step}: ${step.title}
${step.description}
Duration: ${step.duration}
${step.exercises ? `\nExercises:\n${step.exercises.map(ex => `  • ${ex}`).join('\n')}` : ''}
`).join('\n───────────────────────────────────────────────────────────\n')}

Practice Tips:
${data.practice_routine.tips.map(tip => `  ✓ ${tip}`).join('\n')}

${data.practice_routine.weekly_plan ? `
Weekly Plan:
${Object.entries(data.practice_routine.weekly_plan).map(([day, activity]) => 
    `  ${day.replace(/_/g, ' ')}: ${activity}`
).join('\n')}
` : ''}

═══════════════════════════════════════════════════════════════

Generated by Guitar Cover Assistant
Comprehensive AI-Powered Music Analysis Platform
═══════════════════════════════════════════════════════════════
`;

    return text;
}

function showError(message) {
    document.getElementById('uploadWrapper').style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
}

function resetApp() {
    selectedFile = null;
    currentResults = null;
    fileInput.value = '';
    fileName.textContent = '';
    analyzeBtn.style.display = 'none';
    
    document.getElementById('uploadWrapper').style.display = 'block';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Reset loading steps
    ['step1', 'step2', 'step3', 'step4'].forEach(step => {
        document.getElementById(step).classList.remove('active');
    });
    
    // Reset results tabs
    document.querySelectorAll('.results-nav-btn').forEach((btn, index) => {
        btn.classList.remove('active');
        if (index === 0) btn.classList.add('active');
    });
    
    document.querySelectorAll('.results-tab').forEach((tab, index) => {
        tab.classList.remove('active');
        if (index === 0) tab.classList.add('active');
    });
    
    navigateToPage('analyze');
}

// Make navigateToPage globally accessible
window.navigateToPage = navigateToPage;
