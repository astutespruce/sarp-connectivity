<script lang="ts">
	import AlertIcon from '@lucide/svelte/icons/triangle-alert'

	import { Root, Title, Description } from '$lib/components/ui/alert'

	const { class: className = null, iconClass = null, title, children } = $props()
</script>

<Root variant="destructive" class={className}>
	<Title class="font-bold flex gap-2 items-center"><AlertIcon class={iconClass} /> {title}</Title>
	<Description>
		{@render children()}
	</Description>
</Root>
