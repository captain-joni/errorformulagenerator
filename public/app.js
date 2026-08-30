// Fehlerformel Generator -- frontend logic.
// Talks to the FastAPI backend (app/main.py) over three JSON endpoints:
//   POST /api/preview        { formula } -> { latex, variables: [{name, is_known_constant, ...}] }
//   POST /api/differentiate  { formula, variables } -> { original_latex, latex, python_equation }
//   POST /api/calc           { formula, error_formula, values } -> { value, error, formatted }
//
// The variable panel is generated entirely from `variables` in the preview
// response -- the user never types a variable name, only ticks checkboxes
// and fills in numbers.

const STORAGE_KEY = 'efg.state.v2';

// ---------- small helpers ----------

function debounce(fn, delayMs) {
    let handle;
    return (...args) => {
        clearTimeout(handle);
        handle = setTimeout(() => fn(...args), delayMs);
    };
}

function showError(message) {
    const banner = document.getElementById('error-banner');
    if (!message) {
        banner.hidden = true;
        banner.textContent = '';
        return;
    }
    banner.hidden = false;
    banner.textContent = message;
}

async function postJSON(url, body) {
    let response;
    try {
        response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
    } catch {
        throw new Error('Server nicht erreichbar. Läuft der Server?');
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.detail || `Fehler (${response.status})`);
    }
    return data;
}

function renderLatex(container, latex) {
    container.textContent = `$$${latex}$$`;
    if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([container]);
    }
}

async function copyToClipboard(text, button) {
    if (!text) {
        showError('Nichts zum Kopieren vorhanden.');
        return;
    }
    let copied = false;
    try {
        await navigator.clipboard.writeText(text);
        copied = true;
    } catch {
        // Fallback for browsers/contexts without the async Clipboard API (e.g. non-HTTPS)
        const tmp = document.createElement('textarea');
        tmp.value = text;
        tmp.style.position = 'fixed';
        tmp.style.opacity = '0';
        document.body.appendChild(tmp);
        tmp.focus();
        tmp.select();
        try {
            copied = document.execCommand('copy');
        } catch {
            copied = false;
        }
        document.body.removeChild(tmp);
    }

    if (!copied) {
        showError('Automatisches Kopieren nicht verfügbar -- bitte manuell markieren und kopieren (Strg+C).');
        return;
    }
    if (button) {
        const original = button.textContent;
        button.textContent = 'Kopiert!';
        setTimeout(() => { button.textContent = original; }, 1200);
    }
}

function formatNumber(n) {
    if (n === null || n === undefined) return '';
    const num = Number(n);
    if (!Number.isFinite(num)) return String(num);
    const [mantissa, exponent] = num.toPrecision(10).split('e');
    const trimmed = mantissa.includes('.') ? mantissa.replace(/0+$/, '').replace(/\.$/, '') : mantissa;
    return exponent !== undefined ? `${trimmed}e${exponent}` : trimmed;
}

// ---------- persistence (per-viewer convenience, not synced anywhere) ----------

function loadState() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
        return {};
    }
}

function saveState(patch) {
    try {
        const state = loadState();
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...state, ...patch }));
    } catch {
        // localStorage unavailable (private mode, etc.) -- just skip persistence
    }
}

function savePerVariable(name, patch) {
    const state = loadState();
    const perVariable = state.perVariable || {};
    perVariable[name] = { ...perVariable[name], ...patch };
    saveState({ perVariable });
}

// ---------- variable panel ----------

let currentVariables = []; // last list of {name, is_known_constant, constant_value, constant_label, constant_unit}

function buildVariableRow(info) {
    const state = loadState();
    const overrides = new Set(state.overrides || []);
    const saved = (state.perVariable || {})[info.name] || {};
    const treatAsConstant = info.is_known_constant && !overrides.has(info.name);

    const row = document.createElement('div');
    row.className = 'var-row' + (treatAsConstant ? ' var-row--constant' : '');
    row.dataset.variable = info.name;

    if (treatAsConstant) {
        row.innerHTML = `
            <div class="const-info">
                <span class="var-name">${info.name}</span>
                <span class="const-label">${info.constant_label}</span>
                <span class="const-value">${formatNumber(info.constant_value)}${info.constant_unit ? ' ' + info.constant_unit : ''}</span>
            </div>
            <button type="button" class="link-button" data-action="use-as-variable">als Variable verwenden</button>
        `;
        row.querySelector('[data-action="use-as-variable"]').addEventListener('click', () => {
            const s = loadState();
            const ov = new Set(s.overrides || []);
            ov.add(info.name);
            saveState({ overrides: [...ov] });
            renderVariablePanel();
        });
        return row;
    }

    row.innerHTML = `
        <span class="var-name">${info.name}</span>
        <label class="var-check">
            <input type="checkbox" data-role="error-toggle" />
            fehlerbehaftet
        </label>
        <input type="text" inputmode="decimal" data-role="value" placeholder="Wert" />
        <input type="text" inputmode="decimal" data-role="error" placeholder="Δ${info.name}" disabled />
        ${info.is_known_constant ? '<button type="button" class="link-button" data-action="use-as-constant">als Konstante behandeln</button>' : ''}
    `;

    const checkbox = row.querySelector('[data-role="error-toggle"]');
    const valueInput = row.querySelector('[data-role="value"]');
    const errorInput = row.querySelector('[data-role="error"]');

    checkbox.checked = Boolean(saved.errorCarrying);
    errorInput.disabled = !checkbox.checked;
    valueInput.value = saved.value ?? '';
    errorInput.value = saved.error ?? '';

    checkbox.addEventListener('change', () => {
        errorInput.disabled = !checkbox.checked;
        savePerVariable(info.name, { errorCarrying: checkbox.checked });
    });
    valueInput.addEventListener('input', () => savePerVariable(info.name, { value: valueInput.value }));
    errorInput.addEventListener('input', () => savePerVariable(info.name, { error: errorInput.value }));

    const constantButton = row.querySelector('[data-action="use-as-constant"]');
    if (constantButton) {
        constantButton.addEventListener('click', () => {
            const s = loadState();
            const ov = new Set(s.overrides || []);
            ov.delete(info.name);
            saveState({ overrides: [...ov] });
            renderVariablePanel();
        });
    }

    return row;
}

