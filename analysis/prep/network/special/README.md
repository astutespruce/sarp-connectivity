# Southeast Aquatic Barrier Inventory - Special Processing Scripts

This directory contains special-purpose processing scripts to work around specific data issues.

## NHD Region 02 - Chesapeake Bay

The raw NHD flowline data in Region 02 contain artificial segments that span Chesepeake Bay. Left uncorrected, these cause networks to be joined across the bay.

`region2.py` performs spatial joins of flowlines and Chesapeake Bay to identify artificial segments that are completely within the bay.
These IDs are added to `analysis/constants.py` so that they are excluded when flowlines are extracted from the source NHD geodatabase in this region.
