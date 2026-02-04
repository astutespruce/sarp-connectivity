<script lang="ts">
	import WarningIcon from '@lucide/svelte/icons/triangle-alert'

	import SearchField from '$lib/components/search/SearchField.svelte'
	import { Button } from '$lib/components/ui/button'
	import { parseLatLon } from './parser'

	let { value = $bindable(''), ref = $bindable(null), onSubmit } = $props()

	let latitude: number | null = $state(null)
	let longitude: number | null = $state(null)
	let hasCoordinates = $state(false)
	let isValid = $state(true)
	let invalidReason: string | null = $state(null)

	$effect(() => {
		if (!value) {
			reset()
			return
		}

		const {
			lat = null,
			lon = null,
			isValid: nextIsValid,
			invalidReason: nextInvalidReason = null
		} = parseLatLon(value)

		latitude = lat
		longitude = lon
		isValid = nextIsValid
		hasCoordinates = true
		invalidReason = nextInvalidReason
	})

	const handleSubmit = () => {
		if (!(isValid && hasCoordinates)) {
			return
		}

		console.log('submit coords')

		onSubmit({ latitude, longitude })
	}

	const reset = () => {
		value = ''
		latitude = null
		longitude = null
		hasCoordinates = false
		isValid = true
		invalidReason = null
	}

	const handleKeyDown = ({ key }: KeyboardEvent) => {
		if (key === 'Enter') {
			handleSubmit()
		} else if (key === 'Escape') {
			reset()
		}
	}
</script>

<div class="flex gap-2 items-center">
	<SearchField
		bind:value
		bind:ref
		placeholder="Enter latitude, longitude"
		invalid={!isValid}
		onkeydown={handleKeyDown}
	/>

	<Button
		disabled={!(isValid && hasCoordinates)}
		onclick={handleSubmit}
		class="flex-none text-sm px-2"
	>
		Go
	</Button>
</div>

<div class="text-xs text-muted-foreground">
	<div class="mt-2 pb-2">
		Use decimal degrees or degrees° minutes' seconds" in latitude, longitude order.

		{#if !isValid}
			<div class="mt-2 leading-tight">
				<div class="flex items-center gap-1 text-destructive">
					<WarningIcon class="size-4" />
					<div class="font-bold">The value you entered is not valid.</div>
				</div>
				{#if invalidReason}
					<div class="mt-1 text-destructive">
						{invalidReason}
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
