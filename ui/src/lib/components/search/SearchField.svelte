<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader'
	import ResetIcon from '@lucide/svelte/icons/x'
	import SearchIcon from '@lucide/svelte/icons/search'

	import { Button } from '$lib/components/ui/button'
	import { Root as InputGroup, Input, Addon as InputAddOn } from '$lib/components/ui/input-group'

	let {
		value = $bindable(''),
		isLoading = false,
		invalid = false,
		ref = $bindable(),
		...rest
	} = $props()
</script>

<InputGroup class="border-grey-5">
	<InputAddOn align="inline-start">
		<SearchIcon class="size-5" />
	</InputAddOn>

	<Input bind:value bind:ref class="focus:border-accent" aria-invalid={invalid} {...rest} />

	{#if isLoading}
		<InputAddOn align="inline-end">
			<LoadingIcon class="size-5 motion-safe:animate-spin" />
		</InputAddOn>
	{:else if value}
		<InputAddOn align="inline-end">
			<Button
				variant="ghost"
				class="p-0! mr-1 h-auto text-grey-5 hover:text-foreground"
				onclick={() => {
					value = ''
				}}
				aria-label="reset search"
			>
				<ResetIcon class="size-5" />
			</Button>
		</InputAddOn>
	{/if}
</InputGroup>
