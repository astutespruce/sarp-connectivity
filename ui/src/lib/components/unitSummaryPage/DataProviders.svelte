<script lang="ts">
	const { dataProviders = null } = $props()
</script>

{#if dataProviders && dataProviders.length > 0}
	<h2 class="text-2xl font-bold mt-24 mb-2">Data sources</h2>

	<div>
		{#each dataProviders as provider (provider.id)}
			<div
				class="flex flex-col sm:flex-row gap-8 not-first:mt-4 not-first:border-t not-first:border-t-grey-1 not-first:pt-4"
			>
				<div class="flex-auto text-lg">
					{@html provider.description}
				</div>
				{#if provider.logo}
					<div class="flex-none" style={`width:${provider.logoWidth};`}>
						<img src={provider.logo} alt={`${provider.name} logo`} />
					</div>
				{/if}
			</div>
		{/each}
	</div>

	<hr class="divider" />
{/if}
