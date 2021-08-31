import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

const Entry = ({ children, sx, ...props }) => (
  <Text
    {...props}
    sx={{
      display: 'inline',
      ...sx,
    }}
  >
    {children}
  </Text>
)

Entry.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  sx: PropTypes.object,
}

Entry.defaultProps = {
  sx: {},
}

export default Entry
