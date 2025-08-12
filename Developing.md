# National Aquatic Barrier Inventory & Prioritization Tool Development Environment

To develop this application, you need:

- Python 3.12+: required for `analysis` and `api` components
- NodeJS 20+: required for user interface component in `ui`
- mbtileserver: required for interactive maps in the user interface component
- redis: required for background task worker used by `api` component

`uv` and `npm` are used as the package managers for those languages.

## Python environment setup

Python is required for the `analysis` and `api` components of this tool.

See `pyproject.toml` for Python dependencies. The development dependencies are required for the data processing scripts in `analysis`.

Python dependencies are managed using [uv](https://github.com/astral-sh/uv).

```bash
uv venv .venv --python=3.12
# activate for your particular shell type
source .venv/bin/activate.fish
uv pip install -e .[dev]
```

Note: for local development, you will need the development dependencies (`dev`) in addition to the core dependencies used on the server.

### Python environment variables

Create `.env` in the root of this repository with the following entries:

```bash
# AGOL token is obtained from https://fws.maps.arcgis.com/ after signing in with a USFWS collaborator account
# use the network panel in chrome to view requests, and select the token query parameter from one of the requests
# NOTE: this is short-lived
AGOL_TOKEN=<token>

# This token is obtained from https://sarp.maps.arcgis.com/ after signing in with a SARP-provided AGOL account
# NOTE: this is short-lived
AGOL_PRIVATE_TOKEN=<token>

# This token is obtained from a Mapbox account
# NOTE: this is only used for rendering static map images as part of publishing a data release
MAPBOX_TOKEN=<token>

# NOTE: private download endpoints must be enabled on the local development API server
# if not running behind caddy
PROVIDE_DOWNLOAD_ENDPOINTS=1
```

Note: the AGOL tokens are only required in order to pull new data from the SARP services as part of a data release process.
They are not necessary for running other parts of `analysis` or `api`.

### Run API and background task worker:

This is necessary to run the `api` tier for use by the frontend.

#### API server:

Within an active Python environment.

To start the API server (on port 5000, by default), with reloading:

```bash
uvicorn api.server:app --reload --reload-dir api --port 5000
```

#### Background task worker:

In another terminal window, within the active Python environment.

To start the background task worker used for larger downloads:

```bash
arq api.worker.WorkerSettings --watch ./api
```

This needs to be manually killed and restarted on changes to the implementation
of the background task functions.

Note: redis must be running first (see below)

### Managing Python dependency versions

```bash
# list outdated dependencies
uv lock --upgrade --dry-run

# upgrade them all
uv lock --upgrade

# or updgrade specific package(s)
uv lock --upgrade-package <package>
```

## Javascript environment setup:

Javascript is required for the `ui` component of this tool. It is not necessary for performing any of the pre-processing in
`analysis` or the API functionality in `api`.

The NodeJS version is managed
using [nvm](https://github.com/nvm-sh/nvm) and dependencies are installed using `npm`.

See `ui/package.json` for NodeJS dependencies used by the UI tier.

The user interface is contained in the `ui` folder.

```bash
cd ui

# activate NodeJS version specified in .nvmrc
nvm use
npm ci
```

Create `/ui/.env.development` with the following contents:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_API_HOST = <root URL of API host, likely http://localhost/:5000 for local fastapi server >
GATSBY_TILE_HOST = <root URL of tile host, likely http://localhost:8001 for local mbtileserver >
```

The user interface is built using GatsbyJS.

To start the development server (on port 8000, by default):

```bash
gatsby clean
gatsby develop
```

#### Managing Javascript dependencies

```bash
# list outdated dependencies
npm outdated

# install updated packages
npm install --legacy-peer-deps <package>@latest ...
```

## mbtileserver

mbtileserver is required to display interactive maps in the user interface. It is not required by `analysis` or `api`.

Install `mbtileserver` according to https://github.com/consbio/mbtileserver.
Then from appropriate directory (or if installed via `go get` and `~/go/bin` is on your `PATH`): `mbtilserver -p 8001 -d /<PATH TO REPO>/tiles`.

You should now be able to open `http://localhost:8001/services` to see a listing of available tile services.

## Redis

Redis acts as the task broker for running background tasks in the `api` tier. It is not required for data pre-processing in `analysis`.

Install Redis as required for your operating system, and then start the server process by running the following in a terminal:

```bash
redis-server
```
