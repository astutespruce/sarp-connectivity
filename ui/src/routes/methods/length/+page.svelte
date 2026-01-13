<script lang="ts">
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'

	import LowNetworkLengthIcon from '$lib/assets/icons/length_low.svg'
	import HighNetworkLengthIcon from '$lib/assets/icons/length_high.svg'
</script>

<svelte:head>
	<title>Network length | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Little Tennessee River, North Carolina. U.S. Fish and Wildlife Service."
	url="https://www.flickr.com/photos/usfwssoutheast/5149475130/in/gallery-141606341@N03-72157697846677391/"
>
	<enhanced:img src="$lib/assets/images/5149475130_b2334f1edd_4k.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Network length</h1>

	<p class="mt-8">
		Network length measures the amount of connected aquatic network length that would be added to
		the network by removing the barrier. It is the smaller of either the total upstream network
		length or total downstream network length for the networks subdivided by this barrier. This is
		because a barrier may have a very large upstream network, but if there is another barrier
		immediately downstream, the overall effect of removing this barrier will be quite small.
	</p>

	<div class="mt-8 grid sm:grid-cols-2 gap-8">
		<HighlightBox title="Low network length" icon={LowNetworkLengthIcon}>
			Barriers that have small upstream or downstream networks contribute relatively little
			connected aquatic network length if removed.
		</HighlightBox>

		<HighlightBox title="High network length" icon={HighNetworkLengthIcon}>
			Barriers that have large upstream and downstream networks will contribute a large amount of
			connected aquatic network length if they are removed.
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
