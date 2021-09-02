import React from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'

const ButtonGroup = ({ children, sx }) => (
  <Flex
    sx={{
      alignItems: 'stretch',
      'button + button': {
        borderLeft: '1px solid #FFF',
      },
      'button:first-of-type': {
        borderRadius: '6px 0 0 6px',
      },
      'button:last-of-type': {
        borderRadius: '0 6px 6px 0',
      },
      'button:not(:first-of-type):not(:last-of-type)': {
        borderRadius: 0,
      },
      ...sx,
    }}
  >
    {children}
  </Flex>
)

ButtonGroup.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired,
  sx: PropTypes.object,
}

ButtonGroup.defaultProps = {
  sx: {},
}

export default ButtonGroup
