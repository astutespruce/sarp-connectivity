<script lang="ts">
	import { resolve } from '$app/paths'

	import { REGIONS } from '$lib/config/constants'

	const mapImages = import.meta.glob('$lib/assets/images/maps/regions/*.png', {
		eager: true,
		import: 'default',
		query: {
			w: '500;250',
			format: 'avif;webp;png',
			as: 'picture'
		}
	})

	const maps: { [key: string]: any } = {}
	for (const path in mapImages) {
		const [region] = path.split('/').slice(-1)[0].split('.')
		maps[region] = mapImages[path]
	}

	type Region = {
		id: string
		order: number
		name: string
		url: string
		inDevelopment?: boolean
	}
	const regions: Region[] = Object.entries(REGIONS)
		.map(([id, rest]) => ({ id, ...rest }))
		.sort(({ order: a }, { order: b }) => (a < b ? -1 : 1))
</script>

<h2 class="text-2xl sm:text-3xl">Explore the inventory by region</h2>

<div class="grid sm:grid-cols-3 gap-6 bg-blue-0 p-4 items-stretch">
	{#each regions as region (region.id)}
		<a
			href={resolve(`/regions/${region.id}`)}
			class="bg-white p-2 border border-grey-1 rounded-sm h-full flex flex-col justify-end hover:shadow-md hover:border-grey-8 no-underline"
		>
			<div>{region.name}</div>
			{#if region.inDevelopment}
				<div class="text-sm text-muted-foreground">(in development)</div>
			{/if}

			<enhanced:img
				src={maps[region.id]}
				alt={`${region.name} map`}
				class="border border-grey-4 mt-1"
			/>
		</a>
	{/each}
</div>
