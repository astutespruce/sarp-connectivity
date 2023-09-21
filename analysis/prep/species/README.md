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

### Eastern Brook Trout

Eastern Brook Trout potential distribution data were compiled by Trout Unlimited
and provided to SARP on 8/30/2023. These include medium and high resolution
flowlines.

### StreamNet salmonid species

Habitat linework for several salmonid species in the Pacific Northwest were
downloaded from https://www.streamnet.org/home/data-maps/gis-data-sets/
on 9/7/2023.

StreamNet data are prepared and associated with NHD flowlines using
`analysis/prep/species/prep_streamnet.py`.
This selects out species and runs of interest, fills small gaps between
endpoints, and merges the habitat linework. It then tries to find closely
related NHD flowlines that have sufficient overlap with the habitat linework.

NOTE: this merges lines that overlap; this means that canals / ditches that may
be functionaly separate from regular flowlines but spatially overlap are merged
together into a contiuous set of linework.

NOTE: StreamNet data combine linework from multiple sources and levels of detail.
Some areas may have very low resolution linework and not line up well with NHD HR.

### California Baseline Fish Habitat

California Baseline Fish Habitat data were downloaded 9/15/2023 from
https://psmfc.sharefile.com/d-s03b563353ec340faba23d1f14b073f3c

Metadata available at: https://psmfc.maps.arcgis.com/home/item.html?id=a8117ce44a16493ca2aa0571769e5654

These data are prepared and associated with NHD flowlines using
`analysis/prep/speciescprep_ca_baseline_habitat.py`.
