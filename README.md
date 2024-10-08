# National Aquatic Barrier Inventory & Prioritization Tool

https://aquaticbarriers.org/

## Purpose

The [Southeast Aquatic Resources Partnership](https://southeastaquatics.net) has created and maintained the most complete and value-added inventory of aquatic barriers in the Southeastern U.S. This tool helps users prioritize aquatic barriers for removal and mitigation based on metrics that describe aquatic network connectivity.

Three types of barriers are considered in these analyses:

#### Waterfalls:

These natural barriers are considered "hard" barriers that break the aquatic network. These are not assessed for removal but are used to constrain the available aquatic networks used to prioritize artificial barriers.

#### Dams:

These large artificial barriers are considered "hard" barriers that break the aquatic network. Aquatic networks, already divided by waterfalls above, are further divided by these dams. The potential gain of removing a dam is determined by ranking the connectivity metrics for each dam compared to other dams. Small barriers are not included in this analysis.

#### Small barriers (road / stream crossings):

These barriers may or may not break the network, depending on site-specific factors. These include culverts or other small artificial barriers that may impede the flow of aquatic organisms. Aquatic networks, divided by waterfalls and dams above, are further subdivided to assess the network connectivity of each small barrier.

#### Outputs:

These large and small barriers are analyzed to produce two groups of outputs:

1. network metrics for dams, based on cutting the network for all dams and waterfalls
2. network metrics for small barriers, based on cutting the network for all dams, waterfalls, and small barriers

## Data processing

Data processing steps are detailed in [/analysis/README.md](analysis). Data are processed heavily before integrating into the tool.

## Architecture

The user interface tier is stored in `/ui` and consists of a GatsbyJS and React-based application.

The backend is composed of several parts:

- `/analysis`: data processing scripts
- `/api`: FastAPI for requesting subsets and downloads
- map tiles are served from `/tiles` using `mbtileserver` (tiles are not stored in the code repository)

## Development

To develop this application, you need Python 3.12+ and NodeJS 20+.

`pipenv` and `npm` are used as the package managers for those languages.

### mbtileserver

Install `mbtileserver` according to https://github.com/consbio/mbtileserver.
Then from appropriate directory (or if installed via `go get` and `~/go/bin` is on your `PATH`): `mbtilserver -p 8001 -d /<PATH TO REPO>/tiles`.

You should now be able to open `http://localhost:8001/services` to see a listing of available tile services.

### UI Initial setup:

See `ui/package.json` for NodeJS dependencies used by the UI tier.

- `cd ui`
- run `npm install` to install all dependencies.

The following environment variables must be sent in `/ui/.env.development`:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_API_HOST = <root URL of API host, likely http://localhost/:5000 for local fastapi server >
GATSBY_TILE_HOST = <root URL of tile host, likely http://localhost:8001 for local mbtileserver >
```

### API initial setup:

See `pyproject.toml` for Python dependencies. The development dependencies are required for the data processing scripts.

Python dependencies are managed using `uv`.

```bash
uv venv .venv --python=3.12
# activate for your particular shell type
source .venv/bin/activate.fish
uv pip install -e .[dev]
```

#### User interface

The user interface is built using GatsbyJS.

To start the development server (on port 8000, by default):

- `cd ui`
- `gatsby develop`

#### Run API:

Within an active Python environment (`pipenv shell`).

To start the API server (on port 5000, by default), with reloading:

```
uvicorn api.server:app --reload --reload-dir api --port 5000
```

The API loads environment variables from `.env` in the root of this project.

## Deployment

Server configuration and deployment steps are available in [deploy/README.md](deploy/README.md).

### IMPORTANT:

The `version` number and `date` needs to be set properly for each release in `ui/package.json`.
This generally should follow [semantic versioning](https://semver.org/) wherein with `X.Y.Z`:

- `X` refers to a major version, and includes major updates to the inventory data, network data, or analysis methods.
- `Y` refers to a minor version, and includes minor updates to the inventory data (e.g., downloading a new set of data with more barriers) but no substantive change to the overall approach or data used. This should be incremented on every download from the inventory that includes new data.
- `Z` refers to a bug fix version, and is used when new results are released due to bugs in the analysis code.

This version is displayed to end users as the data version.

The `date` property needs to be set to the date the data were last downloaded.

## Credits

This project was made possible in partnership with the [Southeast Aquatic Resources Partnership](https://southeastaquatics.net/) (SARP). Kat Hoenke (SARP Spatial Ecologist and Data Manager) provided all data from SARP used in this project.

It was supported in part by grants from the [U.S. Fish and Wildlife Service Fish Passage Program](https://www.fws.gov/fisheries/fish-passage.html), [Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative](https://gcpolcc.org/), and [Florida State Wildlife Grants Program](https://myfwc.com/conservation/special-initiatives/fwli/grant/).

This project was originally created by [Brendan C. Ward](https://github.com/brendan-ward) at the [Conservation Biology Institute](https://consbio.org/). Brendan, now with [Astute Spruce, LLC](https://astutespruce.com/), has continued to enhance this project in partnership with SARP.
