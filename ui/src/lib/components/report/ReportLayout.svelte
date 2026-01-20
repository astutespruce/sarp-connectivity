<script lang="ts">
	import PrintIcon from '@lucide/svelte/icons/file-input'

	import { browser } from '$app/environment'
	import { Button } from '$lib/components/ui/button'

	import Footer from './Footer.svelte'
	import Feasibility from './Feasibility.svelte'
	import FunctionalNetworkInfo from './FunctionalNetworkInfo.svelte'
	import Header from './Header.svelte'
	import IDInfo from './IDInfo.svelte'
	import InvasiveSpecies from './InvasiveSpecies.svelte'
	import LandscapeContext from './LandscapeContext.svelte'
	import Location from './Location.svelte'
	import { Map } from './map'
	import Ownership from './Ownership.svelte'
	import MainstemNetworkInfo from './MainstemNetworkInfo.svelte'
	import MarineConnectivity from './MarineConnectivity.svelte'
	import Scores from './Scores.svelte'
	import SpeciesHabitat from './SpeciesHabitat.svelte'
	import SpeciesWatershedPresence from './SpeciesWatershedPresence.svelte'

	const { networkType, data } = $props()

	const handlePrint = () => {
		window.print()
	}

	console.log('data', data)
</script>

<div class="report-container max-w-180 pt-8 pb-8 print:pt-0">
	<div class="flex gap-8 justify-between border-b border-b-grey-1 pb-4 mb-4 print:hidden">
		<div class="text-muted-foreground text-xs flex-auto">
			Use the map below to define the extent and basemap you want visible in your report. Use the <b
				>Print/Save PDF</b
			> button to show your browser's print dialog, where you can choose to save it to a PDF.
		</div>
		<Button onclick={handlePrint} disabled={!browser}>
			<PrintIcon class="size-5" />
			Print / Save PDF
		</Button>
	</div>

	<section class="report-page mt-0 print:mt-0">
		<Header {...data} />

		<Map {networkType} {...data} />
	</section>

	<Location {...data} />

	<Ownership {...data} />

	<LandscapeContext {...data} />

	<FunctionalNetworkInfo {...data} />

	{#if data.ranked && ((data.networkType === 'dams' && data.state_ncwc_tier !== -1) || data.huc8_ncwc_tier !== -1)}
		<Scores {networkType} {...data} />
	{/if}

	{#if !data.removed && data.feasibilityclass > 0 && data.feasibilityclass <= 10}
		<Feasibility {...data} />
	{/if}

	{#if data.hasnetwork && data.habitat && data.habitat.length > 0}
		<SpeciesHabitat {...data} />
	{/if}

	{#if data.hasnetwork && data.flowstoocean && data.milestooutlet < 500}
		<MarineConnectivity {...data} />
	{/if}

	{#if data.hasnetwork && data.totalmainstemupstreammiles > 0}
		<MainstemNetworkInfo {networkType} {...data} />
	{/if}

	<SpeciesWatershedPresence {...data} />

	{#if data.hasnetwork && (data.invasive || data.invasivenetwork === 1)}
		<InvasiveSpecies {...data} />
	{/if}

	<IDInfo {...data} />

	<Footer {...data} />
</div>
