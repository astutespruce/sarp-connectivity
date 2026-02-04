type Entry = {
	id?: string
	label: string
	color: string
}

export type Patch = {
	id: string
	label?: string
	entries: Entry[]
}

export type CircleSymbol = {
	color: string
	radius: number
	borderColor?: string
	borderWidth?: number
}

export type Circle = Entry & {
	id: string
	color?: string
	radius?: number
	borderColor?: string
	borderWidth?: number
	symbols?: CircleSymbol[]
}

export type Line = Entry & {
	id: string
	lineWidth: number
	lineStyle?: string
}
