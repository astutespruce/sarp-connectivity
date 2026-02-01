<script lang="ts">
	import MenuIcon from '@lucide/svelte/icons/menu'
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'
	import SurveyIcon from '@lucide/svelte/icons/pencil-ruler'

	import { browser } from '$app/environment'
	import { resolve } from '$app/paths'
	import { page } from '$app/state'
	import { Root, Trigger, Content } from '$lib/components/ui/sheet'

	import ExploreNav from './ExploreNav.svelte'
	import LearnMoreNav from './LearnMoreNav.svelte'

	let isOpen = $state(false)

	const isActivePath = (path: string) => browser && page.url.pathname.endsWith(path)

	const items = [
		{
			id: 'prioritize',
			url: '/priority/',
			label: 'Prioritize',
			icon: PrioritizeIcon,
			description:
				'You can prioritize dams and road-related barriers based on their impact on the overall aquatic network and then download results for further analysis.'
		},
		{
			id: 'survey',
			url: '/survey/',
			label: 'Survey',
			icon: SurveyIcon,
			description:
				'You can select unsurveyed barriers within a given area of interest according to a range of different criteria, and then download the results for planning field surveys.'
		}
	]

	const close = () => {
		isOpen = false
	}
</script>

<Root bind:open={isOpen}>
	<Trigger class="lg:hidden">
		<MenuIcon class="text-white mr-2" />
	</Trigger>
	<Content side="top" class="top-0 bottom-0">
		<nav
			class="[&>a]:not-first:mt-6 leading-tight [&>a]:flex [&>a]:gap-2 [&>a]:items-center [&>a]:data-[is-active=true]:font-bold overflow-auto px-4 pt-4 pb-8"
		>
			<a href={resolve('/', {})} onclick={close}>National Aquatic Connectivity Collaborative</a>

			<div class="mt-6">
				<ExploreNav />
			</div>

			<div class="mt-6 border-t border-t-grey-2 pt-6">
				<div class="font-bold">Prioritize & survey:</div>
				<div class="mt-2">
					{#each items as item (item.id)}
						<div class="flex gap-2 not-first:mt-4">
							<item.icon class="size-5 text-muted-foreground" />
							<a
								href={resolve(item.url, {})}
								data-is-active={isActivePath(item.url).toString()}
								onclick={close}
							>
								{item.label}
							</a>
						</div>
						<p class="text-muted-foreground pl-7 leading-tight text-sm mt-2">
							{item.description}
						</p>
					{/each}
				</div>
			</div>

			<div class="mt-6 border-t border-t-grey-2 pt-6">
				<div class="flex gap-2">
					<div class="font-bold">Learn more:</div>
				</div>
				<div class="mt-2">
					<LearnMoreNav />
				</div>
			</div>
		</nav>
	</Content>
</Root>
