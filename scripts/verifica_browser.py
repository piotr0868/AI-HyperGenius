"""Smoke test Chromium dell'interfaccia reale; non usa un provider IA simulato."""
import asyncio
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import load_settings
from playwright.async_api import async_playwright, expect


async def main():
    settings = load_settings()
    url = f'http://127.0.0.1:{settings.port}'
    output = ROOT / '.data' / 'verification'
    output.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        binary = shutil.which('chromium')
        browser = await playwright.chromium.launch(executable_path=binary, headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 950})
        errors = []
        page.on('pageerror', lambda exc: errors.append(str(exc)))
        response = await page.goto(url)
        assert response.status == 200
        await page.wait_for_selector('#start:not([disabled])')
        await expect(page.locator('#configuration')).to_contain_text('API')
        assert await page.locator('html').get_attribute('lang') == 'it'
        await page.screenshot(path=str(output / 'interfaccia.png'), full_page=True)
        await page.get_by_role('button', name='+ Nuovo obiettivo').click()
        await page.locator('#goal').fill('Prova browser: backend locale con attività e SQLite persistente.')
        await page.get_by_role('button', name='Avvia', exact=True).click()
        if not settings.api_key:
            await expect(page.locator('#state')).to_have_text('Serve il tuo intervento')
            assert settings.credential_var in await page.locator('#summary').inner_text()
            assert await page.locator('#state').inner_text() != 'Pronto'
        await page.reload()
        await page.wait_for_selector('#work-card:not([hidden])')
        assert 'Prova browser:' in await page.locator('#description').inner_text()
        await page.get_by_text('Documenti e conoscenza', exact=True).click()
        await page.locator('#doc-title').fill('Trascrizione prova browser')
        await page.locator('#doc-source').fill('Test interfaccia locale')
        await page.locator('#doc-content').fill('Le richieste ripetute devono mantenere la stessa attività; controllare idempotenza e SQLite.')
        await page.get_by_role('button', name='Salva documento', exact=True).click()
        await expect(page.locator('#document-result')).to_contain_text('salvato')
        await page.reload()
        await page.get_by_text('Documenti e conoscenza', exact=True).click()
        await expect(page.locator('#documents')).to_contain_text('Trascrizione prova browser')
        await page.set_viewport_size({'width': 390, 'height': 844})
        assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        await page.screenshot(path=str(output / 'interfaccia-mobile.png'), full_page=True)
        assert not errors, errors
        await browser.close()
    result = {'passed': True, 'browser': binary or 'playwright Chromium',
        'checks': ['pagina italiana', 'avvio progetto', 'credenziale assente: stato intervento',
                   'recupero dopo ricarica', 'documento persistente', 'layout 390px', 'nessun errore JavaScript'],
        'ai_verified': False, 'provider': settings.provider}
    (output / 'browser.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
