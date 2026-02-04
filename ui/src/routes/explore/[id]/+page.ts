import { error } from '@sveltejs/kit'

import { REGIONS, FISH_HABITAT_PARTNERSHIPS, STATES } from '$lib/config/constants'

export const load = ({ params }) => {
	const stateName = STATES[params.id.toUpperCase() as keyof typeof STATES]
	if (stateName) {
		return {
			id: params.id.toUpperCase(),
			name: stateName,
			type: 'State',
			boundaryLayer: 'State'
		}
	}

	const region = REGIONS[params.id as keyof typeof REGIONS]
	if (region) {
		return {
			id: params.id,
			name: `the ${region.name} region`,
			type: 'Region',
			boundaryLayer: 'boundary'
		}
	}

	const fhp =
		FISH_HABITAT_PARTNERSHIPS[params.id.toUpperCase() as keyof typeof FISH_HABITAT_PARTNERSHIPS]
	if (fhp) {
		return {
			id: params.id.toUpperCase(),
			name: `the ${fhp.name}`,
			type: 'FishHabitatPartnership',
			boundaryLayer: 'fhp_boundary'
		}
	}

	// if we got here, we didn't find a suitable area
	error(404, `Explore area ${params.id} not found`)
}
