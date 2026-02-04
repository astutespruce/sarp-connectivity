<script lang="ts">
	import ExploreIcon from '@lucide/svelte/icons/map'
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'
	import RestorationIcon from '@lucide/svelte/icons/chart-no-axes-combined'

	import { resolve } from '$app/paths'
	import { Button } from '$lib/components/ui/button'

	const { exploreURL, restorationURL, prioritizeURL } = $props()
</script>

<div
	class="grid sm:grid-cols-3 gap-0 bg-grey-1/75 mt-16 p-4 border-t border-t-grey-3 border-b border-b-grey-3 [&>div]:flex [&>div]:flex-col [&>div]:gap-4 [&>div+div]:border-t-2 sm:[&>div+div]:border-t-0 sm:[&>div+div]:border-l-2 [&>div]:border-white [&>div+div]:mt-6 sm:[&>div+div]:mt-0 [&>div+div]:pt-4 sm:[&>div+div]:pt-0 sm:[&>div]:px-6 [&>div]:w-full sm:[&>div]:h-full"
>
	<div>
		<div class="flex-none">
			Explore how many dams or surveyed road/stream crossings there are in a state, county, or
			watershed.
		</div>
		<div class="flex-auto flex justify-center items-end mt-4">
			<Button href={resolve(exploreURL)} class="no-underline">
				<ExploreIcon class="size-6" />
				Start exploring
			</Button>
		</div>
	</div>

	<div>
		<div class="flex-none">
			Explore dams and surveyed road/stream crossings that have been removed or mitigated by state,
			county, or watershed.
		</div>
		<div class="flex-auto flex justify-center items-end mt-4">
			<Button href={resolve(restorationURL)} class="no-underline">
				<RestorationIcon class="size-6" />
				See restoration progress
			</Button>
		</div>
	</div>

	<div>
		<div class="flex-none">
			Identify and rank dams or surveyed road/stream crossings that reconnect the most high-quality
			aquatic networks.
		</div>
		<div class="flex-auto flex justify-center items-end mt-4">
			<Button href={resolve(prioritizeURL)} class="no-underline">
				<PrioritizeIcon class="size-6" />
				Start prioritizing
			</Button>
		</div>
	</div>
</div>
