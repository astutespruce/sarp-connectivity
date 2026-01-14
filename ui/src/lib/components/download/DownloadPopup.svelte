<script lang="ts">
	import DownloadIcon from '@lucide/svelte/icons/download'
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'

	import { resolve } from '$app/paths'
	import { Alert } from '$lib/components/alert'
	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import * as Dialog from '$lib/components/ui/dialog'
	import { Label } from '$lib/components/ui/label'
	import { Progress } from '$lib/components/ui/progress'

	import { CONTACT_EMAIL } from '$lib/env'
	import { cn } from '$lib/utils'
	import { barrierTypeLabels } from '$lib/config/constants'

	let {
		open = $bindable(false),
		barrierType,
		config,
		customRank,
		includeUnranked: initialIncludeUnranked,
		showOptions
	} = $props()

	const barrierTypeLabel = $derived(
		barrierTypeLabels[barrierType as keyof typeof barrierTypeLabels]
	)

	let includeUnranked = $derived(initialIncludeUnranked)

	type Status = {
		inProgress: boolean
		progress: number
		progressMessage?: string | null
		error?: string | null
	}

	let status: Status = $state({
		inProgress: false,
		progress: 0,
		progressMessage: null,
		error: null
	})

	let downloadURL: string | null = $state(null)

	const handleClose = () => (open = false)

	const handleSubmit = () => {
		// TODO: implement
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content showCloseButton={false} class="sm:max-w-2xl h-full sm:h-auto pt-4 overflow-auto">
		<Dialog.Header class="border-b-4 border-b-blue-9 pb-1">
			<Dialog.Title class="text-xl sm:text-2xl"
				>Download {customRank ? 'prioritized' : ''}
				{barrierTypeLabels[barrierType as keyof typeof barrierTypeLabels]}</Dialog.Title
			>
		</Dialog.Header>

		{#if status.error}
			<Alert title="Uh oh!" class="text-lg">
				<p class="text-base">
					We're sorry, there was an unexpected error creating your download. Please try again.
					<br /><br />
					If this happens again, please <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
				</p>
			</Alert>
		{:else if status.inProgress}
			<div class="py-8">
				<p>{status.progressMessage ? `${status.progressMessage}...` : 'Extracting data...'}</p>

				<div class="flex items-center gap-4">
					<Progress value={status.progress} max={100} />
					<div>{status.progress}%</div>
				</div>
			</div>
		{:else if downloadURL}
			<div class="mt-4">
				<p>Your browser should have automatically started downloading your file.</p>

				<div class="text-muted-foreground text-sm mt-2">
					If you don't see the download, please check to make sure that your browser did not block
					the download file. This may be shown whereever your browser indicates that it blocked
					pop-ups.
				</div>

				<p class="mt-6">
					You can also download it directly from
					<a href={downloadURL} download> here </a>.
				</p>

				<div class="text-muted-foreground text-sm">Note: this link will expire in 5 minutes.</div>
			</div>
		{:else}
			{#if showOptions && barrierType !== 'road_crossings'}
				<div class="flex gap-2 items-center">
					<Checkbox id="includeUnranked" bind:checked={includeUnranked} />
					<Label for="includeUnranked" class="font-bold text-lg"
						>Include unranked {barrierTypeLabel}?</Label
					>
				</div>
				<div class="text-muted-foreground ml-7 -mt-4 mb-2">
					This will include {barrierTypeLabel} within your selected geographic area that were not prioritized
					in the analysis. These include any
					{barrierTypeLabel} that were not located on the aquatic network
					{customRank ? ', ' : ' and'} any that have been removed
					{customRank ? ', and any that you filtered out during your prioritization' : ''}.
					{barrierType === 'small_barriers'
						? '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'
						: ''}
				</div>
			{/if}

			<div>
				By downloading these data, you agree to the
				<a href={resolve('/terms/')} target="_blank">Terms of Use</a>, which includes providing
				credit to SARP for any use of the data including publication, reports, presentations, or
				projects. Please see the <b>TERMS_OF_USE.txt</b> file in your download for the appropriate
				citation and more information.
				<br />
				<br />
				Coordinates are in WGS 1984.
			</div>
		{/if}

		<Dialog.Footer
			class={cn('justify-between sm:justify-between gap-8 border-t border-t-grey-2 pt-4 mt-4', {
				'justify-end sm:justify-end': !!downloadURL
			})}
		>
			{#if downloadURL}
				<Button onclick={handleClose}>Close</Button>
			{:else}
				<Button variant="secondary" onclick={handleClose}>Cancel</Button>

				{#if !status.error}
					<Button onclick={handleSubmit} disabled={status.inProgress}>
						{#if status.inProgress}
							<LoadingIcon class="size-5 motion-safe:animate-spin" />
						{:else}
							<DownloadIcon class="size-5" />
						{/if}

						Download</Button
					>
				{/if}
			{/if}
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
