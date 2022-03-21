## Celery
Redpot uses the `celery` library to run periodic and adhoc asynchronous tasks, with `Redis` as the message queue,
and the `django-celery-beat` and`django-celery-results` libraries managed schedules and results in the database.

## Defining tasks
Following celery's default configuration, any function you wish to make schedulable
should be placed in an app's `tasks.py`, and decorated `@app.task`:

```python
# apps/app_name/tasks.py
from redpot.celery import app

@app.task()
def my_task():
    ...
```

### Named tasks
If you plan to run the task on a schedule, it's best to give it a name, because the default name
(`apps.app_name.tasks.my_task`) isn't great to work with in the UI.  Naming it the same as the function is clearer:

```python
@app.task(name='my_task')
def my_task():
    ...
```

### Parameters
Where a task needs arguments, it's best-practice to enforce keyword arguments (as in services), to make the settings
obvious within the application and in admin-scheduled tasks.  Defaults are useful where there are defined business rules
that might be subject to change in the future:

```python
@app.task()
def my_task(*, years=5, months=0):
    ...
```

### Emails on task error
If you want wish to receive an email if the task fails, add the `@mail_on_failure` decorator **below** `@app.task`:
```python
from apps.core.utils.celery import mail_on_failure

@app.task()
@mail_on_failure
def my_task():
    ...
```

This will email `SUPPORT_EMAIL` whenever the task fails.

However, this is really just a holdover from redpot-legacy.  With Redpot setup to forward errors to Sentry.io, all task
errors are logged, and notification emails can be customized.

### Progress notifications
If the task is designed to be queued by users, and you wish to provide progress updates, use the `task_progress` app, which wraps the `celery-progress` library.

#### Redirecting to the progress page
After queueing a task, redirect to the `task:progress` view, along with the task's uuid:

```python
# views.py
from .tasks import my_task

class MyView(FormView):
    ...
    def form_valid(self, form):
        task = tasks.my_task.delay()
        return redirect('task:progress', task_id=task.id)
```

#### Providing progress updates from the task
You'll need to use a `ProgressRecorder`.  To redirect the user from the progress page once it completes, return a
`dict` with a `redirect` key:

```python
# tasks.py
from celery_progress.backend import ProgressRecorder

from redpot.celery import app

@app.task(bind=True)
def my_task(self):
    recorder = ProgressRecorder(self)
    recorder.set_progress(current=1, total=10, description='Starting task')
    ...
    recorder.set_progress(current=2, total=10, description='Doing stuff')
    ...
    return {'redirect': '/redirect/url'}
```


## Scheduling tasks
Once defined, the task can then be scheduled from the Redpot admin site, under **Periodic tasks**.

We typically want our tasks to run at the same time every day, and so use crontab schedules.

## Architecture
Celery is run in its own container, which uses the same image as the Django/uwsgi containers, but simply runs a
different `COMMAND`: `celery -A redpot worker --beat` as opposed to `uwsgi`

### Beats
Because our tasks have very low throughput, we only run a single celery container, and it also includes the
`celery beat` daemon to do the scheduling.

If there's ever a need to scale up to multiple celery containers, the `beat` daemon will need to be separated into a
dedicated container.  Only one beat instance should ever be running (to avoid doubled task runs).
