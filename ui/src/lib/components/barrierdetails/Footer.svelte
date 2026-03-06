<script lang="ts">
	import EmailIcon from '@lucide/svelte/icons/mail-warning'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { barrierTypeLabelSingular, dataVersion } from '$lib/config/constants'
	import { CONTACT_EMAIL } from '$lib/env'
	import { Footer as SidebarFooter } from '$lib/components/sidebar'

	const { barrierType, sarpid } = $props()

	const typeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<SidebarFooter class="flex-none">
	<a
		href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Barrier Inventory for ${typeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the National Barrier Inventory for this barrier:`}
		target="_blank"
		class="flex justify-center items-center gap-2 no-underline hover:underline"
	>
		<EmailIcon class="size-5" /> Report an error with this barrier
	</a>
	<div class="text-xs text-muted-foreground px-4 mt-1 leading-none">
		If this barrier should have a different value for one of the fields above, please let us know!
	</div>
</SidebarFooter>
