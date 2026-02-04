import type { EntryGenerator } from './$types'

const networkTypes = [
	'dams',
	'small_barriers',
	'combined_barriers',
	'smallfish_barriers',
	'smallfish_barriers'
]

export const entries: EntryGenerator = () => networkTypes.map((networkType) => ({ networkType }))
