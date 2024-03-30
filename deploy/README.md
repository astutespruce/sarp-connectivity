# Server setup

## Server

- Create an EC2 T4g.small server based on Ubuntu 22.04 LTS (Arm64)
- Set root volume to have 24 GB (GP3) of space
- Add a second volume with 50 GB (GP3) of space for tiles
- Create an elastic IP and assign to that instance

NOTE: the same configuration is used for staging as for production, because the
staging server is typically promoted to the staging server when ready.

### Create a 4 GB swap file

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Add this to `/etc/fstab`: `/swapfile none swap sw 0 0`

### Format and mount 50 GB secondary volume, used for tiles

se `lsblk` to list volumes; it may be listed as `nvme1n1`

```bash
sudo mkfs -t ext4 /dev/nvme1n1
sudo mkdir /tiles
sudo mount /dev/nvme1n1 /tiles/
```

Add this to `/etc/fstab`: `/dev/nvme1n1 /tiles ext4 defaults,nofail`

## Setup accounts and directories

The application is managed by the `app` user account.

```bash
sudo useradd --create-home app
sudo usermod -a -G app ubuntu
sudo chsh -s /bin/bash app
sudo mkdir /var/www
sudo chown app:app /var/www
sudo chown app:ubuntu /tiles
sudo chmod 774 /tiles
```

## Clone the repository and setup environment files

```bash
sudo su app
cd ~
git clone https://github.com/astutespruce/sarp-connectivity.git
cd sarp-connectivity
mkdir -p data/api
```

Create a `.env` in the root of the repository with the following:

```
SENTRY_DSN=<sentry DSN>
ALLOWED_ORIGINS=<domain of tool>
API_ROOT_PATH=/api/v1
```

Create a `ui/.env.production` file with the following:

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

## Grant ubuntu user write permissions to the root folder

As `ubuntu` user:

```bash
sudo chown -R app:ubuntu /home/app/sarp-connectivity
```

## Install NodeJS and UI dependencies:

Check `.nvmrc` and use the same major version of NodeJS.

As `ubuntu` user:

```bash
sudo apt-get update && sudo apt-get install -y make g++
```

(needed to build @parcel/watch dependency)

As `app` user:

```bash
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
```

Exit and log back in as app user.

```bash
nvm install
npm install -g npm@latest
cd ~/sarp-connectivity/ui
npm run install-deps
```

NOTE: the gatsby-cli version may need to be updated to match version of Gatsby in `package.json`

Build it:

```bash
npm run deploy
```

## Install Python dependencies

As `ubuntu` user:

```bash
sudo apt-get install -y python3-pip
```

As `app` user:

```bash
cd ~/sarp-connectivity
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="/home/app/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
poetry install --only main --extras deploy
```

To activate the shell, use `poetry shell`.

## Install mbtileserver

- as `ubuntu` user, in `/tmp` directory
- install `unzip`: `sudo apt-get update && sudo apt-get install -y unzip`
- Find the latest release on https://github.com/consbio/mbtileserver/releases and download the zip file for the correct architecture (`wget https://github.com/consbio/mbtileserver/releases/download/v0.9.0/mbtileserver_v0.9.0_linux_arm64.zip`).

```bash
unzip <filename>
mv <filename> mbtileserver
sudo chmod 777 mbtileserver
sudo mv mbtileserver /usr/bin
```

Verify it starts up properly (error about no tiles is OK):

```bash
mbtileserver -d /tiles -p 8001
```

Setup and enable service (will be restarted after uploading tiles):

```bash
sudo cp /home/app/sarp-connectivity/deploy/<environment>/service/mbtileserver.service /etc/systemd/system
sudo systemctl enable mbtileserver
```

(where environment is staging or production)

Verify that it loaded as a service correctly:

```bash
sudo service mbtileserver status
```

## Install Caddy

As `ubuntu` user:

follow instructions [here](https://caddyserver.com/docs/install#debian-ubuntu-raspbian) to install on Linux/Arm64:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

Note: this automatically enables the caddy service

```bash
sudo cp /home/app/sarp-connectivity/deploy/<environment>/Caddyfile /etc/caddy/Caddyfile
sudo service caddy restart
```

Verify that it loaded as a service correctly:

```bash
sudo service caddy status
```

## Copy data and tiles to server

- on local (dev) machine, copy contents of `tiles` directory to server:

```bash
rsync -azvhpP --partial --inplace *.mbtiles sarp:/tiles
```

(or appropriate extra volume online just for copying data up)

Restart mbtileserver: `sudo service mbtileserver restart`

On local (dev) machine copy `feather` files in `sarp/data/api/` to server:

```bash
rsync -azvhP --append *.feather sarp:/tmp
```

On remote:

```bash
sudo chown app:app /tmp/*.feather
sudo mv /tmp/*.feather /home/app/sarp-connectivity/data/api
```

## Bring up API

Verify that API starts correctly. As `app` user from within `~/sarp-connectivity`:

```bash
/home/app/.local/bin/poetry run uvicorn api.server:app --port 5000
```

`CTRL-C` to exit

Verify that API starts correctly with gunicorn:

```bash
/home/app/.local/bin/poetry run gunicorn -k uvicorn.workers.UvicornWorker --name uvicorn --workers 2 -b ":5000" api.server:app
```

`CTRL-C` to exit

Enable service:

As `ubuntu` user:

```bash
sudo cp /home/app/sarp-connectivity/deploy/<environment>/service/api.service /etc/systemd/system/
sudo systemctl enable api
sudo service api start
```

Verify the service started correctly:

```bash
sudo service api status
```

For more log messages:

```bash
journalctl -u api
```

Verify that the API returns valid data:

Open `https://<host>/api/v1/public/dams/metadata` in a browser; it should return
valid JSON.

## Verify services

Verify that each service runs properly. For `caddy`, `mbtileserver`, `api` services:

As `ubuntu` user:

Bring any services not already running up

```bash
sudo service caddy start
```

```bash
sudo service <service_name> status
```

This should not show any errors

After that, test the first few steps of the prioritization workflow here: https://<host>/priority

1. Select state as unit
2. Select a state
3. If it shows the filters, everything is working as expected. Otherwise, if it is not showing state boundaries for selection, there is a problem with `mbtileserver`. If it is not showing filters, there is a problem with `api` service. If you can't even boot the application, it is a problem with the `caddy` service or the underlying built JS.

## On update of data

1. pull latest from git repository
2. upload tiles
3. upload feather files
4. `npm run deploy`
5. `sudo service mbtileserver restart`
6. `sudo service api restart`
