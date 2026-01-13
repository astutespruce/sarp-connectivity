<script lang="ts">
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'

	import LowNetworkComplexityIcon from '$lib/assets/icons/size_classes_low.svg'
	import HighNetworkComplexityIcon from '$lib/assets/icons/size_classes_high.svg'
</script>

<svelte:head>
	<title>Network complexity | {SITE_NAME}</title>
</svelte:head>

<HeaderImage author="David Kovalenko." url="https://unsplash.com/photos/qYMa2-P-U0M">
	<enhanced:img src="$lib/assets/images/david-kovalenko-qYMa2-P-U0M-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Network complexity</h1>
	<p class="mt-8">
		A barrier that has upstream tributaries of different size classes, such as small streams, small
		rivers, and large rivers, would contribute a more complex connected aquatic network if it was
		removed. In contrast, a barrier with fewer upstream tributaries may contribute few if any size
		classes to the network if removed. In general, a more complex network composed of a greater
		range of size classes is more likely to have a wide range of available habitat for a greater
		number of aquatic species.
	</p>

	<div class="mt-8 grid sm:grid-cols-2 gap-8">
		<HighlightBox title="No size classes gained" icon={LowNetworkComplexityIcon}>
			Barriers that do not contribute any additional size classes are less likely to contribute a
			wide range of aquatic habitat.
		</HighlightBox>

		<HighlightBox title="Several size classes gained" icon={HighNetworkComplexityIcon}>
			Barriers that have several size classes upstream are more likely to contribute a more complex
			network with a greater range of aquatic habitat for a greater variety of species.
		</HighlightBox>
	</div>

	<h2 class="mt-12">Methods</h2>
	<ol class="mt-2">
		<li>
			Stream and river reaches were assigned to size classes based on total drainage area:
			<ul class="mb-4">
				<li>
					Headwaters: &lt; 10 km
					<sup>2</sup>
				</li>
				<li>
					Creeks: &ge; 10 km
					<sup>2</sup> and &lt; 100 km
					<sup>2</sup>
				</li>
				<li>
					Small rivers: &ge; 100 km
					<sup>2</sup> and &lt; 518 km
					<sup>2</sup>
				</li>
				<li>
					Medium tributary rivers: &ge; 519 km
					<sup>2</sup> and &lt; 2,590 km
					<sup>2</sup>
				</li>
				<li>
					Medium mainstem rivers: &ge; 2,590 km
					<sup>2</sup> and &lt; 10,000 km
					<sup>2</sup>
				</li>
				<li>
					Large rivers: &ge; 10,000 km
					<sup>2</sup> and &lt; 25,000 km
					<sup>2</sup>
				</li>
				<li>
					Great rivers: &ge; 25,000 km
					<sup>2</sup>
				</li>
			</ul>
		</li>
		<li>
			Each barrier is assigned the total number of unique size classes in its upstream functional
			network.
		</li>
	</ol>
</div>
