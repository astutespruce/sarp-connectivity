<script lang="ts">
	import PrintIcon from '@lucide/svelte/icons/file-input'

	import { browser } from '$app/environment'
	import { Button } from '$lib/components/ui/button'

	import Header from './Header.svelte'
	import { Map } from './map'

	const { networkType, data } = $props()

	const handlePrint = () => {
		window.print()
	}
</script>

<div class="container w-180 pt-8 pb-8 print:pt-0">
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

	<Header {...data} />

	<Map {networkType} {...data} />
</div>
