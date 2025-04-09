import os
from pathlib import Path
from datetime import datetime
# > PyYAML
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper
# > Typing
from typing import Type, Callable, TypeVar, Union, Mapping, Sequence, Iterable, Tuple, Dict, List, Any
# > Local Imports
from .models import ChangeLog, Version, Change, DEFAULT_CHANGELOG_DATA
from .exporter import ExporterBase
from .exceptions import (
    VersionExistError, VersionNotExistError,
    ChangeTypeKeyError, ChangeTypeEmojiNotCorrectError
)
from .units import (
    DEFAULT_EXPORTER,
    DEFAULT_EXPORTERS,
    DEFAULT_CHANGE_TYPES
)

# ! Type Alias
T = TypeVar('T')
ChangelogData = Dict[str, Any]
ExporterNameType = str
ExporterType = Type[ExporterBase]
ExporterExtraType = Dict[str, Any]

# ! Methods
def notwrap(data: ChangelogData) -> ChangelogData:
    return data

def notunwrap(data: ChangelogData) -> ChangelogData:
    return data

def defwrap(data: ChangelogData) -> ChangeLog:
    return ChangeLog.model_validate(data)

def defunwrap(data: ChangeLog) -> ChangelogData:
    return data.model_dump(warnings=False)

# ! Main Class
class ChangelogFile:
    # ! Private Initialization Methods
    def __dump(
        self,
        filepath: str,
        data: T,
        unwraping: Callable[[T], ChangelogData]=notunwrap
    ) -> None:
        with open(filepath, 'w') as file:
            yaml.dump(unwraping(data), file, Dumper=Dumper, sort_keys=False)
    
    def __load(
        self,
        filepath: str,
        wraping: Callable[[ChangelogData], T]=notwrap
    ) -> T:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            return wraping(yaml.load(file, Loader=Loader))
    
    def __loadump(
        self,
        filepath: str,
        default: ChangelogData
    ) -> ChangeLog:
        data = default.copy()
        if os.path.exists(filepath):
            try:
                data.update(self.__load(filepath))
            except OSError as e:
                raise e
            except:
                self.__dump(filepath, data)
        else:
            self.__dump(filepath, data)
        return defwrap(data)
    
    def __refresh(self) -> None:
        self.__dump(self.filepath, self.data, defunwrap)
    
    # ! Initialization
    def __init__(
        self,
        filepath: Union[str, Path],
        change_types: List[Tuple[str, str]]=DEFAULT_CHANGE_TYPES,
        exporters: List[Tuple[ExporterNameType, ExporterType, ExporterExtraType]]=DEFAULT_EXPORTERS
    ) -> None:
        self.filepath = os.path.abspath(Path(filepath))
        self.data = self.__loadump(self.filepath, DEFAULT_CHANGELOG_DATA)
        self.exporters: Dict[str, ExporterBase] = {}
        self.set_change_types(change_types)
        for format, exporter, extorter_extra in exporters:
            self.set_exporter_extra(format, extorter_extra)
            self.set_exporter(format, exporter)
    
    # ! Magic Methods
    def __enter__(self):
        return self
    
    def __exit__(*exc_info) -> None:
        pass
    
    # ! Main Methods
    def refresh(self) -> None:
        self.__refresh()
    
    # ! Version Methods
    def exist_version(self, __version: str) -> bool:
        return __version in self.data.versions.keys()
    
    def add_version(
        self,
        __version: str,
        __date: Union[int, float, datetime],
        __url: str,
        __tag: str,
        refresh: bool=True
    ) -> None:
        if self.exist_version(__version):
            raise VersionExistError(__version)
        if isinstance(__date, datetime):
            __date = __date.timestamp()
        else:
            __date = float(__date)
        self.data.versions[__version] = Version(version=__version, date=__date, url=__url, tag=__tag)
        if refresh:
            self.__refresh()
    
    def remove_version(self, __version: str, refresh: bool=True) -> None:
        if not self.exist_version(__version):
            raise VersionNotExistError(__version)
    
    # ! Change Methods
    def add_change(self, __version: str, __type: str, __description: str, refresh: bool=True) -> None:
        if not self.exist_version(__version):
            raise VersionNotExistError(__version)
        if not self.exist_change_type(__type):
            raise ChangeTypeKeyError(__type)
        self.data.versions[__version].changes.append(
            Change(
                type=__type, description=__description
            )
        )
        self.data.versions[__version].changes.sort(key=lambda change: change.type)
        if refresh:
            self.__refresh()
    
    def remove_change(self, __version: str, __index: int, refresh: bool=True) -> None:
        if not self.exist_version(__version):
            raise VersionNotExistError(__version)
        if not (len(self.data.versions[__version].changes) > __index >= 0):
            raise IndexError(__index)
        self.data.versions[__version].changes.pop(__index)
        if refresh:
            self.__refresh()
    
    # ! Change Types Methods
    def exist_change_type(self, __change_type: str) -> bool:
        return __change_type in self.data.change_types.keys()
    
    def add_change_type(self, __key: str, __emoji: str, refresh: bool=True) -> None:
        if self.exist_change_type(__key):
            raise ChangeTypeKeyError(__key)
        if len(__emoji) != 1:
            raise ChangeTypeEmojiNotCorrectError(__emoji)
        self.data.change_types[__key] = __emoji
        if refresh:
            self.__refresh()
    
    def remove_change_type(self, __key: str, refresh: bool=True) -> None:
        if not self.exist_change_type(__key):
            raise ChangeTypeKeyError(__key)
        self.data.change_types.pop(__key)
        if refresh:
            self.__refresh()
    
    def set_change_types(
        self,
        __change_types: Union[
            Dict[str, str],
            Mapping[str, str],
            Iterable[Tuple[str, str]],
            Sequence[Tuple[str, str]]
        ],
        refresh: bool=True
    ) -> None:
        if not isinstance(__change_types, (dict, Mapping, Iterable, Sequence)):
            raise TypeError(type(__change_types))
        self.data.change_types = dict(__change_types)
        if refresh:
            self.__refresh()
    
    # ! Exporter Methods
    def set_exporter_extra(self, __format: str, __extra: Dict[str, Any]={}, reinit: bool=False) -> None:
        self.data.exporters_extra[__format] = __extra
        self.__refresh()
        if reinit:
            self.exporters[__format].__init__(**__extra)
    
    def set_exporter(self, __format: str, __exporter: Type[ExporterBase]) -> None:
        self.exporters[__format] = __exporter(**self.data.exporters_extra[__format])
    
    def export(self, __filepath: str, __format: str=DEFAULT_EXPORTER) -> None:
        self.exporters[__format].export(__filepath, self.data)