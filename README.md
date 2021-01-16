# Installation

Make sure you have venv on your machine for creating virtual environments
```bash
sudo apt-get install python3-venv
```

Navigate to the folder where you want to hold application (example, ~/django)
```bash 
mkdir ~\django && cd ~\django`
```

Download the repository, create a virtual environment, install pre-reqs
```bash 
git clone git@gitlab.conted.ox.ac.uk:django/redpot-unchained.git
cd redpot-unchained
python3 -m venv .venv
source .venv/bin/activate
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
