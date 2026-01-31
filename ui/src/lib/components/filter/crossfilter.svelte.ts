import { op, agg, escape } from 'arquero'
import type { ColumnTable as Table } from 'arquero'
import type { RowObject } from 'arquero/dist/types/table/types'
import { SvelteSet } from 'svelte/reactivity'

import { filters as allFilterConfig } from '$lib/config/filters'
import type { BarrierTypePlural } from '$lib/config/types'
import { sum } from '$lib/util/data'
import { applyFilters, createDimensions, countByDimension } from './util'
import type { Dimension, Dimensions, FilterConfig } from './types'

export class Crossfilter {
	#networkType: BarrierTypePlural | null = $state(null)
	#filterConfig: FilterConfig | null = $state(null)
	// dimensions do not change once this class is initialized
	#dimensions: Dimensions = $state({})

	#data: Table | null = $state(null)
	#filteredData: Table | null = $state(null)

	// total dimension counts are the counts when no filters are applied
	#totalDimensionCounts: Record<string, number> = $state({})
	#dimensionCounts: Record<string, number> = $state({})

	#filters: Record<string, SvelteSet<number | string>> = $state({})
	#hasFilters: boolean = $state(false)
	#filteredCount: number = $state(0)

	#emptyDimensions: SvelteSet<string> = new SvelteSet()
	#emptyGroups: SvelteSet<string> = new SvelteSet()

	constructor(networkType: BarrierTypePlural) {
		console.log('create crossfilter', networkType)

		this.#networkType = networkType
		this.#filterConfig = allFilterConfig[
			networkType as keyof typeof allFilterConfig
		] as FilterConfig
		this.#dimensions = createDimensions(this.#filterConfig)

