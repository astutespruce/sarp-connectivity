import React from 'react'
import { Container, Flex, Box } from 'components/Grid'
import { FaExclamationTriangle } from 'react-icons/fa'

import { OutboundLink } from 'components/Link'
import styled from 'style'

import { siteMetadata } from '../../../gatsby-config'

const IconHeader = styled.h1`
  text-align: center;
`

const StyledIcon = styled(FaExclamationTriangle)`
  height: 7rem;
  width: 7rem;
  margin-right: 1rem;
`

const PageErrorMessage = () => (
  <Container pt="3rem">
    <Flex>
      <IconHeader>
        <StyledIcon />
      </IconHeader>
      <Box>
        <h1>Whoops! Something went wrong...</h1>
        <p>
          We&apos;re sorry, something didn&apos;t quite work properly.
          <br />
          <br />
          Please try to refresh this page. If the error continues, please{' '}
          <OutboundLink to={`mailto:${siteMetadata.contactEmail}`}>
            let us know
          </OutboundLink>
          .
        </p>
      </Box>
    </Flex>
  </Container>
)

export default PageErrorMessage
