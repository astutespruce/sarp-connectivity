<script lang="ts">
	import ArrowIcon from '@lucide/svelte/icons/corner-down-right'
	import FAQIcon from '@lucide/svelte/icons/circle-question-mark'
	import HabitatIcon from '@lucide/svelte/icons/fish'
	import NetworkMethodsIcon from '@lucide/svelte/icons/waypoints'
	import ScoringIcon from '@lucide/svelte/icons/search-alert'
	import SGCNIcon from '@lucide/svelte/icons/scroll-text'

	import { resolve } from '$app/paths'

	const items = [
		{ id: 'faq', url: '/faq/', label: 'Frequently asked questions', icon: FAQIcon },
		{
			id: 'network',
			url: '/methods/network/',
			label: 'Network analysis methods',
			icon: NetworkMethodsIcon,
			children: [
				{ id: 'length', url: '/methods/length/', label: 'Network length' },
				{ id: 'complexity', url: '/methods/complexity/', label: 'Network complexity' },
				{ id: 'unaltered', url: '/methods/unaltered/', label: 'Channel alteration' },
				{ id: 'landcover', url: '/methods/landcover', label: 'Floodplain natural landcover' }
			]
		},
		{
			id: 'sgcn',
			url: '/methods/sgcn/',
			label: 'Listed species and Species of Greatest Conservation Need',
			icon: SGCNIcon
		},
		{
			id: 'habitat',
			url: '/methods/habitat/',
			label: 'Aquatic species habitat network methods',
			icon: HabitatIcon
		},
		{
			id: 'scoring',
			url: '/methods/scoring/',
			label: 'How are barriers prioritized?',
			icon: ScoringIcon
		}
	]
</script>

{#each items as item, i (item.id)}
	<div>
		{#if i > 0}
			<hr class="border-t-0 my-4 border-t-grey-2 sm:border-t" />
		{/if}
		<div class="flex gap-2">
			<item.icon class="size-5 text-muted-foreground flex-none" />
			<a href={resolve(item.url, {})} class="block flex-auto leading-snug">{item.label}</a>
		</div>
		{#if item.children}
			<div class="mb-6 mt-1">
				{#each item.children as child (child.id)}
					<div class="flex gap-2 not-first:mt-2 ml-7">
						<ArrowIcon class="size-4 text-muted-foreground/50 flex-none" aria-hidden="true" />
						<a href={resolve(child.url, {})} class="block flex-auto">{child.label}</a>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/each}
