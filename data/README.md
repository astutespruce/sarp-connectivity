DRAFT dams data obtained from Kat on 8/17/2018
SARP_Bounds data (boundary and HUCs) sent by Kat on 7/11/2018.
Level 3 & 4 ecoregions downloaded from EPA

## SARP Boundary
There was a hole between Missouri and Kentucky.  I selected the same states and Puerto Rico from Census TIGER 2015 state boundaries: SARP_states.shp
I then dissolved it: SARP_boundary.shp


## Dams vector tiles

To convert dams to CSV:
```
ogr2ogr -f CSV sarp_dams.csv Dams_WebViewer.gdb Dam_Inventory_AllDams_Metrics_Draft_Two_08172018 -overwrite
```

To convert dams to mbtiles:

1. First convert to GeoJSON (use WGS84):
```
ogr2ogr -f GeoJSON -t_srs EPSG:4326 sarp_dams.json Dams_WebViewer.gdb Dam_Inventory_AllDams_Metrics_Draft_Two_08172018
```

TODO: investigate using CSV instead of GeoJSON so that we can manage attributes.  Already contains x,y fields with long,lat

2. Then convert GeoJSON to MBTiles:
TODO: tune tile creation / base zoom & reduce rate.  Right now guesses base zoom of 5
TODO: revisit clustering: https://github.com/mapbox/tippecanoe#clustered-points-world-cities-summing-the-clustered-population-visible-at-all-zoom-levels
TODO: refine included attributes

Include select attributes that will be used to join to other info:
UniqueID,State,HUC12,Ecoregion4,Ecoregion3

Consider adding:
River,Height,PurposeCategory,<other domain fields>

```
tippecanoe -Bg -o ../../tiles/sarp_dams.mbtiles -n "SARP Dams" -A "SARP" -N "SARP Dams" -y UniqueID -y State -y HUC12 -y Ecoregion4 -y Ecoregion3 sarp_dams.json
```




## Ecoregions
Downloaded L3 and L4 ecoregions from EPA.

Selected by location in ArcMap against SARP_boundary:
* SARP_ecoregion4.shp
* SARP_ecoregion3.shp

Dissolved on L2_CODE:
* SARP_ecoregion2.shp

Dissolved on L1_CODE:
* SARP_ecoregion1.shp


## Watersheds
Obtained HUC12 - HUC8 levels from Kat

To HUC8 layer, added fields 
* HUC6 = HUC8[:6].  Dissolved on this field: SARP_HUC6.shp
* HUC4 = HUC8[:4].  Dissolved on this field: SARP_HUC4.shp
* HUC2 = HUC8[:2].  Dissolved on this field: SARP_HUC2.shp
