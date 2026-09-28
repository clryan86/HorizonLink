"""Persistent, reviewable knowledge records for HorizonLink.

The repository's knowledge/ directory is the durable store. This module defines
records that calculations and discovery runs can emit. Records are deliberately
separate from executable functions: evidence can mature before it is promoted
into a calculation method.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from typing import Any

@dataclass(frozen=True)
class KnowledgeRecord:
    key:str
    kind:str                 # known_result, benchmark, candidate, falsified, dataset
    statement:str
    status:str               # accepted, provisional, rejected
    evidence:tuple[str,...]=()
    assumptions:tuple[str,...]=()
    variables:tuple[str,...]=()
    value:Any=None
    source:str='HorizonLink'
    created_utc:str=''
    def as_dict(self):
        d=asdict(self)
        if not d['created_utc']: d['created_utc']=datetime.now(timezone.utc).isoformat()
        return d

def promoteable(record:KnowledgeRecord)->bool:
    """Only accepted records with evidence are eligible to seed new functions."""
    return record.status=='accepted' and bool(record.evidence)
