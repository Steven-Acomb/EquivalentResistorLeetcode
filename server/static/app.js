// ---- Theme ----

function getTheme() {
    return localStorage.getItem('theme') || 'dark';
}

function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const btn = document.getElementById('btn-theme');
    if (btn) btn.textContent = theme === 'dark' ? '\u2600' : '\u263E';
    if (editor) {
        monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
    }
}

function toggleTheme() {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', next);
    applyTheme(next);
}

// ---- State ----

let editor = null;
let problemData = null;
let currentLanguage = null;
let running = false;

// Apply theme immediately (before Monaco loads) to avoid flash
applyTheme(getTheme());

// Per-language editor content (in-memory, survives language switching)
const editorState = {};

// ---- File System Access API (native save) ----

const fileHandles = {};                              // per-language FileSystemFileHandle
const HAS_FILE_PICKER = 'showSaveFilePicker' in window;
const FILE_TYPES = {
    python: [{ description: 'Python files', accept: { 'text/x-python': ['.py'] } }],
    java:   [{ description: 'Java files',   accept: { 'text/x-java-source': ['.java'] } }],
};

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
        theme: getTheme() === 'dark' ? 'vs-dark' : 'vs',
        minimap: { enabled: false },
        automaticLayout: true,
        fontSize: 14,
        scrollBeyondLastLine: false,
    });

    // Override Ctrl+S to save
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function () {
        saveSolution();
    });

    // Override Ctrl+O to load
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyO, function () {
        loadSolution();
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
        const meta = getTestMeta(test.name);

        // Per-test mode (has verdict)
        if (test.verdict) {
            const label = VERDICT_LABELS[test.verdict] || test.verdict.toUpperCase();
            const css = VERDICT_CSS[test.verdict] || '';

            html += '<div class="result-row">' +
                '<span class="verdict ' + css + '">' + label + '</span>' +
                '<span>' + escapeHtml(test.name) + '</span>' +
                '<span class="result-meta">(' + test.time_seconds + 's, ' + test.memory_mb + 'MB)</span>' +
                '</div>';

            if (meta) {
                html += '<div class="result-detail">' +
                    escapeHtml(meta.description) +
                    ' — ' + meta.num_base_resistances + ' base values, ' +
                    'max ' + meta.max_resistors + ' resistors, ' +
                    'target: ' + escapeHtml(meta.target_resistance) +
                    '</div>';
            }

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

            if (meta) {
                html += '<div class="result-detail">' +
                    escapeHtml(meta.description) +
                    ' — ' + meta.num_base_resistances + ' base values, ' +
                    'max ' + meta.max_resistors + ' resistors, ' +
                    'target: ' + escapeHtml(meta.target_resistance) +
                    '</div>';
            }

            if (!test.passed && test.message) {
                html += '<div class="result-message collapsed" onclick="this.classList.toggle(\'collapsed\')">' +
                    escapeHtml(test.message) + '</div>';
            }
        }
    }

    el.innerHTML = html;
}

// ---- IndexedDB helpers (for persisting file handles across reloads) ----

function openIDB() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open('workbench', 1);
        req.onupgradeneeded = () => {
            req.result.createObjectStore('fileHandles');
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
}

async function storeHandle(lang, handle) {
    try {
        const db = await openIDB();
        const tx = db.transaction('fileHandles', 'readwrite');
        tx.objectStore('fileHandles').put(handle, lang);
        await new Promise((res, rej) => { tx.oncomplete = res; tx.onerror = rej; });
    } catch (e) {
        console.warn('Failed to persist file handle:', e);
    }
}

async function loadHandle(lang) {
    try {
        const db = await openIDB();
        const tx = db.transaction('fileHandles', 'readonly');
        const req = tx.objectStore('fileHandles').get(lang);
        return new Promise((resolve) => {
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => resolve(null);
        });
    } catch (e) {
        return null;
    }
}

async function removeHandle(lang) {
    try {
        const db = await openIDB();
        const tx = db.transaction('fileHandles', 'readwrite');
        tx.objectStore('fileHandles').delete(lang);
    } catch (e) {
        // non-fatal
    }
}

// ---- Native file save (File System Access API) ----

function getSuggestedFilename(lang) {
    if (!problemData) return null;
    const langData = problemData.languages.find(l => l.name === lang);
    if (!langData || !langData.solution_file) return null;
    // Extract basename: "src/main/java/.../Solution.java" → "Solution.java"
    return langData.solution_file.split('/').pop();
}

