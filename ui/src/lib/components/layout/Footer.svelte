<script lang="ts">
	import { NACC_HOME_URL } from '$lib/env'
	import { dataVersion, dataDate } from '$lib/config/constants'
</script>

<footer
	class="flex-none leading-none bg-blue-9 md:flex items-center justify-between px-2 py-1 text-[0.8rem] gap-6 print:hidden"
>
	<div class="flex-none flex gap-2 [&>a+a]:border-l [&>a+a]:border-grey-4 [&>a+a]:pl-2">
		<a href={NACC_HOME_URL} class="block text-white no-underline hover:underline">NACC Home</a>
		<a
			href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
			class="block text-white no-underline hover:underline"
			>Southeast Aquatic Resources Partnership</a
		>
		<a
			href="https://southeastaquatics.net/about/contact-us"
			class="text-white no-underline hover:underline"
			>Contact Us
		</a>
	</div>
	<div class="flex-auto text-white text-center hidden md:block">
		Data version: {dataVersion} ({dataDate})
	</div>
	<div class="flex-none text-white hidden md:block">
		Created by
		<a href="https://astutespruce.com" class="text-white no-underline hover:underline"
			>Astute Spruce, LLC</a
		>
	</div>
</footer>
