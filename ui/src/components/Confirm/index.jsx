import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Heading, Flex } from 'theme-ui'

const Confirm = ({ title, children, onConfirm, onClose }) => (
  <Flex
    sx={{
      justifyContent: 'center',
      alignItems: 'center',
      position: 'absolute',
      zIndex: 100000,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
    }}
  >
    <Box
      onClick={onClose}
      sx={{
        position: 'absolute',
        zIndex: 1,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        bg: 'rgba(10,10,10,0.86)',
        cursor: 'pointer',
      }}
    />
    <Box
      sx={{
        p: '1.25rem',
        zIndex: 2,
        mx: 'auto',
        position: 'relative',
        width: '300px',
        borderRadius: '0.5rem',
        bg: '#FFF',
      }}
    >
      <Heading as="h4" sx={{ mb: '1rem' }}>
        {title}
      </Heading>

      {children}

      <Flex
        sx={{
          justifyContent: 'space-between',
          pt: '1rem',
          mt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.2',
        }}
      >
        <Button onClick={onClose} sx={{ flex: '0 0 auto' }}>
          No
        </Button>
        <Button variant="warning" onClick={onConfirm} sx={{ flex: '0 0 auto' }}>
          Yes
        </Button>
      </Flex>
    </Box>
  </Flex>
)

Confirm.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default Confirm
