from string import Formatter
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any
from .models import ChangeLog

# ! Formatter
class ExtendedFormatter(Formatter):
    def convert_field(self, value: Any, conversion: Optional[str]) -> str:
        string_value = str(value)
        if conversion == 'U':
            return string_value.upper()
        elif conversion == 'L':
            return string_value.lower()
        elif conversion == 'T':
            return string_value.title()
        elif conversion == 'H':
            return string_value.capitalize()
        elif conversion == 'C':
            return string_value.casefold()
        elif conversion == 'R':
            return string_value.swapcase()
        elif conversion == 'S':
            return string_value.strip()
        return super().convert_field(value, conversion)

# ! Exporter Base
class ExporterBase:
    def __init__(self, **extra: Any) -> None:
        self.extra = extra
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.extra})'
    
    def export(self, filepath: str, data: ChangeLog) -> None:
        raise NotImplementedError

# ! Markdown Version
class MarkdownTableExporterExtra(BaseModel):
    encoding: str = "utf-8"
    errors: str = "ignore"
    version_sep: str = "\n"
    change_sep: str = "<br>"
    start: List[str] = [
        "| Version | Date | Tag | Changes |",
        "| ------- | ---- | --- | ------- |"
    ]
    end: List[str] = []
    date_format: str = "{date.day:02d}.{date.month:02d}.{date.year:04d}"
    change_format: str = "{emoji} {description}"
    version_format: str = "| [v{version}]({url}) | {date} | **{tag!U}** | {changes} |"

# ! Markdown Exporter
class MarkdownTableExporter(ExporterBase):
    def __init__(self, **extra) -> None:
        self.extra = MarkdownTableExporterExtra(**extra)
        self.formatter = ExtendedFormatter()
    
    def export(self, filepath: str, data: ChangeLog) -> None:
        versions_data_lines = [ *self.extra.start ]
        for version in data.versions.values():
            changes_data_lines = []
            for change in version.changes:
                changes_data_lines.append(
                    self.formatter.format(
                        self.extra.change_format,
                        key=data.change_types[change.type],
                        emoji=data.change_types[change.type],
                        description=change.description
                    )
                )
            versions_data_lines.append(
                self.formatter.format(
                    self.extra.version_format,
                    version=version.version,
                    url=version.url,
                    date=self.formatter.format(
                        self.extra.date_format,
                        date=datetime.fromtimestamp(version.date)
                    ),
                    tag=version.tag,
                    changes=self.extra.change_sep.join(changes_data_lines)
                )
            )
        versions_data_lines += self.extra.end
        with open(
            filepath, 'w',
            encoding=self.extra.encoding,
            errors=self.extra.errors
        ) as file:
            file.write(self.extra.version_sep.join(versions_data_lines))

# ! Vars

DEFAULT_MARKDOWN_EXTRA = MarkdownTableExporterExtra().model_dump(warnings=False)
