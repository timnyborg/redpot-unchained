# Gotchas and challenges
The following is a list of issues and challenges discovered while attempting to port redpot code to Django.

## No auto-rollback by default	
Web2py runs each request in a single transaction, and rolls it all back if it hits an unhandled error, so you don't
end up with half of your database commands commited and the other half not.

Django runs in auto-commit mode, so each command is run independently.  If transactions are required, 
```transaction.atomic()``` can be used to wrap queries and commit them together.

For example, when creating fee lines and linking them to an invoice:
```python
with transaction.atomic():
    new_row = Ledger.objects.create(**data)
    myinvoice.ledger_items.add(new_row)
```

## Foreign keys fields are not implicitly integers	
Take an example of a standard foreign key relationship:
```python
class Module(models.Module):
    ...
    portfolio = models.ForeignKey('Portfolio', ...)
```
Imagine you want to check if the module has a particular portfolio.  
`if module.portfolio == 32` will not work, because `module.portfolio` is an object, and it does not implicitly cast itself into an int when used in comparisons.  Instead, you can use `if module.portfolio_id == 32

## QuerySet.get() throws an error if no record found
In web2py, a lookup like `idb.student(id=5)` will return a single record if found, or `None` if there are no matches.

The Django equivalent, `Student.objects.get()`, will throw an exception if no record is found (or more than one).
So, if you're uncertain whether a record exists or not, you have two options, `.first()` and catching the exception:
=== ".first()"
    ```python
    from .models import Student
    record = Student.objects.filter(pk=5).first()
    ```
=== "except ..."
    ```python
    from .models import Student
    try:
        record = Student.objects.get(pk=5)
    except Student.DoesNotExist:
        record = None
    ```

## Be careful about accidentally calling a QuerySet	
QuerySets are lazy, so they don't actually execute until you iterate over them, etc. 
If you go to test whether a variable **contains** a lazy queryset or is None, use `if variable is not None:`, not 
`if variable:`, because the latter will resolve the entire query and check if it has any results, before casting as 
bool!  

The following code caused the first module/view page loaded to take 5 seconds and fill 100MB of ram with the
entire contents of the Module table!

```python hl_lines="6 11"
class PageTitleMixin:
    ...
    
    def get_title(self):
        ...
        if hasattr(self, 'queryset') and self.queryset:
            # Automatically get model name for model views with a queryset
            return self.queryset.model._meta.verbose_name.capitalize()

class View(PageTitleMixin, DetailView):
    queryset = Module.objects.all()
    ...
```

## Forms require more tailoring	
For example, making sure they have `method='post'` or `enctype='multipart/form-data'` when handling files.  Much of the boilerplate can be handled with custom tags, though.

## Each project is its own wsgi application	
web2py acts as a wsgi application, and allows us to drag and drop into the /applications/ folder.  This means a
single uwsgi worker (defined in a single ini file) can serve any and all apps, and most code changes don't require
restarting the workers.

Each django project is its own wsgi application, with no scaffold around it, so it needs its own uwsgi ini and 
workers, and those workers need to be restarted whenever a code change is deployed.  

As a result, we may want to aggregate some apps together, especially as they can be very self-contained within a 
project.  No reason feedback-admin or staff-forms couldn't be rolled into redpot as side-apps.

This also has many benefits.  Django doesn't need to be installed at the server level, but can just be part of the
requirements that form each application's virtual environment.  It's easy to make containers.  Easy to setup a new
dev environment

## Migrations and test databases are awkward with unmanaged (legacy) tables
This is an interesting can of worms.  Django doesn't want to create migrations for unmanaged tables, but those 
migrations are useful for creating dev or test databases for automated unit tests, and for deploying database changes on live.  We may just do manual migrations on live for core tables, and automated migrations for django-controlled tables

## Auth tablenames conflict with web2py tables	(auth_permission, auth_group)
Simultaneous support could be tricky, but web2py allows us to use different table names, so we could migrate them to
non-conflicting names.