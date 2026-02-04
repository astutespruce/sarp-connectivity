import * as Sentry from '@sentry/svelte'
import { browser } from '$app/environment'
import { SENTRY_DSN, DEPLOY_ENV } from '$lib/env'

export const prerender = true
export const ssr = false
export const trailingSlash = 'always'

if (browser && typeof SENTRY_DSN !== 'undefined') {
	Sentry.init({
		dsn: SENTRY_DSN,
		environment: DEPLOY_ENV,
		denyUrls: [
			// Chrome extensions
			/extensions\//i,
			/^chrome:\/\//i,
			/^chrome-extension:\/\//i
		]
	})
	window.Sentry = Sentry
}
