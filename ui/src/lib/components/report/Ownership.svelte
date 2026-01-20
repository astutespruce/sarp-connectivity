<script lang="ts">
	import {
		HAZARD,
		CONDITION,
		CONSTRUCTION,
		CONSTRICTION,
		CROSSING_TYPE,
		PASSAGEFACILITY,
		ROAD_TYPE,
		OWNERTYPE,
		BARRIEROWNERTYPE,
		FERC_REGULATED,
		STATE_REGULATED,
		WATER_RIGHT,
		PURPOSE,
		PASSABILITY,
		SMALL_BARRIER_SEVERITY
	} from '$lib/config/constants'

	import { formatNumber } from '$lib/util/format'
	import { classifySARPScore } from '$lib/util/stats'
	import { isEmptyString } from '$lib/util/string'

	const {
		barrierType,
		ownertype,
		barrierownertype,
		fercregulated,
		stateregulated,
		fedregulatoryagency,
		nrcsdam,
		waterright,
		hazard,
		construction,
		purpose,
		condition,
		passagefacility,
		yearcompleted,
		height,
		width,
		roadtype,
		crossingtype,
		constriction,
		passability,
		barrierseverity,
		sarp_score,
		storagevolume,
		removed,
		costlower,
		costmean,
		costupper,
		fatality,
		protocolused
	} = $props()
</script>

<section>
	<h3>Ownership & construction information</h3>

	<div class="grid sm:grid-cols-2 sm:gap-4">
		<div class="report-entries">
			{#if barrierownertype !== null}
				<div>
					Barrier ownership type:
					{BARRIEROWNERTYPE[barrierownertype as keyof typeof BARRIEROWNERTYPE]}
				</div>
			{/if}

			{#if ownertype > 0}
				<div>
					Conservation land type: {OWNERTYPE[ownertype as keyof typeof OWNERTYPE]}
				</div>
			{/if}

			{#if fercregulated > 0}
				<div>
					Regulated by the Federal Energy Regulatory Commission:
					{FERC_REGULATED[fercregulated as keyof typeof FERC_REGULATED].toLowerCase()}
				</div>
			{/if}

			{#if stateregulated && stateregulated !== -1}
				<div>
					Regulated at the state level:
					{STATE_REGULATED[stateregulated as keyof typeof STATE_REGULATED].toLowerCase()}
				</div>
			{/if}

			{#if fedregulatoryagency}
				<div>
					Federal regulatory agency: {fedregulatoryagency}
				</div>
			{/if}

			{#if nrcsdam === 1}
				<div>This is a NRCS flood control dam</div>
			{/if}

			{#if waterright > 0}
				<div>
					Has an associated water right:
					{WATER_RIGHT[waterright as keyof typeof WATER_RIGHT].toLowerCase()}
				</div>
			{/if}

			{#if fatality > 0}
				<div>
					Number of fatalities recorded: {formatNumber(fatality)}
					<div class="text-xs text-muted-foreground leading-tight">
						based on data provided by
						<a
							href="https://krcproject.groups.et.byu.net/browse.php"
							target="_blank"
							rel="external"
						>
							Fatalities at Submerged Hydraulic Jumps
						</a>.
					</div>
				</div>
			{/if}

			{#if costmean > 0}
				<div>
					Average estimated cost of removal: ${formatNumber(costmean)}
					<br /> (${formatNumber(costlower)} - ${formatNumber(costupper)})
					<div class="text-xs text-muted-foreground mt-2 leading-tight">
						Note: costs are modeled based on dam characteristics and are a very rough estimate only;
						please use with caution. Source: Jumani et. al. (in prep).
					</div>
				</div>
			{/if}
		</div>
		<div class="report-entries sm:border-l-4 sm:border-l-grey-1 sm:pl-4">
			{#if barrierType === 'dams'}
				{#if purpose !== null && purpose >= 0}
					<div>Purpose: {PURPOSE[purpose as keyof typeof PURPOSE].toLowerCase()}</div>
				{/if}

				{#if yearcompleted > 0}
					<div>Constructed completed: {yearcompleted}</div>
				{/if}

				{#if height > 0}
					<div>Height: {height} feet</div>
				{/if}

				{#if width > 0}
					<div>Width: {width} feet</div>
				{/if}

				{#if storagevolume !== null}
					<div>
						Normal storage volume: {formatNumber(storagevolume)} acre/feet
					</div>
				{/if}

				{#if construction !== null && construction > 0}
					<div>
						Construction material: {CONSTRUCTION[
							construction as keyof typeof CONSTRUCTION
						].toLowerCase()}
					</div>
				{/if}

				{#if hazard > 0}
					<div>Hazard rating: {HAZARD[hazard as keyof typeof HAZARD].toLowerCase()}</div>
				{/if}

				{#if condition !== null && condition >= 0}
					<div>
						Structural condition: {CONDITION[condition as keyof typeof CONDITION].toLowerCase()}
					</div>
				{/if}

				{#if !removed && passability !== null}
					<div>
						<div>Passability: {PASSABILITY[passability as keyof typeof PASSABILITY]}</div>
					</div>
				{/if}

				{#if passagefacility !== null && passagefacility >= 0}
					<div>
						Passage facility type: {PASSAGEFACILITY[
							passagefacility as keyof typeof PASSAGEFACILITY
						].toLowerCase()}
					</div>
				{/if}
			{:else}
				{#if roadtype !== null && roadtype >= 0}
					<div>
						Road type: {ROAD_TYPE[roadtype as keyof typeof ROAD_TYPE]}
					</div>
				{/if}

				{#if crossingtype !== null && crossingtype >= 0}
					<div>Crossing type: {CROSSING_TYPE[crossingtype as keyof typeof CROSSING_TYPE]}</div>
				{/if}

				{#if constriction !== null && constriction >= 0}
					<div>
						Type of constriction: {CONSTRICTION[constriction as keyof typeof CONSTRICTION]}
					</div>
				{/if}

				{#if condition !== null && condition >= 0}
					<div>
						Condition: {CONDITION[condition as keyof typeof CONDITION]}
					</div>
				{/if}

				{#if !removed && barrierseverity !== null}
					<div>
						Severity: {SMALL_BARRIER_SEVERITY[
							barrierseverity as keyof typeof SMALL_BARRIER_SEVERITY
						]}
					</div>
				{/if}

				{#if !removed && sarp_score >= 0}
					<div>
						SARP Aquatic Organism Passage Score:
						{formatNumber(sarp_score, 1)} ({classifySARPScore(sarp_score)})

						{#if !isEmptyString(protocolused)}
							<div class="mt-4">
								Protocol used: {protocolused}
							</div>
						{/if}
					</div>
				{/if}

				{#if passagefacility !== null && passagefacility >= 0}
					<div>
						Passage facility type:{PASSAGEFACILITY[
							passagefacility as keyof typeof PASSAGEFACILITY
						].toLowerCase()}
					</div>
				{/if}
			{/if}
		</div>
	</div>
</section>
