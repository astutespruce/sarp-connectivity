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

State boundaries (2023 version) were downloaded from CENSUS Tiger website.

The predefined list of states is assigned in `analysis/constants.py`.

### HUC4s in region

Watershed boundaries were extracted from the NHD WBD national dataset downloaded
on 8/28/2024 from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/National/GDB/

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

### Fish Habitat Partnership boundaries

Fish Habitat Partnership boundaries were downloaded on 4/26/2024 from
https://www.sciencebase.gov/catalog/item/53710d71e4b07ccdd78b368e
and are used to spatially join to barriers.

### Native territories

Native Territories were downloaded 4/10/2024 from https://native-land.ca/

### Priority areas

These include:

- SARP Conservation Opportunity Areas at HUC8 level (provided by SARP).
- Hawaii FHP geographic focus areas (provided by Kat via email on 9/3/2024).

Priority areas are only used for overlay in the maps, not filtering.

### Wild & Scenic rivers

Wild & scenic rivers were provided by Kat Hoenke via email from USFS on 9/12/2024.

These were prepared using `analysis/prep/boundaries/prep_wild_scenic_rivers.py`.

These are used to create buffers that are used for spatial joins because the
wild and scenic rivers may be based on different linework than NHD HR.

These are included alongside the priority areas above for overlay in the map as well.

### Counties

County boundaries (2023 version) were downloaded from CENSUS Tiger website.

### Congressional districts

Congressional districts (2023 version) were downloaded from Census TIGER from
https://www2.census.gov/geo/tiger/TIGER2023/CD/ on 10/3/2024 using
`analysis/prep/boundaries/prep_congressional_districts.py`.

### Protected areas / land ownership

PAD-US v4.0 GDB version downloaded 6/4/2024 from: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

PAD-US v4.0 contains invalid records. To get around this, create a geopackage and
force MultiSurface geometries to MultiPolygon:

```bash
ogr2ogr source_data/ownership/pad_us4.0.gpkg source_data/ownership/PADUS4_0_Geodatabase.gdb PADUS4_0Combined_Proclamation_Marine_Fee_Designation_Easement -progress -skipfailures -nlt MultiPolygon
```

USFS-specific surface ownership parcels were downloaded from https://data-usfs.hub.arcgis.com/datasets/24db18ef747945c49b02252ae39ec4aa_0/explore
on 4/10/2024.

Additional areas for Hawaii were downloaded from: https://prod-histategis.opendata.arcgis.com/datasets/HiStateGIS::reserves/about
on 9/4/2024.

### Environmental Justice Disadvantaged Communities

Environmental justice disadvantaged communities evaluated at the Census tract level
were downloaded 2/8/2023 from: https://screeningtool.geoplatform.gov/en/downloads

Following the same methods as described in the tool above, Tribal areas (2022 version)
were downloaded from the Census TIGER website.

### Native territories

Native territories were downloaded from Native Land Digital (https://native-land.ca/)
on 4/10/2024.

## 4. Create boundary vector tiles

Vector tiles are are created for each of the boundary layers using `analysis/prep/boundaries/create_map_unit_tiles.py`.

Vector tiles of priority areas are created using `analysis/prep/boundaries/create_priority_area_tiles.py`.
