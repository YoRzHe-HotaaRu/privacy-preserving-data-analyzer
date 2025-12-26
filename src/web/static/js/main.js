/**
 * ═══════════════════════════════════════════════════════════════════════════
 * PRIV.GUARD - Privacy-Preserving Data Analyzer
 * Main JavaScript Controller
 * ═══════════════════════════════════════════════════════════════════════════
 */

// ─────────────────────────────────────────────────────────────────────────────
// State Management
// ─────────────────────────────────────────────────────────────────────────────
const state = {
    sessionId: null,
    currentData: null,
    isAnalyzing: false
};

// ─────────────────────────────────────────────────────────────────────────────
// DOM Elements
// ─────────────────────────────────────────────────────────────────────────────
const elements = {
    // Upload
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    uploadProgress: document.getElementById('uploadProgress'),
    progressFill: document.getElementById('progressFill'),
    progressPercent: document.getElementById('progressPercent'),
    uploadStatus: document.getElementById('uploadStatus'),

    // Sections
    uploadSection: document.getElementById('uploadSection'),
    previewSection: document.getElementById('previewSection'),
    piiSection: document.getElementById('piiSection'),
    configSection: document.getElementById('configSection'),
    resultsSection: document.getElementById('resultsSection'),

    // Config
    epsilonSlider: document.getElementById('epsilonSlider'),
    epsilonValue: document.getElementById('epsilonValue'),
    sliderFill: document.getElementById('sliderFill'),
    strategySelect: document.getElementById('strategySelect'),
    quasiInput: document.getElementById('quasiInput'),
    sensitiveInput: document.getElementById('sensitiveInput'),

    // Actions
    analyzeBtn: document.getElementById('analyzeBtn'),
    downloadReportBtn: document.getElementById('downloadReportBtn'),
    themeToggle: document.getElementById('themeToggle')
};

// ─────────────────────────────────────────────────────────────────────────────
// Initialization
// ─────────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);

function init() {
    console.log('🔒 PRIV.GUARD initialized');
    setupUploadHandlers();
    setupConfigHandlers();
    setupAnalysisHandlers();
    setupAnimations();
}

// ─────────────────────────────────────────────────────────────────────────────
// Upload Handlers
// ─────────────────────────────────────────────────────────────────────────────
function setupUploadHandlers() {
    const { uploadZone, fileInput } = elements;

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Click to upload
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    // Validate file type
    const allowedTypes = ['.csv', '.json', '.xlsx', '.xls'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(ext)) {
        showNotification('Please upload a CSV, JSON, or Excel file.', 'error');
        return;
    }

    // Show progress
    elements.uploadProgress.classList.remove('hidden');
    updateProgress(0, 'Initializing upload...');

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Animate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + Math.random() * 15, 90);
            updateProgress(progress, 'Uploading file...');
        }, 200);

        // Upload
        const response = await fetch('/api/v1/upload', {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        state.sessionId = data.session_id;
        state.currentData = data;

        updateProgress(100, 'Processing complete!');

        // Show sections with staggered animation
        setTimeout(() => {
            displayDataPreview(data);
            displayPIIResults(data);
            showSection(elements.previewSection, 0);
            showSection(elements.piiSection, 100);
            showSection(elements.configSection, 200);
        }, 500);

    } catch (error) {
        console.error('Upload error:', error);
        updateProgress(0, 'Upload failed. Please try again.');
        showNotification('Upload failed. Please try again.', 'error');
    }
}

function updateProgress(percent, status) {
    elements.progressFill.style.width = percent + '%';
    elements.progressPercent.textContent = Math.round(percent) + '%';
    elements.uploadStatus.textContent = status;
}

