<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader'
	import ResetIcon from '@lucide/svelte/icons/circle-x'

	import { Button } from '$lib/components/ui/button'
	import { Root as InputGroup, Input, Addon as InputAddOn } from '$lib/components/ui/input-group'

	let { value = $bindable(''), placeholder, isLoading } = $props()
</script>

<InputGroup class="border-grey-5">
	<Input bind:value {placeholder} class="focus:border-accent" />
	{#if isLoading}
		<InputAddOn align="inline-end">
			<LoadingIcon class="size-5 motion-safe:animate-spin" />
		</InputAddOn>
	{:else if value}
		<InputAddOn align="inline-end">
			<Button
				variant="ghost"
				class="p-0! h-auto rounded-full text-grey-5 hover:text-foreground"
				onclick={() => {
					value = ''
				}}
				aria-label="reset search"
			>
				<ResetIcon class="size-6" />
			</Button>
		</InputAddOn>
	{/if}
</InputGroup>
