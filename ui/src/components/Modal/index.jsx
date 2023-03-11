import React from 'react'
import { createPortal } from 'react-dom'
import PropTypes from 'prop-types'
import { Box, Flex, Heading } from 'theme-ui'

const index = ({ children, title, onClose }) => {
  const handleClose = () => {
    onClose()
  }

  return createPortal(
    <Flex
      sx={{
        alignItems: 'center',
        justifyContent: 'center',
        position: 'absolute',
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 10000,
        overflow: 'auto',
      }}
    >
      <Box
        onClick={handleClose}
        sx={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1,
          bg: 'rgba(0, 0, 0, 0.5)',
        }}
      />
      <Box
        sx={{
          pt: '1rem',
          px: '2rem',
          pb: '2rem',
          bg: '#FFF',
          zIndex: 2,
          borderRadius: '1rem',
          boxShadow: '1px 1px 6px #000',
        }}
      >
        <Heading
          as="h3"
          sx={{
            pb: '0.5rem',
            mb: '0.5rem',
            borderBottom: '0.25rem solid',
            borderBottomColor: 'blue.8',
          }}
        >
          {title}
        </Heading>

        {children}
      </Box>
    </Flex>,
    document.body
  )
}

index.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default index
