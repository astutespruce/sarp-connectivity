<script lang="ts">
	import { SCENARIOS, barrierTypeLabels } from '$lib/config/constants'
	import { Downloader } from '$lib/components/download'
	import { Header, Footer } from '$lib/components/sidebar'
	import { Slider } from '$lib/components/ui/slider'
	import { ExpandableParagraph } from '$lib/components/text'
	import { BackButton, StartOverButton } from '$lib/components/workflow'
	import { countBy } from '$lib/util/data'
	import { formatNumber, capitalize } from '$lib/util/format'

	import Histogram from './Histogram.svelte'
	import type { BarrierTypePlural } from '$lib/config/types'

	const resultTypePefix = { full: '', perennial: 'p', mainstem: 'm' }
	const tiers = Array.from({ length: 20 }, (_, i) => i + 1)

	let {
		networkType,
		config: rawConfig,
		scenario: rawScenario,
		resultsType,
		rankData,
		tierThreshold = $bindable(),
		onBack,
		onStartOver
	} = $props()

	const barrierTypeLabel = $derived(barrierTypeLabels[networkType as BarrierTypePlural])

	const scenario = $derived(
		`${resultTypePefix[resultsType as keyof typeof resultTypePefix]}${rawScenario}`
	)
	const scenarioLabel = $derived.by(() => {
		if (scenario === 'ncwc') {
			return 'combined network connectivity and watershed condition'
		} else if (scenario === 'pncwc') {
			return 'combined perennial network connectivity and watershed condition'
		}

		return SCENARIOS[scenario as keyof typeof SCENARIOS].toLowerCase()
	})

	// convert to full histogram
	const counts = $derived.by(() => {
		// count records by tier
		const tierCounts = $derived(countBy(rankData, scenario))

		return tiers.map((tier) => tierCounts[tier] || 0)
	})
</script>

<div class="flex flex-col h-full">
	<Header class="pt-2 pb-1 px-4">
		<BackButton label="modify filters" onClick={onBack} />

		<h2 class="text-xl">Explore results</h2>

		<div class="text-muted-foreground text-sm mt-1">
			{formatNumber(rankData.length, 0)} prioritized {barrierTypeLabel}
		</div>
	</Header>

	<div class="flex-auto pt-2 px-4 pb-4 overflow-y-auto overflow-x-hidden">
		<div class="text-muted-foreground text-sm">
			<ExpandableParagraph
				snippet={`${capitalize(barrierTypeLabel)} are binned into tiers based on...`}
			>
				{capitalize(barrierTypeLabel)} are binned into tiers based on where they fall within the value
				range of the <b>{scenarioLabel}</b>
				score. Tier 1 includes {barrierTypeLabel} that fall within the top 5% of values for this score,
				and tier 20 includes {barrierTypeLabel}
				that fall within the lowest 5% of values for this score.
			</ExpandableParagraph>
		</div>

		<div class="mt-4">
			<h3 class="text-lg leading-snug">
				Choose top-ranked {barrierTypeLabel} for display on map
			</h3>

			<div class="flex items-center my-4 mr-4 text-xs text-muted-foreground gap-2">
				<div class="flex-none">Lowest tier</div>
				<Slider
					type="single"
					bind:value={
						() => 21 - tierThreshold,
						(v) => {
							tierThreshold = 21 - v
						}
					}
					min={1}
					max={20}
					step={1}
					class="max-w-[70%]"
				/>
				<div class="flex-none">Highest tier</div>
			</div>

			<div class="text-xs text-muted-foreground">
				Use this slider to control the number of tiers visible on the map. Based on the number of {barrierTypeLabel}
				visible for your area, you may be able to identify {barrierTypeLabel} that are more feasible in
				the top several tiers than in the top-most tier.
			</div>
		</div>

		<div class="mt-8">
			<h3 class="text-lg mb-1">
				Number of {barrierTypeLabel} by tier:
			</h3>

			<Histogram {counts} threshold={tierThreshold} />
		</div>
	</div>

	<Footer class="pt-4 flex items-center justify-between">
		<StartOverButton {onStartOver} />
		<Downloader
			barrierType={networkType}
			disabled={rankData.length === 0}
			label="Download prioritized barriers"
			config={{ ...rawConfig, scenario }}
			customRank
		/>
	</Footer>
</div>
