<script lang="ts">
	import { resolve } from '$app/paths'
	import { NACC_HOME_URL } from '$lib/env'

	import Logo from '$lib/assets/images/nacc_logo_white.svg'
	import Nav from './Nav.svelte'
	import MobileNav from './MobileNav.svelte'
</script>

<header
	class="flex-none leading-none bg-blue-8 flex gap-6 items-center justify-between p-1 border-b-4 border-blue-9 print:hidden"
>
	<div class="flex-auto flex gap-3 items-center">
		<div class="flex-none">
			<a href={NACC_HOME_URL} target="_blank" rel="external" class="no-underline">
				<img src={Logo} class="h-10 my-px" alt="National Aquatic Connectivity Collaborative logo" />
			</a>
		</div>
		<div>
			<a href={resolve('/')} class=" no-underline text-white">
				<div class="hidden md:block text-xl leading-tight">
					Aquatic Barrier Inventory <br />& Prioritization Tool
				</div>
				<div class="md:hidden text-lg leading-none">Aquatic Barrier Tool</div>
			</a>
		</div>
	</div>
	<Nav />
	<MobileNav />
</header>
