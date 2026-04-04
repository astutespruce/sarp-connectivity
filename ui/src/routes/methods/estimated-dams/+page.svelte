<script lang="ts">
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'
</script>

<svelte:head>
	<title>Estimated Dam Methods | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Amelie"
	url="https://unsplash.com/photos/a-group-of-penguins-on-rocks-by-a-body-of-water-Q3oEolT9ZQE"
>
	<enhanced:img src="$lib/assets/images/amelie-Q3oEolT9ZQE-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Estimated dam methods</h1>
	<p class="mt-8">
		Dams are estimated based on the geometric boundaries of waterbodies at their downstream
		intersection with NHD High Resolution flowlines using the following methods:
	</p>
	<ol class="mt-4">
		<li>
			The aquatic network, including NHD High Resolution flowlines and waterbodies from multiple
			sources are prepared for analysis using several processing and cleaning steps described in
			more detail <a
				href="https://github.com/astutespruce/sarp-connectivity/tree/main/analysis/prep/network"
				target="_blank"
				rel="external">here</a
			>.
		</li>
		<li>
			As part of the above steps, the analysis finds the "drain" points of waterbodies, which are
			the downstream-most points of a set of flowlines that overlaps a waterbody. Drains associated
			with smaller flowline size classes / stream orders are selected for analysis because they are
			more likely to contain un-inventoried dams and also because these methods perform more poorly
			on large waterbodies or stream sizes. These become the set of candidate points for estimating
			dams.
		</li>
		<li>
			Extract a line from the boundary of the waterbody based on the vertex nearest to a given drain
			point and extending to no more than 1/3 of the total coordinates in that waterbody boundary in
			either direction. This is intended to contain the downstream "face" of the waterbody.
		</li>
		<li>
			Perform a Visvalingam-Whyatt simplification of this line to extract the dominant shape and
			remove high-precision vertices.
		</li>
		<li>
			Extract the longest roughly straight line from within the segments in the simplified line
			calculated above.
		</li>
		<li>
			If that line is sufficiently long and contains the waterbody drain point, then flag the
			waterbody drain point as an estimated dam.
		</li>
		<li>
			Estimated dams are then manually reviewed using aerial imagery and other information to
			identify those most likely to represent real dams.
		</li>
		<li>
			As more inventoried dams become available, estimated dams are removed from the inventory
			through a deduplication process.
		</li>
	</ol>
</div>
