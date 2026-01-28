<script lang="ts">
	import EmailIcon from '@lucide/svelte/icons/mail-warning'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { barrierTypeLabelSingular } from '$lib/config/constants'

	import { CONTACT_EMAIL } from '$lib/env'
	import { dataVersion } from '$lib/config/constants'

	const { barrierType, sarpid } = $props()

	const typeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<div class="flex-none py-2 border-t border-t-grey-2 bg-grey-1/50">
	<a
		href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Barrier Inventory for ${typeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the National Barrier Inventory for this barrier:`}
		class="flex justify-center items-center gap-2 no-underline hover:underline"
	>
		<EmailIcon class="size-5" /> Report an error with this barrier
	</a>
	<div class="text-xs text-muted-foreground px-4 mt-1 leading-none">
		If this barrier should have a different value for one of the fields above, please let us know!
	</div>
</div>
