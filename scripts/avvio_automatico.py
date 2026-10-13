"""Primo avvio: chiave locale, requisiti, prove effettive e browser.

Si può aggiungere a una copia esistente senza sostituire .env, .data o il codice.
L'esito è registrato; nessun errore abilita l'esecuzione del codice sull'host.
"""
import asyncio
from datetime import datetime, timezone
from getpass import getpass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import dotenv_values, set_key
from app.config import load_settings
from app.sandbox import Sandbox
from scripts import controlla_ia, prova_agente, verifica_locale


def request_key(provider):
    """Su Windows una casella normale, mascherata, permette Ctrl+V e clic destro."""
    if sys.platform != 'win32':
        return getpass('Chiave API (input nascosto): ').strip()
    try:
        import tkinter as tk
        from tkinter import ttk
        window = tk.Tk()
    except Exception:
        # Non mostrare il contenuto dell'errore: mai esporre clipboard o segreti.
        print('Casella grafica non disponibile. Inserisci la chiave nel terminale (nascosta).', flush=True)
        return getpass('Chiave API: ').strip()
    window.title('Officina — inserisci la chiave')
    window.resizable(False, False)
    frame = ttk.Frame(window, padding=24)
    frame.pack()
    ttk.Label(frame, text=f'Incolla la chiave API {provider}', font=('Segoe UI', 14)).pack(anchor='w')
    ttk.Label(frame, text='Resta sul tuo PC. Non inviarla nella chat.', padding=(0, 8)).pack(anchor='w')
    entry = ttk.Entry(frame, width=48, show='*', font=('Segoe UI', 12))
    entry.pack(fill='x', pady=8)
    result = ['']

    def paste():
        try:
            value = window.clipboard_get().strip()
        except tk.TclError:
            return
        entry.delete(0, 'end')
        entry.insert(0, value)
        entry.focus_set()

    def accept(event=None):
        result[0] = entry.get().strip()
        window.destroy()

    menu = tk.Menu(window, tearoff=False)
    menu.add_command(label='Incolla', command=paste)
    entry.bind('<Button-3>', lambda event: menu.tk_popup(event.x_root, event.y_root))
    ttk.Button(frame, text='Incolla la chiave copiata', command=paste).pack(fill='x', pady=4)
    ttk.Button(frame, text='Salva e continua', command=accept).pack(fill='x', pady=8)
    window.bind('<Return>', accept)
    window.protocol('WM_DELETE_WINDOW', window.destroy)
    window.lift()
    window.after(100, entry.focus_force)
    window.mainloop()
    return result[0]


def save_key(provider, key):
    if len(key) < 20 or any(c.isspace() for c in key) or not key.isascii():
        raise ValueError('Formato della chiave non valido. Nessuna modifica.')
    variable = 'GROQ_API_KEY' if provider == 'groq' else 'AI_PROVIDER_KEY'
    config_path = ROOT / '.env'
    if not config_path.exists():
        config_path.write_text((ROOT / '.env.example').read_text(encoding='utf-8'), encoding='utf-8')
    path = credential_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    set_key(str(path), variable, key, quote_mode='always')
    set_key(str(config_path), 'AI_PROVIDER', provider, quote_mode='always')
    if sys.platform == 'win32':
        account = os.environ.get('USERNAME', '')
        domain = os.environ.get('USERDOMAIN', '')
        if domain:
            account = domain + '\\' + account
        if account:
            result = subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r', account + ':(F)'],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            if result.returncode:
                print('Chiave salvata. Windows non ha aggiornato i permessi del file.', flush=True)
    else:
        path.chmod(0o600)
    os.environ[variable] = key
    os.environ['AI_PROVIDER'] = provider
    print('Chiave salvata sul PC.', flush=True)


def credential_path():
    if sys.platform != 'win32':
        return ROOT / '.env'
    local = os.environ.get('LOCALAPPDATA')
    if not local:
        raise RuntimeError('Cartella locale delle credenziali non disponibile.')
    return Path(local) / 'Officina' / 'credentials.env'


def load_local_credentials():
    if sys.platform == 'win32':
        values = dotenv_values(credential_path())
        for variable in ('GROQ_API_KEY', 'AI_PROVIDER_KEY'):
            if not os.environ.get(variable) and values.get(variable):
                os.environ[variable] = values[variable]


def ensure_launcher():
    launcher = ROOT / 'avvio_automatico.bat'
    if sys.platform == 'win32' and not launcher.exists():
        launcher.write_bytes(
            b'@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
            b'".venv\\Scripts\\python.exe" scripts\\avvio_automatico.py\r\n'
            b'if errorlevel 1 pause\r\n')


