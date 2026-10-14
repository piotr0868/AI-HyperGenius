'use strict';
const form = document.getElementById('form');
const title = document.getElementById('title');
const save = document.getElementById('save');
const status = document.getElementById('esito');
let pending = null;
async function refresh() {
  const response = await fetch('/activities');
  if (!response.ok) throw new Error('Non riesco a leggere le attività. Riprova tra poco.');
  const items = await response.json();
  const list = document.getElementById('items');
  list.replaceChildren();
  for (const item of items) {
    const row = document.createElement('li');
    row.textContent = item.title;
    list.append(row);
  }
  if (!items.length) {
    const row = document.createElement('li');
    row.textContent = 'Ancora nessuna attività.';
    list.append(row);
  }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  const text = title.value.trim();
  if (!text) { status.textContent = 'Scrivi prima il nome dell’attività.'; title.focus(); return; }
  if (!pending || pending.title !== text) pending = {title: text, key: crypto.randomUUID()};
  save.disabled = true;
  status.textContent = 'Salvataggio in corso…';
  try {
    const response = await fetch('/activities', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Idempotency-Key': pending.key},
      body: JSON.stringify({title: pending.title})
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Salvataggio non completato.');
    pending = null;
    title.value = '';
    await refresh();
    status.textContent = 'Attività salvata.';
    title.focus();
  } catch (error) {
    status.textContent = error instanceof TypeError ? 'Connessione interrotta. Premi Salva attività per riprovare.' : error.message;
  } finally { save.disabled = false; }
});
refresh().catch(error => { status.textContent = error.message; });
