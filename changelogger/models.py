from pydantic import BaseModel
from typing import Tuple, List, Dict, Any

# ! ChangelogFile Models
class ChangelogDataChange(BaseModel):
    type: str
    description: str

class ChangelogDataVersion(BaseModel):
    version: str
    date: float
    url: str
    tag: str
    changes: List[ChangelogDataChange]=[]

class ChangelogData(BaseModel):
    exporters_extra: Dict[str, Dict[str, Any]] = {}
    change_types: Dict[str, str] = {}
    versions: Dict[str, ChangelogDataVersion] = {}