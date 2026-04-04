<script lang="ts">
	import { resolve } from '$app/paths'
	import { HeaderImage } from '$lib/components/image'
	import { CONTACT_EMAIL, SITE_NAME, NACC_HOME_URL } from '$lib/env'
</script>

<svelte:head>
	<title>Barrier Inventory Methods | {SITE_NAME}</title>
</svelte:head>

<HeaderImage author="Zach Dutra" url="https://unsplash.com/photos/2d7Y5Yi3aq8">
	<enhanced:img src="$lib/assets/images/zack-dutra-2d7Y5Yi3aq8-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Barrier inventory methods</h1>
	<p class="mt-8">
		Over the last decade, the <a
			href="https://southeastaquatics.net/"
			target="_blank"
			rel="external">Southeast Aquatic Resources Partnership</a
		>
		(SARP), a part of the
		<a href="https://fishhabitat.org/" target="_blank" rel="external">
			National Fish Habitat Partnership</a
		>
		(NFHP), has been working to map and prioritize aquatic organism passage barriers (dams, assessed road
		stream crossings, and waterfalls) across the United States.
		<br /><br />
		This effort is now called the

		<a href="https://aquaticbarriers.org" target="_blank" rel="external">
			National Aquatic Connectivity Collaborative
		</a>
		(NACC), under the NFHP umbrella, and has been funded by a variety of partners including federal and
		state agencies and NGOs. Within this collaborative, partners can use the
		<b>National Aquatic Barrier Inventory & Prioritization Tool</b> to collect barrier data, extract data,
		and prioritize barrier data to create lists of high-priority projects based on criteria important
		to their particular organization or agency.
	</p>
	<h2 class="mt-8">The Inventory</h2>
	<p class="mt-2">
		The NACC inventory tracks three types of barriers: dams, road/stream crossings, and waterfalls.
		These three barrier types are compiled into one inventory using a customized approach that
		combines multiple inventories that are updated frequently from original sources. This inventory
		is a growing and living database of dams, culverts, and other road crossings that spans all 50
		states, Puerto Rico, and the US Virgin Islands, compiled by SARP with the generous support from
		many partners and funders. It integrates existing datasets from local, state, and federal
		partners with data collected from ongoing field surveys and local knowledge of specific
		structures.
		<br /><br />
		This inventory framework can be visualized as an umbrella of over 6.5 million points (all structure
		types including dams, assessed and unassessed road/stream crossings, and waterfalls), made up of:
	</p>
	<ul class="text-lg [&>li+li]:mt-0">
		<li>static and living sources of data from other entities</li>
		<li>field collected data managed by NACC</li>
		<li>estimated structure presence and barrier severity using modeling and other methods</li>
	</ul>
	<h4 class="mt-8">Compiling data from static and living data sources</h4>
	<p>
		To combine living sources of data, we begin with base national or regional datasets such as the
		<a
			href="https://nid.sec.usace.army.mil/nid/#/what-is-nid/closer-look"
			target="_blank"
			rel="external">National Inventory of Dams</a
		>,
		<a
			href="https://www.usgs.gov/data/database-stream-crossings-united-states"
			target="_blank"
			rel="external">USGS road/steam crossings data</a
		>, TNC freshwater network data, followed by data gathered from statewide and local sources such
		as state dam safety programs, water resources divisions, individual basin groups, and academic
		research projects. A list of data sources can be found
		<a
			href="https://docs.google.com/document/d/1mUwk9rHukmY1D_NInxjdIxbBVfILD1Y8Xr-lMqjV4xU/edit?usp=sharing"
			target="_blank"
			rel="external">here</a
		>. All data sources, when compiled and merged into the NACC database, are linked to the main
		input database by SARPID.
	</p>
	<h4 class="mt-8">Collecting NACC field data</h4>
	<p>
		The NACC also utilizes standardized field protocols to fill data gaps, identifying unregulated
		dams, assessed road/stream crossings, and waterfalls with help from a network of partners. The
		road crossing protocol used by the NACC was developed by the North Atlantic Aquatic Connectivity
		Collaborative, and scores crossings based on the degree of which they deviate from an ideal
		crossing (which would span full channel and banks and mimic a natural stream within). To learn
		more, view the road stream crossing <a
			href={`${NACC_HOME_URL}/survey-forms/`}
			target="_blank"
			rel="external">manuals and forms</a
		>. To participate in road/stream crossing training, partners need to be trained on the method
		within our training portal and in the field. We are currently merging into a national program.
		Soon, training materials will be accessible.
		<br /><br />
		To learn more about training opportunities, please
		<a href={`mailto:${CONTACT_EMAIL}`} target="_blank" rel="external">contact us</a>.
	</p>
	<h4 class="mt-8">Modeling barrier presence and severity</h4>
	<p>
		Finally, NACC uses new technology to model the presence of barriers with three different
		methods:
	</p>
	<ul class="text-lg [&>li+li]:mt-0">
		<li>
			estimated dams analysis using a combination of water body datasets including the National
			Hydrography Dataset, Open Street Maps, and the National Wetlands Inventory (view more in depth
			methods <a href={resolve('/methods/estimated-dams/', {})}>here</a>)
		</li>
		<li>
			manual validation of points of diversion from the Western States Water Council –
			<a href="https://westdaat.westernstateswater.org/" target="_blank" rel="external">
				Water Data Exchange (WADE) dataset</a
			>
		</li>
		<li>tracing streams derived from LiDAR, evaluating drops in elevation</li>
	</ul>
	<p class="mt-4">The outputs of these methods must be QAQC’d, and are currently in progress.</p>

	<h2 class="mt-12">Compiling all barriers into the Inventory</h2>
	<p class="mt-2">
		When barriers are merged into the master NACC Inventory, three processes must be completed:
	</p>
	<ol class="mt-4">
		<li>
			<b>Duplicate removal and attribute field mapping:</b> once new datasets are acquired, they are
			compared to their latest versions if they are from a living datasource, such as the California
			Passage Assessment Database. Additions, re-surveys, attribute changes, movements, and
			deletions are identified. The master datasets are updated with the latest version of the
			source data, and every source dataset is stored by date, and given the SARPID of which it
			corresponds so it can be queried by request. If you would like to receive the source dataset
			complete with SARPID to join to tool outputs,
			<a href={`mailto:${CONTACT_EMAIL}`} target="_blank" rel="external">contact us</a>.
		</li>
		<li>
			<b>Connectivity analysis:</b> this occurs by exporting the master inventories monthly, and
			performing several analyses to remove duplicates identified by staff and volunteers, and using
			code to snap the points to the NHDplus hydrography. More technical information on this process
			can be found in the NACC's
			<a
				href="https://github.com/astutespruce/sarp-connectivity/tree/main/analysis/prep/barriers"
				target="_blank"
				rel="external">Github page</a
			>.
		</li>
		<li>
			<b
				>Indicators calculated and datasets uploaded to the National Aquatic Barrier Inventory &
				Prioritization Tool:</b
			>
			Once the connectivity analysis happens, attributes can be attributed to the networks of each barrier
			and therefore attributed to barriers. These indicators are used to prioritize and also for download
			and additional analysis by the user. For more information on these processes, check
			<b>Learn more</b>
			in the top right corner of this page.

			<br /><br />
			The National Aquatic Barrier Inventory & Prioritization Tool is updated monthly with new connectivity
			analyses based on additional data sources acquired and error handling. Most living data sources
			are updated 2-4 times per year, usually around January 1st and August 30.
		</li>
	</ol>
</div>
