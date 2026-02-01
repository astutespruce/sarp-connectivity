<script lang="ts">
	import ExploreIcon from '@lucide/svelte/icons/earth'
	import RestorationIcon from '@lucide/svelte/icons/fish'

	import { resolve } from '$app/paths'
	import { REGIONS } from '$lib/config/constants'

	const regions = Object.entries(REGIONS)
		.map(([id, { name: label, order }]) => ({ id, label, order }))
		.sort(({ order: a }, { order: b }) => (a < b ? -1 : 1))
</script>

<div class="grid sm:grid-cols-2 gap-6 sm:p-2">
	<div>
		<div class="sm:bg-blue-1/50 sm:p-2 rounded-sm">
			<div class="flex gap-2">
				<ExploreIcon class="size-5 text-muted-foreground" />
				<a href={resolve('/explore/')} class="sm:font-bold block leading-snug">
					Explore and download barriers
				</a>
			</div>
			<p class="pl-7 leading-tight text-sm mt-2">
				You can explore summary statistics for different areas like watersheds, states, counties,
				and more. Once you have selected your area of interest, you can download barriers in that
				area. You can also explore all barriers on the map to learn more.
			</p>
		</div>
		<div class="mt-6 sm:bg-blue-1/50 sm:p-2 rounded-sm">
			<div class="flex gap-2">
				<RestorationIcon class="size-5 text-muted-foreground" />
				<a href={resolve('/restoration/')} class="sm:font-bold block leading-snug">
					Explore restoration progress</a
				>
			</div>
			<p class="pl-7 leading-tight text-sm mt-2">
				You can explore removed and mitigated barriers on the map and view summary statistics of
				restoration progress over time for various areas.
			</p>
		</div>
	</div>
	<div class=" sm:border-l sm:border-l-grey-2 sm:pl-6">
		<div class="font-bold">Explore barriers by region:</div>
		<ul class="pl-7 sm:pl-4 sm:mt-4">
			{#each regions as region (region.id)}
				<li class="mt-2 sm:mt-3">
					<a href={resolve(`/regions/${region.id}`)} class="block leading-snug">
						{region.label}
					</a>
				</li>
			{/each}

			<li class="mt-2 sm:mt-3 sm:pt-3 sm:border-t sm:border-t-grey-2">
				<a href={resolve(`/fhp/`)} class="block leading-snug">Fish Habitat Partnerships</a>
			</li>
		</ul>
	</div>
</div>