// ─────────────────────────────────────────────────────────────────────────────
// Data Preview
// ─────────────────────────────────────────────────────────────────────────────
function displayDataPreview(data) {
    const { data_summary } = data;

    // Row count badge
    document.getElementById('rowCount').textContent = `${data_summary.row_count} RECORDS`;

    // Stats grid
    const statsGrid = document.getElementById('dataMetrics');
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${formatNumber(data_summary.row_count)}</div>
            <div class="stat-label">Records</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data_summary.column_count}</div>
            <div class="stat-label">Columns</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.pii_count}</div>
            <div class="stat-label">PII Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${data.columns_with_pii.length}</div>
            <div class="stat-label">At Risk</div>
        </div>
    `;

    // Preview table
    const thead = document.getElementById('previewHead');
    const tbody = document.getElementById('previewBody');

    thead.innerHTML = '<tr>' + data_summary.columns.map(col =>
        `<th>${escapeHtml(col)}</th>`
    ).join('') + '</tr>';

    tbody.innerHTML = data_summary.preview.map(row =>
        '<tr>' + data_summary.columns.map(col =>
            `<td>${escapeHtml(String(row[col] ?? ''))}</td>`
        ).join('') + '</tr>'
    ).join('');

    // Update input placeholders with actual column names
    const nonPiiColumns = data_summary.columns.filter(col => !data.columns_with_pii.includes(col));
    const quasiExample = nonPiiColumns.filter(c => !['id'].includes(c.toLowerCase())).slice(0, 3).join(', ');
    const sensitiveExample = nonPiiColumns.find(c => ['salary', 'income', 'amount', 'price'].some(s => c.toLowerCase().includes(s))) || nonPiiColumns[nonPiiColumns.length - 1] || '';

    if (elements.quasiInput) {
        elements.quasiInput.placeholder = quasiExample || 'e.g., age, city, department';
    }
    if (elements.sensitiveInput) {
        elements.sensitiveInput.placeholder = sensitiveExample || 'e.g., salary, diagnosis';
    }
}

function displayPIIResults(data) {
    const { pii_detected } = data;
    const piiGrid = document.getElementById('piiGrid');

    document.getElementById('piiCount').textContent = `${data.pii_count} THREATS`;

    if (Object.keys(pii_detected).length === 0) {
        piiGrid.innerHTML = '<p class="text-muted" style="text-align: center; padding: 2rem;">No PII detected in dataset</p>';
        return;
    }

    piiGrid.innerHTML = Object.entries(pii_detected).map(([col, info]) => `
        <div class="pii-item">
            <div class="pii-type">${escapeHtml(col)}</div>
            <div class="pii-details">
                <div>${info.count} instances detected</div>
                <div style="margin-top: 0.5rem; opacity: 0.7;">Types: ${info.types.join(', ')}</div>
            </div>
        </div>
    `).join('');
}

// ─────────────────────────────────────────────────────────────────────────────
// Config Handlers
// ─────────────────────────────────────────────────────────────────────────────
function setupConfigHandlers() {
    const { epsilonSlider, epsilonValue, sliderFill } = elements;

    const updateSlider = () => {
        const value = epsilonSlider.value;
        const percent = ((value - 0.1) / (5 - 0.1)) * 100;
        epsilonValue.textContent = value;
        sliderFill.style.width = percent + '%';
    };

    epsilonSlider.addEventListener('input', updateSlider);
    updateSlider(); // Initial state
}

// ─────────────────────────────────────────────────────────────────────────────
// Analysis Handlers
// ─────────────────────────────────────────────────────────────────────────────
function setupAnalysisHandlers() {
    elements.analyzeBtn.addEventListener('click', runAnalysis);
    elements.downloadReportBtn.addEventListener('click', downloadReport);
}

async function runAnalysis() {
    if (!state.sessionId) {
        showNotification('Please upload data first', 'warning');
        return;
    }

    if (state.isAnalyzing) return;
    state.isAnalyzing = true;

    const btn = elements.analyzeBtn;
    const originalContent = btn.innerHTML;
    btn.innerHTML = `
        <span class="btn-icon" style="animation: pulse 1s infinite;">◉</span>
        <span class="btn-text">ANALYZING...</span>
    `;
    btn.disabled = true;

    const params = new URLSearchParams({
        session_id: state.sessionId,
        epsilon: elements.epsilonSlider.value,
        anonymization_strategy: elements.strategySelect.value,
        quasi_identifiers: elements.quasiInput.value,
        sensitive_attribute: elements.sensitiveInput.value
    });

    try {
        const response = await fetch(`/api/v1/analyze?${params}`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Analysis failed');

        const results = await response.json();
        displayResults(results);
        showSection(elements.resultsSection, 0);

        // Scroll to results
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Analysis failed. Please try again.', 'error');
    } finally {
        btn.innerHTML = originalContent;
        btn.disabled = false;
        state.isAnalyzing = false;
    }
}

function displayResults(results) {
    // Privacy Metrics
    const { privacy_metrics } = results;
    document.getElementById('privacyMetrics').innerHTML = `
        <div class="metric-card">
            <div class="metric-value">${privacy_metrics.epsilon}</div>
            <div class="metric-label">Epsilon (ε)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${privacy_metrics.k_anonymity}</div>
            <div class="metric-label">k-Anonymity</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${privacy_metrics.l_diversity}</div>
            <div class="metric-label">l-Diversity</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${privacy_metrics.delta}</div>
            <div class="metric-label">Delta (δ)</div>
        </div>
    `;

    // Budget
    const budgetUsed = (privacy_metrics.budget_used / privacy_metrics.epsilon * 100) || 0;
    document.getElementById('budgetFill').style.width = Math.min(budgetUsed, 100) + '%';
    document.getElementById('budgetPercent').textContent = budgetUsed.toFixed(1) + '%';
    document.getElementById('budgetText').textContent =
        `${privacy_metrics.budget_used.toFixed(3)} / ${privacy_metrics.epsilon} epsilon consumed`;

    // Risk Assessment
    const risk = results.risk_assessment?.overall || {};
    const riskLevel = risk.risk_level || 'Unknown';
    const riskClass = riskLevel.toLowerCase().replace(' ', '-');
    document.getElementById('riskDisplay').innerHTML = `
        <div class="risk-card">
            <div class="risk-level ${riskClass}">${riskLevel.toUpperCase()}</div>
            <div class="metric-label">Re-identification Risk</div>
        </div>
    `;

    // DP Statistics (if any)
    if (results.dp_statistics && Object.keys(results.dp_statistics).length > 0) {
        const dpStatsHtml = Object.entries(results.dp_statistics).map(([col, stats]) => `
            <div class="stat-card">
                <div class="stat-value">${stats.private_mean}</div>
                <div class="stat-label">${escapeHtml(col)} (DP Mean)</div>
            </div>
        `).join('');

        // Insert DP stats after risk display
        const riskDisplay = document.getElementById('riskDisplay');
        const dpSection = document.createElement('div');
        dpSection.className = 'dp-stats-section';
        dpSection.innerHTML = `
            <h4 style="margin-top: 1.5rem; margin-bottom: 1rem; font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); letter-spacing: 0.1em;">DIFFERENTIALLY PRIVATE STATISTICS</h4>
            <div class="stats-grid">${dpStatsHtml}</div>
        `;
        riskDisplay.parentNode.insertBefore(dpSection, riskDisplay.nextSibling);
    }

    // Compliance
    const complianceGrid = document.getElementById('complianceGrid');
    const compliance = results.compliance || {};
    complianceGrid.innerHTML = Object.entries(compliance)
        .filter(([key]) => key !== 'overall_compliant')
        .map(([reg, data]) => {
            if (typeof data !== 'object') return '';
            const statusClass = data.status === 'Compliant' ? 'badge-success' :
                data.status?.includes('Partial') ? 'badge-warning' : 'badge-danger';
            const scoreColor = data.score >= 80 ? 'var(--success)' :
                data.score >= 60 ? 'var(--warning)' : 'var(--danger)';
            return `
                <div class="compliance-item">
                    <div class="compliance-name">${reg.toUpperCase()}</div>
                    <div class="compliance-score" style="color: ${scoreColor}">${data.score}/100</div>
                    <span class="badge ${statusClass}">${data.status}</span>
                </div>
            `;
        }).join('');

    // Anonymized Preview
    if (results.anonymized_preview && results.anonymized_preview.length > 0) {
        const cols = Object.keys(results.anonymized_preview[0]);
        document.getElementById('anonHead').innerHTML = '<tr>' +
            cols.map(col => `<th>${escapeHtml(col)}</th>`).join('') + '</tr>';
        document.getElementById('anonBody').innerHTML = results.anonymized_preview.map(row =>
            '<tr>' + cols.map(col => `<td>${escapeHtml(String(row[col] ?? ''))}</td>`).join('') + '</tr>'
        ).join('');
    }
}

async function downloadReport() {
    if (!state.sessionId) return;

    try {
        window.open(`/api/v1/generate-report?session_id=${state.sessionId}`, '_blank');
    } catch (error) {
        console.error('Report generation error:', error);
        showNotification('Failed to generate report', 'error');
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Animations & Effects
// ─────────────────────────────────────────────────────────────────────────────
function setupAnimations() {
    // Staggered title animation
    const titleLines = document.querySelectorAll('.title-line');
    titleLines.forEach((line, index) => {
        line.style.opacity = '0';
        line.style.transform = 'translateY(30px)';
        setTimeout(() => {
            line.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            line.style.opacity = '1';
            line.style.transform = 'translateY(0)';
        }, 200 + index * 150);
    });

    // Hero description fade in
    const heroDesc = document.querySelector('.hero-description');
    if (heroDesc) {
        heroDesc.style.opacity = '0';
        setTimeout(() => {
            heroDesc.style.transition = 'opacity 0.8s ease';
            heroDesc.style.opacity = '1';
        }, 600);
    }

    // Upload zone fade in
    const uploadZone = document.querySelector('.upload-zone');
    if (uploadZone) {
        uploadZone.style.opacity = '0';
        uploadZone.style.transform = 'translateY(20px)';
        setTimeout(() => {
            uploadZone.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            uploadZone.style.opacity = '1';
            uploadZone.style.transform = 'translateY(0)';
        }, 400);
    }
}

function showSection(section, delay = 0) {
    setTimeout(() => {
        section.classList.remove('hidden');
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        requestAnimationFrame(() => {
            section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        });
    }, delay);
}

// ─────────────────────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'error' ? 'rgba(255, 51, 102, 0.9)' :
            type === 'warning' ? 'rgba(255, 184, 0, 0.9)' :
                'rgba(0, 240, 255, 0.9)'};
        color: ${type === 'error' || type === 'warning' ? '#000' : '#fff'};
        border-radius: 8px;
        font-family: var(--font-mono);
        font-size: 0.85rem;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
