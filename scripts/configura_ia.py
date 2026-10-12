"""Inserimento locale della credenziale: input nascosto, nessun valore stampato."""
from getpass import getpass
import os
from pathlib import Path
import subprocess
import sys
from dotenv import set_key

ROOT = Path(__file__).resolve().parent.parent


def main():
    provider = 'openai' if '--openai' in sys.argv else 'groq'
    variable = 'AI_PROVIDER_KEY' if provider == 'openai' else 'GROQ_API_KEY'
    print(f'Configura {provider} sul tuo computer. Non incollare la chiave nella chat.')
    if provider == 'groq':
        print('Crea un account Free e una chiave su https://console.groq.com/keys')
        print('Controlla nella console le quote del piano gratuito. Non occorre un account OpenAI.')
        if '--no-browser' not in sys.argv:
            import webbrowser
            webbrowser.open('https://console.groq.com/keys')
    else:
        print('Opzione OpenAI: API a pagamento, separate dall’abbonamento ChatGPT.')
    key = getpass('Chiave API (input nascosto, Invio per annullare): ').strip()
    if not key:
        print('Configurazione annullata. Nessuna modifica.')
        return 0
    if len(key) < 20 or any(c.isspace() for c in key) or not key.isascii():
        print('Formato non valido. Nessuna chiave salvata.')
        return 1
    path = ROOT / '.env'
    if not path.exists():
        path.write_text((ROOT / '.env.example').read_text(encoding='utf-8'), encoding='utf-8')
    set_key(str(path), variable, key, quote_mode='always')
    set_key(str(path), 'AI_PROVIDER', provider, quote_mode='always')
    if sys.platform == 'win32':
        account = os.environ.get('USERNAME', '')
        domain = os.environ.get('USERDOMAIN', '')
        if domain:
            account = domain + '\\' + account
        result = subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r', account + ':(F)'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode:
            print('Chiave salvata; permessi Windows non aggiornati. Mantieni la cartella nel tuo profilo personale.')
        else:
            print('Chiave salvata in .env con accesso limitato al tuo account Windows.')
    else:
        path.chmod(0o600)
        print('Chiave salvata in .env con permessi per il solo proprietario.')
    print('La chiave non è stata verificata. Riavvia Officina e avvia un progetto per provarla.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