		window.crossfilter = this
	}

	get data(): Table | null {
		return this.#data
	}

	/**
	 * Set new data, which will reset all filters
	 */
	set data(rawData: Table | null) {
		console.log('set data', rawData)

		console.time('setData')

		// reset state on change of data
		this.#data = null
		this.#filteredData = null
		this.#dimensionCounts = {}
		this.#totalDimensionCounts = {}
		this.#filters = {}
		this.#hasFilters = false
		this.#filteredCount = 0
		this.#emptyDimensions = new SvelteSet()
		this.#emptyGroups = new SvelteSet()

		if (rawData === null) {
			return
		}

		let newData = rawData

		// validate that expected fields are present and split array fields
		const cols = new SvelteSet(newData.columnNames())
		Object.values(this.#dimensions).forEach(({ field, isArray }) => {
			if (!cols.has(field)) {
				throw new Error(`Field is not present in data: ${field}`)
			}
			if (isArray) {
				newData = newData.derive({
					[field]: escape((d: RowObject) => op.split(d[field], ','))
				})
			}
		})

		this.#dimensionCounts = countByDimension(newData, this.#dimensions)

		this.#filterConfig!.filter(({ hasData }) => hasData && !hasData(newData)).forEach(({ id }) => {
			this.#emptyGroups.add(id)
		})

		Object.entries(this.#dimensionCounts).forEach(([field, counts]) => {
			if (!(counts && sum(Object.values(counts)) > 0)) {
				this.#emptyDimensions.add(field)
			}
		})

		this.#data = newData
		this.#filteredData = newData
		this.#totalDimensionCounts = this.#dimensionCounts
		this.#filteredCount = agg(newData, (d) => op.sum(d._count))

		console.timeEnd('setData')
	}

	get dimensions() {
		return this.#dimensions
	}

	get dimensionCounts(): Record<string, number> {
		return this.#dimensionCounts
	}

	get emptyDimensions(): SvelteSet<string> {
		return this.#emptyDimensions
	}

	get emptyGroups(): SvelteSet<string> {
		return this.#emptyGroups
	}

	get filterConfig(): FilterConfig | null {
		return this.#filterConfig
	}

	/**
	 * Return an index of all filters by field
	 */
	get filterConfigIndex(): Record<string, Dimension> {
		const out: Record<string, Dimension> = {}
		this.#filterConfig?.forEach(({ filters }) => {
			filters.forEach((dimension) => {
				out[dimension.field] = dimension
			})
		})

		return out
	}

	get filteredCount(): number {
		return this.#filteredCount
	}

	get filteredData(): Table | null {
		return this.#filteredData
	}

	get filters() {
		return this.#filters
	}

	/**
	 * Serialize filters to a string so that they can be used as a query key for tanstack-query
	 * @returns
	 */
	serializeFilters(): string {
		return JSON.stringify(this.#filters, (_, value) => (value && value.size ? [...value] : value))
	}

	/**
	 * Add a filter on field based on the set of values passed in
	 * @param field - field to filter
	 * @param values - set of values to filter IN; if empty or null, will remove the filter on this field
	 */
	setFilter(field: string, values: SvelteSet<number | string> | null): void {
		if (!this.#dimensions[field]) {
			console.warn(`Filter requested on dimension that does not exist: ${field}`)
			return
		}

		console.time('setFilter')

		if (values && values.size > 0) {
			// only set if non-empty
			this.#filters[field] = values
		} else {
			// unset it
			delete this.#filters[field]
		}

		this.#updateFilterState()

		console.timeEnd('setFilter')
	}

	/**
	 * Add or remove a filter value for field.  If the value was already filtered IN,
	 * it is removed; otherwise it is added.
	 * @param field - field to update
	 * @param value - value to add / remove
	 */
	toggleFilterValue(field: string, value: number | string): void {
		if (!this.#dimensions[field]) {
			console.warn(`Filter requested on dimension that does not exist: ${field}`)
			return
		}

		console.time('update filter value')

		if (this.#filters[field]) {
			// if already filtered IN, remove it
			if (this.#filters[field].has(value)) {
				this.#filters[field].delete(value)
			} else {
				this.#filters[field].add(value)
			}
		} else {
			this.#filters[field] = new SvelteSet([value])
		}

		this.#updateFilterState()

		console.timeEnd('update filter value')
	}

	/**
	 * Reset filter values on field
	 * @param field - field to reset
	 */
	resetFilter(field: string): void {
		console.time('resetFilter')

		delete this.#filters[field]

		this.#updateFilterState()

		console.timeEnd('resetFilter')
	}

	#updateFilterState() {
		this.#hasFilters =
			Object.entries(this.#filters).filter(
				/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
				([_, filter]) => filter && filter.size > 0
			).length > 0

		if (this.#hasFilters) {
			const { data: newFilteredData, dimensionCounts: newDimensionCounts } = applyFilters(
				this.#data,
				this.#dimensions,
				this.#filters
			)
			this.#filteredData = newFilteredData
			this.#filteredCount =
				this.#filteredData && this.#filteredData.size > 0
					? agg(this.#filteredData, (d) => op.sum(d._count))
					: 0
			this.#dimensionCounts = newDimensionCounts
		} else {
			this.#filteredData = this.#data
			this.#filteredCount =
				this.#data && this.#data.size > 0 ? agg(this.#data, (d) => op.sum(d._count)) : 0
			this.#dimensionCounts = this.#totalDimensionCounts
		}
	}

	/**
	 * Reset all filters
	 */
	resetFilters(): void {
		console.time('resetFilters')

		// keep data and totalDimensionCounts the same
		this.#filters = {}
		this.#filteredData = this.#data
		this.#filteredCount = agg(this.#data!, (d) => op.sum(d._count))
		this.#hasFilters = false
		this.#dimensionCounts = this.#totalDimensionCounts

		console.timeEnd('resetFilters')
	}

	/**
	 * Reset all filters within group
	 * @param groupId - ID of group to reset
	 */
	resetGroupFilters(groupId: string): void {
		console.time('resetGroupFilters')

		this.#filterConfig!.filter(({ id }) => id === groupId)[0].filters.forEach(({ field }) => {
			if (this.#filters[field]) {
				delete this.#filters[field]
			}
		})

		this.#updateFilterState()

		console.timeEnd('resetGroupFilters')
	}

	get hasFilters(): boolean {
		return this.#hasFilters
	}

	get networkType(): BarrierTypePlural | null {
		return this.#networkType
	}

	get totalDimensionCounts(): Record<string, number> {
		return this.#totalDimensionCounts
	}
}
