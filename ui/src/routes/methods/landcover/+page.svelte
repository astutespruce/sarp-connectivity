<script lang="ts">
	import { HighlightBox } from '$lib/components/elements'
	import { HeaderImage } from '$lib/components/image'
	import { SITE_NAME } from '$lib/env'

	import LowLandcoverIcon from '$lib/assets/icons/nat_landcover_low.svg'
	import HighLandcoverIcon from '$lib/assets/icons/nat_landcover_high.svg'
</script>

<svelte:head>
	<title>Network length | {SITE_NAME}</title>
</svelte:head>

<HeaderImage
	author="Loakfoma Creek, Noxubee National Wildlife Refuge, Mississippi. U.S. Fish and Wildlife Service."
	url="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/"
>
	<enhanced:img src="$lib/assets/images/6882770647_c43a945282_o.jpg" alt="" />
</HeaderImage>

<div class="page-content">
	<h1>Floodplain natural landcover</h1>
	<p class="mt-8">
		Rivers and streams that have a greater amount of natural landcover in their floodplain are more
		likely to have higher quality aquatic habitat. These areas may have more cool-water refugia for
		temperature sensitive species due to shading from the overstory, and may have fewer water
		quality issues. In contrast, rivers that have less natural landcover are more likely to be
		altered and have impaired water quality.
	</p>

	<div class="mt-8 grid sm:grid-cols-2 gap-8">
		<HighlightBox title="Low network length" icon={LowLandcoverIcon}>
			Barriers with less natural landcover are less likely to contribute high quality habitat for
			aquatic species if removed.
		</HighlightBox>

		<HighlightBox title="High network length" icon={HighLandcoverIcon}>
			Barriers with aquatic networks that have more natural landcover are more likely to contribute
			higher quality habitat if they are removed.
		</HighlightBox>
	</div>

	<h2 class="mt-12">Methods</h2>
	<ol class="mt-2">
		<li>
			Floodplains are delineated using data derived from FATHOM Inc, which has modeled 30 by 30
			meter 100 year floodplain boundaries. For more information visit:
			<br />
			<a
				href="https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf"
				target="_blank"
				rel="external"
			>
				https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf
			</a>.
		</li>
		<li>
			Natural landcover is derived from the USDA National Landcover Database (NLCD) 2016 30 by 30
			meter landcover raster dataset. For more information see:
			<a href="https://www.mrlc.gov/data/nlcd-2016-land-cover-conus" target="_blank" rel="external">
				https://www.mrlc.gov/data/nlcd-2016-land-cover-conus
			</a>.
		</li>
		<li>
			Natural landcover is extracted from the overall NLCD dataset and clipped to the floodplain
			area for analysis.
		</li>
		<li>
			The contributing watershed (catchment) of each stream and river reach is extracted from the
			NHDPlus dataset.
		</li>
		<li>
			The total amount of natural landcover within the catchment area as well as the floodplain area
			of that catchment area are tallied for each functional network.
		</li>
		<li>
			Floodplain natural landcover is measured from the overall percent of natural landcover
			throughout the entire functional network.
		</li>
	</ol>
</div>
