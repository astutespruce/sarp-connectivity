<script lang="ts">
	import { SITE_NAME } from '$lib/env'
</script>

<svelte:head>
	<title>Not found | {SITE_NAME}</title>
</svelte:head>

<div class="relative w-full h-full">
	<div class="hidden md:block absolute top-0 bottom-0 left-0 right-0 overflow-hidden">
		<enhanced:img
			src="$lib/assets/images/25898720604_f380ee9709_k.jpg"
			alt=""
			class="brightness-80"
		/>
		<div class="sticky bottom-0">
			<div class="absolute bottom-0 right-0 bg-black/65 text-white px-2 text-sm">
				Photo: students looking for macroinvertebrates in Cartoogechaye Creek, NC |
				<a
					href="https://www.flickr.com/photos/usfwssoutheast/25898720604/"
					target="_blank"
					class="text-white"
				>
					U.S. Fish & Wildlife Service Southeast Region</a
				>
			</div>
		</div>
	</div>
	<div class="relative mx-auto max-w-200 p-4 bg-white top-10">
		<h1 class="text-5xl">PAGE NOT FOUND</h1>
		<div class="text-2xl mt-4">
			However, we hope that by restoring aquatic connectivity, aquatic organisms will continue to be
			FOUND.
		</div>
	</div>
</div>
