import React from 'react'
import PropTypes from 'prop-types'
import { Box, Container, Flex, Spinner } from 'theme-ui'

const PageLoadingMessage = ({ message }) => (
  <Container pt="3rem">
    <Flex
      sx={{
        py: '1rem',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '10rem',
      }}
    >
      <Spinner sx={{ flex: '0 0 auto', color: 'primary', m: '0 1rem 0 0' }} />
      <Box sx={{ fontSize: 3, color: 'grey.7' }}>{message}</Box>
    </Flex>
  </Container>
)

PageLoadingMessage.propTypes = {
  message: PropTypes.string,
}

PageLoadingMessage.defaultProps = {
  message: 'Loading...',
}

export default PageLoadingMessage