function renderVariablePanel() {
    const panel = document.getElementById('variable-panel');
    panel.innerHTML = '';
    if (currentVariables.length === 0) {
        panel.innerHTML = '<p class="empty-hint">Noch keine Formel erkannt.</p>';
        return;
    }
    currentVariables.forEach((info) => panel.appendChild(buildVariableRow(info)));
}

function collectValuesForCalc() {
    const state = loadState();
    const overrides = new Set(state.overrides || []);
    const values = {};

    currentVariables.forEach((info) => {
        if (info.is_known_constant && !overrides.has(info.name)) {
            values[info.name] = { value: String(info.constant_value), error: '0' };
            return;
        }
        const row = document.querySelector(`.var-row[data-variable="${CSS.escape(info.name)}"]`);
        if (!row) return;
        const value = row.querySelector('[data-role="value"]').value;
        const checked = row.querySelector('[data-role="error-toggle"]').checked;
        const error = checked ? row.querySelector('[data-role="error"]').value : '0';
        values[info.name] = { value, error };
    });
    return values;
}

function collectErrorCarryingVariables() {
    const state = loadState();
    const overrides = new Set(state.overrides || []);
    return currentVariables
        .filter((info) => !(info.is_known_constant && !overrides.has(info.name)))
        .filter((info) => {
            const row = document.querySelector(`.var-row[data-variable="${CSS.escape(info.name)}"]`);
            return row && row.querySelector('[data-role="error-toggle"]').checked;
        })
        .map((info) => info.name);
}

// ---------- state used between the "differentiate" and "calc" steps ----------

let currentErrorEquation = '';
let currentPreviewLatex = '';
let currentErrorLatex = '';

// ---------- actions ----------

async function runPreview() {
    const formula = document.getElementById('formula').value;
    const previewBox = document.getElementById('latex-output_2');
    if (!formula.trim()) {
        previewBox.textContent = '';
        currentPreviewLatex = '';
        currentVariables = [];
        renderVariablePanel();
        return;
    }
    try {
        const data = await postJSON('/api/preview', { formula });
        renderLatex(previewBox, data.latex);
        currentPreviewLatex = data.latex;
        currentVariables = data.variables;
        renderVariablePanel();
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

async function runDifferentiate() {
    const formula = document.getElementById('formula').value;
    const variables = collectErrorCarryingVariables();

    if (variables.length === 0) {
        showError('Bitte mindestens eine Größe als fehlerbehaftet ankreuzen.');
        return;
    }

    try {
        const data = await postJSON('/api/differentiate', { formula, variables });
        currentErrorEquation = data.python_equation;
        currentErrorLatex = data.latex;

        document.getElementById('error-formula-card').hidden = false;
        renderLatex(document.getElementById('latex-output'), data.latex);
        document.getElementById('python-equation').value = data.python_equation;
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

async function runCalc() {
    if (!currentErrorEquation) {
        showError('Bitte zuerst die Fehlerformel berechnen (Schritt 2).');
        return;
    }

    const formula = document.getElementById('formula').value;
    const values = collectValuesForCalc();

    try {
        const data = await postJSON('/api/calc', {
            formula,
            error_formula: currentErrorEquation,
            values,
        });
        document.getElementById('losung').textContent = `Ergebnis: ${data.formatted}`;
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

// ---------- wiring ----------

document.getElementById('formula').addEventListener('input', debounce(() => {
    saveState({ formula: document.getElementById('formula').value });
    document.getElementById('error-formula-card').hidden = true;
    currentErrorEquation = '';
    runPreview();
}, 400));

document.getElementById('fehlerformel').addEventListener('click', runDifferentiate);
document.getElementById('ausrechnen').addEventListener('click', runCalc);

document.getElementById('copy-equation').addEventListener('click', (e) => {
    copyToClipboard(document.getElementById('python-equation').value, e.currentTarget);
});
document.getElementById('copy-latex-preview').addEventListener('click', (e) => {
    copyToClipboard(currentPreviewLatex && `$$${currentPreviewLatex}$$`, e.currentTarget);
});
document.getElementById('copy-latex-error').addEventListener('click', (e) => {
    copyToClipboard(currentErrorLatex && `$$${currentErrorLatex}$$`, e.currentTarget);
});

// ---------- restore persisted state on load ----------

(function restore() {
    const state = loadState();
    if (state.formula) {
        document.getElementById('formula').value = state.formula;
        runPreview();
    }
})();
