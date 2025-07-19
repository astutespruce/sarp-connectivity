# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Species Data Preparation

Data on T&E species are obtained by SARP from regional and state partners. These
are summarized to the HUC12 level. Where possible, additional names of T&E species
are used to help find listed species in the data where they have been subject
to taxonomic change.

Data on trout species are obtained by SARP and joined at the HUC12 level.

## Listed Federal Threatened & Endangered species

The authoritative list of species was downloaded from USFWS on 5/3/2024 from
https://ecos.fws.gov/ecp0/reports/ad-hoc-species-report?kingdom=V&kingdom=I&status=E&status=T&status=EmE&status=EmT&status=EXPE&status=EXPN&status=SAE&status=SAT&mapstatus=3&fcrithab=on&fstatus=on&fspecrule=on&finvpop=on&fgroup=on&header=Listed+Animals

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

### Chesapeake Bay Diadromous Species Habitat

Data were provided by Erik Martin (TNC) on 11/15/2022. We extracted current
and potential habitat, but not historic habitat.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_chesapeake_species_habitat.py`.

### Apache trout

Habitat lines for Apache trout were provided by Kat Hoenke on 4/29/2025 via email.
These data came from Dan Dauwalter, Trout Unlimited and Zachary Jackson, USFWS.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_apache_trout.py`.

### Gila trout

Habitat lines for Gila trout were provided by Kat Hoenke on 4/29/2025 via email.
These data came from Dan Dauwalter, Trout Unlimited.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_gila_trout.py`.

### Coastal cutthroat trout

Habitat lines for coastal cutthroat trout were by Kat Hoenke on 4/29/2025 via email.
These data came from the Pacific States Marine Fisheries Commission.

Because these largely duplicate coastal cutthroat data from StreamNet, these
were only integrated in NHD region 18 where StreamNet data were unavailable.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_ca_coastal_cutthroat_trout.py`.

### Lahontan cutthroat trout

Habitat lines for coastal cutthroat trout were by provided by Kat Hoenke on 4/29/2025 via email.
These data came from Trout Unlimited.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_lahontan_cutthroat_trout.py`.

### Colorado River cutthroat trout

Habitat lines for Colorado River cutthroat trout were provided by Kat Hoenke on 5/19/2025 via email.
These data came from the Colorado River Cutthroat Trout Working Group.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_colorado_river_cutthroat_trout.py`.

### Greenback cutthroat trout

Habitat lines for Greenback cutthroat trout were provided by Kat Hoenke on 5/21/2025 via email.
These data came from the Greenback Recovery Team.

These data were prepared and associated with NHD flowlines using
`analysis/prep/species/prep_greenback_cutthroat_trout.py`.

### Rio Grande cutthroat trout

Habitat lines for Rio Grand cutthroat trout were provided by Kat Hoenke on 6/26/2025 bia email.
These data came from the Rio Grande cutthroat trout working group.

These data were prepared and associated with nHD flowlines using
`analysis/prep/species/prep_rio_grande_cutthroat_trout.py`.

### Combined Species Habitat

The datasets above are combined together using
`analysis/prep/species/aggregate_species_habitat.py`. This merges eastern
brook trout to include the brook trout data from the Chesapeake dataset, and
contains a boolean column per species and group (e.g., anadromous species from
streamnet).
