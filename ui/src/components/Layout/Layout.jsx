import React from 'react'
import PropTypes from 'prop-types'
import { useErrorBoundary } from 'use-error-boundary'
import { Box, Flex } from 'theme-ui'

import { isUnsupported, hasWindow } from 'util/dom'
import UnsupportedBrowser from './UnsupportedBrowser'
import Header from './Header'
import Footer from './Footer'
import PageError from './PageError'

const Layout = ({ children }) => {
  const { ErrorBoundary, didCatch } = useErrorBoundary({
    onDidCatch: (err, errInfo) => {
      // eslint-disable-next-line no-console
      console.error('Error boundary caught', err, errInfo)

      if (hasWindow && window.Sentry) {
        const { Sentry } = window
        Sentry.withScope((scope) => {
          scope.setExtras(errInfo)
          Sentry.captureException(err)
        })
      }
    },
  })

  return (
    <Flex sx={{ height: '100%', flexDirection: 'column' }}>
      <Header />

      <Box
        sx={{
          flex: '1 1 auto',
          overflowY: 'auto',
          overflowX: 'hidden',
          height: '100%',
        }}
      >
        {isUnsupported ? (
          <UnsupportedBrowser />
        ) : (
          <Box
            sx={{
              flex: '1 1 auto',
              overflowY: 'auto',
              overflowX: 'hidden',
              height: '100%',
            }}
          >
            {didCatch ? (
              <PageError />
            ) : (
              <ErrorBoundary>{children}</ErrorBoundary>
            )}
          </Box>
        )}
      </Box>

      <Footer />
    </Flex>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout
