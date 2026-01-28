<script lang="ts">
	import QuestionIcon from '@lucide/svelte/icons/circle-question-mark'
	import * as Tooltip from '$lib/components/ui/tooltip'
	import * as Dialog from '$lib/components/ui/dialog'

	const { label = null, title, children, 'aria-label': ariaLabel = null } = $props()
</script>

<!-- only show tooltip on desktop version -->
<div class="hidden md:block">
	<Tooltip.Provider delayDuration={0}>
		<Tooltip.Root disableHoverableContent disableCloseOnTriggerClick>
			<Tooltip.Trigger
				aria-label={ariaLabel}
				class="text-left  underline underline-offset-4 decoration-dashed decoration-2 decoration-link/50 cursor-pointer hover:decoration-link/75 hover:text-link"
			>
				{label || title}
			</Tooltip.Trigger>
			<Tooltip.Content side="right" sideOffset={2} class="pt-2 pb-4 px-3 max-w-md">
				<h4 class="text-base border-b border-b-grey-2 pb-1">
					{title}
				</h4>
				<div class="text-sm leading-snug mt-2">
					{@render children()}
				</div>
			</Tooltip.Content>
		</Tooltip.Root>
	</Tooltip.Provider>
</div>

<!-- mobile is a dialog instead -->
<div class="block md:hidden">
	<Dialog.Root>
		<Dialog.Trigger
			aria-label={ariaLabel}
			class="text-left  underline underline-offset-4 decoration-dashed decoration-2 decoration-link/50 cursor-pointer hover:decoration-link/75 hover:text-link"
		>
			{label || title}
		</Dialog.Trigger>
		<Dialog.Content class="z-10000">
			<Dialog.Header class="border-b pb-2 border-b-grey-3">
				<Dialog.Title class="text-left text-2xl">{title}</Dialog.Title>
			</Dialog.Header>
			<div class="text-md">
				{@render children()}
			</div>
		</Dialog.Content>
	</Dialog.Root>
</div>
