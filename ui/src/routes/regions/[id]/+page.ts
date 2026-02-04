import { error } from '@sveltejs/kit'

import { REGIONS, CONNECTIVITY_TEAMS, STATE_DATA_PROVIDERS } from '$lib/config/constants.js'

import type { EntryGenerator } from './$types'

type Region = {
	name: string
	states: string[]
	inDevelopment?: boolean
}

type DataProvider = {
	id: string
	description: string
	logo?: string
	logoWidth?: string
}

type ConnectivityTeamKey = keyof typeof CONNECTIVITY_TEAMS

export const load = async ({ params }) => {
	const region = REGIONS[params.id as keyof typeof REGIONS]

	if (!region) {
		error(404, `Region ${params.id} not found`)
	}

	const { name, states, inDevelopment } = region as Region

	const teams = states
		.filter((state) => CONNECTIVITY_TEAMS[state as ConnectivityTeamKey])
		.map((state) => CONNECTIVITY_TEAMS[state as ConnectivityTeamKey])

	let dataProviders: DataProvider[] = []
	states.forEach((state) => {
		dataProviders.push(...(STATE_DATA_PROVIDERS[state as keyof typeof STATE_DATA_PROVIDERS] || []))
	})

	const dataProviderFilenames = new Set(
		dataProviders.filter(({ logo }) => logo).map(({ logo }) => logo)
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

		dataProviders = dataProviders.map(({ logo, ...rest }) => ({
			...rest,
			logo: logo ? logos[logo] : undefined
		}))
	}

	const { default: map } = await import(
		`$lib/assets/images/maps/regions/${params.id}.png?as=picture&w=500&format=avif;webp;png`
	)

	return {
		name,
		states,
		inDevelopment,
		dataProviders,
		teams,
		map
	}
}

export const entries: EntryGenerator = () => Object.keys(REGIONS).map((id) => ({ id }))
