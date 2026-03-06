<script lang="ts">
	import { op } from 'arquero'
	import type { RowObject } from 'arquero/dist/types/table/types'

	import { CONTACT_EMAIL } from '$lib/env'
	import { SURVEYED } from '$lib/config/constants'
	import { Downloader } from '$lib/components/download'
	import { Header, Footer } from '$lib/components/sidebar'

	import { BackButton, StartOverButton } from '$lib/components/workflow'
	import { formatNumber, singularOrPlural } from '$lib/util/format'

	let { networkType, crossfilter, config, onBack, onStartOver } = $props()

	const surveyedStatusValues = Object.entries(SURVEYED)
	const surveyedStatusCounts = $derived(
		Object.fromEntries(
			crossfilter.filteredData
				.groupby('surveyed')
				.rollup({ _count: (d: RowObject) => op.sum(d._count) })
				.rename({ _count: 'count' })
				.objects()
				.map(({ surveyed, count }: { surveyed: number; count: number }) => [surveyed, count])
		)
	)
</script>

<div class="flex flex-col h-full">
	<Header class="pt-2 pb-1 px-4">
		<BackButton label="modify filters" onClick={onBack} />

		<h2 class="text-xl">Download selected crossings</h2>
	</Header>

	<div class="flex-auto pt-4 px-4 pb-4 overflow-y-auto overflow-x-hidden">
		<p>
			You have currently selected {formatNumber(crossfilter.filteredCount)} road/stream crossings for
			download, including:
		</p>
		<ul class="list-disc pl-4 mt-2">
			{#each surveyedStatusValues as [value, label] (value)}
				<li class="not-first:mt-1">
					{formatNumber(surveyedStatusCounts[value] || 0)} that
					{singularOrPlural('is', 'are', surveyedStatusCounts[value] || 0)}
					{label}
				</li>
			{/each}
		</ul>

		<hr />

		<div class="mt-8 text-muted-foreground text-sm">
			The NACC is currently developing a new crossing data portal to collect surveyed crossing data
			based on the North Atlantic Aquatic Connectivity Collaborative Data Center.

			<br /><br />

			For now, if you are surveying crossings in the Northeast, you can use the
			<a href="https://naacc.org/naacc_data_center_home.cfm" target="_blank" rel="external"
				>NAACC Data Center</a
			>.

			<br /><br />
			You can also <a href={`mailto:${CONTACT_EMAIL}`} target="_blank">contact us</a> for access to an
			ArcGIS Survey123 data collector app that will help you collect survey data according to the NAACC's
			nontidal and tidal protocols.
		</div>
	</div>

	<Footer class="pt-4 flex items-center justify-between">
		<StartOverButton {onStartOver} />
		<Downloader
			barrierType={networkType}
			label="Download selected crossings"
			triggerLabel="Download selected crossings"
			disabled={crossfilter.filteredCount === 0}
			{config}
		/>
	</Footer>
</div>
