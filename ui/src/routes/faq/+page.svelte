<script lang="ts">
	import FAQIcon from '@lucide/svelte/icons/circle-question-mark'

	import { resolve } from '$app/paths'
	import { CONTACT_EMAIL, NACC_HOME_URL, SITE_NAME, SITE_URL } from '$lib/env'
	import { MAP_SERVICES, dataDate, dataVersion } from '$lib/config/constants'
	import { HeaderImage } from '$lib/components/image'
</script>

<svelte:head>
	<title>FAQ | {SITE_NAME}</title>
</svelte:head>

<HeaderImage author="Kazuend" url="https://unsplash.com/photos/cCthPLHmrzI">
	<enhanced:img src="$lib/assets/images/kazuend-cCthPLHmrzI-unsplash.jpg" alt="" />
</HeaderImage>

<div class=" page-content">
	<h1 class="page-header">
		<FAQIcon class="size-14 text-grey-8" />

		Frequently Asked Questions
	</h1>

	<p class="mt-12 text-xl">
		Please also see the
		<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">FAQ page</a> for the National Aquatic
		Connectivity Collaborative (NACC) for general FAQs about the overall effort, data sources, and the
		inventory.
	</p>
	<hr />

	<div class="mt-8 [&_h2]:text-2xl sm:[&_h2]:text-3xl [&_h2]:mb-2">
		<div>
			<h2>What is the purpose of this Inventory and Prioritization Tool?</h2>
			<p>
				The objective of this inventory and tool is to build a community of practice among resource
				managers and enable them to identify high priority aquatic connectivity restoration
				projects. Regularly updating barriers in this inventory allows it to better reflect the
				degree of aquatic habitat fragmentation from aquatic barriers across political boundaries at
				a national scale. We provide a collaborative atmosphere where all resource managers can
				contribute to the collective effort of restoring rivers and streams through aquatic barrier
				removal.
				<br />
				<br />
				You can help improve the inventory by sharing data, assisting with field reconnaissance to evaluate
				the impact of aquatic barriers, joining a Aquatic Connectivity Team, or even by reporting issues
				with the inventory data in this tool.
				<br />
				<br />
				<a href={`mailto:${CONTACT_EMAIL}`} target="_blank">Contact us</a> to learn more about how you
				can help improve this barrier inventory and tool.
			</p>
		</div>

		<hr />

		<div>
			<h2>What can the Inventory and Prioritization Tool do?</h2>
			<p>
				The prioritization tool allows users to
				<a href={resolve('/explore/', {})}>explore and download barrier</a> inventory information at
				different scales. It also allows users to
				<a href={resolve('/priority/', {})}>prioritize</a> barriers at different scales using
				different filtering approaches and different prioritization scenarios. It is also possible
				to
				<a href={resolve('/restoration/', {})}>summarize accomplishments</a> over multiple years, such
				as miles restored through barrier removal by year.
			</p>
		</div>

		<hr />

		<div>
			<h2>How are barriers prioritized within the Tool?</h2>
			<p>
				Within the tool, a user can prioritize dams, surveyed road/stream crossings, or both barrier
				types together. Waterfalls are included within network analysis as well, but are not
				prioritized. A priority barrier to remove would be one that reconnects high quality habitat.
				<br />
				<br />
				For this reason, we calculate and use four metrics for each barrier:
			</p>

			<ul class="mt-2">
				<li>Miles restored by the potential removal of the structure</li>
				<li>
					Percent natural land cover within the floodplain of the structure&apos;s upstream network
				</li>
				<li>The percent of the upstream network that is altered by canals and ditching</li>
				<li>The complexity of the upstream network (number of stream size classes)</li>
			</ul>

			<p>
				<br />
				These four metrics can be combined into three scenarios:
			</p>
			<ul class="mt-2">
				<li>network length</li>
				<li>watershed condition</li>
				<li>combined network lenght and watershed condition</li>
			</ul>

			<p>
				<br />
				Within the prioritization tool, users can identify a targeted set of filters to prioritize based
				on a wide range of available filters. These filters include the number of threatened and endangered
				species in a HUC12, landowner type, environmental justice, number of barriers downstream to the
				ocean, and more. Once an output is generated, users can toggle between priorities for the area
				of interest and also explore results for perennial reaches only or all (perennial vs ephemeral/intermittent)
				reaches.
				<br />
				<br />
				Planned future enhancements include the ability to prioritize barriers for larger species vs smaller
				ones.
				<br />
				<br />
				More information about how barriers are prioritized can be found
				<a href={resolve('/methods/scoring/', {})}>here</a>.
			</p>
		</div>

		<hr />

		<div>
			<h2>How does the Prioritization Tool deal with "beneficial barriers"?</h2>
			<p>
				To incorporate local relevance into the inventory such as the presence of beneficial
				barriers which prevent the migration of invasive species, SARP works to code barriers within
				a Social Feasibility field. Barriers that may be invasive barriers are marked as such, and
				therefore not available for prioritization in the tool. However, this data is lacking, and
				unless this information is available within an existing inventory, we rely on our partners
				to tell us where these invasive barriers are located.
				<br />
				<br />
				To report an invasive species barrier miscoded within the inventory, as with missing barriers,
				please contact
				<a href={`mailto:${CONTACT_EMAIL}`} target="_blank">
					{CONTACT_EMAIL}
				</a>
				with the coordinates, or when prioritizing within the tool, scroll to the bottom of the sidebar
				for the barrier in question and click
				<b>Report a problem with this barrier</b>.
			</p>
		</div>

		<hr />

		<div>
			<h2>How can I download barriers for a specific area?</h2>
			<p>
				Use the
				<a href={resolve('/explore', {})}>
					<b>Explore & Download</b>
				</a>
				page to select one or more states, counties, or hydrologic units for your area of interest. You
				can then download all dams, surveyed road/stream crossings, or both types for that area.
			</p>
		</div>

		<hr />

		<div>
			<h2>How can I download all available barriers?</h2>
			<p>
				Use the download button on the bottom left of the
				<a href={resolve('/explore/', {})}>
					<b>Explore & Download</b>
				</a>
				page or the
				<a href={resolve('/restoration/', {})}>
					<b>Restoration</b>
				</a>
				page to download all available dams and / or surveyed road/stream crossings.
			</p>
		</div>

		<hr />

		<div>
			<h2>How do I cite the inventory?</h2>
			<p>
				When downloading the data, you can find the citation within the Terms of Use text file.
				Alternatively, if citing the inventory in general, you may use the following citation:
			</p>
			<blockquote class="mt-4 ml-8">
				National Aquatic Connectivity Collaborative (NACC). {dataDate.split('/')[2]}. National
				Aquatic Barrier Inventory v{dataVersion} ({dataDate}). Compiled by the
				<a
					href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
					target="_blank"
					rel="external">Southeast Aquatic Resources Partnership</a
				>
				(SARP) and the
				<a href="https://www.fishhabitat.org/" target="_blank" rel="external"
					>National Fish Habitat Partnership</a
				>
				(NFHP). [Downloaded {new Date().toLocaleDateString()}
				from
				<a href={SITE_URL} target="_blank" rel="external">
					{SITE_URL}
				</a>].
			</blockquote>
		</div>

		<hr />

		<div>
			<h2>How can I access map services to display barriers in a GIS application?</h2>
			<p>
				If you would like to access map services of a recent version of the aquatic barriers and
				connectivity results (may not match the exact version here), you can import one of the
				following connectivity analysis map services into your GIS tool of choice:
			</p>

			<ul class="mt-2">
				<li>
					<a href={MAP_SERVICES.dams} target="_blank" rel="external">Dams</a> based on networks that are
					cut by dams and waterfalls.
				</li>
				<li>
					<a href={MAP_SERVICES.small_barriers} target="_blank" rel="external">
						Surveyed road/stream crossings
					</a>
					based on networks that are cut by dams, waterfalls, and surveyed road/stream crossings.
				</li>
				<li>
					<a href={MAP_SERVICES.combined_barriers} target="_blank" rel="external">
						Dams & surveyed road/stream crossings
					</a>
					based on networks that are cut by dams, waterfalls, and surveyed road/stream crossings.
				</li>
			</ul>
		</div>

		<hr />

		<div>
			<h2>What kind of barriers does the Inventory track?</h2>
			<p>
				See the
				<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">NACC FAQ page</a>.
			</p>
		</div>

		<hr />

		<div>
			<h2>What data sources are included in the Inventory?</h2>
			<p>
				See the
				<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">NACC FAQ page</a>.
			</p>
		</div>

		<hr />

		<div>
			<h2>How is the Inventory maintained and updated?</h2>
			<p>
				See the
				<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">NACC FAQ page</a>.
			</p>
		</div>

		<hr />

		<div>
			<h2>How can I report a missing barrier?</h2>
			<p>
				See the
				<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">NACC FAQ page</a>.
			</p>
		</div>
	</div>
</div>
