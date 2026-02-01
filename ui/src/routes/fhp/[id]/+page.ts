import { error } from '@sveltejs/kit'

import { FISH_HABITAT_PARTNERSHIPS } from '$lib/config/constants.js'

import type { EntryGenerator } from './$types'

export const load = async ({ params }) => {
	type FHPKeyType = keyof typeof FISH_HABITAT_PARTNERSHIPS
	type FHPType = {
		name: string
		description: string
		url: string
		logo?: string
		logoWidth?: string
	}

	const fhp = FISH_HABITAT_PARTNERSHIPS[params.id as FHPKeyType] as FHPType

	if (!fhp) {
		error(404, `FHP ${params.id} not found`)
	}

	const logo = fhp.logo
		? (Object.entries(
				import.meta.glob('$lib/assets/images/*_logo.*', {
					eager: true,
					import: 'default'
				})
			)
				.filter(([path]) => path.split('/').slice(-1)[0] === fhp.logo)
				/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
				.map(([_, img]) => img)[0] as string)
		: null

	const { default: map } = await import(
		`$lib/assets/images/maps/fhp/${params.id}.png?as=picture&w=500&format=avif;webp;jpeg`
	)

	return {
		...fhp,
		logo,
		map
	}
}

export const entries: EntryGenerator = () =>
	Object.keys(FISH_HABITAT_PARTNERSHIPS).map((id) => ({ id }))
