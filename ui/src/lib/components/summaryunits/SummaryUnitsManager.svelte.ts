import { SvelteSet } from 'svelte/reactivity'

class SummaryUnitManager {
	#ids = new SvelteSet()
	#items = []

	constructor() {}

	clear(): void {
		this.#ids.clear()
	}
}
