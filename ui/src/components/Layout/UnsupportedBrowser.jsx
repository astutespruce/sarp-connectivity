import React from 'react'
import { Container, Flex, Box, Heading, Paragraph } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

const UnsupportedBrowser = () => (
  <Container pt="3rem">
    <Flex>
      <Heading as="h1" sx={{ flex: '0 0 auto' }}>
        <ExclamationTriangle size="5rem" style={{ marginRight: '1rem' }} />
      </Heading>
      <Box sx={{ flex: '1 1 auto' }}>
        <Heading as="h2">
          Unfortunately, you are using an unsupported version of Internet
          Explorer.
        </Heading>
        <Paragraph>
          Please use a modern browser such as Google Chrome, Firefox, or
          Microsoft Edge.
        </Paragraph>
      </Box>
    </Flex>
  </Container>
)

export default UnsupportedBrowser
