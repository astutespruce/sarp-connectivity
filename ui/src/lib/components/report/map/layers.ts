import { barrierTypeLabels, pointLegends } from '$lib/config/constants'
import type { NetworkType } from '$lib/config/types'
import { capitalize } from '$lib/util/format'

export type LegendSymbol = {
	color: string
	radius?: number
	borderColor?: string
	borderWidth?: number
	borderStyle?: string
}

export type LegendEntry = {
	type: 'circle' | 'line'
	label: string
	// for optional properties at entry level
	color?: string
	radius?: number
	borderColor?: string
	borderWidth?: number
	borderStyle?: string
	// for optional properties at symbol level
	symbols?: LegendSymbol[]
}

export const pointHighlightLayer = {
	id: 'point-highlight',
	source: {
		type: 'geojson',
		data: null
	},
	type: 'circle',
	minzoom: 12,
	maxzoom: 24,
	paint: {
		'circle-color': '#fd8d3c',
		'circle-radius': 14,
		'circle-stroke-width': 3,
		'circle-stroke-color': '#f03b20'
	}
}

const flowlineSymbols: { [key: string]: LegendEntry } = {
	flowline: {
		color: '#1891ac',
		label: 'Stream reach',
		type: 'line',
		borderWidth: 2
	},
	alteredFlowline: {
		color: '#9370db',
		label: 'Altered stream reach (canal / ditch / reservoir)',
		type: 'line',
		borderWidth: 2
	},
	intermittentFlowline: {
		label: 'Intermittent / ephemeral stream reach',
		color: '#1891ac',
		type: 'line',
		borderStyle: 'dashed',
		borderWidth: 2
	}
}

type GetLegendEntriesParams = {
	name: string
	networkType: NetworkType
	visibleLayers: Set<string>
}

type GetLegendEntries = (params: GetLegendEntriesParams) => LegendEntry[]

export const getLegendEntries: GetLegendEntries = ({ name, networkType, visibleLayers }) => {
	const networkTypeLabel = barrierTypeLabels[networkType as NetworkType]
	const entries: LegendEntry[] = [
		{
			color: '#fd8d3c',
			borderColor: '#f03b20',
			type: 'circle',
			label: name,
			borderWidth: 2
		},
		{
			color: '#fd8d3c',
			type: 'line',
			label: 'Upstream network',
			borderWidth: 2
		}
	]

	const { included: primary, unrankedBarriers, other } = pointLegends
	entries.push({
		...primary.getSymbol(networkType),
		type: 'circle',
		label: capitalize(primary.getLabel(networkTypeLabel))
	})

	unrankedBarriers
		.filter(
			({ id }) =>
				// don't show minor barriers for dams view
				id !== 'minorBarrier' || networkType !== 'dams'
		)
		.forEach(({ getSymbol, getLabel }) => {
			entries.push({
				...getSymbol(networkType),
				type: 'circle',
				label: capitalize(getLabel(networkTypeLabel))
			})
		})

	other.forEach(({ id, getLabel, getSymbol }) => {
		// if visible layers are tracked, but not currently
		// visible, don't add to legend
		if (
			(id === 'dams-secondary' || id === 'waterfalls') &&
			visibleLayers &&
			!visibleLayers.has(id)
		) {
			return
		}

		if (id === 'dams-secondary' && networkType !== 'small_barriers') {
			return
		}

		entries.push({
			...getSymbol(),
			type: 'circle',
			label: capitalize(getLabel())
		})
	})

	if (visibleLayers) {
		const flowlineElementsPresent = Object.entries(flowlineSymbols)
			.filter(([key]) => visibleLayers.has(key))
			/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
			.map(([_, symbol]) => symbol)
		entries.push(...flowlineElementsPresent)
	} else {
		entries.push(...Object.values(flowlineSymbols))
	}

	return entries
}
