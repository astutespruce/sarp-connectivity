import React from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'

const TopBar = ({ children }) => (
  <Flex
    sx={{
      alignItems: 'center',
      p: '0.5rem',
      position: 'absolute',
      top: 0,
      left: '10px',
      zIndex: 1000,
      bg: '#FFF',
      borderRadius: '0 0 0.25rem 0.25rem',
      boxShadow: '1px 1px 8px #333',
      fontSize: 'small',
      button: {
        textTransform: 'lowercase',
        py: '0.25rem',
        px: '0.5rem',
      },
    }}
  >
    {children}
  </Flex>
)

TopBar.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
}

export default TopBar
