<script lang="ts">
	import { cn } from '$lib/utils'

	const { children, allowScroll = false } = $props()
</script>

<div
	class={cn(
		'flex flex-col flex-none border-r border-r-grey-8 h-full overflow-x-hidden overflow-y-hidden',
		{
			'overflow-y-auto': allowScroll
		}
	)}
>
	{@render children()}
</div>
