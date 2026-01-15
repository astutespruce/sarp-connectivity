<script lang="ts">
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link'
	import { CONTACT_EMAIL } from '$lib/env'
	import { cn } from '$lib/utils'
	import TeamIcon from '$lib/assets/icons/team.svg'

	const { team = null, teams = null } = $props()
</script>

{#snippet TeamListItem(team: { name: string; url?: string })}
	<div class="flex">
		{#if team.url}
			<a href={team.url} target="_blank" rel="external"
				>{team.name}

				<ExternalLinkIcon class="size-5 text-link/40 inline ml-1 -mt-1" />
			</a>
		{:else}
			{team.name}
		{/if}
	</div>
{/snippet}

<h2 class="text-2xl font-bold mt-24">You can help!</h2>

<div
	class={cn({
		'grid sm:grid-cols-[2fr_1fr] gap-8': team || (teams && teams.length > 0),
		'sm:grid-cols-2': teams && teams.length >= 6
	})}
>
	<p class="mt-2">
		You can help improve the inventory You can help improve the inventory by sharing data, assisting
		with field reconnaissance to evaluate the impact of aquatic barriers, or even by reporting
		issues with the inventory data in this tool. To join an aquatic connectivity team click
		<a
			href="https://www.americanrivers.org/aquatic-connectivity-groups/"
			target="_blank"
			rel="external"
		>
			here
		</a>.
		<br />
		<br />
		<a href={`mailto:${CONTACT_EMAIL}`}>Contact us</a> to learn more about how you can help improve aquatic
		connectivity.
	</p>

	{#if team}
		<div class="p-4 bg-blue-1/50 rounded-md">
			<div class="flex gap-4 font-bold text-lg leading-tight">
				<img src={TeamIcon} alt="" aria-hidden="true" class="size-18" />
				This state has an active Aquatic Connectivity Team
			</div>
			{@render TeamListItem(team)}
		</div>
	{:else if teams && teams.length > 0}
		<div>
			<div class="font-bold text-lg leading-tight">Aquatic connectivity teams:</div>

			<ul class="list-disc list-outside pl-4 mt-2">
				{#each teams as team (team.name)}
					<li class="not-first:mt-2">
						{@render TeamListItem(team)}
					</li>
				{/each}
			</ul>
		</div>
	{/if}
</div>
