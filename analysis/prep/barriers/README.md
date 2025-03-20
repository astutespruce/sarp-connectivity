# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Aquatic Barriers

This is the main data flow for updating barrier data, each time new barriers need to be processed for use in the tool.

Barriers are extracted from multiple sources for the network connectivity and barrier prioritization analyses.
These are processed in the following order.

1. dams
2. waterfalls
3. road-related barriers (surveyed) and road crossings (unsurveyed)

NOTE: surveyed road-related barriers are called “small barriers” throughout the data processing pipeline and unsurveyed road-related barriers are called “road crossings”.

The output of the processing steps below are full barriers datasets in `data/barriers/master` and a subset of dams, small barriers, and waterfalls that were snapped to the aquatic network in `data/barriers/snapped`.

The full datasets include attributes that identify whether they were dropped (removed from all analyses and not shown on map), excluded (removed from all analyses but shown on map), snapped, or duplicates.

WARNING: There are many duplicate dams within the inventory. Some occur very near each others, others are quite far away (>250m). The scripts try to identify likely duplicates and remove them from analysis.

## ArcGIS Online token

Your `.env` file in the root of the project must contain:

```bash
AGOL_TOKEN=<token>
AGOL_PRIVATE_TOKEN=<token>
```

`AGOL_TOKEN` is based on an FWS collaborator account that has access to SARP's services on the FWS AGOL organization. `AGOL_PRIVATE_TOKEN` is based on a separate account within SARP's own AGOL organization; this is used to access the feature services for private barriers. To get each kind of token, sign in to the FWS and SARP AGOL accounts, then use the network tab in your browser to look at any requests that include `token=<token>` as part of the URL's query parameters and copy / paste that token value into the `.env` file. These tokens are only valid for a short period and you will need to refetch them if running the download script multiple times over a relatively short period.

See Kat Hoenke @ SARP for access to these accounts.

## Data sources:

- Dams: hosted on FWS ArcGIS Online
- Surveyed road barriers: hosted on ArcGIS Online in FWS organization (public barriers) and SARP organization (private barriers); services include related crossing survey photos
- Waterfalls: hosted on FWS ArcGIS Online
- Modeled road crossings: downloaded from USGS in Feb 2022 and provided directly by Kat from USFS data sources.
- National Anthropogenic Barriers Database (NABD): obtained by Kat and provided on 1/22/2021
- OpenStreetMap

## One-time data preparation

See [analysis/prep/barriers/special/README.md](./special/README.md) for steps that are performed a single time in advance or on every update of the underlying aquatic network data or contextual data used for spatial joins.

## Barrier data download for each data release

Dams, surveyed road-related barriers, and waterfalls are downloaded from ArcGIS Online using `analysis/prep/barriers/download.py`.

This is run at the beginning of each data update cycle. This script will check for duplicate SARPIDs, which must be fixed by Kat in the master services and re-downloaded.

The date of this download is used as the publish date of this data release cycle.

## Barrier data processing

During the following process steps, barriers are assigned a status to determine how they may participate in later steps in the analysis. These terms have special meaning below:

- dropped: barriers are dropped from all analyses after this step; they are not used in the network analysis, they do not show on any maps, and they are not available for download. These are intended to capture data errors and barriers that don’t exist and are not associated with known removed barriers.
- excluded: barriers that do not break the network in any network analysis. These are intended to capture barriers that do not impede the movement of species (e.g., fully passable). These are included for display in maps and are available for download.
- invasive: natural or anthropogenic barriers specifically identified as barriers that impede the movement of invasive species. These break the network but are not prioritized for removal during ranking steps.
- duplicate: barriers that duplicate other barriers at the same general location; to the degree possible these are identified manually and automatically. These are dropped from all analyses after this step.

### Dams

Dams are processed using `analysis/prep/prep_dams.py`.

#### Update master to manually snapped locations

The downloaded dam data includes a manually snapped dams dataset from ArcGIS Online. These locations are edited by users to correct snapping errors, or otherwise flag dams that should be excluded from processing. The locations of dams have been updated using corrected locations obtained from the National Anthropogenic Barrier database or snapped manually by SARP staff and aquatic connectivity team members. These corrected locations are joined to the master inventory. Depending on the combination of attributes between the master inventory and the snapping locations, the manually snapped records may override the location and other attributes in the master inventory.

NOTE: manually snapped dams are intentionally managed as a separate map service to control the degree of access by users, which requires the script to re-sync the manual snapping status back into the master.

