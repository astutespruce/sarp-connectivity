<script lang="ts">
	import ExploreIcon from '@lucide/svelte/icons/chart-column'
	import LearnMoreIcon from '@lucide/svelte/icons/info'
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'
	import SurveyIcon from '@lucide/svelte/icons/pencil-ruler'

	import { browser } from '$app/environment'
	import { resolve } from '$app/paths'
	import { page } from '$app/state'

	import { Root, List, Item, Trigger, Link, Content } from '$lib/components/ui/navigation-menu'

	import ExploreNav from './ExploreNav.svelte'
	import LearnMoreNav from './LearnMoreNav.svelte'

	const isActivePath = (path: string) => browser && page.url.pathname.endsWith(path)
</script>

<Root class="flex-none pr-1 hidden lg:block" viewport={false}>
	<List>
		<Item>
			<Trigger><ExploreIcon class="size-5 text-white" /> Explore & Download</Trigger>
			<Content>
				<div class="w-[600px]">
					<ExploreNav />
				</div>
			</Content>
		</Item>
		<Item>
			<Link href={resolve('/priority/')} data-is-active={isActivePath('/priority/').toString()}>
				<PrioritizeIcon class="size-5 text-white" />
				Prioritize</Link
			>
		</Item>
		<Item>
			<Link href={resolve('/survey/')} data-is-active={isActivePath('/survey/').toString()}>
				<SurveyIcon class="size-5 text-white" />

				Survey</Link
			>
		</Item>

		<Item>
			<Trigger>
				<LearnMoreIcon class="size-5 text-white" />
				Learn more
			</Trigger>
			<Content>
				<div class="w-[320px] p-2">
					<LearnMoreNav />
				</div>
			</Content>
		</Item>
	</List>
</Root>
