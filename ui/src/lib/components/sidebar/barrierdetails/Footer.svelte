<script lang="ts">
	import EmailIcon from '@lucide/svelte/icons/mail-warning'
	import type { BarrierTypePlural } from '$lib/config/types'
	import { barrierTypeLabelSingular } from '$lib/config/constants'

	import { CONTACT_EMAIL } from '$lib/env'

	const { barrierType, sarpid } = $props()

	const typeLabel = $derived(barrierTypeLabelSingular[barrierType as BarrierTypePlural])
</script>

<div class="flex-none py-2 border-t border-t-grey-2">
	<div class="flex justify-center items-center gap-1">
		<a
			href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Barrier Inventory for ${typeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the National Barrier Inventory for this barrier:`}
		>
			<EmailIcon size="1rem" /> Report an error with this barrier
		</a>
	</div>
	<div class="text-xs text-muted-foreground px-4 mt-1 leading-tight">
		If this barrier should have a different value for one of the fields above, please let us know!
	</div>
</div>
