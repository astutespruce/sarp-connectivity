Southeast Aquatic Barrier Inventory - dams data download

Date downloaded: {{date}}
Data version: {{version}}
Downloaded from: {{url}}
Filename: {{filename}}

### Selected Area: ###
{{layer}}: {{ids}}


### Description ###

This inventory is a growing and living database of dams and road / stream crossings compiled by
the Southeast Aquatic Resources Partnership with the generous support from many partners and
funders. Information about network connectivity, landscape condition, and presence of threatened
and endangered aquatic organisms are added to this inventory to help you investigate barriers at
any scale for your desired purposes.

This inventory consists of datasets from local, state, and federal partners. It is supplemented
with input from partners with on the ground knowledge of specific structures. The information on
barriers is not complete or comprehensive across the region, and depends on the availability and
completeness of existing data and level of partner feedback. Some areas of the region are more complete than others but none
should be considered 100% complete.

All network analyses were conducted using the NHD High Resolution Plus dataset 
(https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution).

If you are able to help improve the inventory by sharing data or assisting with field
reconnaissance, please contact us (https://southeastaquatics.net/about/contact-us).


### File Contents ###
lat: latitude.
lon: longitude.
Name: Barrier name, if available.
SARPID: SARP Identifier.
NIDID: National Inventory of Dams Identifier.
Source: Source of this record in the inventory.
River: River name where dam occurs, if available.

Year: year that construction was completed, if available.  0 = data not available.
Height: dam height in feet, if available.  0 = data not available.
Construction: material used in dam construction, if known.
Purpose: primary purpose of dam, if known.
Condition: condition of the dam as of last assessment, if known.  Note: assessment dates are not known.
Feasibility: feasibility of dam removal, based on reconnaissance.  Note: reconnaissance information is available only for a small number of dams.
TESpp: Number of federally threatened or endangered aquatic species within the same subwatershed (HUC12) as the dam.  Note: Rare species information is based on occurrences within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time.
OwnerType: Land ownership type.  This information is derived from the CBI Protected Areas Database and TNC Secured Lands Database, to highlight ownership types of particular importance to partners.  NOTE: does not include most private land.
ProtectedLand: Indicates if the dam occurs on public land as represented within the CBI Protected Areas Database of the U.S. and TNC Secured Lands Database.

Basin: Name of the hydrologic basin (HUC6) where the dam occurs.
HUC6: Hydrologic basin identifier where the dam occurs.
HUC8: Hydrologic subbasin identifier where the dam occurs.
HUC12: Hydrologic subwatershed identifier where the dam occurs.
County: County where dam occurs.
State: State where dam occurs.
ECO3: EPA Level 3 Ecoregion Identifier.
ECO4: EPA Level 4 Ecoregion Identifier.

HasNetwork: indicates if this dam was snapped to the aquatic network for analysis.  1 = on network, 0 = off network.  Note: network metrics and scores are not available for dams that are off network.
StreamOrder: NHDPlus Modified Strahler stream order. -1 = not available.
Landcover: average amount of the river floodplain in the upstream network that is in natural landcover types. -1 = not available.
Sinuosity: length-weighted sinuosity of the upstream river network.  Sinuosity is the ratio between the straight-line distance between the endpoints for each stream reach and the total stream reach length. -1 = not available.
SizeClasses: number of unique upstream size classes that could be gained by removal of this dam. -1 = not available.
UpstreamMiles: number of miles in the upstream river network from this dam. -1 = not available.
DownstreamMiles: number of miles in the complete downstream river network from this dam.  Note: this measures the length of the complete downstream network including all tributaries, and is not limited to the shortest downstream path. -1 = not available.
GainMiles: absolute number of miles that could be gained by removal of this dam.  Calculated as the minimum of the upstream and downstream network lengths. -1 = not available.
TotalNetworkMiles: upstream plus downstream network miles. -1 = not available.

SE_NC_tier: network connectivity tier for all on-network dams within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the dams within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.
SE_WC_tier: watershed condition tier for all on-network dams within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the dams within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.
SE_NCWC_tier: combined network connectivity and watershed condition tier for all on-network dams within hydrologic basins that fall completely or partly within the Southeastern US states.  Tier 1 represents the dams within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.

State_NC_tier: network connectivity tier for the state that contains this dam.  Tier 1 represents the dams within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.
State_WC_tier: watershed condition tier for the state that contains this dam.  Tier 1 represents the dams within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.
State_NCWC_tier: combined network connectivity and watershed condition tier for the state that contains this dam.  Tier 1 represents the dams within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.

NC_tier: network connectivity tier for your selected subset.  Tier 1 represents the dams within the top 5% of scores for network connectivity and tier 20 represents the lowest 5%.  -1 = not prioritized.
WC_tier: watershed condition tier for your selected subset.  Tier 1 represents the dams within the top 5% of scores for watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.
NCWC_tier: combined network connectivity and watershed condition tier for your selected subset.  Tier 1 represents the dams within the top 5% of scores for the combined network connectivity and watershed condition and tier 20 represents the lowest 5%.  -1 = not prioritized.


### Caveats and Data Limitations ###

Note: data come from a variety of sources and available descriptive information is not comprehensive.

Note: information on rare species is highly limited.

