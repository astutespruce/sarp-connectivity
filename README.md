# National Aquatic Barrier Inventory & Prioritization Tool

https://aquaticbarriers.org/

## About

The [Southeast Aquatic Resources Partnership](https://southeastaquatics.net)(SARP) has created and maintained the most complete and value-added inventory of aquatic barriers in the U.S. This tool helps users prioritize aquatic barriers for removal and mitigation based on metrics that describe aquatic network connectivity.

Four types of barriers are considered in these analyses:

- waterfalls: these natural barriers break the aquatic network and thus constrain the networks that could be reconnected by removing artificial barriers.
- dams: large artificial barriers that break the aquatic network and may be evaluated for network connectivity.
- surveyed road-related barriers: road / stream crossings that have been evaluated for impact to aquatic organisms and may be evaluated for network connectivity.
- unsurveyed modeled road / stream crossings: intersections between stream and road datasets that may indicate potential road-related barriers. These are not evaluated for network connectivity because they have not yet been surveyed to determine impact to aquatic organisms.

These barriers are compiled by SARP from multiple data sources at the national, state, and local levels, and are supplemented with additional information from field reconnaissance where available. Based on their degree of impact to aquatic organisms, these barriers may be used in different aquatic connectivity analyses. The tool currently includes the following aquatic connectivity analyses that are used to help prioritize these barriers for removal or mitigation:

- dams: aquatic networks are cut by waterfalls and dams in order to prioritize dams for removal or mitigation.
- road-related barriers: aquatic networks are cut by waterfalls, dams, and surveyed road-related barriers with at least moderate barrier severity in order to prioritize road-related barriers for removal or mitigation.
- dam & road-related barriers: aquatic networks are cut by waterfalls, dams, and surveyed road-related barriers with at least moderate barrier severity in order to prioritize dams and road-related barriers for removal or mitigation.
- large-bodied fish barriers: aquatic networks are cut by waterfalls and dams that do not have partial or seasonal passibility for salmonids and non-salmonids, and surveyed road-related barriers with severe or significant barrier severity in order to prioritize dams and road-related barriers for removal or mitigation.
- small-bodied fish barriers: aquatic networks are cut by waterfalls, dams, and surveyed road-related barriers with at least minor severity in order to prioritize dams and road-related barriers for removal or mitigation.

## Architecture

There are 3 main parts to this tool, located in separate folders:

- `analysis`: data processing pipeline, which is run in advance of publishing results via the tool
- `api`: backend API, which serves data to the frontend and provides things like data downloads
- `ui`: frontend user interface

The user interface tier is stored in `/ui` and consists of a GatsbyJS and React (Javascript) application.
The user interface is "built" in advance to create static web assets (HTML, Javascript, CSS, etc).
These files are served via a development server locally or via a reverse proxy on the server.

The backend is composed of several parts:

- `/api`: FastAPI (Python) for requesting subsets and downloads
- map tiles are served from `/tiles` using `mbtileserver` (tiles are not stored in the code repository)
- reverse proxy: `caddy` is used to route to backend services and serve static assets of the user interface

## Data processing

Data processing steps are detailed in [/analysis/README.md](analysis). Data are processed heavily before integrating into the tool.

## Development

Local development environment setup is described in [Developing.md](./Developing.md).

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

It was supported in part by grants from the [U.S. Fish and Wildlife Service Fish Passage Program](https://www.fws.gov/fisheries/fish-passage.html), [Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative](https://gcpolcc.org/), and [Florida State Wildlife Grants Program](https://myfwc.com/conservation/special-initiatives/swap/grant/).

This project was created by [Brendan C. Ward](https://github.com/brendan-ward) in partnership with SARP.
