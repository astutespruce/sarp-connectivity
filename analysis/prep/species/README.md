# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Species Data Preparation

Data on T&E species are obtained by SARP from regional and state partners. These
are summarized to the HUC12 level. Where possible, additional names of T&E species
are used to help find listed species in the data where they have been subject
to taxonomic change.

Data on trout species are obtained by SARP and joined at the HUC12 level.

## Salmonid ESU / DPS

Data on Salmon Evolutionarily Significant Units (ESUs) and Steelhead Trout
Discrete Population Segments (DPSs) are obtained by SARP from NOAA. These are
spatially joined to HUC12s.

These are prepared using `analysis/prep/species/prep_salmonid_esu.py`.

## Species summaries

Data are processed using `analysis/prep/species/calculate_spp_stats.py`.

## Species habitat data

IMPORTANT: species habitat data are assigned to "cleaned" NHD flowlines output
by `analysis/prep/network/prepare_flowlines_waterbodies.py`.

### Eastern Brook Trout

Eastern Brook Trout potential distribution data were compiled by Trout Unlimited
and provided to SARP on 8/30/2023. These are based on NHD medium resolution
flowlines. These data are prepared and associated with NHD high resolution
flowlines using `analysis/prep/species/prep_eastern_brook_trout.py`.

### StreamNet salmonid species

Habitat linework for several salmonid species in the Pacific Northwest were
downloaded on 9/7/2023 from https://www.streamnet.org/home/data-maps/gis-data-sets/.
These data represent current habitat and account for impassable barriers.

StreamNet data are prepared and associated with NHD flowlines using
`analysis/prep/species/prep_streamnet.py`.
This selects species of interest, fills small gaps between endpoints, and merges
the habitat linework. It then tries to find closely related NHD flowlines that
have sufficient overlap with the habitat linework.

NOTE: this merges lines that overlap; this means that canals / ditches that may
be functionaly separate from regular flowlines but spatially overlap are merged
together into a contiuous set of linework.

NOTE: StreamNet data combine linework from multiple sources and levels of detail.
Some areas may have very low resolution linework and not line up well with NHD HR.

### California Baseline Fish Habitat

California Baseline Fish Habitat data were downloaded 9/15/2023 from
https://psmfc.sharefile.com/d-s03b563353ec340faba23d1f14b073f3c. These data
represent potential habitat for anadromous species and resident rainbow trout
in southern California.

Metadata available at: https://psmfc.maps.arcgis.com/home/item.html?id=a8117ce44a16493ca2aa0571769e5654

These data are prepared and associated with NHD flowlines using
`analysis/prep/species/prep_ca_baseline_habitat.py`.

### South Atlantic Anadromous Species Habitat

Data were provided by Kat Hoenke from the SEACAP project.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_south_atlantic_anadromous.py`.

### Chesapeake Bay Diadromous Species Habitat

Data were provided by Erik Martin (TNC) on 11/15/2022. We extracted current
and potential habitat, but not historic habitat.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_chesapeake_species_habitat.py`.

### Combined Species Habitat

The datasets above are combined together using
`analysis/prep/species/aggregate_species_habitat.py`. This merges eastern
brook trout to include the brook trout data from the Chesapeake dataset, and
contains a boolean column per species and group (e.g., anadromous species from
streamnet).
