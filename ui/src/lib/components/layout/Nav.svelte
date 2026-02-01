<script lang="ts">
	import PrioritizeIcon from '@lucide/svelte/icons/search-check'
	import SurveyIcon from '@lucide/svelte/icons/pencil-ruler'

	import { resolve } from '$app/paths'
	import { Root, List, Item, Trigger, Link, Content } from '$lib/components/ui/navigation-menu'

	import ExploreNav from './ExploreNav.svelte'
	import LearnMoreNav from './LearnMoreNav.svelte'
</script>

<Root class="flex-none hidden lg:block" viewport={false}>
	<List>
		<Item>
			<Trigger>
				<!-- <ExploreIcon class="size-5 text-white" />  -->
				Explore & Download
			</Trigger>
			<Content>
				<div class="w-[600px]">
					<ExploreNav />
				</div>
			</Content>
		</Item>
		<Item>
			<Link href={resolve('/priority/', {})}>
				<PrioritizeIcon class="size-5 text-white" />
				Prioritize</Link
			>
		</Item>
		<Item>
			<Link href={resolve('/survey/', {})}>
				<SurveyIcon class="size-5 text-white" />

				Survey</Link
			>
		</Item>

		<Item>
			<Trigger>Learn more</Trigger>
			<Content>
				<div class="w-[320px] p-2">
					<LearnMoreNav />
				</div>
			</Content>
		</Item>
	</List>
</Root>
