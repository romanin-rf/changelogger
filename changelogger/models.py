from pydantic import BaseModel
from typing import List, Dict, Any

# ! ChangelogFile Models
class Change(BaseModel):
    type: str
    description: str

class Version(BaseModel):
    version: str
    date: float
    url: str
    tag: str
    changes: List[Change]=[]

class ChangeLog(BaseModel):
    exporters_extra: Dict[str, Dict[str, Any]] = {}
    change_types: Dict[str, str] = {}
    versions: Dict[str, Version] = {}

DEFAULT_CHANGELOG_DATA = ChangeLog().model_dump(warnings=False)