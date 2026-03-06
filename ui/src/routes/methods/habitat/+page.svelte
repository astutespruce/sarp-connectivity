<script lang="ts">
	import { resolve } from '$app/paths'
	import { Alert } from '$lib/components/alert'
	import { HeaderImage } from '$lib/components/image'
	import { CONTACT_EMAIL, SITE_NAME } from '$lib/env'
</script>

<svelte:head>
	<title>Aquatic species habitat network methods | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Brandon"
	url="https://unsplash.com/photos/gray-fish-on-water-during-daytime-enPHTN3OPRw"
>
	<enhanced:img src="$lib/assets/images/brandon-enPHTN3OPRw-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Aquatic species habitat network methods</h1>
	<p class="mt-8">
		Instream habitat data for key species and species groups were compiled from regional partners
		and associated with the
		<a
			href="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution"
			target="_blank"
			rel="external"
		>
			National Hydrography Dataset - High Resolution Plus
		</a>
		(NHDPlusHR) dataset from the U.S. Geological Survey, which is used to
		<a href={resolve('/methods/network/', {})}>create the aquatic networks</a> used in this tool.
		Our overall goal is to estimate the amount of species-level habitat that could be gained by
		removing or mitgating a specific barrier based on the best available species data and
		standardized aquatic network data.
		<br />
		<br />
		These estimates are intended to be a starting point for exploring and prioritizing barriers from a
		species perspective rather than the total upstream or downstream functional networks, which may greatly
		overestimate the amount of habitat that could be made available to particular species.
	</p>

	<Alert title="Warning" class="mt-8 mb-12 text-lg">
		<p class="text-base mt-2">
			These estimates should be used with caution due to the many inherent limitations of species
			habitat data, including incomplete coverage of the current or potential distribution of a
			species, lack of data within particular stream reaches, incorrect attribution of stream
			reaches to habitat, or simplistic elevation gradient rules used to define maximum extents of
			species habitat. Furthermore, the methods below attribute habitat to entire NHDPlusHR
			flowlines without considering elevation gradients or other natural barriers that would prevent
			the dispersal of aquatic organisms, and may both over and underestimate actual habitat for
			these species and species groups.
			<br />
			<br />
			If you find a major error in the habitat lengths associated with barriers in this tool, please
			<a href={`mailto:${CONTACT_EMAIL}`} target="_blank" class="text-destructive">contact us</a>.
		</p>
	</Alert>

	<div class="mt-8">
		<h2>Table of contents:</h2>
		<ul class="mt-2">
			<li>
				<a href="#StreamNet"> Pacific Northwest Anadromous and Resident Fish Species Habitat </a>
			</li>
			<li>
				<a href="#CABaseline">California Baseline Fish Habitat</a>
			</li>
			<li>
				<a href="#EasternBrookTrout">Eastern Brook Trout Habitat</a>
			</li>
			<li>
				<a href="#Northeast"> Chesapeake Bay Watershed Diadromous Fish Habitat </a>
			</li>
			<li>
				<a href="#SARP">Southeast Diadromous Fish Habitat</a>
			</li>
			<li>
				<a href="#ApacheTrout">Apache & Gila Trout</a>
			</li>
			<li>
				<a href="#InteriorCutthroatTrout">
					Colorado River, Greenback, Lahontan, and Rio Grande cutthroat trout
				</a>
			</li>
			<li>
				<a href="#CoastalCutthroatTrout"> Coastal Cutthroat Trout (California) </a>
			</li>
		</ul>
	</div>

	<hr class="divider" />

	<div id="StreamNet">
		<h2>Pacific Northwest Anadromous and Resident Fish Species Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-4">
			<p>
				Known current (not potential) instream habitat data for key anadromous and resident fish
				species in Washington, Oregon, Idaho, and Montana were derived from
				<a
					href="https://www.streamnet.org/home/data-maps/gis-data-sets/"
					target="_blank"
					rel="external"
				>
					StreamNet
				</a>
				(January 2019 version). These habitat data are compiled by StreamNet from partners within the
				region and are attributed to stream segments within a common regional mixed-scale hydrography
				dataset, and may include segments that are used for one or more life stages such as spawning or
				migration.
			</p>

			<figure>
				<enhanced:img
					src="$lib/assets/images/52633917843_8c189a8ea2_c.jpg"
					alt="Salmon at Wildwood Recreation Site"
				/>
				<figcaption>
					Salmon. Photo:
					<a
						href="https://www.flickr.com/photos/blmoregon/52633917843/in/album-72177720303743258/"
						target="_blank"
						rel="external"
					>
						Bureau of Land Management Oregon & Washington
					</a>.
				</figcaption>
			</figure>
		</div>

		<div class="font-bold mt-8">Species included:</div>
		<div class="grid sm:grid-cols-3 gap-2 sm:gap-4 mt-2">
			<ul>
				<li>Bonneville cutthroat trout</li>
				<li>Bull trout</li>
				<li>Chinook salmon</li>
				<li>Chum salmon</li>
				<li>Coastal cutthroat trout</li>
				<li>Coho salmon</li>
			</ul>
			<ul>
				<li>
					Green sturgeon<sup>*</sup>
				</li>
				<li>Kokanee</li>
				<li>
					Pacific lamprey<sup>*</sup>
				</li>
				<li>Pink salmon</li>
				<li>Rainbow trout</li>
				<li>Redband trout</li>
			</ul>
			<ul>
				<li>Sockeye salmon</li>
				<li>Steelhead</li>
				<li>Westslope cutthroat trout</li>
				<li>White sturgeon</li>
				<li>Yellowstone cutthroat trout</li>
			</ul>
		</div>
		<p class="text-sm text-muted-foreground mt-2">
			<sup>*</sup> only available for subset of range.
		</p>

		<p class="mt-8 font-bold">
			We used the following steps to attribute StreamNet species habitat data for each species to
			NHDPlusHR flowlines:
		</p>

		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>
				Merged linework to aggregate all life stages into a single set of linework and then split
				back into individual segments.
			</li>
			<li>
				Identified and filled gaps (&lt;5 meters) between the endpoints of nearby lines; these were
				most likely the result of processing errors and different vintages of underlying hydrography
				used in the StreamNet data.
			</li>
			<li>
				Identified related groups of habitat lines that were within 1 kilometer of each other; these
				groups are used to determine when to fill gaps in the species habitat linework.
			</li>
			<li>Dropped any line segments &lt; 1 meter in length.</li>
			<li>
				Dropped any line segments well outside species range; these were most likely the result of
				processing or attribution errors.
			</li>
			<li>
				Selected NHDPlusHR flowlines that intersect a 50 meter buffer around habitat linework for
				further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches, network
				loops, or occurred between distinct groups of species habitat. The remaining flowlines are
				retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 50 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 65% of its length is within the buffer, it overlaps
				by at least 10 meters, and the total amount of overlap is less than 500 meters different
				from its total length. Any fragments that have high overlap with the buffer but are less
				than 150 meters in length were dropped unless they are headwaters or connect to upstream
				segments already marked as habitat.
			</li>
			<li>
				The outputs of steps 8 and 9 are used to define anchor points in a network analysis to fill
				gaps between segments identified as habitat. We created a linear directed graph facing
				downstream using the NHDPlusHR network toplogy (excluding any network loops) and traversed
				this graph from the anchor points to upstream points of disconnected habitat linework (gaps
				must be less than 100 flowlines long). We selected flowlines identified from traversing
				these networks to fill gaps if they did not bridge distinct habitat groups and had at least
				50% overlap with a 100 meter buffer around the habitat linework.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence. For most species, the
				overall linework was similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-muted-foreground text-sm">
			Note: the habitat data included used within this tool is a best first approximation of the
			StreamNet data, attributed at the entire NHDPlusHR flowline level; it does not include
			elevation gradients or other natural barriers that may have been included within the original
			data.
		</p>
	</div>

	<hr class="divider" />

	<div id="CABaseline">
		<h2>California Baseline Fish Habitat</h2>

		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-4">
			<p>
				Known current and potential instream habitat data for key anadromous species and resident
				resident rainbow trout (Southern California) were derived from the
				<a
					href="https://psmfc.maps.arcgis.com/home/item.html?id=a8117ce44a16493ca2aa0571769e5654"
					target="_blank"
					rel="external"
				>
					California Baseline Fish Habitat
				</a>
				dataset (version 3) provided by the
				<a href="https://www.cafishpassageforum.org/" target="_blank" rel="external">
					California Fish Passage Forum
				</a>. This dataset attributed habitat data to the NHDPlus v2.1 medium-resolution
				hydrography, and aggregates all included species together into a single habitat dataset.
				This dataset is focused on estimating habitat for anadromous species and thus does not
				include full coverage of resident species across California.
			</p>

			<figure>
				<enhanced:img
					src="$lib/assets/images/52706030122_dc2b358ec0_c.jpg"
					alt="Coho salmon spawning in the Salmon River, 2015"
				/>
				<figcaption>
					Coho salmon. Photo:
					<a
						href="https://www.flickr.com/photos/usfws_pacificsw/52706030122/in/album-72177720301505972/"
						target="_blank"
						rel="external"
					>
						U.S. Fish and Wildlife Service Pacific Southwest Region
					</a>.
				</figcaption>
			</figure>
		</div>

		<p class="mt-8 font-bold">
			We used the following steps to attribute the California Baseline Fish Habitat data to
			NHDPlusHR flowlines:
		</p>

		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>Merged line segments by ReachCode.</li>
			<li>
				Selected NHDPlusHR flowlines that have the same ReachCode as the habitat linework and
				overlapped the corresponding reaches in the habitat linework by at least 75% of their length
				and where their endpoints were within 1 kilometer of the nearest point in the habitat
				linework, and marked these as habitat. This was done to prevent including flowlines that had
				corresponding ReachCode values but represented grossly different actual stream reaches.
			</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 50 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches, network
				loops, or occurred between distinct groups of species habitat. The remaining flowlines are
				retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 50 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 65% of its length is within the buffer, it overlaps
				by at least 10 meters, and the total amount of overlap is less than 500 meters different
				from its total length. Any fragments that have high overlap with the buffer but are less
				than 150 meters in length were dropped unless they are headwaters or connect to upstream
				segments already marked as habitat.
			</li>
			<li>
				The outputs of steps 1, 4, and 5 are used to define anchor points in a network analysis to
				fill gaps between segments identified as habitat. We created a linear directed graph facing
				downstream using the NHDPlusHR network toplogy (excluding any network loops and canals /
				ditches) and traversed this graph from the anchor points to upstream points of disconnected
				habitat linework (gaps must be less than 100 flowlines long). We selected flowlines
				identified from traversing these networks to fill gaps if they did not bridge distinct
				habitat groups and had at least 50% overlap with a 200 meter buffer around the habitat
				linework. (the larger tolerance was required due to the low resolution of NHDPlus in some
				areas)
			</li>
			<li>
				We then filled gaps between habitat segments identified above and the ocean, if the total
				gap was less than 10 kilometers.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-sm text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of the
			California Baseline Fish Habitat dataset, attributed at the entire NHDPlusHR flowline level;
			it does not include elevation gradients or other natural barriers that may have been included
			within the California Baseline Fish Habitat dataset.
		</p>
	</div>

	<hr class="divider" />

	<div id="EasternBrookTrout">
		<h2>Eastern Brook Trout Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-4">
			<p>
				Eastern brook trout habitat data were derived from nonpublic data provided by Trout
				Unlimited. These data are based on NHDPlus medium-resolution flowlines that intersect with
				brook trout population patches, which were compiled from assessments by Trout Unlimited
				(2017-2022). These data are intended to provide a best guess estimate of brook trout
				instream habitat based on available data.
			</p>
			<figure>
				<enhanced:img
					src="$lib/assets/images/4752172480_74c20f37af_c.jpg"
					alt="Eastern Brook Trout"
				/>
				<figcaption>
					Eastern Brook Trout. Photo:
					<a
						href="https://www.flickr.com/photos/usfwsnortheast/4752172480/in/gallery-144603962@N07-72157719171281455/"
						target="_blank"
						rel="external"
					>
						U.S. Fish and Wildlife Service Northeast Region
					</a>.
				</figcaption>
			</figure>
		</div>

		<p class="mt-8 font-bold">
			We used the following steps to attribute the eastern brook trout habitat data to NHDPlusHR
			flowlines:
		</p>

		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>Merged line segments by ReachCode.</li>
			<li>
				Selected NHDPlusHR flowlines that have the same ReachCode as the habitat linework and
				overlapped the corresponding reaches in the habitat linework by at least 75% of their length
				and where their endpoints were within 2 kilometer of the nearest point in the habitat
				linework, and marked these as habitat. This was done to prevent including flowlines that had
				corresponding ReachCode values but represented grossly different actual stream reaches.
			</li>
			<li>
				Discarded any of the above flowlines that are coded by NHDPlusHR as intermittent and where
				either endpoint is greater than 250 meters from the nearest point on the habitat linework.
			</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 100 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches, network
				loops, or occurred between distinct groups of species habitat. The remaining flowlines are
				retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 100 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 65% of its length is within the buffer, it overlaps
				by at least 10 meters, and the total amount of overlap is less than 1 kilometer different
				from its total length. Any flowlines where either endpoint is greater than 2 kilometers from
				the nearest point on the habitat line work or any intermittent segments where the distance
				from either endpoint to the nearest point on the habitat linework is greater than 250 meters
				are discarded. Any fragments that have high overlap with the buffer but are less than 300
				meters in length were dropped unless they are headwaters or connect to upstream segments
				already marked as habitat.
			</li>
			<li>
				The outputs of steps 1, 6, and 7 are used to define anchor points in a network analysis to
				fill gaps between segments identified as habitat. We created a linear directed graph facing
				downstream using the NHDPlusHR network toplogy (excluding any network loops and canals /
				ditches) and traversed this graph from the anchor points to upstream points of disconnected
				habitat linework (gaps must be less than 100 flowlines long). We selected flowlines
				identified from traversing these networks to fill gaps if they did not bridge distinct
				habitat groups and had at least 50% overlap with a 300 meter buffer around the habitat
				linework. (the larger tolerance was required due to the low resolution of NHDPlus in some
				areas)
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="text-sm mt-8 text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of the
			eastern brook trout habitat data, attributed at the entire NHDPlusHR flowline level; it does
			not include elevation gradients or other natural barriers that may have been included within
			the original data.
		</p>
	</div>

	<hr class="divider" />

	<div id="Northeast">
		<h2>Chesapeake Bay Watershed Diadromous Fish Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-4">
			<div>
				<p>
					Habitat for several diadromous species in the Chesapeake Bay Watershed were derived from
					data provided by the Chesapeake Fish Passage Workgroup. These data were attributed to
					either NHDPlus medium-resolution flowlines or NHDPlusHR flowlines.
					<br />
					<br />
					<b>Species included:</b>
				</p>
				<div class="grid sm:grid-cols-3 gap-2 sm:gap-4 mt-2">
					<ul>
						<li>Alewife</li>
						<li>American eel</li>
						<li>American shad</li>
					</ul>
					<ul>
						<li>Atlantic sturgeon</li>
						<li>Blueback herring</li>
						<li>Brook trout</li>
					</ul>
					<ul>
						<li>Hickory shad</li>
						<li>Shortnose sturgeon</li>
						<li>Striped bass</li>
					</ul>
				</div>
			</div>
			<figure>
				<enhanced:img
					src="$lib/assets/images/8574372559_f05ce9e42a_c.jpg"
					alt="Eastern Brook Trout"
				/>
				<figcaption>
					Eastern Brook Trout. Photo:
					<a
						href="https://www.flickr.com/photos/usfwsnortheast/8574372559/in/gallery-144603962@N07-72157719171281455/"
						target="_blank"
						rel="external"
					>
						U.S. Fish and Wildlife Service Northeast Region
					</a>.
				</figcaption>
			</figure>
		</div>
		<p class="mt-8 font-bold">
			We used the following steps to attribute the Chesapeake Bay Watershed diadromous fish habitat
			data for each species to NHDPlusHR flowlines:
		</p>
		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>Merged line segments by ReachCode.</li>
			<li>
				Selected NHDPlusHR flowlines that have the same ReachCode as the habitat linework and
				overlapped the corresponding reaches in the habitat linework by at least 75% of their length
				and where their endpoints were within 2 kilometer of the nearest point in the habitat
				linework, and marked these as habitat. This was done to prevent including flowlines that had
				corresponding ReachCode values but represented grossly different actual stream reaches.
			</li>
			<li>
				Discarded any of the above flowlines that are coded by NHDPlusHR as intermittent and where
				either endpoint is greater than 500 meters from the nearest point on the habitat linework.
			</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 50 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches, network
				loops, or occurred between distinct groups of species habitat. The remaining flowlines are
				retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 50 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 65% of its length is within the buffer, it overlaps
				by at least 10 meters, and the total amount of overlap is less than 1 kilometer different
				from its total length. Any flowlines where either endpoint is greater than 2 kilometers from
				the nearest point on the habitat line work are discarded. Any fragments that have high
				overlap with the buffer but are less than 150 meters in length were dropped unless they are
				headwaters or connect to upstream segments already marked as habitat.
			</li>
			<li>
				The outputs of steps 1, 6, and 7 are used to define anchor points in a network analysis to
				fill gaps between segments identified as habitat. We created a linear directed graph facing
				downstream using the NHDPlusHR network toplogy (excluding any network loops and canals /
				ditches) and traversed this graph from the anchor points to upstream points of disconnected
				habitat linework (gaps must be less than 100 flowlines long). We selected flowlines
				identified from traversing these networks to fill gaps if they did not bridge distinct
				habitat groups and had at least 10% overlap with a 200 meter buffer around the habitat
				linework.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-muted-foreground text-sm">
			Note: the habitat data included used within this tool is a best first approximation of the
			Chesapeake Bay Watershed diadromous habitat data, attributed at the entire NHDPlusHR flowline
			level; it does not include elevation gradients or other natural barriers that may have been
			included within the original habitat data.
		</p>
	</div>

	<hr class="divider" />

	<div id="SARP">
		<h2>Southeast Diadromous Fish Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-4">
			<p>
				Diadromous fish habitat for the Southeast region was derived from data developed by the
				Southeast Aquatic Resources partnership. These data are based on an analysis of NHDPlus High
				Resolution flowlines in networks that flow into marine areas and have no dams downstream.
				SARP&apos;s methods included an analysis of element occurrence data for key diadromous
				species in the Southeast along with rules to determine possible habitat based on stream
				order.
				<br />
				<br />
				NOTE: this is an early draft of this habitat dataset, which is currently undergoing review by
				stakeholders and expected to be improved in subsequent versions.
			</p>

			<figure>
				<enhanced:img src="$lib/assets/images/6359207695_1d41348492_c.jpg" alt="Gulf sturgeon" />
				<figcaption>
					Gulf Sturgeon. Photo:
					<a
						href="https://www.flickr.com/photos/usfwsendsp/6359207695/in/album-72157625204217622/"
						target="_blank"
						rel="external"
					>
						Kayla Kimmel, U.S. Fish and Wildlife Service
					</a>
				</figcaption>
			</figure>
		</div>

		<p class="mt-12 font-bold">
			We used the following steps to attribute the Southeast diadromous fish habitat data to
			NHDPlusHR flowlines:
		</p>
		<ol class="mt-2">
			<li>
				Because these data were derived from networks based on NHDPlus High Resolution flowlines
				developed elsewhere in this tool, all network segments included NHDPlusID identifiers. We
				simply joined the diadromous habitat back to full flowlines based on NHDPlusID.
				<br />
				<br />
				However, where the upper end of habitat was based on the most-downstream dam on a given network,
				attributing at the flowline caused the habitat to extend a short distance upstream of the dam
				to the upper end of the flowline. This is a known issue with the methods here that attribute to
				the entire flowline level.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-sm text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of the
			Southeast diadromous fish habitat data, attributed at the entire NHDPlusHR flowline level; it
			does not include elevation gradients or other natural barriers that may have been included
			within the original data.
		</p>
	</div>

	<hr class="divider" />

	<div id="ApacheTrout">
		<h2>Apache & Gila Trout Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-2">
			<p>
				Apache trout habitat data were derived from data provided by Dan Dauwalter (Trout Unlimited)
				and Zachary Jackson (U.S. Fish and Wildlife Service).
				<br />
				<br />
				Gila trout habitat data were derived from data provided by Dan Dauwalter (Trout Unlimited).
			</p>

			<figure>
				<enhanced:img src="$lib/assets/images/usfws-apache-trout.jpg" alt="Apache Trout" />
				<figcaption>
					Apache Trout. Photo:
					<a href="https://www.fws.gov/media/apache-trout" target="_blank" rel="external">
						U.S. Fish and Wildlife Service
					</a>.
				</figcaption>
			</figure>
		</div>

		<p class="mt-8 font-bold">
			We used the following steps to attribute the Apache and Gila trout habitat data to NHDPlusHR
			flowlines:
		</p>
		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 50 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches or network
				loops. The remaining flowlines are retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 50 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 50% of its length is within the buffer and the
				total amount of overlap is less than 1 kilometer different from its total length, or if its
				upstream endpoint is within 1 meter of the habitat linework and has at least 25% overlap.
				Any Any fragments that have high overlap with the buffer but are less than 150 meters in
				length were dropped unless they are headwaters or connect to upstream segments already
				marked as habitat.
			</li>
			<li>
				We manually selected NHD flowlines that were not otherwise selected above if they had a
				suitable amount of visual overlap and landscape position suggested that habitat could be
				extended to their entire lengths.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-sm text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of the
			Apache and Gila trout habitat data, attributed at the entire NHDPlusHR flowline level; it does
			not include elevation gradients or other natural barriers that may have been included within
			the original data.
		</p>
	</div>

	<hr class="divider" />

	<div id="InteriorCutthroatTrout">
		<h2>Colorado River, Greenback, Lahontan, and Rio Grande Cutthroat Trout Habitat</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-2">
			<p>
				Colorado River cutthroat trout habitat data were derived from data provided by the Colorado
				Cutthroat Trout Working Group.
				<br />
				<br />
				Greenback cutthroat habitat data were derived from data provided by the Greenback Cutthroat Recovery
				Team.
				<br />
				<br />
				Lahontan cutthroat trout habitat data were derived from data provided by Trout Unlimited. Data
				appear to have been developed based on an older version of NHDPlus High Resolution and were very
				close to the latest available NHDPlus High Resolution flowlines.
				<br />
				<br />
				Rio Grande cutthroat habitat data were derived from data provided by the Rio Grande Cutthroat
				Working Group.
			</p>

			<figure>
				<enhanced:img
					src="$lib/assets/images/usfws-lahontan-cutthroat-trout.jpg"
					alt="Lahontan Cutthroat Trout"
				/>
				<figcaption>
					Lahontan Cutthroat Trout. Photo:
					<a
						href="https://www.fws.gov/media/lahontan-cutthroat-trout-7"
						target="_blank"
						rel="external"
					>
						Chad Mellison, U.S. Fish and Wildlife Service
					</a>.
				</figcaption>
			</figure>
		</div>
		<p class="mt-8 font-bold">
			We used the following steps to attribute the cutthroat trout habitat data to NHDPlusHR
			flowlines:
		</p>
		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 10 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches or network
				loops. The remaining flowlines are retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 50 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 50% of its length is within the buffer and the
				total amount of overlap is less than 1 kilometer different from its total length, or if its
				upstream endpoint is within 1 meter of the habitat linework and has at least 25% overlap.
				Any Any fragments that have high overlap with the buffer but are less than 150 meters in
				length were dropped unless they are headwaters or connect to upstream segments already
				marked as habitat.
			</li>
			<li>
				We manually selected NHD flowlines that were not otherwise selected above if they had a
				suitable amount of visual overlap and landscape position suggested that habitat could be
				extended to their entire lengths. We manually deselected NHD flowlines that were erroneously
				marked as habitat above due to spatial proximity; these include canals / ditches that
				closely parallel waterways with habitat.
			</li>
			<li>
				We extracted any flowlines that had significant overlap with Colorado River cutthroat trout
				waterbodies identified as current populations (excluded waterbodies specifically marked as
				recreational populations or populations no longer present).
			</li>
			<li>
				We extracted any flowlines that had significant overlap with Greenback cutthroat trout
				waterbodies.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-sm text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of these
			cutthroat trout habitat data, attributed at the entire NHDPlusHR flowline level; it does not
			include elevation gradients or other natural barriers that may have been included within the
			original data.
		</p>
	</div>

	<hr class="divider" />

	<div id="CoastalCutthroatTrout">
		<h2>Coastal Cutthroat Trout Habitat (California)</h2>
		<div class="grid sm:grid-cols-[2fr_1fr] mt-2 gap-8">
			<p>
				Coastal cutthroat trout habitat data in California were derived from habitat linework
				provided by the Pacific States Marine Fisheries Commission. Because coastal cutthroat trout
				habitat data are already prepared for Oregon and Washington using StreamNet data (above),
				this additional data was limited to California.
			</p>

			<figure>
				<enhanced:img
					src="$lib/assets/images/usfws-releasing-cutthroat.jpg"
					alt="Cutthroat Trout"
				/>
				<figcaption>
					Cutthroat Trout. Photo:
					<a href="https://www.fws.gov/media/releasing-cutthroat" target="_blank" rel="external">
						U.S. Fish and Wildlife Service
					</a>.
				</figcaption>
			</figure>
		</div>

		<p class="mt-8 font-bold">
			We used the following steps to attribute the coastal cutthroat trout habitat data to NHDPlusHR
			flowlines:
		</p>
		<ol class="mt-2">
			<li>Reprojected to the USGS CONUS Albers projection.</li>
			<li>Selected habitat linework within NHD region 18.</li>
			<li>
				Selected NHDPlusHR flowlines that intersected a 100 meter buffer around the habitat linework
				for further processing below.
			</li>
			<li>
				Selected any flowlines where both the upstream and downstream endpoints fall within 1 meter
				of habitat linework and marked them as habitat if they were not canals / ditches or network
				loops. The remaining flowlines are retained for further processing below.
			</li>
			<li>
				Calculated the amount of overlap with the 100 meter buffer around habitat linework, and
				marked a flowline as habitat if at least 65% of its length is within the buffer and the
				total amount of overlap is less than 1 kilometer different from its total length. Any Any
				fragments that have high overlap with the buffer but are less than 300 meters in length were
				dropped unless they are headwaters or connect to upstream segments already marked as
				habitat.
			</li>
			<li>
				The outputs of steps 4 and 5 are used to define anchor points in a network analysis to fill
				gaps between segments identified as habitat. We created a linear directed graph facing
				downstream using the NHDPlusHR network toplogy (excluding any network loops and canals /
				ditches) and traversed this graph from the anchor points to upstream points of disconnected
				habitat linework (gaps must be less than 100 flowlines long). We selected flowlines
				identified from traversing these networks to fill gaps if they did not bridge distinct
				habitat groups and had at least 10% overlap with a 200 meter buffer around the habitat
				linework.
			</li>
			<li>
				We visually and quantitatively compared the extracted NHDPlusHR flowlines tagged as habitat
				to the original data to ensure reasonable spatial correspondence; the overall linework was
				similar and had roughly similar lengths.
			</li>
		</ol>

		<p class="mt-8 text-sm text-muted-foreground">
			Note: the habitat data included used within this tool is a best first approximation of the
			coastal cutthroat trout habitat data, attributed at the entire NHDPlusHR flowline level; it
			does not include elevation gradients or other natural barriers that may have been included
			within the original data.
		</p>
	</div>
</div>
