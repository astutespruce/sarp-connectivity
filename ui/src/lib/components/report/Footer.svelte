<script lang="ts">
	import NACCLogo from '$lib/assets/images/nacc_logo.svg'
	import { dataVersion } from '$lib/config/constants'
	import { CONTACT_EMAIL, SITE_URL, NACC_HOME_URL } from '$lib/env'

	const { barrierType, sarpid } = $props()
</script>

<section>
	<h2>Contact us</h2>

	<div class="text-sm">
		If you see an issue with the details for this barrier, please
		<a
			href={`mailto:${CONTACT_EMAIL}?subject=Problem with National Aquatic Barrier Inventory for ${
				barrierType === 'dams' ? 'dam' : 'road/stream crossing'
			}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the Inventory for this barrier:`}
		>
			let us know!
		</a>
		<br />
		<br />
		If you would like more information about this barrier or the aquatic connectivity analysis results
		presented above, please
		<a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
	</div>

	<hr />

	<div class="grid sm:grid-cols-[1fr_180px] gap-8 mt-12">
		<div class="text-xs">
			This report was created on {new Date().toLocaleDateString()} using the
			<a href={SITE_URL} target="_blank" rel="external">
				National Aquatic Barrier Inventory & Prioritization Tool
			</a>, part of the
			<a href={NACC_HOME_URL} target="_blank" rel="external">
				National Aquatic Connectivity Collaborative
			</a>
			(NACC), led by the
			<a
				href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
				target="_blank"
				rel="external"
			>
				Southeast Aquatic Resources Partnership
			</a>
			and the
			<a href="https://www.fishhabitat.org/" target="_blank" rel="external">
				National Fish Habitat Partnership
			</a>.
		</div>

		<img src={NACCLogo} alt="NACC logo" class="block w-full h-auto" />
	</div>
	<div class="mt-4 text-xs">
		This project is made possible by funding from the
		<a href="https://www.fws.gov/program/national-fish-passage" target="_blank" rel="external">
			U.S. Fish and Wildlife Service
		</a>,
		<a href="https://www.americanrivers.org/" target="_blank" rel="external"> American Rivers </a>,
		the
		<a href="https://www.nfwf.org/" target="_blank" rel="external">
			National Fish and Wildlife Foundation
		</a>,
		<a href="https://www.fs.usda.gov/" target="_blank" rel="external">
			U.S. Department of Agriculture, Forest Service
		</a>,
		<a href="https://www.nature.org/" target="_blank" rel="external"> The Nature Conservancy </a>,
		<a href="https://www.tu.org/" target="_blank" rel="external">Trout Unlimited</a>, and state
		wildlife grant funding from Florida and Texas. This effort would not be possible without the
		collaboration of NACC partners from numerous state, federal, and non profit organizations.
	</div>
</section>
