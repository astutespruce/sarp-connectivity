# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Boundary Data Prep

## Overall workflow

1. define analysis regions
2. prepare hydrologic unit boundaries
3. prepare administrative and ecological boundaries
4. create boundary vector tiles

## 1. Define analysis regions

The analysis region is based on 2 parts

- states in the region
- NHD HUC4s that intersect the state boundaries

The analysis boundary is based on the outer edge of all HUC4s that intersect
the states within the region (with exceptions). However, local barrier inventory
data are only available for states within the region, and national-level
barrier inventory data are used for the areas within the analysis boundary that
are outside these states.

The analysis regions are created using `analysis/prep/define_region.py`.

This produces 5 main output files for each analysis region:

- state boundaries
- analysis state boundary (dissolved states)
- HUC2
- HUC4

For each of above, an FGB file is written for use in GIS, and feather file
for use later in the analysis pipeline.

### States in region

State boundaries (2022 version) were downloaded from CENSUS Tiger website.

The predefined list of states is assigned in `analysis/constants.py`.

### HUC4s in region

Watershed boundaries were extracted from the NHD WBD national dataset downloaded
on 2/15/2022 from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/National/GDB/

## 2. Prepare hydrologic boundaries

Hydrologic boundaries are used for summary units for visualization in the map
and are joined to the barrier inventory during the analysis.

These include:

- HUC6
- HUC8
- HUC12

These are extracted using `analysis/prep/boundaries/extract_watersheds.py`.

## 3. Prepare administrative and ecological boundaries

Additional boundaries are joined to the barrier inventory during the analysis.

These are processed using `analysis/prep/boundaries/prep_boundaries.py`.

Additional watershed-level priorities are joined during this processing. These
include:

- SARP Conservation Opportunity Areas at HUC8 level (provided by SARP)

### Counties

County boundaries (2022 version) were downloaded from CENSUS Tiger website.

### Federal Ownership

Kat Hoenke (SARP) provided the BLM's Surface Management Agency dataset on 3/10/2023.
This was used to extract federal ownership types.

### Protected Areas

Kat Hoenke (SARP) extracted protected area data from CBI Protected Areas and TNC Secured Lands and merged them together. Kat later obtained a boundaries layer from USFS, and overlayed this over the top (11/4/2019). Because this causes multiple owner type polygons to occur in the same location, the `Preference` attribute is added, so that we can sort on ascending preference to assign the most appropriate ownership to a given barrier (nulls assigned arbitrary high value). Only nonfederal areas were
extracted from the protected areas dataset.

### Environmental Justice Disadvantaged Communities

Environmental justice disadvantaged communites evaluated at the Census tract level
were downloaded 2/8/2023 from: https://screeningtool.geoplatform.gov/en/downloads

Following the same methods as described in the tool above, Tribal areas (2022 version)
were downloaded from the Census TIGER website.

## 4. Create boundary vector tiles

Vector tiles are are created for each of the boundary layers using `analysis/prep/boundaries/create_region_tiles.py`.
