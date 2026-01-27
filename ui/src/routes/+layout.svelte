<script lang="ts">
	import { onMount } from 'svelte'
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'

	import { afterNavigate } from '$app/navigation'

	import { Analytics, Footer, Header } from '$lib/components/layout'

	import '../app.css'
	import { SITE_NAME } from '$lib/env'

	let { children } = $props()

	const queryClient = new QueryClient()

	// reset scroll of content node on navigate
	let contentNode: Element | null = $state(null)
	afterNavigate(() => {
		if (contentNode) {
			contentNode.scrollTop = 0
		}
	})

	onMount(() => {
		// set site name for print views (note the nested quotes required for CSS)
		document.documentElement.style.setProperty(
			'--print-footer',
			`"${SITE_NAME} (${new Date().toLocaleDateString()})"`
		)
	})
</script>

<Analytics />

<QueryClientProvider client={queryClient}>
	<div class="flex flex-col h-full w-full overflow-none print:h-auto">
		<Header />

		<main bind:this={contentNode} class="h-full w-full flex-auto overflow-auto print:h-auto">
			{@render children()}
		</main>
		<Footer />
	</div>
</QueryClientProvider>
