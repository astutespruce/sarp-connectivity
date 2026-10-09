<script lang="ts">
	import ExploreIcon from '@lucide/svelte/icons/earth'
	import RestorationIcon from '@lucide/svelte/icons/fish'

	import { resolve } from '$app/paths'
	import { REGIONS } from '#lib/config/constants.js'

	const regions = Object.entries(REGIONS)
		.map(([id, { name: label, order }]) => ({ id, label, order }))
		.sort(({ order: a }, { order: b }) => (a < b ? -1 : 1))
</script>

<div class="grid sm:grid-cols-2 gap-6 sm:p-2">
	<div>
		<div class="sm:bg-blue-1/50 sm:p-2 rounded-sm">
			<div class="flex gap-2">
				<ExploreIcon class="size-5 text-muted-foreground" />
				<a href={resolve('/explore/', {})} class="sm:font-bold block leading-snug">
					Summarize & download barriers
				</a>
			</div>
			<ul class="mt-2 text-sm pl-6 [&_li]:not-first-of-type:mt-2 leading-tight">
				<li>
					<b>View summary statistics</b> for different areas like watersheds, states, counties, and more
				</li>
				<li>
					<b>Download barriers</b> for the nation or a selected area.
				</li>
				<li>
					<b>Explore details</b> for a selected barrier on the map.
				</li>
			</ul>
		</div>
		<div class="mt-6 sm:bg-blue-1/50 sm:p-2 rounded-sm">
			<div class="flex gap-2">
				<RestorationIcon class="size-5 text-muted-foreground" />
				<a href={resolve('/restoration/', {})} class="sm:font-bold block leading-snug">
					Explore restoration progress</a
				>
			</div>
			<ul class="mt-2 text-sm pl-6 [&_li]:not-first-of-type:mt-2 leading-tight">
				<li>
					<b>View summary statistics</b> for removed / mitigated barriers and progress over time.
				</li>
				<li>
					<b>Explore details</b> for a selected removed barrier on the map.
				</li>
			</ul>
		</div>
	</div>
	<div class=" sm:border-l sm:border-l-grey-2 sm:pl-6">
		<div class="font-bold">Explore barriers by region:</div>
		<ul class="pl-7 sm:pl-4 sm:mt-4">
			{#each regions as region (region.id)}
				<li class="mt-2 sm:mt-3">
					<a href={resolve(`/regions/${region.id}`, { id: region.id })} class="block leading-snug">
						{region.label}
					</a>
				</li>
			{/each}

			<li class="mt-2 sm:mt-3 sm:pt-3 sm:border-t sm:border-t-grey-2">
				<a href={resolve(`/fhp/`, {})} class="block leading-snug">Fish Habitat Partnerships</a>
			</li>
		</ul>
	</div>
</div>
