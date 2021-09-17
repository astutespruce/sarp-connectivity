# Server setup

## Server

- Create an EC2 micro server based on Ubuntu 20.04 LTS
- Set root volume to have 12 GB of space
- Create a second volume with 20 GB of space
- Create an elastic IP and assign to that instance
- Create a 4 GB swap file according to instructions here: https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-16-04
  - `sudo fallocate -l 4G /swapfile`
  - `sudo chmod 600 /swapfile`
  - `sudo mkswap /swapfile`
  - `sudo swapon /swapfile`
  - add this to `/etc/fstab`: `/swapfile none swap sw 0 0`

* Format and mount 20 GB secondary volume
  - use `lsblk` to list volumes; it should be listed as `xvdb`
  - `sudo mkfs -t ext4 /dev/xvdb`
  - `sudo mkdir /tiles`
  - `sudo mount /dev/xvdb /tiles/`
  - add this to `/etc/fstab`: `/dev/xvdb /tiles ext4 defaults,nofail`

## Setup accounts and directories

The application is managed by the `app` user account.

- `sudo useradd --create-home app`
- `sudo usermod -a -G app ubuntu`
- `sudo chsh -s /bin/bash app`
- `sudo mkdir /var/www`
- `sudo chown app:app /var/www`
- `sudo chown app:app /tiles`

## Clone the repository

- `sudo su app`
- `cd ~`
- `git clone https://github.com/astutespruce/sarp-connectivity.git`
- `cd sarp-connectivity`
- `mkdir data`
- `mkdir data/api`

## Copy tiles up

- on local (dev) machine, copy contents of `tiles` directory to server: `rsync -azvhP --append *.mbtiles sarp:/tmp`
- move to `/tiles` and change ownership to `app`

## Copy data up

- on local (dev) machine copy `feather` files in `sarp/data/api/` to server: `rsync -azvhP --append *.feather sarp:/tmp`
- on remote: `sudo mv /tmp/*.feather /home/app/sarp-connectivity/data/api`

## Install and build mbtileserver

- Find the latest release on https://github.com/consbio/mbtileserver/releases and download the zip file for the correct architecture (`wget https://github.com/consbio/mbtileserver/releases/download/v0.7.0/mbtileserver_v0.7.0_linux_amd64.zip`).
- unzip, rename to `mbtileserver`, and make executable (`chmod 777 mbtileserver`)
- `sudo su app`
- `mkdir /home/app/go`
- `mkdir /home/app/go/bin`
- `mv /tmp/mbtileserver /home/app/go/bin

Enable service

- as `ubuntu` user
- copy `deploy/production/service/mbtileserver.service` to `/etc/systemd/system/`
- `sudo systemctl enable mbtileserver`

## Install `nodejs` 16:

- as `ubuntu` user
- `curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -`
- `sudo apt-get update && sudo apt-get install -y nodejs`

## Install Caddy

- as `ubuntu` user
- follow instructions [here](https://caddyserver.com/docs/download) to install on Ubuntu
- the service file is installed to `/lib/systemd/system/caddy.service`
- copy `deploy/production/Caddyfile` from this directory in the repo to `/etc/caddy/Caddyfile`
- edit the caddyfile if necessary for the environment (e.g., staging)

## Install pip and pipenv

- as `ubuntu` user
- `sudo apt-get install -y python3-pip`
- `sudo pip3 install pipenv`

## Install node dependencies

- `cd ui`

Create a `.env.production` file with the following:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_SENTRY_DSN = <dsn>
GATSBY_GOOGLE_ANALYTICS_ID = <ga id>
GATSBY_API_HOST = <root URL of API host>
GATSBY_TILE_HOST = <root URL of tile host>
GATSBY_MAILCHIMP_URL=<url>
GATSBY_MAILCHIMP_USER_ID=<user id>
GATSBY_MAILCHIMP_FORM_ID=<form id>
```

- `npm ci`
- `npm run deploy`

## Install Python dependencies

- as `ubuntu` user
- `cd `~/sarp-connectivity`
- `pipenv install --skip-lock`
- `pip install -e .`

Verify that API starts correctly:

- `uvicorn api.server:app --reload --port 5000`
- `CTRL-C` to exit

Verify that API starts correctly with gunicorn:

- `/usr/local/bin/pipenv run gunicorn -k uvicorn.workers.UvicornWorker --name uvicorn --workers 2 -b ":5000" api.server:app`
- `CTRL-C` to exit

Enable service:

- as `ubuntu` user
- copy `services/api.service` to `/etc/systemd/system/`
- `sudo systemctl enable api`

## Verify services

Verify that each service runs properly. For `caddy`, `mbtileserver`, `api` services:

- As `ubuntu` user
- `sudo service <service_name> start`
- `sudo service <service_name> status` (look for errors or success)
- `sudo service <service_name> stop`

After that, test the first few steps of the prioritization workflow here: https://connectivity.sarpdata.com/priority

1. Select state as unit
2. Select a state
3. If it shows the filters, everything is working as expected. Otherwise, if it is not showing state boundaries for selection, there is a problem with `mbtileserver`. If it is not showing filters, there is a problem with `api` service. If you can't even boot the application, it is a problem with the `caddy` service or the underlying built JS.
