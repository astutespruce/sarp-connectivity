import type { Map } from 'mapbox-gl'
import { Crossfilter } from '$lib/components/filter'

// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	// extend Window object to handle properties / functions added at runtime
	interface Window {
		/* eslint-disable-next-line @typescript-eslint/no-explicit-any */
		dataLayer?: any[]

		// sentry is dynamically defined at runtime
		Sentry?: {
			captureException: (any) => void
		}

		// gtag is added dynamically at runtime
		gtag?: (...unknown) => void

		// map is dynamically added to window on map pages
		map?: Map

		// crossfilter is dynamically added to window on priority / survey pages
		crossfilter?: Crossfilter
	}
}

export {}
