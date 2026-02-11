<script lang="ts">
	import { resolve } from '$app/paths'
	import { SITE_NAME } from '$lib/env'
	import { Button } from '$lib/components/ui/button'
	import { HeaderImage } from '$lib/components/image'

	import { summaryStats } from '$lib/config/summaryStats'

	const {
		rankedDams,
		rankedSmallBarriers,
		rankedLargefishBarriersDams,
		rankedLargefishBarriersSmallBarriers,
		rankedSmallfishBarriersDams,
		rankedSmallfishBarriersSmallBarriers
	} = summaryStats

	const steps = [
		{
			label: 'Select area of interest',
			description:
				'You can select areas using state, county, and watershed boundaries.  Prioritization is limited to areas with dams or surveyed road/stream crossings depending on the scenario.'
		},
		{
			label: 'Filter barriers',
			description:
				'You can filter barriers by feasibility, height, and other key characteristics to select those that best meet your needs.'
		},
		{
			label: 'Explore priorities on the map',
			description:
				'Once you have defined your area of interest and selected the barriers you want, you can explore them on the map.'
		},
		{
			label: 'Download prioritized barriers',
			description:
				'You can download the inventory for your area of interest and perform offline work.'
		}
	]

	const networkTypes = [
		{
			id: 'dams',
			label: 'Dams',
			description: 'Prioritize dams based on aquatic networks cut by dams and waterfalls.',
			count: rankedDams
		},
		{
			id: 'small_barriers',
			label: 'Surveyed crossings',
			description:
				'Prioritize surveyed road/stream crossings based on aquatic networks cut by dams, waterfalls, and crossings with at least moderate barrier severity.',
			count: rankedSmallBarriers
		},
		{
			id: 'combined_barriers',
			label: 'Dams & surveyed crossings',
			description:
				'Prioritize dams and surveyed road/stream crossings based on aquatic networks cut by dams, waterfalls, and crossings with at least moderate barrier severity.',
			count: rankedDams + rankedSmallBarriers
		},
		{
			id: 'largefish_barriers',
			label: 'Large-bodied fish barriers',
			description:
				'Prioritize dams and surveyed road/stream crossings that are likely to impact large-bodied fish species based on aquatic networks cut by dams and waterfalls that do not have partial or seasonal passability to salmonids and non-salmonids, and crossings with severe or significant barrier severity.',
			count: rankedLargefishBarriersDams + rankedLargefishBarriersSmallBarriers
		},
		{
			id: 'smallfish_barriers',
			label: 'Small-bodied fish barriers',
			description:
				'Prioritize dams and surveyed road/stream crossings based on aquatic networks cut by dams, waterfalls, and crossings with at least minor barrier severity.',
			count: rankedSmallfishBarriersDams + rankedSmallfishBarriersSmallBarriers
		}
	]
</script>

<svelte:head>
	<title>Prioritize dams and surveyed road/stream crossings | {SITE_NAME}</title>
</svelte:head>

<HeaderImage author="Zach Dutra" url="https://unsplash.com/photos/2d7Y5Yi3aq8">
	<enhanced:img src="$lib/assets/images/zack-dutra-2d7Y5Yi3aq8-unsplash.jpg" alt="" />
</HeaderImage>

<div class="grid md:grid-cols-[1fr_2fr] gap-0 pb-8">
	<div class="md:bg-grey-1/75 pt-8 px-4 pb-4">
		<h1 class="text-2xl pb-2 border-b-2 border-b-white">How to prioritize barriers:</h1>

		<div class="mt-4">
			{#each steps as step, i (step.label)}
				<div class="flex gap-2 mt-2 items-center not-first:mt-8">
					<div class="step size-8">{i + 1}</div>
					<div class="text-xl font-bold">{step.label}</div>
				</div>
				<p class="text-sm text-muted-foreground mt-2 ml-10">
					{step.description}
				</p>
			{/each}
		</div>
	</div>

	<div class="mx-8 mt-8 md:mt-0">
		<h2 class="text-2xl mt-8">Prioritization scenarios available:</h2>
		<div class="grid md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5 gap-4 mt-4">
			{#each networkTypes as networkType (networkType.id)}
				<div class="bg-blue-1/40 rounded-lg pt-2 px-4 pb-4 border border-grey-2">
					<div class="flex flex-col gap-2 h-full">
						<div class="flex-none font-bold border-b-2 border-b-white pb-2 text-lg">
							{networkType.label}
						</div>
						<div class="flex flex-auto f-full text-sm">
							{networkType.description}
						</div>
						<Button
							href={resolve(`/priority/${networkType.id}/`, { networkType: networkType.id })}
							class="w-full flex-none mt-6">Start prioritizing</Button
						>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>
