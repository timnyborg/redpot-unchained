# Development principles

### 12 Factor design (https://12factor.net/)
* No credentials should be stored in the source code.  Instead, they should come from Environment Variables or secrets files.  Act like the source code is public.
* No configuration should be stored in the source code.  Hosts, ports, service urls, etc., should come from Environment Variables or secrets files.  You should be able to switch any connected resource (database, cache, file server, APIs, etc.) without editing the source code.
* All python dependencies should go in requirements.txt.  Fetching them on a new environment should be as simple as `pip install -r requirements.txt`
* All debian dependencies should go in the Dockerfile.  When deploying to a new environment, you shouldn't need to look through pip install errors to figure out what you're missing.

### Smallish apps
To separate concerns, and to keep models and views manageable, each app should be concerned with one class of object and its dependencies (e.g. Student, Module, Tutor, Programme, Invoice, Contract).  You may wind up with more imports, but it'll be easier to find what you're looking for once there's a form for every model object.

### DRY
Where you find yourself doing the same thing over and over in different apps generalize it and put it in the `main` app. (Maybe it should be called `core`?)
Including:
* Mixins for Classes, Forms, Models, etc.
* Custom-defined Views, Validators, FieldTypes, FormFields, abstract Models, 
* Templates, sub-templates, template tags, template filters
* Model Managers for common filters (e.g. queries using is_active)

### GET requests should be read-only
See https://twitter.com/rombulow/status/990684463007907840

A GET request should never change the model's state.  So our endpoints like programme/remove-module/ or module/publish/
should only respond to POSTs.  This can be done through confirmation forms (e.g. an UpdateView or DeleteView, maybe in a 
modal), javascript, or a host of other approaches.

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
scp <your_username>@deltamap:/home/www-data/django/redpot/secrets.json .
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

Get a copy of the secrets file, containing dev database login details, etc.
```bash 
scp <your_username>@deltamap:/home/www-data/django/redpot/secrets.json .
```

Build and start the container(s)
```bash
sudo docker-compose up --build -d
```

View the application in browser at `http://<your_server>:8001` or `localhost:8001`

You're now running two copies in parallel, on ports 8001 and 8002 (because why not!)