Additional snapped locations are read directly from the NABD dataset and used to supplement cleanup of the locations in the master inventory where they were not otherwise manually snapped and where they can be joined on NIDID.

#### Data cleanup and recoding

The script performs a variety of data cleanup and recoding operations to try and standardize values. It will recode certain text attributes into integer domains for use in the API and user interface; these are decoded back to text before display to the user.

#### Marking dam status for use in the data pipeline

Dams are marked to drop completely from all analyses if any of the following are true:

- reconnaissance (`Recon`) indicates dam may have been removed or an error (no longer visible) or if dam is proposed and not yet built
- feasibility (`Feasibility`) indicates dam is an error
- manual review (`ManualReview`) indicates dam should be deleted because it was manually identified as a duplicate or does not exist
- type of structure (`StructureCategory`) indicates that the dam does not have a physical barrier structure (e.g., no-structure diversion)

Dams are marked to exclude from breaking the network if any of the following are true:

- feasibility indicates they were breached with full flow
- passage facility (`PassageFacility`) indicates they were partially breached or had a barrier removal
- passability (`Passability`) indicates no barrier
- reconnaissance or feasibility indicates a fish passage was installed and passability is marked as passable or unknown

Dams are marked as invasive species barriers if any of the following are true:

- reconnaissance indicates they are invasive species barriers
- feasibility indicates they are invasive species barriers
- manual review indicates they are invasive species barriers
- invasive species (`InvasiveSpecies`) attribute indicates invasive barrier

NOTE: invasive species barriers break the networks but are not prioritized for removal in the ranking calculations.

Dams are marked as removed barriers if any of the following are true:

- reconnaissance indicates dam was deliberately removed
- feasibility indicates dam was deliberately removed
- manual review indicates dam was deliberately removed

NOTE: removed dams only break the network when calculating network statistics for removed barriers; they do not otherwise break the networks.

Dams are marked as estimated dams if any of the following are true:

- name (`Name`) indicates it was estimated
- source (`Source`) indicates it was estimated

NOTE: estimated dams are derived from an analysis of NHD waterbodies and flowlines and are are manually reviewed using imagery to determine that they are likely indeed anthropogenic dams and not natural features.

#### Initial deduplication

Dams may be marked by manual review as duplicates; these are marked as duplicates throughout and are not used alongside other dams during any other deduplication process.

Dams are automatically deduplicated before snapping based on a 10 meter tolerance. Dams with the highest level of information available are given higher precedence to retain during deduplication, and removed dams are given the highest precedence.

#### Snapping

The majority of the snapping logic called during processing of dams is in `analysis/prep/barriers/lib/snap.py`.

Dams are assigned a snapping tolerance based on their characteristics:

- by default, dams are given a 150 meter tolerance
- dams from data sources that are likely off network (e.g., retention ponds) or flowlines not yet mapped in NHD are given a 50 meter tolerance
- estimated dams are given a 25 meter tolerance
- dams that are manually snapped are given a 25 meter tolerance
- dams that are marked on network or from NABD are given a tolerance based on their length (`Length`), rounded to the nearest 100 meters, up to 1000 meters; this is intended to handle dams that are very long and represented by a point far from the crossing point with the network

Dams that are marked as off-network during manual review or identified as duplicates prior to snapping are not snapped to the network.

Dams are snapped to the network using the following ordered sequence of steps. As soon as a dam snaps according to a given step, it is not analyzed further during the snapping process. At several of the steps, the approach uses a series of snapping targets to try and find the best fit for a given dam. Any dams that are not snapped are not allowed to break the network during analysis, but are still displayed on maps and available for download.

##### 1. Snap estimated dams to waterbody drain points

Waterbody drain points are the downstream-most points on the network where it exits a given waterbody. These are extracted based on the configuration of the aquatic network and waterbodies during preparation of the NHD data.

Estimated dams that haven’t already been manually snapped to the network are first snapped to the nearest waterbody drain point within 25 meters. This snapping is tailored for estimated dams that were originally estimated from the network at the drain points.

Any that did not initially snap to the drain point but are inside a waterbody or within 1 meter of its edge, and that waterbody has only a single drain point, and are within 2000 meters of that drain point are snapped to that drain point. This snapping is tailored for estimated dams from earlier generations of the estimated dams analysis, which generally occur well within waterbodies rather than at their drain points.

##### 2. Snap dams to NHD dam points

NHD dam points are identified during preparation of the aquatic network and dam features within NHD. These are generally points on the aquatic network where flowlines cross dam line or polygon features in NHD and are taken as a strong indication that a dam exists at that location. These dams are particularly useful for dams that are very long, where the point within the inventory is representative of the dam location but nowhere near the crossing point with the aquatic network.

