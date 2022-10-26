import React from 'react'
import { Container, Flex, Box, Heading, Paragraph } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/Link'
import { siteMetadata } from 'constants'

const PageErrorMessage = () => (
  <Container pt="3rem">
    <Flex sx={{ alignItems: 'flex-start' }}>
      <Box sx={{ flex: '0 0 auto', mr: '1rem' }}>
        <ExclamationTriangle size="5rem" />
      </Box>
      <Box sx={{ flex: '1 1 auto' }}>
        <Heading as="h2">Whoops! Something went wrong...</Heading>
        <Paragraph sx={{ mt: '2rem' }}>
          We&apos;re sorry, something didn&apos;t quite work properly.
          <br />
          <br />
          Please try to refresh this page. If the error continues, please{' '}
          <OutboundLink to={`mailto:${siteMetadata.contactEmail}`}>
            let us know
          </OutboundLink>
          .
        </Paragraph>
      </Box>
    </Flex>
  </Container>
)

export default PageErrorMessage
