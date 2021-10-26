import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

const ExpandableParagraph = ({ snippet, children, ...props }) => {
  const [isOpen, setIsOpen] = useState(false)

  const toggle = () => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }
  return (
    <Box sx={{ cursor: 'pointer' }} onClick={toggle}>
      {isOpen ? (
        children
      ) : (
        <Text {...props} as="span" sx={{ display: 'inline' }}>
          {snippet}
        </Text>
      )}{' '}
      <Text
        {...props}
        as="span"
        sx={{
          display: 'inline',
          color: 'primary',
          '&:hover': { textDecoration: 'underline' },
        }}
      >
        Show {isOpen ? 'less' : 'more'} ...
      </Text>
    </Box>
  )
}

ExpandableParagraph.propTypes = {
  snippet: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.element]).isRequired,
}

export default ExpandableParagraph
