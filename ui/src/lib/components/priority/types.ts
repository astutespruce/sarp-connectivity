export type Option = { value: string; label: string }

export type Status = { isLoading: boolean; error?: string | null }

export type Step = 'select-layer' | 'select-units' | 'filter' | 'results'

export type ResultType = 'full' | 'perennial' | 'mainstem'
