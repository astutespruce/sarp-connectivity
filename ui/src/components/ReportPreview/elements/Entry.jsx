import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

const Entry = ({ children, sx, ...props }) => (
  <Box
    {...props}
    sx={{
      ...sx,
      px: '0.5rem',
      '&:not(:first-of-type)': {
        mt: '0.5rem',
        pt: '0.25rem',
        borderTop: '1px solid',
        borderTopColor: 'grey.1',
      },
    }}
  >
    {children}
  </Box>
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
