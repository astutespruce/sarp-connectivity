import React from 'react'
import PropTypes from 'prop-types'
import { useErrorBoundary } from 'use-error-boundary'

import SEO from 'components/SEO'
import { Flex } from 'components/Grid'
import styled, { ThemeProvider, theme } from 'style'
import { isUnsupported, hasWindow } from 'util/dom'
import UnsupportedBrowser from './UnsupportedBrowser'
import Header from './Header'
import Footer from './Footer'
import PageError from './PageError'

import { siteMetadata } from '../../../gatsby-config'

const Wrapper = styled(Flex).attrs({ flexDirection: 'column' })`
  height: 100%;
`

const Content = styled.div`
  flex: 1 1 auto;
  overflow-y: auto;
  height: 100%;
`

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
    <ThemeProvider theme={theme}>
      <Wrapper>
        <SEO title={title || siteMetadata.title} />
        <Header />

        <Content>
          {isUnsupported ? (
            <UnsupportedBrowser />
          ) : (
            <>
              {didCatch ? (
                <PageError />
              ) : (
                <ErrorBoundary>{children}</ErrorBoundary>
              )}
            </>
          )}
        </Content>

        <Footer />
      </Wrapper>
    </ThemeProvider>
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
