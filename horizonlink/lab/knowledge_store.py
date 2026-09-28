"""SQLite knowledge store for HorizonLink research runs.

Stores scenarios, calculation outputs, candidate relationships, validation
results, and promoted knowledge. This is intentionally local and append-only by
default so research history is auditable.
"""
from __future__ import annotations
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any
from .runner import LabInput, LabReport

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 inputs_json TEXT NOT NULL,
 summary_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outputs(
 run_id INTEGER NOT NULL,
 calculation TEXT NOT NULL,
 category TEXT NOT NULL,
 status TEXT NOT NULL,
 output_name TEXT NOT NULL,
 output_value REAL,
 output_json TEXT,
 FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE TABLE IF NOT EXISTS candidates(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 x TEXT NOT NULL, y TEXT NOT NULL, model TEXT NOT NULL,
 score REAL NOT NULL, parameters_json TEXT NOT NULL,
 provenance_json TEXT, falsification_json TEXT,
 state TEXT NOT NULL DEFAULT 'candidate',
 notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS knowledge(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 key TEXT NOT NULL UNIQUE,
 kind TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 evidence TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'provisional'
);
"""

class KnowledgeStore:
    def __init__(self, path: str|Path="knowledge/horizonlink.sqlite3"):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path)
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self): self.db.close()

    def save_report(self, report:LabReport)->int:
        cur=self.db.execute("INSERT INTO runs(inputs_json,summary_json) VALUES (?,?)",
            (json.dumps(report.inputs,sort_keys=True),json.dumps(report.summary,sort_keys=True)))
        run_id=int(cur.lastrowid)
        for calc in report.calculations:
            if calc.outputs:
                for name,value in calc.outputs.items():
                    numeric=float(value) if isinstance(value,(int,float)) else None
                    self.db.execute("""INSERT INTO outputs
                    (run_id,calculation,category,status,output_name,output_value,output_json)
                    VALUES (?,?,?,?,?,?,?)""",
                    (run_id,calc.name,calc.category,calc.status,name,numeric,
                     None if numeric is not None else json.dumps(value,sort_keys=True)))
            else:
                self.db.execute("""INSERT INTO outputs
                (run_id,calculation,category,status,output_name,output_json)
                VALUES (?,?,?,?,?,?)""",(run_id,calc.name,calc.category,calc.status,"__status__",
                json.dumps({"error":calc.error,"notes":calc.notes})))
        self.db.commit()
        return run_id

    def save_candidate(self,candidate:dict[str,Any],*,provenance=None,falsification=None,notes="")->int:
        cur=self.db.execute("""INSERT INTO candidates
        (x,y,model,score,parameters_json,provenance_json,falsification_json,notes)
        VALUES (?,?,?,?,?,?,?,?)""",(
            candidate["x"],candidate["y"],candidate["model"],float(candidate["score"]),
            json.dumps(candidate.get("parameters",{}),sort_keys=True),
            json.dumps(provenance,sort_keys=True) if provenance is not None else None,
            json.dumps(falsification,sort_keys=True) if falsification is not None else None,notes))
        self.db.commit(); return int(cur.lastrowid)

    def promote(self,key:str,kind:str,payload:dict[str,Any],*,evidence="",status="validated"):
        self.db.execute("""INSERT INTO knowledge(key,kind,payload_json,evidence,status)
        VALUES (?,?,?,?,?)
        ON CONFLICT(key) DO UPDATE SET kind=excluded.kind,payload_json=excluded.payload_json,
        evidence=excluded.evidence,status=excluded.status""",
        (key,kind,json.dumps(payload,sort_keys=True),evidence,status))
        self.db.commit()

    def knowledge_items(self,status:str|None=None):
        if status is None:
            rows=self.db.execute("SELECT key,kind,payload_json,evidence,status FROM knowledge ORDER BY key")
        else:
            rows=self.db.execute("SELECT key,kind,payload_json,evidence,status FROM knowledge WHERE status=? ORDER BY key",(status,))
        return [{"key":k,"kind":kind,"payload":json.loads(p),"evidence":e,"status":s} for k,kind,p,e,s in rows]
