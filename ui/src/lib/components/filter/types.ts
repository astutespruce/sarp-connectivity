import type { Table } from 'arquero'

export type Dimension = {
	field: string
	title: string
	help?: string
	hideMissingValues?: boolean
	hideIfEmpty?: boolean
	sort?: boolean
	isArray?: boolean
	labels: string[]
	values: number[] | string[]
}

export type Dimensions = {
	[key: string]: Dimension
}

type FilterGroup = {
	id: string
	title: string
	filters: Dimension[]
	hasData: (data: Table) => boolean
}

export type FilterConfig = FilterGroup[]
