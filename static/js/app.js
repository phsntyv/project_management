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
        renderTable(data.columns, data.rows);
        preview.classList.remove('hidden');
    } catch (err) {
        showMessage(`Erreur : ${err.message}`, 'error');
    }
});
