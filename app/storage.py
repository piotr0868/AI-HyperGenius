import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
import hashlib


def now():
    return datetime.now(timezone.utc).isoformat()


def terms(text):
    ignored = {"che", "per", "con", "una", "del", "della", "dei", "gli", "alla", "come", "voglio", "questo"}
    return list(dict.fromkeys(w.lower() for w in re.findall(r"[\wÀ-ÿ]{3,}", text) if w.lower() not in ignored))[:18]


class Store:
    def __init__(self, data_dir: Path):
        self.root = data_dir
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.root / "memory.sqlite3", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
          id TEXT PRIMARY KEY, description TEXT NOT NULL, state TEXT NOT NULL,
          summary TEXT NOT NULL, next_step TEXT NOT NULL, created TEXT NOT NULL,
          updated TEXT NOT NULL, control TEXT NOT NULL DEFAULT 'run',
          criteria TEXT NOT NULL DEFAULT '[]', plan TEXT NOT NULL DEFAULT '[]',
          question TEXT, history TEXT NOT NULL DEFAULT '[]',
          model_calls INTEGER NOT NULL DEFAULT 0, tool_calls INTEGER NOT NULL DEFAULT 0,
          input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
          estimated_cost REAL, failed_checks INTEGER NOT NULL DEFAULT 0,
          verified_hash TEXT, last_check TEXT, elapsed REAL NOT NULL DEFAULT 0,
          outcome TEXT NOT NULL DEFAULT '', docs_consulted INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          created TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS versions (
          id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          path TEXT NOT NULL, content TEXT, created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS documents (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, source TEXT NOT NULL,
          source_date TEXT NOT NULL, added TEXT NOT NULL, content TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge USING fts5(
          doc_id UNINDEXED, title, content, tokenize='unicode61'
        );
        CREATE TABLE IF NOT EXISTS procedures (
          id TEXT PRIMARY KEY, family TEXT NOT NULL, version INTEGER NOT NULL,
          title TEXT NOT NULL, trigger TEXT NOT NULL, guidance TEXT NOT NULL,
          examples TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'bozza',
          test_result TEXT, created TEXT NOT NULL
        );
        """)
        self.db.commit()

    def close(self):
        self.db.close()

    def rows(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def execute(self, sql, args=()):
        with self.lock, self.db:
            return self.db.execute(sql, args).lastrowid

    def create_project(self, description):
        pid = uuid.uuid4().hex
        timestamp = now()
        self.execute("""INSERT INTO projects
          (id,description,state,summary,next_step,created,updated)
          VALUES(?,?,'Preparazione','Obiettivo ricevuto.','Definire risultato e verifiche.',?,?)""",
          (pid, description, timestamp, timestamp))
        self.workspace(pid).mkdir(parents=True)
        self.event(pid, "requisiti", {"description": description})
        return self.project(pid)

    def project(self, pid):
        rows = self.rows("SELECT * FROM projects WHERE id=?", (pid,))
        if not rows:
            raise KeyError("Progetto non trovato")
        row = rows[0]
        for key in ("criteria", "plan", "history", "last_check"):
            row[key] = json.loads(row[key]) if row[key] else None
        return row

    def update(self, pid, **values):
        allowed = {"state", "summary", "next_step", "control", "criteria", "plan", "question", "history",
                   "model_calls", "tool_calls", "input_tokens", "output_tokens", "estimated_cost",
                   "failed_checks", "verified_hash", "last_check", "elapsed", "outcome", "docs_consulted"}
        if not set(values) <= allowed:
            raise ValueError("Campo non consentito")
        values = {k: json.dumps(v, ensure_ascii=False) if k in ("criteria", "plan", "history", "last_check") else v
                  for k, v in values.items()}
        values["updated"] = now()
        self.execute("UPDATE projects SET " + ",".join(f"{k}=?" for k in values) + " WHERE id=?",
                     (*values.values(), pid))

    def event(self, pid, kind, detail):
        self.execute("INSERT INTO events(project_id,created,kind,detail) VALUES(?,?,?,?)",
                     (pid, now(), kind, json.dumps(detail, ensure_ascii=False)))

    def events(self, pid):
        rows = self.rows("SELECT * FROM events WHERE project_id=? ORDER BY id DESC LIMIT 200", (pid,))
        for row in rows:
            row["detail"] = json.loads(row["detail"])
        return rows

    def recover(self):
        for row in self.rows("SELECT id FROM projects WHERE state IN ('Preparazione','Lavoro','Verifica')"):
            self.update(row['id'], state="Serve il tuo intervento", control="pause", question=None,
                        summary="L'applicazione è stata chiusa. File e memoria sono conservati.",
                        next_step="Premi Riprendi per continuare dalle verifiche.")
            self.event(row['id'], "recupero", {"message": "Processo precedente interrotto; nessuna verifica presunta."})

    def workspace(self, pid):
        if not re.fullmatch(r"[a-f0-9]{32}", pid):
            raise ValueError("Identificativo non valido")
        return self.root / "projects" / pid / "workspace"

    def safe_path(self, pid, name):
        if not name or len(name) > 200 or '\\' in name or ':' in name:
            raise ValueError("Percorso non valido")
        relative = PurePosixPath(name)
        if relative.is_absolute() or any(p in ("..", ".git", ".env") or p.startswith('.') for p in relative.parts):
            raise ValueError("Percorso non consentito")
        if relative.suffix.lower() not in {".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".html", ".css", ".js", ".ts"}:
            raise ValueError("Tipo di file non consentito")
        base = self.workspace(pid).resolve()
        path = self.workspace(pid) / relative
        if any(p.is_symlink() for p in [path, *path.parents] if p != base.parent.parent.parent):
            raise ValueError("I collegamenti simbolici non sono consentiti")
        if not path.resolve().is_relative_to(base):
            raise ValueError("Percorso esterno al progetto")
        return path

    def files(self, pid):
        result = {}
        root = self.workspace(pid)
        for p in sorted(root.rglob('*')):
            if p.is_symlink():
                raise ValueError("Collegamento simbolico nel progetto")
            if p.is_file():
                name = p.relative_to(root).as_posix()
                self.safe_path(pid, name)
                result[name] = p.read_text(encoding='utf-8')
        return result

    def write_file(self, pid, name, content):
        if len(content.encode()) > 128000:
            raise ValueError("File troppo grande: massimo 128 KB")
        path = self.safe_path(pid, name)
        files = self.files(pid)
        files[name] = content
        if len(files) > 100 or sum(len(x.encode()) for x in files.values()) > 2000000:
            raise ValueError("Limite progetto: 100 file e 2 MB")
        old = path.read_text(encoding='utf-8') if path.exists() else None
        version = self.execute("INSERT INTO versions(project_id,path,content,created) VALUES(?,?,?,?)",
                               (pid, name, old, now()))
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_text(content, encoding='utf-8')
        tmp.replace(path)
        self.update(pid, verified_hash=None)
        self.event(pid, "file", {"path": name, "previous_version": version})
        return {"path": name, "previous_version": version}

    def rollback(self, pid, version_id):
        rows = self.rows("SELECT * FROM versions WHERE id=? AND project_id=?", (version_id, pid))
        if not rows:
            raise KeyError("Versione non trovata")
        row = rows[0]
        path = self.safe_path(pid, row['path'])
        if row['content'] is None:
            if path.exists():
                self.execute("INSERT INTO versions(project_id,path,content,created) VALUES(?,?,?,?)",
                             (pid, row['path'], path.read_text(), now()))
                path.unlink()
        else:
            self.write_file(pid, row['path'], row['content'])
        self.update(pid, verified_hash=None, state="Serve il tuo intervento",
                    summary="Versione precedente ripristinata.", next_step="Riprendi e ripeti le verifiche.")
        self.event(pid, "ripristino", {"version": version_id})

    def digest(self, pid):
        payload = json.dumps(self.files(pid), sort_keys=True, ensure_ascii=False).encode()
        return hashlib.sha256(payload).hexdigest()

    def add_document(self, title, source, source_date, content):
        doc_id = uuid.uuid4().hex
        with self.lock, self.db:
            self.db.execute("INSERT INTO documents VALUES(?,?,?,?,?,?)",
                            (doc_id, title, source, source_date, now(), content))
            for start in range(0, len(content), 2400):
                self.db.execute("INSERT INTO knowledge(doc_id,title,content) VALUES(?,?,?)",
                                (doc_id, title, content[start:start + 2800]))
        return doc_id

    def search(self, query):
        words = terms(query)
        if not words:
            return []
        match = ' OR '.join('"' + w + '"' for w in words)
        candidates = self.rows("""SELECT d.id,d.title,d.source,d.source_date,k.content
          FROM knowledge k JOIN documents d ON d.id=k.doc_id
          WHERE knowledge MATCH ? ORDER BY bm25(knowledge) LIMIT 100""", (match,))
        result, seen = [], set()
        for candidate in candidates:
            if candidate['id'] not in seen:
                seen.add(candidate['id'])
                result.append(candidate)
            if len(result) == 4:
                break
        return result

    def relevant_procedures(self, query):
        words = set(terms(query))
        return [r for r in self.rows("SELECT title,trigger,guidance,version FROM procedures WHERE status='attiva'")
                if words.intersection(terms(r['trigger']))][:3]
