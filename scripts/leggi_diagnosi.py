"""Legge lo stato attuale senza IA, test, import del codice generato o modifiche al database."""
import ast
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import load_settings


def safe_text(value, limit=2400):
    text = value if isinstance(value, str) else ''
    return re.sub(r'\b(?:gsk_|sk-)[A-Za-z0-9_-]{8,}', '[CHIAVE OSCURATA]', text)[:limit]


def safe_value(value):
    if isinstance(value, str):
        return safe_text(value, 8000)
    if isinstance(value, dict):
        return {safe_text(key, 200): safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [safe_value(item) for item in value]
    return value


def code_outline(path):
    # Analisi sintattica, senza import/exec. Dimensione limitata prima della lettura.
    if path.is_symlink() or path.stat().st_size > 128000:
        return {'analysis': 'skipped: linked or oversized file'}
    source = path.read_text(encoding='utf-8')
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError) as exc:
        return {'syntax_error': type(exc).__name__, 'line': getattr(exc, 'lineno', None)}
    functions = []
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({'name': node.name, 'parameters': [arg.arg for arg in node.args.args]})
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    flags = sorted({node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and node.value in ('--port', '--db')})
    return {'functions': functions[:20], 'imports': imports[:20], 'contract_cli_flags': flags}


def collect(settings):
    data = settings.data_dir / 'live-acceptance'
    checkpoint = data / 'RUN.json'
    saved = data / 'RESULTS.json'
    identifier = None
    if checkpoint.exists():
        identifier = json.loads(checkpoint.read_text(encoding='utf-8')).get('generation_id')
    if not identifier and saved.exists():
        identifier = json.loads(saved.read_text(encoding='utf-8')).get('generation', {}).get('id')
    if not isinstance(identifier, str) or not re.fullmatch(r'[a-f0-9]{32}', identifier):
        raise ValueError('No valid generation project')
    db = sqlite3.connect((data / 'memory.sqlite3').resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        row = db.execute('SELECT * FROM projects WHERE id=?', (identifier,)).fetchone()
        if row is None:
            raise ValueError('Project not found')
        events = [dict(event) for event in db.execute(
            'SELECT id,kind,detail FROM events WHERE project_id=? ORDER BY id DESC LIMIT 100', (identifier,))]
        for event in events:
            event['detail'] = json.loads(event['detail'])
        project = dict(row)
    finally:
        db.close()
    workspace = data / 'projects' / identifier / 'workspace'
    if workspace.is_symlink() or not workspace.resolve().is_relative_to(data.resolve()):
        raise ValueError('Workspace outside application data')
    files = []
    outlines = {}
    for path in sorted(workspace.rglob('*')):
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(workspace)):
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(workspace).as_posix()
        files.append({'path': safe_text(relative, 200), 'bytes': path.stat().st_size})
        if path.parent == workspace and path.suffix == '.py':
            outlines[relative] = code_outline(path)
    history = json.loads(project['history'])
    outputs = {item['call_id']: item for item in history if item.get('type') == 'function_call_output'
               and isinstance(item.get('call_id'), str)}
    attempts = []
    for item in history:
        if item.get('type') != 'function_call' or item.get('name') != 'write_file':
            continue
        try:
            args = json.loads(item['arguments'])
        except (KeyError, TypeError, ValueError):
            continue
        if not isinstance(args, dict) or args.get('path') != 'main.py':
            continue
        output = outputs.get(item.get('call_id'), {}).get('output', '')
        attempts.append({'characters': len(args.get('content', '')) if isinstance(args.get('content'), str) else None,
                         'result': safe_text(output, 800)})
    last_message = next((event['detail'].get('text', '') for event in events if event['kind'] == 'messaggio_ia'), '')
    errors = [{'tool': safe_text(event['detail'].get('tool'), 100),
               'message': safe_text(event['detail'].get('message'), 1000)}
              for event in events if event['kind'] == 'errore_strumento'][:8]
    operations = [{'event_id': event['id'], 'tool': safe_text(event['detail'].get('tool'), 100),
                   'path': safe_text(event['detail'].get('arguments', {}).get('path'), 200)}
                  for event in events if event['kind'] == 'operazione'][:12]
    check = json.loads(project['last_check']) if project.get('last_check') else {}
    budget = next((event['detail'] for event in events if event['kind'] == 'controllo_budget_token'), None)
    return safe_value({'mode': 'project read-only; no API or generated-code execution',
            'project': {key: project[key] for key in ('id', 'state', 'model_calls', 'tool_calls',
                'input_tokens', 'output_tokens', 'failed_checks', 'docs_consulted', 'elapsed')},
            'files_now': files, 'python_outline_now': outlines,
            'last_check': {'passed': check.get('passed'), 'check': check.get('check'),
                'stderr': safe_text(check.get('stderr'), 4000)},
            'last_token_budget': budget, 'main_write_attempts': attempts[-5:],
            'recent_tool_errors': errors, 'recent_operations': operations,
            'last_agent_message': safe_text(last_message, 6000)})


