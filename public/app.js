// Fehlerformel Generator -- frontend logic.
// Talks to the FastAPI backend (app/main.py) over the three JSON endpoints:
//   POST /api/preview        { formula } -> { latex }
//   POST /api/differentiate  { formula, variables } -> { original_latex, latex, python_equation }
//   POST /api/calc           { formula, error_formula, values } -> { value, error, formatted }

const STORAGE_KEY = 'efg.state.v1';

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
    } catch (networkError) {
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

// ---------- dynamic per-variable value/error inputs ----------

function updateVariableInputs() {
    const variables = document.getElementById('variables').value.split(',').map((v) => v.trim());
    const container = document.getElementById('variable-container');
    const state = loadState();
    const savedValues = state.varValues || {};
    container.innerHTML = '';

    variables.forEach((variable) => {
        if (!variable) return;

        const inputDiv = document.createElement('div');
        inputDiv.className = 'dynamic-input';

        const label = document.createElement('label');
        label.textContent = `Variable ${variable}:`;
        inputDiv.appendChild(label);

        const valueInput = document.createElement('input');
        valueInput.type = 'text';
        valueInput.dataset.role = 'value';
        valueInput.dataset.variable = variable;
        valueInput.placeholder = `Wert für ${variable}`;
        valueInput.value = savedValues[variable]?.value ?? '';
        inputDiv.appendChild(valueInput);

        const errorInput = document.createElement('input');
        errorInput.type = 'text';
        errorInput.dataset.role = 'error';
        errorInput.dataset.variable = variable;
        errorInput.placeholder = `Fehler für ${variable}`;
        errorInput.value = savedValues[variable]?.error ?? '';
        inputDiv.appendChild(errorInput);

        container.appendChild(inputDiv);
    });

    container.addEventListener('input', persistVariableValues);
}

function persistVariableValues() {
    const container = document.getElementById('variable-container');
    const varValues = {};
    container.querySelectorAll('input[data-variable]').forEach((input) => {
        const name = input.dataset.variable;
        varValues[name] = varValues[name] || { value: '', error: '' };
        varValues[name][input.dataset.role] = input.value;
    });
    saveState({ varValues });
}

function collectVariableValues() {
    const container = document.getElementById('variable-container');
    const values = {};
    container.querySelectorAll('input[data-variable]').forEach((input) => {
        const name = input.dataset.variable;
        values[name] = values[name] || { value: '', error: '0' };
        values[name][input.dataset.role] = input.value;
    });
    return values;
}

// ---------- state used between the "differentiate" and "calc" steps ----------

let currentErrorEquation = '';

// ---------- actions ----------

async function runPreview() {
    const formula = document.getElementById('formula').value;
    const container = document.getElementById('latex-output_2');
    if (!formula.trim()) {
        container.textContent = '';
        return;
    }
    try {
        const data = await postJSON('/api/preview', { formula });
        renderLatex(container, data.latex);
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

async function runDifferentiate() {
    const formula = document.getElementById('formula').value;
    const variables = document.getElementById('variables_2').value.split(',').map((v) => v.trim()).filter(Boolean);

    try {
        const data = await postJSON('/api/differentiate', { formula, variables });
        currentErrorEquation = data.python_equation;

        renderLatex(document.getElementById('latex-output'), data.latex);
        document.getElementById('python-equation').value = data.python_equation;
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

async function runCalc() {
    if (!currentErrorEquation) {
        showError('Bitte zuerst die Fehlerformel berechnen (Button oben).');
        return;
    }

    const formula = document.getElementById('formula').value;
    const values = collectVariableValues();

    try {
        const data = await postJSON('/api/calc', {
            formula,
            error_formula: currentErrorEquation,
            values,
        });
        const resultDiv = document.getElementById('losung');
        resultDiv.textContent = `Ergebnis: ${data.formatted}`;
        showError('');
    } catch (err) {
        showError(err.message);
    }
}

async function copyEquation() {
    const field = document.getElementById('python-equation');
    if (!field.value) return;
    try {
        await navigator.clipboard.writeText(field.value);
        const button = document.getElementById('copy-equation');
        const original = button.textContent;
        button.textContent = 'Kopiert!';
        setTimeout(() => { button.textContent = original; }, 1200);
    } catch {
        field.select();
        showError('Automatisches Kopieren nicht verfügbar -- Text wurde markiert, bitte manuell kopieren (Strg+C).');
    }
}

// ---------- wiring ----------

document.getElementById('variables').addEventListener('input', () => {
    updateVariableInputs();
    saveState({ variables: document.getElementById('variables').value });
});

document.getElementById('formula').addEventListener('input', debounce(() => {
    saveState({ formula: document.getElementById('formula').value });
    runPreview();
}, 400));

document.getElementById('variables_2').addEventListener('input', () => {
    saveState({ variables2: document.getElementById('variables_2').value });
});

document.getElementById('tex-anzeigen').addEventListener('click', (e) => {
    e.preventDefault();
    runPreview();
});

document.getElementById('fehlerformel').addEventListener('click', (e) => {
    e.preventDefault();
    runDifferentiate();
});

document.getElementById('ausrechnen').addEventListener('click', (e) => {
    e.preventDefault();
    runCalc();
});

document.getElementById('copy-equation').addEventListener('click', copyEquation);

// ---------- restore persisted state on load ----------

(function restore() {
    const state = loadState();
    if (state.formula) document.getElementById('formula').value = state.formula;
    if (state.variables2) document.getElementById('variables_2').value = state.variables2;
    if (state.variables) {
        document.getElementById('variables').value = state.variables;
        updateVariableInputs();
    }
    if (state.formula) runPreview();
})();
