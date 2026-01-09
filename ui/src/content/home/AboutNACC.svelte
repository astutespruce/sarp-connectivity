<script lang="ts">
	import { resolve } from '$app/paths'

	import { NACC_HOME_URL } from '$lib/env'
	import DamIcon from '$lib/assets/icons/dam.svg'
	import PrioritizeIcon from '$lib/assets/icons/prioritize.svg'
	import TeamIcon from '$lib/assets/icons/team.svg'
</script>

<h2 class="text-2xl sm:text-3xl">National Aquatic Connectivity Collaborative</h2>

<div class="text-xl sm:text-2xl mt-2">
	Enhancing aquatic connectivity by empowering people with actionable data:
</div>

<div
	class="grid sm:grid-cols-3 gap-4 mt-6 [&>div]:bg-blue-1/50 [&>div]:rounded-2xl [&>div]:p-4 [&_h3]:border-b-4 [&_h3]:border-b-white [&_h3]:pb-2 [&_h3]:mb-2 [&_h3]:text-xl sm:[&_h3]:text-2xl [&_h3]:flex [&_h3]:items-center [&_h3]:gap-2 [&_img]:size-10 sm:[&_img]:size-16"
>
	<div>
		<h3>
			<img src={DamIcon} alt="inventory icon" />
			Inventory
		</h3>
		<div>
			The aquatic barrier inventory is the foundation for identifying and prioritizing aquatic
			connectivity projects with partners. It provides essential information about the location,
			status, and characteristics of potential aquatic barriers.
			<br />
			<br />
			<a href={`${NACC_HOME_URL}/inventory/`} target="_blank" rel="external">
				Learn more about the inventory
			</a>.
		</div>
	</div>

	<div>
		<h3>
			<img src={PrioritizeIcon} alt="prioritization icon" />

			Prioritization
		</h3>
		<div>
			In order to maximize partner effort and return on investment, aquatic barriers are prioritized
			based on their contribution to the aquatic network if removed. Quantitative metrics provide
			actionable information to assist barrier removal projects.
			<br />
			<br />
			<a href={resolve('/scoring_methods')}>Read more about the methods here...</a>
		</div>
	</div>

	<div>
		<h3>
			<img src={TeamIcon} alt="teams icon" />
			Teams
		</h3>
		<div>
			Aquatic connectivity teams make barrier removal projects a reality. By combining effort across
			organizations and jurisdictions, partners work together to identify, prioritize, and implement
			barrier removal projects.
			<br />
			<br />
			<a href={`${NACC_HOME_URL}/teams/`} target="_blank" rel="external">
				Learn more about Aquatic Connectivity Teams
			</a>.
		</div>
	</div>
</div>

<p class="mt-6">
	<a href={NACC_HOME_URL} target="_blank" rel="external">
		Learn more about the National Aquatic Connectivity Collabrative
	</a>
	and explore
	<a href={`${NACC_HOME_URL}/faq/`} target="_blank" rel="external">Frequently Asked Questions</a> about
	it.
</p>
