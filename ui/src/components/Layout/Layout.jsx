import React from 'react'
import PropTypes from 'prop-types'
import { useErrorBoundary } from 'use-error-boundary'
import { Box, Flex } from 'theme-ui'

import { isUnsupported, hasWindow } from 'util/dom'
import UnsupportedBrowser from './UnsupportedBrowser'
import Header from './Header'
import Footer from './Footer'
import PageError from './PageError'
import SEO from './SEO'

import { siteMetadata } from '../../../gatsby-config'

const Layout = ({ children, title }) => {
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
      <SEO title={title || siteMetadata.title} />
      <Header />

      <Box sx={{ flex: '1 1 auto', overflowY: 'auto', height: '100%' }}>
        {isUnsupported ? (
          <UnsupportedBrowser />
        ) : (
          <Box sx={{ flex: '1 1 auto', overflowY: 'auto', height: '100%' }}>
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
  title: PropTypes.string,
}

Layout.defaultProps = {
  title: '',
}

export default Layout
