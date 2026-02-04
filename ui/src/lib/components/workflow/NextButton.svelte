<script lang="ts">
	import ChevronsRightIcon from '@lucide/svelte/icons/chevrons-right'

	import { Button } from '$lib/components/ui/button'

	const { label, disabled = false, title = null, onClick } = $props()
</script>

<Button {disabled} {title} onclick={onClick}>
	<div>
		{label}
	</div>
	<ChevronsRightIcon class="size-6" />
</Button>
