<script lang="ts">
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'

	import HighAlteredIcon from '$lib/assets/icons/sinuosity_low.svg'
	import LowAlteredIcon from '$lib/assets/icons/sinuosity_high.svg'
</script>

<svelte:head>
	<title>Channel alteration | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Washington State Department of Agriculture."
	url="https://www.flickr.com/photos/wsdagov/42209868424/"
>
	<enhanced:img src="$lib/assets/images/42209868424_bb2dd0f7f0_o.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Channel alteration</h1>
	<p class="mt-8">
		Altered river and stream reaches are those that are specifically identified as canals or
		ditches. These represent areas where the hydrography, flow, and water quality may be highly
		altered compared to natural conditions.
		<br />
		<br />
		Networks are characterized by the percent of their total network length that is in altered river and
		stream reaches.
	</p>

	<div class="mt-8 grid sm:grid-cols-2 gap-8">
		<HighlightBox title="Highly altered" icon={HighAlteredIcon}>
			Rivers and streams altered by artificial channelization to create canals and ditches may have
			a lower variety and quality of in-stream habitat due to differences in hydrography, flow,
			water quality, and other factors compared to natural stream channels. Barriers with more
			highly altered upstream networks may contribute less natural habitat if removed.
		</HighlightBox>

		<HighlightBox title="Less altered" icon={LowAlteredIcon}>
			Rivers and streams with lower amounts of artificial channelization to create canals and
			ditches may have a wider variety of higher-quality in-stream habitat. Barriers with less
			altered upstream networks may contribute more natural habitat if removed.
		</HighlightBox>
	</div>

	<h2 class="mt-12">Methods</h2>
	<ol class="mt-2">
		<li>
			The total upstream length is calculated as the sum of the lengths of all upstream river and
			stream reaches.
		</li>
		<li>
			The total downstream length is calculated for the network immediately downstream of the
			barrier. Note: this is the total network length of the downstream network, <i>not</i> the shortest
			downstream path to the next barrier or river mouth.
		</li>
		<li>Network length is the smaller of the upstream or downstream network lengths.</li>
	</ol>
</div>
