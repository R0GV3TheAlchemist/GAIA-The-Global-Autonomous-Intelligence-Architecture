// GAIA Dev Suite — Monaco Code Editor
// Phase 4.2 — Full editor integration
// Loaded lazily via CDN on first use

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type MonacoInstance = any;

declare global {
  interface Window { require: any; monaco: MonacoInstance; }
}

let _editorInstance: MonacoInstance = null;
let _currentPath: string | null = null;
let _onSave: ((path: string, content: string) => void) | null = null;

const GAIA_THEME = {
  base: 'vs-dark' as const,
  inherit: true,
  rules: [
    { token: 'comment',    foreground: '4a7c6a', fontStyle: 'italic' },
    { token: 'keyword',    foreground: '00b4a6' },
    { token: 'string',     foreground: '7ec8a0' },
    { token: 'number',     foreground: 'c3a6ff' },
    { token: 'type',       foreground: '5ccfe6' },
    { token: 'identifier', foreground: 'e0e0e0' },
  ],
  colors: {
    'editor.background':              '#1e1e1e',
    'editor.foreground':              '#e0e0e0',
    'editor.lineHighlightBackground': '#2a2a2a',
    'editor.selectionBackground':     '#00b4a640',
    'editorCursor.foreground':        '#00b4a6',
    'editorLineNumber.foreground':    '#4a4a4a',
    'editor.findMatchBackground':     '#00b4a630',
  },
};

export async function loadMonaco(): Promise<void> {
  if (typeof window.monaco !== 'undefined') return;
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.0/min/vs/loader.js';
    script.onload = () => {
      window.require.config({
        paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.0/min/vs' }
      });
      window.require(['vs/editor/editor.main'], () => {
        window.monaco.editor.defineTheme('gaia-dark', GAIA_THEME);
        resolve();
      });
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

export async function mountMonacoEditor(
  container: HTMLElement,
  options?: { onSave?: (path: string, content: string) => void }
): Promise<void> {
  await loadMonaco();
  if (options?.onSave) _onSave = options.onSave;

  _editorInstance = window.monaco.editor.create(container, {
    theme: 'gaia-dark',
    automaticLayout: true,
    fontSize: 13,
    fontFamily: "'Cascadia Code', 'Fira Code', monospace",
    fontLigatures: true,
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    renderWhitespace: 'selection',
    bracketPairColorization: { enabled: true },
    suggestOnTriggerCharacters: true,
    quickSuggestions: true,
  });

  // Ctrl+S save
  _editorInstance.addCommand(
    window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.KeyS,
    () => {
      if (_currentPath && _onSave) {
        _onSave(_currentPath, _editorInstance.getValue());
      }
    }
  );

  // Ctrl+H find & replace
  _editorInstance.addCommand(
    window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.KeyH,
    () => _editorInstance.getAction('editor.action.startFindReplaceAction').run()
  );
}

export function openInEditor(path: string, content: string): void {
  if (!_editorInstance) return;
  _currentPath = path;
  const ext = path.split('.').pop() ?? '';
  const langMap: Record<string, string> = {
    ts: 'typescript', tsx: 'typescript',
    js: 'javascript', jsx: 'javascript',
    py: 'python',
    rs: 'rust',
    json: 'json',
    md: 'markdown',
    toml: 'ini',
    css: 'css',
    html: 'html',
  };
  const language = langMap[ext] ?? 'plaintext';
  const model = window.monaco.editor.createModel(content, language);
  _editorInstance.setModel(model);
}

export function markEditorClean(): void {
  _editorInstance?.getModel()?.setEOL(0);
}

/** Returns the text currently selected in the editor, or null if nothing is selected. */
export function getSelectedCode(): string | null {
  if (!_editorInstance) return null;
  const selection = _editorInstance.getSelection();
  if (!selection || _editorInstance.getModel()?.getValueInRange(selection).trim() === '') return null;
  return _editorInstance.getModel()?.getValueInRange(selection) ?? null;
}

/** Returns the full source text of the currently open file. */
export function getEditorContent(): string {
  return _editorInstance?.getValue() ?? '';
}

/** Returns the file path of the currently open file, or null if no file is open. */
export function getCurrentFilePath(): string | null {
  return _currentPath;
}

/**
 * Inserts text at the current cursor position (or replaces the current selection).
 * Used by the AI Pair Programmer to apply refactor/fix suggestions inline.
 */
export function insertAtCursor(text: string): void {
  if (!_editorInstance) return;
  const selection = _editorInstance.getSelection();
  const op = { range: selection, text, forceMoveMarkers: true };
  _editorInstance.executeEdits('gaia-pair-programmer', [op]);
  _editorInstance.focus();
}

/**
 * Registers GAIA ghost-text inline completions provider.
 * Called once during mountRightSidebar — safe to call multiple times (no-ops if already registered).
 */
let _inlineProviderRegistered = false;
export function registerGaiaInlineCompletions(gaiaEndpoint: string): void {
  if (_inlineProviderRegistered || typeof window.monaco === 'undefined') return;
  _inlineProviderRegistered = true;

  window.monaco.languages.registerInlineCompletionsProvider('*', {
    async provideInlineCompletions(model: MonacoInstance, position: MonacoInstance) {
      const lineContent = model.getLineContent(position.lineNumber);
      if (lineContent.trim().length < 4) return { items: [] };

      try {
        const res = await fetch(gaiaEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'complete',
            code: model.getValue(),
            cursor_line: position.lineNumber,
            cursor_col: position.column,
            file_path: _currentPath,
          }),
        });
        if (!res.ok) return { items: [] };
        const data = await res.json() as { completion?: string };
        if (!data.completion) return { items: [] };
        return {
          items: [{
            insertText: data.completion,
            range: {
              startLineNumber: position.lineNumber,
              startColumn: position.column,
              endLineNumber: position.lineNumber,
              endColumn: position.column,
            },
          }],
        };
      } catch {
        return { items: [] };
      }
    },
    freeInlineCompletions() { /* no-op */ },
  });
}
