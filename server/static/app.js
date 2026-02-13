// ---- State ----

let editor = null;
let problemData = null;
let currentLanguage = null;
let running = false;

// Per-language editor content (in-memory, survives language switching)
const editorState = {};

// Monaco language mode mapping
const MONACO_LANG = {
    python: 'python',
    java: 'java',
};

// Verdict display config
const VERDICT_LABELS = {
    passed: 'PASS',
    failed: 'FAIL',
    time_limit_exceeded: 'TLE',
    memory_limit_exceeded: 'MLE',
    runtime_error: 'RTE',
};

const VERDICT_CSS = {
    passed: 'verdict-passed',
    failed: 'verdict-failed',
    time_limit_exceeded: 'verdict-tle',
    memory_limit_exceeded: 'verdict-mle',
    runtime_error: 'verdict-rte',
};

// ---- Initialization ----

require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs' } });

require(['vs/editor/editor.main'], function () {
    editor = monaco.editor.create(document.getElementById('editor-container'), {
        value: '',
        language: 'python',
        theme: 'vs',
        minimap: { enabled: false },
        automaticLayout: true,
        fontSize: 14,
        scrollBeyondLastLine: false,
    });

    // Override Ctrl+S to save
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function () {
        saveSolution();
    });

    loadProblem();
});

// ---- API helpers ----

async function api(method, path, body) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body !== undefined) {
        opts.body = JSON.stringify(body);
    }
    const resp = await fetch(path, opts);
    if (!resp.ok) {
        const detail = await resp.json().catch(() => ({}));
        throw new Error(detail.detail || `HTTP ${resp.status}`);
    }
    return resp.json();
}

// ---- Problem loading ----

async function loadProblem() {
    try {
        problemData = await api('GET', '/api/problem');
    } catch (e) {
        document.getElementById('problem-description').innerHTML =
            '<p style="color:red">Failed to load problem: ' + e.message + '</p>';
        return;
    }

    // Render problem description
    document.getElementById('problem-description').innerHTML = problemData.description_html;

    // Populate language selector
    const select = document.getElementById('language-select');
    select.innerHTML = '';
    for (const lang of problemData.languages) {
        const opt = document.createElement('option');
        opt.value = lang.name;
        opt.textContent = lang.name.charAt(0).toUpperCase() + lang.name.slice(1);
        select.appendChild(opt);
    }

    // Select first language and load its solution
    if (problemData.languages.length > 0) {
        select.value = problemData.languages[0].name;
        await switchLanguage(problemData.languages[0].name);
    }
}

// ---- Language switching ----

async function switchLanguage(lang) {
    // Save current editor content in memory before switching
    if (currentLanguage && editor) {
        editorState[currentLanguage] = editor.getValue();
    }

    currentLanguage = lang;

    // If we have in-memory state for this language, restore it
    if (editorState[lang] !== undefined) {
        editor.setValue(editorState[lang]);
    } else {
        // Load from server (saved solution or stub)
        try {
            const data = await api('GET', '/api/solution/' + lang);
            editor.setValue(data.code);
            editorState[lang] = data.code;
        } catch (e) {
            // Fall back to stub from problem data
            const langData = problemData.languages.find(l => l.name === lang);
            const stub = langData ? langData.stub : '';
            editor.setValue(stub);
            editorState[lang] = stub;
        }
    }

    // Set Monaco language mode
    const model = editor.getModel();
    monaco.editor.setModelLanguage(model, MONACO_LANG[lang] || 'plaintext');

    // Clear results when switching languages
    document.getElementById('results-content').innerHTML = '';
}

// ---- Test execution ----

async function runTests() {
    if (running || !currentLanguage) return;

    running = true;
    const btn = document.getElementById('btn-run');
    btn.disabled = true;
    btn.textContent = 'Running...';

    const resultsEl = document.getElementById('results-content');
    resultsEl.innerHTML = '<div class="results-loading">Running tests...</div>';

    const code = editor.getValue();

    try {
        const result = await api('POST', '/api/run', {
            language: currentLanguage,
            code: code,
        });
        renderResults(result);
    } catch (e) {
        resultsEl.innerHTML = '<div class="results-error">Error: ' + escapeHtml(e.message) + '</div>';
    } finally {
        running = false;
        btn.disabled = false;
        btn.textContent = 'Run';
    }
}

