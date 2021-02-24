# playing with fabric for common jobs

from invoke import task


@task
def refresh_uwsgi(c):
    c.run("python3 ./manage.py collectstatic --noinput")
    path = '/etc/uwsgi/apps-enabled/redpot-unchained.ini'
    print(f'Reloading uwsgi daemon ({path})')
    c.run(f"touch {path}")
