<script lang="ts">
	import { HeaderImage } from '$lib/components/image'
	import SARPLogo from '$lib/assets/images/sarp_logo_highres.png'
</script>

<HeaderImage author="David Kovalenko" url="https://unsplash.com/photos/qYMa2-P-U0M">
	<enhanced:img src="$lib/assets/images/david-kovalenko-qYMa2-P-U0M-unsplash.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Terms of use</h1>

	<p class="mt-12">
		The data made available through this tool represent substantial effort and investment from the
		<a
			href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act"
			target="_blank"
			rel="external"
		>
			Southeast Aquatic Resources Partnership
		</a>
		(SARP) and SARP's funders, partners, and data contributors.
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
			you will credit SARP in anything produced using the data provided by this tool including, but
			not limited to, peer-reviewed publications via acknowledgments, presentations and reports via
			logo placement, and newsletter or interview articles via logo and/or verbal credit.
		</li>
	</ol>

	<p class="mt-12">In order to download data:</p>

	<ol class="mt-2">
		<li>you will provide your name, email address, and other information to SARP.</li>
		<li>
			you agree to be contacted by SARP staff if a data issue is discovered in the data made
			available through this tool. However, SARP staff are not obligated to notify you of any data
			issues.
		</li>
		<li>
			you agree to be contacted by SARP staff for information about how you are using these data, in
			order to help SARP staff report statistics to SARP&apos;s funders and partners, who have
			helped make these data available to you.
		</li>
		<li>
			you agree to be contacted by SARP staff upon data updates to ensure you are working with the
			most accurate data available. However, SARP staff are not obligated to notify you of data
			updates.
		</li>
	</ol>

	<div class="grid sm:grid-cols-[1fr_2fr] gap-8 mt-12">
		<a href={SARPLogo} target="_blank" rel="external" aria-label="SARP logo">
			<img src={SARPLogo} alt="SARP logo" class="w-lg" />
		</a>
		<div class="flex items-center">
			<div class="text-muted-foreground">
				A high resolution logo can be obtained by clicking on the logo to the left to open it in a
				new window.
			</div>
		</div>
	</div>
</div>
