import { SvelteSet } from 'svelte/reactivity'
import { getQueryClientContext } from '@tanstack/svelte-query'
import type { QueryClient } from '@tanstack/svelte-query'

import { fetchUnitDetails } from '$lib/api'
import { extractYearRemovedStats } from '$lib/util/stats'
import { captureException } from '$lib/util/log'

import type { SummaryUnit } from './types'

export class SummaryUnitManager {
	#ids = new SvelteSet()
	#items: SummaryUnit[] = $state.raw([])
	#isLoading: boolean = $state(false)
	#error: string | null = $state(null)
	#queryClient: QueryClient | undefined = $state.raw()

	constructor() {
		this.#queryClient = getQueryClientContext()
	}

	clear(): void {
		this.#ids.clear()
		this.#items = []
		this.#isLoading = false
		this.#error = null
	}

	get ids(): string[] {
		return [...this.#ids] as string[]
	}

	get items(): SummaryUnit[] {
		return this.#items
	}

	get count(): number {
		return this.#items.length
	}

	async toggleItem(item: SummaryUnit): Promise<void> {
		// remove if already present
		if (this.#ids.has(item.id)) {
			this.removeItem(item)
		} else {
			await this.addItem(item)
		}
	}

	async addItem(item: SummaryUnit): Promise<void> {
		// assume if barrier counts are present it was from a search feature and already
		// has necessary data loaded
		if (item.dams !== undefined) {
			this.#ids.add(item.id)
			this.#items = [
				...this.#items,
				{
					...item,
					removedBarriersByYear: extractYearRemovedStats(
						item.removedDamsByYear,
						item.removedSmallBarriersByYear
					)
				}
			]
			this.#isLoading = false
			this.#error = null
			return
		}

		// otherwise fetch details for it
		this.#isLoading = true

		try {
			const data = await this.#queryClient!.fetchQuery({
				queryKey: ['unit-details', item.layer, item.id],
				queryFn: async () => fetchUnitDetails(item.layer, item.id)
			})

			// if multiple requests resolved with this id due to slow requests, ignore
			// subsequent requests
			if (!this.#ids.has(item.id)) {
				this.#ids.add(item.id)
				this.#items = [
					...this.#items,
					{
						...item,
						...data
					}
				]
				this.#isLoading = false
				this.#error = null
			}
		} catch (ex) {
			captureException(ex as Error | string)
			this.#isLoading = false
			this.#error = ex as string
		}
	}

	removeItem(item: SummaryUnit): void {
		this.#ids.delete(item.id)
		this.#items = this.#items.filter(({ id }) => id !== item.id)
	}

	getUnitIdsByLayer(): Record<string, string[] | number[]> {
		return this.#items.reduce((prev: Record<string, string[]>, item: SummaryUnit) => {
			prev[item.layer] = [...(prev[item.layer] || []), item.id]
			return prev
		}, {})
	}

	get isLoading(): boolean {
		return this.#isLoading
	}

	get error(): string | null {
		return this.#error
	}
}
