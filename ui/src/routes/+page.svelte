<script lang="ts">
	import NACCLogo from '$lib/assets/images/nacc_logo.svg'
	import { SITE_NAME } from '$lib/env'

	import { About, AboutNACC, GetInvolved, HowToUse, Regions, Top } from '$content/home'
</script>

<svelte:head>
	<title>{SITE_NAME}</title>
</svelte:head>

<div class="container mt-8 flex justify-center">
	<img src={NACCLogo} alt="National Aquatic Connectivity Collaborative logo" class="w-lg h-48" />
</div>

<div
	class="py-4 text-white text-shadow-black mt-2"
	style="background:radial-gradient(farthest-corner circle at 50% 85% in oklch, var(--blue-8), var(--blue-9)); text-shadow: 1px 1px 3px #000;"
>
	<div class="container">
		<h1>
			<div class="leading-none text-2xl italic text-shadow-2xl">National</div>
			<div class="text-3xl md:text-5xl mt-2 text-shadow-2xl">
				Aquatic Barrier Inventory
				<br />& Prioritization Tool
			</div>
		</h1>
	</div>
</div>

<Top />

<div class="container pb-12">
	<About />
	<hr class="divider" />
	<AboutNACC />
	<hr class="divider" />
	<HowToUse />
	<hr class="divider" />
	<Regions />
	<hr class="divider" />
	<GetInvolved />
</div>
