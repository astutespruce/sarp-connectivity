import React from 'react'

import * as Sentry from '@sentry/react'
import { QueryClient, QueryClientProvider } from 'react-query'

import { siteMetadata } from './gatsby-config'

const queryClient = new QueryClient()

export const wrapRootElement = ({ element }) => (
  <QueryClientProvider client={queryClient}>{element}</QueryClientProvider>
)

const { sentryDSN } = siteMetadata
export const onClientEntry = () => {
  if (sentryDSN) {
    Sentry.init({
      dsn: sentryDSN,
      beforeSend(event, { originalException: error }) {
        if (error && error.message) {
          // this error happens when ResizeObserver not able to deliver all observations within a single animation frame
          if (error.message.match(/ResizeObserver loop limit exceeded/i)) {
            return null
          }
        }
        return event
      },
    })
    window.Sentry = Sentry
  }
}
