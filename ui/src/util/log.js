/* eslint-disable no-console */
import * as Sentry from '@sentry/browser'

export const captureException = err => {
  Sentry.captureException(err)
  console.error(err)
}
