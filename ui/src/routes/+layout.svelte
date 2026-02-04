<script lang="ts">
	import { onMount } from 'svelte'
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'

	import { browser } from '$app/environment'
	import { GOOGLE_ANALYTICS_ID } from '$lib/env'
	import { afterNavigate } from '$app/navigation'

	import { Footer, Header } from '$lib/components/layout'

	import '../app.css'
	import { SITE_NAME } from '$lib/env'

	let { children } = $props()

	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				staleTime: 10 * 60 * 1000 // 10 minutes
			}
		}
	})

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

	const handleGTAGLoad = () => {
		if (!window.dataLayer) {
			console.warn('GTAG not properly initialized')
			return
		}

		console.debug('setting up GTAG')

		function gtag() {
			dataLayer.push(arguments)
		}

		gtag('js', new Date())
		gtag('config', GOOGLE_ANALYTICS_ID)
		window.gtag = gtag
	}
</script>

<svelte:head>
	{#if browser && GOOGLE_ANALYTICS_ID}
		<script
			async
			src={`https://www.googletagmanager.com/gtag/js?id=${GOOGLE_ANALYTICS_ID}`}
			onload={handleGTAGLoad}
		></script>
	{/if}
</svelte:head>

<QueryClientProvider client={queryClient}>
	<div class="flex flex-col h-full w-full overflow-none print:h-auto">
		<Header />

		<main bind:this={contentNode} class="h-full w-full flex-auto overflow-auto print:h-auto">
			{@render children()}
		</main>
		<Footer />
	</div>
</QueryClientProvider>
