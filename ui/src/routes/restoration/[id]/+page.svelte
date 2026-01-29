<script lang="ts">
	import LoadingIcon from '@lucide/svelte/icons/loader-circle'
	import { createQuery } from '@tanstack/svelte-query'

	import { fetchUnitDetails } from '$lib/api'
	import { RestorationPage } from '$lib/components/restoration'
	import { NotFoundPage, PageLoadingError } from '$lib/components/layout'

	const { data } = $props()

	const dataRequest = createQuery(() => ({
		queryKey: [data.type, data.id],
		queryFn: async () => fetchUnitDetails(data.type, data.id)
	}))
</script>

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
	{#if dataRequest.data}
		<RestorationPage type={data.type} data={{ ...dataRequest.data, ...data }} />
	{:else}
		<NotFoundPage />
	{/if}
{/if}
