/**
 * Privacy-Preserving Data Analyzer - Main JavaScript
 */

// State
let sessionId = null;
let currentData = null;

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const uploadStatus = document.getElementById('uploadStatus');

const uploadSection = document.getElementById('uploadSection');
const previewSection = document.getElementById('previewSection');
const piiSection = document.getElementById('piiSection');
const configSection = document.getElementById('configSection');
const resultsSection = document.getElementById('resultsSection');

const epsilonSlider = document.getElementById('epsilonSlider');
const epsilonValue = document.getElementById('epsilonValue');
const analyzeBtn = document.getElementById('analyzeBtn');
const downloadReportBtn = document.getElementById('downloadReportBtn');

// Event Listeners
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupUploadHandlers();
    setupConfigHandlers();
    setupAnalysisHandlers();
}

// Upload Handlers
function setupUploadHandlers() {
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
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

    // File input
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    // Validate
    const allowedTypes = ['.csv', '.json', '.xlsx', '.xls'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(ext)) {
        alert('Please upload a CSV, JSON, or Excel file.');
        return;
    }

    // Show progress
    uploadProgress.classList.remove('hidden');
    progressFill.style.width = '0%';
    uploadStatus.textContent = 'Uploading...';

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Animate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 10, 90);
            progressFill.style.width = progress + '%';
        }, 100);

        // Upload
        const response = await fetch('/api/v1/upload', {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);
        progressFill.style.width = '100%';

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        sessionId = data.session_id;
        currentData = data;

        uploadStatus.textContent = 'Upload complete!';

        // Show sections
        setTimeout(() => {
            displayDataPreview(data);
            displayPIIResults(data);
            showSection(previewSection);
            showSection(piiSection);
            showSection(configSection);
        }, 500);

    } catch (error) {
        console.error('Upload error:', error);
        uploadStatus.textContent = 'Upload failed. Please try again.';
        progressFill.style.width = '0%';
    }
}

function displayDataPreview(data) {
    const { data_summary } = data;

    // Row count badge
    document.getElementById('rowCount').textContent = `${data_summary.row_count} rows`;

    // Metrics
    const metricsGrid = document.getElementById('dataMetrics');
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <div class="metric-value">${data_summary.row_count}</div>
            <div class="metric-label">Records</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${data_summary.column_count}</div>
            <div class="metric-label">Columns</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${data.pii_count}</div>
            <div class="metric-label">PII Detected</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${data.columns_with_pii.length}</div>
            <div class="metric-label">Columns with PII</div>
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
}

function displayPIIResults(data) {
    const { pii_detected } = data;
    const piiGrid = document.getElementById('piiGrid');

    document.getElementById('piiCount').textContent = `${data.pii_count} PII found`;

    if (Object.keys(pii_detected).length === 0) {
        piiGrid.innerHTML = '<p class="text-muted">No PII detected</p>';
        return;
    }

    piiGrid.innerHTML = Object.entries(pii_detected).map(([col, info]) => `
        <div class="pii-item">
            <div class="pii-type">${escapeHtml(col)}</div>
            <div class="text-small text-muted">
                ${info.count} instances<br>
                Types: ${info.types.join(', ')}
            </div>
        </div>
    `).join('');
}

// Config Handlers
function setupConfigHandlers() {
    epsilonSlider.addEventListener('input', (e) => {
        epsilonValue.textContent = e.target.value;
    });
}

// Analysis Handlers
function setupAnalysisHandlers() {
    analyzeBtn.addEventListener('click', runAnalysis);
    downloadReportBtn.addEventListener('click', downloadReport);
}

async function runAnalysis() {
    if (!sessionId) {
        alert('Please upload data first');
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '🔄 Analyzing...';

    const params = new URLSearchParams({
        session_id: sessionId,
        epsilon: epsilonSlider.value,
        anonymization_strategy: document.getElementById('strategySelect').value,
        quasi_identifiers: document.getElementById('quasiInput').value,
        sensitive_attribute: document.getElementById('sensitiveInput').value
    });

    try {
        const response = await fetch(`/api/v1/analyze?${params}`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Analysis failed');

        const results = await response.json();
        displayResults(results);
        showSection(resultsSection);

    } catch (error) {
        console.error('Analysis error:', error);
        alert('Analysis failed. Please try again.');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔒 Analyze with Privacy Protection';
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
    document.getElementById('budgetFill').style.width = budgetUsed + '%';
    document.getElementById('budgetText').textContent =
        `Budget: ${budgetUsed.toFixed(1)}% used (${privacy_metrics.budget_used}/${privacy_metrics.epsilon})`;

    // Risk Assessment
    const risk = results.risk_assessment?.overall || {};
    document.getElementById('riskDisplay').innerHTML = `
        <div class="metric-card">
            <div class="metric-value">${risk.risk_level || 'N/A'}</div>
            <div class="metric-label">Risk Level</div>
        </div>
    `;

    // Compliance
    const complianceGrid = document.getElementById('complianceGrid');
    const compliance = results.compliance || {};
    complianceGrid.innerHTML = Object.entries(compliance)
        .filter(([key]) => key !== 'overall_compliant')
        .map(([reg, data]) => {
            if (typeof data !== 'object') return '';
            const statusClass = data.status === 'Compliant' ? 'badge-success' :
                data.status?.includes('Partial') ? 'badge-warning' : 'badge-danger';
            return `
                <div class="compliance-item">
                    <div class="compliance-name">${reg.toUpperCase()}</div>
                    <div class="compliance-score">${data.score}/100</div>
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
    if (!sessionId) return;

    try {
        window.open(`/api/v1/generate-report?session_id=${sessionId}`, '_blank');
    } catch (error) {
        console.error('Report generation error:', error);
    }
}

// Utilities
function showSection(section) {
    section.classList.remove('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
