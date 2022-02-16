# Adapted from https://www.caktusgroup.com/blog/2017/03/14/production-ready-dockerfile-your-python-django-app/
# Specify debian version to avoid breaking on new version releases (needs syncing with microsoft packages)
FROM python:3.9-slim-bullseye

# Create a group and user to run our app
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

# Add microsoft package repository
RUN apt-get update && apt-get install -y curl gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install packages needed to run your application (not build deps):
ENV ACCEPT_EULA=Y
RUN apt-get update && apt-get install -y --no-install-recommends \
      # odbc drivers
      msodbcsql18 \
      # git required while we have repos in requirements
      git \
      # weasyprint prereqs
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python packages
COPY requirements.txt /requirements.txt

# Install build deps, install python packages, then remove build deps in a single step - key for keeping size down
RUN BUILD_DEPS=" \
    build-essential \
    unixodbc-dev \
    libsasl2-dev \
    libldap2-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir uwsgi \
    \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Application code
RUN mkdir /code/ \
    && chown ${APP_USER}:${APP_USER} /code/
WORKDIR /code/
ADD --chown=${APP_USER}:${APP_USER} . /code/

# uWSGI will listen on this port
EXPOSE 8000

# Call collectstatic
RUN python manage.py collectstatic --noinput \
# build the mkdocs
  && mkdocs build

# Tell uWSGI where to find your wsgi file
ENV UWSGI_WSGI_FILE=redpot/wsgi.py

# Base uWSGI configuration
ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_LAZY_APPS=1

# Number of uWSGI workers and threads per worker
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

# Change to a non-root user
USER ${APP_USER}:${APP_USER}

# Start uWSGI
CMD ["uwsgi", "--show-config"]
