<script lang="ts">
	import { resolve } from '$app/paths'
	import { Alert } from '$lib/components/alert'
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'
	import NetworkGraphicSVG from '$lib/assets/images/functional_network.svg'

	import NetworkLengthIcon from '$lib/assets/icons/length_high.svg'
	import NetworkComplexityIcon from '$lib/assets/icons/size_classes_high.svg'
	import ChannelAlterationIcon from '$lib/assets/icons/sinuosity_high.svg'
	import NaturalLandcoverIcon from '$lib/assets/icons/nat_landcover_high.svg'
</script>

<svelte:head>
	<title>Prioritizing aquatic barriers for removal | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Amelie"
	url="https://unsplash.com/photos/a-group-of-penguins-on-rocks-by-a-body-of-water-Q3oEolT9ZQE"
>
	<enhanced:img src="$lib/assets/images/amelie-Q3oEolT9ZQE-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Prioritizing aquatic barriers for removal</h1>

	<div class="mt-12">
		<div class="flex gap-4">
			<div class="step">1</div>
			<div class="text-2xl">
				Aquatic barriers are identified and measured for their potential impact on aquatic
				organisms:
			</div>
		</div>

		<div class="grid sm:grid-cols-[5fr_3fr] gap-12 mt-8">
			<div>
				<p>
					Aquatic barriers are natural and human-made structures that impede the passage of aquatic
					organisms through the river network.
					<br />
					<br />
					They include:
				</p>
				<ul class="mt-2">
					<li>Waterfalls</li>
					<li>Dams</li>
					<li>Surveyed road/stream crossings</li>
				</ul>
				<p>
					<br />
					Where possible, human-made barriers have been surveyed using field reconnaissance to determine
					their likely impact on aquatic organisms as well as their feasibility of removal. You can leverage
					these characteristics to select a smaller number of barriers to prioritize.
				</p>
			</div>

			<figure>
				<div class="flex justify-center sm:justify-end">
					<enhanced:img src="$lib/assets/images/9272554306_b34bf886f4_z.jpg" alt="Hartwell Dam" />
				</div>
				<figcaption>
					Hartwell Dam, Georgia. Photo:
					<a
						href="https://www.flickr.com/photos/savannahcorps/9272554306/"
						target="_blank"
						rel="external"
					>
						Billy Birdwell, U.S. Army Corps of Engineers.
					</a>
				</figcaption>
			</figure>
		</div>
	</div>

	<hr />

	<div>
		<div class="flex gap-4">
			<div class="step">2</div>
			<div class="text-2xl">
				Aquatic barriers are measured for their impact on the aquatic network:
			</div>
		</div>
		<div class="grid sm:grid-cols-[5fr_1fr] gap-12 mt-8">
			<div>
				<p>
					Functional aquatic networks are the stream and river reaches that extend upstream from a
					barrier or river mouth to either the origin of that stream or the next upstream barrier.
					They form the basis for the aquatic network metrics used in this tool.
					<br />
					<br />
					To calculate functional networks, all barriers were snapped to the&nbsp;
					<a
						href="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution"
						target="_blank"
						rel="external"
					>
						USGS High Resolution National Hydrography Dataset
					</a>
					(NHDPlus). Where possible, their locations were manually inspected to verify their correct position
					on the aquatic network.
					<br />
					<br />
					<a href={resolve('/methods/network/', {})}> Read more about network analysis methods </a>.
				</p>
				<Alert title="Warning" class="mt-12">
					<p class="text-base">
						Due to limitations of existing data sources for aquatic networks, not all aquatic
						barriers can be correctly located on the aquatic networks. These barriers are not
						included in the network connectivity analysis and cannot be prioritized using this tool.
						However, these data can still be downloaded from this tool and used for offline
						analysis.
					</p>
				</Alert>
			</div>

			<figure>
				<div class="flex justify-center sm:justify-end">
					<img src={NetworkGraphicSVG} alt="network graphic" class="h-106" />
				</div>
				<figcaption>Diagram showing upstream functional network.</figcaption>
			</figure>
		</div>
	</div>

	<hr />

	<div>
		<div class="flex gap-4">
			<div class="step">3</div>
			<div class="text-2xl">
				Barriers are characterized using metrics that describe the quality and status of their
				functional networks:
			</div>
		</div>

		<div class="grid sm:grid-cols-2 gap-4 mt-4">
			<HighlightBox title="Network length" icon={NetworkLengthIcon}>
				Network length measures the amount of connected aquatic network length that would be added
				to the network by removing the barrier. Longer connected networks may provide more overall
				aquatic habitat for a wider variety of organisms and better support dispersal and migration.
				<br />
				<br />
				<a href={resolve('/methods/length/', {})}>Read more...</a>
			</HighlightBox>

			<HighlightBox title="Network complexity" icon={NetworkComplexityIcon}>
				Network complexity measures the number of unique upstream size classes that would be added
				to the network by removing the barrier. A barrier that has upstream tributaries of different
				size classes, such as small streams, small rivers, and large rivers, would contribute a more
				complex connected aquatic network if it was removed.
				<br />
				<a href={resolve('/methods/complexity/', {})}>Read more...</a>
			</HighlightBox>

			<HighlightBox title="Channel alteration" icon={ChannelAlterationIcon}>
				Altered river and stream reaches are those that are specifically identified as canals or
				ditches. These represent areas where the hydrography, flow, and water quality may be highly
				altered compared to natural conditions.
				<br />
				<a href={resolve('/methods/unaltered/', {})}>Read more...</a>
			</HighlightBox>

			<HighlightBox title="Natural landcover" icon={NaturalLandcoverIcon}>
				Natural landcover measures the amount of area within the floodplain of the upstream aquatic
				network that is in natural landcover. Rivers and streams that have a greater amount of
				natural landcover in their floodplain are more likely to have higher quality aquatic
				habitat.
				<br />
				<a href={resolve('/methods/landcover/', {})}>Read more...</a>
			</HighlightBox>
		</div>
	</div>

	<p class="mt-4">
		Barrier ranks are calculated for each of these metrics using the following methods:
	</p>
	<ol class="mt-2">
		<li>
			Any geographic and attribute filters specified by the user are applied to select barriers for
			ranking.
		</li>
		<li>
			The unique values for that metric are calculated across all selected barriers. This is so that
			all barriers with the same value for a given metric are assigned the same rank for that
			metric.
		</li>
		<li>
			The unique values are sorted into ascending order and their integer index within this sorted
			order is converted to a 0-1 scale based on the total number of unique values. This means that
			the lowest metric value corresponds to the lowest index value. This is used to assign a rank
			for that metric to each barrier.
			<br /><br />
			Note: channel alteration is measured based on the percent of the channel that is unaltered, so that
			it follows the same ordering as the other metrics.
		</li>
	</ol>

	<hr />

	<div>
		<div class="flex gap-4">
			<div class="step">4</div>
			<div class="text-2xl">
				Metrics are combined and ranked to create three scenarios for prioritizing barriers for
				removal:
			</div>
		</div>
		<div class="grid sm:grid-cols-2 gap-4 mt-4">
			<HighlightBox title="Network connectivity">
				Aquatic barriers prioritized according to network connectivity are driven exclusively on the
				total amount of functional aquatic network that would be reconnected if a given dam was
				removed. This is driven by the&nbsp;
				<a href={resolve('/methods/length', {})}>network length</a> metric. No consideration is given
				to other characteristics that measure the quality and condition of those networks.
			</HighlightBox>

			<HighlightBox title="Watershed condition">
				Aquatic barriers prioritized according to watershed condition are driven by metrics related
				to the overall quality of the aquatic network that would be reconnected if a given dam was
				removed. It is based on a combination of&nbsp;
				<a href={resolve('/methods/complexity', {})}>network complexity</a>,
				<a href={resolve('/methods/unaltered', {})}>percent unaltered</a>, and
				<a href={resolve('/methods/landcover', {})}>floodplain natural landcover</a>. Each of these
				metrics is weighted equally.
			</HighlightBox>
		</div>

		<HighlightBox title="Network connectivity + watershed condition" class="mt-4">
			Aquatic barriers prioritized according to combined network connectivity and watershed
			condition are driven by both the length and quality of the aquatic networks that would be
			reconnected if these barriers are removed. <b>Network connectivity</b> and
			<b>watershed condition</b> are weighted equally.
		</HighlightBox>
	</div>

	<p class="mt-8">
		To reduce the impact of outliers, such as very long functional networks, barriers are assigned
		tiers based on their relative rank within the overall range of unique values for a given metric.
		Many barriers have the same value for a given metric and are given the same relative rank; this
		causes the distribution of values among ranks to be highly uneven in certain areas.
		<br />
		<br />
		Once barriers have been ranked for each of the above scenarios, they are binned into 20 tiers to simplify
		interpretation and use. To do this, barriers that fall in the best 5% of the range of ranks for that
		metric are assigned to Tier 1 (top tier), whereas barriers that fall in the worst 5% of the range
		of ranks for that metric are assigned Tier 20 (bottom tier).
		<br />
		<br />
		Barrier tiers are calculated for these scenarios using the following methods:
	</p>
	<ol class="mt-2">
		<li>
			The ranks for each individual metric are combined into a weighted average using equal weights
			to calculate a composite rank. That is, if there are 3 metric ranks that contribute to a
			composite rank, then each metric is assigned a weight of 1/3.
		</li>
		<li>
			This composite rank is then converted into a relative rank that falls between the minimum and
			maximum rank values across all selected barriers. This puts all barriers on a 0-100% scale.
		</li>
		<li>
			This scale is then subdivided into 5% increments, which correspond to the 20 tiers used in
			this analysis. The lowest 5% of ranks corresponds to Tier 20, and the highest 5% of ranks
			corresponds to Tier 1.
		</li>
	</ol>

	<Alert title="Warning" class="mt-8 text-lg">
		<p class="text-base">
			Tiers are based on position within the range of observed ranks for a given area. They are <i
				>not</i
			> based on the frequency of ranks, such as percentiles, and therefore may have a highly uneven number
			of barriers per tier depending on the area. In general, there are fewer barriers in the top tiers
			than there are in the bottom tiers. This is largely because many barriers share the same value for
			a given metric.
		</p>
	</Alert>
</div>
