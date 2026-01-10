<script lang="ts">
	import { cn } from '$lib/utils'

	const { title, icon = null, children, class: className = '' } = $props()
</script>

<div class={cn('bg-blue-1/50 p-4 rounded-2xl', className)}>
	<div class="flex gap-2 items-center border-b-4 border-b-white pb-2">
		{#if icon}
			<img src={icon} alt="" aria-hidden="true" class="size-10 sm:size-16" />
		{/if}

		<div class="font-bold text-xl sm:text-2xl">{title}</div>
	</div>
	<div class="mt-2">
		{@render children()}
	</div>
</div>
