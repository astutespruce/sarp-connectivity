<script lang="ts">
	import {
		FISH_HABITAT_PARTNERSHIPS,
		STATES,
		TNC_COLDWATER_STATUS,
		TNC_RESILIENCE,
		TU_BROOK_TROUT_PORTFOLIO
	} from '$lib/config/constants'

	const {
		brooktroutportfolio,
		cold,
		congressionaldistrict,
		ejtract,
		ejtribal,
		fishhabitatpartnership,
		nativeterritories,
		resilience
	} = $props()
</script>

<section>
	<h2>Landscape context</h2>

	<div class="report-entries">
		{#if cold}
			<div>
				Ability of the watershed to maintain cold water habitat:
				{TNC_COLDWATER_STATUS[cold as keyof typeof TNC_COLDWATER_STATUS]}
				<div class="text-xs text-muted-foreground leading-tight">
					based on The Nature Conservancy's cold water temperature score where this barrier occurs
					(TNC; March 2024).
				</div>
			</div>
		{/if}

		{#if resilience}
			<div>
				Freshwater resilience: {TNC_RESILIENCE[resilience as keyof typeof TNC_RESILIENCE]}
				<div class="text-xs text-muted-foreground leading-tight">
					based on the The Nature Conservancy&apos;s freshwater resilience category of the watershed
					where this barrier occurs (v0.44).
				</div>
			</div>
		{/if}

		{#if brooktroutportfolio}
			Eastern brook trout conservation portfolio:
			{TU_BROOK_TROUT_PORTFOLIO[brooktroutportfolio as keyof typeof TU_BROOK_TROUT_PORTFOLIO]}
			<div class="text-xs text-muted-foreground leading-tight">
				based on the
				<a
					href="https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/"
					target="_blank"
					rel="external"
				>
					brook trout conservation portfolio
				</a>
				category of the watershed where this barrier occurs, as identified by Trout Unlimited (7/4/2022).
			</div>
		{/if}

		{#if ejtract || ejtribal}
			<div>
				Climate and environmental justice:
				{ejtract ? 'within a disadvantaged census tract' : null}
				{ejtract && ejtribal ? ', ' : null}
				{ejtribal ? 'within a tribal community' : null}
			</div>
		{/if}

		{#if nativeterritories}
			<div>
				Within the following native territories: {nativeterritories}
				<div class="text-xs text-muted-foreground leading-tight">
					based on data provided by
					<a href="https://native-land.ca/"> Native Land Digital </a>.
				</div>
			</div>
		{/if}

		{#if congressionaldistrict}
			<div>
				Congressional district (119th congress):
				{STATES[congressionaldistrict.slice(0, 2) as keyof typeof STATES]} Congressional District
				{congressionaldistrict.slice(2)}
			</div>
		{/if}

		{#if fishhabitatpartnership}
			<div>
				Fish Habitat Partnerships working in this area:
				<div class="mt-1 ml-4">
					{#each fishhabitatpartnership.split(',') as fhp, i (fhp)}
						<a
							href={FISH_HABITAT_PARTNERSHIPS[fhp as keyof typeof FISH_HABITAT_PARTNERSHIPS].url}
							target="_blank"
							rel="external"
						>
							{FISH_HABITAT_PARTNERSHIPS[fhp as keyof typeof FISH_HABITAT_PARTNERSHIPS].name}
						</a>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</section>
