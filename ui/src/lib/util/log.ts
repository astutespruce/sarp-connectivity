/* eslint-disable no-console */
import * as Sentry from '@sentry/browser'

export const captureException = (err: Error | string) => {
	Sentry.captureException(err)
	console.error(err)
}
