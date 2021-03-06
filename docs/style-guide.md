## Indentation, line endings , etc.
Basic code style rules (4-space indents for most languages, LF line endings,
etc.) are defined in [.editorconfig](https://gitlab.conted.ox.ac.uk/django/redpot-unchained/-/blob/master/.editorconfig)

.editorconfig is supported out of the box by PyCharm, and packages are
available for VSCode, Atom, etc.

## Multiline queries
Complicated queries are guaranteed to break the [PEP8 79-character limit](https://www.python.org/dev/peps/pep-0008/#maximum-line-length)
and become unreadable.

For example, this query that gets other runs of a module (`self`):
```python
other_runs =  Module.objects.filter(url=self.url, division=self.division).exclude(id=self.id).order_by(F('start_date').desc(nulls_last=True))
```

Python syntax allows a few approaches for splitting them across multiple lines.

### Extra lines per operation
```python
other_runs =  Module.objects.filter(
    url=self.url,
    division=self.division
).exclude(
    id=self.id
).order_by(
    F('start_date').desc(nulls_last=True)
)
```
Typically the longest, but very useful when you have many `filter` or `order_by` arguments

### Wrapped in parentheses
```python
other_runs =  (
    Module.objects
    .filter(url=self.url, division=self.division)
    .exclude(id=self.id)
    .order_by(F('start_date').desc(nulls_last=True))
)
```
Compact and readable.  Very useful when there are many short operations

### Line-continuation with \\
```python
other_runs = Module.objects\
             .filter(url=self.url, division=self.division)\
             .exclude(id=self.id)\
             .order_by(F('start_date').desc(nulls_last=True))\
```
The most compact, but arguable the ugliest.  The indentation varies wildly, depending on the variable name

### Or just use black
If you configure [pre-commit hooks](pre-commit-hooks.md), `black` will automatically format these long statements
according to their length.  You can also configure your IDE to run black (and isort) on file save
([details](https://black.readthedocs.io/en/stable/integrations/editors.html#pycharm-intellij-idea)).

## Organizing imports
Since more or less every file in Django is a module, many of them will end up filled with imports.

Extending [PEP8's guidelines](https://www.python.org/dev/peps/pep-0008/#imports), imports
should be at the top of the file, grouped in the following order:

1. Standard library imports (os, sys)
2. Third party imports (dateutil, django_filters, django_tables2, redis, requests)
3. Django core library (django.db.models, django.urls)
4. Other apps in the project (apps.module.models, apps.main.utils.mixins, redpot.settings)
5. The current app (.models, .views, .urls)

Each group should be separated by a line

### Example

```python
import os

from dateutil import relativedelta
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Coalesce

from apps.core.utils.views import PageTitleMixin
from apps.tutor.utils import expense_forms
from apps.discount.models import Discount

from .models import Module, ModuleStatus
from .forms import ModuleForm
from .datatables import ModuleSearchTable, WaitlistTable
```

### isort makes it easy
To automatically organize your imports, run `isort <filename>`, or run `isort .` to recursively reformat an entire directory (or project).

isort uses default settings in `pyproject.toml`

### pre-commit makes it easier!
Why run isort by hand, when you can do it automatically?

See [pre-commit hooks](pre-commit-hooks.md) for details
