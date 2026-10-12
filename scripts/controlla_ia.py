"""Controllo di accesso e modello: richiesta read-only, non una prova dell'agente."""
import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import load_settings
from app.providers import create_client
import groq
import openai


async def main():
    settings = load_settings()
    if not settings.api_key:
        print(f'NON ESEGUITO: manca {settings.credential_var}. Apri configura_ia.bat sul tuo PC.')
        return 2
    try:
        async with create_client(settings, timeout=20) as client:
            models = await client.models.list()
        available = {m.id for m in models.data if getattr(m, 'active', True)}
        if settings.model not in available:
            print(f'Accesso a {settings.provider} riuscito, ma il modello configurato non è disponibile.')
            print('Controlla GROQ_MODEL o AI_MODEL nella configurazione locale.')
            return 1
        print(f'Accesso API e modello disponibili: {settings.provider}, {settings.model}.')
        print('Questo controllo non verifica il piano Free, la fatturazione o le capacità dell’agente.')
        print('Per la prova completa esegui scripts/prova_agente.py.')
        return 0
    except (groq.APIStatusError, openai.APIStatusError) as exc:
        print(f'Controllo non riuscito: HTTP {exc.status_code}. Verifica chiave, quota e permessi nella console.')
        return 1
    except (groq.APIConnectionError, openai.APIConnectionError):
        print(f'Connessione non riuscita. Verifica accesso HTTPS a {settings.api_host}.')
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