function renderResults(result) {
    const el = document.getElementById('results-content');

    if (result.status === 'build_error') {
        el.innerHTML =
            '<div class="results-summary">BUILD ERROR</div>' +
            '<div class="results-error">' + escapeHtml(result.stderr || 'Unknown build error') + '</div>';
        return;
    }

    if (result.status === 'timeout') {
        el.innerHTML = '<div class="results-summary">TIMEOUT</div>' +
            '<div class="results-error">The test command exceeded the time limit.</div>';
        return;
    }

    if (result.status === 'runtime_error') {
        el.innerHTML =
            '<div class="results-summary">RUNTIME ERROR</div>' +
            '<div class="results-error">' + escapeHtml(result.stderr || 'Process killed') + '</div>';
        return;
    }

    const summary = result.summary;
    let html = '<div class="results-summary">' +
        summary.passed + '/' + summary.total + ' passed (' + summary.time_seconds + 's)</div>';

    for (const test of result.tests) {
        // Per-test mode (has verdict)
        if (test.verdict) {
            const label = VERDICT_LABELS[test.verdict] || test.verdict.toUpperCase();
            const css = VERDICT_CSS[test.verdict] || '';

            html += '<div class="result-row">' +
                '<span class="verdict ' + css + '">' + label + '</span>' +
                '<span>' + escapeHtml(test.name) + '</span>' +
                '<span class="result-meta">(' + test.time_seconds + 's, ' + test.memory_mb + 'MB)</span>' +
                '</div>';

            if (test.message) {
                html += '<div class="result-message collapsed" onclick="this.classList.toggle(\'collapsed\')">' +
                    escapeHtml(test.message) + '</div>';
            }
        }
        // Batch mode (has passed boolean)
        else {
            const label = test.passed ? 'PASS' : 'FAIL';
            const css = test.passed ? 'verdict-passed' : 'verdict-failed';

            html += '<div class="result-row">' +
                '<span class="verdict ' + css + '">' + label + '</span>' +
                '<span>' + escapeHtml(test.name) + '</span>' +
                '<span class="result-meta">(' + test.time_seconds + 's)</span>' +
                '</div>';

            if (!test.passed && test.message) {
                html += '<div class="result-message collapsed" onclick="this.classList.toggle(\'collapsed\')">' +
                    escapeHtml(test.message) + '</div>';
            }
        }
    }

    el.innerHTML = html;
}

// ---- Solution persistence ----

async function saveSolution() {
    if (!currentLanguage) return;

    const code = editor.getValue();
    const btn = document.getElementById('btn-save');

    try {
        await api('PUT', '/api/solution/' + currentLanguage, { code });
        editorState[currentLanguage] = code;
        btn.textContent = 'Saved!';
        setTimeout(() => { btn.textContent = 'Save'; }, 1500);
    } catch (e) {
        btn.textContent = 'Error';
        setTimeout(() => { btn.textContent = 'Save'; }, 1500);
    }
}

async function resetSolution() {
    if (!currentLanguage) return;
    if (!confirm('Reset to the original stub? Your saved solution for ' + currentLanguage + ' will be deleted.')) {
        return;
    }

    try {
        await api('DELETE', '/api/solution/' + currentLanguage);
    } catch (e) {
        // Ignore delete errors — stub fallback still works
    }

    // Reload stub
    const langData = problemData.languages.find(l => l.name === currentLanguage);
    const stub = langData ? langData.stub : '';
    editor.setValue(stub);
    editorState[currentLanguage] = stub;
}

// ---- Event listeners ----

document.getElementById('language-select').addEventListener('change', function () {
    switchLanguage(this.value);
});

document.getElementById('btn-run').addEventListener('click', runTests);
document.getElementById('btn-save').addEventListener('click', saveSolution);
document.getElementById('btn-reset').addEventListener('click', resetSolution);

// ---- Utilities ----

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
