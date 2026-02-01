<script lang="ts">
	import { resolve } from '$app/paths'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'
	import { FISH_HABITAT_PARTNERSHIPS } from '$lib/config/constants'

	import NFHPLogo from '$lib/assets/images/nfhp_logo.svg'

	const mapImages = import.meta.glob('$lib/assets/images/maps/fhp/*.png', {
		eager: true,
		import: 'default',
		query: {
			w: '500;250',
			format: 'avif;webp;png',
			as: 'picture'
		}
	})

	const maps: { [key: string]: unknown } = {}
	for (const path in mapImages) {
		const [region] = path.split('/').slice(-1)[0].split('.')
		maps[region] = mapImages[path]
	}

	const fhps = Object.entries(FISH_HABITAT_PARTNERSHIPS)
		.sort(([leftId], [rightId]) => (leftId <= rightId ? -1 : 1))
		.map(([id, { name }]) => ({ id, name }))
</script>

<svelte:head>
	<title>Fish Habitat Partnerships | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Brook trout. Photo: Jason Ross/USFWS."
	url="https://www.flickr.com/photos/usfwsmidwest/34597621345/"
>
	<enhanced:img src="$lib/assets/images/34597621345_26d60382fd_o.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Fish Habitat Partnerships</h1>

	<div class="grid sm:grid-cols-[2fr_1fr] gap-8 mt-12">
		<p>
			The
			<a href="https://www.fishhabitat.org/" target="_blank" rel="external">
				National Fish Habitat Partnership
			</a>
			works to conserve and protect the nation&apos;s fisheries and aquatic systems through a network
			of 20 Fish Habitat Partnerships.
		</p>
		<figure>
			<img src={NFHPLogo} alt="National Fish Habitat Partnership logo" class="w-[264px] h-[56px]" />
		</figure>
	</div>

	<div class="font-bold text-xl mt-12">
		View more about the status of the inventory in each Fish Habitat Partnership:
	</div>

	<div class="grid sm:grid-cols-3 gap-6 bg-blue-0 p-4 items-stretch mt-2">
		{#each fhps as fhp (fhp.id)}
			<a
				href={resolve(`/fhp/${fhp.id}/`, { id: fhp.id })}
				class="bg-white p-2 border border-grey-1 rounded-sm h-full flex flex-col justify-end hover:shadow-md hover:border-grey-8 no-underline"
			>
				<div>
					{fhp.name}
				</div>

				<enhanced:img
					src={maps[fhp.id]}
					alt={`${fhp.name} map`}
					class="border border-grey-4 mt-1"
				/>
			</a>
		{/each}
	</div>
</div>