async function nativeSave(lang, code) {
    // 1. Check in-memory handle
    let handle = fileHandles[lang] || null;

    // 2. Try restoring from IndexedDB
    if (!handle) {
        handle = await loadHandle(lang);
    }

    // 3. Verify permission on existing handle
    if (handle) {
        let perm = await handle.queryPermission({ mode: 'readwrite' });
        if (perm === 'prompt') {
            perm = await handle.requestPermission({ mode: 'readwrite' });
        }
        if (perm !== 'granted') {
            handle = null; // permission denied — fall through to picker
        }
    }

    // 4. No valid handle — open the picker
    if (!handle) {
        const suggestedName = getSuggestedFilename(lang) || 'solution';
        handle = await window.showSaveFilePicker({
            suggestedName,
            types: FILE_TYPES[lang] || [],
        });
    }

    // 5. Write the file
    const writable = await handle.createWritable();
    await writable.write(code);
    await writable.close();

    // 6. Cache and persist handle
    fileHandles[lang] = handle;
    await storeHandle(lang, handle);
}

// ---- Native file load (File System Access API) ----

function getAcceptExtensions(lang) {
    const types = FILE_TYPES[lang];
    if (!types || !types[0]) return '';
    const exts = Object.values(types[0].accept).flat();
    return exts.join(',');
}

async function nativeLoad(lang) {
    const handle = await window.showOpenFilePicker({
        types: FILE_TYPES[lang] || [],
        multiple: false,
    });
    const fileHandle = handle[0];
    const file = await fileHandle.getFile();
    const text = await file.text();

    // Cache handle so next Save writes back to this file
    fileHandles[lang] = fileHandle;
    await storeHandle(lang, fileHandle);

    return text;
}

function fallbackLoad(lang) {
    return new Promise((resolve, reject) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = getAcceptExtensions(lang);
        input.addEventListener('change', () => {
            const file = input.files[0];
            if (!file) { reject(new Error('No file selected')); return; }
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file);
        });
        input.click();
    });
}

async function loadSolution() {
    if (!currentLanguage) return;

    const btn = document.getElementById('btn-load');
    let text = null;

    if (HAS_FILE_PICKER) {
        try {
            text = await nativeLoad(currentLanguage);
        } catch (e) {
            if (e.name === 'AbortError') return; // user cancelled
            console.warn('Native load failed, falling back to file input:', e);
            try {
                text = await fallbackLoad(currentLanguage);
            } catch (e2) {
                console.warn('Fallback load also failed:', e2);
                return;
            }
        }
    } else {
        try {
            text = await fallbackLoad(currentLanguage);
        } catch (e) {
            console.warn('File load failed:', e);
            return;
        }
    }

    if (text !== null) {
        editor.setValue(text);
        editorState[currentLanguage] = text;
        btn.textContent = 'Loaded!';
        setTimeout(() => { btn.textContent = 'Load'; }, 1500);
    }
}

// ---- Solution persistence ----

async function backendSave(lang, code, btn) {
    try {
        await api('PUT', '/api/solution/' + lang, { code });
        editorState[lang] = code;
        btn.textContent = 'Saved!';
        setTimeout(() => { btn.textContent = 'Save'; }, 1500);
    } catch (e) {
        btn.textContent = 'Error';
        setTimeout(() => { btn.textContent = 'Save'; }, 1500);
    }
}

async function saveSolution() {
    if (!currentLanguage) return;

    const code = editor.getValue();
    const btn = document.getElementById('btn-save');

    if (HAS_FILE_PICKER) {
        try {
            await nativeSave(currentLanguage, code);
            editorState[currentLanguage] = code;
            btn.textContent = 'Saved!';
            setTimeout(() => { btn.textContent = 'Save'; }, 1500);
        } catch (e) {
            if (e.name === 'AbortError') {
                // User cancelled the picker — do nothing
                return;
            }
            console.warn('Native save failed, falling back to backend:', e);
            await backendSave(currentLanguage, code, btn);
        }
    } else {
        await backendSave(currentLanguage, code, btn);
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

    // Clear native file handle so next save reopens picker
    delete fileHandles[currentLanguage];
    await removeHandle(currentLanguage);

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
document.getElementById('btn-load').addEventListener('click', loadSolution);
document.getElementById('btn-reset').addEventListener('click', resetSolution);
document.getElementById('btn-theme').addEventListener('click', toggleTheme);

// ---- Utilities ----

function getTestMeta(testName) {
    if (!problemData || !problemData.tests) return null;
    // Extract ID from "test_1", "test_2", etc.
    const match = testName.match(/(\d+)$/);
    if (!match) return null;
    const id = parseInt(match[1], 10);
    return problemData.tests.find(t => t.id === id) || null;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
