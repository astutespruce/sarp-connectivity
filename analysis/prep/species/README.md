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
