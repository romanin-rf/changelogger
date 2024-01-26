# ChangeLogger

## Description
A module for generating changelog in any format.

## Using
```python
from datetime import datetime
from changelogger import ChangelogFile

clf = ChangelogFile("test.yaml")

clf.add_version('0.1.0', datetime.now(), "https://example.com", 'pre-release')

clf.add_change('0.1.0', 'add', 'Added code')
clf.add_change('0.1.0', 'remove', 'Removed code')

clf.export('test.md')

print(clf.data)
```