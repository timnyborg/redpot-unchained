# Installation

Navigate to the folder where you want to hold application (example, ~/django)
```bash 
mkdir ~\django && cd ~\django`
```

Download the repository, install pre-reqs (not using a venv yet)
```bash 
git clone git@gitlab.conted.ox.ac.uk:django/redpot-unchained.git
cd redpot-unchained
pip3 install -r requirements.txt
```

Get a copy of the secrets file, containing dev database login details, etc.
```bash 
scp <your_username>@deltamap:/home/www-data/django/redpot/secrets.json .
```

Start up the server
```bash
python3 manage.py runserver 0.0.0.0:8080
```

View the application in browser at `http://<your_server>:8080`