async def live_with_progress():
    task = asyncio.create_task(prova_agente.main())
    while not task.done():
        await asyncio.wait({task}, timeout=20)
        if not task.done():
            print('Lavoro: prova agente ancora in corso. Tentativi e tempo restano limitati.', flush=True)
    return await task


def docker_paths():
    locations = []
    if sys.platform == 'win32':
        for variable, suffix in [('LOCALAPPDATA', 'Programs/DockerDesktop'), ('ProgramFiles', 'Docker/Docker')]:
            base = os.environ.get(variable)
            if base:
                locations.append(Path(base) / suffix)
        for base in locations:
            binary = base / 'resources' / 'bin'
            if binary.is_dir():
                os.environ['PATH'] = str(binary) + os.pathsep + os.environ.get('PATH', '')
    return locations


def docker_linux():
    if not shutil.which('docker'):
        return False
    try:
        result = subprocess.run(['docker', 'info', '--format', '{{.OSType}}'],
                                capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and result.stdout.strip() == 'linux'
    except (OSError, subprocess.TimeoutExpired):
        return False


def ensure_docker():
    locations = docker_paths()
    if docker_linux():
        return True
    if sys.platform != 'win32':
        return False
    desktop = next((p / 'Docker Desktop.exe' for p in locations if (p / 'Docker Desktop.exe').is_file()), None)
    if desktop is None and shutil.which('winget'):
        print('Preparazione: provo a installare Docker Desktop dal gestore ufficiale Windows.', flush=True)
        try:
            # Il gestore mantiene firma e checksum. Nessuna accettazione automatica
            # di contratti, elevazione nascosta, modifica WSL o riavvio del PC.
            subprocess.run(['winget', 'install', '--id', 'Docker.DockerDesktop', '--exact',
                            '--source', 'winget', '--scope', 'user', '--silent', '--disable-interactivity'],
                           timeout=900, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass
        locations = docker_paths()
        desktop = next((p / 'Docker Desktop.exe' for p in locations if (p / 'Docker Desktop.exe').is_file()), None)
    if desktop is None:
        print('Serve il tuo intervento: installa Docker Desktop per Windows con WSL 2 e container Linux.', flush=True)
        print('https://docs.docker.com/desktop/setup/install/windows-install/', flush=True)
        return False
    print('Preparazione: avvio Docker Desktop. Se chiede un’autorizzazione, compare sul tuo PC.', flush=True)
    subprocess.Popen([str(desktop)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if docker_linux():
            return True
        time.sleep(3)
    print('Serve il tuo intervento: Docker non è pronto. Controlla la sua finestra e i requisiti WSL 2.', flush=True)
    return False


def prepare_image():
    try:
        subprocess.run(['docker', 'pull', 'python:3.12-slim'], check=True, timeout=600)
        digest = subprocess.check_output(['docker', 'image', 'inspect', 'python:3.12-slim',
                                          '--format', '{{index .RepoDigests 0}}'], text=True, timeout=20).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print('Immagine non preparata: download fallito o tempo massimo raggiunto.', flush=True)
        return False
    import re
    if not re.fullmatch(r'[a-z0-9./_-]+@sha256:[a-f0-9]{64}', digest):
        print('Digest immagine non valido: esecuzione autonoma disabilitata.', flush=True)
        return False
    set_key(str(ROOT / '.env'), 'SANDBOX_IMAGE', digest, quote_mode='never')
    os.environ['SANDBOX_IMAGE'] = digest
    print('Immagine verificata e fissata per l’esecuzione isolata.', flush=True)
    return True


def fingerprint(settings):
    digest = hashlib.sha256()
    digest.update(json.dumps({'provider': settings.provider, 'model': settings.model,
                             'image': settings.sandbox_image}, sort_keys=True).encode())
    for folder in ('app', 'examples/activity_backend'):
        for path in sorted((ROOT / folder).rglob('*.py')):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    for name in ('prova_agente.py', 'verifica_locale.py', 'avvio_automatico.py'):
        digest.update((ROOT / 'scripts' / name).read_bytes())
    return digest.hexdigest()


def read_report(path):
    try:
        report = json.loads(path.read_text(encoding='utf-8'))
        return report if isinstance(report, dict) else {}
    except (OSError, ValueError):
        return {}


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def verified_live_evidence(settings):
    evidence = read_report(settings.data_dir / 'live-acceptance' / 'RESULTS.json')
    generation = evidence.get('generation', {})
    repair = evidence.get('repair') or {}
    repaired = repair.get('project', {})
    if not (generation.get('state') == 'Pronto' and repaired.get('state') == 'Pronto'
            and repair.get('detected_initial_fault') is True
            and repair.get('corrected_and_retested') is True and repair.get('original_unchanged') is True):
        return False
    from app.storage import Store
    store = Store(settings.data_dir / 'live-acceptance')
    try:
        return all(item.get('verified_hash') and store.digest(item['id']) == item['verified_hash']
                   for item in (generation, repaired))
    except (KeyError, ValueError):
        return False
    finally:
        store.close()


def run_setup(retry=False):
    settings = load_settings()
    path = settings.data_dir / 'setup' / 'RESULTS.json'
    previous = read_report(path)
    report = {'date': datetime.now(timezone.utc).isoformat(), 'platform': sys.platform,
              'api': 'not_run', 'sandbox': 'not_run', 'reference': 'not_run', 'live_ai': 'not_run'}
    write_report(path, report)
    if not settings.api_key:
        key = request_key(settings.provider)
        if not key:
            report['reason'] = 'Inserimento chiave annullato. Nessuna chiamata IA.'
            write_report(path, report)
            return report
        save_key(settings.provider, key)
        settings = load_settings()
    print('Preparazione: controllo accesso API e disponibilità del modello.', flush=True)
    report['api'] = 'passed' if asyncio.run(controlla_ia.main()) == 0 else 'failed'
    write_report(path, report)
    if report['api'] != 'passed':
        report['reason'] = 'Controllo API fallito. Generazione e correzione IA non eseguite.'
        write_report(path, report)
        return report
    if not ensure_docker():
        report['sandbox'] = 'unavailable'
        report['reason'] = 'Docker Linux non disponibile: esecuzione autonoma disabilitata.'
        write_report(path, report)
        return report
    state = asyncio.run(Sandbox(settings).status())
    if not state['available']:
        print('Preparazione: scarico l’immagine Python e ne fisso il digest verificato.', flush=True)
        if not prepare_image():
            report['sandbox'] = 'failed'
            write_report(path, report)
            return report
        settings = load_settings()
    if not asyncio.run(Sandbox(settings).status())['available']:
        report['sandbox'] = 'failed'
        write_report(path, report)
        return report
    report['sandbox'] = 'passed'
    signature = fingerprint(settings)
    report['fingerprint'] = signature
    same = previous.get('fingerprint') == signature
    reference_path = ROOT / '.data' / 'verification' / 'local_acceptance.json'
    reference = read_report(reference_path)
    if (same and previous.get('reference') == 'passed' and reference.get('fault_detection_passed') is True
            and reference.get('reference_backend', {}).get('passed') is True
            and reference.get('restored_reference', {}).get('passed') is True):
        report['reference'] = 'passed'
        report['reference_reused'] = True
    else:
        print('Verifica: backend, persistenza, idempotenza e difetto deliberato, senza IA.', flush=True)
        report['reference'] = 'passed' if asyncio.run(verifica_locale.main()) == 0 else 'failed'
    write_report(path, report)
    if report['reference'] != 'passed':
        report['reason'] = 'Verifica essenziale fallita: prova con IA non eseguita.'
        write_report(path, report)
        return report
    if same and previous.get('live_ai') in ('passed', 'failed', 'running', 'interrupted', 'not_verified') and not retry:
        report['live_ai'] = previous['live_ai'] if previous['live_ai'] != 'running' else 'interrupted'
        if report['live_ai'] == 'passed' and not verified_live_evidence(settings):
            report['live_ai'] = 'not_verified'
        report['live_ai_reused'] = True
        if report['live_ai'] != 'passed':
            report['reason'] = 'Prova IA precedente non completata. Nessun tentativo automatico ripetuto.'
    else:
        print('Lavoro: provo l’agente reale. Generazione e correzione separata hanno limiti di tentativi e tempo.', flush=True)
        report['live_ai'] = 'running'
        write_report(path, report)
        report['live_ai'] = 'passed' if asyncio.run(live_with_progress()) == 0 else 'failed'
        if report['live_ai'] != 'passed':
            report['reason'] = 'Prova con IA non completata. Consulta i risultati; quote e modello possono limitarla.'
    write_report(path, report)
    print('Risultati effettivi salvati sul PC:', path, flush=True)
    print('Verifica agente:', 'PASSATA' if report['live_ai'] == 'passed' else 'NON COMPLETATA', flush=True)
    return report


def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        ensure_launcher()
        load_local_credentials()
        report = run_setup(retry='--riprova-verifica' in sys.argv)
        if report.get('reason'):
            print('Serve il tuo intervento:', report['reason'], flush=True)
        print('Apro Officina nel browser. Conserva questa finestra aperta.', flush=True)
        import avvia
        avvia.main()
        return 0
    except KeyboardInterrupt:
        print('Avvio interrotto. File e memoria conservati.', flush=True)
        return 130
    except Exception as exc:
        print(f'Avvio non completato ({type(exc).__name__}). Nessuna chiave viene mostrata.', flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
