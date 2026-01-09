<script lang="ts">
	import FAQIcon from '@lucide/svelte/icons/circle-question-mark'

	import { resolve } from '$app/paths'

	const items = [{ id: 'faq', url: '/faq/', label: 'Frequently asked questions', icon: FAQIcon }]
</script>

{#each items as item (item.id)}
	<div class="flex gap-2 not-first:mt-4">
		<item.icon class="size-5 text-muted-foreground" />
		<a href={resolve(item.url)} class="block">{item.label}</a>
	</div>
{/each}