The process first finds dams that are near NHD dam point within the tolerance associated with each dam (above); these become snapping target candidates. These candidates are then filtered to remove any that are more than 10 times as far away from a given dam as the closest candidate, unless they are all within 150 meters. The candidates are then sorted based on descending size class, network loop status, and snapping distance.

It then finds all waterbody drain points that are within 150 meters of each dam. Any dams that are closer to a drain point associated with a waterbody that is larger than the waterbody associated with the NHD dam are dropped from this snapping.

For the rest, it then snaps the dam to the first NHD dam candidate. This intentionally favors snapping to nearby NHD dams that are on larger streams and associated with larger waterbodies and avoids snapping to loops where possible.

##### 3. Snap dams to waterbodies

For this step, known lowhead dams are given a tolerance of 100 meters to prevent moving them from a more correct location mid-stream to a further location that is associated with an impoundment. This is especially important where dams occur in a chain where some are run of the river / lowhead dams and others have small impoundments.

For each dam, it tries to find the nearest waterbody (polygon) within 1 meter; this mostly selects for those that are within or very near the waterbody. It then finds the nearest drain point of that waterbody (there may be multiple per waterbody). These become the snapping candidates, which are sorted by descending size class, network loop status, and snapping distance. Any dams that are within their tolerance of the candidate drain point are snapped to that candidate. This favors snapping to larger stream sizes and avoids network loops where possible.

For remaining dams that are not within or immediately next to a waterbody, it finds the nearest waterbody drain point within 250 meters, and then brings in all other drains associated with the waterbody associated with that drain point and calculates their distance away from each dam in question. These become the snapping candidates, which are sorted by descending size class, network loop status, and snapping distance. Any dams that are within their tolerance of the candidate drain point are snapped to that candidate.

##### 4. Snap dams to flowlines

For each dam, it finds flowlines within its tolerance; these become snapping target lines. It drops any off-network flowlines (as coded by NHD) if they are greater than 25 meters away; this assumes that any dams or diversion structures on those off-network flowlines, which are generally canals and ditches, must be precisely located in order to snap to them, and this prevents dams on main channels from snapping to structures on a parallel canal or ditch.

Within the set of candidates, it tries to find the nearest non-loop flowline if it is within 25 meters of the dam. This covers the case at junctions of multiple flowlines at the exit of a waterbody, where some of them may be coded as loops. Because any that snap to loops are discarded from the network analysis, this tries to snap to non-loops where possible.

It then takes the nearest flowline (or nearest non-loop from above) and calculates the nearest position on that flowline to the original dam point and uses that as the snapped coordinate.

#### Post-snapping deduplication

After snapping, dams are deduplicated again using a 10 meter tolerance, preferring the dams with the most information available, and removed dams are given the highest precedence. Estimated dams are deduplicated within a 50 meter tolerance.

#### Spatial joins

Dams are spatially joined to a variety of contextual datasets after snapping.

#### Export dams for network analysis

Snapped dams that are not marked as dropped, excluded, or duplicates can participate in at least some of the types of network analyses. Dams always cut the networks for dams, road-related, and small-bodied fish network analyses. Dams that are included in the large-bodied fish network analysis if they are not marked as being passable to salmonids.

### Waterfalls

Waterfalls are processed using `analysis/prep/barriers/prep_waterfalls.py`.

This script cleans and recodes waterfall data for use throughout the data analysis pipeline.

#### Marking waterfall status for use in the data pipeline

Waterfalls are dropped from the analysis if any of the following are true:

- reconnaissance indicates waterfall is an error or does not appear to exist
- manual review indicates waterfall is an error
- waterfall is specifically known to be a historical waterfall and no longer presents as a barrier given current network configuration (e.g., drowned waterfalls within impoundments / impounded rivers)
- waterfall type indicates historical, rapids (not considered to be a network breaking barrier), or associated with a dam

Waterfalls are excluded from breaking the networks if any of the following are true:

- barrier severity (`BarrierSeverity`) indicates no barrier

Waterfalls are marked as blocking the spread of invasive species if any of the following are true:

- reconnaissance indicates invasive species barrier
- manual review indicates invasive species barrier

#### Snapping & deduplication

Waterfalls are snapped to the aquatic network based on a 100 meter tolerance.

Waterfalls are then deduplicated against each other using a 50 meter tolerance.

Waterfalls are then deduplicated against dams based on a 50 meter tolerance.

#### Spatial joins

