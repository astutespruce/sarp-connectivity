# Southeast Aquatic Barriers Inventory Visualization & Prioritization Tool

## Purpose

The [Southeast Aquatic Resources Partnership](https://southeastaquatics.net) has created and maintained the most complete and value-added inventory of aquatic barriers in the Southeastern U.S. This tool helps users prioritize aquatic barriers for removal and mitigation based on metrics that describe aquatic network connectivity.

Three types of barriers are considered in these analyses:

#### Waterfalls:

These natural barriers are considered "hard" barriers that break the aquatic network. These are not assessed for removal, but are used to constrain the available aquatic networks used to prioritize artificial barriers.

#### Dams:

These large artificial barriers are considered "hard" barriers that break the aquatic network. Aquatic networks, already divided by waterfalls above, are further divided by these dams. The potential gain of removing a dam is determined by ranking the connectivity metrics each dam compared to other dams. Small barriers are not included in this analysis.

#### Small barriers (road / stream crossings):

These barriers may or may not break the network, depending on site specific factors. They may be culverts or other small artificial barriers that may impede the flow of aquatic organisms. Aquatic networks, divided by waterfalls and dams above, are further subdivided in order to assess the network connectivity of each small barrier.

#### Outputs:

These large and small barriers are analyzed to produce 2 groups of outputs:

1. network metrics for dams, based on cutting the network for all dams and waterfalls
2. network metrics for small barriers, based on cutting the network for all dams, waterfalls, and small barriers

## Data processing

Data processing steps are detailed in [/analysis/README.md](analysis).

## Architecture

The user interface tier is stored in `/ui` and consists of a React-based application.

The backend is composed of several parts:

-   `/data/*.py`: data processing scripts
-   `/api`: flask API for requesting subsets and downloads
-   map tiles are served from `/tiles` using `mbtileserver`

## Development

To develop this application, you need Python 3.6+ and NodeJS 8.9+

`pipenv` and `npm` are used as the package managers for those languages.

### mbtileserver

Install `mbtileserver` according to https://github.com/consbio/mbtileserver
Then from appropriate directory (or if installed via `go get` and `~/go/bin` is on your `PATH`): `mbtilserver -d /<PATH TO REPO>/tiles`.

You should now be able to open `http://localhost:8000/services` to see a listing of available tile services.

### UI Initial setup:

-   `cd ui`
-   run `npm install` to install all dependencies.

The following environment variables must be sent in `/ui/.env.development`:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_API_HOST = <root URL of API host, likely http://localhost/:5000 for local flask server >
GATSBY_TILE_HOST = <root URL of tile host, likely http://localhost:8001 for local mbtileserver >
```

### Flask API initial setup:

-   `cd api`
-   run `pipenv install` to setup a Python virtual environment and install all dependencies.

Running the above is also required as Python or NodeJS dependencies change.

### Development environment

#### User interface

The user interface is built using GatsbyJS.

To start the development server (on port 8000, by default):

-   `cd ui`
-   `gatsby develop`

To start the frontend application (on port 3000, by default:
`cd ui && yarn start`
Then open `http://localhost:3000` in your browser.

#### Flask API:

To start the report server (on port 5000, by default):

```
export FLASK_APP=api.server
export FLASK_ENV=development
pipenv run flask run
```

Alternatively, you can run flask from within your virtual environment:

```
pipenv shell
flask run
```

## Deployment

Server configuration and deployment steps are available in the [wiki](https://github.com/astutespruce/sarp-connectivity/wiki/AWS-Server-Setup).

The following environment variables must be set in `/ui/.env.production` or otherwise passed to Gatsby during the build process:

```
GATSBY_MAPBOX_API_TOKEN = <token>
GATSBY_SENTRY_DSN = <dsn>
GATSBY_GOOGLE_ANALYTICS_ID = <ga id>
GATSBY_API_HOST = <root URL of API host>
GATSBY_TILE_HOST = <root URL of tile host>
GATSBY_MAILCHIMP_URL = <POST URL of mailchimp subscription form>
GATSBY_MAILCHIMP_USER_ID = <mailchimp user ID>
GATSBY_MAILCHIMP_FORM_ID = <mailchimp audience ID for subscription form>
```

The `MAILCHIMP_*` variables are used to capture user information for data download, and submit those to a signup form in Mailchimp.

### IMPORTANT:

The `version` number and `date` needs to be set properly for each release in `ui/package.json`.
This generally should follow [semantic versioning](https://semver.org/) wherein with `X.Y.Z`:

-   `X` refers to a major version, and includes major updates to the inventory data, network data, or analysis methods.
-   `Y` refers to a minor version, and includes minor updates to the inventory data (e.g., downloading a new set of data with more barriers) but no substantive change to the overall approach or data used. This should be incremented on every download from the inventory that includes new data.
-   `Z` refers to a bug fix version, and is used when new results are released due to bugs in the analysis code.

This version is displayed to end users as the data version.

The `date` property needs to be set to the date the data were last downloaded.

## Credits

This project was made possible in partnership with the [Southeast Aquatic Resources Partnership](https://southeastaquatics.net/) (SARP).

It was supported in part by grants from the [U.S. Fish and Wildlife Service Fish Passage Program](https://www.fws.gov/fisheries/fish-passage.html), [Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative](https://gcpolcc.org/), and [Florida State Wildlife Grants Program](https://myfwc.com/conservation/special-initiatives/fwli/grant/).

This project was originally created by [Brendan C. Ward](https://github.com/brendan-ward) at the [Conservation Biology Institute](https://consbio.org/). Brendan, now with [Astute Spruce, LLC](https://astutespruce.com/), has continued to enhance this project in partnership with SARP.
