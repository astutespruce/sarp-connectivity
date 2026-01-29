<script lang="ts">
	import CloseIcon from '@lucide/svelte/icons/chevron-down'
	import { Button } from '$lib/components/ui/button'

	import Circle from './Circle.svelte'

	const {
		title = 'Legend',
		subtitle = null,
		patches = [],
		circles = [],
		lines = [],
		footnote = null
	} = $props()

	const hasElements = $derived(
		(patches && patches.length > 0) ||
			(circles && circles.length > 0) ||
			(lines && lines.length > 0)
	)

	let isOpen = $state(false)
</script>

{#if hasElements || footnote}
	{#if isOpen}
		<div
			class="absolute right-2.5 bottom-6 text-sm px-4 pt-1 pb-2 bg-white hover:bg-white text-foreground border border-grey-5 rounded-md shadow-grey-6 shadow-lg max-w-[16rem]"
		>
			<Button
				variant="ghost"
				class="block w-full h-auto p-0! font-bold"
				onclick={() => {
					isOpen = false
				}}
			>
				<div class="flex items-center gap-2 justify-between text-lg">
					{title}
					<CloseIcon class="size-5" />
				</div>
			</Button>
			{#if subtitle}
				<div class="text-xs text-muted-foreground leading-tight mb-2">
					{subtitle}
				</div>
			{/if}

			{#if patches && patches.length > 0}
				<div>
					{#each patches as patch (patch.id)}
						<div class="not-first-of-type:mt-2">
							{#if patch.label}
								<div class="mb-1 font-bold leading-tight text-sm">
									{patch.label}
								</div>
							{/if}

							<div>
								{#each patch.entries as entry (`${entry.label}-${entry.color}`)}
									<div class="flex gap-2 group">
										<div
											class="ml-1 h-4 w-5 flex-none border-grey-5 border-t-none border-l border-r border-b group-first-of-type:rounded-t-sm group-last-of-type:rounded-b-sm group-first-of-type:border-t"
											style="background-color:{entry.color}"
										></div>
										<div class="text-xs leading-none text-foreground">{entry.label}</div>
									</div>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			{/if}

			{#if circles && circles.length > 0}
				{#if patches && patches.length > 0}
					<hr class="mt-2 mb-0 border-grey-1" />
				{/if}

				<div>
					{#each circles as circle (circle.id)}
						<div
							class="flex items-start pt-2 not-first:border-t not-first:border-t-grey-1 not-first:mt-1 gap-2"
						>
							<div class="flex flex-none items-baseline min-w-5">
								{#if circle.symbols && circle.symbols.length > 0}
									{#each circle.symbols as symbol, i (`${symbol.color}-${symbol.borderColor}-${i}`)}
										<Circle {...symbol} />
									{/each}
								{:else}
									<Circle {...circle} />
								{/if}
							</div>
							<div class="text-xs leading-none text-foreground">{circle.label}</div>
						</div>
					{/each}
				</div>
			{/if}

			{#if lines && lines.length > 0}
				{#if (patches && patches.length > 0) || (circles && circles.length > 0)}
					<hr class="mt-2 mb-0 border-grey-1" />
				{/if}

				<div>
					{#each lines as line (line.id)}
						<div
							class="flex items-start pt-2 not-first:border-t not-first:border-t-grey-1 not-first:mt-1 gap-2"
						>
							<div
								class="flex-none w-5 h-2"
								style="border-bottom-color:{line.color}; border-bottom-width:{line.lineWidth * 2 ||
									2}px; border-bottom-style:{line.lineStyle || 'solid'};"
							></div>
							<div class="text-xs leading-none text-foreground">{line.label}</div>
						</div>
					{/each}
				</div>
			{/if}

			{#if footnote}
				<div class="text-xs text-muted-foreground mt-2 pt-2 leading-tight border-t border-t-grey-1">
					{footnote}
				</div>
			{/if}
		</div>
	{:else}
		<Button
			onclick={() => {
				isOpen = true
			}}
			title="Click to show legend"
			class="absolute right-2.5 bottom-6 text-sm py-2 bg-white hover:bg-white text-foreground border-none font-bold"
			style="box-shadow:0 0 0 2px #0000001a"
		>
			Legend
		</Button>
	{/if}
{/if}
