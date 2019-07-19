# Southeast Aquatic Barriers Inventory Visualization & Prioritization Tool

## Data processing

Data processing steps are detailed in `/data/README.md`.

## Architecture

The user interface tier is stored in `/ui` and consists of a React-based application.

The backend is composed of several parts:

-   `/data/*.py`: data processing scripts
-   `/api`: flask API for requesting subsets and downloads
-   map tiles are served from `/tiles` using `mbtileserver`

## Development

To develop this application, you need Python 3.6+ and NodeJS 8.9+

`pipenv` and `yarn` are used as the package managers for those languages.

### mbtileserver

Install `mbtilserver` according to https://github.com/consbio/mbtileserver
Then from appropriate directory (or if installed via `go get` and `~/go/bin` is on your `PATH`): `mbtilserver -d /<PATH TO REPO>/tiles`.

You should now be able to open `http://localhost:8000/services` to see a listing of available tile services.

### UI Initial setup:

-   `cd ui`
-   run `yarn install` to install all depedencies.

### Flask API initial setup:

-   `cd api`
-   run `pipenv install` to setup a Python virtual environment and install all dependencies.

Running the above is also required as Python or NodeJS dependencies change.

### Development servers

#### User interface (Webpack development server)

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

Server configuration and deployment steps are available in the [wiki](https://github.com/consbio/sarp/wiki).

## Credits

This project was made possible in partnership with the [Southeast Aquatic Resources Partnership](https://southeastaquatics.net/) (SARP).

It was supported in part by grants from the [U.S. Fish and Wildlife Service Fish Passage Program](https://www.fws.gov/fisheries/fish-passage.html), [Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative](https://gcpolcc.org/), and [Florida State Wildlife Grants Program](https://myfwc.com/conservation/special-initiatives/fwli/grant/).

This project was originally created by [Brendan C. Ward](https://github.com/brendan-ward) at the [Conservation Biology Institute](https://consbio.org/). Brendan, now with [Astute Spruce, LLC](https://astutespruce.com/), has continued to enhance this project in partnership with SARP.
