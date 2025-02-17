# Server setup

## Server

- Create an EC2 T4g.medium server based on Ubuntu 24.04 LTS (Arm64)
- Set root volume to have 30 GB (GP3) of space
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
sudo mkdir -p /downloads/custom
sudo mkdir -p /downloads/national
sudo chown -R app:app /downloads
sudo chmod -R 774 /downloads
```

## Clone the repository and setup environment files

```bash
sudo su app
cd ~
git clone https://github.com/astutespruce/sarp-connectivity.git
cd sarp-connectivity
mkdir -p data/api
```

Edit `~/.bashrc` to always login to `/home/app/sarp-connectivity` folder by adding
this line toward the top:

```
cd ~/sarp-connectivity
```

Create a `.env` in the root of the repository with the following:

```
SENTRY_DSN=<sentry DSN>
ALLOWED_ORIGINS=<domain of tool>
API_ROOT_PATH=/api/v1
CUSTOM_DOWNLOAD_DIR=/downloads/custom
```

Create a `ui/.env.production` file with the following:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_SENTRY_DSN = <dsn>
GATSBY_GOOGLE_ANALYTICS_ID = <ga id>
GATSBY_API_HOST = <root URL of API host>
GATSBY_TILE_HOST = <root URL of tile host>
GATSBY_MAILCHIMP_URL=https://mc.us19.list-manage.com/subscribe/landing-page
GATSBY_MAILCHIMP_USER_ID=<user id>
GATSBY_MAILCHIMP_FORM_ID=<form id>
GATSBY_MAILCHIMP_FORM_ID2=<form id2>
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
cd ~/sarp-connectivity/ui
nvm install
npm install -g npm@latest
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
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv --python 3.12
uv sync --frozen
```

## Install mbtileserver

- as `ubuntu` user, in `/tmp` directory
- install `unzip`: `sudo apt-get update && sudo apt-get install -y unzip`
- Find the latest release on https://github.com/consbio/mbtileserver/releases and download the zip file for the correct architecture (`curl -L -o /tmp/mbtileserver_v0.11.0_linux_arm64.zip https://github.com/consbio/mbtileserver/releases/download/v0.11.0/mbtileserver_v0.11.0_linux_arm64.zip`).

```bash
unzip mbtileserver_v0.11.0_linux_arm64.zip
sudo chmod 777 mbtileserver_v0.11.0_linux_arm64
sudo mv mbtileserver_v0.11.0_linux_arm64 /usr/bin/mbtileserver
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
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Note: this automatically enables the caddy service

Add caddy to `app` and `www-data` groups:

```bash
sudo usermod -aG app caddy
sudo usermod -aG www-data caddy
```

Note: this is necessary for serving files from /downloads/custom/\*_/_.zip because
temporary directories are created by the background task worker for `app` user
and `www-data` group.

```bash
sudo cp /home/app/sarp-connectivity/deploy/<environment>/Caddyfile /etc/caddy/Caddyfile
sudo service caddy restart
```

Note: this will only work properly if the instance is being routed to for the domain
name specified in the Caddyfile.

If the domain was previously used on a different server, you can transfer the
TLS certificates from that server to avoid re-fetching those from LetsEncrypt
(not a problem unless it hits a rate limit).

These assets are stored in `/var/lib/caddy/.local/share/caddy`.

Package them on the previous server:

```bash
sudo su root
mkdir /tmp/caddy
sudo cp -aR /var/lib/caddy/.local/share/caddy/* /tmp/caddy
exit
sudo chown -R ubuntu:ubuntu /tmp/caddy
```

Then transfer that to the new server.

Verify that it loaded as a service correctly:

```bash
sudo service caddy status
```

## Install Redis

As `ubuntu` user:

follow instructions for Ubuntu [here](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/):

```bash
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install -y redis
```

This should enable the Redis server to be running automatically. Confirm that it
started correctly:

```bash
sudo service redis-server status
```

## Copy data and tiles to server

Upload data according to the [data release workflow](./DataRelease.md).

## Bring up API

Verify that API starts correctly. As `app` user from within `~/sarp-connectivity`:

```bash
/home/app/sarp-connectivity/.venv/bin/uvicorn api.server:app --port 5000
```

`CTRL-C` to exit

Verify that API starts correctly with gunicorn:

```bash
/home/app/sarp-connectivity/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker --name uvicorn --workers 2 -b ":5000" api.server:app
```

`CTRL-C` to exit

Verify the background task worker starts correctly:

```bash
/home/app/sarp-connectivity/.venv/bin/arq api.worker.WorkerSettings
```

`CTRL-C` to exit

Enable API and background task (arq) services:

As `ubuntu` user:

```bash
sudo cp /home/app/sarp-connectivity/deploy/<environment>/service/api.service /etc/systemd/system/
sudo systemctl enable api
sudo service api start

sudo cp /home/app/sarp-connectivity/deploy/<environment>/service/arq.service /etc/systemd/system/
sudo systemctl enable arq
sudo service arq start
```

Verify the services started correctly:

```bash
sudo service api status
sudo service arq status
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

## Data updates

See [Data Release steps](./DataRelease.md).
