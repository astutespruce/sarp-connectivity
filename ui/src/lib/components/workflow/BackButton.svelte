<script lang="ts">
	import ChevronsLeftIcon from '@lucide/svelte/icons/chevrons-left'
	import { Button } from '$lib/components/ui/button'

	const { label, onClick } = $props()
</script>

<Button
	variant="link"
	class="no-underline hover:underline h-auto p-0! text-left gap-0.5 -mx-3 text-sm"
	onclick={onClick}
>
	<ChevronsLeftIcon class="size-5" />
	{label}
</Button>
