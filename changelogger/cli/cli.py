import os
import rich_click as click
from datetime import datetime
from rich.tree import Tree
from rich.console import Console
from changelogger import ChangelogFile, DEFAULT_EXPORTER
# > Typing
from typing import Callable, Literal, Optional, Any
# > Local Imports
from . import params

# ! Constants
DEFAULT_FILEPATH = os.path.abspath('changelog.yaml')
DEFAULT_OUTPUT_FILEPATH = os.path.abspath('changelog')

# ! Vars
console = Console()

# ! Runtime variables
debug = False
filepath = None
changelog = None

# ! Runtime Methods
def exceptor():
    def wrapper(method: Callable[..., Any]):
        def wrapped(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                if debug:
                    console.print_exception(show_locals=True, word_wrap=True, width=console.width)
                else:
                    console.print(f"[red]{e.__class__.__name__}[/red]: {e.__str__()}")
        return wrapped
    return wrapper

# ! Main (Group)
@click.group()
@click.option(
    '--filepath', '-f', 'fp',
    help='Path to changelog file.',
    type=click.Path(dir_okay=False, resolve_path=True, path_type=str),
    default=DEFAULT_FILEPATH, show_default=True
)
@click.option(
    '--debug', '-d', '_debug',
    help='Enable debug mode.',
    is_flag=True, default=False
)
@click.version_option(package_name='changelogger')
@exceptor()
def main(fp: str, _debug: bool):
    global filepath, changelog, debug
    debug = _debug
    filepath = fp
    changelog = ChangelogFile(filepath)

# ! Main (Group) > Commands
@main.command('create', help='Creating an empty changelog.')
@exceptor()
def create():
    global changelog
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
    changelog = ChangelogFile(filepath)

@main.command('tree', help='Displaying the changelog as a tree.')
@exceptor()
def tree():
    main_tree = Tree(f'\\[[yellow]{os.path.basename(changelog.filepath)}[/yellow]]', highlight=True)
    change_types_tree = main_tree.add('\\[[magenta]change_types[/magenta]]')
    for idx, change_type in enumerate(changelog.data.change_types.items()):
        change_types_tree.add(f'{idx}: {repr(change_type)}')
    versions_tree = main_tree.add('\\[[magenta]versions[/magenta]]')
    for version in changelog.data.versions.values():
        version_datetime = datetime.fromtimestamp(version.date)
        version_tree = versions_tree.add(
            f'[yellow]v{version.version}[/yellow] ([bold not italic cyan]{version_datetime.day:02d}.{version_datetime.month:02d}.{version_datetime.year:04d}[/bold not italic cyan]) \\[[green]{version.tag.upper()}[/green]]'
        )
        for idx, change in enumerate(version.changes):
            version_tree.add(f'{idx}: {changelog.data.change_types[change.type]} [green]{change.description}[/green]')
    console.print(main_tree)

@main.command('export', help='Export changelog.')
@click.option(
    '-f', '--format', 'format',
    help='Selecting export of format.',
    type=click.STRING, default=DEFAULT_EXPORTER, show_default=True
)
@click.option(
    '-o', '--output', 'output',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    default=DEFAULT_OUTPUT_FILEPATH, show_default=True
)
@exceptor()
def export(format: str, output: str):
    changelog.export(output, format)

@main.group('change', help='Managing change logs.')
@exceptor()
def change():
    pass

@main.group('version', help='Version log management.')
@exceptor()
def version():
    pass

# ! Main (Group) > Change (Group) > Commands
@change.command('add', help='Adding a change.')
@click.argument('version', type=params.Version())
@click.argument('change_type', type=click.STRING)
@click.argument('description', type=click.STRING)
@exceptor()
def add_change(version: str, change_type: str, description: str):
    changelog.add_change(version, change_type, description)

@change.command('remove', help='Removing a change.')
@click.argument('version', type=params.Version())
@click.argument('index', type=click.INT)
@exceptor()
def remove_change(version: str, index: int):
    changelog.remove_change(version, index)

@change.command('edit', help='Editing a change.')
@click.argument('version', type=params.Version())
@click.argument('index', type=click.INT)
@click.option(
    '-t', '--type', 'tp',
    type=click.STRING, default=None
)
@click.option(
    '-d', '--description', 'description',
    type=click.STRING, default=None
)
@exceptor()
def edit_change(
    version: str,
    index: int,
    tp: Optional[str]=None,
    description: Optional[str]=None
):
    if tp is not None:
        changelog.data.versions[version].changes[index].type = tp
    if description is not None:
        changelog.data.versions[version].changes[index].description = description
    changelog.refresh()

@change.command('sort', help='Sorting a changes.')
@click.argument('version', type=params.Version())
@click.argument('by', type=click.Choice(['type-text', 'type-index']))
@exceptor()
def sort_change(version: str, by: Literal['type-text', 'type-index']):
    if by == 'type-text':
        changelog.data.versions[version].changes.sort(
            key=lambda change: change.type
        )
    elif by == 'type-index':
        ctsi = {change_type: idx for idx, change_type in enumerate(changelog.data.change_types)}
        changelog.data.versions[version].changes.sort(
            key=lambda change: ctsi[change.type]
        )
    else:
        raise ValueError(by)
    changelog.refresh()

# ! Main (Group) > Version (Group) > Commands
@version.command('add', help='Adding a version.')
@click.argument('version', type=params.Version())
@click.argument('date', type=click.DateTime(['%d.%m.%Y', '%d.%m.%Y-%H:%M:%S', '%d.%m.%Y %H:%M:%S']))
@click.argument('url', type=params.URL())
@click.argument('tag', type=click.STRING)
@exceptor()
def add_version(version: str, date: float, url: str, tag: str):
    changelog.add_version(version, date, url, tag)

@version.command('remove', help='Removing a version.')
@click.argument('version', type=params.Version())
@exceptor()
def remove_version(version: str):
    changelog.remove_version(version)

@version.command('sort', help='Sorting a versions.')
@click.argument('by', type=click.Choice(['version']))
@exceptor()
def sort_version(by: Literal['version']):
    if by == 'version':
        changelog.data.versions = {
            key: value for key, value in sorted(list(changelog.data.versions.items()), key=lambda x: x[0])
        }
    changelog.refresh()