# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Boundary Data Prep

## Analysis regions and units

## Analysis regions and units source data

Unless otherwise noted, source data are saved to `data/boundaries/source`.

Watershed boundaries were extracted from the NHD WBD national dataset downloaded
on 9/24/2026 from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/National/GDB/ and saved to `data/nhd/wbd/WBD_National_GDB_2026.gdb`.
(data version 9/2/2026)

2025 versions of the states, counties and equivalents, and Congressional districts (119th congress) were downloaded on 9/24/2026 from CENSUS Tiger website. Congressional districts were downloaded using `analysis/prep/boundaries/download_congressional_districts.py` because they have to be downloaded individually.

Fish Habitat Partnership data were provided by Kat Hoenke via email on 8/26/2026
(downloaded using ArcGIS from https://psmfc.maps.arcgis.com/home/item.html?id=55a44f6b38c049618820a7f55c9a1b5b).

Water resource inventory areas for Washington State were downloaded from https://geo.wa.gov/datasets/waecy::water-resource-inventory-areas-wria/about
on 7/21/2025. These are intended to be combined with other state-level water resource areas once identified.

### Prepare analysis region and analyis unit boundaries

The analysis region is all states/territories except American Samoa, Guam, and
the Commonwealth of the Northern Mariana Islands (see `analysis/constants.py::STATES`).

Analysis units are boundaries used for selecting areas of interest and summarizing
results in the tool. Additional datasets used to provide landscape context are
processed in a separate step below.

The analysis regions and units are created using `analysis/prep/prep_analysis_boundaries.py`,
which produces the following files in `data/boundaries`:

- `states.feather`: state boundaries for all states within analysis region
- `region_boundary.feather`: total analysis region and boundary for each region within it
- `huc2.feather`: HUC2 boundaries within analysis region
- `huc4.feather`: HUC4 boundaries within the HUC2s above (excluding those exclusively in Mexico where data are unavailable)
- `huc6.feather`: HUC6 boundaries within HUC4s above
- `huc8.feather`: HUC8 boundaries within HUC4s above
- `huc10.feather`: HUC10 boundaries within HUC4s above
- `huc12.feather`: HUC12 boundaries within HUC4s above
- `counties.feather`: counties for the states above
- `congressional_districts.feather`: congressional districts for the states above
- `fhp_boundary.feather`: Fish Habitat Partnership boundaries
- `state_water_resource_areas`: state water resource areas
- `map_units.feather`: compiled map units used for search index by API

## Ancillary / contextual boundaries

### Source data

#### Protected areas / land ownership

PAD-US v4.1 GDB version downloaded 8/19/2025 from: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

The original PAD-US v4.1 data contains invalid records. In order to get around
this, first create a new geopackage and then create index on state name to make
query faster:

```bash
ogr2ogr source_data/protected_areas/pad_us4.1.gpkg source_data/protected_areas/PADUS4_1.gdb PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures -nlt CONVERT_TO_LINEAR
```

Additional areas for Hawaii were downloaded from: https://prod-histategis.opendata.arcgis.com/datasets/HiStateGIS::reserves/about
on 9/4/2024.

##### USFS ownership and administrative boundaries

USFS-specific surface ownership parcels were downloaded from https://data-usfs.hub.arcgis.com/datasets/24db18ef747945c49b02252ae39ec4aa_0/explore
on 4/10/2024.

USFS-specific administrative boundaries were downloaded from https://data-usfs.hub.arcgis.com/datasets/09e4c1162a4d4af3a84163cbc76108c4_1/explore
on 2/14/2025.

NOTE: all USFS lands were excluded from PAD-US and superseded with the USFS specific ones above.

##### Combined protected areas

Protected areas were processed into dissolved polygons by ownership category.
These may include overlapping ownership categories. These are sorted in the
following precedence order: USFS ownership, USFS administrative boundary,
remaining ownership categories.

Wilderness areas are extracted separately for filtering.

#### Native territories

Native Territories were downloaded 4/10/2024 from https://native-land.ca/

#### Wild & Scenic rivers

Designated wild & scenic corridors were extracted from PAD-US above.

Wild & scenic rivers lines were provided by Kat Hoenke via email from USFS on 9/12/2024.
These are buffered by 250 meters (arbitrary) and used outside of the designated
corridors.

Eligible and suitable wild & scenic river lines were downloaded from
https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_WildScenicRiverEligibleSuitable_01/MapServer/1
on 2/15/2025 using `analysis/prep/boundaries/download_wsr_eligible_suitable.py`.

This download step was necessary in order to extract data from the FeatureLayer
in the above map service, because no downloadable data could be found.

These are buffered by 250 meters and used outside of the corridors and buffers
above.

#### Priority areas

These include:

- SARP Conservation Opportunity Areas at HUC8 level (provided by SARP).
- Hawaii FHP geographic focus areas (provided by Kat via email on 9/3/2024).

Priority areas are only used for overlay in the maps, not filtering.

#### Environmental Justice Disadvantaged Communities

Environmental justice disadvantaged communities evaluated at the Census tract level
were downloaded 2/8/2023 from: https://screeningtool.geoplatform.gov/en/downloads
(no longer)

Following the same methods as described in the tool above, American Indian Area Geographies (2022 version)
were downloaded from the Census TIGER website.

#### Native territories

Native territories were downloaded from Native Land Digital (https://native-land.ca/)
on 4/10/2024.

#### Trout Unlimited Brook Trout Conservation Portfolio

The most recent Trout Unlimited Brook Trout Conservation Portfolio data were provided by Matthew Mayfield at Trout Unlimited on 7/23/2025 via email.

These are current as of 7/4/2022.

More information available at: https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/

### Prepare contextual areas

Run `analysis/prep/boundaries/prep_contextual_boundaries.py`.

## Create boundary vector tiles

Vector tiles are are created for each of the boundary layers using `analysis/prep/boundaries/create_map_unit_tiles.py`.

Vector tiles of priority areas are created using `analysis/prep/boundaries/create_priority_area_tiles.py`.
