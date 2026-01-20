import type { Map } from 'mapbox-gl'

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
		Sentry: {
			captureException: (any) => void
		}

		// map is dynamically added to window on map pages
		map: Map | undefined
	}
}

export {}
