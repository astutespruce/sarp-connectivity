import React from 'react'
import { Container, Flex, Box } from 'components/Grid'
import { FaExclamationTriangle } from 'react-icons/fa'

import styled from 'style'

const IconHeader = styled.h1`
  text-align: center;
`

const StyledIcon = styled(FaExclamationTriangle)`
  height: 7rem;
  width: 7rem;
  margin-right: 1rem;
`

const UnsupportedBrowser = () => (
  <Container pt="3rem">
    <Flex>
      <IconHeader>
        <StyledIcon />
      </IconHeader>
      <Box>
        <h1>
          Unfortunately, you are using an unsupported version of Internet
          Explorer.
        </h1>
        <p>
          Please use a modern browser such as Google Chrome, Firefox, or
          Microsoft Edge.
        </p>
      </Box>
    </Flex>
  </Container>
)

export default UnsupportedBrowser
