'use strict';
const $ = id => document.getElementById(id);
let token = '', selected = localStorage.getItem('officina-project'), current = null, editingProcedure = null;
let busy = false, stopped = false;
const hide = (id, value) => { $(id).hidden = value; };
const text = (id, value) => { $(id).textContent = value || ''; };
function report(error) { text('error', error.message || String(error)); hide('error', false); }
async function api(path, body, method) {
  const response = await fetch('/api' + path, {method: method || (body === undefined ? 'GET' : 'POST'),
    headers: body === undefined ? {} : {'Content-Type': 'application/json', 'X-App-Token': token},
    body: body === undefined ? undefined : JSON.stringify(body)});
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Controlla i dati inseriti.');
  }
  return response.json();
}
function fillList(id, items) {
  $(id).replaceChildren(...items.map(item => { const li = document.createElement('li'); li.textContent = item; return li; }));
}
async function listProjects() {
  const projects = await api('/projects');
  $('projects').replaceChildren(...projects.map(p => {
    const button = document.createElement('button'); button.className = 'project' + (p.id === selected ? ' selected' : '');
    button.textContent = p.description.slice(0, 75);
    const small = document.createElement('small'); small.textContent = p.state; button.append(small);
    button.onclick = () => { select(p.id); refresh().catch(report); }; return button;
  }));
}
function select(id) {
  selected = id; current = null;
  if (id) localStorage.setItem('officina-project', id); else localStorage.removeItem('officina-project');
  hide('goal-card', Boolean(id)); hide('work-card', !id); hide('error', true);
}
function render(p) {
  current = p;
  text('state', p.state); $('state').className = 'badge' + (p.state === 'Pronto' ? ' ready' : p.state === 'Serve il tuo intervento' ? ' intervention' : '');
  text('pause-state', p.control === 'pause' ? 'Pausa richiesta / in pausa' : '');
  text('summary', p.summary); text('description', p.description); text('next-step', p.next_step);
  text('outcome', p.outcome || 'Il risultato atteso non è ancora stato definito.');
  fillList('plan', p.plan || []); fillList('criteria', p.criteria || []); fillList('files', p.files || []);
  const cost = p.estimated_cost === null ? 'Costo non disponibile: prezzi del modello non configurati.' : `Costo stimato: $${p.estimated_cost.toFixed(4)} USD.`;
  text('usage', `${p.model_calls} chiamate IA · ${p.tool_calls} operazioni · ${p.input_tokens} token in ingresso · ${p.output_tokens} token in uscita. ${cost}`);
  text('check', p.last_check ? JSON.stringify(p.last_check, null, 2) : 'Nessuna prova eseguita. Il progetto non è ancora verificato.');
  text('events', p.events.map(e => `${new Date(e.created).toLocaleString('it-IT')} · ${e.kind}\n${JSON.stringify(e.detail, null, 2)}`).join('\n\n'));
  $('pause').disabled = !p.worker_active || p.control === 'pause' || p.state === 'Pronto';
  $('resume').disabled = p.state === 'Pronto' || Boolean(p.question) || (p.worker_active && p.control === 'run');
  $('stop').disabled = !p.worker_active || p.state === 'Pronto';
  hide('answer-form', !p.question); text('question', p.question);
  hide('download', !p.files.length); $('download').href = `/api/projects/${p.id}/download`;
  hide('evidence', !p.last_check);
  if (p.last_check) {
    const check = p.last_check.check || {};
    const passedMessage = p.verified_hash ? `${check.unit_tests} test del progetto passati. Verifiche indipendenti: ${(check.contract || []).join(', ')}.` : 'L’ultima prova era passata, ma i file sono cambiati. Occorre ripetere le verifiche.';
    text('evidence', p.last_check.passed ? passedMessage : 'Una verifica è fallita o non si è completata. L’agente deve correggere il problema e ripetere le prove.');
    $('evidence').className = 'notice' + (p.last_check.passed ? '' : ' error');
  }
  const oldVersion = $('versions').value;
  $('versions').replaceChildren(...p.versions.map(v => { const option = document.createElement('option'); option.value = v.id; option.textContent = `${v.path} · prima della modifica #${v.id}`; return option; }));
  if (p.versions.some(v => String(v.id) === oldVersion)) $('versions').value = oldVersion;
  $('rollback').disabled = p.worker_active || !p.versions.length;
}
async function refresh() {
  if (busy || stopped) return;
  busy = true;
  try { if (selected) render(await api(`/projects/${selected}`)); await listProjects(); }
  catch (error) { report(error); }
  finally { busy = false; }
}
$('new-project').onclick = () => { select(null); listProjects().catch(report); $('goal').focus(); };
$('goal-form').onsubmit = async event => {
  event.preventDefault(); $('start').disabled = true; hide('error', true);
  try { const p = await api('/projects', {description: $('goal').value}); select(p.id); await refresh(); }
  catch (error) { report(error); }
  finally { $('start').disabled = false; }
};
for (const action of ['pause', 'resume', 'stop']) $(action).onclick = async () => {
  try { await api(`/projects/${selected}/control`, {action}); await refresh(); } catch (error) { report(error); }
};
$('answer-form').onsubmit = async event => {
  event.preventDefault();
  try { await api(`/projects/${selected}/answer`, {answer: $('answer').value}); $('answer').value = ''; await refresh(); }
  catch (error) { report(error); }
};
$('rollback').onclick = async () => {
  try { await api(`/projects/${selected}/rollback`, {version_id: Number($('versions').value)}); await refresh(); }
  catch (error) { report(error); }
};
async function loadDocuments() {
  const docs = await api('/documents');
  fillList('documents', docs.map(d => `${d.title} · ${d.source_date} · ${d.source}`));
}
$('doc-date').value = new Date().toLocaleDateString('en-CA');
$('doc-file').onchange = async () => {
  const file = $('doc-file').files[0]; if (!file) return;
  if (file.size > 64000 || !/\.(txt|md)$/i.test(file.name)) { report(new Error('Usa un file .txt o .md entro 64 KB.')); return; }
  $('doc-content').value = await file.text(); if (!$('doc-title').value) $('doc-title').value = file.name;
  if (!$('doc-source').value) $('doc-source').value = `Documento locale: ${file.name}`;
};
$('document-form').onsubmit = async event => {
  event.preventDefault();
  try { await api('/documents', {title: $('doc-title').value, source: $('doc-source').value, source_date: $('doc-date').value, content: $('doc-content').value});
    text('document-result', 'Documento salvato.'); await loadDocuments();
  } catch (error) { report(error); }
};
async function loadProcedures() {
  const procedures = await api('/procedures');
  $('procedures').replaceChildren(...procedures.map(p => {
    const div = document.createElement('div'); div.className = 'procedure-item';
    const name = document.createElement('strong'); name.textContent = `${p.title} · v${p.version} · ${p.status}`; div.append(name);
    const guidance = document.createElement('p'); guidance.textContent = p.guidance; div.append(guidance);
    function button(label, handler, disabled=false) { const b = document.createElement('button'); b.textContent = label; b.className = 'secondary'; b.disabled = disabled; b.onclick = handler; div.append(b); }
    button('Modifica come nuova versione', () => {
      editingProcedure = p.id; $('proc-title').value = p.title; $('proc-trigger').value = p.trigger; $('proc-guidance').value = p.guidance;
      $('proc-example').value = p.examples[0].prompt; $('proc-expected').value = p.examples[0].expected_contains.join(', ');
      text('save-procedure', `Salva nuova versione dopo v${p.version}`); $('proc-guidance').focus();
    });
    button('Prova sull’esempio con IA', async () => {
      text('procedure-result', 'Prova in corso. Attendi il risultato.');
      try { const r = await api(`/procedures/${p.id}/test`, {}); text('procedure-result', r.passed ? 'Esempio superato. Puoi adottare questa versione.' : (r.error || 'Esempio non superato. Consulta i risultati e modifica la procedura.')); await loadProcedures(); }
      catch (error) { report(error); }
    }, p.status === 'attiva');
    button(p.status === 'attiva' ? 'Disattiva' : 'Adotta versione verificata', async () => {
      try { await api(`/procedures/${p.id}/${p.status === 'attiva' ? 'deactivate' : 'activate'}`, {}); await loadProcedures(); } catch (error) { report(error); }
    }, !['attiva', 'verificata'].includes(p.status));
    if (p.test_result) { const details = document.createElement('details'); const summary = document.createElement('summary'); summary.textContent = 'Risultati dell’esempio'; const pre = document.createElement('pre'); pre.textContent = JSON.stringify(p.test_result, null, 2); details.append(summary, pre); div.append(details); }
    return div;
  }));
}
$('procedure-form').onsubmit = async event => {
  event.preventDefault();
  try {
    const body = {title: $('proc-title').value, trigger: $('proc-trigger').value, guidance: $('proc-guidance').value,
      examples: [{prompt: $('proc-example').value, expected_contains: $('proc-expected').value.split(',').map(x => x.trim()).filter(Boolean)}]};
    const result = await api(editingProcedure ? `/procedures/${editingProcedure}` : '/procedures', body, editingProcedure ? 'PUT' : 'POST');
    editingProcedure = null; text('save-procedure', 'Salva bozza'); text('procedure-result', `Versione ${result.version} salvata come bozza. Provala prima di adottarla.`); await loadProcedures();
  } catch (error) { report(error); }
};
async function start() {
  token = (await api('/session')).token;
  const health = await api('/health');
  text('configuration', `${health.ai_configured ? 'Chiave API configurata; autenticazione da verificare con una chiamata reale.' : 'Chiave API mancante: l’agente non può ancora iniziare.'} ${health.sandbox.available ? 'Immagine Docker disponibile; le prove verificheranno l’esecuzione.' : health.sandbox.reason}`);
  const l = health.limits;
  text('limits', `Limiti per progetto: ${l.model_calls} chiamate IA, ${l.tool_calls} operazioni, ${l.corrections} correzioni, ${l.tokens} token, ${l.seconds} secondi; ${l.command_seconds} secondi per comando.`);
  select(selected); await refresh(); await loadDocuments(); await loadProcedures();
  setInterval(() => refresh(), 2000);
}
window.addEventListener('pagehide', () => { stopped = true; });
start().catch(report);
