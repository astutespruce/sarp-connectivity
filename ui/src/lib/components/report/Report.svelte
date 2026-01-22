<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import { createQuery } from '@tanstack/svelte-query'

	import { fetchBarrierDetails } from '$lib/api'
	import { SITE_NAME } from '$lib/env'
	import { NotFoundPage, PageLoadingError } from '$lib/components/layout'

	import ReportLayout from './ReportLayout.svelte'

	const { sarpid, networkType } = $props()

	const dataRequest = createQuery(() => ({
		queryKey: ['report', networkType, sarpid],
		queryFn: async () => fetchBarrierDetails(networkType, sarpid)
	}))

	const data = $derived(dataRequest.data)

	const pageTitle = $derived(
		data && data.name ? `Barrier report for ${data.name}` : 'Barrier report'
	)
</script>

<svelte:head>
	<title>{pageTitle} | {SITE_NAME}</title>
</svelte:head>

{#if dataRequest.error}
	<div class="container">
		<PageLoadingError />
	</div>
{:else if dataRequest.isLoading}
	<div class="container">
		<div class="flex justify-center items-center gap-4 text-xl text-muted-foreground mt-16">
			<LoadingIcon class="size-12 motion-safe:animate-spin" />
			Loading...
		</div>
	</div>
{:else if dataRequest.isSuccess}
	{#if data}
		<ReportLayout {networkType} {data} />
	{:else}
		<NotFoundPage />
	{/if}
{/if}
