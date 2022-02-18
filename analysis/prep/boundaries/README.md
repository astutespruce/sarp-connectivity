# Southeast Aquatic Barrier Inventory Data Processing - Boundary Data Prep

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

State boundaries (2021 version) were downloaded from CENSUS Tiger website.

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

### Counties

County boundaries (2021 version) were downloaded from CENSUS Tiger website.

### EPA Ecoregions

Level 3 and 4 ecoregions were downloaded from: https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states

Note: ecoregions are not available for Puerto Rico.

### Protected Areas

Kat Hoenke (SARP) extracted protected area data from CBI Protected Areas and TNC Secured Lands and merged them together. Kat later obtained a boundaries layer from USFS, and overlayed this over the top (11/4/2019). Because this causes multiple owner type polygons to occur in the same location, the `Preference` attribute is added, so that we can sort on ascending preference to assign the most appropriate ownership to a given barrier (nulls assigned arbitrary high value).

## 4. Create boundary vector tiles

Vector tiles are are created for each of the boundary layers.

Depending on which analysis region you are creating tiles for, run one of:

- `analysis/prep/boundaries/generate_region_tiles.sh`
- `analysis/prep/boundaries/generate_sarp_tiles.sh`

Both create files with the same name in the same location, because only one
set is intended to be used at a time within this project.
