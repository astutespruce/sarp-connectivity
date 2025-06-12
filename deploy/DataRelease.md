# National Aquatic Barrier Inventory and Prioritization Tool - Data Release workflow

## Analysis steps

Note: assumes no changes to the prepared network, species, floodplain natural
landcover, or boundaries used for spatial joins; assumes that only updates are
an updated batch of barrier data.

### Download, cleanup, and snap barriers:

1. manually fetch the latest ArcGIS Online tokens and save them to `.env`
2. `python analysis/prep/barriers/download.py`
3. If there are duplicate SARPIDs, contact Kat to resolve them and download again afterward
4. `python analysis/prep/barriers/prep_dams.py`
5. `python analysis/prep/barriers/prep_waterfalls.py`
6. `python analysis/prep/barriers/prep_road_barriers.py`

### Run network analysis and aggregate results

1. `python analysis/network/cut_flowlines.py`
2. `python analysis/network/run_network_analysis.py`
3. `python analysis/network/calc_removed_barrier_stats.py`
4. `python analysis/post/aggregate_networks.py`

### Create tiles

1. `python analysis/post/create_barrier_tiles.py`
2. `python analysis/post/create_network_tiles.py` (takes several hours)
3. `python analysis/post/create_summary_tiles.py`

### Update summaries and maps built into user interface

1. `python analysis/post/extract_summary_stats.py`
2. `python analysis/post/create_static_maps.py`

## Data uploading steps

### Deploy to staging server

1. in the AWS console, attach the `transfer - tiles2` volume to the staging server as `/dev/sdf`
2. ssh to the staging server
3. run `lsblk` to determine what device that was mounted at, e.g., /dev/nvme2n1
4. mount that as `/tiles2`: `sudo mount /dev/nvme2n1 /tiles2`
5. delete all contents from that volume: `sudo rm -rf /tiles2/*`
6. exit the staging server
7. use `rsync` from the local workstation to transfer the contents of the local `tiles` directory to `/tiles2` on the server
8. use `rsync` from the local workstation to transfer the contents of the local `data/api` directory to `/tiles2/api` on the server
9. ssh to the staging server
10. stop services:

    - `sudo service api stop`
    - `sudo service arq stop`
    - `sudo service mbtileserver stop`

11. delete all contents of `/tiles`: `sudo rm -rf /tiles/*`
12. delete all contents of the home data directory: `sudo rm -rf /home/app/sarp-connectivity/data/api/*`
13. delete all contents of the download directories:
    - `sudo rm -rf /downloads/national/*`
    - `sudo rm -rf /downloads/custom/*`
14. copy latest data to the tiles directory: `sudo cp -aR /tiles2/* /tiles/`
15. copy the API data to the home directory: `sudo cp -a /tiles2/api/*.feather /home/app/sarp-connectivity/data/api`, `sudo cp -a /tiles2/api/*.db /home/app/sarp-connectivity/data/api`
16. copy the national download zip files to the downloads directory: `sudo cp -a /tiles2/api/downloads/* /downloads/national/`
17. as the `app` user: `sudo su app`
18. pull the latest code `git pull origin` (update any dependencies at this point, if needed)
19. rebuild the UI: `cd ui && npm run deploy`
20. exit the `app` user
21. bring th services back up:
    - `sudo service api start`
    - `sudo service arq start`
    - `sudo service mbtileserver start`
22. make sure they all came up properly
    - `sudo service api status`
    - `sudo service arq status`
    - `sudo service mbtileserver status`
23. unmount the transfer volume: `sudo umount /tiles2`
24. exit the staging server

Test the staging server and get Kat's approval for recent changes.

### Deploy to production server

1. in the AWS console, detach the `transfer - tiles2` volume from the the staging server and attach to the production server as `/dev/sdf`
2. ssh to the production server
3. run `lsblk` to determine what device that was mounted at, e.g., /dev/nvme2n1
4. mount that as `/tiles2`: `sudo mount /dev/nvme2n1 /tiles2`
5. use google analytics to verify that server is not actively being used; avoid any meeting times indicated by Kat. Generally try to do this in the evening Pacific time.
6. stop services:

   - `sudo service api stop`
   - `sudo service arq stop`
   - `sudo service mbtileserver stop`

7. delete all contents of `/tiles`: `sudo rm -rf /tiles/*`
8. delete all contents of the home data directory: `sudo rm -rf /home/app/sarp-connectivity/data/api/*`
9. delete all contents of the download directories:
   - `sudo rm -rf /downloads/national/*`
   - `sudo rm -rf /downloads/custom/*`
10. copy latest data to the tiles directory: `sudo cp -aR /tiles2/* /tiles/`
11. copy the API data to the home directory: `sudo cp -a /tiles2/api/*.feather /home/app/sarp-connectivity/data/api`, `sudo cp -a /tiles2/api/*.db /home/app/sarp-connectivity/data/api`
12. copy the national download zip files to the downlods directory: `sudo cp -a /tiles2/api/downloads/* /downloads/national/`
13. as the `app` user: `sudo su app`
14. pull the latest code `git pull origin` (update any dependencies at this point, if needed)
15. rebuild the UI: `cd ui && npm run deploy`
16. exit the `app` user
17. bring th services back up:
    - `sudo service api start`
    - `sudo service arq start`
    - `sudo service mbtileserver start`
18. make sure they all came up properly
    - `sudo service api status`
    - `sudo service arq status`
    - `sudo service mbtileserver status`
19. unmount the transfer volume: `sudo umount /tiles2`
20. in the AWS console, detach the `transfer - tiles2` volume from the the production server and attach to the staging server as `/dev/sdf`

## Other data release activities

1. run `analysis/export/export_barriers.py` on `combined_barriers` with state ranking
   and post the resulting FGDB file for Kat.
