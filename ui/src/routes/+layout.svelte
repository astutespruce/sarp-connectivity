<script lang="ts">
	import { afterNavigate } from '$app/navigation'

	import { Analytics, Footer, Header } from '$lib/components/layout'

	import '../app.css'

	let { children } = $props()

	// reset scroll of content node on navigate
	let contentNode: Element | null = $state(null)
	afterNavigate(() => {
		if (contentNode) {
			contentNode.scrollTop = 0
		}
	})
</script>

<Analytics />

<div class="flex flex-col h-full w-full overflow-none">
	<Header />

	<div bind:this={contentNode} class="h-full w-full flex-auto overflow-auto">
		{@render children()}
	</div>
	<Footer />
</div>
