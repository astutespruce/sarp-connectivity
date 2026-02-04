<script lang="ts">
	import { CONTACT_EMAIL } from '$lib/env'
	import { HeaderImage } from '$lib/components/image'
	import NACCLogo from '$lib/assets/images/nacc_logo.svg'
</script>

<HeaderImage author="David Kovalenko" url="https://unsplash.com/photos/qYMa2-P-U0M">
	<enhanced:img src="$lib/assets/images/david-kovalenko-qYMa2-P-U0M-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Terms of use</h1>

	<p class="mt-12">
		The data made available through this tool represent substantial effort and investment from the
		<a href="https://aquaticbarriers.org" target="_blank" rel="external"
			>National Aquatic Connectivity Collaborative</a
		>
		(NACC),
		<a
			href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
			target="_blank"
			rel="external"
		>
			Southeast Aquatic Resources Partnership
		</a>
		(SARP),
		<a href="https://www.fishhabitat.org/" target="_blank" rel="external"
			>National Fish Habitat Partnership</a
		>
		(NFHP), and their funders, partners, and data contributors.
		<br />
		<br />
		<br />
		This project was supported in part by grants from the
		<a href="https://www.fws.gov/fisheries/fish-passage.html" target="_blank" rel="external">
			U.S. Fish and Wildlife Service Fish Passage Program
		</a>,
		<a href="https://www.americanrivers.org/" target="_blank" rel="external"> American Rivers </a>,
		the
		<a href="https://www.fs.usda.gov/" target="_blank" rel="external">
			U.S. Department of Agriculture, Forest Service
		</a>, the
		<a href="https://www.nfwf.org/" target="_blank" rel="external">
			National Fish and Wildlife Foundation
		</a>,
		<a href="https://www.nature.org/" target="_blank" rel="external"> The Nature Conservancy </a>,
		<a href="https://www.tu.org/" target="_blank" rel="external">Trout Unlimited</a>, the
		<a href="https://gcpolcc.org/" target="_blank" rel="external">
			Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
		</a>, and the
		<a
			href="https://myfwc.com/conservation/special-initiatives/swap/grant/"
			target="_blank"
			rel="external"
		>
			Florida State Wildlife Grants Program
		</a>.

		<br /><br /><br />
		By using this tool, you agree to the following:
	</p>

	<ol class="mt-2">
		<li>
			you will credit NACC, SARP, and NFHP in anything produced using the data provided by this tool
			including, but not limited to, peer-reviewed publications via acknowledgments, presentations
			and reports via logo placement, and newsletter or interview articles via logo and/or verbal
			credit.
		</li>
	</ol>

	<p class="mt-12">In order to download data:</p>

	<ol class="mt-2">
		<li>you will provide your name, email address, and other information to NACC.</li>
		<li>
			you agree to be contacted by NACC staff if a data issue is discovered in the data made
			available through this tool. However, NACC staff are not obligated to notify you of any data
			issues.
		</li>
		<li>
			you agree to be contacted by NACC staff for information about how you are using these data, in
			order to help NACC staff report statistics to NACC's funders and partners, who have helped
			make these data available to you.
		</li>
		<li>
			you agree to be contacted by NACC staff upon data updates to ensure you are working with the
			most accurate data available. However, NACC staff are not obligated to notify you of data
			updates.
		</li>
	</ol>

	<div class="grid sm:grid-cols-[1fr_2fr] gap-8 mt-12">
		<a href={NACCLogo} target="_blank" rel="external" aria-label="NACC logo">
			<img src={NACCLogo} alt="NACC logo" class="w-lg" />
		</a>
		<div class="flex items-center">
			<div class="text-muted-foreground">
				A downloadable version of the logo can be obtained by clicking on the logo to the left to
				open it in a new browser tab or window. If you need it in a different format, please use an
				image conversion tool or <a href={`mailto:${CONTACT_EMAIL}`}>contact us</a>.
			</div>
		</div>
	</div>
</div>
