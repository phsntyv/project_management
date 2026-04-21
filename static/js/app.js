const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file');
const fileName = document.getElementById('file-name');
const messageEl = document.getElementById('message');
const preview = document.getElementById('preview');
const metaFile = document.getElementById('meta-file');
const metaCount = document.getElementById('meta-count');
const thead = document.querySelector('#data-table thead');
const tbody = document.querySelector('#data-table tbody');

fileInput.addEventListener('change', () => {
    fileName.textContent = fileInput.files[0]?.name || 'Choisir un fichier CSV…';
});

function showMessage(text, type) {
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
}

function renderQualityReport(report) {
    const reportEl = document.getElementById('quality-report');
    const titleEl = document.getElementById('report-title');
    const summaryEl = document.getElementById('report-summary');
    const detailsEl = document.getElementById('report-details');

    titleEl.textContent = report.status;
    summaryEl.innerHTML = `
        <strong>📊 ${report.summary}</strong><br/>
        📈 Lignes affectées: ${report.affected_rows}/${report.total_rows}
    `;

    if (report.total_anomalies === 0) {
        detailsEl.innerHTML = '<p class="success">✅ Aucune anomalie détectée.</p>';
        reportEl.classList.remove('hidden');
        return;
    }

    let html = '<div class="anomaly-summary">';
    if (report.anomalies_by_type.null > 0) {
        html += `<p>🔴 Valeurs manquantes: ${report.anomalies_by_type.null}</p>`;
    }
    if (report.anomalies_by_type.inconsistency > 0) {
        html += `<p>🟠 Incohérences: ${report.anomalies_by_type.inconsistency}</p>`;
    }
    if (report.anomalies_by_type.outlier > 0) {
        html += `<p>🟡 Valeurs aberrantes: ${report.anomalies_by_type.outlier}</p>`;
    }
    html += '</div>';

    if (Object.keys(report.anomalies_by_row).length > 0) {
        html += '<details><summary>🔍 Afficher les détails</summary><ul>';
        for (const [rowId, anomalies] of Object.entries(report.anomalies_by_row)) {
            html += `<li><strong>Row #${rowId}:</strong><ul>`;
            for (const anom of anomalies) {
                const icon = {'null': '❌', 'inconsistency': '⚠️', 'outlier': '⚡'}[anom.type] || '•';
                html += `<li>${icon} <strong>${anom.column}:</strong> ${anom.message}</li>`;
            }
            html += '</ul></li>';
        }
        html += '</ul></details>';
    }

    detailsEl.innerHTML = html;
    reportEl.classList.remove('hidden');
}

function renderTable(columns, rows) {
    thead.innerHTML = '<tr>' + columns.map(c => `<th>${escapeHtml(c)}</th>`).join('') + '</tr>';
    tbody.innerHTML = rows.map(row => {
        let cells = columns.map(c => {
            if (c === 'Catégorie') {
                const categorie = row._categorie;
                const categoryClass = {
                    'VIP': 'category-vip',
                    'Loyal': 'category-loyal',
                    'Actif': 'category-actif',
                    'À risque': 'category-risk',
                    'Churned': 'category-churned',
                    'Prospect': 'category-prospect'
                }[categorie] || 'category-default';
                return `<td><span class="category ${categoryClass}">${escapeHtml(categorie)}</span></td>`;
            }
            if (c === 'Recommandation') {
                const rec = row._recommandation;
                return `<td><span class="recommendation recommendation-${rec.priority}">${escapeHtml(rec.text)}</span></td>`;
            }
            return `<td>${escapeHtml(row[c] ?? '')}</td>`;
        }).join('');
        return '<tr>' + cells + '</tr>';
    }).join('');
}

function escapeHtml(v) {
    return String(v)
        .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!fileInput.files[0]) return;

    const fd = new FormData();
    fd.append('file', fileInput.files[0]);

    showMessage('Envoi en cours…', 'success');

    try {
        const res = await fetch('/api/upload', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Erreur serveur');

        showMessage(data.message, 'success');
        metaFile.textContent = fileInput.files[0].name;
        metaCount.textContent = `${data.row_count} lignes · ${data.columns.length} colonnes`;

        if (data.quality_report) {
            renderQualityReport(data.quality_report);
        }

        renderTable(data.columns, data.rows);
        preview.classList.remove('hidden');
    } catch (err) {
        showMessage(`Erreur : ${err.message}`, 'error');
    }
});
