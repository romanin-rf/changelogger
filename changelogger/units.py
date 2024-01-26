from .exporter import MarkdownTableExporter, DEFAULT_MARKDOWN_EXTRA

# ! Defaults
DEFAULT_CHANGE_TYPES = {
    'add': '➕',
    'remove': '➖',
    'fix': '🔧',
    'update': '🌟',
    'deprecate': '💀',
    'refactor': '🔁'
}
DEFAULT_EXPORTERS = [
    ('markdown-table', MarkdownTableExporter, DEFAULT_MARKDOWN_EXTRA)
]
DEFAULT_EXPORTER = 'markdown-table'