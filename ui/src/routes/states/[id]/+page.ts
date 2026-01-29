import { error } from '@sveltejs/kit'

import { REGIONS, STATES, CONNECTIVITY_TEAMS, STATE_DATA_PROVIDERS } from '$lib/config/constants.js'

import type { EntryGenerator } from './$types'

export const load = async ({ params }) => {
	const name = STATES[params.id as keyof typeof STATES]

	if (!name) {
		error(404, `State ${params.id} not found`)
	}

	const regions = Object.entries(REGIONS)
		.map(([id, rest]) => ({ id, ...rest }))
		.filter(({ states }) => states.indexOf(params.id) !== -1)
	const team = CONNECTIVITY_TEAMS[params.id as keyof typeof CONNECTIVITY_TEAMS]

	let dataProviders = STATE_DATA_PROVIDERS[params.id as keyof typeof STATE_DATA_PROVIDERS] || []

	const dataProviderFilenames = new Set(
		Object.values(dataProviders)
			.filter(({ logo }) => logo)
			.map(({ logo }) => logo)
	)
	if (dataProviderFilenames.size > 0) {
		const logos = Object.fromEntries(
			Object.entries(
				import.meta.glob('$lib/assets/images/*_logo.*', {
					eager: true,
					import: 'default'
				})
			)
				.map(([path, img]) => [path.split('/').slice(-1)[0], img])
				.filter(([filename]) => dataProviderFilenames.has(filename as string))
		)

		dataProviders = dataProviders.map(({ logo, ...rest }) => ({ ...rest, logo: logos[logo] }))
	}

	const { default: map } = await import(
		`$lib/assets/images/maps/states/${params.id}.png?as=picture&w=500&format=avif;webp;png`
	)

	return {
		name,
		regions,
		team,
		dataProviders,
		map
	}
}

export const entries: EntryGenerator = () => Object.keys(STATES).map((id) => ({ id }))
