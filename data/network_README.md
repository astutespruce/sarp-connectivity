# Network data processing

This uses https://github.com/brendan-ward/nhdnet for processing

1. Download NHDPlus HR data for all applicable HUC4s that have dams. Note: Region 8 is not available yet.
2. Get the barriers inventory from Kat
3. Run `nhdnet/sarp/custom/prepare_nhd.py` for each applicable region
4. Run `nhdnet/sarp/custom/merge.py` to merge HUC4s to regions and region groups for later processing
5. Run `nhdnet/sarp/custom/create_spatial_indices.py` to create the spatial indices needed for later processing
6. Run `nhdnet/sarp/custom/snap_dams_for_qa.py` to generate dams for manual QA. Send these to Kat. She moves points to get them in the right place, removes ones that are not present at all, and codes them as to known off-network dams. Right now, this is limited only to those likely to snap to the largest size classes in the network.
7. Run `nhdnet/sarp/custom/prep_dams.py` to snap all QA'd dams to the network
8. Run `nhdnet/sarp/custom/prep_small_barriers.py` to snap all small barriers to the network
9. Run `nhdnet/sarp/custom/prep_waterfalls` to snap all waterfalls to the network.
10. Run `nhdnet/sarp/custom/network_analysis.py` for the actual network analysis (cutting of segments, dissolving functional networks, network stats, etc)
