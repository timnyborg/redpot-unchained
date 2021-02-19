An unusually busy app might look like this:

```
~/redpot-unchained/apps/

tutor/
  __init__.py
  fixtures/
    module_status.yaml
  migrations/
  static/
  templates/
    tutor/
      view.html
      edit.html
      ...
  templatetags/
    __init__.py
    tutor_tags.py
  __init__.py
  admin.py
  apps.py
  datatables.py
  forms.py
  menus.py
  models.py
  tasks.py
  tests.py
  urls.py
  utils.py
  views.py
```

## datatables.py
Contains:

 * `django_tables2.Table` classes used in the application's views
 * `django_filters.FilterSet` classes used with those tables (typically for searching). If the number of filters grows
   too large, it could be split into a filter_sets.py

## fixtures/
Contains:

* YAML or JSON files containing table data to make the application work on a
  new database. _e.g._ status tables, type tables, HESA tables like Nationality
  or Ethnicity.  The names should indicate the model, _e.g._ `nationality.yaml`
* YAML or JSON files containing fake table data needed for any integration
  tests. _e.g._ a tutor record and module record in order to test tutor
  payments.  The names should begin with `test_` and indicate which sort of
  tests they're used for, _e.g._ `test_tutor_payments.yaml`.

    **Note:** it's probably better to use factory_boy than test fixtures, where possible

## forms.py
Contains:

 * `ModelForm` classes used in the application's views

## menus.py
Contains:

* Any app-specific menus defined using `django-simple-menu`'s `Menu.add_item()`

## models.py
Contains:

* `Model` classes
* `Manager` classes
* `QuerySet` classes

If this file grows too large, it may make sense to replace it with a `models/` folder, with a `.py` file for each
module or group of modules, though too many models may be a sign that the app is too large.

## tasks.py
Contains:

* Functions that are Celery tasks, marked with the `@shared_task` decorator.

The functions should be kept thin, essentially wrapping other function calls where possible.

## tests.py
Contains:

* `TestCase` classes

If the app is quite small, the tests may fit in a single file.

For larger applications, a `tests/` folder with multiple `test_*.py` files will be better:
```
tests/
  test_forms.py
  test_validators.py
  test_views.py
```

## urls.py
Contains:

* URL routing for the application, inherited by the project's master `urls.py`

## utils.py
Contains:

* Helper functions. _e.g._ string or date transforms, unicode stuff.