Waterfalls are spatially joined to a variety of contextual datasets after snapping.

#### Export waterfalls for network analysis

Snapped waterfalls that are not marked as dropped, excluded, or duplicates can participate in at least some of the types of network analyses. Waterfalls always cut the networks for dams, road-related, and small-bodied fish network analyses. Waterfalls that are included in the large-bodied fish network analysis if they are not marked as being passable to salmonids.

### Road-related barriers and crossings

Road-related barriers are processed using `analysis/prep/barriers/prep_road_barriers.py`.

Modeled USGS and USFS road / stream crossings are first prepared as described in [analysis/prep/barriers/special/README.md](./special/README.md).  They are deduplicated and snapped to the network.  They are then used as snapping targets for surveyed road-related barriers.

Any modeled crossings not already assigned to a crossing type that occur on stream orders of at least 7 are marked as assumed bridges instead of assumed culverts.  This affects how they are snapped below.

Modeled crossings are dropped if they are within 10 meters of a snapped dam or waterfall.

Surveyed road-related barriers (“surveyed barriers” hereafter) are cleaned and recoded to standardize data values.


#### Marking road barrier status for use in the data pipeline

Surveyed barriers are dropped from the analysis if any of the following are true:
- potential project (`PotentialProject`) indicates there is no crossing
- reconnaissance indicates barrier was removed or in error or crossing is proposed and not built
- manual review indicates barrier is an error

Surveyed barriers are excluded from breaking the network in any analysis if any of the following are true:
- potential project is not one of the types that indicates a barrier (severe, moderate, significant, indeterminate, or minor barrier, or potential or proposed project )

Surveyed barriers are marked as blocking the spread of invasive species if any of the following are true:
- reconnaissance indicates invasive species barrier
- manual review indicates invasive species barrier

Surveyed barriers are marked as removed barriers if any of the following are true:
- potential project indicates barrier was removed (past or completed project)
- reconnaissance indicates barrier was deliberately removed
- manual review indicates barrier was deliberately removed

#### Marking road barrier ownership

Surveyed barriers are joined to the nearest road in Census TIGER roads (2022 version) within a 50 meter tolerance to supplement barrier owner type if not otherwise available in the surveyed barriers data.

#### Snapping

Surveyed barriers are assigned a snapping tolerance based on their data source:
- by default, all barriers use a 50 meter tolerance
- barriers from Oregon or Washington use a 75 meter tolerance
- barriers from the USFS bat survey use 100 meter tolerance
- barriers that are manually snapped use a 25 meter tolerance

Surveyed barriers that are dropped or manually identified as off network are not snapped at all.

Surveyed barriers are joined to modeled crossings on a shared identifier (where crossing IDs were included as part of the data provided during survey in the field).  Where a surveyed barrier occurs within 250 meters of the modeled crossing, the surveyed barrier is snapped to that crossing; beyond that we assume that they are data entry errors.

We then find the nearest modeled crossing for each surveyed barrier within a 50 meter tolerance.  The surveyed barrier is then snapped to the modeled crossing point, and the modeled crossing is marked as associated with that barrier (and vice-versa).

The remaining surveyed barriers are then snapped to the nearest flowline based on their type, within the tolerance based on their data source.  Culverts are snapped to the nearest flowline that is less than stream order 7 to prevent them from snapping to large rivers (more likely to be bridges) when they are in fact culverts on incoming smaller tributaries (mapped or unmapped).  All other surveyed barrier types are snapped to the nearest flowline.

#### Post-snapping deduplication

After snapping, surveyed barriers are deduplicated using a 10 meter tolerance, preferring barriers with the highest barrier severity, and removed barriers are given the highest precedence.

Surveyed barriers are dropped if they are within 10 meters of a dam or waterfall.

#### Spatial joins

Surveyed barriers are spatially joined to a variety of contextual datasets after snapping.


#### Export surveyed barriers for use in the network analysis

Surveyed barriers that were were snapped to flowlines not marked as loops or off-network flowlines, and not dropped or marked as duplicates are exported for network analyses depending on their barrier severity.

For the default network analysis, all surveyed barriers of greater severity than minor barriers are used to break the network.  For the large-bodied fish analysis, only severe and significant barriers and potential or proposed projects break the network.  For the small-bodied fish analysis, all surveyed barriers (including minor barriers) break the network.

#### Export modeled crossings for use in planning surveys

Modeled crossings are attributed to surveyed status if a surveyed barrier snapped to them above.  All snapped modeled crossings are exported for use in the Survey view in the user interface, which allows filtering crossings based on surveyed status as as other factors.