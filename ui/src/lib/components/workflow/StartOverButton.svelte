<script lang="ts">
	import TrashIcon from '@lucide/svelte/icons/trash-2'

	import {
		Root as AlertDialog,
		Trigger,
		Content,
		Header,
		Title,
		Description,
		Footer,
		Cancel,
		Action
	} from '$lib/components/ui/alert-dialog'
	import { buttonVariants } from '$lib/components/ui/button'

	const { onStartOver } = $props()
</script>

<AlertDialog>
	<Trigger class={buttonVariants({ variant: 'destructive' })} title="Start over">
		<TrashIcon class="size-5" />
	</Trigger>
	<Content>
		<Header>
			<Title class="text-xl">Start over?</Title>
			<Description class="text-lg pb-4">You will lose all your work. Are you sure?</Description>
		</Header>
		<Footer class="justify-between sm:justify-between border-t border-t-grey-2 pt-4">
			<Cancel class={buttonVariants({ variant: 'default' })}>No</Cancel>
			<Action class={buttonVariants({ variant: 'destructive' })} onclick={onStartOver}>Yes</Action>
		</Footer>
	</Content>
</AlertDialog>
