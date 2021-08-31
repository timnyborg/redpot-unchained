# Installation (virtual machine)

Make sure you have venv on your machine for creating virtual environments
```bash
sudo apt-get install python3-venv
```

Navigate to the folder where you want to hold application (example, ~/django)
```bash
mkdir ~/django && cd ~/django
```

Download the repository, create a virtual environment, install pre-reqs
```bash
git clone git@gitlab.conted.ox.ac.uk:django/redpot-unchained.git
cd redpot-unchained
sudo apt install $(cat ./dependencies.txt)
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Get a copy of the secrets file, containing dev database login details, etc.
```bash
scp <your_username>@deltamap:/home/www-data/django/redpot/secrets.env .
```

Start up the server
```bash
python3 manage.py runserver 0.0.0.0:8080
```

View the application in browser at `http://<your_server>:8080` or `localhost:8080`

# Installation (docker)

First, install docker and docker-compose
* https://docs.docker.com/get-docker/
* https://docs.docker.com/compose/install/

Navigate to the folder where you want to hold application (example, ~/docker)
```bash
mkdir ~/docker && cd ~/docker
```

Download the repository
```bash
git clone git@gitlab.conted.ox.ac.uk:django/redpot-unchained.git
cd redpot-unchained
```

### Option 1: connecting to existing services (database, redis, etc.)
Get a copy of the secrets file, containing dev database login details, etc.
```bash
scp <your_username>@deltamap:/home/www-data/django/redpot/secrets.env .
```

Build and start the container
```bash
sudo docker-compose up --build -d django
```

### Option 2: a standalone dev stack (running mssql, redis, etc. as containers)
Build and start the containers
```bash
sudo docker-compose up --build -d
```

Create the empty database
```bash
sudo docker compose exec mssql /opt/mssql-tools/bin/sqlcmd -U sa -P Test@only -Q "CREATE DATABASE redpot;"
```

Create the database structure
```bash
sudo docker compose exec django python manage.py migrate
```

Create a superuser
```bash
sudo docker compose exec django python manage.py createsuperuser
```
Choose username, email, and password when prompted.  Now you can login!

### Installation complete
View the application in browser at `http://<your_server>:8000` or `localhost:8000`

You're now running redpot!