def collect_repair_summary(settings):
    """Riepilogo breve della copia, con soli campi diagnostici e database in lettura."""
    data = settings.data_dir / 'live-acceptance'
    saved = json.loads((data / 'RESULTS.json').read_text(encoding='utf-8'))
    repair = saved.get('repair') or {}
    project = repair.get('project') or {}
    if not project:
        return {'mode': 'read-only; no API or execution', 'repair': 'non avviata',
                'generation_state': (saved.get('generation') or {}).get('state')}
    pid = project.get('id')
    if not isinstance(pid, str) or not re.fullmatch(r'[a-f0-9]{32}', pid):
        raise ValueError('No valid repair project')
    check = project.get('last_check') or {}
    counters = check.get('check') or {}
    report = {'mode': 'read-only; no API or execution',
        'repair': {key: project.get(key) for key in ('id', 'state', 'model_calls', 'tool_calls',
            'input_tokens', 'output_tokens', 'failed_checks', 'elapsed')},
        'reason': safe_text(project.get('summary'), 400),
        'checks_passed': check.get('passed'),
        'unit_tests': {key: counters.get(key) for key in ('unit_tests', 'unit_failures', 'unit_errors')},
        'last_error': safe_text((check.get('stderr') or '')[-650:], 650),
        'proof': {key: repair.get(key) for key in ('detected_initial_fault', 'corrected_and_retested',
            'original_unchanged', 'tests_unchanged')},
        'ai_write_recorded': bool(repair.get('ai_repair_write'))}
    budget = (saved.get('last_token_budget') or {}).get('repair') or {}
    if budget:
        report['token_budget'] = {key: budget.get(key) for key in ('used_tokens', 'required_tokens', 'limit_tokens')}
    with closing(sqlite3.connect((data / 'memory.sqlite3').resolve().as_uri() + '?mode=ro', uri=True)) as db:
        operations = db.execute('SELECT detail FROM events WHERE project_id=? AND kind=? ORDER BY id DESC LIMIT 4',
                                (pid, 'operazione')).fetchall()
        report['last_operations'] = [{'tool': detail.get('tool'), 'path': detail.get('arguments', {}).get('path')}
                                     for (raw,) in operations for detail in [json.loads(raw)]]
        message = db.execute('SELECT detail FROM events WHERE project_id=? AND kind=? ORDER BY id DESC LIMIT 1',
                             (pid, 'messaggio_ia')).fetchone()
        if message:
            report['last_ai_message'] = safe_text(json.loads(message[0]).get('text'), 350)
        errors = db.execute('SELECT detail FROM events WHERE project_id=? AND kind=? ORDER BY id DESC LIMIT 2',
                            (pid, 'errore_strumento')).fetchall()
        if errors:
            report['tool_errors'] = [safe_text(json.loads(raw).get('message'), 160) for (raw,) in errors]
    return safe_value(report)


def main():
    try:
        settings = load_settings()
        report = collect_repair_summary(settings) if '--correzione' in sys.argv else collect(settings)
        directory = settings.data_dir / 'diagnostics'
        if directory.is_symlink() or not directory.resolve().is_relative_to(settings.data_dir.resolve()):
            raise ValueError('Diagnostics path not allowed')
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / ('diagnosi-' + uuid.uuid4().hex[:12] + '.txt')
        with path.open('x', encoding='utf-8') as file:
            file.write(json.dumps(report, ensure_ascii=False, indent=2))
        print('Diagnosi preparata. Nessuna chiamata IA, nessun test e nessun cambiamento al progetto.', flush=True)
        if sys.platform == 'win32':
            subprocess.Popen(['notepad.exe', str(path)])
        else:
            print(path)
        return 0
    except Exception as exc:
        print(f'Diagnosi non completata ({type(exc).__name__}). Nessuna chiave viene mostrata.', flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
